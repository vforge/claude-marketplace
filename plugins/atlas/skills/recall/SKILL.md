---
name: recall
description: Search the Atlas knowledge base for prior work — what was decided on a ticket, what a system does, notes from a meeting, who someone is, what happened recently. Searches in a deliberate order (distilled knowledge first, then ticket artifacts, then curated notes) and filters out superseded revisions. Use before starting work on a ticket that may have history, when asked "what do we know about X", "did we decide", "have I looked at this before", or when context from past sessions would help.
argument-hint: "[what you're looking for]"
---

# recall

Find prior work in **Atlas** (`$ATLAS_VAULT_ROOT/Atlas`) instead of grepping blindly or re-deriving what's already written down.

The vault has ~950 notes across layers with different reliability. Search order matters more than search cleverness.

## Search order

**1. `knowledge/` — distilled, start here.** Compiled pages carrying current best understanding above a `---` divider and append-only provenance below it. If the answer is here it's already synthesised and cites its sources. (Empty until Phase 4 of the unification plan; skip if so.)

**2. `work/<ticket-or-slug>/` — ticket artifacts.** ~96 directories keyed by ticket or topic, **not by repo** — so `MON-712` is one directory even though it spans four repos. Two rules for reading it:

- **Filter out superseded revisions.** `status: superseded` in frontmatter, or a lower `-vN` than a sibling. The newest date prefix with the highest `-vN` is current.
- **Distinguish the three axes** before treating files as a sequence:
  - `supersedes:` → a revision chain, read the last one
  - `variant:` → parallel siblings from one run, none authoritative; read several or the synthesis
  - `derives_from:` → a synthesis of siblings, usually the best single read

**3. Curated notes** — `Meeting Notes/YYYY/`, `Projects/`, `Technical Documentation/`, `Contacts/`, `Documents/`. Human-written, title-case names, generally the most reliable prose in the vault.

**4. `inbox/` and `log/`** — unsorted capture and the append-only activity log. Use for "what was I doing recently", not for authoritative answers.

## How to search

Frontmatter is the query surface:

```sh
A="$ATLAS_VAULT_ROOT/Atlas"
grep -rl "ticket: PROJ-1234" "$A/work" "$A/knowledge"     # everything on a ticket
grep -rl "repos:.*my-service" "$A/work"                        # everything touching a repo
grep -rln "type: review" "$A/work"                          # by artifact type
ls "$A/work/proj-1234/"                                     # the whole history of one ticket
```

- From inside a checkout with the symlink wired up, `.atlas/` is the same directory — `ls .atlas/proj-1234/` works and is shorter.
- Filenames are informative: `YYYY-MM-DD-<slug>[-vN].md`. Date-sorted listing is a timeline.
- **Legacy artifacts carry `provenance: imported-2026-08-18`.** Their `created:` came from mtime; where `date_precision: approximate` is set, the date is a bulk-copy artifact and means nothing. 306 have no `type:` — deliberately unset rather than guessed, so don't rely on `type:` for completeness on old material.
- Some legacy names are inconsistent (spaces, uppercase, six competing version schemes). Grep content, don't assume naming.

## What not to search

- **`../specstory/`** — SpecStory session transcripts, ~69k files. Raw logs full of dead ends and superseded reasoning: legitimate for "when did I work on this", never citable as documentation. `debug/` alone is 66k JSON files and will drown any broad grep.
- The **Dev Hub Vault** (`../Dev Hub Vault/`) is a separate vault for dev-generic content, managed by another agent.

## Report

Answer the question, then cite the files you used as paths. Say explicitly when you found **nothing** — that's a useful result and stops the user assuming coverage that doesn't exist. If what you found is superseded or its date is unreliable, say that rather than presenting it flatly.
