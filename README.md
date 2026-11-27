# A Closet Full of Skills and Nothing to Wear

**The more skills you install, the less often your coding agent picks the right one. MCP tools hold up better.** Measured with up to 1,000 skills and 791 MCP tools in Claude Code and Codex.

This repository has everything behind the blog post: the requests, the experiment scripts, every result record, the analysis that turns those records into the published numbers, the captured skill listings, the methodology, and the post itself. You can reproduce every number without spending anything, and re-run the experiments if you want to pay for it.

**Read the post: https://galinaalperovich.github.io/closet-full-of-skills/**

The page is `docs/index.html`, built from the sources in [`post/`](post/). The figures are also exported as PNGs in [`post/images/`](post/images/). A readable Markdown copy of the post is in [`post/post.md`](post/post.md): to suggest a change to the text, edit that file in a pull request. Accepted changes are carried over into `post/build_post.py`, which builds the page.

## What was measured

I asked Claude Code and Codex natural requests that were written for one particular skill or MCP tool, such as “Audit the SEO of my site” for `seo-audit`, with no explicit invocation (no `/seo-audit`, no “use the seo-audit skill”). Then I counted how often the agent selected that component as more skills or tools were installed next to it.

| | Skills (E1): target alone → 20 → 220 → 1,020 skills | MCP tools (E2), 15 single-step targets: alone → 20 → ~220 → 791 tools |
|---|---|---|
| Claude Code + Haiku | 78% → 48% → 25% → 16% | 83% → 78% → 77% → 78% |
| Claude Code + Sonnet | 94% → 76% → 56% → 34% | 87% → 81% → 76% → 79% |
| Claude Code + Fable 5.2 | 99% → 99% → 98% → 72% | 90% → 87% → 81% → 84% |
| Codex + GPT-6 Astra | 100% → 99% → 83% → 10% | not in these results (a partial run with the first setup is kept in `mcp/gpt.jsonl`) |
| Codex + GPT-6 Sol | 100% → 100% → 82% → 12% | 96% → 78% → 86% → 81% |

**Skills + tools together** (E3, Haiku and Sonnet only), from the single component to the smaller and the larger mix: skill requests 79% → 33% → 21% (Haiku) and 94% → 45% → 34% (Sonnet); single-step tool requests 83% → 79% → 78% and 87% → 80% → 79%.

- 6,594 retained runs: 4,980 Claude Code runs and 1,614 Codex runs. On top of those there is one excluded, rate-limited GPT batch (`skills/gpt_subscription_failed.jsonl`).
- **Two rounds of data collection.** Round 1 (20 November 2026): E1 for all three configurations, E3b, every Codex run, and a first pass of the Claude Code E2/E3 runs. Round 2 (22 November 2026): all 2,040 Claude Code E2/E3 runs again, because headless Claude Code had refused every MCP call and its per-folder auto-memory had carried notes from one run to the next. The 18 E1 runs of the one skill folder with a carried-over memory note (Sonnet, `caveman`, alone) were rerun the same way. Details are in `METHODOLOGY.md` §1.1.
- **Two more configurations** were added on 25 November 2026, with the same harness versions, requests and setups: Claude Fable 5.2 in Claude Code and GPT-6 Sol in Codex, each with E1 (one run per request) and E2. They were not run in E3. See `METHODOLOGY.md` §14.
- **Round 3 of the tool runs** (25–27 November 2026): every E2 run, and the tool requests of E3, were repeated for Haiku, Sonnet, Fable 5.2 and GPT-6 Sol. The stub server's reply had told the agent to "reply with one short sentence", which ended a run after its first call, and the first GPT-6 Sol run also had its MCP calls blocked, built-in web search on, and test folders inside a git repository. Round 3 uses a plain "Done." reply, an 8-turn limit in Claude Code, pre-approved stub servers in both harnesses, no web search in Codex, and folders outside a repository. **The tool numbers above are from round 3.** See `METHODOLOGY.md` §15.
- **Listing budget raised** (27 November 2026). Both harnesses have a setting for the skill listing budget (Claude Code: `skillListingBudgetFraction` or `SLASH_COMMAND_TOOL_CHAR_BUDGET`; Codex: `skills.max_context_tokens`, at most 10,000). With it at its limit, the 1,020-skill setup was run again, 120 requests per model: Haiku 16% → 8%, Sonnet 34% → 44%, Fable 72% → 82%, GPT-6 Sol 12% → 41%. Claude Code then lists all 1,037 descriptions (about 184,000 characters per request); Codex lists 618 names, 9 of the 20 targets. See `METHODOLOGY.md` §16.
- **What the model saw.** After the runs, the skill listing each harness sends to the model was captured with a local stand-in server, without calling any model ([`listing/`](listing/)). At 20 skills both harnesses listed every description. At 1,020 skills, Claude Code kept descriptions for only 19 of 1,037 entries, and Codex listed only 321 entries, alphabetically, with no descriptions: 3 of the 20 targets. See `METHODOLOGY.md` §10.
- What is measured is **selection of the designated component within the observation window**, not the quality of the answer.
- Every rate and paired change has a 95% confidence interval (request-cluster bootstrap, 2,000 resamples, fixed seed; Wilson score interval where all runs succeeded) in `analysis/derived/`. See `METHODOLOGY.md` §8.
- The full design, statistics, limitations and every number are in [`METHODOLOGY.md`](METHODOLOGY.md). Read it before you reuse a number.

