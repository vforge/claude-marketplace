---
name: borrow-skill
description: Copy someone else's Claude Code skill into ~/.claude/skills/ verbatim, with a provenance README. Use when the user says "adopt this skill", "borrow this skill", "add this skill to my global skills", or points at a skill in another repo/plugin pack and wants it locally.
argument-hint: "[skill-source-url]"
---

Borrow a skill from a GitHub repo into `~/.claude/skills/<name>/`: copy every file the skill ships (`SKILL.md`, companion `.md` files, `references/`, `scripts/`) verbatim, then write a one-line `README.md` recording where it came from.

## Steps

1. **Resolve the source.** From `$ARGUMENTS` (a GitHub blob/tree URL, or `owner/repo` plus a path), get `owner`, `repo`, `branch`, and the skill's root directory — the folder containing its `SKILL.md`, not the file itself.
2. **List the skill's files.** `gh api repos/<owner>/<repo>/contents/<path>?ref=<branch>` recursively (descend into subdirectories like `references/`, `scripts/`) to get the full file list under that root. Done when every file under the root — not just `SKILL.md` — is accounted for.
3. **Determine the local name.** Read the `name:` field from the fetched `SKILL.md` frontmatter; that's the target directory name under `~/.claude/skills/`. If `~/.claude/skills/<name>/` already exists, stop and ask before overwriting — don't clobber a skill that may have local edits.
4. **Copy verbatim.** `mkdir -p ~/.claude/skills/<name>/` and fetch each listed file with `curl -sL` from `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`, writing it to the matching relative path under the new skill directory. No edits, no reformatting — byte-for-byte what's upstream.
5. **Write the provenance README.** Single line, matching the existing borrowed skills in this directory (`unslop`, `tdd`, `how`, `writing-for-agents`, ...):

   ```
   Borrowed from <source URL> — copied verbatim on <today's date>[, including its <extra files/subfolders> where present]. Not for agent consumption, just a note to self on where this came from if it needs updating later.
   ```

   Get today's date from the environment context, never hardcode a remembered one.

## Completion criterion

Every file under the skill's upstream root exists locally at the matching relative path, plus the one-line `README.md`. Report the final file list and the path.

## Non-GitHub sources

If the source isn't a GitHub URL (a gist, a blog post, a pasted `SKILL.md`), skip the API listing: fetch or ask for the file content directly, still land it at `~/.claude/skills/<name>/`, and note the actual source form in the README line instead of a `raw.githubusercontent.com` shape.
