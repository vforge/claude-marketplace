#!/usr/bin/env bash
# Wire a checkout's two hidden symlinks to their shared stores:
#
#   .atlas     -> Atlas/work/                     artifact store — the SAME target for
#                                                  every checkout. Keyed by ticket inside,
#                                                  not by repo, so cross-repo work has one
#                                                  home and any repo can read any ticket.
#   .specstory -> specstory/<remote-repo-name>/    SpecStory VS Code extension output,
#                                                  keyed by git remote so parallel checkouts
#                                                  (my-repo, my-repo-ai, my-repo-test) share
#                                                  one history.
#
# Both names must stay gitignored — the global ~/.gitignore-global patterns `.atlas` and
# `.specstory` are what keep them off GitHub. Claude Code also needs Atlas in
# permissions.additionalDirectories to write through .atlas without sandbox prompts.
#
# Usage: setup-here.sh <checkout-path>
# Example: setup-here.sh ~/Developer/myorg/my-repo-worktree-x
#
# Requires ATLAS_VAULT_ROOT: the parent directory containing Atlas/ and
# specstory/ (set it in your shell profile — this script ships in the skill
# directory, not next to the stores it wires up, so the path can't be derived).
set -euo pipefail

ROOT="${ATLAS_VAULT_ROOT:?set ATLAS_VAULT_ROOT to the parent dir of Atlas/ and specstory/}"
WORK="$ROOT/Atlas/work"
SPECSTORY="$ROOT/specstory"
repo="${1:?usage: setup-here.sh <checkout-path>}"

cd "$repo"

# specstory keys on the remote repo name, not the checkout directory name
remote="$(git remote get-url origin 2>/dev/null | sed 's|.*[/:]||; s|\.git$||')"
[ -n "$remote" ] || { echo "ERROR: no git remote in $repo — cannot derive specstory key" >&2; exit 1; }

link_to() {  # $1 = link name at repo root   $2 = target dir
  local link="$1" target="$2"
  [ -d "$target" ] || { echo "ERROR: $target does not exist" >&2; exit 1; }
  if [ -L "$link" ]; then
    rm "$link"
  elif [ -e "$link" ]; then
    echo "ERROR: $repo/$link exists and is not a symlink — merge its contents into $target first" >&2
    exit 1
  fi
  ln -s "$target" "$link"
  echo "linked $link -> $target"
}

# A new repo's session directory carries no history worth scaffolding — just make it.
mkdir -p "$SPECSTORY/$remote"

link_to .atlas     "$WORK"
link_to .specstory "$SPECSTORY/$remote"

# The symlinks must be gitignored (global ~/.gitignore-global has .atlas and .specstory).
for link in .atlas .specstory; do
  git -C "$repo" check-ignore -q "$link" \
    || echo "WARNING: $link is NOT gitignored in this checkout — add it to .git/info/exclude" >&2
done
