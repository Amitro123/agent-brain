# mistake-brain-skill

## [2026-08-14] router.md's grep pattern for unrouted entries never matched anything
When writing a grep/regex pattern against a markdown template defined elsewhere in the same skill, copy the literal rendered text (including formatting markers like `**`) instead of re-deriving the pattern from the conceptual field name — and test the pattern against a real file before shipping it.
Source: mistake log entry [2026-08-14 21:53] router.md's grep pattern for unrouted entries never matched anything

## [2026-08-14] compose_mistakes.py left orphaned blank-line gaps after removing entries
After any text-removal operation between fixed separators, normalize consecutive blank lines afterward rather than assuming the removal is clean.
Source: mistake log entry [2026-08-14 21:47] compose_mistakes.py left orphaned blank-line gaps after removing entries

## [2026-08-14] compose_mistakes.py archive file missing blank line before first entry
When composing text with fixed separators, always rstrip and re-append a known separator instead of branching on the existing suffix.
Source: mistake log entry [2026-08-14 21:45] compose_mistakes.py archive file missing blank line before first entry
