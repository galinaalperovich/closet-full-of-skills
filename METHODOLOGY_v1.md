# Skill and MCP tool selection under load: methodology

**Status:** working document for external review, 20 November 2026.
**Question:** when a coding agent has many Agent Skills and/or MCP tools installed, how often does it still use the right one for an ordinary request?
**Short answer so far (Experiment 1, skills only):** the rate falls steadily as skills are added, on every model tested. Experiments 2 and 3 (MCP tools, and skills plus tools together) are running; their results are not in this document yet.

All paths are relative to `skill-trigger-spike/` unless stated otherwise.

---

## 1. Overview

| # | Experiment | Status | Runs |
|---|---|---|---|
| 0 | Static survey of popular skill repositories | Done | n/a (no model calls) |
| 1 | Skills only: does the target skill fire as unrelated skills are added? | Done | 2,400 |
| 2 | MCP tools only: same design, with real MCP tool definitions | Claude done or nearly done; GPT partial | 1,440 planned |
| 3 | Realistic mix: skills and MCP servers installed together | Claude running; GPT not started | 1,620 planned |
| 3b | Five skills from repositories trending on GitHub this month, alone | Claude running; GPT not started | 90 planned |

The unit of measurement throughout is a **run**: one request sent once to one harness, model and setup, recorded as hit or miss.

---

## 2. Systems under test

| Harness | Version | Models | How skills are exposed | How a skill “fires” | How an MCP tool “fires” |
|---|---|---|---|---|---|
| Claude Code | 2.1.328 | Claude Haiku 5.5 (`--model haiku`), Claude Sonnet 5.5 (`--model sonnet`) | `.claude/skills/<name>/SKILL.md` in the working folder | The model calls the `Skill` tool with that skill’s name | The model calls `mcp__<server>__<tool>` |
| Codex CLI | 0.160.0 | `gpt-6-astra`, reasoning effort `medium` | `.agents/skills` (a symlink to the same `.claude/skills` folder) | The agent runs a shell command that reads `skills/<name>/SKILL.md` | The event stream contains an `mcp_tool_call` item for that server and tool |

