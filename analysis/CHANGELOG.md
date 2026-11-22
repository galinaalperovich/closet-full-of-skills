# Change log: version 2 → version 3

Date: 22 November 2026. The Claude Code runs of Experiments 2 and 3, and the 18 E1 runs of the one affected E1 folder, were repeated after two setup errors were found. The rest of E1, E3b and every Codex run are unchanged. The version 2 result files are unchanged on disk, and `python3 analysis/analyze.py` still reproduces version 2; `ANALYSIS_VERSION=3` produces the numbers below (`derived/v3/`). Details are in `METHODOLOGY.md` §0.

## What was wrong

| Problem | Effect on version 2 | How it was found |
|---|---|---|
| **MCP calls were refused.** Headless Claude Code (`claude -p`) asks permission before running an MCP tool; with nobody to approve, every call returned “Claude requested permissions to use mcp__…, but you haven't granted it yet” instead of the stub result. | Which tool was called first is measured correctly. What the agent did after the refusal was not the documented design: retries, other tools, browser second steps, any-time selection. | A recorded example of a headless MCP call, made while building a selection checker, showed the refusal. |
| **Auto-memory carried over between runs.** Claude Code keeps a memory per folder path and loads it at every start. All runs of a setup shared one folder. | Agents answering the `memory.create_entities` requests saved notes with Claude Code's own memory; later runs in six E2/E3 folders (from 20 November 14:18) started with them. One E1 folder (Sonnet, `caveman`, `alone`) was affected too; its 18 runs were rerun. | The raw logs of the first v3 pass showed runs reading notes “saved in an earlier session”. |

## What was done

- All Claude Code E2/E3 runs repeated (2 × 1,020) with the stub MCP servers pre-approved (`ALLOW_MCP=1`) and every run in a fresh copy of its test folder (`ISOLATE=1`). Nothing else changed: Claude Code 2.1.328, models, folders, requests, tool definitions, stub text, turn limits.
- The 18 E1 runs of Sonnet / `caveman` / `alone` repeated the same way (`ISOLATE=1` in `run.py`), with the original command. Results in `sonnet_e1_caveman_v3.jsonl`, raw logs in `raw_e1/`; they replace the original 18 records in version 3.
- Raw event logs kept for every run (`mcp/raw/`, local paths removed). New `analysis/raw_checks.py`: all 1,677 MCP calls reached the stub, none were refused; 229 of 230 `Skill` calls returned without an error (the exception was a built-in skill, not a study skill).
- A first v3 pass with MCP allowed but shared folders (E2 complete, E3 partial) is kept as `mcp/*_v3_shared.jsonl`. New `analysis/compare_versions.py` compares v2, that pass and v3 run by run.
- Runner: `LOAD_MAX` waits for the machine's load to drop before starting a job; 8 parallel mixed-setup runs (up to 73 stub servers each) had made a 10-core laptop unresponsive.

## Effect on the numbers (Claude Code, v2 → v3)

| Measure | Haiku | Sonnet |
|---|---|---|
| MCP, 15 single-step targets: alone → 20 → ~220 → 791 | 86 → 79 → 78 → 78% becomes 84 → 82 → 79 → 80% | 92 → 81 → 77 → 77% becomes 88 → 76 → 78 → 77% |
| MCP, paired change alone → 791 (single-step) | −7.8 → −4.4 pp | −15.6 → −11.1 pp |
| MCP, paired change ~220 → 791 (single-step) | 0.0 → +1.1 pp | 0.0 → −1.1 pp |
| E1, Sonnet `alone` (caveman folder rerun) | unchanged | 334/360 (92.8%) → 339/360 (94.2%) |
| E1, Sonnet paired change alone → 1,020 skills | unchanged | −59.2 → −60.6 pp |
| Mixed, skill requests: baseline → smaller / larger | −48.0 / −55.3 → −46.0 / −58.0 pp | −49.6 / −58.9 → −49.3 / −60.0 pp |
| Mixed, single-step tool requests: alone → smaller / larger | −8.9 / −12.2 → −5.6 / −8.9 pp | −16.7 / −17.8 → −13.3 / −17.8 pp |

Matched run by run, requests flipped in both directions between versions (`derived/v3/v2_vs_v3_runs.csv`); no setup moved by more than 6 points. **The conclusions did not change.**

## Claims

