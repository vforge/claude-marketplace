#!/usr/bin/env python3
"""
enthropy mode 1: textual redundancy analysis.

Scoring layers:
  1. Per-file gzip ratio  — intra-file repetition (1 - compressed/raw)
  2. Cross-file NCD       — Normalized Compression Distance between file pairs
  3. Shingle dedup        — exact duplicate passages (k-gram word matching)

Usage:
  measure.py [path] [--shingle-size N] [--min-passage M]
             [--top-pairs K] [--top-passages K] [--max-pairs-files N]

  path defaults to current working directory.
"""

import argparse
import gzip
import hashlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", "node_modules", ".obsidian", "zz_archive", "__pycache__",
    ".venv", "venv", "dist", "build", ".next", ".cache",
}
EXCLUDED_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip", ".gz", ".tar",
    ".lock", ".map", ".woff", ".woff2", ".ttf", ".ico", ".mp3", ".mp4",
    ".mov", ".webp", ".db", ".sqlite",
}
TEXT_EXTS = {
    ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".json", ".yaml", ".yml", ".toml", ".html", ".css", ".sh", ".rb",
    ".java", ".c", ".cpp", ".h", ".hpp", ".swift", ".kt", ".lua",
}


def is_text_file(p: Path) -> bool:
    suf = p.suffix.lower()
    if suf in EXCLUDED_EXTS:
        return False
    if suf in TEXT_EXTS:
        return True
    try:
        with open(p, "rb") as f:
            chunk = f.read(2048)
        if b"\x00" in chunk:
            return False
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files = []
    for root, dirs, names in os.walk(target):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for name in names:
            if name.startswith("."):
                continue
            p = Path(root) / name
            if is_text_file(p):
                files.append(p)
    return sorted(files)


def tokenize_with_lines(text: str):
    """Return (tokens, line_per_token). Lowercased word-tokens for matching."""
    toks: list[str] = []
    lines: list[int] = []
    for ln, line in enumerate(text.split("\n"), 1):
        for word in re.findall(r"\w+", line.lower()):
            toks.append(word)
            lines.append(ln)
    return toks, lines


def gz(data: bytes) -> int:
    return len(gzip.compress(data, compresslevel=6))


def file_redundancy(text: str) -> float:
    raw = text.encode("utf-8", errors="ignore")
    if len(raw) < 200:
        return 0.0
    return 1.0 - (gz(raw) / len(raw))


def ncd(a: bytes, b: bytes) -> float:
    cab = gz(a + b)
    ca = gz(a)
    cb = gz(b)
    denom = max(ca, cb)
    if denom == 0:
        return 1.0
    return (cab - min(ca, cb)) / denom


def find_duplicate_passages(file_data, k: int, min_passage: int):
    """
    file_data: list of (path, text, tokens, line_per_token)
    Returns: dict of normalized_passage_text -> [(path, line_start, line_end, tokens), ...]
    """
    shingle_locs = defaultdict(list)
    for fidx, (_, _, toks, _) in enumerate(file_data):
        if len(toks) < k:
            continue
        for i in range(len(toks) - k + 1):
            shingle = " ".join(toks[i : i + k])
            h = hashlib.blake2b(shingle.encode(), digest_size=8).digest()
            shingle_locs[h].append((fidx, i))

    dup_positions = defaultdict(set)
    for locs in shingle_locs.values():
        if len(locs) >= 2:
            for fidx, pos in locs:
                for o in range(k):
                    dup_positions[fidx].add(pos + o)

    text_to_locations = defaultdict(list)
    for fidx, positions in dup_positions.items():
        path, _, toks, lines = file_data[fidx]
        sorted_pos = sorted(positions)
        if not sorted_pos:
            continue
        runs = []
        start = prev = sorted_pos[0]
        for p in sorted_pos[1:]:
            if p == prev + 1:
                prev = p
            else:
                runs.append((start, prev))
                start = prev = p
        runs.append((start, prev))
        for s, e in runs:
            length = e - s + 1
            if length < min_passage:
                continue
            passage = " ".join(toks[s : e + 1])
            text_to_locations[passage].append(
                (path, lines[s], lines[e], length)
            )

    return {p: locs for p, locs in text_to_locations.items() if len(locs) >= 2}


