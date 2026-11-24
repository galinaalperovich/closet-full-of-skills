#!/usr/bin/env python3
"""Single reproducible entry point for the skill/MCP selection study.

Reads the result files UNCHANGED, applies documented retry/filter rules, and writes the derived tables to
analysis/derived/ plus a report, analysis/REPORT.md.

    python3 analysis/analyze.py

Rules (fixed before computing any corrected metric):
  * Logical run key: E1 = (model, setup, target, request i, rep); E2/E3 = (model, setup, target, request i).
  * Retry rule: keep the FIRST attempt in file order that has no infrastructure error; never chosen by outcome.
    Attempts that only ever failed are reported as infrastructure failures and excluded from routing denominators.
  * Turn-limited runs (Claude `error_max_turns`) are RETAINED in every denominator. Metrics read
    "selected within the observation window".
  * Bootstrap: 2,000 resamples, seed 20261120. Request-cluster (resample requests) and two-stage
    (resample target components, then requests within them). Paired differences keep the same
    requests in both conditions within each resample. Repetitions are averaged within request x condition.
"""
import csv, gzip, hashlib, json, math, os, random, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
# Claude Code E2/E3 come from the second collection round (mcp/*_round2.jsonl), in which the stub MCP servers were
# allowed and every run had a fresh folder; the first round's Claude Code E2/E3 records are skipped (headless Claude Code
# had denied every MCP call). The 18 E1 runs of Sonnet / caveman / alone come from an isolated rerun, because a memory
# note saved by one original run reached later runs in that folder. E3b and all Codex records come from the first round.
OUT = os.path.join(HERE, "derived"); os.makedirs(OUT, exist_ok=True)
SEED = 20261120; B = 2000
P = lambda *a: os.path.join(ROOT, *a)

# ---------------------------------------------------------------- inputs + manifest
INPUTS = {
    "E1": [("haiku.jsonl", "claude", "haiku", "subscription"), ("sonnet.jsonl", "claude", "sonnet", "subscription"),
           ("gpt.jsonl", "codex", "gpt", "api_key")],
    "E1_excluded": [("gpt_subscription_failed.jsonl", "codex", "gpt", "subscription")],
    "R1": [("mcp/haiku_round1.jsonl", "claude", "haiku", "subscription"), ("mcp/sonnet_round1.jsonl", "claude", "sonnet", "subscription"),
           ("mcp/gpt.jsonl", "codex", "gpt", "by_line")],
    "R2": [("mcp/haiku_round2.jsonl", "claude", "haiku", "subscription"), ("mcp/sonnet_round2.jsonl", "claude", "sonnet", "subscription")],
    "E1_rerun": [("sonnet_e1_caveman_rerun.jsonl", "claude", "sonnet", "subscription")],
}
E1_RERUN = lambda r: r["model"] == "sonnet" and r["setup"] == "alone" and r["target"] == "caveman"
OTHER = ["prompts.json", "mcp/mcp_targets.json", "mcp/trending_skill_prompts.json", "mcp/tools_inventory.json",
         "build.py", "run.py", "run_codex.py", "mcp/build.py", "mcp/run.py", "mcp/stub_server.py",
         "scan.py", "weight.py", "report.py", "scan.json", "weight.json", "source_commits.tsv",
         "analysis/alt_judge_input.json", "analysis/alt_judgments.json", "analysis/analyze.py"]
def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
manifest = []
for grp in INPUTS.values():
    for f, *_ in grp:
        manifest.append({"file": f, "sha256": sha(P(f)), "lines": sum(1 for _ in open(P(f)))})
for f in OTHER:
    if os.path.exists(P(f)): manifest.append({"file": f, "sha256": sha(P(f)), "lines": sum(1 for _ in open(P(f), errors="replace"))})
json.dump({"collection_date": "2026-11-20 (E1, E3b, Codex); 2026-11-22 (Claude Code E2/E3 second round, Sonnet caveman alone E1 rerun)", "seed": SEED, "bootstrap_resamples": B, "files": manifest},
          open(os.path.join(OUT, "manifest.json"), "w"), indent=1)

# ---------------------------------------------------------------- normalise records
SETUP_NAME = {"mixed_typical": "mixed_smaller", "mixed_heavy": "mixed_larger"}
HARNESS_MCP = {"list_mcp_resources", "list_mcp_resource_templates", "read_mcp_resource"}
BROWSER = {"playwright-mcp.browser_take_screenshot", "playwright-mcp.browser_fill_form", "chrome-devtools.performance_start_trace",
           "chrome-devtools.list_console_messages", "chrome-devtools.lighthouse_audit"}
def termination(rec, harness):
    err = str(rec.get("error") or "")
    if harness == "claude":
        s = rec.get("sub")
        if s == "success": return "completed"
        if s == "error_max_turns": return "turn_limit"
        if s: return "harness_error"
    else:
        if rec.get("sub") == "ok" and not err: return "completed"
    if "429" in err: return "api_error"
    if "Timeout" in err: return "timeout"
    return "harness_error" if err else "unknown"

rows, attempts, SUPERSEDED = [], [], []
def has_raw(rec, f):   # raw event log kept for this run (second-round records name it, relative to the result file's folder)
    p = rec.get("raw")
    return bool(p) and os.path.exists(os.path.join(os.path.dirname(P(f)), p))
