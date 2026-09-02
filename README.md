# vforge

A Claude Code plugin marketplace with one plugin, `v`: four skills for auditing generated text, writing reference docs, and thinking through decisions.

## Install

```
/plugin marketplace add vforge/claude-marketplace
/plugin install v@vforge
```

Then restart Claude Code, or run `/plugin` to confirm it is enabled.

## Skills

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

## Origins

`unslop`, `spec`, and `idea` were extracted from a large worldbuilding vault, where they were tuned against real generated documents over months. The failure classes in `unslop` are all things that actually shipped and survived multiple review passes. Domain-specific examples have been replaced with neutral ones; the structure is unchanged.

## Layout

```
.claude-plugin/marketplace.json
plugins/v/
├── .claude-plugin/plugin.json
└── skills/
    ├── enthropy/{SKILL.md,measure.py,semantic_candidates.py}
    ├── unslop/SKILL.md
    ├── spec/SKILL.md
    └── idea/SKILL.md
```

## License

MIT
