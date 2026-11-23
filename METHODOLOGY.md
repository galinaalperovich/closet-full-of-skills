# Skill and MCP tool selection under load: methodology (version 3)

**Status:** version 3, 22 November 2026 (two Codex setup notes added on 23 November, §2, §4.4, §5.5; no numbers changed). The Claude Code runs of Experiments 2 and 3, and the 18 E1 runs of one folder, were repeated after two setup errors were found (§0). Version 2, revised after external review (`METHODOLOGY_REVIEW.md`) on 20 November, is preserved unchanged as `METHODOLOGY_v2.md`, and version 1 as `METHODOLOGY_v1.md`. Every change is listed in `analysis/CHANGELOG.md`. All numbers below are produced by `ANALYSIS_VERSION=3 python3 analysis/analyze.py`; the full generated tables are in `analysis/REPORT_v3.md` and the CSVs in `analysis/derived/v3/`. `python3 analysis/analyze.py` without the variable still reproduces version 2 byte for byte.

**Research question (exploratory):** in these model–harness configurations, how often is a designated skill, or an accepted MCP operation, selected within the observation window as the installed collection changes?

The study keeps three questions apart:

| Question | Measured here? |
|---|---|
| **Target retention:** was the designated component selected? | Yes. This is the primary metric. |
| **Appropriate routing:** was some acceptable component selected for the request? | Partly. Retrospective and exploratory (§7.4). |
| **Task performance:** was the request completed correctly? | No. Skill bodies and tool results are stubs; files do not exist. |

All paths are relative to the repository root.

---

## 0. Version 3: what was wrong, and what was rerun

Two problems in how Claude Code was launched affected the Claude Code runs of Experiments 2 and 3 in version 2:

1. **MCP calls were refused.** In headless mode (`claude -p`), Claude Code asks for permission before it runs an MCP tool, and with nobody to approve, the call is refused. The v2 runner never pre-approved the stub servers, so every Claude Code MCP call returned “Claude requested permissions to use mcp__…, but you haven't granted it yet” instead of the stub result. The runner recorded selection from the call itself, so **which tool was called first is measured correctly**. Everything after that first call was not the documented design: what the agent did after the refusal, second steps of browser tasks, and the any-time selection metric. Codex runs are not affected (`approval_policy="never"` records the call before execution, §5.5). Skill loads are not affected (the `Skill` tool needs no approval; every v3 `Skill` call returned without an error).
2. **Claude Code's auto-memory carried over between runs.** Claude Code keeps an auto-memory per folder path and loads its index at the start of every session in that folder. All runs of one setup shared one folder. Agents answering the `memory.create_entities` requests usually saved the fact with Claude Code's own memory instead of calling the memory MCP tool, and later runs in the same folder then started with those notes (five short entries about a fictional manager, project and package manager). This affected six E2/E3 folders in v2 from 20 November 14:18 onwards, and one E1 folder (§9.1).

**What was rerun.** All Claude Code runs of E2 and E3, for Haiku and Sonnet (2 × 1,020), with two changes and nothing else:
- `--allowedTools mcp__<server>` for every configured server (`ALLOW_MCP=1` in `mcp/run2.py`), so calls reach the stub;
- every run in a fresh copy of its test folder, at a new path with the same folder name (`ISOLATE=1`), so every run starts with an empty auto-memory. Notes a run saves are kept in its raw log.

Harness version (2.1.328), models, folders, requests, tool definitions, stub text and turn limits are unchanged. A first v3 pass with MCP allowed but shared folders (E2 complete, E3 partial) is kept as `mcp/*_v3_shared.jsonl` for comparison.

**Also rerun: the one affected E1 folder.** The 18 runs of Sonnet, `caveman`, `alone` (6 requests × 3 repetitions) were repeated the same way, one fresh folder per run (`ISOLATE=1` in `run.py`), with the original command and 3-turn limit. Results are in `sonnet_e1_caveman_v3.jsonl` and replace the original 18 records in version 3 (§9.1). The rest of E1, E3b and every Codex run are unchanged. The original result files are unchanged on disk.

**Raw logs.** Every v3 run kept its full event stream (`mcp/raw/` and, for the E1 rerun, `raw_e1/`, with local paths removed). `analysis/raw_checks.py` uses them to check what the records alone could not (§7.5).

---

## 1. Overview

