# Skill and MCP tool selection under load: methodology (version 2)

**Status:** revised after external review (`METHODOLOGY_REVIEW.md`), 20 November 2026. Version 1 is preserved unchanged as `METHODOLOGY_v1.md`; every change is listed in `analysis/CHANGELOG.md`. All numbers below are produced by `analysis/analyze.py` from the unchanged result files. The full generated tables are in `analysis/REPORT.md` and the CSVs in `analysis/derived/v2/`.

**Research question (exploratory):** in these model–harness configurations, how often is a designated skill, or an accepted MCP operation, selected within the observation window as the installed collection changes?

The study keeps three questions apart:

| Question | Measured here? |
|---|---|
| **Target retention:** was the designated component selected? | Yes. This is the primary metric. |
| **Appropriate routing:** was some acceptable component selected for the request? | Partly. Retrospective and exploratory (§7.4). |
| **Task performance:** was the request completed correctly? | No. Skill bodies and tool results are stubs; files do not exist. |

All paths are relative to `skill-trigger-spike/`.

---

## 1. Overview

| # | Experiment | Status | Retained runs |
|---|---|---|---|
| 0 | Static survey of a selected sample of popular skill repositories | Done | n/a (no model calls) |
| 1 | Skills only: does the designated skill get selected as more skills are installed? | Done: Haiku, Sonnet, GPT | 2,400 |
| 2 | MCP tools only: same design with published MCP tool definitions | Done: Haiku, Sonnet. GPT partial (`mcp_alone` 120, `mcp_pack20` 54) | 1,134 |
| 3 | Two constructed mixed scenarios, skills and MCP servers together (`mixed_smaller`, `mixed_larger`) | Done: Haiku, Sonnet. GPT not run | 1,080 |
| 3b | Five skills from GitHub-trending repositories, installed alone | Done: Haiku, Sonnet. GPT not run | 60 |

A **run** is one request sent once to one model–harness configuration in one setup. A proposed follow-up, kept separate from these results, is in `FOLLOWUP_PROTOCOL.md`.

---

## 2. Model–harness configurations

The systems differ in model, harness, tool affordances, budgets and permissions. Differences between them are differences between **configurations**. They are not attributed to the model alone or to the harness alone.

| Harness | Version | Model as requested | Access route | Skill exposure | Detection rule (what is recorded) |
|---|---|---|---|---|---|
| Claude Code | 2.1.328 | `--model haiku` (Claude Haiku 5.5), `--model sonnet` (Claude Sonnet 5.5) | Experimenter's Claude subscription | `.claude/skills/<name>/SKILL.md` in the working folder | **Invocation attempt:** a `Skill` tool call with that name. Loading success was not verified. MCP: a `mcp__<server>__<tool>` call. |
| Codex CLI | 0.160.0 | `gpt-6-astra`, reasoning effort `medium` | E1 and the first 170 E2 runs: API key in a scratch `CODEX_HOME`. Five E2 runs: ChatGPT subscription with `--ignore-user-config` | `.agents/skills`, a symlink to the same folder | **Command proxy:** a completed `command_execution` whose command text matches `skills/<name>/SKILL.md`. Exit status and output were not checked. MCP: an `mcp_tool_call` item on `item.started`. |

Model IDs are the aliases as requested. Resolved model IDs were not recorded.

**Observation windows.** Claude Code: `--max-turns 3` in E1 and `--max-turns 4` in E2/E3/E3b. Codex `exec`: one turn with no turn cap; timeouts were 300 s (E1) and 420 s (E2). The two harnesses therefore had different opportunities to select a component. The size and direction of that effect on cross-harness comparison is not quantified.

**Harness-provided capabilities.** “Alone” means one *experimental* component, not one available capability. The Claude Code `init` event reported 23 built-in skills in every setup (24/43/243/1,043 skills in total in E1), plus built-in tools (`Glob`, `Read`, `WebFetch`, `ToolSearch`…). MCP tools were deferred behind `ToolSearch`. Codex exposes a shell and its own MCP discovery tools (`list_mcp_resources`, `list_mcp_resource_templates`). The Codex tool inventory was not recorded.