def norm_e1(rec, harness, model, access, f, ln):
    fired = [x.split(":")[-1] for x in rec.get("fired", [])]
    return dict(exp="E1", harness=harness, model=model, access=access, file=f, line=ln, setup=rec["cond"], kind="skill",
                target=rec["target"], i=rec["i"], rep=rec.get("rep", 0), turn_cap=3 if harness == "claude" else None,
                term=termination(rec, harness), components=["skill:" + x for x in fired], builtins=[],
                target_sel=bool(rec["hit"]), capable_server=None, overlap_family=None, toolsearch=None,
                n_skills=rec.get("n_skills"), n_tools=None, mcp_failed=[], cost=rec.get("cost"), usage=rec.get("usage"),
                in_tok=rec.get("in_tok"), first_tool=rec.get("first_tool"), has_raw=has_raw(rec, f))
def norm_mcp(rec, harness, model, access, f, ln):
    env = rec["env"].split("/")[0]; exp = {"mcp": "E2", "sk": "E3b", "mixed": "E3"}[env.split("_")[0]]
    used = rec.get("used", [])
    # Codex's own MCP discovery tools (list_mcp_resources etc., server "codex" or the queried server) are harness
    # built-ins, not experimental components (the recorded `outcome` field is left untouched).
    used = ["builtin:" + u[4:] if u.startswith("mcp:") and (u.split(".")[0] == "mcp:codex" or u.split(".", 1)[1] in HARNESS_MCP) else u for u in used]
    return dict(exp=exp, harness=harness, model=model, access=access, file=f, line=ln, setup=SETUP_NAME.get(env, env), kind=rec["kind"],
                target=rec["target"], i=rec["i"], rep=0, turn_cap=4 if harness == "claude" else None, term=termination(rec, harness),
                components=[u for u in used if not u.startswith("builtin:")], builtins=[u for u in used if u.startswith("builtin:")],
                target_sel=bool(rec.get("hit_strict")), capable_server=bool(rec.get("hit")), overlap_family=rec.get("overlap_tool"),
                toolsearch=rec.get("toolsearch"), n_skills=rec.get("n_skills"), n_tools=rec.get("n_tools"),
                mcp_failed=rec.get("mcp_failed", []), cost=rec.get("cost"), usage=rec.get("usage"), in_tok=rec.get("in_tok"), first_tool=None,
                has_raw=has_raw(rec, f))
for grp, items in INPUTS.items():
    for f, harness, model, access in items:
        for ln, l in enumerate(open(P(f))):
            rec = json.loads(l)
            acc = access if access != "by_line" else ("api_key" if "ts" not in rec else "subscription")
            r = (norm_e1 if grp.startswith("E1") else norm_mcp)(rec, harness, model, acc, f, ln)
            if grp == "R1" and harness == "claude" and r["exp"] in ("E2", "E3"): continue   # replaced by the second round
            if grp == "E1" and E1_RERUN(r): SUPERSEDED.append(r); continue   # replaced by the isolated rerun
            r["batch"] = "excluded_429_batch" if grp == "E1_excluded" else "main"
            r["infra_fail"] = r["term"] in ("api_error", "timeout", "harness_error", "unknown")
            attempts.append(r)
seen = {}
for r in attempts:
    if r["batch"] != "main": continue
    key = (r["exp"], r["model"], r["setup"], r["target"], r["i"], r["rep"])
    r["key"] = key
    if key not in seen or (seen[key]["infra_fail"] and not r["infra_fail"]): seen[key] = r
retained = [r for r in seen.values() if not r["infra_fail"]]
infra_only = [r for r in seen.values() if r["infra_fail"]]

# ---------------------------------------------------------------- alternative appropriateness (retrospective)
JUD = {}
jp = os.path.join(HERE, "alt_judgments.json")
if os.path.exists(jp):
    for j in json.load(open(jp)): JUD[j["id"]] = j["label"]
RANK = ["equivalent", "preliminary_step", "related_partial", "unassessable", "inappropriate"]
def miss_class(r):
    if r["target_sel"]: return "target"
    if r["components"]:
        labs = [JUD.get(f'{r["kind"]}|{r["target"]}|{r["i"]}|{c}') for c in r["components"]]
        labs = [l for l in labs if l] or ["not_judged"]
        for k in RANK:
            if k in labs: return "alt_" + k
        return "alt_not_judged"
    return "builtin_only" if r["builtins"] else "no_component_detected"
for r in retained:
    r["miss_class"] = miss_class(r)
    r["acceptable_sel"] = r["miss_class"] in ("target", "alt_equivalent")
# first observed experimental component (proxy). For tools, use accepted set from targets file.
T = json.load(open(P("mcp/mcp_targets.json")))
for r in retained:
    if not r["components"]: r["first_is_target"] = False; continue
    c = r["components"][0]
    if r["kind"] == "skill": r["first_is_target"] = c == "skill:" + r["target"]
    else: r["first_is_target"] = c.startswith("mcp:") and c[4:] in set(T[r["target"]]["accept"])

# ---------------------------------------------------------------- stats helpers
def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)
def req_means(rs, metric):
    m = defaultdict(list)
    for r in rs: m[(r["target"], r["i"])].append(1.0 if r[metric] else 0.0)
    return {k: sum(v) / len(v) for k, v in m.items()}
