"""Second rating batch: the (request, alternative) pairs from target misses that the first batch did not cover.

The first batch (alt_judge_input.json, 210 pairs) came from the first collection round. This script collects every pair
from the result files the analysis now reads (Fable and GPT-6 Sol skills runs, and the third-round MCP runs) whose id
is not in alt_judgments.json, in the same format, and writes alt_judge_input_2.json. The rater's answers go to
alt_judgments_2.json; analyze.py reads both judgment files.

    python3 analysis/alt_judge_make_batch2.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
P = lambda *a: os.path.join(ROOT, *a)
done = {j["id"] for j in json.load(open(P("analysis", "alt_judgments.json")))}
T = json.load(open(P("mcp", "mcp_targets.json")))
P1 = json.load(open(P("skills", "prompts.json"))); P2 = json.load(open(P("mcp", "trending_skill_prompts.json")))
REQ = {("skill", k.split(":")[1]): v for k, v in list(P1.items()) + list(P2.items())}
REQ.update({("tool", k): v["prompts"] for k, v in T.items()})
INV = {f"{s}.{t['name']}": t.get("description", "") for s, ts in json.load(open(P("mcp", "tools_inventory.json"))).items() for t in ts}
HARNESS_MCP = {"list_mcp_resources", "list_mcp_resource_templates", "read_mcp_resource"}

def skill_desc(name):
    for base in ("envs/crowd1000", "envs2/mixed_heavy", "envs2/sk_alone/" + name):
        f = P(base, ".claude", "skills", name, "SKILL.md")
        if os.path.exists(f):
            m = re.search(r"^description:\s*(.*)$", open(f, errors="replace").read(), re.M)
            if m: return "Skill. " + m.group(1).strip().strip("'\"")
    return "Skill. (Harness built-in skill; description not captured)"
def desc(c):
    if c.startswith("skill:"): return skill_desc(c[6:])
    return "MCP tool. " + INV.get(c[4:], "(description not captured)")

items = {}
def add(kind, target, i, comp):
    cid = f"{kind}|{target}|{i}|{comp}"
    if cid in done or cid in items: return
    items[cid] = dict(id=cid, request=REQ[(kind, target)][i], designated_target=target,
                      target_description=desc(("skill:" if kind == "skill" else "mcp:") + target),
                      alternative=comp, alternative_description=desc(comp))
for f in ("skills/fable.jsonl", "skills/gpt_sol.jsonl"):                      # skills experiment
    for l in open(P(f)):
        r = json.loads(l)
        if r.get("error") or r["hit"]: continue
        for x in r.get("fired", []):
            n = x.split(":")[-1]
            if n != r["target"]: add("skill", r["target"], r["i"], "skill:" + n)
for f in ("mcp/haiku_round3.jsonl", "mcp/sonnet_round3.jsonl", "mcp/fable_round3.jsonl", "mcp/gpt_sol_round3.jsonl"):
    if not os.path.exists(P(f)): continue
    for l in open(P(f)):
        r = json.loads(l)
        if r.get("error") or r["hit_strict"]: continue
        for u in r.get("used", []):
            if u.startswith("builtin:"): continue
            if u.startswith("mcp:") and (u.split(".")[0] == "mcp:codex" or u.split(".", 1)[1] in HARNESS_MCP): continue
            add(r["kind"], r["target"], r["i"], u)
out = sorted(items.values(), key=lambda x: x["id"])
json.dump(out, open(P("analysis", "alt_judge_input_2.json"), "w"), indent=1, ensure_ascii=False)
print("pairs to rate:", len(out), "| skills:", sum(1 for x in out if x["id"].startswith("skill|")), "| tools:", sum(1 for x in out if x["id"].startswith("tool|")))
