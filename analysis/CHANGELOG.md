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
