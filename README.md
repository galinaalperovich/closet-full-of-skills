# A Closet Full of Skills and Nothing to Wear

**The more skills you install, the less often your coding agent picks the right one. MCP tools hold up better.** Measured with up to 1,000 skills and 791 MCP tools in Claude Code and Codex.

This repository has everything behind the blog post: the requests, the experiment scripts, every result record, the analysis that turns those records into the published numbers, the captured skill listings, the methodology, and the post itself. You can reproduce every number without spending anything, and re-run the experiments if you want to pay for it.

**Read the post: https://galinaalperovich.github.io/closet-full-of-skills/**

The page is `docs/index.html`, built from the sources in [`post/`](post/). The figures are also exported as PNGs in [`post/images/`](post/images/). A readable Markdown copy of the post is in [`post/post.md`](post/post.md): to suggest a change to the text, edit that file in a pull request. Accepted changes are carried over into `post/build_post.py`, which builds the page.

## What was measured

I asked Claude Code and Codex natural requests that were written for one particular skill or MCP tool, such as “Audit the SEO of my site” for `seo-audit`, with no explicit invocation (no `/seo-audit`, no “use the seo-audit skill”). Then I counted how often the agent selected that component as more skills or tools were installed next to it.

| | Skills (E1): target alone → 20 → 220 → 1,020 skills | MCP tools (E2), 15 single-step targets: alone → 20 → ~220 → 791 tools |
|---|---|---|
| Claude Code + Haiku | 78% → 48% → 25% → 16% | 84% → 82% → 79% → 80% |
| Claude Code + Sonnet | 94% → 76% → 56% → 34% | 88% → 76% → 78% → 77% |
| Claude Code + Fable 5.2 | 99% → 99% → 98% → 72% | 89% → 84% → 82% → 82% |
| Codex + GPT-6 Astra | 100% → 99% → 83% → 10% | 91% alone (82 of 90). With 20 tools only 24 requests were run: 92% (22 of 24), down from 100% (24 of 24) on the same requests. Larger setups not run |
| Codex + GPT-6 Sol | 100% → 100% → 82% → 12% | 78% → 50% → 40% → 32%, with strong caveats: Codex blocked the MCP calls, had built-in web search, and one target could be done in the shell (`METHODOLOGY.md` §14) |

**Skills + tools together** (E3, Haiku and Sonnet only), change against the single component: skill requests −46 to −60 points, tool requests −6 to −18.

- 6,594 retained runs: 4,980 Claude Code runs and 1,614 Codex runs. On top of those there is one excluded, rate-limited GPT batch (`gpt_subscription_failed.jsonl`).
- **Two rounds of data collection.** Round 1 (20 November 2026): E1 for all three configurations, E3b, every Codex run, and a first pass of the Claude Code E2/E3 runs. Round 2 (22 November 2026): all 2,040 Claude Code E2/E3 runs again, because headless Claude Code had refused every MCP call and its per-folder auto-memory had carried notes from one run to the next. The 18 E1 runs of the one skill folder with a carried-over memory note (Sonnet, `caveman`, alone) were rerun the same way. The numbers above use round 2 for Claude Code E2/E3. Details are in `METHODOLOGY.md` §1.1.
- **Two more configurations** were added on 25 November 2026, with the same harness versions, requests and setups: Claude Fable 5.2 in Claude Code and GPT-6 Sol in Codex, each with E1 (one run per request) and E2. They were not run in E3. Design, results and caveats are in `METHODOLOGY.md` §14.
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

`analysis/derived/manifest.json` records the SHA-256 of every input. The result files (`*.jsonl`) are byte-identical to the ones the analysis was first run on. Only two kinds of file differ from my working copy: scripts whose machine-specific paths became environment variables, and `scan.json`, where other people's home-folder names found by the survey scanner were replaced with `<user>`.

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
scripts/fetch_sources.sh          # 43 skill repositories -> third_party/repos/
scripts/fetch_sources.sh --mcp    # optional: MCP tool sources -> third_party/mcp/ (not needed to run; the inventory is frozen)
```

**2. Build the test folders.** I checked that both builds reproduce the original folders byte for byte from the pinned commits.
```bash
python3 build.py          # E1 -> envs/  (alone, pack20, crowd200, crowd1000)
python3 mcp/build.py      # E2/E3 -> envs2/  (MCP-only setups, trending skills alone, two mixed setups)
```

**3. Run.** Always write to a **new** output file. The runners resume from the file you name, so never point them at the shipped results.
```bash
# E1, skills only. Arguments: setups, repeats per request, model, output file
ISOLATE=1 python3 run.py alone,pack20,crowd200,crowd1000 1 haiku  results/haiku_rerun.jsonl
ISOLATE=1 python3 run.py alone,pack20,crowd200,crowd1000 3 sonnet results/sonnet_rerun.jsonl
python3 run_codex.py alone,pack20,crowd200,crowd1000 1 medium results/gpt_rerun.jsonl
CODEX_MODEL=gpt-6-sol python3 run_codex.py alone,pack20,crowd200,crowd1000 1 medium results/gpt_sol_rerun.jsonl

