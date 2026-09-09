---
name: flatten-and-rebase
description: Flatten the current branch's commits into one (or N, if given) and rebase onto the latest main/master/origin or a specified base branch. Use when asked to "flatten and rebase", "squash and rebase", "flatten my branch", or "squash all commits onto main".
argument-hint: "[commit-count] [base-branch]"
---

# flatten-and-rebase

Squash the current branch down to N commits (default 1), then rebase it onto
the updated base branch (`origin/<base>`, auto-detected as the repo default
unless given).

## 1. Resolve inputs

- Parse `$ARGUMENTS`: a bare integer → commit count (default `1`); any other
  token → base branch name.
- Base branch default: `git symbolic-ref refs/remotes/origin/HEAD` (strip
  `refs/remotes/origin/`), falling back to `main` or `master`, whichever
  exists.
- Current branch: `git branch --show-current`. Bail if empty (detached HEAD)
  or if it equals the base branch — nothing to flatten.
- Working tree must be clean (`git status --porcelain`) — bail and ask the
  user to commit or stash otherwise.

## 2. Safety net

Before rewriting anything:

```
git branch backup/<branch>-$(date +%Y%m%d-%H%M%S) HEAD
```

Mention this branch in your final report as the rollback path.

## 3. Update the base

```
git fetch origin <base>
```

Rebase target is `origin/<base>` — never mutate the user's local base
branch.

## 4. Flatten to N commits

```
merge_base=$(git merge-base HEAD origin/<base>)
n_commits=$(git rev-list --count "$merge_base"..HEAD)
```

If `n_commits <= N`, skip flattening — nothing to squash.

**N = 1 (default):**

```
git reset --soft "$merge_base"
git commit -m "<message>"
```

Ask the user for the commit message, or default to the branch's first
commit subject.

**N > 1:** split `git rev-list --reverse "$merge_base"..HEAD` into N
contiguous chunks (oldest-first order = todo order). Build a rebase todo
marking each chunk's first commit `pick` and the rest `squash`, then run it
non-interactively — no editor ever opens, so this is safe for a non-TTY
shell:

```
GIT_SEQUENCE_EDITOR="cp <generated-todo-file>" GIT_EDITOR=true \
  git rebase -i "$merge_base"
```

(`GIT_EDITOR=true` accepts the auto-combined commit message for each squash
step — fine for a mechanical flatten.)

## 5. Rebase onto the updated base

```
git rebase origin/<base>
```

On conflicts: stop, surface them to the user, and let them resolve and run
`git rebase --continue` — or `git rebase --abort` to bail out (the backup
branch from step 2 is still there regardless).

## 6. Report — don't push

Show `git log --oneline origin/<base>..HEAD` as confirmation. History was
just rewritten, so **do not push automatically**. Ask the user first; only
on explicit confirmation run:

```
git push --force-with-lease origin <branch>
```
