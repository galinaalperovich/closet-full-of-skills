#!/usr/bin/env bash
# Clone every source repository at the exact commit used in the study (source_commits.tsv).
#   scripts/fetch_sources.sh            skill repositories -> third_party/repos/<owner>_<repo>
#   scripts/fetch_sources.sh --mcp      also the MCP tool sources -> third_party/mcp/<owner>_<repo>
#   ONLY="owner/repo other/repo" scripts/fetch_sources.sh   fetch a subset
# Nothing is executed from the cloned repositories; the build scripts only read SKILL.md frontmatter.
set -euo pipefail
cd "$(dirname "$0")/.."
MCP_SOURCES="Accenture/mcp-bench ChromeDevTools/chrome-devtools-mcp github/github-mcp-server icip-cas/LiveMCPBench microsoft/playwright-mcp"
WITH_MCP=0; [ "${1:-}" = "--mcp" ] && WITH_MCP=1
fail=0
while IFS=$'\t' read -r repo commit date; do
  [ "$repo" = "repo" ] && continue
  if [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $repo "* ]]; then continue; fi
  if [[ " $MCP_SOURCES " == *" $repo "* ]]; then
    [ "$WITH_MCP" = 1 ] || continue; dest="third_party/mcp/${repo/\//_}"
  else
    dest="third_party/repos/${repo/\//_}"
  fi
  if [ -d "$dest/.git" ]; then echo "exists  $repo"; else
    mkdir -p "$(dirname "$dest")"
    git clone --quiet --filter=blob:none --no-checkout "https://github.com/$repo.git" "$dest" || { echo "FAILED  $repo (clone)"; fail=1; continue; }
  fi
  if git -C "$dest" -c advice.detachedHead=false checkout --quiet "$commit" 2>/dev/null; then echo "ok      $repo @ ${commit:0:10} ($date)"
  else echo "FAILED  $repo: commit $commit not found (force-pushed or deleted upstream)"; fail=1; fi
done < source_commits.tsv
exit $fail
