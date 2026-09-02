#!/bin/sh
# Fails if a staged Markdown file references a /prefix:skill command whose
# prefix doesn't match any current plugin name — the mistake a plugin rename
# leaves behind (e.g. /vforge:idea surviving the vforge -> v rename).
# Scoped to README.md and skill docs; CLAUDE.md and other meta-docs are
# excluded since they cite stale-looking examples on purpose.
set -eu
cd "$(git rev-parse --show-toplevel)"

valid_prefixes=$(find plugins -maxdepth 3 -path '*/.claude-plugin/plugin.json' -exec sh -c 'grep -m1 "\"name\"" "$1"' _ {} \; \
  | sed -E 's/.*"name": *"([^"]+)".*/\1/' | sort -u)

fail=0
staged_md=$(git diff --cached --name-only --diff-filter=ACM -- 'README.md' 'plugins/*/skills/**/*.md')

for f in $staged_md; do
  refs=$(git show ":$f" | grep -oE '/[A-Za-z0-9_-]+:[A-Za-z0-9_-]+' | sed -E 's#^/([^:]+):.*#\1#' | sort -u || true)
  for prefix in $refs; do
    if ! printf '%s\n' "$valid_prefixes" | grep -qx "$prefix"; then
      echo "check-command-refs: $f references '/$prefix:...' — no plugin named '$prefix' exists (valid: $(printf '%s' "$valid_prefixes" | tr '\n' ' '))" >&2
      fail=1
    fi
  done
done

if [ "$fail" -ne 0 ]; then
  echo "check-command-refs: fix stale skill-command references before committing." >&2
  exit 1
fi