## Reproduce the published numbers (free, about a minute)

```bash
pip install pyyaml                   # the only dependency (Python 3.9+)
python3 analysis/analyze.py          # the published numbers: analysis/REPORT.md and analysis/derived/
python3 analysis/raw_checks.py       # checks that need the raw logs (round 2 and Fable Claude Code runs): derived/raw_checks.csv, raw_browser.csv
python3 analysis/budget.py           # the cost model behind the follow-up plan: derived/followup_budget.csv
git status --short analysis/         # expect no changes: you get the same tables
```

`analysis/derived/manifest.json` records the SHA-256 of every input. The result files (`*.jsonl`) are byte-identical to the ones the analysis was first run on. Only two kinds of file differ from my working copy: scripts whose machine-specific paths became environment variables, and `survey/scan.json`, where other people's home-folder names found by the survey scanner were replaced with `<user>`.

To rebuild the post and its figures:

```bash
cd post
python3 figs.py         # -> figs.json: the charts, computed from analysis/derived (the survey chart comes from fig_weight.svg)
python3 build_post.py   # -> skills-mcp-post.html (identical to the shipped one)
python3 export_png.py   # -> images/*.png, plus images/card.png (1200x630 at 2x, for link previews) and images/thumb_3x2.png
                        #    (needs Google Chrome; set CHROME_BIN if it is elsewhere)
python3 build_page.py   # -> ../docs/index.html, the standalone page served by GitHub Pages; it also runs build_md.py,
                        #    which writes post.md, the Markdown copy (needs beautifulsoup4)
```

## Re-run the experiments (costs money)

**Prerequisites**
- Claude Code (the study used 2.1.328) and/or Codex CLI (0.160.0), Python 3.9+ with PyYAML, and git.
- Versions matter. Both harnesses change how they list skills and tools between releases, so expect your numbers to differ from mine on newer versions. That difference is a finding in itself.

**1. Fetch the sources at the exact commits used.** Third-party repositories are not redistributed here.
```bash
sources/fetch_sources.sh          # 43 skill repositories -> third_party/repos/
sources/fetch_sources.sh --mcp    # optional: MCP tool sources -> third_party/mcp/ (not needed to run; the inventory is frozen)
```

**2. Build the test folders.** I checked that both builds reproduce the original folders byte for byte from the pinned commits.
```bash
python3 skills/build.py          # E1 -> envs/  (alone, pack20, crowd200, crowd1000)
python3 mcp/build.py      # E2/E3 -> envs2/  (MCP-only setups, trending skills alone, two mixed setups)
```

