# vforge

A Claude Code plugin marketplace with two plugins: `v`, a personal toolkit for
writing, auditing, and git workflows, and `atlas`, tooling for a personal
knowledge-base vault.

## Install

```
/plugin marketplace add vforge/claude-marketplace
/plugin install v@vforge
/plugin install atlas@vforge
```

Then restart Claude Code, or run `/plugin` to confirm it is enabled.

## `v` — writing, auditing, and git workflows

### `/v:enthropy` — measure redundancy

Finds repeated content in a file, directory, or project.

- **Mode 1** (default) — textual duplicates via gzip compression ratios, normalized compression distance, and shingle matching.
- **Mode 2** (`--semantic`) — passages that convey the same fact in different words, judged by a Haiku subagent over candidate pairs pre-filtered by vocabulary overlap.
- `--all` runs both.

```
/v:enthropy docs/
/v:enthropy --semantic src/prompts
/v:enthropy --all .
```

Requires `python3` (standard library only).

### `/v:unslop` — audit generated text

Fourteen failure classes that survive review in AI-drafted documents: metaphor standing in for a mechanism, rhetorical totalisers, circular flourishes, dramatic exemplification, compressed derivation, negation framing, scope overreach, consequences drawn from imperceptible effects, stale claims contradicting later rulings, and unmarked provenance.

The governing insight: **a sentence that reads as settled stops being checked.** Colourful phrasing is a correctness problem, because it conceals claims the document's own rules do not support. The report ends with the factual errors the phrasing was hiding — that list is the point of the exercise.

Writes a timestamped variant beside the original, never overwriting, and preserves checkbox state so review progress survives the edit.

```
/v:unslop docs/architecture.md
```

### `/v:unslop-prose` — cut AI tells from any writing

Edits text to remove AI-writing patterns — puffery, hedging, em dashes, inline-header lists, filler phrases, hyphenated-pair overuse, persuasive authority tropes, and more — and adds back a human voice; optionally matches voice against a writing sample. Narrower than `unslop`: this is a style pass, not an audit for the factual errors that phrasing conceals.

### `/v:spec` — reference documents in point form

One fact per line, max ~15 words, no paragraphs anywhere. Consequences get their own `→` line; unresolved conflicts get `⚠` and stay unresolved rather than being smoothed over in prose. Ships a banned list (AI vocabulary, hedges, intensifiers, throat-clearing) and six tests to run before output, including the deletion test and the retrieval test.

```
/v:spec the retry and backoff behaviour of the ingest worker
```

### `/v:idea` — argue both sides

Research what already exists, then 8–12 independent arguments for and 8–12 against, hidden assumptions challenged and inverted, 3–5 genuine alternatives to the same underlying goal, and first/second/third-order effects traced forward and backward.

It ends in a decision map keyed to your priorities plus the open questions only you can answer, rather than a recommendation.

```
/v:idea move session state out of Postgres into Redis
```

### `/v:flatten-and-rebase` — squash and rebase a branch

Flattens the current branch to N commits (default 1) and rebases onto the latest base branch, with a backup branch created first and a confirmation step before any force-push.

```
/v:flatten-and-rebase
/v:flatten-and-rebase 3 develop
```

### `/v:borrow-skill` — adopt a third-party skill

Copies a skill from another repo or plugin pack into `~/.claude/skills/` verbatim, plus a one-line provenance README recording where it came from.

### `/v:sidequest` — pause/resume for unrelated work

Task-stack push: write a handoff for the main task, isolate the tangent in a worktree if it's code, do the tangent, then resume or abandon back to the main task. Requires `atlas@vforge` installed alongside `v@vforge` — the handoff is written via `atlas`'s `note` skill.

### `/v:archive` — retire a file without deleting it

Moves a file into the project's archive directory (`.archive`, `.archived`, or `zz_archive` — whichever exists), preserving its path relative to the project root. Errors out, naming what to create, if none of the three exist — never creates one itself.

```
/v:archive docs/old-plan.md
```

## `atlas` — Atlas knowledge-base tooling

Personal-infrastructure skills for a knowledge vault (`Atlas`) and its `.atlas`/`.specstory` symlink convention. Set `ATLAS_VAULT_ROOT` to the parent directory containing `Atlas/` and `specstory/`. These are tied to that vault's location and layout, not general-purpose.

### `/atlas:note` — save an artifact to Atlas

Writes a plan, spec, review, or research note into the vault with correct naming, frontmatter, and revision chain — finds the prior version, bumps `-vN`, sets `supersedes`/`status` — the bookkeeping that's easy to skip by hand.

### `/atlas:recall` — search Atlas for prior work

Searches the vault in a deliberate order (distilled knowledge, then ticket artifacts, then curated notes, then inbox/log), filtering out superseded revisions.

### `/atlas:setup-here` — wire a checkout's .atlas/.specstory symlinks

Points a checkout's `.atlas` and `.specstory` at the shared vault and specstory store, refusing to clobber a real (non-symlink) directory in the way.

## Origins

`unslop`, `spec`, and `idea` were extracted from a large worldbuilding vault, where they were tuned against real generated documents over months. The failure classes in `unslop` are all things that actually shipped and survived multiple review passes. Domain-specific examples have been replaced with neutral ones; the structure is unchanged.

The rest were ported from a personal global `~/.claude/skills/` directory — some work-connected variants of these already live in a separate employer-internal marketplace; what's here is the private-use set. Skills borrowed verbatim from third parties (Cursor's `pstack` pack, other public skill repos) were left out — they carry their own provenance notes and aren't this repo's to redistribute. `unslop-prose` is the one exception: it's a genuine derivative (Cursor's `pstack unslop` plus patterns from `blader/humanizer` and Wikipedia's "Signs of AI writing"), attributed in its own Provenance section rather than left out.

## Layout

```
.claude-plugin/marketplace.json
plugins/v/
├── .claude-plugin/plugin.json
└── skills/
    ├── enthropy/{SKILL.md,measure.py,semantic_candidates.py}
    ├── unslop/SKILL.md
    ├── unslop-prose/SKILL.md
    ├── spec/SKILL.md
    ├── idea/SKILL.md
    ├── flatten-and-rebase/SKILL.md
    ├── borrow-skill/SKILL.md
    ├── sidequest/SKILL.md
    └── archive/SKILL.md
plugins/atlas/
├── .claude-plugin/plugin.json
└── skills/
    ├── note/SKILL.md
    ├── recall/SKILL.md
    └── setup-here/{SKILL.md,setup-here.sh}
```

## License

MIT