Documented listing limits, which motivate the design (sources: [Claude Code skills docs](https://code.claude.com/docs/en/skills.md), [Codex skills docs](https://learn.chatgpt.com/docs/build-skills), [Agent Skills spec](https://agentskills.io/specification)):
- **Claude Code:** the skill listing (names and descriptions) gets 1% of the context window by default. Each entry’s description is cut at 1,536 characters. When the listing overflows, all names stay, and descriptions are dropped starting with the least-used skills. The warning goes only to the debug log.
- **Codex:** the initial skills list gets 2% of the context window, at most 10,000 tokens (8,000 characters if the window is unknown), and descriptions are shortened first.
- **Agent Skills spec:** `name` is at most 64 characters (lowercase letters, digits and hyphens) and must match the folder name; `description` is at most 1,024 characters.

---

## 3. Experiment 0: static survey

**Sample.** Repositories found with `gh search repos` across skill-related topics and keywords (`topic:claude-skills`, `topic:agent-skills`, `topic:claude-code-plugin`, `topic:claude-code-skills`, `topic:claude-code`, `topic:agents-md`, `topic:claude-code-subagents`, `skills in:name claude`, `topic:mcp-server`, `topic:ai-agents`), sorted by stars. From the top results, 36 repositories that ship `SKILL.md` files were selected by hand (`repos.txt`). On review feedback, 7 skill repositories from [GitHub trending (monthly)](https://github.com/trending?since=monthly) on 20 November 2026 were added: `Nutlope/hallmark`, `cloudflare/security-audit-skill`, `AgriciDaniel/claude-seo`, `elementalsouls/Claude-BugHunter`, `kajisho5/ffmpeg-skill`, `Jakeschincariol/instagram-agent-skill`, `google-labs-code/stitch-skills`. Total: 43 repositories cloned, 42 containing skills. Exact commits are in `source_commits.tsv`.

**Procedure.** Shallow clones (`git clone --depth 1`, git hooks disabled). No repository code was executed; all checks are static text parsing (`scan.py`, `weight.py`, `report.py`, Python standard library plus PyYAML).

**Units.** Every `SKILL.md` file is parsed. Identical files (same SHA-1) are counted once (“unique skills”). For size estimates, duplicate names within one repository are counted once.

**Checks** (`scan.py`):

| Check | Definition |
|---|---|
| Frontmatter | Present and valid YAML mapping |
| Name | Present, matches the spec pattern, ≤64 characters, equals folder name |
| Description | Present; flagged if >1,024 or <40 characters, or if it contains no trigger wording (“use when”, “trigger”, “whenever”…) |
| Body length | Flagged above 500 lines (spec recommendation) |
| Broken references | Markdown links and conventional paths (`scripts/…`, `references/…`) that do not exist |
| Orphan files | Bundled `.md/.py/.sh/.js/.ts` files never mentioned in the skill |
| Undeclared Python dependencies | Third-party imports (parsed with `ast`) with no requirements file, no PEP 723 header, and no mention in the skill text |
| Old model IDs, personal absolute paths | Regex matches |
| Tests | Any file or folder matching `evals?`, `tests?`, `evals.json`, `*_test.*`, `test_*` inside the skill folder |

**Listing size** (`weight.py`): for each repository, `Σ (len(name) + min(1536, len(description + when_to_use)))` characters; tokens estimated as characters ÷ 4. Compared against 8,000 characters (about 2,000 tokens, the Claude Code default for a 200K window).

**Headline numbers** (42 repositories, 6,908 distinct skills): structural defects affect 0–3% of skills each; about 2.6% of skills ship any test or eval file; 16 of 42 repositories exceed the 8,000-character budget if installed whole; 732 skill names appear in two or more repositories (first 35 repositories). Full tables: `report2.txt`, `weight2.txt`.

---

## 4. Experiment 1: skills only

### 4.1 Targets and requests
- **20 target skills** from widely installed repositories: `anthropics/skills` (`pdf`, `xlsx`, `pptx`, `docx`, `webapp-testing`, `mcp-builder`, `frontend-design`), `mattpocock/skills` (`tdd`, `grill-me`, `diagnosing-bugs`), `obsidianmd/obsidian-skills` (`obsidian-markdown`, `json-canvas`), `blader/humanizer`, `vercel-labs/agent-skills` (`vercel-react-best-practices`, `web-design-guidelines`), `addyosmani/agent-skills` (`security-and-hardening`), `emilkowalski/skills` (`animate`), `JuliusBrussee/caveman`, `coreyhaines31/marketingskills` (`seo-audit`, `copywriting`).
- **6 requests per skill, 120 in total** (`prompts.json`). Written by the experimenter as a user would ask, never naming the skill, before any model run. Requests cover the skill’s main use cases and vary in wording; some are deliberately indirect (for example “Be brief. Less words.” for `caveman`).

### 4.2 Setups
| Setup | Skills installed |
|---|---|
| `alone` | The target skill only (a separate folder per target) |
| `pack20` | All 20 target skills |
| `crowd200` | The 20 targets plus 200 filler skills |
| `crowd1000` | The 20 targets plus 1,000 filler skills |

**Fillers:** sampled uniformly at random (seed 7) from `sickn33/agentic-awesome-skills` (3,049 distinct skills), excluding target names and names of Claude Code’s built-in skills. `crowd200` is a subset of `crowd1000`. Built by `build.py`.

In addition, Claude Code always exposes its own 23 built-in skills (for example `dataviz`, `run`, `code-review`); these are present in every setup, including `alone`.

### 4.3 Skill stubs
Each installed skill keeps its **original `name`, `description` and `when_to_use`**, re-serialised as YAML. The body is replaced with one line: “The instructions for this skill are omitted in this test. Reply with one short sentence.” Rationale: the decision to load a skill is made from the listing (name and description) only; the body is read after that decision. Stubbing also guarantees that no downloaded code or instructions can run. Consequence: only the first selection decision is meaningful; behaviour after loading is not representative.

### 4.4 Isolation and invocation
Each run starts a fresh process in the setup’s folder, which contains nothing but the skills.

Claude Code (`run.py`):
```
claude -p "<request>" --model <haiku|sonnet> --output-format stream-json --verbose \
  --setting-sources project --strict-mcp-config --no-session-persistence \
  --max-turns 3 --disallowedTools Bash
```
- `--setting-sources project`: user-level settings, skills and plugins of the experimenter are not loaded.
- `--strict-mcp-config` with no config: no MCP servers.
- The `init` event was checked to list only the expected skills (24 in `alone`, 43 in `pack20`, 243 in `crowd200`, 1,043 in `crowd1000`, each including the 23 built-ins).

Codex (`run_codex.py`):
```
codex exec --json --ephemeral --skip-git-repo-check -s read-only \
  -c model_reasoning_effort="medium" "<request>"
```
run with `CODEX_HOME` set to a scratch folder containing only an API-key login and `model = "gpt-6-astra"`, so no user configuration, skills or MCP servers were loaded.

### 4.5 Scoring
- **Hit:** the target skill was loaded at any point in the run (Claude: a `Skill` tool call whose `skill` argument, after any `plugin:` prefix, equals the target name; Codex: any executed command matching `skills/<target>/SKILL.md`).
- **Miss, other skill:** a different skill was loaded and the target was not.
- **Miss, no skill:** no skill was loaded.
- Runs that ended in a harness or API error are excluded from rates and re-run (none remained in the final data).

### 4.6 Repetitions and volume
| Model | Repetitions per request | Runs |
|---|---|---|
| Haiku | 1 | 480 |
| Sonnet | 3 | 1,440 |
| GPT | 1 | 480 |

Parallelism 6–8 processes. Runs were executed on 20 November 2026.

### 4.7 Results with uncertainty
Wilson 95% intervals treat runs as independent. Because the same 120 requests are reused, a cluster bootstrap that resamples requests (2,000 resamples, seed 1) is also reported; it is the more honest interval.

| Model | Setup | Hits | Rate | Wilson 95% | Request-cluster bootstrap 95% |
|---|---|---|---|---|---|
| Haiku | alone | 94/120 | 78.3% | 70.1–84.8 | 70.8–85.8 |
| Haiku | pack20 | 57/120 | 47.5% | 38.8–56.4 | 38.3–56.7 |
| Haiku | crowd200 | 30/120 | 25.0% | 18.1–33.4 | 17.5–32.5 |
| Haiku | crowd1000 | 19/120 | 15.8% | 10.4–23.4 | 10.0–22.5 |
| Sonnet | alone | 334/360 | 92.8% | 89.6–95.0 | 88.1–96.9 |
| Sonnet | pack20 | 272/360 | 75.6% | 70.9–79.7 | 67.5–82.5 |
| Sonnet | crowd200 | 202/360 | 56.1% | 50.9–61.1 | 48.1–65.0 |
| Sonnet | crowd1000 | 121/360 | 33.6% | 28.9–38.6 | 26.1–41.4 |
| GPT | alone | 120/120 | 100.0% | 96.9–100.0 | 100.0–100.0 |
| GPT | pack20 | 119/120 | 99.2% | 95.4–99.9 | 97.5–100.0 |
| GPT | crowd200 | 100/120 | 83.3% | 75.7–88.9 | 76.7–90.0 |
| GPT | crowd1000 | 12/120 | 10.0% | 5.8–16.7 | 5.0–15.8 |

Miss types at `crowd1000`: Haiku 3% other skill / 81% no skill; Sonnet 2.5% / 64%; GPT 24% / 66%.

Observed context cost (pilot, Haiku, single turn): about 33.4K input tokens per request with one skill installed versus 43.3K with 1,000 extra skills.

---

## 5. Experiment 2: MCP tools only

### 5.1 Tool definitions
791 real tool definitions from 73 servers (`mcp/tools_inventory.json`), taken from published data, never by running the servers:

| Source | Tools | How obtained | Fidelity |
|---|---|---|---|
| [`github/github-mcp-server`](https://github.com/github/github-mcp-server) | 149 | `pkg/github/__toolsnaps__/*.snap` (the project’s own JSON snapshots) | Exact name, description, input schema |
| [`ChromeDevTools/chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 63 | Parsed from `docs/tool-reference.md` | Exact name and description; schema reconstructed from the parameter list |
| [`microsoft/playwright-mcp`](https://github.com/microsoft/playwright-mcp) | 72 | Parsed from the README tool list | Exact name and description; schema reconstructed |
| [LiveMCPBench](https://github.com/icip-cas/LiveMCPBench) | 507 | `baseline/mcp_copilot/config/mcp_arg_*.json` (70 servers) | Name and description as published by the benchmark; schema reconstructed from its parameter strings |

Duplicates were removed (by name within a server, keeping the entry with a description); tools without any description were dropped. The community Playwright server in LiveMCPBench is renamed `playwright-ea` to keep it distinct from Microsoft’s.

### 5.2 Stub MCP server
`mcp/stub_server.py` (Python standard library only) implements MCP over stdio: `initialize`, `tools/list` (returns the server’s real definitions), `tools/call` (returns the text “Stub result: this tool is disabled in a test. Reply with one short sentence.”), `ping`. One process per server, launched by the harness from a generated config, so tool names appear exactly as in real use (for example `mcp__github__create_issue`).

### 5.3 Targets and requests
20 target tools, 6 requests each (`mcp/mcp_targets.json`): GitHub (`create_issue`, `create_pull_request`, `search_code`, `list_notifications`), Playwright MCP (`browser_take_screenshot`, `browser_fill_form`), Chrome DevTools (`performance_start_trace`, `list_console_messages`, `lighthouse_audit`), `context7.get-library-docs`, `fetch.fetch`, `git.git_log`, `filesystem.directory_tree`, `memory.create_entities`, `time.convert_time`, `yahoo-finance.get_current_stock_price`, `wikipedia.get_summary`, `arxiv-mcp-server.search_papers`, `youtube-transcript.get_transcript`, `mcp-server-chart.generate_bar_chart`.

**Accepted tools.** Real users do not care which of two equivalent tools is used, so each target has an accepted set that includes equivalent tools on other servers (for example, any server’s screenshot tool). The full sets are in `mcp_targets.json`. Two examples:
- `github.create_issue` accepts `github.create_issue` and `github.issue_write` (GitHub’s server exposes both; in the pilot Claude chose one and GPT the other).
- `yahoo-finance.get_current_stock_price` accepts stock-price tools from `yahoo-finance`, `yfmcp`, `investor` and both `asset-price-mcp` servers.

### 5.4 Setups
| Setup | Tools installed |
|---|---|
| `mcp_alone` | Only the target tool, on its real server name |
| `mcp_pack20` | The 20 target tools |
| `mcp_crowd200` | The 20 targets plus 200 random other tools (seed 11) |
| `mcp_crowdall` | The 20 targets plus all 771 other tools |

No skills are installed (Claude Code’s built-in skills and tools remain). Built by `mcp/build_v2.py`.

### 5.5 Invocation
Claude Code: as in §4.4, plus `--mcp-config <setup>/_mcp.json`, and `--max-turns 4` (one extra turn because Claude Code may first call `ToolSearch` to load deferred MCP tools; observed in the pilot).

Codex:
```
codex exec --json --ephemeral --skip-git-repo-check [--ignore-user-config] -s read-only \
  -c model="gpt-6-astra" -c model_reasoning_effort="medium" -c approval_policy="never" \
  -c mcp_servers.<name>.command="python3" -c mcp_servers.<name>.args=[...] ... "<request>"
```
With `approval_policy="never"`, Codex attempts the MCP call but does not execute it; the attempt is detected from the `item.started` event. The first 170 GPT runs used an API key in a scratch `CODEX_HOME` (no user config); later runs use the experimenter’s ChatGPT login with `--ignore-user-config`, which excludes the experimenter’s own MCP servers. Model and effort are identical.

### 5.6 Scoring
Each run records the ordered list of distinct skills and tools used, then one outcome:

| Outcome | Rule |
|---|---|
| `hit` | Any accepted tool (or, for browser targets, the right tool family; see below) was called |
| `other_skill` | No hit; a skill was loaded |
| `other_mcp` | No hit; some other MCP tool was called |
| `builtin` | No hit; only the harness’s own tools were used (Claude: `WebSearch`, `WebFetch`, `Read`, `Glob`…; Codex: shell, web search) |
| `none` | Nothing was called |

**Browser family rule.** Browser tasks need several steps: open the page, then screenshot or trace. Within the turn limit the final call is often not reached. For the five browser targets, `hit` also counts calling any tool on a server that can do the job (screenshot and form filling: `playwright-mcp`, `chrome-devtools`, `puppeteer`, `playwright-ea`; trace: `chrome-devtools`, `playwright-mcp`; console: `chrome-devtools`, `playwright-mcp`, `playwright-ea`; Lighthouse: `chrome-devtools` only). A strict score (`hit_strict`, exact accepted tool only) is recorded alongside and will be reported.

Claude Code’s use of `ToolSearch` is recorded per run (`toolsearch`).

---

## 6. Experiment 3: realistic mix of skills and MCP tools

### 6.1 Setups
| Setup | Skills | MCP tools |
|---|---|---|
| `mixed_typical` | 25 targets + 75 fillers = 100 | 437 tools: the full real servers of all 20 tool targets, plus document servers that overlap with document skills (`pdf-reader-mcp`, `excel`, `ppt`, `word-document-server`) |
| `mixed_heavy` | 25 targets + 375 fillers = 400 | All 791 tools |

**Skill targets:** the 20 from Experiment 1 plus 5 from trending repositories: `hallmark`, `security-audit` (Cloudflare), `seo` (claude-seo), `ffmpeg-skill`, `ig-carousel` (`mcp/trending_skill_prompts.json`, 6 requests each).

**Skill fillers:** 40% from a pool of 342 skills from trending and popular repositories (claude-seo, Claude-BugHunter, stitch-skills, ffmpeg-skill, instagram-agent-skill, impeccable, claude-mem, mattpocock, addyosmani, emilkowalski, anthropics, marketingskills, vercel-labs, obsidian), 60% from `sickn33/agentic-awesome-skills`; seed 11.

**Deliberate overlaps,** as they exist in real installations: `pdf`/`xlsx`/`pptx`/`docx` skills next to PDF, Excel, PowerPoint and Word MCP servers; `webapp-testing` next to Playwright and Chrome DevTools; `security-audit` next to `security-and-hardening`; `seo` next to `seo-audit`; `hallmark` next to `frontend-design`.

### 6.2 Requests and scoring
Both request sets run in both setups: 150 skill requests and 120 tool requests. Scoring as in §5.6; for skill requests the accepted set is the target skill. An additional flag `overlap_tool` records when a skill request was served by an overlapping MCP tool instead (for example `excel_write_to_sheet` for an `xlsx` request), so a lenient “task routed to a capable component” rate can be reported next to the strict skill rate.

### 6.3 Experiment 3b
The five trending skills are also run `alone` (one skill installed) to give a baseline for the mix.

---

## 7. Data and files

| File | Content |
|---|---|
| `prompts.json` | Experiment 1 requests |
| `build.py`, `run.py`, `run_codex.py` | Experiment 1 environment builder and runners |
| `haiku.jsonl`, `sonnet.jsonl`, `gpt.jsonl` | Experiment 1 results, one record per run |
| `gpt_subscription_failed.jsonl` | Excluded: first GPT attempt, 476 of 480 runs failed with HTTP 429 |
| `mcp/tools_inventory.json` | 791 tool definitions |
| `mcp/mcp_targets.json`, `mcp/trending_skill_prompts.json` | Experiment 2 and 3 targets, accepted sets and requests |
| `mcp/stub_server.py`, `mcp/build_v2.py`, `mcp/run2.py` | Stub MCP server, environment builder, runner |
| `mcp/haiku_v2.jsonl`, `mcp/sonnet_v2.jsonl`, `mcp/gpt_v2.jsonl` | Experiment 2, 3 and 3b results |
| `mcp/raw/<harness>_<model>/<setup>/*.json.gz` | Full raw event stream and exact command per run. Added to the runner during the experiment; at the time of writing, no completed run has a raw log (all Claude batches had already started with the earlier runner). Only GPT runs started from now on will have one |
| `scan.py`, `weight.py`, `report.py`, `scan2.json`, `weight2.json`, `report2.txt`, `weight2.txt` | Experiment 0 |
| `source_commits.tsv` | Commit of every cloned source repository |

**Record fields.** Experiment 1: `cond`, `target`, `i` (request index), `rep`, `model`, `hit`, `fired` (skills loaded), `first_tool`, `n_skills`, `in_tok`, `cost` or `usage`. Experiments 2–3: `env`, `kind` (`skill`/`tool`), `target`, `accept`, `i`, `prompt`, `harness`, `model`, `used` (ordered distinct `skill:`/`mcp:`/`builtin:` items), `outcome`, `hit`, `hit_strict`, `overlap_tool`, `toolsearch`, `n_tools`, `n_skills`, `mcp_failed` (servers that did not connect), `in_tok`, `cost` or `usage`, `ts`, `raw`.

**Not captured.** The exact prompt sent to the model (neither CLI exposes it). For runs without raw logs: the agent’s text, tool arguments and tool results.

---

## 8. Reproducing

1. Clone the repositories in `source_commits.tsv` at the listed commits.
2. Experiment 1: `python3 build.py`, then `python3 run.py alone,pack20,crowd200,crowd1000 <reps> <haiku|sonnet> out.jsonl` and `python3 run_codex.py alone,pack20,crowd200,crowd1000 1 medium out.jsonl`.
3. Experiments 2–3: `python3 mcp/build_v2.py`, then `python3 mcp/run2.py <claude|codex> <model> <mcp|trend|mixed> out.jsonl` (`PAR` sets parallelism; `STOP_ON_429=1` stops at the first rate-limit error). Runners skip runs already present without error, so they can be resumed.

Paths to the scratch folders holding cloned repositories and built environments are hard-coded at the top of the scripts and must be adjusted.

---

## 9. Threats to validity and known limitations

**Construct**
- **Selection, not quality.** We measure whether the right component is chosen, not whether the final answer is good. A miss is not necessarily a bad answer; the model may solve the task without the skill.
- **Some “misses” are defensible.** For example Sonnet chose `seo-technical` over `seo-audit` for “Do a technical SEO check”. Experiment 1 scores these as misses; Experiments 2–3 use accepted sets to reduce this for tools, but not for skills.
- **Stub bodies.** Only the first selection decision is valid. Multi-step behaviour after loading a stub, or after a stub tool result, is not representative.

**Internal**
- **Request authorship.** All requests were written by the experimenter, who also chose the targets. They were written before any run and not tuned afterwards, but they are not blind or independently sourced.
- **Turn limits.** Claude Code was capped at 3 turns (Experiment 1) and 4 turns (Experiments 2–3); a skill or tool chosen later would be missed. Codex has no turn limit in `exec`. This favours Codex slightly and makes Experiment 1 and Experiments 2–3 not strictly comparable for Claude.
- **Empty working folder.** Requests mention files (`invoice-jan.pdf`) that do not exist. Some agents first look for them with built-in tools and may then answer without loading anything.
- **Sandbox and approvals.** Codex ran read-only with approvals disabled, so MCP calls were attempted but rejected; Claude Code had `Bash` disallowed. Both differ from a normal interactive setup.
- **Built-in skills and tools.** Claude Code’s 23 built-in skills and its built-in tools (`WebSearch`, `WebFetch`, `Glob`…) compete in every setup. This is realistic, but it means `alone` is never literally one option.
- **Codex budget explanation.** That GPT’s cliff between 220 and 1,020 skills is caused by Codex’s 2% / 10,000-token listing cap is an interpretation; we did not inspect what Codex sent to the model.

**External**
- **Fillers.** In Experiment 1, fillers come from one large community collection; real installations have fewer but more overlapping skills. Experiment 3 addresses this partly.
- **Schemas.** For 642 of 791 tools, input schemas were reconstructed from documentation or benchmark parameter strings; names and descriptions are original. Selection depends mostly on names and descriptions.
- **Harnesses, versions, models.** Two harnesses, one version each, three models, one day. Other harnesses (Cursor, Gemini CLI) and later versions may behave differently; Claude Code’s and Codex’s budgets are configurable and may change.

**Statistical**
- **Repetitions.** One repetition per request for Haiku and GPT, three for Sonnet. Per-skill numbers (6 or 18 runs) are noisy; the setup-level trends have non-overlapping intervals (§4.7).
- **Independence.** Runs reuse the same requests; request-clustered intervals are reported for that reason.
- **Mixed access paths for GPT.** Experiment 2 GPT runs were made partly through an API key and partly through a ChatGPT plan (same model and settings). Rate-limited runs (HTTP 429) are excluded and retried, never counted as misses.

**Process notes**
- Pilot runs (Experiment 1: `--max-turns 1`; Experiment 2: a scoring bug that compared `mcp:`-prefixed names against unprefixed accepted names) were discarded and are not part of the results.
- One example in the blog draft (`interview-me`) was checked against the data and corrected before publication.

---

## 10. Cost

| Item | Basis | Amount |
|---|---|---|
| Experiment 1, Claude | Claude Code’s reported list-price equivalent on a subscription (not billed separately) | Haiku $1.89, Sonnet $85.87 |
| Experiment 1, GPT | 19.1M input tokens (11.0M cached reads, 8.1M cache writes), 133K output, priced at OpenAI’s list price for GPT-6 Astra ($10 / $1 / $12.50 / $50 per million input / cached / cache write / output) | about $119 |
| Experiment 2, GPT (first 170 runs, API key) | 12.3M input, 61K output, same prices | about $53 |

Each Codex run starts a fresh session, so the full listing is written to the cache every run; cache writes are the dominant GPT cost.
