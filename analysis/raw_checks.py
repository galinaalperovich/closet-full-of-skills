"""Checks that need the raw event logs, which exist for the second-round Claude Code E2/E3 runs and the Fable E2 runs.

For every such run it reads mcp/raw/... and records:
  - whether each MCP call reached the stub server (result = stub text) or was refused or failed,
  - whether each Skill call returned without an error,
  - which built-in calls were refused by Claude Code's permission system,
  - which tool definitions ToolSearch loaded (used for the browser targets: was the target loaded
    before the stub reply ended the run?),
  - whether the run left notes in Claude Code's own auto-memory (each run starts with an empty one).
Writes derived/raw_checks.csv (per model x setup x request kind) and derived/raw_browser.csv.
"""
import csv, gzip, json, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MCP = os.path.join(os.path.dirname(HERE), "mcp")
OUT = os.path.join(HERE, "derived")
STUB = "Stub result: this tool is disabled in a test"
DENIED = "requested permissions to use"
BROWSER = {"playwright-mcp.browser_take_screenshot", "playwright-mcp.browser_fill_form", "chrome-devtools.performance_start_trace",
           "chrome-devtools.list_console_messages", "chrome-devtools.lighthouse_audit"}
SETUP = {"mcp_alone": "mcp_alone", "mcp_pack20": "mcp_pack20", "mcp_crowd200": "mcp_crowd200", "mcp_crowdall": "mcp_crowdall",
         "mixed_typical": "mixed_smaller", "mixed_heavy": "mixed_larger"}


def text_of(content):
    if isinstance(content, str): return content
    return " ".join(b.get("text", "") for b in content or [] if isinstance(b, dict))


def parse(path):
    d = json.load(gzip.open(os.path.join(MCP, path)))
    names, results, loaded = {}, {}, set()
    for line in d["stdout_events"].splitlines():
        try: e = json.loads(line)
        except ValueError: continue
        if e.get("type") not in ("assistant", "user"): continue
        for b in e.get("message", {}).get("content", []):
            if not isinstance(b, dict): continue
            if b.get("type") == "tool_use":
                names[b["id"]] = b.get("name", "")
            elif b.get("type") == "tool_result":
                c = b.get("content")
                results[b.get("tool_use_id")] = (bool(b.get("is_error")), text_of(c))
                if isinstance(c, list):
                    loaded |= {x.get("tool_name") for x in c if isinstance(x, dict) and x.get("type") == "tool_reference"}
    return names, results, loaded, len(d.get("memory_after") or {})


rows = defaultdict(Counter); browser = defaultdict(Counter)
for m, fn in (("haiku", "haiku_round2.jsonl"), ("sonnet", "sonnet_round2.jsonl"), ("fable", "fable.jsonl")):
    seen = set()
    for line in open(os.path.join(MCP, fn)):
        r = json.loads(line)
        key = (r["env"], r["target"], r["i"])
        if r.get("error") or key in seen or not r.get("raw"): continue   # first attempt without an infrastructure error
        seen.add(key)
        setup = SETUP[r["env"].split("/")[0]]
        part = "skill" if r["kind"] == "skill" else ("tool-browser" if r["target"] in BROWSER else "tool-single-step")
        names, results, loaded, mem = parse(r["raw"])
        c = rows[(m, setup, part)]; c["runs"] += 1; c["runs_saved_builtin_memory"] += mem > 0
        for tid, n in names.items():
            err, txt = results.get(tid, (None, ""))
            if n.startswith("mcp__"):
                c["mcp_calls"] += 1
                c["mcp_reached_stub"] += STUB in txt
                c["mcp_refused"] += DENIED in txt
                c["mcp_other_error"] += bool(err) and DENIED not in txt
                c["mcp_no_result"] += tid not in results
            elif n == "Skill":
                c["skill_calls"] += 1; c["skill_ok"] += err is False; c["skill_error"] += err is True
            elif n != "ToolSearch":
                c["builtin_calls"] += 1
                if DENIED in txt: c["builtin_refused"] += 1; c["refused:" + n] += 1
        if part == "tool-browser":
            acc = {"mcp__" + a.replace(".", "__", 1) for a in r["accept"]}
            b = browser[(m, setup)]; b["runs"] += 1
            b["target_selected"] += bool(r["hit_strict"])
            b["target_definition_loaded"] += bool(acc & loaded)
            b["loaded_but_not_called"] += bool(acc & loaded) and not r["hit_strict"]
            b["any_mcp_call"] += any(u.startswith("mcp:") for u in r["used"])

fields = ["model", "setup", "part", "runs", "mcp_calls", "mcp_reached_stub", "mcp_refused", "mcp_other_error", "mcp_no_result",
          "skill_calls", "skill_ok", "skill_error", "builtin_calls", "builtin_refused", "runs_saved_builtin_memory", "refused_by_tool"]
with open(os.path.join(OUT, "raw_checks.csv"), "w", newline="") as h:
    w = csv.DictWriter(h, fieldnames=fields); w.writeheader()
    for (m, s, p), c in sorted(rows.items()):
        ref = ";".join(f"{k[8:]}={v}" for k, v in sorted(c.items()) if k.startswith("refused:"))
        w.writerow({"model": m, "setup": s, "part": p, **{k: c[k] for k in fields[3:-1]}, "refused_by_tool": ref})
with open(os.path.join(OUT, "raw_browser.csv"), "w", newline="") as h:
    f2 = ["model", "setup", "runs", "target_selected", "target_definition_loaded", "loaded_but_not_called", "any_mcp_call"]
    w = csv.DictWriter(h, fieldnames=f2); w.writeheader()
    for (m, s), b in sorted(browser.items()): w.writerow({"model": m, "setup": s, **{k: b[k] for k in f2[2:]}})
tot = Counter()
for c in rows.values(): tot.update(c)
print(f"runs {tot['runs']}; MCP calls {tot['mcp_calls']}: reached stub {tot['mcp_reached_stub']}, refused {tot['mcp_refused']}, "
      f"other error {tot['mcp_other_error']}, no result {tot['mcp_no_result']}; Skill calls {tot['skill_calls']}: ok {tot['skill_ok']}, "
      f"error {tot['skill_error']}; built-in calls {tot['builtin_calls']}, refused {tot['builtin_refused']}; "
      f"runs that saved a note to Claude Code's own memory {tot['runs_saved_builtin_memory']}")
