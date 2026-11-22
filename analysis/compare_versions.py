"""Compare analysis v2 (Claude MCP calls denied by headless permissions) with v3 (stub MCP servers allowed).

Run after `python3 analyze.py` and `ANALYSIS_VERSION=3 python3 analyze.py`. Writes derived/v3/v2_vs_v3.csv
(the headline rates side by side) and derived/v3/v2_vs_v3_runs.csv (matched runs: same model, setup,
target and request index, first attempt in each file), for v2 -> v3 and for the shared-folder v3 pass -> v3.
"""
import csv, json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
D2, D3 = os.path.join(HERE, "derived", "v2"), os.path.join(HERE, "derived", "v3")
ROOT = os.path.dirname(HERE)
# The five two-step browser targets, as defined in analyze.py
BROWSER = {"playwright-mcp.browser_take_screenshot", "playwright-mcp.browser_fill_form", "chrome-devtools.performance_start_trace",
           "chrome-devtools.list_console_messages", "chrome-devtools.lighthouse_audit"}


def rows(d, f):
    with open(os.path.join(d, f)) as h:
        return list(csv.DictReader(h))


out = []
# E2: strict and single-step rates per setup
for f, key, metrics in [
    ("e2_mcp_rates.csv", ("model", "setup"), ["strict_rate", "nonbrowser_rate", "capable_server_rate"]),
    ("e3_mixed_rates.csv", ("model", "setup", "kind"), ["strict_rate"]),
    ("e3_chart_rates.csv", ("model", "series", "setup"), ["rate"]),
    ("paired_vs_alone.csv", ("experiment", "model", "to_setup"), ["diff", "req_lo", "req_hi"]),
    ("e3_paired.csv", ("model", "comparison"), ["diff", "req_lo", "req_hi"]),
]:
    a = {tuple(r[k] for k in key): r for r in rows(D2, f)}
    b = {tuple(r[k] for k in key): r for r in rows(D3, f)}
    for k in sorted(set(a) | set(b)):
        for m in metrics:
            v2 = a.get(k, {}).get(m, ""); v3 = b.get(k, {}).get(m, "")
            delta = "" if "" in (v2, v3) else round(float(v3) - float(v2), 4)
            out.append({"table": f, "row": " | ".join(k), "metric": m, "v2": v2, "v3": v3, "v3_minus_v2": delta})
with open(os.path.join(D3, "v2_vs_v3.csv"), "w", newline="") as h:
    w = csv.DictWriter(h, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)


# Matched runs: first record per (model, env, target, i) in each file, Claude E2/E3 only
def first(path):
    seen = {}
    for line in open(path):
        r = json.loads(line)
        if r.get("error"): continue
        if r["env"].startswith("sk_alone"): continue   # E3b skills-alone runs were not rerun
        seen.setdefault((r["env"], r["target"], r["i"]), r)
    return seen


runs = []
# v2: MCP calls refused. v3_shared: first v3 pass, MCP allowed but runs shared a folder (and so Claude Code's
# auto-memory); stopped after E2 and part of E3. v3: the final pass, MCP allowed and every run in a fresh folder copy.
PAIRS = [("v2", "v3", "{m}_v2.jsonl", "{m}_v3.jsonl"), ("v3_shared", "v3", "{m}_v3_shared.jsonl", "{m}_v3.jsonl")]
for name_a, name_b, fa, fb in PAIRS:
    for m in ("haiku", "sonnet"):
        a = first(os.path.join(ROOT, "mcp", fa.format(m=m))); b = first(os.path.join(ROOT, "mcp", fb.format(m=m)))
        cell = defaultdict(Counter)
        for k in set(a) & set(b):
            setup = k[0].split("/")[0]
            part = "skill" if a[k]["kind"] == "skill" else ("tool-browser" if a[k]["target"] in BROWSER else "tool-single-step")
            c = cell[(setup, part)]
            c["n"] += 1; c["a_hit"] += bool(a[k]["hit_strict"]); c["b_hit"] += bool(b[k]["hit_strict"])
            c["hit_to_miss"] += a[k]["hit_strict"] and not b[k]["hit_strict"]
            c["miss_to_hit"] += b[k]["hit_strict"] and not a[k]["hit_strict"]
        for (setup, part), c in sorted(cell.items()):
            runs.append({"comparison": f"{name_a} -> {name_b}", "model": m, "setup": setup, "part": part, **c,
                         "a_rate": round(c["a_hit"] / c["n"], 4), "b_rate": round(c["b_hit"] / c["n"], 4)})
with open(os.path.join(D3, "v2_vs_v3_runs.csv"), "w", newline="") as h:
    fields = ["comparison", "model", "setup", "part", "n", "a_hit", "b_hit", "a_rate", "b_rate", "hit_to_miss", "miss_to_hit"]
    w = csv.DictWriter(h, fieldnames=fields); w.writeheader(); w.writerows(runs)
print("wrote", os.path.join(D3, "v2_vs_v3.csv"), "and v2_vs_v3_runs.csv")
