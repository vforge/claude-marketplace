---
name: setup-here
description: Wire a git checkout's .atlas and .specstory symlinks to the shared stores — .atlas to the Atlas vault's work/ directory, .specstory to the specstory store keyed by git remote. Use when setting up a new checkout or worktree, when artifacts have nowhere to go, or when a link is missing, dangling, or pointing at the wrong target.
argument-hint: "[checkout-path]"
---

# setup-here

Give a checkout its two gitignored symlinks. Both targets are **derived** — nothing to choose:

```
.atlas     -> Atlas/work/                  the same target in every checkout
.specstory -> specstory/<remote-repo-name>/  parallel checkouts share one
```

`$ARGUMENTS` is the checkout path; default to `git rev-parse --show-toplevel`.

## Happy path

```sh
"$CLAUDE_SKILL_DIR/setup-here.sh" "<checkout-path>"
```

The script derives the remote name, creates `specstory/<remote>/` on demand, replaces existing symlinks, and warns if either path isn't gitignored. If it succeeds, verify and report — that's the whole job.

## The cases the script deliberately refuses

**`.atlas` or `.specstory` is a real directory, not a symlink.** The script stops rather than clobber data. Migrate first:

1. Copy its contents into `Atlas/work/<ticket-or-slug>/` — one directory per ticket or topic, **never per repo**. Add frontmatter per `Atlas/AGENTS.md`.
2. Where a filename already exists in `work/`, compare contents. Identical → one file, with both repos in `repos:`. Different → genuine **variants**, kept as `<name>--<repo>.md` with `variant:` set. Never silently pick a winner.
3. `cmp` every file against its copy before deleting the original.
4. Then run the script.

**A link points somewhere other than the two targets above.** An older layout keyed artifacts per repo (and an even older one nested both under `ai/_misc`/`ai/_specstory`); anything still pointing at either is writing where nothing reads. Copy any content forward into `Atlas/work/<ticket-or-slug>/` before repointing.

**Not gitignored.** The global `~/.gitignore-global` patterns `.atlas` and `.specstory` should cover both. If a repo lacks that protection, add `.atlas` and `.specstory` to `<checkout>/.git/info/exclude`. Note a trailing-slash pattern (`.atlas/`) matches directories but **not** symlinks — a repo relying on that form is unprotected.

## Verify before reporting success

```sh
ls -A "<checkout>/.atlas/"        # trailing slash matters
ls -A "<checkout>/.specstory/"
git -C "<checkout>" status --porcelain      # must be unchanged
git -C "<checkout>" check-ignore .atlas .specstory
```

**Without the trailing slash `ls` lists the symlink itself**, so a working link looks like it holds exactly one entry. This has caused a false alarm before.

Claude Code also needs the vault in `permissions.additionalDirectories` to write *through* `.atlas` without prompts — already configured for `Atlas`.

## Scope

One checkout. To audit many at once — stale links, unmigrated content, artifacts drifting outside the vault — use `/check-ai-dirs` in the Atlas vault instead.