**3. Run.** Always write to a **new** output file. The runners resume from the file you name, so never point them at the shipped results.
```bash
# E1, skills only. Arguments: setups, repeats per request, model, output file
ISOLATE=1 python3 skills/run.py alone,pack20,crowd200,crowd1000 1 haiku  results/haiku_rerun.jsonl
ISOLATE=1 python3 skills/run.py alone,pack20,crowd200,crowd1000 3 sonnet results/sonnet_rerun.jsonl
python3 skills/run_codex.py alone,pack20,crowd200,crowd1000 1 medium results/gpt_rerun.jsonl
CODEX_MODEL=gpt-6-sol python3 skills/run_codex.py alone,pack20,crowd200,crowd1000 1 medium results/gpt_sol_rerun.jsonl

# E2 (MCP only), E3b (trending skills alone), E3 (mixed). Arguments: harness, model, job set, output file
STOP_ON_HIT=1 MAX_TURNS=8 ALLOW_MCP=1 ISOLATE=1 PAR=2 python3 mcp/run.py claude haiku mcp   results/haiku_mcp.jsonl
STOP_ON_HIT=1 MAX_TURNS=8 ALLOW_MCP=1 ISOLATE=1 PAR=2 ONLY_KIND=tool python3 mcp/run.py claude sonnet mixed results/sonnet_mixed.jsonl
CODEX_MODEL=gpt-6-sol CODEX_APPROVE_MCP=1 CODEX_WEB_SEARCH=disabled python3 mcp/run.py codex gpt-6-sol mcp results/gpt_sol_mcp.jsonl
```
- Run `mkdir results` first.
- Useful environment variables:
  - `PAR`: parallel runs (default 6 for E1, 4 for E2/E3).
  - `ONLY_ENV`, `ONLY_I` and `ONLY_TARGET`: run a subset (`skills/run.py` takes `ONLY_TARGET`).
  - `STOP_ON_429=1`: stop at the first rate limit.
  - `STOP_ON_HIT=1` (Claude Code, `mcp/run.py`): end a run as soon as it calls an accepted tool. Such a run has no cost or token totals.
  - `MAX_TURNS` (Claude Code, `mcp/run.py`): the turn limit, 4 when unset; round 3 used 8.
  - `ONLY_KIND=tool` or `skill`: run only those requests of a job set.
  - `CODEX_APPROVE_MCP=1`: pre-approve the stub servers in Codex. Without it, `approval_policy="never"` makes Codex refuse every MCP call.
  - `CODEX_WEB_SEARCH=disabled`: turn off Codex's built-in web search.
  - `RAW_DIR`: where raw event logs go (`mcp/raw` when unset).
  - `ALLOW_MCP=1` (Claude Code): pre-approve the stub MCP servers. Without it, headless Claude Code refuses every MCP call, which is what happened in round 1.
  - `ISOLATE=1` (Claude Code, `skills/run.py` and `mcp/run.py`): run each job in a fresh copy of its test folder, so Claude Code's per-folder auto-memory starts empty every time, and keep the raw output. It does not reset Claude Code's global skill-usage record (`skillUsage` in `~/.claude.json`), which decides which descriptions survive in large listings (`METHODOLOGY.md` §10).
  - `LOAD_MAX=<n>`: wait before starting a job while the 1-minute load average is above n. The mixed setups start up to 73 stub servers per run; 8 parallel runs once made a 10-core laptop unresponsive.
  - `SKILL_REPOS`, `ENVS_DIR` and `ENVS2_DIR`: move the inputs and test folders.
  - `CODEX_MODEL`: the Codex model (`skills/run_codex.py`: the Codex default when unset; `mcp/run.py`: `gpt-6-astra` when unset).
  - `CODEX_EXTRA`: extra Codex config for `skills/run_codex.py` and `listing/capture.py`, separated by `;`, for example `skills.max_context_tokens=10000`.
  - `SLASH_COMMAND_TOOL_CHAR_BUDGET` (read by Claude Code itself): the skill listing budget in characters.
  - `CODEX_BIN`: the path to Codex.
- For Codex, build the test folders outside any git repository (`ENVS2_DIR`), or the model can answer git requests from the shell.
- For Codex, use a separate `CODEX_HOME` that is logged in with an API key, so your personal Codex settings and skills don't leak into the runs.
- `analysis/analyze.py` reads the shipped file names (the `INPUTS` list at its top). To analyse a rerun, point that list at your files.

**Captured listings (free, no model calls).** `listing/capture.py` records what each harness sends to the model in each skills setup, using a local stand-in server. See [`listing/README.md`](listing/README.md).

**What it costs** (list prices; details in `analysis/derived/cost_by_batch.csv`)

