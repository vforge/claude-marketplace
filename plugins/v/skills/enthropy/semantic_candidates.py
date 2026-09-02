#!/usr/bin/env python3
"""
enthropy mode 2 — stage A: extract candidate pairs for semantic-dup judging.

Splits files into paragraphs, computes pairwise word-set Jaccard, emits top-K
candidate pairs as JSON for a downstream LLM judge.

Usage:
  semantic_candidates.py [path] [--top-k K] [--min-jaccard X]
                                [--min-tokens M] [--max-tokens N]
                                [--output FILE]

Defaults: top-k=30, min-jaccard=0.4, min-tokens=30, max-tokens=500.
"""

import argparse
import json
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

# Minimal stop-word list. Polish + English content-mixed; we filter aggressively
# common short words and rely on document-frequency capping (below) for the rest.
STOPWORDS = {
    # English
    "the", "a", "an", "and", "or", "but", "if", "of", "in", "on", "at", "to",
    "for", "with", "by", "from", "as", "is", "are", "was", "were", "be", "been",
    "being", "has", "have", "had", "do", "does", "did", "will", "would", "can",
    "could", "should", "may", "might", "must", "shall", "this", "that", "these",
    "those", "it", "its", "they", "them", "their", "there", "here", "what",
    "which", "who", "whom", "whose", "when", "where", "why", "how", "not", "no",
    "yes", "all", "any", "some", "each", "every", "other", "another", "such",
    "than", "then", "so", "too", "very", "just", "only", "also", "more", "most",
    "less", "least", "many", "much", "few", "one", "two", "three", "into", "out",
    "up", "down", "over", "under", "above", "below", "before", "after", "during",
    "while", "until", "between", "among", "through", "about", "around", "again",
    "still", "ever", "never", "always", "often", "sometimes", "now", "yet",
    # Polish
    "i", "oraz", "lub", "ale", "jeśli", "z", "ze", "w", "we", "na", "do", "od",
    "po", "przy", "dla", "bez", "przed", "za", "pod", "nad", "między", "to",
    "ten", "ta", "te", "tych", "tym", "się", "jest", "są", "był", "była", "było",
    "były", "być", "ma", "mają", "miał", "miała", "miało", "może", "można",
    "nie", "tak", "lub", "albo", "też", "także", "również", "tylko", "już",
    "jeszcze", "bardzo", "więcej", "mniej", "wszystkie", "każdy", "który",
    "która", "które", "co", "kto", "gdzie", "kiedy", "jak", "dlaczego",
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


WORD_RE = re.compile(r"[\w\u0080-\uffff]+", re.UNICODE)
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ])")


def content_words(text: str) -> set[str]:
    out = set()
    for w in WORD_RE.findall(text.lower()):
        if len(w) <= 2:
            continue
        if w in STOPWORDS:
            continue
        if w.isdigit():
            continue
        out.add(w)
    return out


def count_tokens(text: str) -> int:
    return sum(1 for _ in WORD_RE.finditer(text))


def split_paragraphs(text: str) -> list[tuple[int, int, str]]:
    """Yield (line_start, line_end, paragraph_text). Splits on blank lines."""
    chunks = []
    current_lines: list[str] = []
    current_start = 1
    line_idx = 0
    for line_idx, line in enumerate(text.split("\n"), 1):
        if line.strip() == "":
            if current_lines:
                joined = "\n".join(current_lines).strip()
                if joined:
                    chunks.append((current_start, line_idx - 1, joined))
                current_lines = []
            current_start = line_idx + 1
        else:
            if not current_lines:
                current_start = line_idx
            current_lines.append(line)
    if current_lines:
        joined = "\n".join(current_lines).strip()
        if joined:
            chunks.append((current_start, line_idx, joined))
    return chunks


def maybe_subsplit(chunk: tuple[int, int, str], max_tokens: int) -> list[tuple[int, int, str]]:
    """If a paragraph exceeds max_tokens, group its sentences into ~max/2-token blocks."""
    line_start, line_end, text = chunk
    if count_tokens(text) <= max_tokens:
        return [chunk]
    sentences = SENT_RE.split(text)
    if len(sentences) <= 1:
        return [chunk]
    target = max_tokens // 2
    out = []
    cur: list[str] = []
    cur_tokens = 0
    for s in sentences:
        st = count_tokens(s)
        if cur and cur_tokens + st > target:
            out.append((line_start, line_end, " ".join(cur).strip()))
            cur = []
            cur_tokens = 0
        cur.append(s)
        cur_tokens += st
    if cur:
        out.append((line_start, line_end, " ".join(cur).strip()))
    return out


