# Third-party material

**Skill repositories are not redistributed.** `scripts/fetch_sources.sh` clones the 43 skill repositories at the commits in `source_commits.tsv`. This repository contains only:
- Metadata derived from them by the survey scripts (`scan*.json`, `weight*.json`, `report2.txt`, `weight2.txt`): skill names, file paths, lengths, hashes and issue flags.
- Short quotations of skill names and descriptions where the analysis needs them (`analysis/alt_judge_input.json`, the post).

Each skill belongs to its authors, under its repository's license.

**MCP tool definitions.** `mcp/tools_inventory.json` and `mcp/mcp_targets.json` contain tool names, descriptions and parameter schemas taken from:

| Source | License | Use |
|---|---|---|
| [github/github-mcp-server](https://github.com/github/github-mcp-server) | MIT, © GitHub | GitHub tools, exact schemas |
| [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Apache-2.0 | Chrome DevTools tools |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Apache-2.0, © Microsoft | Playwright tools |
| [icip-cas/LiveMCPBench](https://github.com/icip-cas/LiveMCPBench) | Apache-2.0 | 70 further servers, as packaged by LiveMCPBench |

Some array parameters lacked an `items` schema in the extracted definitions. 85 of them were reconstructed (inventory v2; see `analysis/derived/v2/schema_audit.json` and `METHODOLOGY.md`). The definitions were only *served* to the agents by a stub server; none of these servers was run. The original licenses and notices apply to this material. `source_commits.tsv` also lists Accenture/mcp-bench, which was considered as a source but is not used in the inventory.