| Configuration | Per run | This study |
|---|---|---|
| Claude Code, Haiku | about $0.002–0.009 | covered by a Claude subscription ($144.56 list price recorded for the 4,020 Haiku and Sonnet runs in the results; tool runs stopped at the designated call report no cost) |
| Claude Code, Sonnet | about $0.03–0.14 | (included above) |
| Claude Code, Fable 5.2 | about $0.12–0.38 | covered by the same subscription ($113.95 list price recorded for 960 runs) |
| Claude Code, runs not used in the results | | $327.54 list price for 5,153 runs: rounds 1 and 2 of the tool runs and smaller reruns |
| Codex + GPT-6 Astra, skills (E1) | $0.19–0.31 measured | $119.13 for 480 runs |
| Codex + GPT-6 Astra, MCP alone / 20 tools, first setup | $0.29 / $0.35 measured | $52.60 for 170 API runs, not used in the results |
| Codex + GPT-6 Sol, skills (E1) | $0.05–0.08 measured | $30.81 for 480 runs |
| Codex + GPT-6 Sol, MCP (E2), round 3 | $0.06–0.09 measured | $35.79 for 480 runs |
| Codex + GPT-6 Sol, MCP (E2), first run | $0.07–0.09 measured | $39.00 for 480 runs, not used in the results |
| Codex + GPT, mixed setups | about $1.5–2.2 **estimated** | not run |

Most of a GPT run's cost is writing the prompt prefix (system prompt, skill listing, tool definitions) to the cache, because every run is a new session. Use `STOP_ON_429` and a spending limit on your API key.

**Safety.**
- Every skill keeps its real name and description, but its instructions are replaced with a one-line stub. Every MCP tool is served by `mcp/stub_server.py`, which returns its definition and a stub result. No code from the fetched repositories is ever run.
- Claude Code runs use `--disallowedTools Bash --strict-mcp-config --setting-sources project`, and Codex runs use `-s read-only`.
- Built-in web tools were not disabled. In headless mode, with nobody to approve, Claude Code refused web searches and most page fetches (it allows a few documentation sites). Codex's own web search worked.

## Repository layout

```
├── METHODOLOGY.md          design, measurement, statistics, all results, limitations
├── FOLLOWUP_PROTOCOL.md    a costed plan to finish the study (a proposal, not results)
├── THIRD_PARTY.md          licenses of the third-party material
├── skills/                 Experiment 1: skills only
├── mcp/                    Experiments 2, 3 and 3b: MCP tools only, trending skills, skills and tools mixed
├── listing/                the skill listings each harness actually sent to the model
├── survey/                 Experiment 0: static survey of 42 skill repositories
├── sources/                the source repositories, their pinned commits, and the script that fetches them
├── analysis/               turns the result records into every published number
├── post/                   the blog post: builder, figures, PNG exports, Markdown copy
└── docs/                   the published page (GitHub Pages)
```

**`skills/`** (E1)

| File | What it is |
|---|---|
| `prompts.json` | The 20 target skills, 6 requests each |
| `build.py`, `run.py`, `run_codex.py` | Build the four skill setups; run them in Claude Code; run them in Codex |
| `haiku.jsonl`, `sonnet.jsonl`, `fable.jsonl`, `gpt.jsonl`, `gpt_sol.jsonl` | Results, one record per run (`gpt.jsonl` is GPT-6 Astra) |
| `sonnet_e1_caveman_rerun.jsonl` | The 18-run rerun of Sonnet / `caveman` / alone, used in place of those records of `sonnet.jsonl` |
| `e1_fullbudget_*.jsonl` | 1,020 skills with the listing budget raised to its limit, 120 runs per model (read by `post/build_post.py`) |
| `gpt_subscription_failed.jsonl` | The excluded, rate-limited GPT batch, kept for transparency |
| `raw_e1/` | Raw event logs of the rerun and of the Fable runs, local paths removed |

**`mcp/`** (E2, E3, E3b)

| File | What it is |
|---|---|
| `mcp_targets.json`, `trending_skill_prompts.json` | The 20 MCP tool targets and the 5 trending skills, 6 requests each |
| `tools_inventory.json` | The frozen inventory of 791 tool definitions from 73 servers (see `THIRD_PARTY.md`) |
| `build.py`, `run.py`, `stub_server.py` | Build the MCP and mixed setups; run both harnesses; the stub MCP server |
| `*_round3.jsonl` | Round 3: every E2 run, and the tool requests of E3. **The tool results come from these** |
| `haiku_round2.jsonl`, `sonnet_round2.jsonl`, `fable.jsonl`, `gpt_sol.jsonl` | Round 2 (Claude Code, MCP allowed, fresh folder per run) and the first Fable and GPT-6 Sol runs |
| `haiku_round1.jsonl`, `sonnet_round1.jsonl`, `gpt.jsonl` | Round 1 (the analysis uses the GPT and E3b records) |
| `raw/`, `raw_r3/` | Raw event logs of round 2 and of the Claude Code round 3 runs, local paths removed |