| Version 2 | Version 3 | Status |
|---|---|---|
| Single-step MCP selection in Claude Code fell from 86–92% to 77–78% | From 84–88% to 77–80% | Corrected (numbers) |
| Flat from ~220 to 791 tools | Still flat: +1.1 and −1.1 pp | Unchanged |
| Browser targets: “the stub answered ‘reply with one short sentence’, and the run ended” | In v2 the permission refusal ended the run; in v3 the stub does. The raw logs show the target tool's definition had been loaded with `ToolSearch` in all 120 browser runs of the two larger setups, and the target was called in 20 | Corrected (mechanism), with new evidence |
| `ToolSearch` called in 81–95% of MCP runs | 62–92% | Corrected |
| Mixed setups: skill requests lost 48–59 pp, single-step tool requests 9–18 pp | 46–60 pp and 6–18 pp | Corrected (numbers) |
| Sonnet selected the skill alone in 93% of runs (334 of 360) | 94% (339 of 360), after rerunning the one E1 folder with a carried-over memory note | Corrected (numbers) |
| 76% of skill misses in the mixed setups used built-in tools only (306 of 401) | 79% (317 of 400) | Corrected (numbers) |
| “No retained run has a raw log” | Every v3 Claude Code E2/E3 run has one | Corrected |
| “Built-in web tools were not disabled, so a run can fetch public web pages” | Claude Code refused web searches and most page fetches in headless mode; Codex's own web search worked (46 of 175 E2 runs) | Corrected |
| Requests “written by me” | Written with an LLM | Corrected (wording) |

## New findings (exploratory)
1. **The memory target competes with Claude Code's own memory.** `memory.create_entities` was selected in 1 of 6 requests in every setup, alone included, in v2 and v3; in the other runs the agent saved the fact with its built-in memory.
2. **Codex had web search, Claude Code did not.** One more way the configurations differ.
3. **Auto-memory in E1:** five Sonnet `caveman` `alone` runs had started with a carried-over note, all misses. In the isolated rerun of that folder, 11 of 18 runs selected the skill (6 of 18 originally); four of the five affected runs became hits. Sonnet `alone` is now 94.2% instead of 92.8%.
4. **Alternatives not rated:** 13 of the 247 v3 misses with an alternative chose only alternatives the v2 rater never saw. They count as not judged.

---

# Change log: methodology v1 → v2 and blog draft v1 → v2

Date: 20 November 2026. This responds to `METHODOLOGY_REVIEW.md`. The historical result files are unchanged (their SHA-256 hashes are in `derived/v2/manifest.json`). Original metrics are kept next to the renamed or new ones.

Status labels:
- **Corrected:** the analysis or the statement was wrong or incomplete.
- **Narrowed:** the claim was kept, with a tighter scope.
- **Removed:** the claim was dropped.
- **Unresolved:** the current data cannot settle it; a follow-up is proposed.

## Analysis (review §3)

| Review item | What changed | Status |
|---|---|---|
| 3.1 Turn-limit exhaustion | `termination_status` derived separately. Capped runs stay in all denominators. Misses split by completed vs turn-limited. Counts reproduce the review exactly (Haiku 158/480, Sonnet 131/1,440). “No errors remained” replaced by an audit table. “Favours Codex slightly” replaced with “not quantified”. | Corrected |
| 3.2 Exact-target scoring | Metric renamed `designated_target_selection`. Added a blind, independent appropriateness rating for all 210 alternatives that occurred, with an `acceptable_component_selected` rate. Labelled retrospective. | Corrected |
| 3.3 Stub feedback | Added a first-observed-selection proxy. For skills it differs from the any-time metric in 9 of 2,400 E1 runs. For browser tools, post-stub behaviour dominates; this is now stated with the results. | Corrected |
| 3.4 Browser family score | v1 `hit` renamed `capable_server_selected` and demoted to secondary. Strict accepted-tool selection is primary. Non-browser targets are reported separately. `overlap_tool` renamed `overlapping_family_selected`, with no “served” language. | Corrected; **this changes the MCP headline** (see below) |
| 3.5 Detection and infrastructure | Detection labelled “Claude invocation attempt” and “Codex command proxy”. Audit of infrastructure failures, the excluded 429 batch, MCP connection status and init exposure counts. Fixed retry rule. Codex `list_mcp_resources*` calls reclassified from MCP alternatives to harness built-ins. Detector validation needs raw logs, so it is moved to the follow-up. | Corrected; validation unresolved |
| 3.6 Uncertainty | Paired request-cluster and two-stage (skill-level) bootstraps. The GPT `alone` interval is annotated. The “non-overlapping intervals” claim is removed. Seed, rules and code are published. | Corrected |

## Wording and claims (review §4, §6)

