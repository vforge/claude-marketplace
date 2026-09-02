---
name: enthropy
description: Measure redundancy in a file, directory, or project. Mode 1 (default) finds textual duplicates via gzip ratios, NCD, and shingle matching. Mode 2 (--semantic) finds passages that convey the same fact in different words, using a Haiku subagent to judge candidate pairs pre-filtered by vocabulary overlap. Use when the user wants to find repeated content, near-duplicate files, "what's just being said over and over", or rephrased-but-redundant passages.
---

# /enthropy — measure redundancy

## Argument parsing

Inspect the user's args for these flags:
- `--semantic` → run mode 2 only (skip mode 1)
- `--all` → run both mode 1 and mode 2
- everything else (or no flags) → run mode 1 only

The remaining non-flag token is the path; default to `.` if absent.

## Mode 1 — textual redundancy

Run the analyzer:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/enthropy/measure.py" <path>
```

Where `<path>` is:
- A single file → intra-file repetition + passages repeated within it
- A directory → per-file scores + cross-file similarity + cross-file duplicate passages
- Omitted or `.` → current working directory

The script ignores `.git`, `node_modules`, `.obsidian`, `zz_archive`, and other non-content directories. It only inspects text files.

### What the report contains

1. **Per-file gzip redundancy** — `1 - compressed/raw`. Pure prose ~0.50–0.65; >0.75 suspicious; >0.85 likely contains literal repeats.
2. **Most similar file pairs (NCD)** — Normalized Compression Distance. Near-0 = near-duplicate files. Skipped for directories with >80 files (O(n²) cost).
3. **Duplicate passages** — k-gram word shingling. Each entry shows the repeated text plus *every* location it appears at (with line numbers), ranked by `tokens × occurrences`.

### After running

- Read the whole report; do **not** edit anything unless the user asks.
- For each significant duplicate passage, briefly classify it:
  - **(a) deliberate** — quotes, citations, intentional refrains, structured templates
  - **(b) drift** — same fact rephrased across versions, near-dupes from rewrites
  - **(c) boilerplate / waste** — frontmatter, headers, empty scaffolding repeated everywhere
  - **(d) actual redundancy** — same point made multiple times in the same conceptual section, nothing meaningful added by the repeat
- Categories (b) and (d) are what the user cares about. Highlight those first; mention (a)/(c) only briefly.
- If many results look like noise (boilerplate, frontmatter), suggest re-running with `--min-passage 20` or higher. If results are too sparse, suggest `--shingle-size 4 --min-passage 6`.

### Tuning flags

| Flag | Default | Purpose |
|---|---|---|
| `--shingle-size N` | 6 | k-gram word size for fingerprinting. Smaller → catches shorter repeats but more noise. |
| `--min-passage M` | 10 | Min token length of a duplicate passage to report. |
| `--top-pairs K` | 10 | How many file pairs to show in section 2. |
| `--top-passages K` | 20 | How many duplicate passages to show in section 3. |
| `--max-pairs-files N` | 80 | Skip cross-file NCD if a directory has more files than this. |

### When to suggest re-runs

- **Too much frontmatter noise** → re-run with `--min-passage 25` to filter out short YAML blocks
- **Suspect a specific file pair** → re-run on a path containing only those two files
- **Want to see medium-sized dupes** → `--shingle-size 4 --min-passage 8`

## Mode 2 — semantic duplication

Two stages: a deterministic Python filter produces candidate pairs, then a Haiku subagent judges each pair semantically.

### Stage A — extract candidates

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/enthropy/semantic_candidates.py" <path> --output /tmp/enthropy-candidates.json
```

This splits all text files into paragraphs (30–500 tokens each), computes word-set Jaccard on content words (Polish + English stop-list applied, document-frequency capped), and writes the top-K pairs above a Jaccard threshold to JSON.

The JSON has shape:
```json
{
  "base": "...", "files": N, "chunks": N,
  "settings": {...},
  "candidates": [
    {"id": 1, "jaccard": 0.85, "shared_words": 42,
     "a": {"file": "...", "line_start": N, "line_end": N, "tokens": N, "text": "..."},
     "b": {"file": "...", "line_start": N, "line_end": N, "tokens": N, "text": "..."}}
  ]
}
```