**Documented listing limits** (motivation only, not a measured mechanism; sources: [Claude Code skills docs](https://code.claude.com/docs/en/skills.md), [Codex skills docs](https://learn.chatgpt.com/docs/build-skills), [Agent Skills spec](https://agentskills.io/specification)):
- **Claude Code:** the skill listing gets 1% of the context window. Each description is capped at 1,536 characters. When the listing overflows, descriptions of the least-used skills are dropped.
- **Codex:** the listing gets 2% of the context window, up to 10,000 tokens, and descriptions may be shortened or omitted.

What each model actually saw was **not captured** in any run.

---

## 3. Experiment 0: static survey

**Corpus (frozen, expanded version).** A selected sample of popular repositories found through the stated searches. It is not a verified ranking of the most popular repositories globally.
- Searches: `gh search repos` over `topic:claude-skills`, `topic:agent-skills`, `topic:claude-code-plugin`, `topic:claude-code-skills`, `topic:claude-code`, `topic:agents-md`, `topic:claude-code-subagents`, `skills in:name claude`, `topic:mcp-server` and `topic:ai-agents`, sorted by stars.
- From these, 36 repositories with `SKILL.md` files were hand-picked. Seven skill repositories from [GitHub trending (monthly)](https://github.com/trending?since=monthly) on 20 November 2026 were added.
- In total, 43 repositories were cloned and 42 contain skills. Commits are in `source_commits.tsv`.
- The earlier 35-repository subset used in the first blog draft is superseded. All survey numbers below come from the expanded corpus.

**Units.**
- 14,418 `SKILL.md` files.
- 7,848 distinct *files*, meaning distinct SHA-1 contents. Distinct files are not distinct capabilities.
- 6,908 skills after collapsing duplicate names within each repository. This is the unit for listing size and test detection.

**Checks.** `scan.py` runs static text parsing only, and no repository code was executed. The definitions are unchanged from v1:
- frontmatter and name rules;
- description length and trigger wording;
- body length;
- broken references;
- orphan files;
- undeclared Python dependencies;
- old model IDs and personal paths;
- test or eval files inside the skill folder.

**Headline numbers, bounded to what the scanner detects:**
- Each structural defect class affects 0–3% of distinct files. The classes are invalid frontmatter or name, broken links or paths, undeclared dependencies, personal paths and old model IDs.
- Some hygiene findings are more common: 4.8% of files exceed 500 body lines, 16.2% bundle files that are never referenced, and 47.9% have no explicit trigger wording.
- Bundled test or eval files were detected for 177 of 6,908 skills (2.6%). Tests can live outside the skill folder, so this does not mean the other skills were never tested. A matching filename also does not establish a meaningful evaluation.
- 16 of 42 repositories exceed 8,000 characters of listing if installed whole.
- 831 skill names occur in two or more repositories.

Full tables: `report2.txt`, `weight2.txt`, `analysis/derived/v2/survey.json`.

---

## 4. Experiment 1: skills only

### 4.1 Targets and requests
**20 selected target skills:**
- `anthropics/skills`: `pdf`, `xlsx`, `pptx`, `docx`, `webapp-testing`, `mcp-builder`, `frontend-design`
- `mattpocock/skills`: `tdd`, `grill-me`, `diagnosing-bugs`
- `obsidianmd/obsidian-skills`: `obsidian-markdown`, `json-canvas`
- `blader/humanizer`
- `vercel-labs/agent-skills`: `vercel-react-best-practices`, `web-design-guidelines`
- `addyosmani/agent-skills`: `security-and-hardening`
- `emilkowalski/skills`: `animate`
- `JuliusBrussee/caveman`
- `coreyhaines31/marketingskills`: `seo-audit`, `copywriting`

**Requests.** There are 120 experimenter-written requests, 6 per skill (`prompts.json`). They were written before any model run and not edited afterwards. The prompt audit (`derived/v2/prompt_audit.csv`) found none with explicit invocation syntax, meaning a slash command, the word “skill”, `$name` or “use the <name>”.

63 of the 150 skill requests (E1 plus E3b) contain a word from the target's name, for example “Grill me…” or “report.pdf”. Lexical overlap is not a flaw in itself, but it affects any interpretation about distinctiveness.

### 4.2 Setups
| Setup | Experimental skills installed |
|---|---|
| `alone` | The target only (one folder per target) |
| `pack20` | The 20 targets |
| `crowd200` | The 20 targets plus 200 sampled additional skills |
| `crowd1000` | The 20 targets plus 1,000 sampled additional skills |

The additional skills are **one** uniform random sample (seed 7) from **one** collection, `sickn33/agentic-awesome-skills`. Target names and the names of Claude Code's built-in skills are excluded. `crowd200` is a subset of `crowd1000`.

Some additional skills overlap with targets, for example 16 others containing “seo” and 14 containing “bug” or “debug”. Results describe this sampled collection, not installations in general (`build.py`).

### 4.3 Stubs
Each installed skill keeps its original `name`, `description` and `when_to_use`, re-serialised as YAML. The body is replaced with: “The instructions for this skill are omitted in this test. Reply with one short sentence.”

This preserves the metadata that initial routing depends on. It changes later behaviour, because the stub tells the agent to stop. Initial routing and later actions are analysed separately (§7.3).

### 4.4 Isolation and invocation
Each run is a fresh process in the setup's folder. The folder contains only the skills: **no files, no repository, no browser state.** This is a minimal-context routing test, not ordinary task execution. Requests that mention files (31 of 120) refer to files that do not exist.

Claude Code (`run.py`):
```
claude -p "<request>" --model <haiku|sonnet> --output-format stream-json --verbose \
  --setting-sources project --strict-mcp-config --no-session-persistence \
  --max-turns 3 --disallowedTools Bash
```

Codex (`run_codex.py`):
```
codex exec --json --ephemeral --skip-git-repo-check -s read-only \
  -c model_reasoning_effort="medium" "<request>"
```
`CODEX_HOME` was a scratch folder containing only an API-key login and `model = "gpt-6-astra"`.

### 4.5 Repetitions
Haiku 1, Sonnet 3, GPT 1 repetition per request: 480 + 1,440 + 480 runs, all executed on 20 November 2026. Repetitions are not new task scenarios: the 2,400 runs reuse 120 requests attached to 20 skills.

---

## 5. Experiment 2: MCP tools only

### 5.1 Tool definitions and fidelity
791 definitions from 73 servers (`mcp/tools_inventory.json`), obtained from published data without running the servers:

| Source | Tools | Fidelity label |
|---|---|---|
| [`github/github-mcp-server`](https://github.com/github/github-mcp-server) toolsnaps | 149 | Exact name, description and schema |
| [`ChromeDevTools/chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp) `docs/tool-reference.md` | 63 | Exact name and description; schema reconstructed |
| [`microsoft/playwright-mcp`](https://github.com/microsoft/playwright-mcp) README | 72 | Exact name and description; schema reconstructed |
| [LiveMCPBench](https://github.com/icip-cas/LiveMCPBench) `mcp_arg_*.json` | 507 | Name and description as published by the benchmark; schema reconstructed |

**Schema audit** (`derived/v2/schema_audit.json`, structural checks only):
- 85 array parameters in reconstructed schemas lack `items`. Eight target or accepted tools are affected, including `memory.create_entities`, `mcp-server-chart.generate_bar_chart` and `playwright-mcp.browser_fill_form`.
- Enum constraints written in prose became plain strings.
- Required flags were spot-checked against the pinned Chrome DevTools reference. For example, `pageId` is required there too.

Both harnesses accepted the definitions (no connection failures; see the audit). The study does not assert that schema differences cannot affect selection.

### 5.2 Stub MCP server
`mcp/stub_server.py` implements `initialize`, `tools/list`, `tools/call` and `ping` over stdio. Every call returns “Stub result: this tool is disabled in a test. Reply with one short sentence.” This is synthetic feedback that ends most episodes after the first call (§7.3).

### 5.3 Targets, requests and accepted operations
There are 20 target tools with 6 requests each (`mcp/mcp_targets.json`):
- GitHub: `create_issue`, `create_pull_request`, `search_code`, `list_notifications`
- Playwright MCP: `browser_take_screenshot`, `browser_fill_form`
- Chrome DevTools: `performance_start_trace`, `list_console_messages`, `lighthouse_audit`
- `context7`, `fetch`, `git`, `filesystem`, `memory`, `time`, `yahoo-finance`, `wikipedia`, `arxiv`, `youtube-transcript`, `mcp-server-chart`

Each target has an accepted set of equivalent tool names. Two examples:
- `github.create_issue` accepts `issue_write`.
- The stock-price target accepts the price tools of five servers.

The sets were written before the main runs, with one pilot-informed addition (`issue_write`). **Accepted sets are tool names. Arguments were not recorded**, so a multi-operation tool such as `issue_write` cannot be confirmed to have been called with a create operation.

**Browser targets.** Five targets need a page to be open first. In `mcp_alone` only the target tool exists. In larger setups, navigation tools exist too.

### 5.4 Setups
| Setup | Tools |
|---|---|
| `mcp_alone` | The target tool only, on its real server name |
| `mcp_pack20` | The 20 targets |
| `mcp_crowd200` | 20 targets plus 200 random others (seed 11) |
| `mcp_crowdall` | 20 targets plus all 771 others |

### 5.5 Invocation
Claude Code: as in §4.4, plus `--mcp-config` and `--max-turns 4`.

Codex: `codex exec --json --ephemeral --skip-git-repo-check [--ignore-user-config] -s read-only -c model="gpt-6-astra" -c model_reasoning_effort="medium" -c approval_policy="never" -c mcp_servers.<name>.command=... "<request>"`.

With `approval_policy="never"`, an MCP call is attempted but not executed. **Access-route change:** runs 1–170 used the API key and runs 171–175 the ChatGPT subscription.
- The five subscription runs averaged 138.6K input tokens, against 86.6K on the API key in the same setup. This is direct evidence that the execution environments differ.
- They are tagged separately, and the four successful ones are included only in pooled `mcp_pack20` counts that are always shown with their denominator.

---

## 6. Experiment 3: two constructed mixed scenarios, and 3b

| Setup (v1 name) | Skills | MCP tools |
|---|---|---|
| `mixed_smaller` (`mixed_typical`) | 25 targets + 75 sampled = 100 | 437: the full servers of the 20 tool targets plus four document servers |
| `mixed_larger` (`mixed_heavy`) | 25 targets + 375 sampled = 400 | all 791 |

**Skill targets:** the 20 from E1, plus five from trending repositories: `hallmark`, `security-audit`, `seo`, `ffmpeg-skill`, `ig-carousel`.

**Sampled skills:** 40% from 342 skills of trending and popular repositories, and 60% from `sickn33/agentic-awesome-skills` (seed 11). The 75 sampled skills are a subset of the 375.

Several overlaps were placed deliberately, for example `xlsx` next to an Excel MCP server. Both request sets ran in both setups: 150 skill requests and 120 tool requests.

These are **two constructed scenarios**. They change skills and tools at the same time, so they do not identify an interaction between skills and tools. They are not a sample of typical installations.

E3b runs the five trending skills `alone` with 4 turns.

---

## 7. Measurement (analysis version 2)

### 7.1 Termination status
Termination status is derived independently of selection:
- **completed:** Claude `success`, Codex `ok`
- **turn_limit:** Claude `error_max_turns`
- **api_error:** for example HTTP 429
- **timeout**
- **harness_error**
- **unknown**

Turn-limited runs are **retained** in every denominator. A target selected before the limit is still a hit. A run that hit the limit without the target is “not observed within the window”, never “never selected”.

### 7.2 Retry and denominators
- **Logical run key:** E1 uses (model, setup, target, request, repetition). E2/E3 use (model, setup, target, request).
- **Rule:** keep the first attempt in file order without an infrastructure error. The choice is never made by outcome.
- **Excluded batch:** the first GPT E1 batch through the subscription (476 of 480 attempts failed with HTTP 429) is excluded entirely and shown in the audit.
- **E2 failures:** one E2 GPT attempt failed with 429 and has no successful retry. It is reported as an infrastructure failure.
- **Other retries:** no other logical run has more than one attempt in the files.

### 7.3 Metrics
| Metric | Definition | Role |
|---|---|---|
| `designated_target_selection` | Target skill invoked (Claude) or its command proxy matched (Codex) at any point in the window; for tools, any tool name in the accepted set | Primary. Called “hit” in v1 |
| `first_observed_selection_is_target` | The first experimental component recorded is the target. A proxy: built-in actions may precede it, ToolSearch is stored separately, and repeated calls were deduplicated | Initial-routing proxy |
| `capable_server_selected` | v1 browser-family score: any tool on a server able to do the job | Secondary routing measure only |
| `overlapping_family_selected` | v1 `overlap_tool`: a skill request routed to an MCP server whose tool family overlaps the skill (e.g. any Excel tool for an `xlsx` request) | Descriptive flag; not evidence that the request was served |
| `acceptable_component_selected` | Target, or an alternative rated “equivalent” for that request (§7.4) | Retrospective, exploratory |

The any-time metric includes actions taken after stub feedback. For skills, `first_observed_selection_is_target` differs from the any-time metric in only 9 of 2,400 E1 runs, so the stub's effect on that headline is small.

For browser targets the stub feedback matters a lot. After a navigation call returns “Reply with one short sentence”, the requested screenshot, trace or audit is rarely reached (§9.2).

### 7.4 Alternatives: retrospective appropriateness rating
A target miss falls into one of these classes:
- **appropriate alternative:** the rater judged it “equivalent”
- **preliminary step:** for example opening a page
- **related or partial alternative**
- **inappropriate alternative**
- **unassessable**
- **built-in actions only**
- **no component detected**

The 210 distinct (request, alternative) pairs that occurred in target misses were rated by an independent LLM rater. The rater saw only the request, the two descriptions and the label definitions. It was blind to model, setup, frequency and outcome (`analysis/alt_judge_input.json`, `analysis/alt_judgments.json`).

The ratings were made after the results and only for alternatives that actually occurred, so they are labelled **retrospective/exploratory**. Accepted sets for new runs must be frozen beforehand (`FOLLOWUP_PROTOCOL.md`).

**Reclassification.** Codex's own discovery calls (`list_mcp_resources`, `list_mcp_resource_templates`) were stored as MCP calls in v1. In v2 they are classed as harness built-ins. This changes miss classes only, never `designated_target_selection`.

### 7.5 What the records cannot show
- Exact prompts.
- Rendered catalogues: target visibility, surviving description length, position.
- Agent text.
- Tool arguments and results.
- Codex command exit status.
- Ordered events, beyond the deduplicated `used` list and Claude's `first_tool`.

**No retained run has a raw log** (§11). Historical detection therefore cannot be validated retroactively. A validation rerun is part of the follow-up.

---

## 8. Statistics
- **Inferential target.** By default: variation over these requests in this sampled collection.
  - **Request-cluster bootstrap:** resample the 120 (or 150) requests; repetitions are averaged within request × condition.
  - **Two-stage bootstrap:** resample the 20 target components, then requests within them. This is a sensitivity analysis for a claim about skills like these, not about arbitrary skills.
  - Both use 2,000 resamples with seed 20261120.
- **Paired differences.** The same requests are kept in both conditions within each resample. Conditions are never resampled independently. The tables also report how many requests got worse or better.
- **GPT `alone`** (120/120). The bootstrap is degenerate for all-success data, so the Wilson interval (96.9–100%) is quoted. It does not imply certainty about future prompts.
- **Interval overlap.** Overlap is not used as a test, and the v1 claim that adjacent setups had non-overlapping intervals is withdrawn. Several adjacent request-cluster intervals overlap, for example Haiku `crowd200` against `crowd1000`.
- **Out of scope.** No claim treats the runs as 2,400 independent tasks. Filler-sample variation is not captured, because only one sample was drawn.

---

## 9. Results

### 9.1 Experiment 1: designated-target skill selection within the window

| Model | Setup | Selected | Rate | Request-cluster 95% | Two-stage 95% | Turn-limited (with target) |
|---|---|---|---|---|---|---|
| Haiku | alone | 94/120 | 78.3% | 70.8–85.0 | 66.6–89.2 | 13 (8) |
| Haiku | pack20 | 57/120 | 47.5% | 38.3–56.7 | 35.0–61.7 | 32 (6) |
| Haiku | crowd200 | 30/120 | 25.0% | 18.3–32.5 | 15.0–35.9 | 53 (6) |
| Haiku | crowd1000 | 19/120 | 15.8% | 9.2–22.5 | 5.8–28.3 | 60 (4) |
| Sonnet | alone | 334/360 | 92.8% | 88.1–96.9 | 83.6–99.4 | 2 (2) |
| Sonnet | pack20 | 272/360 | 75.6% | 68.0–82.5 | 62.8–87.5 | 3 (0) |
| Sonnet | crowd200 | 202/360 | 56.1% | 47.8–64.4 | 41.4–70.6 | 55 (0) |
| Sonnet | crowd1000 | 121/360 | 33.6% | 26.1–41.7 | 18.3–49.2 | 71 (0) |
| GPT | alone | 120/120 | 100% | Wilson 96.9–100 | n/a | – |
| GPT | pack20 | 119/120 | 99.2% | 97.5–100 | 96.7–100 | – |
| GPT | crowd200 | 100/120 | 83.3% | 76.7–89.2 | 70.8–93.3 | – |
| GPT | crowd1000 | 12/120 | 10.0% | 5.0–15.8 | 0.8–21.7 | – |

The v1 hit totals are reproduced exactly (`derived/v2/reproduction_e1.csv`).

**Turn limits.** 158 of 480 Haiku runs and 131 of 1,440 Sonnet runs ended at the 3-turn limit, concentrated in the larger setups. Selection within the window is what is measured. How many capped runs would have selected the target later is unknown.

**Paired change from `alone` to `crowd1000`:**

| Model | Change | Request-cluster 95% | Two-stage 95% | Requests worse / better |
|---|---|---|---|---|
| Haiku | −62.5 pp | −71.7 to −53.3 | −75.9 to −47.5 | 76 / 1 |
| Sonnet | −59.2 pp | −67.0 to −50.8 | −75.8 to −43.3 | 79 / 0 |
| GPT | −90.0 pp | −95.0 to −84.2 | −99.2 to −78.3 | 108 / 0 |

Every adjacent step is in `derived/v2/e1_paired.csv`. Every adjacent step is negative. The two-stage interval includes zero only for Haiku `crowd200→crowd1000` (−20.0 to +3.3) and for GPT `alone→pack20`.

**Target misses at `crowd1000`:**

| Model | Misses | Appropriate alternative | Related alternative | Inappropriate or unassessable | No skill, completed | No skill, turn-limited |
|---|---|---|---|---|---|---|
| Haiku | 101 | 1 | 0 | 3 | 44 | 53 |
| Sonnet | 239 | 8 | 0 | 1 | 160 | 70 |
| GPT | 108 | 12 | 11 | 6 | 79 | 0 |

Counting rated-equivalent alternatives as acceptable raises the `crowd1000` rate to 16.7% (Haiku), 35.8% (Sonnet) and 20.0% (GPT). Most target misses involved **no detected skill selection** within the window. Whether the agent “decided to do it itself” cannot be established, because its text was not retained.

### 9.2 Experiment 2: MCP tools only

| Model | Setup | Strict accepted tool (all 20) | Non-browser 15 targets | Browser 5: strict / capable server | Turn-limited |
|---|---|---|---|---|---|
| Haiku | mcp_alone | 99/120 (82.5%) | 77/90 (85.6%) | 22 / 22 of 30 | 30 |
| Haiku | mcp_pack20 | 81/120 (67.5%) | 71/90 (78.9%) | 10 / 13 | 44 |
| Haiku | mcp_crowd200 | 71/120 (59.2%) | 70/90 (77.8%) | 1 / 25 | 34 |
| Haiku | mcp_crowdall | 75/120 (62.5%) | 70/90 (77.8%) | 5 / 30 | 31 |
| Sonnet | mcp_alone | 102/120 (85.0%) | 83/90 (92.2%) | 19 / 19 | 0 |
| Sonnet | mcp_pack20 | 79/120 (65.8%) | 73/90 (81.1%) | 6 / 7 | 3 |
| Sonnet | mcp_crowd200 | 69/120 (57.5%) | 69/90 (76.7%) | 0 / 28 | 10 |
| Sonnet | mcp_crowdall | 69/120 (57.5%) | 69/90 (76.7%) | 0 / 30 | 9 |
| GPT | mcp_alone | 104/120 (86.7%) | 82/90 (91.1%) | 22 / 22 | – |
| GPT | mcp_pack20 (partial) | 33/54 (61.1%) | 22/24 (91.7%) | 11 / 18 of 30 | – |

- **Non-browser targets:** the paired change `mcp_alone→mcp_crowdall` was −7.8 pp for Haiku (request-cluster −14.4 to −2.2; two-stage −20.0 to +1.1) and −15.6 pp for Sonnet (−23.3 to −7.8; −31.1 to −2.2). Between `crowd200` and `crowdall`, the change was 0.0 for both models.
- **Claude Code:** used `ToolSearch` in 81–95% of runs.
- **Browser targets:** in larger setups, the first call is almost always a navigation tool. The independent rater classed it as a “preliminary step”: 24–31 runs in each Claude `crowd` setup. The stub's “reply with one short sentence” then ends the episode, so the requested operation is unobserved. The strict browser rate in larger setups mostly measures this stubbed environment. The capable-server rate measures only the first routing step. **Neither measures completion.**

### 9.3 Experiment 3 (constructed scenarios) and 3b

| Model | Setup | Skill requests: target | Tool requests: strict | Tool requests: non-browser strict |
|---|---|---|---|---|
| Haiku | single-skill baseline* | 119/150 (79.3%) | 99/120 (82.5%) | 85.6% |
| Haiku | mixed_smaller | 47/150 (31.3%) | 73/120 (60.8%) | 76.7% |
| Haiku | mixed_larger | 36/150 (24.0%) | 69/120 (57.5%) | 73.3% |
| Sonnet | single-skill baseline* | 362/390 runs (92.8%) | 102/120 (85.0%) | 92.2% |
| Sonnet | mixed_smaller | 65/150 (43.3%) | 68/120 (56.7%) | 75.6% |
| Sonnet | mixed_larger | 51/150 (34.0%) | 68/120 (56.7%) | 74.4% |

\* The baseline for the 20 E1 skills is E1 `alone` with a 3-turn window. The baseline for the five trending skills is E3b with 4 turns (Haiku 25/30, Sonnet 28/30). The mixed scenarios had 4 turns, so the window difference favours the mixed scenarios.

| Paired change | Haiku | Sonnet |
|---|---|---|
| Skill requests, baseline → `mixed_larger` | −55.3 pp (−63.3 to −46.7) | −58.9 pp (−66.7 to −51.1) |
| Non-browser tool requests, `mcp_alone` → `mixed_larger` | −12.2 pp (−20.0 to −5.6) | −17.8 pp (−26.7 to −10.0) |

**Skill-request misses** in the mixed scenarios were mostly built-in actions only: Haiku 78 and 90, Sonnet 62 and 76. The commonest were `Glob`, `Grep` and `Read`, consistent with searching the empty folder for files the requests mention. A share of these runs then hit the turn limit (Haiku 27/33, Sonnet 13/15).

**Overlapping tool families** were selected on 3–9 skill requests per setup.

These scenarios show a larger decline for skill requests than for single-step tool requests *in these two constructed setups*. They do not identify an interaction.

---

## 10. Tokens and cost

**Usage fields.**
- Codex reports `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens` and `output_tokens` (which includes `reasoning_output_tokens`) per `turn.completed`.
- In the API-key runs, cached plus cache-write tokens equal total input within a few tokens, so cache writes are a **provider-reported field**, not a derived difference.
- Totals are **sums over all model requests in the run**: about 4 requests per run in `mcp_pack20`, from input ÷ cache-write. They do not isolate the initial catalogue.
- Claude records keep `total_cost_usd` and summed input, cache-creation and cache-read tokens, also across turns.

**Price source.**
- [OpenAI model page for gpt-6-astra](https://developers.openai.com/api/docs/models/gpt-6-astra.md), checked 20 November 2026: input $10, cached input $1, cache writes $12.50, output $50 per million tokens.
- Requests over 272K input tokens are priced at 2× (1.5× for output). One run's *summed* input exceeded 272K. No single request can be shown to have done so, so standard rates are applied and that run's cost is a lower bound.

| Item | Runs | Basis | Amount |
|---|---|---|---|
| E1 GPT, API key | 480 | List price × reported usage | **$119.13 billed** |
| E2 GPT, API key | 170 | Same | **$52.60 billed** |
| GPT via ChatGPT plan (E1 excluded batch, five E2 runs) | 485 attempts | Plan, not billed per token | $0 (list-price equivalent $1.61) |
| Claude Code, all experiments | 4,020 | Claude Code's `total_cost_usd` estimate; Claude plan, not billed per token | $0 (list-price equivalent $192.61) |
| **Total billed** | | | **$171.73** |

Actual billing should be checked against the OpenAI usage dashboard. The figures above are list-price calculations from reported usage.

**Indirect evidence on catalogue size.** Codex's per-run cache writes grew from 13.2K (`alone`) to 20.3K tokens (`crowd1000`), while the installed listing grew by roughly 44K tokens (≈178K characters). This is consistent with a capped or shortened catalogue, but it does not show whether the target was visible.

Claude's summed input rose from 64.5K to 102.2K tokens per Sonnet run. That rise mixes catalogue size with extra turns. A single-turn Haiku pilot, whose records were not retained, measured about 33.4K against 43.3K input tokens.

---

## 11. Data, files, reproducing

| File | Content |
|---|---|
| `haiku.jsonl`, `sonnet.jsonl`, `gpt.jsonl` | E1 results (unchanged) |
| `gpt_subscription_failed.jsonl` | Excluded E1 batch (unchanged) |
| `mcp/haiku_v2.jsonl`, `mcp/sonnet_v2.jsonl`, `mcp/gpt_v2.jsonl` | E2/E3/E3b results (unchanged) |
| `analysis/analyze.py` | The single analysis entry point (this document's numbers) |
| `analysis/budget.py` | Follow-up cost model |
| `analysis/REPORT.md`, `analysis/derived/v2/*.csv`, `manifest.json` | Derived tables; SHA-256 of every input |
| `analysis/alt_judge_input.json`, `analysis/alt_judgments.json` | Blind alternative ratings |
| `analysis/CHANGELOG.md` | Claim-by-claim change log |
| `METHODOLOGY_v1.md` | Version 1, unchanged |
| `FOLLOWUP_PROTOCOL.md` | Proposed follow-up (not results) |
| Experiment scripts | `prompts.json`, `build.py`, `run.py`, `run_codex.py`, `mcp/*` |
| Survey files | `scan*.py/json`, `weight*`, `report*`, `source_commits.tsv` |

**Raw logs.** `mcp/raw/` was added to the runner during the experiment. No retained run has one: every Claude batch started under the earlier runner, and the GPT runs after the change ended in a rate limit.

**Reproducing.**
1. `python3 analysis/analyze.py` regenerates every number in this document.
2. Re-running the experiments requires the cloned repositories at the commits in `source_commits.tsv`.
3. Then run `build.py` / `mcp/build_v2.py` and the runners. Paths come from environment variables at the top of each script, with defaults inside this repository (see `README.md`).

---

## 12. Setup choices that remain, and their boundaries

| Choice | Kept as | Boundary on claims |
|---|---|---|
| Fixed turn limits | Bounded selection window | Rates are “within the window”; capped misses are not “never selected” |
| Exact-target scoring | Target retention | A miss can be an appropriate alternative; the appropriateness analysis is retrospective |
| Stub bodies and results | Initial routing test | Post-stub behaviour is not normal agent behaviour; browser operations beyond the first call are unobserved |
| Empty folders, Codex read-only, Claude `Bash` disallowed | Minimal-context routing benchmark | No claims about ordinary task execution or the reasons for abstaining |
| One filler sample, experimenter-written requests | Case study | Inference limited to this collection and these requests |
| Built-ins and native discovery (`ToolSearch`, Codex shell, Codex MCP discovery) | End-to-end configuration test | Differences are between configurations, not models |
| Mixed API and plan access for GPT E2 | Separately tagged batches | No equivalence assumed; the 5 plan runs are shown separately in the audit |
| Reconstructed MCP schemas | Fidelity-labelled | Structural defects listed; no claim that schemas cannot matter |
| Mixed scenarios | Two constructed scenarios | No interaction or “typical user” claims |
| Static survey | Selected corpus | Detected files only; no ecosystem prevalence claims |

**Mechanisms remain hypotheses.** Catalogue limits are one plausible explanation for the declines and for the Codex drop between 220 and 1,020 skills. Target visibility was not measured. The design does not isolate the effect of a skill's distinctiveness either: several distinctive targets kept higher rates in this sample.

**Mitigations are untested.** Mitigations discussed elsewhere (sharper descriptions, router skills, hooks, retrieval, larger budgets) are hypotheses for future evaluation. Installing fewer skills is the manipulation that was tested, but its effect on task quality was not measured.