**`analysis/`**

| File | What it is |
|---|---|
| `analyze.py` | The single entry point that produces every published number |
| `REPORT.md`, `derived/` | Its outputs: rates, paired differences, intervals, costs, audits, input hashes |
| `raw_checks.py` | Checks that need the raw logs (`derived/raw_checks.csv`, `derived/raw_browser.csv`) |
| `alt_judge_*` | Blind ratings of the alternatives agents chose instead: inputs, the rater's prompt and rules, its labels |
| `budget.py` | The cost model for the follow-up plan (`derived/followup_budget.csv`) |

**`survey/`** has the read-only scanner (`scan.py`, `report.py`, `weight.py`, `stdlib.json`; it runs no repository code) and its outputs (`scan.json`, `weight.json`, `report.txt`, `weight.txt`). **`sources/`** has `repos.txt`, `source_commits.tsv` and `fetch_sources.sh`.

Run records use the setup names from the time the runs were made: `mixed_typical` and `mixed_heavy` are called “mixed, smaller” and “mixed, larger” in the methodology and the post.

## Check your own agent

A skill that runs this check on your own setup is coming soon. Until then, the manual version: go to a real project folder and send a few requests the way you would really ask.

```bash
# Claude Code: prints the skill or MCP tool it selected
claude -p "Audit the SEO of my site." --output-format stream-json --verbose --max-turns 3 \
  | jq -r 'select(.type=="assistant") | .message.content[]?
           | select(.type=="tool_use") | select(.name=="Skill" or (.name|startswith("mcp__")))
           | if .name=="Skill" then "skill: " + .input.skill else "tool: " + .name end'

# Codex: prints the SKILL.md paths named in its commands (a match does not prove
# the read succeeded, and Codex's own skills under skills/.system are not matched)
codex exec --json -s read-only "Audit the SEO of my site." \
  | grep -o 'skills/[a-z0-9-]*/SKILL.md' | sort -u
```

Then repeat with only that skill enabled. A handful of requests won't give you a reliable rate, but it shows whether the skill is ever picked. Three things to know:

- **In `-p` mode, Claude Code refuses MCP calls you have not allowed.** Add `--allowedTools mcp__<server>`.
- **Claude Code keeps a memory per folder.** A note saved in one test run is loaded in the next, so use a fresh folder for every run.
- **Codex has both problems in its own flavour.** With `approval_policy="never"` it blocks MCP calls on servers you have not approved (`-c 'mcp_servers.<name>.default_tools_approval_mode="approve"'`), and it ships 5 skills of its own (`-c skills.bundled.enabled=false`).

## Known limitations (in short)

- **Selection, not quality.** A run without the skill can still produce a fine answer.
- **Minimal setup.** Empty folders, stub instructions, and 3 turns in Claude Code for skills (8 for tools).
- **Few samples.** One sample of extra skills, and six LLM-written requests per target.
- **Few raw logs.** Only the round 2 Claude Code runs (E2/E3, and the 18-run E1 rerun) kept their full event stream. The other runs kept what the agent called, not its text.
- **Listings captured afterwards.** The skill listings were captured after the runs. In Claude Code at ~220 and 1,020 skills, which skills keep a description depends on a usage record that the study's own runs updated, so the exact listing in each run is unknown.
- **Thinner Codex and Fable data.** One run per request, no mixed setups, and GPT-6 Astra has no tool results in the current setup.
- **Configurations, not models.** Differences between harnesses belong to the whole configuration.

The full list is in `METHODOLOGY.md` §13, and a plan for closing the gaps is in `FOLLOWUP_PROTOCOL.md`. Pull requests with reruns on newer harness versions, other models or other harnesses are very welcome.

## License

- Code (`*.py`, `scripts/`): MIT, see [`LICENSE`](LICENSE).
- Data, documentation, the post and its figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Third-party material keeps its own license, see [`THIRD_PARTY.md`](THIRD_PARTY.md).
