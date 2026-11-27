# Follow-up protocol: finishing the study for at most $100 billed

**Status:** proposal. Nothing here has been run, and none of it is a result. It addresses the open limitations listed in `METHODOLOGY.md` §13.

**Budget rule.** At most **$100 billed**. Billed means OpenAI API usage priced from the reported usage fields at the [gpt-6-astra list price](https://developers.openai.com/api/docs/models/gpt-6-astra.md). Claude Code runs go through the existing Claude plan and are not billed per token; their list-price equivalent is shown for transparency. The cost model is `analysis/budget.py`, and the per-item estimates are in `analysis/derived/followup_budget.csv`.

## 1. What “complete” means here
When this is done, every cell of the final matrix will have a defensible value or an explicit, costed reason it was not run:

| | Skills only (E1) | MCP only (E2) | Constructed mix (E3) | Crossed skills × tools | Controls | Validation |
|---|---|---|---|---|---|---|
| Claude Haiku | done + 2 more filler samples | done + browser rerun | done | **new** | **new** | **new** |
| Claude Sonnet | done + 2 more filler samples | done + browser rerun | done | **new** (half the requests) | **new** | **new** |
| GPT (Codex) | done + cliff replication | 4 points (20 requests each at the large points) | not run: ~$1.5–2.2 per run (see §4) | not run | **new** | raw-logged subset |

## 2. Pipeline changes before any run
A new runner, `run_followup.py`, leaves the study's runners (`skills/run.py`, `skills/run_codex.py`, `mcp/run.py`) unchanged.
1. **Raw logs:** save the full ordered event stream from process start, including partial output on timeout, plus the exact command. Configuration manifests contain no credentials.
2. **Run metadata:** record the resolved model ID if the CLI reports one, the access route, the commit of the runner and the scoring code, and a catalogue manifest (installed names and hashes) per setup.
3. **First selection batch:** score the first selection batch before any stub result, denial or synthetic instruction is delivered. Parallel calls in that batch all count as “first”.
4. **Codex evidence:** keep command exit status and output.
5. **Arguments:** keep tool arguments, so multi-operation tools such as `issue_write` can be scored by operation.
6. **Pre-flight check per setup:** verify that the expected skills and MCP tools are exposed and that every server connected. A setup that fails is an infrastructure failure, not a routing miss.
7. **Detector tests:** run the detectors on known cases before use: a skill read, a failed read (missing file), alternative path forms, a variable path, and parallel tool calls.
8. **Schema repair:** add the missing `items` to the 85 reconstructed array parameters. The repaired inventory gets a new file name and hash; the study's runs used the current `mcp/tools_inventory.json`.
9. **Hard cap:** after each GPT run, add its list-price cost from the reported usage to a ledger file. Stop before starting a run that the projected cost would push past $100.
10. **Execution order:** randomise across setups within each item, with a seed. Do not run setups in sequence.

## 3. Frozen before running
- **Request subsamples.** GPT items use request `i = 0` for every target, which is fixed now, before any new run. C1 uses 40 requests drawn with seed 20261121 (2 per target).
- **Accepted sets.**
  - For each skill and tool target, retrieve candidate alternatives from the installed inventory: the top 15 by text similarity, plus every alternative that occurred in the study.
  - Rate them blind with the same rubric as `analysis/alt_judgments.json`.
  - Freeze `accepted_sets.json`.
  - Scores against these sets are confirmatory only for new runs.
- **Controls.**
  - 20 explicit-invocation positives, one per E1 target, for example “Use the pdf skill to merge a.pdf and b.pdf.”
  - 20 negatives that no installed skill should serve, for example “What is 17 × 23?” or “Translate ‘good morning’ into French.”
  - Control scores are reported separately from natural-request scores.
- **Primary metrics.** First-batch designated-target selection, with termination status. Any-time selection is secondary.

## 4. Budget and priority (GPT, billed)
Measured costs per run (API key, list price): E1-type setups $0.19–0.31; `mcp_alone` $0.29; `mcp_pack20` $0.35.

Modelled costs for the unmeasured setups use a base prompt of 18.1K tokens, about 4.1 model requests per run, and 82% of the estimated tool-definition tokens loaded. That last figure is fitted from `alone → pack20` and is consistent with Codex putting every MCP definition into context:
- `mcp_crowd200`: $0.83 (up to $0.94 if 100% load)
- `mcp_crowdall`: $2.08 ($2.48)
- `mixed_smaller`: $1.48 ($1.72)
- `mixed_larger`: $2.23 ($2.64)

The full remaining GPT design (876 runs) would cost about **$1,380** on the API, so it is out of scope.

| Order | Item | Runs | Estimate | High |
|---|---|---|---|---|
| 1 | **G1** E2 MCP curve at `i = 0` for all 20 targets: fill `mcp_pack20` (11), `mcp_crowd200` (20), `mcp_crowdall` (20). The first crowd200 and crowdall runs are the cost probes. If the measured cost projects past the cap, stop and re-plan before continuing. | 51 | $61.94 | $72.32 |
| 2 | **G2** Controls at 1,020 skills: 20 positives + 20 negatives | 40 | $12.22 | $12.22 |
| 3 | **G3** Replicate the Codex drop with a second filler sample (`crowd1000`, seed 2, `i = 0`) | 20 | $6.11 | $6.11 |
| 4 | **G4** Locate the drop: new 520-skill setup, `i = 0` (cut first if the cap binds) | 20 | $5.42 | $5.42 |
| 5 | **G5** Only if budget remains: the five trending skills alone, all 30 requests | 30 | $5.84 | $5.84 |
| | **Total** | 161 | **$91.54** | $101.91 → **capped at $100** |

**What gets cut if costs run high:** G5 first, then G4. G1 and G2 are the ones that make the GPT column readable.

**GPT in the mixed scenarios is not run.** Even one request per target in `mixed_larger` (45 runs) would cost about $100. If this cell matters later, the free option is the ChatGPT plan. It must run as a separately labelled batch, with a 20-run bridge: `mcp_alone`, `i = 0`, run on both routes and compared before any pooling. This is because plan runs carried about 60% more input tokens than API runs in the same setup. Throughput was about 4 runs per rate-limit window, so this takes roughly 1–2 days in the background.

## 5. Claude items (Claude plan; $0 billed)
| Item | Design | Runs | List-price equivalent |
|---|---|---|---|
| **C1** Observation window | 40 seeded requests × {`pack20`, `crowd1000`} × {3, 10 turns} × {Haiku, Sonnet}, paired. The 3-turn arm doubles as a raw-logged reproduction of the study's E1 rates on the same requests. | 320 | $16.92 |
| **C2** Fixtures | The 31 file-referencing E1 requests, with small valid files (PDF, XLSX, PPTX, DOCX, a minimal repo) identical across setups, × {`alone`, `crowd1000`} × 2 models | 124 | $4.00 |
| **C3** Filler samples | `crowd1000` rebuilt with seeds 8 and 9, all 120 requests × 2 models | 480 | $22.42 |
| **C4** Controls | As G2, × {`alone`, `crowd1000`} × 2 models | 160 | $5.16 |
| **C5** Crossed design | Nested pools. Skills {100, 400} × tools {20 targets only, all 791}, all four cells rerun in one randomised batch. Haiku: all 270 requests per cell. Sonnet: `i ∈ {0, 2, 4}`. The interaction is the difference between the tool-load effects at the two skill levels, with a paired bootstrap. | 1,620 | $89.26 |
| **C6** Browser targets | Non-terminal stubs: navigation returns a small page snapshot, the other tools return plausible results, and nothing says “stop”. 30 browser requests × {`alone`, `pack20`, `crowdall`} × 2 models, 8 turns | 180 | $19.84 |
| | **Total** | 2,884 | **$157.60** (high ≈ $240) |

**If the Claude plan's usage limits are tight,** drop Sonnet from C5. That cuts about $65 of list-price equivalent and loses only the Sonnet interaction estimate.

**Detector validation.** No extra runs are needed. Manually check 100 raw logs from C1–C6 and G1–G4, stratified by harness, setup and outcome (apparent hits and misses), and report agreement with the automatic detectors.

## 6. Time
- **GPT items:** about 1–2 hours at 4 parallel runs.
- **Claude items:** about 5–7 hours at 6 parallel runs, subject to plan limits.
- **Re-analysis:** `analyze.py` gains the new items, about 2 hours.
- **Write-up and figures:** half a day.

## 7. Decision rules, fixed now
- **G1 probe:** if the first `mcp_crowdall` run costs more than $3, drop `mcp_crowdall` to 10 targets (even target indices) and report it as such.
- **C1 observation window:** if 10 turns raise selection by 10 pp or more in any cell, the study's E1 rates for that model are reported mainly as “within 3 turns” and the 10-turn rates become the headline.
- **C3 filler samples:** the result is reported as the across-sample range. If the range at `crowd1000` exceeds 20 pp, generalisation claims about collection size are withdrawn.
- **C4 controls:** if positive controls are selected less than 90% of the time at `crowd1000`, the explicit-invocation path is itself degraded, and the paper says so.
