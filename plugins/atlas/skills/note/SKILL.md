---
name: note
description: Save an artifact into the Atlas knowledge base with the correct name, frontmatter and revision chain — plans, specs, reviews, PR descriptions, research notes, ideas, meeting transcripts. Handles the immutable-revision bookkeeping (find the previous version, bump -vN, set supersedes/status) that is easy to skip by hand. Use when writing any personal or temporary artifact, when asked to "save this", "note this", "write this up", or when revising an artifact that already exists.
argument-hint: "[ticket-or-slug] [type]"
---

# note

Write an artifact into **Atlas** — the knowledge base at `$ATLAS_VAULT_ROOT/Atlas` — correctly named, correctly frontmattered, and correctly linked to whatever it supersedes.

Full conventions: `Atlas/AGENTS.md`. This skill exists because the revision rules take four steps to honour by hand and therefore get skipped.

## Where it goes

```
work/<ticket-or-slug>/YYYY-MM-DD-<artifact-slug>.md
```

`work/` is keyed by **ticket or topic, never by repo**. Reach it whichever way fits the session:

- **Inside a checkout with the symlink wired up** (see `setup-here`): `.atlas/<ticket>/…` — identical in every repo. Prefer this; committed code comments use these paths.
- **Anywhere else:** the absolute path (`$ATLAS_VAULT_ROOT/Atlas`). `Atlas` is in `permissions.additionalDirectories`, so no prompt.

## 0. Verify the vault is reachable

Check `$ATLAS_VAULT_ROOT` is set and non-empty before anything else — unset, it silently turns `$ATLAS_VAULT_ROOT/Atlas` into `/Atlas`, a path that doesn't exist. If it's empty, stop and tell the user to set it (see the `atlas` plugin's `setup-here` skill) rather than writing anywhere.

## 1. Work out the destination

- **Ticket** — from `$ARGUMENTS` if given, else from the current branch (`git branch --show-current`; branches carry the lowercase Jira key), else from the conversation. Lowercase in the path, uppercase in frontmatter. No ticket → a short kebab-case slug describing the task.
- **Artifact slug** — what the thing *is*: `spec`, `plan`, `pr-description`, `review`, `clarifications`, `stack-review`. Not a restatement of the ticket.
- **Repos** — `git remote get-url origin` for the current checkout. If the work spans repos, list them all; that list is the whole reason `work/` isn't partitioned by repo.

## 2. Check for an existing version — the part that matters

Before writing, look for prior artifacts with the same slug in that directory:

```sh
ls ".atlas/<ticket>/" | grep -- "-<slug>"      # or the absolute path
```

Then decide, and **say which you chose and why**:

| Situation | Action |
|---|---|
| Nothing there | New file, no `supersedes:` |
| Exists, and your change **preserves meaning** (typo, formatting, broken link) | Edit in place. Do not create a version. |
| Exists, and your change **alters meaning** | New file (below) |
| Exists, and yours is a **parallel sibling** produced in the same run (per-model, per-repo, per-lane) | A **variant**, not a revision — see §4 |

**New revision** = all four of these, or the chain is broken:

1. New filename: today's date, same slug, next `-vN` (`2026-08-18-spec-v3.md`). The first revision of an unsuffixed file becomes `-v2`.
2. `supersedes: "[[<previous basename without .md>]]"` in the new file.
3. `status: superseded` in the **previous** file — the only edit you may make to an immutable file besides typos.
4. Never write `superseded_by:`. Obsidian backlinks give the reverse direction free.

Files are immutable because the date in the filename must stay true. Editing a three-day-old file makes its own name a lie and destroys the answer to "what changed yesterday".

## 3. Frontmatter

```yaml
---
created: 2026-08-18T14:32
type: plan            # plan|spec|review|pr-description|research|meeting|transcript|idea|scratch|decision|guide
repos: [my-service]      # every repo the work touches
ticket: PROJ-1234    # uppercase here, lowercase in the path
tags: [ad-engine]
status: active        # draft|active|superseded|done
author: claude-code
supersedes: "[[2026-08-15-spec-v2]]"   # only when revising
---
```

- **`author:`, never `source:`.** `source:` is reserved for a captured document's origin URL — `document-intake` already uses it that way.
- **Never reference code by relative path.** `../../apps/…` resolves against the vault, not the checkout, and is already broken in 26 legacy artifacts. Use `code_refs: [<repo>:<path>#<symbol>]` and GitHub permalinks with a commit SHA.
- Don't hand-write `updated` — the `frontmatter-modified-date` plugin maintains it.
- Omit a field rather than guess it. An absent `type:` is better than a wrong one.

## 4. Variants and derived artifacts

A fan-out — N reviewers, N models, one pane per repo — produces **siblings, not versions**:

- Put the set in a dated directory: `work/<ticket>/2026-08-18-<slug>/`
- One file per sibling, named by a **descriptive token**: `opus.md`, `sonnet.md`, `ux-platform.md`. **Never `-1`, `-2`** — those read as versions, and that single ambiguity is what made the pre-migration store unreadable.
- Each carries `variant: <token>`.
- A synthesis of the set carries `derives_from: ["[[opus]]", "[[sonnet]]"]` — a different edge from `supersedes:`. One means "replaces", the other means "built from".

## 5. Not an artifact?

- Raw capture with no home yet — a transcript, a dump, a half-formed idea → `Atlas/inbox/`, same naming, sort later.
- Distilled cross-cutting knowledge → `Atlas/knowledge/`, which has its own two-zone page format. Promotion there is always explicitly invoked; don't do it as a side effect.
- Session transcripts from the SpecStory extension → not yours to write. They live in `../specstory/`.

## 6. Report

State the path written, the type, whether it superseded something (and which file), and anything you left unset. If you edited in place rather than creating a revision, say so and why — that's the judgement call the user most needs to see.