def build_chunks(files: list[Path], min_tokens: int, max_tokens: int):
    """Returns list of dicts: {file, line_start, line_end, text, words(set), tokens}."""
    chunks = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for raw_chunk in split_paragraphs(text):
            for sub in maybe_subsplit(raw_chunk, max_tokens):
                ls, le, body = sub
                tk = count_tokens(body)
                if tk < min_tokens:
                    continue
                words = content_words(body)
                if len(words) < 5:
                    continue
                chunks.append({
                    "file": str(f),
                    "line_start": ls,
                    "line_end": le,
                    "text": body,
                    "words": words,
                    "tokens": tk,
                })
    return chunks


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


def find_candidates(chunks: list[dict], min_jaccard: float, top_k: int):
    """Inverted index → candidate pairs sharing ≥3 content words → exact Jaccard."""
    word_to_chunks: dict[str, list[int]] = defaultdict(list)
    for i, c in enumerate(chunks):
        for w in c["words"]:
            word_to_chunks[w].append(i)

    pair_overlap: dict[tuple[int, int], int] = defaultdict(int)
    for w, idxs in word_to_chunks.items():
        if len(idxs) < 2 or len(idxs) > 200:
            # skip ultra-common words (appear in >200 chunks) to keep cost bounded
            continue
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                a, b = idxs[i], idxs[j]
                pair_overlap[(a, b)] += 1

    scored = []
    for (i, j), shared in pair_overlap.items():
        if shared < 3:
            continue
        j_score = jaccard(chunks[i]["words"], chunks[j]["words"])
        if j_score >= min_jaccard:
            scored.append((j_score, i, j))
    scored.sort(reverse=True)
    return scored[:top_k]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--top-k", type=int, default=30)
    ap.add_argument("--min-jaccard", type=float, default=0.4)
    ap.add_argument("--min-tokens", type=int, default=30)
    ap.add_argument("--max-tokens", type=int, default=500)
    ap.add_argument("--output", default=None, help="write JSON to file (default: stdout)")
    args = ap.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"path not found: {target}", file=sys.stderr)
        return 1

    base = target if target.is_dir() else target.parent
    files = collect_files(target)
    if not files:
        result = {"base": str(base), "files": 0, "chunks": 0, "candidates": []}
    else:
        chunks = build_chunks(files, args.min_tokens, args.max_tokens)
        candidates_raw = find_candidates(chunks, args.min_jaccard, args.top_k)
        candidates = []
        for cid, (score, i, j) in enumerate(candidates_raw, 1):
            ci, cj = chunks[i], chunks[j]
            candidates.append({
                "id": cid,
                "jaccard": round(score, 3),
                "shared_words": len(ci["words"] & cj["words"]),
                "a": {
                    "file": str(Path(ci["file"]).relative_to(base)) if Path(ci["file"]).is_relative_to(base) else ci["file"],
                    "line_start": ci["line_start"],
                    "line_end": ci["line_end"],
                    "tokens": ci["tokens"],
                    "text": ci["text"],
                },
                "b": {
                    "file": str(Path(cj["file"]).relative_to(base)) if Path(cj["file"]).is_relative_to(base) else cj["file"],
                    "line_start": cj["line_start"],
                    "line_end": cj["line_end"],
                    "tokens": cj["tokens"],
                    "text": cj["text"],
                },
            })
        result = {
            "base": str(base),
            "files": len(files),
            "chunks": len(chunks),
            "settings": {
                "top_k": args.top_k,
                "min_jaccard": args.min_jaccard,
                "min_tokens": args.min_tokens,
                "max_tokens": args.max_tokens,
            },
            "candidates": candidates,
        }

    output_text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
        print(f"wrote {len(result['candidates'])} candidates to {args.output}", file=sys.stderr)
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