| # | Experiment | Status | Retained runs |
|---|---|---|---|
| 0 | Static survey of a selected sample of popular skill repositories | Done | n/a (no model calls) |
| 1 | Skills only: does the designated skill get selected as more skills are installed? | Done: Haiku, Sonnet, GPT | 2,400 |
| 2 | MCP tools only: same design with published MCP tool definitions | Done: Haiku, Sonnet (rerun in v3). GPT partial (`mcp_alone` 120, `mcp_pack20` 54) | 1,134 |
| 3 | Two constructed mixed scenarios, skills and MCP servers together (`mixed_smaller`, `mixed_larger`) | Done: Haiku, Sonnet (rerun in v3). GPT not run | 1,080 |
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

**Harness-provided capabilities.** “Alone” means one *experimental* component, not one available capability. The Claude Code `init` event reported 23 built-in skills in every setup (24/43/243/1,043 skills in total in E1), plus 27 built-in tools. The v3 raw logs record the list: `Glob`, `Grep`, `Read`, `Write`, `Edit`, `NotebookEdit`, `WebSearch`, `ToolSearch`, `Skill`, `Task`, and tools that came from the Claude desktop app environment the runs were launched from (`Artifact`, `CronCreate`, `PushNotification`, `SendMessage`, `Workflow` and others). `Bash` was disallowed. MCP tools and some built-ins (such as `WebFetch`) were deferred behind `ToolSearch`. Codex exposes a shell and its own MCP discovery tools (`list_mcp_resources`, `list_mcp_resource_templates`). The Codex tool inventory was not recorded. Codex 0.160.0 also installs 5 bundled skills into `$CODEX_HOME/skills/.system` on first start (`imagegen`, `openai-docs`, `review-agent`, `skill-creator`, `skill-installer`), enabled by default. The study did not turn them off, so they were very likely listed in every Codex run, and “alone” meant the target plus 5 bundled skills (§4.4).

**Permissions (Claude Code).** Runs used the default permission mode with nobody to approve, so any call that needed approval was refused: `WebSearch` always, `WebFetch` except for a few pre-approved documentation sites, searches and reads outside the test folder, writes into the test folder, and most subagent launches. Reads and writes in Claude Code's own memory and session scratch folders were allowed. Codex, by contrast, completed its own built-in web search in 46 of its 175 E2 runs, so web search was an alternative route for GPT but not for Claude. This is one more way the configurations differ. In v2 this also refused every MCP call (§0). In v3 only the stub MCP servers were pre-approved. The raw-log counts are in `derived/v3/raw_checks.csv`.

**Auto-memory (Claude Code).** On, as by default. In v3 each run starts with an empty memory (§0).

