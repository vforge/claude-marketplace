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
