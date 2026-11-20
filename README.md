# I Installed 1,000 Skills and 791 MCP Tools in Claude Code and Codex

**The right skill was picked far less often. Single-step MCP tool selection in Claude Code held up better.**

This repository has everything behind the blog post: the requests, the experiment scripts, every result record, the analysis that turns those records into the published numbers, the methodology with an external review and my response to it, and the post itself. You can reproduce every number without spending anything, and re-run the experiments if you want to pay for it.

**Read the post: https://galinaalperovich.github.io/in-context-forgetting/**

The page is `docs/index.html`, built from the sources in [`post/`](post/). The figures are also exported as PNGs in [`post/images2/`](post/images2/).

## What was measured

I asked Claude Code and Codex natural requests that were written for one particular skill or MCP tool, such as “Audit the SEO of my site” for `seo-audit`, with no explicit invocation (no `/seo-audit`, no “use the seo-audit skill”). Then I counted how often the agent selected that component as more skills or tools were installed next to it.

| | Claude Code + Haiku | Claude Code + Sonnet | Codex + GPT |
|---|---|---|---|
| **Skills** (E1): target alone → 20 → 220 → 1,020 skills | 78% → 48% → 25% → 16% | 93% → 76% → 56% → 34% | 100% → 99% → 83% → 10% |
| **MCP tools** (E2), 15 single-step targets: alone → 20 → ~220 → 791 tools | 86% → 79% → 78% → 78% | 92% → 81% → 77% → 77% | 91% alone (82 of 90). With 20 tools, only 24 requests were run: 22 of 24, down from 24 of 24 on the same requests. Larger setups not run |
| **Skills + tools together** (E3), change against the single component | skill requests −48 to −59 points (both models); tool requests −9 to −18 | | not run (cost) |

- 4,674 retained runs: 4,020 Claude Code runs and 654 GPT runs. On top of those there is one excluded, rate-limited GPT batch (`gpt_subscription_failed.jsonl`).
- What is measured is **selection of the designated component within the observation window**, not the quality of the answer.
- The full design, statistics, limitations and every number are in [`METHODOLOGY.md`](METHODOLOGY.md). Read it before you reuse a number.

## Reproduce the published numbers (free, about a minute)

```bash
pip install pyyaml               # the only dependency (Python 3.9+)
python3 analysis/analyze.py      # rewrites analysis/REPORT.md and analysis/derived/v2/
git status --short analysis/     # expect no changes: you get the same tables
python3 analysis/budget.py       # the cost model behind the follow-up plan
```

`analysis/derived/v2/manifest.json` records the SHA-256 of every input. The result files (`*.jsonl`) are byte-identical to the ones the analysis was first run on. Only two kinds of file differ from my working copy: scripts whose machine-specific paths became environment variables, and `scan*.json`, where other people's home-folder names found by the survey scanner were replaced with `<user>`.

To rebuild the post and its figures:

```bash
cd post
python3 figs2.py && python3 build_post2.py    # -> skills-mcp-post.html (identical to the shipped one)
python3 build_page.py                         # -> ../docs/index.html, the standalone page served by GitHub Pages
python3 export_png2.py                        # -> images2/*.png (needs Google Chrome; set CHROME_BIN if it is elsewhere)
```

## Re-run the experiments (costs money)

**Prerequisites**
- Claude Code (the study used v2.1.328) and/or Codex CLI (v0.160.0), Python 3.9+ with PyYAML, and git.
- Versions matter. Both harnesses change how they list skills and tools between releases, so expect your numbers to differ from mine on newer versions. That difference is a finding in itself.

**1. Fetch the sources at the exact commits used.** Third-party repositories are not redistributed here.
```bash
scripts/fetch_sources.sh          # 43 skill repositories -> third_party/repos/
scripts/fetch_sources.sh --mcp    # optional: MCP tool sources -> third_party/mcp/ (not needed to run; the inventory is frozen)
```

**2. Build the test folders.** I checked that both builds reproduce the original folders byte for byte from the pinned commits.
```bash
python3 build.py          # E1 -> envs/  (alone, pack20, crowd200, crowd1000)
python3 mcp/build_v2.py   # E2/E3 -> envs2/  (MCP-only setups, trending skills alone, two mixed setups)
```

**3. Run.** Always write to a **new** output file. The runners resume from the file you name, so never point them at the shipped results.
```bash
# E1, skills only. Arguments: setups, repeats per request, model, output file
python3 run.py alone,pack20,crowd200,crowd1000 1 haiku  results/haiku_rerun.jsonl
python3 run.py alone,pack20,crowd200,crowd1000 3 sonnet results/sonnet_rerun.jsonl
python3 run_codex.py alone,pack20,crowd200,crowd1000 1 medium results/gpt_rerun.jsonl

# E2 (MCP only), E3b (trending skills alone), E3 (mixed). Arguments: harness, model, job set, output file
python3 mcp/run2.py claude haiku mcp   results/haiku_mcp.jsonl
python3 mcp/run2.py claude sonnet mixed results/sonnet_mixed.jsonl
python3 mcp/run2.py codex  gpt   mcp   results/gpt_mcp.jsonl
```
- Run `mkdir results` first.
- Useful environment variables:
  - `PAR`: parallel runs (default 6 for E1, 4 for E2/E3).
  - `ONLY_ENV` and `ONLY_I`: run a subset.
  - `STOP_ON_429=1`: stop at the first rate limit.
  - `SKILL_REPOS` and `ENVS2_DIR`: move the inputs and test folders.
  - `CODEX_BIN`: the path to Codex.