def pct(xs, q):
    xs = sorted(xs); i = (len(xs) - 1) * q; lo = int(math.floor(i)); hi = int(math.ceil(i))
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
def boot(fn_keys, keys, two_stage=False, seed=SEED):
    """fn_keys(list_of_keys)->statistic. keys are (target,i)."""
    rnd = random.Random(seed); out = []
    by_t = defaultdict(list)
    for k in keys: by_t[k[0]].append(k)
    ts = sorted(by_t)
    for _ in range(B):
        if two_stage:
            s = []
            for t in (rnd.choice(ts) for _ in ts):
                ks = by_t[t]; s += [rnd.choice(ks) for _ in ks]
        else:
            s = [rnd.choice(keys) for _ in keys]
        out.append(fn_keys(s))
    return pct(out, .025), pct(out, .975)
def rate_row(rs, metric):
    m = req_means(rs, metric); keys = sorted(m)
    k = sum(1 for r in rs if r[metric]); n = len(rs)
    f = lambda s: sum(m[x] for x in s) / len(s)
    lo, hi = wilson(k, n); b1 = boot(f, keys); b2 = boot(f, keys, True)
    return dict(k=k, n=n, rate=k / n, wilson_lo=lo, wilson_hi=hi, req_lo=b1[0], req_hi=b1[1], skill_lo=b2[0], skill_hi=b2[1], n_requests=len(keys))
def paired_row(ra, rb, metric):
    ma, mb = req_means(ra, metric), req_means(rb, metric); keys = sorted(set(ma) & set(mb))
    f = lambda s: sum(mb[x] - ma[x] for x in s) / len(s)
    d = f(keys); b1 = boot(f, keys); b2 = boot(f, keys, True)
    worse = sum(1 for k in keys if mb[k] < ma[k]); better = sum(1 for k in keys if mb[k] > ma[k])
    return dict(diff=d, req_lo=b1[0], req_hi=b1[1], skill_lo=b2[0], skill_hi=b2[1], n_pairs=len(keys), requests_worse=worse, requests_better=better)
def sel(**kw):
    out = retained
    for k, v in kw.items():
        out = [r for r in out if (r[k] in v if isinstance(v, (set, list, tuple)) else r[k] == v)]
    return out
