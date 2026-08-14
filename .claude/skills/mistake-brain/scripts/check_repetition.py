#!/usr/bin/env python3
"""Scan MISTAKES.md for root causes that repeat 3+ times.

Used by /mistake-brain promote to decide which failures have happened
often enough to justify a hard rule in CLAUDE.md or .claude/rules/.

Usage:
    python check_repetition.py [path/to/MISTAKES.md] [--min-count 3] [--threshold 0.6] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

ENTRY_HEADER_RE = re.compile(r"^## \[(?P<date>[^\]]+)\]\s*(?P<title>.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^- \*\*(?P<key>[^:*]+):\*\*\s*(?P<value>.+?)\s*$")


@dataclass
class Entry:
    date: str
    title: str
    fields: dict = field(default_factory=dict)

    @property
    def root_cause(self) -> str:
        return self.fields.get("Root cause", "")

    @property
    def status(self) -> str:
        return self.fields.get("Status", "")


def parse_entries(text: str) -> list[Entry]:
    headers = list(ENTRY_HEADER_RE.finditer(text))
    entries = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[start:end]
        fields = {}
        for line in body.splitlines():
            fm = FIELD_RE.match(line.strip())
            if fm:
                fields[fm.group("key").strip()] = fm.group("value").strip()
        entries.append(Entry(date=m.group("date"), title=m.group("title"), fields=fields))
    return entries


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def cluster_by_root_cause(entries: list[Entry], threshold: float) -> list[list[Entry]]:
    """Greedy single-pass clustering: each entry joins the first cluster whose
    representative (first member) it's similar enough to, else starts a new one.
    Good enough for the small, mostly-manually-written logs this operates on —
    not meant to be a general-purpose text clustering algorithm."""
    clusters: list[list[Entry]] = []
    reps: list[str] = []
    for entry in entries:
        norm = normalize(entry.root_cause)
        if not norm:
            continue
        placed = False
        for idx, rep in enumerate(reps):
            if similarity(norm, rep) >= threshold:
                clusters[idx].append(entry)
                placed = True
                break
        if not placed:
            clusters.append([entry])
            reps.append(norm)
    return clusters


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="MISTAKES.md", help="Path to MISTAKES.md (default: ./MISTAKES.md)")
    parser.add_argument("--min-count", type=int, default=3, help="Minimum repeats to report a group (default: 3)")
    parser.add_argument("--threshold", type=float, default=0.6, help="Root-cause similarity threshold, 0-1 (default: 0.6)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    entries = parse_entries(text)
    if not entries:
        print(f"error: no entries found in {path} — check it follows the MISTAKES.md format", file=sys.stderr)
        return 1

    clusters = cluster_by_root_cause(entries, args.threshold)
    repeated = [c for c in clusters if len(c) >= args.min_count]
    repeated.sort(key=len, reverse=True)

    if args.json:
        out = [
            {
                "count": len(group),
                "representative_root_cause": group[0].root_cause,
                "entries": [
                    {"date": e.date, "title": e.title, "root_cause": e.root_cause, "status": e.status}
                    for e in group
                ],
            }
            for group in repeated
        ]
        print(json.dumps({"total_entries": len(entries), "repeated_groups": out}, indent=2))
        return 0

    print(f"Scanned {len(entries)} entries in {path}")
    if not repeated:
        print(f"No root cause repeats {args.min_count}+ times yet.")
        return 0

    print(f"\n{len(repeated)} root cause(s) repeating {args.min_count}+ times:\n")
    for group in repeated:
        print(f"  [{len(group)}x] {group[0].root_cause}")
        for e in group:
            print(f"      - {e.date}  {e.title}  (status: {e.status or 'unknown'})")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