def fmt_path(p: Path, base: Path) -> str:
    try:
        return str(p.relative_to(base))
    except ValueError:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--shingle-size", type=int, default=6)
    ap.add_argument("--min-passage", type=int, default=10,
                    help="min token length of a duplicated passage to report")
    ap.add_argument("--top-pairs", type=int, default=10)
    ap.add_argument("--top-passages", type=int, default=20)
    ap.add_argument("--max-pairs-files", type=int, default=80,
                    help="skip cross-file NCD if more files than this (O(n²))")
    args = ap.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"path not found: {target}", file=sys.stderr)
        return 1

    base = target if target.is_dir() else target.parent
    files = collect_files(target)
    if not files:
        print("No text files found.")
        return 0

    print(f"# enthropy report — {target}\n")
    print(f"Files analyzed: **{len(files)}**  ·  shingle k={args.shingle_size}  ·  min passage={args.min_passage} tokens\n")

    # Layer 1: per-file redundancy
    rows = []
    file_texts: dict[Path, str] = {}
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        file_texts[f] = text
        rows.append((file_redundancy(text), f, len(text)))
    rows.sort(reverse=True)

    print("## 1. Per-file redundancy (gzip ratio)\n")
    print("Higher = more internal repetition. Pure prose typically ~0.50–0.65; >0.75 is suspicious; >0.85 likely contains lots of literal repeats.\n")
    print("| Redundancy | Size (chars) | File |")
    print("|---|---|---|")
    for r, f, sz in rows[:20]:
        print(f"| {r:.2f} | {sz:>7,} | `{fmt_path(f, base)}` |")
    if len(rows) > 20:
        print(f"\n_({len(rows) - 20} more files omitted)_\n")
    else:
        print()

    # Layer 2: cross-file NCD
    if len(files) >= 2:
        if len(files) <= args.max_pairs_files:
            print("## 2. Most similar file pairs (NCD)\n")
            print("0.0 = identical, 1.0 = unrelated. Pairs <0.5 likely share substantial content.\n")
            byts = {f: file_texts[f].encode("utf-8", errors="ignore") for f in files}
            pairs = []
            flist = list(byts.keys())
            for i in range(len(flist)):
                a = byts[flist[i]]
                if not a:
                    continue
                for j in range(i + 1, len(flist)):
                    b = byts[flist[j]]
                    if not b:
                        continue
                    pairs.append((ncd(a, b), flist[i], flist[j]))
            pairs.sort()
            print("| NCD | File A | File B |")
            print("|---|---|---|")
            for d, a, b in pairs[: args.top_pairs]:
                print(f"| {d:.2f} | `{fmt_path(a, base)}` | `{fmt_path(b, base)}` |")
            print()
        else:
            print(f"## 2. Most similar file pairs (NCD)\n\n_Skipped: {len(files)} files exceeds --max-pairs-files={args.max_pairs_files} (O(n²) cost). Re-run on a narrower path if you want pair scores._\n")

    # Layer 3: shingle dupes
    file_data = []
    for f in files:
        text = file_texts.get(f, "")
        toks, lines = tokenize_with_lines(text)
        file_data.append((f, text, toks, lines))

    duplicates = find_duplicate_passages(
        file_data, k=args.shingle_size, min_passage=args.min_passage
    )

    print("## 3. Duplicate passages\n")
    if not duplicates:
        print(f"_No passages of ≥{args.min_passage} tokens are repeated._\n")
    else:
        ranked = sorted(
            duplicates.items(),
            key=lambda kv: kv[1][0][3] * len(kv[1]),  # tokens × occurrences
            reverse=True,
        )
        for i, (passage, locs) in enumerate(ranked[: args.top_passages], 1):
            length = locs[0][3]
            occ = len(locs)
            preview = passage if len(passage) <= 240 else passage[:240] + "…"
            print(f"### #{i}  ·  {length} tokens  ·  {occ}× occurrences\n")
            print(f"> {preview}\n")
            print("**Locations:**")
            for path, l1, l2, _ in locs:
                rng = f"L{l1}" if l1 == l2 else f"L{l1}-{l2}"
                print(f"- `{fmt_path(path, base)}:{rng}`")
            print()
        if len(ranked) > args.top_passages:
            print(f"_({len(ranked) - args.top_passages} more duplicate passages omitted)_\n")

    # Summary
    total_chars = sum(sz for _, _, sz in rows)
    avg_red = sum(r for r, _, _ in rows) / len(rows) if rows else 0.0
    print("## Summary\n")
    print(f"- Total: **{total_chars:,}** chars across **{len(files)}** files")
    print(f"- Avg per-file redundancy: **{avg_red:.2f}**")
    print(f"- Distinct duplicate passages (≥{args.min_passage} tokens): **{len(duplicates)}**")
    if duplicates:
        total_dup_tokens = sum(locs[0][3] * len(locs) for locs in duplicates.values())
        print(f"- Total tokens consumed by repeats: **{total_dup_tokens:,}**")
    return 0


if __name__ == "__main__":
    sys.exit(main())