def write_csv(name, rows_):
    if not rows_: return
    keys = list(rows_[0].keys())
    with open(os.path.join(OUT, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
        for r in rows_: w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
pc = lambda x: f"{100*x:.1f}" if x == x else "n/a"

MODELS = ["haiku", "sonnet", "gpt"]
E1S = ["alone", "pack20", "crowd200", "crowd1000"]
E2S = ["mcp_alone", "mcp_pack20", "mcp_crowd200", "mcp_crowdall"]

# ---------------------------------------------------------------- 1. audit table
audit = []
groups = defaultdict(list)
for r in attempts: groups[(r["exp"], r["harness"], r["model"], r["setup"], r["access"], r["batch"])].append(r)
for (exp, h, m, s, acc, b), rs in sorted(groups.items()):
    keys = {(x["target"], x["i"], x["rep"]) for x in rs}
    ret = [x for x in retained if x["exp"] == exp and x["model"] == m and x["setup"] == s and x["access"] == acc and x["batch"] == b]
    audit.append(dict(exp=exp, harness=h, model=m, setup=s, access=acc, batch=b, attempts=len(rs), logical_runs=len(keys),
                      retained=len(ret), infra_failures=sum(1 for x in rs if x["infra_fail"]),
                      turn_limit=sum(1 for x in ret if x["term"] == "turn_limit"),
                      turn_limit_no_target=sum(1 for x in ret if x["term"] == "turn_limit" and not x["target_sel"]),
                      exposure_counts=";".join(sorted({f'skills={x["n_skills"]},tools={x["n_tools"]}' for x in ret if x["n_skills"] is not None})) or "not recorded",
                      mcp_connect_failures=sum(1 for x in ret if x["mcp_failed"]), raw_log_coverage=sum(1 for x in ret if x["has_raw"])))
write_csv("audit.csv", audit)


# ---------------------------------------------------------------- 3. E1 rates, termination, first selection, acceptable
e1 = []
for m in MODELS:
    for s in E1S:
        rs = sel(exp="E1", model=m, setup=s)
        if not rs: continue
        a = rate_row(rs, "target_sel"); acc = rate_row(rs, "acceptable_sel")
        fs = sum(1 for r in rs if r["first_is_target"])
        tl = [r for r in rs if r["term"] == "turn_limit"]; co = [r for r in rs if r["term"] == "completed"]
        mc = Counter(r["miss_class"] for r in rs)
        e1.append(dict(model=m, setup=s, n=a["n"], n_requests=a["n_requests"], target_selected=a["k"], rate=a["rate"],
                       wilson_lo=a["wilson_lo"], wilson_hi=a["wilson_hi"], req_boot_lo=a["req_lo"], req_boot_hi=a["req_hi"],
                       skill_boot_lo=a["skill_lo"], skill_boot_hi=a["skill_hi"], first_selection_is_target=fs,
                       acceptable_selected=acc["k"], acceptable_rate=acc["rate"],
                       completed=len(co), completed_target=sum(1 for r in co if r["target_sel"]),
                       turn_limit=len(tl), turn_limit_target=sum(1 for r in tl if r["target_sel"]),
                       miss_alt_equivalent=mc["alt_equivalent"], miss_alt_related=mc["alt_related_partial"],
                       miss_alt_inappropriate=mc["alt_inappropriate"], miss_alt_unassessable=mc["alt_unassessable"] + mc["alt_not_judged"],
                       miss_no_skill_completed=sum(1 for r in co if r["miss_class"] in ("builtin_only", "no_component_detected")),
                       miss_no_skill_turn_limit=sum(1 for r in tl if r["miss_class"] in ("builtin_only", "no_component_detected"))))
write_csv("e1_rates.csv", e1)
e1p = []
for m in MODELS:
    for a, b in [("alone", "pack20"), ("pack20", "crowd200"), ("crowd200", "crowd1000"), ("alone", "crowd1000")]:
        ra, rb = sel(exp="E1", model=m, setup=a), sel(exp="E1", model=m, setup=b)
        if ra and rb: e1p.append(dict(model=m, from_setup=a, to_setup=b, **paired_row(ra, rb, "target_sel")))
write_csv("e1_paired.csv", e1p)
# per-target E1 (designated target selection by setup, all models pooled per model)
e1t = []
for m in MODELS:
    for t in sorted({r["target"] for r in sel(exp="E1")}):
        row = dict(model=m, target=t)
        for s in E1S:
            rs = sel(exp="E1", model=m, setup=s, target=t); row[s] = f'{sum(r["target_sel"] for r in rs)}/{len(rs)}'
        e1t.append(row)
write_csv("e1_per_target.csv", e1t)

# ---------------------------------------------------------------- 4. E2 MCP
e2 = []
for m in MODELS:
    for s in E2S:
        rs = sel(exp="E2", model=m, setup=s)
        if not rs: continue
        nb = [r for r in rs if r["target"] not in BROWSER]; br = [r for r in rs if r["target"] in BROWSER]
        a = rate_row(rs, "target_sel"); c = rate_row(rs, "capable_server"); x = rate_row(nb, "target_sel")
        mc = Counter(r["miss_class"] for r in rs)
        e2.append(dict(model=m, setup=s, n=a["n"], strict=a["k"], strict_rate=a["rate"], strict_req_lo=a["req_lo"], strict_req_hi=a["req_hi"],
                       strict_skill_lo=a["skill_lo"], strict_skill_hi=a["skill_hi"],
                       nonbrowser_n=x["n"], nonbrowser_strict=x["k"], nonbrowser_rate=x["rate"], nonbrowser_req_lo=x["req_lo"], nonbrowser_req_hi=x["req_hi"],
                       browser_n=len(br), browser_strict=sum(r["target_sel"] for r in br), browser_capable_server=sum(r["capable_server"] for r in br),
                       capable_server=c["k"], capable_server_rate=c["rate"],
                       first_component_accepted=sum(1 for r in rs if r["first_is_target"]),
                       acceptable=sum(1 for r in rs if r["acceptable_sel"]),
                       turn_limit=sum(1 for r in rs if r["term"] == "turn_limit"),
                       turn_limit_browser=sum(1 for r in br if r["term"] == "turn_limit"),
                       toolsearch=sum(1 for r in rs if r["toolsearch"]),
                       miss_alt_equivalent=mc["alt_equivalent"], miss_alt_preliminary=mc["alt_preliminary_step"],
                       miss_alt_related=mc["alt_related_partial"], miss_alt_inappropriate=mc["alt_inappropriate"],
                       miss_builtin_only=mc["builtin_only"], miss_none=mc["no_component_detected"]))
write_csv("e2_mcp_rates.csv", e2)
e2p = []
for m in MODELS:
    for a, b in [("mcp_alone", "mcp_pack20"), ("mcp_pack20", "mcp_crowd200"), ("mcp_crowd200", "mcp_crowdall"), ("mcp_alone", "mcp_crowdall")]:
        ra, rb = sel(exp="E2", model=m, setup=a), sel(exp="E2", model=m, setup=b)
        if ra and rb:
            e2p.append(dict(model=m, from_setup=a, to_setup=b, subset="all20", **paired_row(ra, rb, "target_sel")))
            e2p.append(dict(model=m, from_setup=a, to_setup=b, subset="nonbrowser15", **paired_row([r for r in ra if r["target"] not in BROWSER], [r for r in rb if r["target"] not in BROWSER], "target_sel")))
write_csv("e2_paired.csv", e2p)

# ---------------------------------------------------------------- 5. E3 mixed + E3b
e3 = []
for m in MODELS:
    for s in ["sk_alone", "mixed_smaller", "mixed_larger"]:
        for kind in ["skill", "tool"]:
            rs = sel(model=m, setup=s, kind=kind)
            if not rs: continue
            a = rate_row(rs, "target_sel"); mc = Counter(r["miss_class"] for r in rs)
            e3.append(dict(model=m, setup=s, kind=kind, n=a["n"], strict=a["k"], strict_rate=a["rate"], req_lo=a["req_lo"], req_hi=a["req_hi"],
                           skill_lo=a["skill_lo"], skill_hi=a["skill_hi"],
                           capable_server=sum(1 for r in rs if r["capable_server"]), acceptable=sum(1 for r in rs if r["acceptable_sel"]),
                           overlapping_family_selected=sum(1 for r in rs if r["overlap_family"]),
                           turn_limit=sum(1 for r in rs if r["term"] == "turn_limit"),
                           miss_alt_equivalent=mc["alt_equivalent"], miss_alt_preliminary=mc["alt_preliminary_step"], miss_alt_related=mc["alt_related_partial"],
                           miss_alt_inappropriate=mc["alt_inappropriate"], miss_builtin_only=mc["builtin_only"], miss_none=mc["no_component_detected"],
                           builtin_only_completed=sum(1 for r in rs if r["miss_class"] == "builtin_only" and r["term"] == "completed"),
                           builtin_only_turn_limit=sum(1 for r in rs if r["miss_class"] == "builtin_only" and r["term"] == "turn_limit")))
write_csv("e3_mixed_rates.csv", e3)
# paired: mixed skill requests vs single-skill baseline (E1 alone, 3 turns, for the 20; E3b sk_alone, 4 turns, for 5)
e3p = []
for m in ["haiku", "sonnet"]:
    base = sel(exp="E1", model=m, setup="alone") + sel(exp="E3b", model=m, setup="sk_alone")
    for s in ["mixed_smaller", "mixed_larger"]:
        e3p.append(dict(model=m, comparison=f"skill: single-skill baseline -> {s}", **paired_row(base, sel(model=m, setup=s, kind="skill"), "target_sel")))
        e3p.append(dict(model=m, comparison=f"tool: mcp_alone -> {s}", **paired_row(sel(exp="E2", model=m, setup="mcp_alone"), sel(model=m, setup=s, kind="tool"), "target_sel")))
        e3p.append(dict(model=m, comparison=f"tool nonbrowser: mcp_alone -> {s}", **paired_row(
            [r for r in sel(exp="E2", model=m, setup="mcp_alone") if r["target"] not in BROWSER],
            [r for r in sel(model=m, setup=s, kind="tool") if r["target"] not in BROWSER], "target_sel")))
write_csv("e3_paired.csv", e3p)

# ---------------------------------------------------------------- 5b. extra tables for the post's charts (used by the post)
def req_rate_row(rs, metric):
    """Request-weighted rate: each request counts once, whatever its number of repetitions."""
    m = req_means(rs, metric); keys = sorted(m)
    f = lambda s: sum(m[x] for x in s) / len(s)
    b1 = boot(f, keys); b2 = boot(f, keys, True)
    return dict(n_requests=len(keys), n_runs=len(rs), rate=f(keys), req_lo=b1[0], req_hi=b1[1], skill_lo=b2[0], skill_hi=b2[1])
# paired change versus "alone" at every size (forest plot)
pva = []
for m in MODELS:
    for b in ["pack20", "crowd200", "crowd1000"]:
        ra, rb = sel(exp="E1", model=m, setup="alone"), sel(exp="E1", model=m, setup=b)
        if ra and rb: pva.append(dict(experiment="E1 skills", model=m, to_setup=b, **paired_row(ra, rb, "target_sel")))
for m in MODELS:
    ra = [r for r in sel(exp="E2", model=m, setup="mcp_alone") if r["target"] not in BROWSER]
    for b in ["mcp_pack20", "mcp_crowd200", "mcp_crowdall"]:
        rb = [r for r in sel(exp="E2", model=m, setup=b) if r["target"] not in BROWSER]
        if ra and rb: pva.append(dict(experiment="E2 MCP single-step tools", model=m, to_setup=b, **paired_row(ra, rb, "target_sel")))
write_csv("paired_vs_alone.csv", pva)
# rates behind the mixed-scenario chart, request-weighted, with intervals
e3c = []
for m in ["haiku", "sonnet"]:
    base = sel(exp="E1", model=m, setup="alone") + sel(exp="E3b", model=m, setup="sk_alone")
    e3c.append(dict(model=m, series="skill requests", setup="single component", **req_rate_row(base, "target_sel")))
    for s in ["mixed_smaller", "mixed_larger"]:
        e3c.append(dict(model=m, series="skill requests", setup=s, **req_rate_row(sel(model=m, setup=s, kind="skill"), "target_sel")))
    nb = lambda rs: [r for r in rs if r["target"] not in BROWSER]
    e3c.append(dict(model=m, series="single-step tool requests", setup="single component", **req_rate_row(nb(sel(exp="E2", model=m, setup="mcp_alone")), "target_sel")))
    for s in ["mixed_smaller", "mixed_larger"]:
        e3c.append(dict(model=m, series="single-step tool requests", setup=s, **req_rate_row(nb(sel(model=m, setup=s, kind="tool")), "target_sel")))
write_csv("e3_chart_rates.csv", e3c)

# ---------------------------------------------------------------- 6. builtin actions in mixed skill misses
bi = Counter()
for r in retained:
    if r["exp"] == "E3" and r["kind"] == "skill" and r["miss_class"] == "builtin_only": bi.update(set(r["builtins"]))
write_csv("e3_builtin_actions_in_skill_misses.csv", [dict(action=k, runs=v) for k, v in bi.most_common()])

# ---------------------------------------------------------------- 7. survey (expanded corpus, frozen)
S = json.load(open(P("scan.json"))); W = json.load(open(P("weight.json")))
uniq = {}
for r in S: uniq.setdefault(r["sha"], r)
repos_with = {r["repo"] for r in S}
wr = W["repos"]
def wget(x, k):
    return x.get(k) if isinstance(x, dict) else None
survey = dict(repositories_cloned=43, repositories_with_skills=len(repos_with), skill_files=len(S), distinct_files_sha1=len(uniq))
if isinstance(wr, dict): items = list(wr.items())
else: items = [(x.get("repo"), x) for x in wr]
survey["skills_name_dedup_within_repo"] = sum(int(wget(v, "skills") or 0) for _, v in items)
survey["skills_with_detected_test_or_eval_files"] = sum(int(wget(v, "w_eval") or wget(v, "with_eval") or 0) for _, v in items)
over = [k for k, v in items if (wget(v, "listing_chars") or 0) > 8000]
survey["repos_over_8000_char_listing"] = len(over)
sn = W.get("shared_names")
survey["names_in_2plus_repos"] = len(sn) if sn is not None else None
json.dump(survey, open(os.path.join(OUT, "survey.json"), "w"), indent=1)

# ---------------------------------------------------------------- 8. prompt audit
PR = json.load(open(P("prompts.json"))); PR2 = json.load(open(P("mcp/trending_skill_prompts.json")))
pa = []
for k, ps in list(PR.items()) + list(PR2.items()):
    name = k.split(":")[1]; toks = [t for t in name.split("-") if len(t) >= 3]
    for i, p in enumerate(ps):
        low = p.lower()
        explicit = bool(re.search(r"(^|\s)/[a-z][\w-]+", p) or re.search(r"\bskills?\b", low) or ("$" + name) in low or re.search(r"\buse (the )?" + re.escape(name), low))
        overlap = [t for t in toks if t in low]
        pa.append(dict(target=name, i=i, explicit_invocation_syntax=explicit, name_tokens_in_request=";".join(overlap)))
write_csv("prompt_audit.csv", pa)

# ---------------------------------------------------------------- 9. tokens and cost
PRICE = dict(input=10.0, cached=1.0, cache_write=12.5, output=50.0)   # gpt-6-astra standard, developers.openai.com model page, checked 2026-11-20
def gpt_cost(u):
    inp, ca, cw, out = u.get("input_tokens", 0), u.get("cached_input_tokens", 0), u.get("cache_write_input_tokens", 0), u.get("output_tokens", 0)
    unc = max(0, inp - ca - cw)
    return (unc * PRICE["input"] + ca * PRICE["cached"] + cw * PRICE["cache_write"] + out * PRICE["output"]) / 1e6
cost = []
cg = defaultdict(list)
for r in attempts:
    cg[(r["exp"], r["model"], r["access"], r["batch"], r["setup"])].append(r)
for (exp, m, acc, b, s), rs in sorted(cg.items()):
    row = dict(exp=exp, model=m, access=acc, batch=b, setup=s, attempts=len(rs))
    if m == "gpt":
        us = [r["usage"] for r in rs if r["usage"]]
        tot = Counter()
        for u in us: tot.update({k: v for k, v in u.items() if isinstance(v, int)})
        row.update(input_tokens=tot["input_tokens"], cached_input_tokens=tot["cached_input_tokens"], cache_write_input_tokens=tot["cache_write_input_tokens"],
                   output_tokens=tot["output_tokens"], reasoning_output_tokens=tot["reasoning_output_tokens"],
                   runs_over_272k_total_input=sum(1 for u in us if u.get("input_tokens", 0) > 272000),
                   list_price_usd=sum(gpt_cost(u) for u in us), billed_usd=(sum(gpt_cost(u) for u in us) if acc == "api_key" else 0.0),
                   cost_basis="OpenAI list price applied to reported usage fields" + ("" if acc == "api_key" else "; ChatGPT plan, not billed per token"))
    else:
        row.update(input_tokens=sum(r["in_tok"] or 0 for r in rs), cached_input_tokens=None, cache_write_input_tokens=None, output_tokens=None,
                   reasoning_output_tokens=None, runs_over_272k_total_input=None,
                   list_price_usd=sum(r["cost"] or 0 for r in rs), billed_usd=0.0,
                   cost_basis="Claude Code total_cost_usd estimate; Claude subscription, not billed per token")
    cost.append(row)
write_csv("cost_by_batch.csv", cost)
# mean usage per run, GPT, by setup (for the budget model)
gu = []
for (exp, m, acc, b, s), rs in sorted(cg.items()):
    if m != "gpt" or b != "main": continue
    us = [r["usage"] for r in rs if r["usage"]]
    if not us: continue
    mean = lambda k: sum(u.get(k, 0) for u in us) / len(us)
    gu.append(dict(exp=exp, setup=s, access=acc, runs=len(us), mean_input=mean("input_tokens"), mean_cached=mean("cached_input_tokens"),
                   mean_cache_write=mean("cache_write_input_tokens"), mean_output=mean("output_tokens"), mean_cost_usd=sum(gpt_cost(u) for u in us) / len(us)))
write_csv("gpt_usage_per_run.csv", gu)
cu = []
for exp in ["E1", "E2", "E3b", "E3"]:
    for m in ["haiku", "sonnet"]:
        for s in sorted({r["setup"] for r in retained if r["exp"] == exp}):
            rs = [r for r in retained if r["exp"] == exp and r["model"] == m and r["setup"] == s]
            if rs: cu.append(dict(exp=exp, model=m, setup=s, runs=len(rs), mean_total_input_tokens_all_turns=sum(r["in_tok"] or 0 for r in rs) / len(rs),
                                  mean_cost_usd=sum(r["cost"] or 0 for r in rs) / len(rs)))
write_csv("claude_usage_per_run.csv", cu)

# ---------------------------------------------------------------- 9b. MCP schema audit (structural only)
INV = json.load(open(P("mcp/tools_inventory.json")))
OKT = {"string", "number", "integer", "boolean", "object", "array", "null"}
src = lambda s_: "github-mcp-server toolsnaps (exact)" if s_ == "github" else ("chrome-devtools-mcp docs (reconstructed)" if s_ == "chrome-devtools" else ("playwright-mcp README (reconstructed)" if s_ == "playwright-mcp" else "LiveMCPBench (reconstructed)"))
sa = Counter(); problems = []
def tcheck(sch, path):
    if isinstance(sch, dict):
        t = sch.get("type"); ts = t if isinstance(t, list) else ([t] if isinstance(t, str) else [])
        for x in ts:
            if x not in OKT: problems.append((path, "bad type " + str(x)))
        if sch.get("type") == "array" and "items" not in sch: problems.append((path, "array without items"))
        for k, v in sch.items():
            if k in ("properties",) and isinstance(v, dict):
                for pk, pv in v.items(): tcheck(pv, path + "." + pk)
            elif k == "items": tcheck(v, path + "[]")
for s_, ts in INV.items():
    for t in ts:
        sa[src(s_)] += 1; sch = t.get("inputSchema") or {}
        if sch.get("type") != "object": problems.append((f"{s_}.{t['name']}", "root not object"))
        req = set(sch.get("required", [])); props = set((sch.get("properties") or {}).keys())
        if req - props: problems.append((f"{s_}.{t['name']}", "required not in properties: " + ",".join(sorted(req - props))))
        tcheck(sch, f"{s_}.{t['name']}")
json.dump({"tools_by_source": sa, "structural_problems": len(problems), "examples": problems[:30],
           "known_fidelity_loss": "reconstructed schemas keep parameter names, types, required flags and descriptions; enum constraints written in prose (e.g. chrome-devtools lighthouse_audit device: desktop|mobile) became plain strings"},
          open(os.path.join(OUT, "schema_audit.json"), "w"), indent=1)

# ---------------------------------------------------------------- 10. report
L = []
w = L.append
w("# Derived results\n")
w(f"Generated by `analysis/analyze.py` from unchanged result files (hashes in `derived/manifest.json`). Seed {SEED}, {B} bootstrap resamples.\n")
w("All rates are **designated-target selection within the observation window** (Claude Code: 3 turns in E1, 4 in E2/E3; Codex: one `exec` turn, no turn cap). Turn-limited runs stay in every denominator.\n")
w("E1 uses the isolated rerun for Sonnet / caveman / alone (18 runs) in place of the original 18 runs of that folder.\n")
w("## Audit\n")
w("| Exp | Model | Setup | Access | Attempts | Retained | Infra failures | Turn-limited | ...without target | Exposure (init counts) |\n|---|---|---|---|---|---|---|---|---|---|")
for a in audit: w(f'| {a["exp"]} | {a["model"]} | {a["setup"]} | {a["access"]}{"" if a["batch"]=="main" else " (excluded batch)"} | {a["attempts"]} | {a["retained"]} | {a["infra_failures"]} | {a["turn_limit"]} | {a["turn_limit_no_target"]} | {a["exposure_counts"]} |')
# raw event logs, counted from the retained records and the log files present, per experiment and model
rl = defaultdict(lambda: [0, 0])
for x in retained:
    if x["batch"] != "main": continue
    rl[(x["exp"], x["model"])][0] += 1; rl[(x["exp"], x["model"])][1] += x["has_raw"]
tot = sum(v[0] for v in rl.values()); got = sum(v[1] for v in rl.values())
w(f"\nRaw event logs (retained runs, main batches): {got:,} of {tot:,} have one. The `raw_log_coverage` column in `audit.csv` gives the count per setup.\n")
w("| Experiment | Model | Retained | With raw log |\n|---|---|---|---|")
for (e, m), (n, k) in sorted(rl.items()): w(f"| {e} | {m} | {n} | {k} |")
w("\nRuns without a raw log have only their result record: the selection fields were extracted when the run finished, and the event stream was not kept (methodology §7.5).\n")
nj = [x for x in retained if x["batch"] == "main" and x["miss_class"] == "alt_not_judged"]
njp = {(x["kind"], x["target"], x["i"], c) for x in nj for c in x["components"]}
njc = Counter((x["exp"], x["model"], x["setup"]) for x in nj)
w(f"Alternative ratings (`alt_judgments.json`) cover the alternatives selected in the first collection round. In the second round, {len(nj)} misses selected only alternatives that were never rated "
  f"({len(njp)} distinct request–alternative pairs): " + ", ".join(f"{e} {m} {s} {k}" for (e, m, s), k in sorted(njc.items())) +
  ". They are counted with the unassessable alternatives, never as equivalent, so rates that add equivalent alternatives are lower bounds for these setups.\n")
w("## E1: designated-target skill selection\n")
w("| Model | Setup | Selected | Rate | Request-cluster 95% | Two-stage (skill) 95% | First skill = target | Turn-limited (of which target) | Acceptable incl. equivalent alternatives |\n|---|---|---|---|---|---|---|---|---|")
for r in e1: w(f'| {r["model"]} | {r["setup"]} | {r["target_selected"]}/{r["n"]} | {pc(r["rate"])}% | {pc(r["req_boot_lo"])}–{pc(r["req_boot_hi"])} | {pc(r["skill_boot_lo"])}–{pc(r["skill_boot_hi"])} | {r["first_selection_is_target"]} | {r["turn_limit"]} ({r["turn_limit_target"]}) | {r["acceptable_selected"]} ({pc(r["acceptable_rate"])}%) |')
w("\nMiss breakdown:\n\n| Model | Setup | Equivalent alt. | Related alt. | Inappropriate alt. | Unassessable alt. | No skill, completed | No skill, turn-limited |\n|---|---|---|---|---|---|---|---|")
for r in e1: w(f'| {r["model"]} | {r["setup"]} | {r["miss_alt_equivalent"]} | {r["miss_alt_related"]} | {r["miss_alt_inappropriate"]} | {r["miss_alt_unassessable"]} | {r["miss_no_skill_completed"]} | {r["miss_no_skill_turn_limit"]} |')
w("\nPaired changes (percentage points; same requests in both conditions):\n\n| Model | From → to | Change | Request-cluster 95% | Two-stage 95% | Requests worse / better |\n|---|---|---|---|---|---|")
for r in e1p: w(f'| {r["model"]} | {r["from_setup"]} → {r["to_setup"]} | {100*r["diff"]:+.1f} | {100*r["req_lo"]:+.1f} to {100*r["req_hi"]:+.1f} | {100*r["skill_lo"]:+.1f} to {100*r["skill_hi"]:+.1f} | {r["requests_worse"]} / {r["requests_better"]} |')
w("\nGPT `alone` selected the target in 120/120 runs. Resampling cannot produce a failure from all-success data, so its bootstrap interval is degenerate; the Wilson interval (96.9–100%) is the one to quote.\n")
w("## E2: MCP tools only\n")
w("| Model | Setup | Strict accepted tool | Rate | Req. 95% | Non-browser 15 targets | Browser 5: strict / capable server | Capable server (secondary) | Turn-limited (browser) | ToolSearch used |\n|---|---|---|---|---|---|---|---|---|---|")
for r in e2: w(f'| {r["model"]} | {r["setup"]} | {r["strict"]}/{r["n"]} | {pc(r["strict_rate"])}% | {pc(r["strict_req_lo"])}–{pc(r["strict_req_hi"])} | {r["nonbrowser_strict"]}/{r["nonbrowser_n"]} ({pc(r["nonbrowser_rate"])}%) | {r["browser_strict"]} / {r["browser_capable_server"]} of {r["browser_n"]} | {pc(r["capable_server_rate"])}% | {r["turn_limit"]} ({r["turn_limit_browser"]}) | {r["toolsearch"]} |')
w("\nPaired changes:\n\n| Model | From → to | Subset | Change | Req. 95% | Two-stage 95% |\n|---|---|---|---|---|---|")
for r in e2p: w(f'| {r["model"]} | {r["from_setup"]} → {r["to_setup"]} | {r["subset"]} | {100*r["diff"]:+.1f} | {100*r["req_lo"]:+.1f} to {100*r["req_hi"]:+.1f} | {100*r["skill_lo"]:+.1f} to {100*r["skill_hi"]:+.1f} |')
w("\nMiss breakdown (E2): equivalent / preliminary step / related / inappropriate / built-in only / none\n")
for r in e2: w(f'- {r["model"]} {r["setup"]}: {r["miss_alt_equivalent"]} / {r["miss_alt_preliminary"]} / {r["miss_alt_related"]} / {r["miss_alt_inappropriate"]} / {r["miss_builtin_only"]} / {r["miss_none"]}')
w("\n## E3 constructed mixed scenarios and E3b\n")
w("| Model | Setup | Requests | Strict target | Rate | Req. 95% | Overlapping server/tool family selected | Built-in only (completed / turn-limited) | Turn-limited |\n|---|---|---|---|---|---|---|---|---|")
for r in e3: w(f'| {r["model"]} | {r["setup"]} | {r["kind"]} | {r["strict"]}/{r["n"]} | {pc(r["strict_rate"])}% | {pc(r["req_lo"])}–{pc(r["req_hi"])} | {r["overlapping_family_selected"]} | {r["builtin_only_completed"]} / {r["builtin_only_turn_limit"]} | {r["turn_limit"]} |')
w("\nPaired changes:\n\n| Model | Comparison | Change | Req. 95% | Two-stage 95% |\n|---|---|---|---|---|")
for r in e3p: w(f'| {r["model"]} | {r["comparison"]} | {100*r["diff"]:+.1f} | {100*r["req_lo"]:+.1f} to {100*r["req_hi"]:+.1f} | {100*r["skill_lo"]:+.1f} to {100*r["skill_hi"]:+.1f} |')
w("\nThe single-skill baseline for the 20 Experiment 1 skills ran with a 3-turn cap; the mixed scenarios had 4. The cap difference favours the mixed scenarios.\n")
w("Built-in actions in mixed-scenario skill misses: " + ", ".join(f"{k} {v}" for k, v in bi.most_common(8)) + ".\n")
w("## Survey (expanded corpus, frozen)\n")
w("```\n" + json.dumps(survey, indent=1) + "\n```\n")
w("## Prompt audit\n")
nexp = sum(1 for r in pa if r["explicit_invocation_syntax"]); nov = sum(1 for r in pa if r["name_tokens_in_request"])
w(f"{len(pa)} skill requests. Explicit invocation syntax (slash command, the word 'skill', `$name`, 'use the <name>'): {nexp}. Requests containing a token of the target's name (≥3 letters): {nov}.\n")
w("## Cost\n")
tb = sum(r["billed_usd"] for r in cost); tl = sum(r["list_price_usd"] for r in cost)
w(f"Billed per token (API key, GPT): ${tb:.2f}. List-price equivalent of everything, including subscription runs: ${tl:.2f}. Details: `cost_by_batch.csv`.\n")
RPT = os.path.join(HERE, "REPORT.md")
open(RPT, "w").write("\n".join(L))
print("wrote", RPT)
print("billed", round(tb, 2), "list", round(tl, 2), "judgments", len(JUD))
