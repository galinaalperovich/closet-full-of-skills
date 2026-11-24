#!/usr/bin/env python3
"""Cost model for the follow-up plan. Reads the derived usage tables; prints and writes derived/followup_budget.csv.
GPT per-run cost: measured where the setup was run on the API key; otherwise modelled as
  P = base_prompt + alpha * tool_definition_tokens + min(skill_listing, 10K cap)
  cost = P * (12.50 + (k-1) * 1.00) / 1e6 + output * 50 / 1e6
with base_prompt, k (model requests per run) and alpha fitted from mcp_alone -> mcp_pack20 (API runs).
Claude: list-price equivalent from Claude Code's total_cost_usd per run (billed $0 on the Claude plan)."""
import csv, json, os
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, "derived")
gu = {(r["exp"], r["setup"], r["access"]): r for r in csv.DictReader(open(os.path.join(D, "gpt_usage_per_run.csv")))}
cu = {(r["exp"], r["model"], r["setup"]): float(r["mean_cost_usd"]) for r in csv.DictReader(open(os.path.join(D, "claude_usage_per_run.csv")))}
a, p = gu[("E2", "mcp_alone", "api_key")], gu[("E2", "mcp_pack20", "api_key")]
base = float(a["mean_cache_write"]); k = float(p["mean_input"]) / float(p["mean_cache_write"]); out = float(p["mean_output"])
alpha = (float(p["mean_cache_write"]) - base) / (4200 - 260)          # 20 vs 1 tool definitions, chars/4 estimate
TOOLDEF = {"mcp_crowd200": 41300, "mcp_crowdall": 140000, "mixed_smaller": 83100, "mixed_larger": 140000}   # chars/4, from built envs
SKL = {"mixed_smaller": 8100, "mixed_larger": 10000}
def model_cost(setup, alpha_=alpha):
    P = base + alpha_ * TOOLDEF[setup] + SKL.get(setup, 0)
    return P * (12.5 + (k - 1) * 1.0) / 1e6 + out * 50 / 1e6
g = lambda e, s: float(gu[(e, s, "api_key")]["mean_cost_usd"])
GPT = {"e1_alone": g("E1", "alone"), "e1_crowd200": g("E1", "crowd200"), "e1_crowd1000": g("E1", "crowd1000"),
       "mcp_alone": g("E2", "mcp_alone"), "mcp_pack20": g("E2", "mcp_pack20")}
for s in TOOLDEF: GPT[s] = model_cost(s)
GPT_HI = {s: model_cost(s, 1.0) for s in TOOLDEF}
plan = [
 # executed in this order; the runner stops when cumulative billed cost (from reported usage) would pass $100
 ("G1", "E2 MCP curve, fixed subsample i=0 for all 20 targets: fill mcp_pack20 (11), mcp_crowd200 (20), mcp_crowdall (20). The first crowd200 and crowdall runs are the cost probes", [(11, "mcp_pack20"), (20, "mcp_crowd200"), (20, "mcp_crowdall")]),
 ("G2", "Controls at 1,020 skills: 20 explicit-invocation positives + 20 unrelated negatives", [(40, "e1_crowd1000")]),
 ("G3", "Replicate the Codex cliff with a second filler sample: crowd1000 seed 2, i=0 for 20 targets", [(20, "e1_crowd1000")]),
 ("G4", "Locate the cliff: new 520-skill point, i=0 for 20 targets (cut first if the cap binds)", [(20, "e1_crowd200")]),
 ("G5", "If budget remains: E3b five trending skills alone, all 30 requests", [(30, "e1_alone")]),
]
rows = []; tot = 0; tot_hi = 0
for pid, what, items in plan:
    c = sum(n * GPT[key] for n, key in items); chi = sum(n * GPT_HI.get(key, GPT[key]) for n, key in items)
    runs = sum(n for n, _ in items); tot += c; tot_hi += chi
    rows.append(dict(id=pid, harness="Codex / GPT (API key)", what=what, runs=runs, est_usd=round(c, 2), est_usd_high=round(chi, 2), billed="yes"))
claude = [
 ("C1", "Observation window: 40 seeded requests x {pack20, crowd1000} x {3, 10 turns} x {Haiku, Sonnet}", 320,
  40*2*(cu[("E1","haiku","pack20")]+cu[("E1","haiku","crowd1000")])*1.5 + 40*2*(cu[("E1","sonnet","pack20")]+cu[("E1","sonnet","crowd1000")])*1.5),
 ("C2", "Fixture-backed folders: 31 file-referencing requests x {alone, crowd1000} x 2 models", 124,
  31*(cu[("E1","haiku","alone")]+cu[("E1","haiku","crowd1000")]+cu[("E1","sonnet","alone")]+cu[("E1","sonnet","crowd1000")])),
 ("C3", "Filler-sample replication: crowd1000 with seeds 8 and 9, all 120 requests x 2 models", 480,
  2*120*(cu[("E1","haiku","crowd1000")]+cu[("E1","sonnet","crowd1000")])),
 ("C4", "Positive/negative controls (as G2) x {alone, crowd1000} x 2 models", 160,
  40*(cu[("E1","haiku","alone")]+cu[("E1","haiku","crowd1000")]+cu[("E1","sonnet","alone")]+cu[("E1","sonnet","crowd1000")])),
 ("C5", "Crossed skills x tools design: {100, 400 skills} x {20, 791 tools}, nested pools; Haiku all 270 requests, Sonnet i in {0,2,4}", 1080+540,
  1080*cu[("E3","haiku","mixed_larger")] + 540*cu[("E3","sonnet","mixed_larger")]),
 ("C6", "Browser targets with non-terminal stubs (navigate returns a page): 30 requests x {alone, pack20, crowdall} x 2 models, 8 turns", 180,
  90*cu[("E2","haiku","mcp_crowdall")]*2 + 90*cu[("E2","sonnet","mcp_crowdall")]*2),
]
ctot = 0
for pid, what, runs, c in claude:
    ctot += c; rows.append(dict(id=pid, harness="Claude Code (Claude plan)", what=what, runs=runs, est_usd=round(c, 2), est_usd_high=round(c * 1.5, 2), billed="no (list-price equivalent)"))
with open(os.path.join(D, "followup_budget.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(json.dumps(dict(base_prompt=round(base), requests_per_run=round(k, 2), alpha=round(alpha, 2), per_run_gpt={k_: round(v, 3) for k_, v in GPT.items()},
                      per_run_gpt_alpha1={k_: round(v, 3) for k_, v in GPT_HI.items()}), indent=1))
for r in rows: print(r["id"], r["runs"], r["est_usd"], r["est_usd_high"], r["what"][:90])
print("GPT billed total", round(tot, 2), "(high", round(tot_hi, 2), ")  Claude list-price equivalent", round(ctot, 2))
full = 66*GPT["mcp_pack20"] + 120*GPT["mcp_crowd200"] + 120*GPT["mcp_crowdall"] + 30*GPT["e1_alone"] + 270*GPT["mixed_smaller"] + 270*GPT["mixed_larger"]
print("Full remaining GPT design on API:", round(full), "USD")