If `candidates` is empty, report that no candidate pairs cleared the Jaccard threshold and suggest re-running with `--min-jaccard 0.3` (or lower). **Skip stage B in that case.**

### Stage B — dispatch to Haiku judge

If candidates exist, spawn one Agent call:
- `subagent_type`: `general-purpose`
- `model`: `haiku`
- `description`: `Semantic dup judge for /enthropy`
- `prompt`: the verbatim rubric below, with the candidates JSON path interpolated.

**Rubric prompt to use (copy this body, adjust path):**

> You are reviewing pairs of text passages to identify SEMANTIC DUPLICATION — places where two passages convey the same fact or proposition, even if phrased differently.
>
> Read the candidate pairs from `/tmp/enthropy-candidates.json` (the `candidates` array). For each pair, classify as:
>
> - **REDUNDANT** — Both passages convey the same fact(s). Neither adds meaningful information the other lacks. Cutting one would lose nothing.
> - **OVERLAPPING** — They share a core point but each adds something distinct. Cutting one would lose some information.
> - **DISTINCT** — Despite vocabulary overlap, they make different points. Both should stay.
>
> Be STRICT about REDUNDANT — only call it that if cutting one passage would genuinely lose nothing. Adjacent paragraphs that elaborate on the same topic are usually OVERLAPPING, not REDUNDANT. Lists of structurally identical items (e.g. open-question checklists with different topics) are DISTINCT despite vocabulary overlap.
>
> Return a single JSON array on stdout — no prose, no markdown, no preamble. Each item must be:
> ```json
> {"id": <int>, "verdict": "REDUNDANT|OVERLAPPING|DISTINCT",
>  "shared": "<one short clause naming the shared point>",
>  "a_unique": "<one short clause or null>",
>  "b_unique": "<one short clause or null>"}
> ```
>
> Cover every candidate id. Keep clauses under 15 words each.

The subagent will return a JSON array. Parse it.

### Stage C — compile the report

Render a markdown section like this:

```
## Semantic redundancy (Haiku judge)

Analyzed N candidate pairs (Jaccard ≥ X). M REDUNDANT · M OVERLAPPING · M DISTINCT.

### REDUNDANT (M pairs)

#### #R1 — <shared clause>
- `<file_a>:L<a1>-<a2>` — <first 80 chars of A text>…
- `<file_b>:L<b1>-<b2>` — <first 80 chars of B text>…

[repeat for each REDUNDANT pair, sorted by candidate Jaccard descending]

### OVERLAPPING (M pairs)

#### #O1 — <shared clause>
- `<file_a>:L<a1>-<a2>` — adds: <a_unique>
- `<file_b>:L<b1>-<b2>` — adds: <b_unique>

[repeat for OVERLAPPING]

### DISTINCT — filtered as false positives (M)

_Suppressed; use --show-distinct to inspect._
```

REDUNDANT and OVERLAPPING are the actionable buckets. DISTINCT means the Jaccard pre-filter caught vocabulary overlap but the judge ruled the passages actually make different points — collapse that section to a count by default.

If the user invoked with `--all`, prepend the mode 1 report (run mode 1 first, then mode 2 below it).

### Tuning flags (for stage A)

| Flag | Default | Purpose |
|---|---|---|
| `--top-k K` | 30 | Max candidate pairs to emit. |
| `--min-jaccard X` | 0.4 | Lower → more candidates (more false positives, more Haiku work). |
| `--min-tokens M` | 30 | Drop chunks shorter than this. |
| `--max-tokens N` | 500 | Sub-split paragraphs longer than this. |

### When to suggest re-runs

- **Zero candidates** → re-run stage A with `--min-jaccard 0.3` or `--min-jaccard 0.25`
- **Too many candidates, mostly DISTINCT** → re-run with `--min-jaccard 0.55` to tighten the filter
- **Many short fragments missed** → re-run with `--min-tokens 15`