**Documented listing limits** (motivation only, not a measured mechanism; sources: [Claude Code skills docs](https://code.claude.com/docs/en/skills.md), [Codex skills docs](https://learn.chatgpt.com/docs/build-skills), [Agent Skills spec](https://agentskills.io/specification)):
- **Claude Code:** the skill listing gets 1% of the context window. Each description is capped at 1,536 characters. When the listing overflows, descriptions of the least-used skills are dropped.
- **Codex:** the listing gets 2% of the context window, up to 10,000 tokens, and descriptions may be shortened or omitted.

The rendered listing each model received was **not captured** in any run. For the v3 Claude Code E2/E3 runs, the raw `init` event records the names of the skills and tools that were exposed, but not the text the model saw.

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

**Requests.** There are 120 requests, 6 per skill (`prompts.json`), written with an LLM. They were written before any model run and not edited afterwards. The prompt audit (`derived/v2/prompt_audit.csv`) found none with explicit invocation syntax, meaning a slash command, the word “skill”, `$name` or “use the <name>”.

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
The 18 rerun runs of version 3 (§9.1) used the same command in a fresh copy of the folder.

Codex (`run_codex.py`):
```
codex exec --json --ephemeral --skip-git-repo-check -s read-only \
  -c model_reasoning_effort="medium" "<request>"
```
`CODEX_HOME` was a scratch folder containing only an API-key login and `model = "gpt-6-astra"`. On first start Codex adds its 5 bundled skills to that folder (§2). They were not turned off (`-c skills.bundled.enabled=false` does that), so they were very likely listed next to the experimental skills in every setup. The skill detector matches `skills/<name>/SKILL.md`, which does not match `skills/.system/<name>/SKILL.md`, so a read of a bundled skill would have been recorded as no skill rather than as another skill. This affects only how misses are classified, not hits. Found on 2026-11-23 while checking a Codex detector against recorded `codex exec` runs with the same Codex version.

### 4.5 Repetitions
Haiku 1, Sonnet 3, GPT 1 repetition per request: 480 + 1,440 + 480 runs, all executed on 20 November 2026. The 18 Sonnet runs of `caveman` `alone` were repeated on 22 November (§9.1). Repetitions are not new task scenarios: the 2,400 runs reuse 120 requests attached to 20 skills.

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
`mcp/stub_server.py` implements `initialize`, `tools/list`, `tools/call` and `ping` over stdio. Every call returns “Stub result: this tool is disabled in a test. Reply with one short sentence.” This is synthetic feedback that ends most episodes after the first call (§7.3). In the v2 Claude Code runs the stub was never reached, because the calls were refused (§0). In v3, every Claude Code MCP call returned the stub text (`derived/v3/raw_checks.csv`).

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
Claude Code: as in §4.4, plus `--mcp-config` and `--max-turns 4`. In v3, also `--allowedTools mcp__<server>,…` for every configured server, and each run in a fresh copy of the test folder (§0).

Codex: `codex exec --json --ephemeral --skip-git-repo-check [--ignore-user-config] -s read-only -c model="gpt-6-astra" -c model_reasoning_effort="medium" -c approval_policy="never" -c mcp_servers.<name>.command=... "<request>"`.

With `approval_policy="never"`, an MCP call is attempted but not executed: Codex records the call the model made and returns “MCP tool call requires approval, but approval policy is never” instead of the stub result. Selection is therefore observed, but what the agent did next was a reaction to that error. Servers can be pre-approved with `-c mcp_servers.<name>.default_tools_approval_mode="approve"`; the study did not do this, and the Codex MCP runs were not repeated. A stub server that fails to start leaves no trace in the Codex output, so a GPT MCP miss cannot be told apart from a server that never connected. **Access-route change:** runs 1–170 used the API key and runs 171–175 the ChatGPT subscription.
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

## 7. Measurement (analysis versions 2 and 3)

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

The ratings were made after the results and only for alternatives that actually occurred, so they are labelled **retrospective/exploratory**. They were made for the version 2 runs. In version 3, 13 of the 247 Claude Code E2/E3 misses that selected an alternative chose only alternatives the rater never saw (15 distinct pairs). Those count as “not judged”, never as acceptable, so the v3 acceptable rates are, if anything, slightly low. Accepted sets for new runs must be frozen beforehand (`FOLLOWUP_PROTOCOL.md`).

**Reclassification.** Codex's own discovery calls (`list_mcp_resources`, `list_mcp_resource_templates`) were stored as MCP calls in v1. In v2 they are classed as harness built-ins. This changes miss classes only, never `designated_target_selection`.

### 7.5 What the records cannot show
- Exact prompts.
- Rendered catalogues: target visibility, surviving description length, position.
- Agent text.
- Tool arguments and results.
- Codex command exit status.
- Ordered events, beyond the deduplicated `used` list and Claude's `first_tool`.

**Raw logs exist only for the v3 Claude Code E2/E3 runs** (§0, §11). For those runs the list above is answered by the event stream: agent text, tool arguments and results, and event order. E1, E3b and all Codex runs have no raw log, so their detection cannot be validated retroactively. A validation rerun for them is part of the follow-up.

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
| Sonnet | alone | 339/360 | 94.2% | 90.0–97.8 | 87.2–99.4 | 2 (2) |
| Sonnet | pack20 | 272/360 | 75.6% | 68.0–82.5 | 62.8–87.5 | 3 (0) |
| Sonnet | crowd200 | 202/360 | 56.1% | 47.8–64.4 | 41.4–70.6 | 55 (0) |
| Sonnet | crowd1000 | 121/360 | 33.6% | 26.1–41.7 | 18.3–49.2 | 71 (0) |
| GPT | alone | 120/120 | 100% | Wilson 96.9–100 | n/a | – |
| GPT | pack20 | 119/120 | 99.2% | 97.5–100 | 96.7–100 | – |
| GPT | crowd200 | 100/120 | 83.3% | 76.7–89.2 | 70.8–93.3 | – |
| GPT | crowd1000 | 12/120 | 10.0% | 5.0–15.8 | 0.8–21.7 | – |

The v1 hit totals are reproduced exactly from the original records (`derived/v2/reproduction_e1.csv`; version 3 repeats the check in `derived/v3/reproduction_e1.csv`). The Sonnet `alone` row uses the 18 rerun records for `caveman`.

**Turn limits.** 158 of 480 Haiku runs and 131 of 1,440 Sonnet runs ended at the 3-turn limit, concentrated in the larger setups. Selection within the window is what is measured. How many capped runs would have selected the target later is unknown.

**Auto-memory in E1 (found and rerun in version 3).** One E1 folder had a carried-over memory note: Sonnet, `caveman`, `alone`. Two runs of one request saved “keep answers short” with Claude Code's memory instead of loading the skill (their first action was `Write`), and up to five runs that finished after them started with that note. Haiku's E1 runs had finished before the note was written, and no other E1 folder had memory notes. The 18 runs of that folder were repeated with one fresh folder per run: **11 of 18** selected the skill, against 6 of 18 originally, so Sonnet `alone` is 339/360 (94.2%) instead of 334/360 (92.8%). The gain is where the note could have mattered: the five runs that had started with the note went from 0 to 4 hits in the rerun, and the request whose runs wrote the note went from 0 to 1 of 3. One rerun saved a memory note again, which no other run could see. No rerun had an error.

**Paired change from `alone` to `crowd1000`:**

| Model | Change | Request-cluster 95% | Two-stage 95% | Requests worse / better |
|---|---|---|---|---|
| Haiku | −62.5 pp | −71.7 to −53.3 | −75.9 to −47.5 | 76 / 1 |
| Sonnet | −60.6 pp | −68.6 to −52.5 | −76.4 to −44.7 | 82 / 0 |
| GPT | −90.0 pp | −95.0 to −84.2 | −99.2 to −78.3 | 108 / 0 |

Every adjacent step is in `derived/v3/e1_paired.csv`. Every adjacent step is negative. The two-stage interval includes zero only for Haiku `crowd200→crowd1000` (−20.0 to +3.3) and for GPT `alone→pack20`.

**Target misses at `crowd1000`:**

| Model | Misses | Appropriate alternative | Related alternative | Inappropriate or unassessable | No skill, completed | No skill, turn-limited |
|---|---|---|---|---|---|---|
| Haiku | 101 | 1 | 0 | 3 | 44 | 53 |
| Sonnet | 239 | 8 | 0 | 1 | 160 | 70 |
| GPT | 108 | 12 | 11 | 6 | 79 | 0 |

Counting rated-equivalent alternatives as acceptable raises the `crowd1000` rate to 16.7% (Haiku), 35.8% (Sonnet) and 20.0% (GPT). Most target misses involved **no detected skill selection** within the window. Whether the agent “decided to do it itself” cannot be established, because its text was not retained.

### 9.2 Experiment 2: MCP tools only

Claude Code rows are version 3 (MCP allowed, one fresh folder per run). GPT rows are unchanged from version 2.

| Model | Setup | Strict accepted tool (all 20) | Non-browser 15 targets | Browser 5: strict / capable server | Turn-limited | ToolSearch called |
|---|---|---|---|---|---|---|
| Haiku | mcp_alone | 95/120 (79.2%) | 76/90 (84.4%) | 19 / 19 of 30 | 32 | 107/120 |
| Haiku | mcp_pack20 | 83/120 (69.2%) | 74/90 (82.2%) | 9 / 12 of 30 | 54 | 106/120 |
| Haiku | mcp_crowd200 | 79/120 (65.8%) | 71/90 (78.9%) | 8 / 26 of 30 | 45 | 104/120 |
| Haiku | mcp_crowdall | 82/120 (68.3%) | 72/90 (80.0%) | 10 / 30 of 30 | 59 | 102/120 |
| Sonnet | mcp_alone | 94/120 (78.3%) | 79/90 (87.8%) | 15 / 15 of 30 | 0 | 110/120 |
| Sonnet | mcp_pack20 | 74/120 (61.7%) | 68/90 (75.6%) | 6 / 6 of 30 | 7 | 102/120 |
| Sonnet | mcp_crowd200 | 71/120 (59.2%) | 70/90 (77.8%) | 1 / 27 of 30 | 8 | 94/120 |
| Sonnet | mcp_crowdall | 70/120 (58.3%) | 69/90 (76.7%) | 1 / 30 of 30 | 2 | 75/120 |
| GPT | mcp_alone | 104/120 (86.7%) | 82/90 (91.1%) | 22 / 22 of 30 | – | – |
| GPT | mcp_pack20 (partial) | 33/54 (61.1%) | 22/24 (91.7%) | 11 / 18 of 30 | – | – |

- **Non-browser targets:** the paired change `mcp_alone→mcp_crowdall` was −4.4 pp for Haiku (request-cluster −10.0 to 0.0; two-stage −14.4 to +3.3) and −11.1 pp for Sonnet (request-cluster −17.8 to −4.4; two-stage −24.4 to −1.1). Between `crowd200` and `crowdall` it was +1.1 pp for Haiku (−2.2 to +5.6) and −1.1 pp for Sonnet (−6.7 to +4.4).
- **Claude Code** called `ToolSearch` in 62–92% of runs per setup.
- **Browser targets:** in the larger setups the first call is almost always a navigation tool, which the stub answers with “reply with one short sentence”, and the episode ends. The raw logs show that `ToolSearch` had already loaded the target tool's definition in 120 of 120 browser runs in the two `crowd` setups, while the target was called in 20. The strict browser rate in larger setups therefore mostly measures this stubbed environment, and the capable-server rate only the first routing step. **Neither measures completion.**

### 9.3 Experiment 3 (constructed scenarios) and 3b

| Model | Setup | Skill requests: target | Tool requests: strict | Tool requests: non-browser strict |
|---|---|---|---|---|
| Haiku | single-skill baseline* | 119/150 (79.3%) | 95/120 (79.2%) | 84.4% |
| Haiku | mixed_smaller | 50/150 (33.3%) | 82/120 (68.3%) | 78.9% |
| Haiku | mixed_larger | 32/150 (21.3%) | 81/120 (67.5%) | 75.6% |
| Sonnet | single-skill baseline* | 367/390 runs (94.1%) | 94/120 (78.3%) | 87.8% |
| Sonnet | mixed_smaller | 67/150 (44.7%) | 69/120 (57.5%) | 74.5% |
| Sonnet | mixed_larger | 51/150 (34.0%) | 67/120 (55.8%) | 70.0% |

\* The baseline for the 20 E1 skills is E1 `alone` with a 3-turn window. The baseline for the five trending skills is E3b with 4 turns (Haiku 25/30, Sonnet 28/30). The mixed scenarios had 4 turns, so the window difference favours the mixed scenarios. The tool baseline is the version 3 `mcp_alone`.

| Paired change | Haiku | Sonnet |
|---|---|---|
| Skill requests, baseline → `mixed_larger` | −58.0 pp (−66.0 to −50.0) | −60.0 pp (−68.0 to −52.2) |
| Non-browser tool requests, `mcp_alone` → `mixed_larger` | −8.9 pp (−15.6 to −2.2) | −17.8 pp (−26.7 to −10.0) |

**Skill-request misses** in the mixed scenarios were mostly built-in actions only: Haiku 83 and 93, Sonnet 59 and 82 (smaller, larger). The commonest were `Glob`, `Grep` and `Read`, consistent with searching the empty folder for files the requests mention. Of these built-in-only runs, Haiku 73, Sonnet 25 hit the turn limit.

**Overlapping tool families** were selected on 3–6 skill requests per setup.

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
| Claude Code, all experiments (runs in the results) | 4,020 | Claude Code's `total_cost_usd` estimate; Claude plan, not billed per token | $0 (list-price equivalent $198.02) |
| Claude Code, discarded runs (v2 E2/E3, superseded; the stopped shared-folder v3 pass; the 18 original Sonnet `caveman` `alone` E1 runs) | 3,233 | Same | $0 (list-price equivalent $149.64) |
| **Total billed** | | | **$171.73** |

Actual billing should be checked against the OpenAI usage dashboard. The figures above are list-price calculations from reported usage.

**Indirect evidence on catalogue size.** Codex's per-run cache writes grew from 13.2K (`alone`) to 20.3K tokens (`crowd1000`), while the installed listing grew by roughly 44K tokens (≈178K characters). This is consistent with a capped or shortened catalogue, but it does not show whether the target was visible.

Claude's summed input rose from 64.5K to 102.2K tokens per Sonnet run. That rise mixes catalogue size with extra turns. A single-turn Haiku pilot, whose records were not retained, measured about 33.4K against 43.3K input tokens.

---

## 11. Data, files, reproducing

| File | Content |
|---|---|
| `haiku.jsonl`, `sonnet.jsonl`, `gpt.jsonl` | E1 results (unchanged) |
| `sonnet_e1_caveman_v3.jsonl` | Version 3 rerun of Sonnet / `caveman` / `alone` (18 runs, one fresh folder per run); replaces those 18 records of `sonnet.jsonl` in version 3 |
| `gpt_subscription_failed.jsonl` | Excluded E1 batch (unchanged) |
| `mcp/haiku_v2.jsonl`, `mcp/sonnet_v2.jsonl`, `mcp/gpt_v2.jsonl` | E2/E3/E3b results of version 2 (unchanged). Version 3 uses their GPT and E3b records |
| `mcp/haiku_v3.jsonl`, `mcp/sonnet_v3.jsonl` | Version 3 Claude Code E2/E3 results: MCP allowed, one fresh folder per run |
| `mcp/haiku_v3_shared.jsonl`, `mcp/sonnet_v3_shared.jsonl` | First v3 pass, MCP allowed but shared folders (stopped after E2 and part of E3); comparison only |
| `mcp/raw/claude_haiku/`, `mcp/raw/claude_sonnet/` | Raw event logs of both v3 passes, local paths removed |
| `raw_e1/claude_sonnet/` | Raw event logs of the E1 rerun, local paths removed |
| `analysis/analyze.py` | The single analysis entry point (this document's numbers) |
| `analysis/budget.py` | Follow-up cost model |
| `analysis/REPORT.md`, `analysis/derived/v2/*.csv`, `manifest.json` | Derived tables; SHA-256 of every input |
| `analysis/derived/v2/paired_vs_alone.csv`, `e3_chart_rates.csv` | Tables behind the post's forest plot and mixed-scenario chart (paired change from alone; request-weighted rates with intervals) |
| `analysis/alt_judge_input.json`, `analysis/alt_judgments.json` | Blind alternative ratings |
| `analysis/CHANGELOG.md` | Claim-by-claim change log |
| `METHODOLOGY_v2.md`, `METHODOLOGY_v1.md` | Versions 2 and 1, unchanged |
| `FOLLOWUP_PROTOCOL.md` | Proposed follow-up (not results) |
| Experiment scripts | `prompts.json`, `build.py`, `run.py`, `run_codex.py`, `mcp/*` |
| Survey files | `scan*.py/json`, `weight*`, `report*`, `source_commits.tsv` |

**Raw logs.** `mcp/raw/` was added to the runner during the original experiment, too late for any retained v2 run (every Claude batch started under the earlier runner, and the GPT runs after the change ended in a rate limit). Every v3 run has one (3,215 logs: the 2,040 retained runs and the 1,175 of the stopped shared-folder pass; plus 18 for the E1 rerun in `raw_e1/`). Local paths, the user ID in temporary paths and the working folder's name (also where an agent mentioned it in its text) were replaced with placeholders, and the `init` event's machine-specific fields (memory and scratch paths, socket, timings) were dropped. `analysis/raw_checks.py` gives identical results on the scrubbed and the original logs.

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
| Default permission mode, nobody to approve | Stub MCP servers pre-approved in v3; other approval-gated calls refused | Web search and most web fetches were unavailable in every Claude Code run |
| Codex `approval_policy="never"`, stub servers not pre-approved | GPT E2 not repeated | GPT MCP results measure which tool was called; what followed was a reaction to an approval error, and a miss can also be a server that failed to start (§5.5) |
| Codex bundled skills left on | Not repeated | Codex “alone” is the target plus 5 bundled skills (§2, §4.4) |
| Auto-memory on (harness default) | One fresh folder per run in v3 | v2 E2/E3 and one E1 folder had notes carried over between runs (§0) |
| Empty folders, Codex read-only, Claude `Bash` disallowed | Minimal-context routing benchmark | No claims about ordinary task execution or the reasons for abstaining |
| One filler sample, LLM-written requests | Case study | Inference limited to this collection and these requests |
| Built-ins and native discovery (`ToolSearch`, Codex shell, Codex MCP discovery) | End-to-end configuration test | Differences are between configurations, not models |
| Mixed API and plan access for GPT E2 | Separately tagged batches | No equivalence assumed; the 5 plan runs are shown separately in the audit |
| Reconstructed MCP schemas | Fidelity-labelled | Structural defects listed; no claim that schemas cannot matter |
| Mixed scenarios | Two constructed scenarios | No interaction or “typical user” claims |
| Static survey | Selected corpus | Detected files only; no ecosystem prevalence claims |

**Mechanisms remain hypotheses.** Catalogue limits are one plausible explanation for the declines and for the Codex drop between 220 and 1,020 skills. Target visibility was not measured. The design does not isolate the effect of a skill's distinctiveness either: several distinctive targets kept higher rates in this sample.

**Mitigations are untested.** Mitigations discussed elsewhere (sharper descriptions, router skills, hooks, retrieval, larger budgets) are hypotheses for future evaluation. Installing fewer skills is the manipulation that was tested, but its effect on task quality was not measured.
