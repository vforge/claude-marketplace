---
name: archive
description: Move a file into the project's archive directory (.archive, .archived, or zz_archive, whichever exists), preserving its path relative to the project root. Use when asked to archive a file, retire it, or move it out of the way without deleting it. Errors if no archive directory exists, naming what to create.
argument-hint: "<path>"
---

# archive

Move `$ARGUMENTS` into the project's archive directory, keeping its path relative to the project root unchanged.

## 1. Find the archive directory

Project root: `git rev-parse --show-toplevel`, or the current directory if not a git repo.

Check for `.archive`, `.archived`, `zz_archive` at the root, in that order. The first one that exists is the archive directory.

**None exist:** stop. Report which three names were checked and that none exist, and tell the user to create one — `mkdir .archive` at the project root — before retrying. Do not create it yourself.

## 2. Resolve the move

- Resolve `$ARGUMENTS` against the current directory, then take its path relative to the project root — `old.md` given from inside `docs/` is `docs/old.md`.
- Destination: `<archive dir>/<that relative path>`. `foo/bar/baz.md` becomes `<archive dir>/foo/bar/baz.md`.
- Already inside the archive directory: nothing to do, say so.
- Destination already exists: stop and ask — don't silently overwrite an existing archived file.
- Source doesn't exist: stop, name the path that's missing.

## 3. Move it

`mkdir -p` the destination's parent, then pick the move:

- **Source tracked** (`git ls-files --error-unmatch <src>` succeeds) **and destination not ignored** (`git check-ignore -q <dest>` fails): `git mv` — the move is a rename, not a delete-and-add, so history follows the file.
- **Source tracked, destination ignored:** `git rm --cached <src>` then `mv`. A plain `git mv` here would force-track the file inside the ignored archive directory.
- **Source untracked, or not a git repo:** plain `mv` — `git mv` refuses untracked files.

Done when the source path is gone and the destination holds the file with its content unchanged — verify both.

## 4. Report

State the source and destination paths, and which move was used: `git mv` rename, `git rm --cached` + `mv` (file now untracked), or plain `mv`.
