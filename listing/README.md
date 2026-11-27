# Captured skill listings

What Claude Code and Codex put in the skill listing they send to the model, in each skills setup of Experiment 1. Captured on 24 November 2026, after the main runs, with the harness versions of the study (Claude Code 2.1.328, Codex CLI 0.160.0). The method and findings are also in `METHODOLOGY.md` §10.

## How it works

- `capture.py` runs each harness exactly as in the study (same commands, flags and test folders), but points it at a local stand-in server instead of the model API. The server records the first model request and returns a canned reply, which ends the run.
- No model is called, and nothing reaches Anthropic or OpenAI. Request headers, which carry credentials, are never stored.
- It sends one request per target folder in `alone` (the target's first request in `skills/prompts.json`) and one request (the first `pdf` request) in each of `pack20`, `crowd200` and `crowd1000`.
- `analyze_listing.py` reads the recorded requests, extracts the skill listing and writes the two CSV files. No request text is copied into them.
- The raw request bodies are not published, because they contain the harness system prompts and local paths.
- Skills only. The MCP setups were not captured.

## Files

| File | Content |
|---|---|
| `capture.py` | Runs the harnesses against the stand-in server and saves each request body to a folder you name |
| `analyze_listing.py` | Turns the saved requests into the two CSV files |
| `summary.csv` | One row per harness and setup: entries, entries with a description, listing characters, targets listed, targets with a description (and their names) |
| `targets.csv` | One row per harness, setup and target: listed (1/0), description characters shown, description characters installed |

The `harness` column:

| Value | What was captured |
|---|---|
| `claude` | Claude Code with Haiku, using the skill-usage record as it stood after the study |
| `claude-sonnet` | The same with Sonnet (the listing is identical to Haiku's) |
| `claude-fable` | The same with Fable 5.2, captured on 25 November 2026 after its runs (`pack20`, `crowd200` and `crowd1000`; the listing is identical to Haiku's) |
| `claude-fresh` | Claude Code with a clean usage record (a separate `CLAUDE_CONFIG_DIR`) |
| `claude-seeded` | Claude Code with a usage record seeded with heavy use of `seo-audit` and `pdf` |
| `codex` | Codex CLI |

## Findings

| Setup | Claude Code | Codex |
|---|---|---|
| `alone` | The target, with its full description (all 20 folders) | The target, with its full description (all 20 folders) |
| `pack20` (20 skills) | All 37 entries (20 targets + 17 harness skills), full descriptions | All 24 entries, full descriptions |
| `crowd200` (~220 skills) | 237 entries, only 100 with a description; the rest name only | All 224 entries, every description cut to about 30 characters |
| `crowd1000` (1,020 skills) | All 1,037 names, only 19 with a description | 321 entries: its own 4 skills, then installed skills in alphabetical order up to “developer-listening”; no descriptions; 3 of the 20 targets |

- At 20 skills, both harnesses listed every description in full. The decline at 20 skills happened with every description visible.
- Claude Code capped the listing at about 30,000 characters in both the ~220 and the 1,020 setups.
- Codex at 1,020 skills listed only 3 of the 20 targets: `animate`, `caveman` and `copywriting`. In the study, 11 of GPT-6 Astra's 12 hits at 1,020 skills were exactly these three targets (`copywriting` 5/6, `animate` 4/6, `caveman` 2/6, plus `json-canvas` 1/6), and every alternative it picked was alphabetically early.
- Which Claude Code skills keep a description depends on its global usage record (`skillUsage` in `~/.claude.json`: a use count and last-used time per skill, shared across projects):
  - with the record as it stood after the study: 3 of the 20 targets at 1,020 skills (`grill-me`, `json-canvas`, `tdd`), all 20 at ~220;
  - with a clean record: none at 1,020, and 8 at ~220 (the alphabetically first, `animate` … `humanizer`);
  - with a record seeded with heavy use of `seo-audit` and `pdf`: exactly those two at 1,020.
- Haiku and Sonnet received the same listing.

**What this means for the study.** The study's own runs updated the usage record, because each `Skill` call counts. So for Claude Code at ~220 and 1,020 skills, the listing could change during the study, favouring skills that had been selected earlier. The exact listing in each original run cannot be reconstructed.

## Reproduce

You need Claude Code and/or Codex CLI, and the E1 test folders in `envs/` (`python3 skills/build.py`, see the main `README.md`). Keep the capture folder outside the repository: the request bodies contain system prompts and local paths.

```bash
python3 listing/capture.py /path/to/captures              # both harnesses; add "claude" or "codex" to run one
python3 listing/analyze_listing.py /path/to/captures      # -> listing/summary.csv and listing/targets.csv
```

Environment variables for `capture.py`:
- `MODEL`: the Claude Code model (default `haiku`).
- `CONFIG_DIR`: a separate Claude Code state folder, passed as `CLAUDE_CONFIG_DIR`. Use it for a clean or seeded usage record.
- `TAG`: a suffix for the harness label, for example `TAG=-fresh` gives `claude-fresh`.
- `ONLY`: a comma-separated list of setups, for example `ONLY=crowd1000`.
- `CODEX_BIN`: the path to Codex.
