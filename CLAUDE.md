# Commit messages

This repo uses [Conventional Commits](https://www.conventionalcommits.org/).

One line: `<type>[optional !]: <description>`, imperative mood, lowercase after the colon. No body, no footer, no trailers — including no `Co-Authored-By:`.

Types used here:
- `feat` — a skill, plugin, or other user-facing capability is added
- `fix` — corrects broken behavior
- `refactor` — restructures existing capability (rename, removal, reorganization) without adding new behavior
- `chore` — metadata, tooling, or housekeeping with no effect on installed capability
- `docs` — documentation only

Append `!` to the type when the change alters something an installed user depends on: a skill name, a command prefix, an install id, a file a skill reads.

# Before committing

`scripts/check-command-refs.sh` catches one specific mistake: a `` /prefix:skill `` reference in a staged Markdown file whose prefix doesn't match any current plugin name — what a rename leaves behind (e.g. `/vforge:idea` surviving the `vforge` → `v` rename). It runs as this clone's `.git/hooks/pre-commit`; since git hooks aren't tracked, a fresh clone needs it copied back into place, or run manually before committing:

```
scripts/check-command-refs.sh
```

It can't catch the other failure mode: skill content carrying over something that shouldn't ship — a leftover non-neutral example, a real path, a name specific to wherever the content was drafted. That needs a read, not a grep. Before committing a new or changed `SKILL.md`, read it once asking "would this mean anything outside this repo?" — a worldbuilding example, a company name, a real file path are all things a keyword search won't reliably catch.