| v1 claim | v2 | Status |
|---|---|---|
| “Why your AI agent ignores its skills” | Title now names both skills and MCP and states the measured outcome | Narrowed |
| “The right skill fired” | “The designated skill was selected under our detection rule” | Narrowed |
| “Wrong skill” / “miss = wrong” | Alternatives rated. At 1,020 skills, 12 of GPT's 108 misses were equivalent alternatives | Corrected |
| “Most misses are silence” / “the agent just starts working” | “Most target misses involved no detected skill selection within the window”; the reason is not inferred | Narrowed |
| “Stubbing does not change the result” | Stubs preserve metadata but change later behaviour | Corrected |
| “Only the target skill is installed” | “Only the target experimental skill; harness capabilities remain” | Corrected |
| “20 good, unrelated skills” / “unrelated fillers” | “20 selected skills” / “sampled additional skills, some overlapping” | Corrected |
| “The harnesses fail differently” | “The tested configurations show different selection curves” | Narrowed |
| “Codex's budget causes the cliff” | One plausible explanation. New indirect evidence (cache writes grow 7K tokens while the listing grows about 44K) is reported as such | Unresolved |
| “Distinctive names survive” | Observed in this sample; the design does not isolate distinctiveness | Narrowed |
| “The model was confident it could do it itself” | Removed; text not retained | Removed |
| “Same mechanism, same failure” (MCP) | “A related routing problem; shared mechanisms not tested” | Narrowed |
| “MCP tools hold at about 80% even with 791 tools” (draft findings page) | That figure was the browser-family score. Under strict scoring all-target rates fall from 82–85% to 58–62%. Non-browser targets fall from 86–92% to 77–78%, then stay flat from 220 to 791 tools. | **Corrected** |
| “Tools hold, skills collapse in the mix” | In the two constructed scenarios, skill requests lost 48–59 pp and non-browser tool requests lost 9–18 pp. No interaction claim. | Narrowed |
| “Does installing skills make the agent smarter? No.” | “Installing more skills reduced designated-target selection in this test; task quality was not measured” | Narrowed |
| “Almost nobody tests skills” | “Bundled test/eval files detected for 2.6% of 6,908 sampled skills” | Narrowed |
| “The 35 most popular repositories” | “A selected sample of 42 popular skill repositories” (expanded corpus throughout) | Corrected |
| “732 duplicate names” (35-repo subset) | 831 names in two or more repositories (expanded corpus) | Corrected |
| “10K extra tokens on every request” | “In a single-turn Haiku pilot, about 10K more input tokens”; records not retained | Narrowed |
| “A real setup has fewer but more overlapping skills” | “Real installations may differ; their distribution was not sampled” | Narrowed |
| “mixed_typical / mixed_heavy” | Renamed “mixed_smaller / mixed_larger”, constructed scenarios | Corrected |
| Fixes (Tricks #1–6) | All marked as untested hypotheses, except that “fewer skills” is the tested manipulation | Narrowed |

## Cost (review §6.2)

| v1 | v2 | Status |
|---|---|---|
| “Cache writes = input − cached” | Codex reports `cache_write_input_tokens` directly; totals are sums over model requests | Corrected |
| “Cache writes are the dominant GPT cost because sessions are fresh” | Cache writes are 76–87% of list-price GPT cost per run in the API batches. The claim about the cause is removed. | Narrowed |
| GPT-6 Astra prices from secondary sources | Verified on the OpenAI model page (checked 20 November 2026). Long-context rule noted. Billed $171.73; Claude list-price equivalent $192.61 (not billed) | Corrected |

## New findings from the re-analysis (exploratory)
1. **MCP curves flatten after 20 tools in Claude Code.** For non-browser targets, `crowd200 → crowdall` changed by 0.0 pp for both models. This is consistent with deferred loading via `ToolSearch` (used in 81–95% of runs), but not tested as a mechanism.
2. **Browser targets measure the stub, not the agent.** With navigation tools available, the first call is a navigation step (a preliminary step in 24–31 runs per crowd setup), and the stub then ends the episode.
3. **GPT never selected `performance_start_trace`, even alone** (0/6). It used Codex's MCP discovery tools and the shell instead. The tool's `pageId` parameter is required in the source; there was no page.
4. **The access route changes the context:** five GPT plan runs averaged 138.6K input tokens against 86.6K on the API key.

## Unresolved, carried to `FOLLOWUP_PROTOCOL.md`
Detector validation; turn-budget sensitivity; fixture-backed folders; multiple filler samples; positive and negative controls; the crossed skills × tools design; browser targets with non-terminal stubs; the GPT MCP curve beyond 20 tools; GPT in the mixed scenarios.