# E2 (MCP only), E3b (trending skills alone), E3 (mixed). Arguments: harness, model, job set, output file
ALLOW_MCP=1 ISOLATE=1 LOAD_MAX=20 PAR=2 python3 mcp/run.py claude haiku mcp   results/haiku_mcp.jsonl
ALLOW_MCP=1 ISOLATE=1 LOAD_MAX=20 PAR=2 python3 mcp/run.py claude sonnet mixed results/sonnet_mixed.jsonl
python3 mcp/run.py codex  gpt   mcp   results/gpt_mcp.jsonl
CODEX_MODEL=gpt-6-sol python3 mcp/run.py codex gpt-6-sol mcp results/gpt_sol_mcp.jsonl
```
- Run `mkdir results` first.
- Useful environment variables:
  - `PAR`: parallel runs (default 6 for E1, 4 for E2/E3).
  - `ONLY_ENV`, `ONLY_I` and `ONLY_TARGET`: run a subset (`run.py` takes `ONLY_TARGET`).
  - `STOP_ON_429=1`: stop at the first rate limit.
  - `ALLOW_MCP=1` (Claude Code): pre-approve the stub MCP servers. Without it, headless Claude Code refuses every MCP call, which is what happened in round 1.
  - `ISOLATE=1` (Claude Code, `run.py` and `mcp/run.py`): run each job in a fresh copy of its test folder, so Claude Code's per-folder auto-memory starts empty every time, and keep the raw output. It does not reset Claude Code's global skill-usage record (`skillUsage` in `~/.claude.json`), which decides which descriptions survive in large listings (`METHODOLOGY.md` §10).
  - `LOAD_MAX=<n>`: wait before starting a job while the 1-minute load average is above n. The mixed setups start up to 73 stub servers per run; 8 parallel runs once made a 10-core laptop unresponsive.
  - `SKILL_REPOS`, `ENVS_DIR` and `ENVS2_DIR`: move the inputs and test folders.
  - `CODEX_MODEL`: the Codex model (`run_codex.py`: the Codex default when unset; `mcp/run.py`: `gpt-6-astra` when unset).
  - `CODEX_BIN`: the path to Codex.
- For Codex, use a separate `CODEX_HOME` that is logged in with an API key, so your personal Codex settings and skills don't leak into the runs.
- `analysis/analyze.py` reads the shipped file names (the `INPUTS` list at its top). To analyse a rerun, point that list at your files.

**Captured listings (free, no model calls).** `listing/capture.py` records what each harness sends to the model in each skills setup, using a local stand-in server. See [`listing/README.md`](listing/README.md).

**What it costs** (list prices; details in `analysis/derived/cost_by_batch.csv`)

| Configuration | Per run | This study |
|---|---|---|
| Claude Code, Haiku | about $0.002–0.009 | covered by a Claude subscription ($198.02 list price for the 4,020 Claude runs in the results, plus $149.64 for 3,233 runs not used in the results) |
| Claude Code, Sonnet | about $0.03–0.14 | (included above) |
| Claude Code, Fable 5.2 | about $0.12–0.38 | covered by the same subscription ($211.81 list price for 960 runs) |
| Codex + GPT, skills (E1) | $0.19–0.31 measured | $119.13 for 480 runs |
| Codex + GPT, MCP alone / 20 tools | $0.29 / $0.35 measured | $52.60 for 170 API runs |
| Codex + GPT, ~220 / 791 tools | about $0.44 / $0.46 **estimated** from GPT-6 Sol's usage, at five times its price | not run |
| Codex + GPT-6 Sol, skills (E1) | $0.05–0.08 measured | $30.81 for 480 runs |
| Codex + GPT-6 Sol, MCP (E2) | $0.07–0.09 measured | $39.00 for 480 runs |
| Codex + GPT, mixed setups | about $1.5–2.2 **estimated** | not run |

Most of a GPT run's cost is writing the prompt prefix (system prompt, skill listing, tool definitions) to the cache, because every run is a new session. Use `STOP_ON_429` and a spending limit on your API key.

**Safety.**
- Every skill keeps its real name and description, but its instructions are replaced with a one-line stub. Every MCP tool is served by `mcp/stub_server.py`, which returns its definition and a stub result. No code from the fetched repositories is ever run.
- Claude Code runs use `--disallowedTools Bash --strict-mcp-config --setting-sources project`, and Codex runs use `-s read-only`.
- Built-in web tools were not disabled. In headless mode, with nobody to approve, Claude Code refused web searches and most page fetches (it allows a few documentation sites). Codex's own web search worked.

## Repository layout

| Path | What it is |
|---|---|
| `METHODOLOGY.md` | The methodology: design, measurement, statistics, all results, boundaries |
| `FOLLOWUP_PROTOCOL.md` | A costed plan to finish the study (proposal, not results) |
| `prompts.json`, `mcp/trending_skill_prompts.json`, `mcp/mcp_targets.json` | The 20 skill targets, the 5 trending skills and the 20 MCP tool targets, each with 6 requests |
| `build.py`, `run.py`, `run_codex.py` | E1: build the skill setups; run Claude Code; run Codex |
| `mcp/build.py`, `mcp/run.py`, `mcp/stub_server.py` | E2, E3, E3b: build the MCP and mixed setups; run both harnesses; the stub MCP server |
| `mcp/tools_inventory.json` | The frozen inventory of 791 MCP tool definitions from 73 servers (see `THIRD_PARTY.md`) |
| `haiku.jsonl`, `sonnet.jsonl`, `gpt.jsonl`, `fable.jsonl`, `gpt_sol.jsonl` | E1 results: one record per run (`gpt.jsonl` is GPT-6 Astra) |
| `sonnet_e1_caveman_rerun.jsonl`, `raw_e1/` | E1 rerun of Sonnet / `caveman` / alone (18 runs, one fresh folder each) and its raw logs, plus the raw logs of the Fable E1 runs; used in place of those 18 records of `sonnet.jsonl` |
| `gpt_subscription_failed.jsonl` | The excluded E1 GPT batch (rate-limited subscription runs), kept for transparency |
| `mcp/haiku_round1.jsonl`, `mcp/sonnet_round1.jsonl`, `mcp/gpt.jsonl` | E2, E3 and E3b results from round 1 (the analysis uses the GPT and E3b records) |
| `mcp/haiku_round2.jsonl`, `mcp/sonnet_round2.jsonl` | Claude Code E2 and E3 results from round 2 (MCP allowed, a fresh folder per run) |
| `mcp/fable.jsonl`, `mcp/gpt_sol.jsonl` | E2 results for Fable 5.2 (run like round 2) and GPT-6 Sol (run like GPT-6 Astra) |
| `mcp/raw/` | Raw event logs of round 2 and of the Fable E2 runs, with local paths removed |
| `analysis/analyze.py` | The single entry point that produces every published number |
| `analysis/REPORT.md`, `analysis/derived/` | Its outputs: rates, paired differences, intervals, costs, audits, input hashes |
| `analysis/raw_checks.py` | Raw-log checks for the round 2 runs (`derived/raw_checks.csv`, `derived/raw_browser.csv`) |
| `analysis/alt_judge_*` | Blind rating of the 210 alternatives agents chose: input, the rater's prompt, its rules, its labels |
| `analysis/budget.py` | The cost model for the follow-up plan (`derived/followup_budget.csv`) |
| `listing/` | Captured skill listings: what each harness sent to the model in each skills setup (no model called) |
| `scan.py`, `report.py`, `weight.py`, `stdlib.json` | Experiment 0: the static survey of skill repositories (read-only, runs no repo code) |
| `scan.json`, `weight.json`, `report.txt`, `weight.txt` | Survey outputs for the 42 repositories that contain skills |
| `repos.txt`, `source_commits.tsv` | Source repositories and the exact commits used |
| `scripts/fetch_sources.sh` | Clones every source at its pinned commit |
| `post/` | The blog post's builder, figure code, PNG exports and a Markdown copy (`post.md`) |
| `docs/` | The published post (GitHub Pages) |

Run records use the setup names from the time the runs were made: `mixed_typical` and `mixed_heavy` are called “mixed, smaller” and “mixed, larger” in the methodology and the post.

## Known limitations (in short)

- **Selection, not quality.** A run without the skill can still produce a fine answer.
- **Minimal setup.** Empty folders, stub instructions, and 3–4 turns in Claude Code.
- **Few samples.** One sample of extra skills, and six LLM-written requests per target.
- **Few raw logs.** Only the round 2 Claude Code runs (E2/E3, and the 18-run E1 rerun) kept their full event stream. The other runs kept what the agent called, not its text.
- **Listings captured afterwards.** The skill listings were captured after the runs. In Claude Code at ~220 and 1,020 skills, which skills keep a description depends on a usage record that the study's own runs updated, so the exact listing in each run is unknown.
- **Thinner GPT data.** One run per request, and only two MCP setups.
- **Configurations, not models.** Differences between harnesses belong to the whole configuration.

The full list is in `METHODOLOGY.md` §13, and a plan for closing the gaps is in `FOLLOWUP_PROTOCOL.md`. Pull requests with reruns on newer harness versions, other models or other harnesses are very welcome.

## License

- Code (`*.py`, `scripts/`): MIT, see [`LICENSE`](LICENSE).
- Data, documentation, the post and its figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Third-party material keeps its own license, see [`THIRD_PARTY.md`](THIRD_PARTY.md).