- For Codex, use a separate `CODEX_HOME` that is logged in with an API key, so your personal Codex settings and skills don't leak into the runs.
- `analysis/analyze.py` reads the original file names. To analyse a rerun, point its input list at your files.

**What it costs** (list prices; details in `analysis/derived/v2/cost_by_batch.csv`)

| Configuration | Per run | This study |
|---|---|---|
| Claude Code, Haiku | about $0.002–0.009 | covered by a Claude subscription ($192.61 list price for all 4,020 Claude runs) |
| Claude Code, Sonnet | about $0.03–0.14 | (included above) |
| Codex + GPT, skills (E1) | $0.19–0.31 measured | $119.13 for 480 runs |
| Codex + GPT, MCP alone / 20 tools | $0.29 / $0.35 measured | $52.60 for 170 API runs |
| Codex + GPT, ~220 / 791 tools | about $0.83 / $2.08 **estimated** | not run |
| Codex + GPT, mixed setups | about $1.5–2.2 **estimated** | not run |

Most of a GPT run's cost is writing the prompt prefix (system prompt, skill listing, tool definitions) to the cache, because every run is a new session. Use `STOP_ON_429` and a spending limit on your API key.

**Safety.**
- Every skill keeps its real name and description, but its instructions are replaced with a one-line stub. Every MCP tool is served by `mcp/stub_server.py`, which returns its definition and a stub result. No code from the fetched repositories is ever run.
- Claude Code runs use `--disallowedTools Bash --strict-mcp-config --setting-sources project`, and Codex runs use `-s read-only`.
- Built-in web tools were **not** disabled, so a run can fetch public web pages.

## Repository layout

| Path | What it is |
|---|---|
| `METHODOLOGY.md` | The current methodology (v2): design, measurement, statistics, all results, boundaries |
| `METHODOLOGY_v1.md`, `METHODOLOGY_REVIEW.md` | The first version, and the external review it received |
| `analysis/CHANGELOG.md` | Response to the review, claim by claim: corrected, narrowed, removed, unresolved |
| `FOLLOWUP_PROTOCOL.md` | A costed plan to finish the study (proposal, not results) |
| `prompts.json`, `mcp/trending_skill_prompts.json`, `mcp/mcp_targets.json` | The 20 skill targets, the 5 trending skills and the 20 MCP tool targets, each with 6 requests |
| `build.py`, `run.py`, `run_codex.py` | E1: build the skill setups; run Claude Code; run Codex |
| `mcp/build_v2.py`, `mcp/run2.py`, `mcp/stub_server.py` | E2, E3, E3b: build the MCP and mixed setups; run both harnesses; the stub MCP server |
| `mcp/tools_inventory.json` | The frozen inventory of 791 MCP tool definitions from 73 servers (see `THIRD_PARTY.md`) |
| `haiku.jsonl`, `sonnet.jsonl`, `gpt.jsonl` | E1 results: one record per run |
| `gpt_subscription_failed.jsonl` | The excluded E1 GPT batch (rate-limited subscription runs), kept for transparency |
| `mcp/haiku_v2.jsonl`, `mcp/sonnet_v2.jsonl`, `mcp/gpt_v2.jsonl` | E2, E3 and E3b results |
| `analysis/analyze.py` | The single entry point that produces every published number |
| `analysis/REPORT.md`, `analysis/derived/v2/` | Its outputs: rates, paired differences, intervals, costs, audits, input hashes |
| `analysis/alt_judge_*` | Blind rating of the 210 alternatives agents chose: input, the rater's prompt, its rules, its labels |
| `analysis/budget.py` | The cost model for the follow-up plan |
| `scan.py`, `report.py`, `weight.py`, `stdlib.json` | Experiment 0: the static survey of skill repositories (read-only, runs no repo code) |
| `scan2.json`, `weight2.json`, `report2.txt`, `weight2.txt` | Survey outputs for the 42 repositories used in v2 (`scan.json` and `weight.json` are the earlier, smaller survey) |
| `repos.txt`, `source_commits.tsv` | Source repositories and the exact commits used |
| `scripts/fetch_sources.sh` | Clones every source at its pinned commit |
| `post/` | The blog post's builder, figure code and PNG exports |
| `docs/` | The published post (GitHub Pages) |

Run records use the setup names from the time the runs were made: `mixed_typical` and `mixed_heavy` are called “mixed, smaller” and “mixed, larger” in the methodology and the post.

## Known limitations (short version)

- **Selection, not quality.** A run without the skill can still produce a fine answer.
- **Minimal setup.** Empty folders, stub instructions, and 3–4 turns in Claude Code.
- **Few samples.** One sample of extra skills, and six requests per target, all written by me.
- **No raw logs.** The retained runs kept what the agent called, not its text.
- **Thinner GPT data.** One run per request, and only two MCP setups.
- **Configurations, not models.** Differences between harnesses belong to the whole configuration.

The full list is in `METHODOLOGY.md` §12, and a plan for closing the gaps is in `FOLLOWUP_PROTOCOL.md`. Pull requests with reruns on newer harness versions, other models or other harnesses are very welcome.

## License

- Code (`*.py`, `scripts/`): MIT, see [`LICENSE`](LICENSE).
- Data, documentation, the post and its figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Third-party material keeps its own license, see [`THIRD_PARTY.md`](THIRD_PARTY.md).
