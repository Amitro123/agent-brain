# mistake-brain-skill

## [2026-08-15] Kept the MISTAKES.md filename when generalizing to 4 entry types
- Added: 2026-08-15 17:15
Renaming a widely-cross-referenced file for a purely cosmetic scope change isn't worth the migration cost — a new field (`Type`) that disambiguates content is a cheaper and clearer fix than a rename, as long as the mismatch is documented explicitly rather than left to look like an oversight.
Source: mistake log entry [2026-08-15 17:00] Kept the MISTAKES.md filename when generalizing to 4 entry types

## [2026-08-15] draft_mistake_on_revert.py's own regex matched its test payload's quoted example text
- Added: 2026-08-15 17:15
When matching a pattern against a shell command string (not just a markdown field), strip quoted spans before matching — quoted example text inside echo/printf/heredoc is the same class of problem as a quoted illustration inside a free-text field, just in a different file format.
Source: mistake log entry [2026-08-15 11:28] draft_mistake_on_revert.py's own regex matched its test payload's quoted example text

## [2026-08-14] Shell-quoting escape syntax leaked into SKILL.md's YAML frontmatter
- Added: 2026-08-15 17:15
After editing YAML frontmatter (or any structured/parseable format) with an escaped special character, validate by actually parsing it, not by visual inspection — and use the target format's own escape convention, not a habit borrowed from a different context (shell).
Source: mistake log entry [2026-08-14 22:45] Shell-quoting escape syntax leaked into SKILL.md's YAML frontmatter

## [2026-08-14] router.md's unrouted grep pattern false-matches quoted example text
- Added: 2026-08-15 17:15
Anchor structural-field grep patterns to match the whole line, not just a substring, so the pattern can only match the real field line, never a quotation of it inside another field's descriptive text.
Source: mistake log entry [2026-08-14 22:32] router.md's unrouted grep pattern false-matches quoted example text

## [2026-08-14] CI cluster promoted to CLAUDE.md despite the scope rubric indicating Area-scope
Never override a classification decision to manufacture test-path coverage — if a procedure's own rubric produces the same answer for two cases, that's the correct answer for both; broaden the test scenario with different data instead of contradicting the rubric on live output.
Source: mistake log entry [2026-08-14 23:10] CI cluster promoted to CLAUDE.md despite the scope rubric indicating Area-scope

## [2026-08-14] check_repetition.py keeps re-flagging already-promoted clusters
Fixed: check_repetition.py now excludes Status: promoted entries from clustering (unrouted/routed still count). Verified against the real MISTAKES.md — 6 already-promoted entries correctly excluded, 0 false candidates.
Source: mistake log entry [2026-08-14 22:30] check_repetition.py keeps re-flagging already-promoted clusters

## [2026-08-14] router.md's grep pattern for unrouted entries never matched anything
When writing a grep/regex pattern against a markdown template defined elsewhere in the same skill, copy the literal rendered text (including formatting markers like `**`) instead of re-deriving the pattern from the conceptual field name — and test the pattern against a real file before shipping it.
Source: mistake log entry [2026-08-14 21:53] router.md's grep pattern for unrouted entries never matched anything

## [2026-08-14] compose_mistakes.py left orphaned blank-line gaps after removing entries
After any text-removal operation between fixed separators, normalize consecutive blank lines afterward rather than assuming the removal is clean.
Source: mistake log entry [2026-08-14 21:47] compose_mistakes.py left orphaned blank-line gaps after removing entries

## [2026-08-14] compose_mistakes.py archive file missing blank line before first entry
When composing text with fixed separators, always rstrip and re-append a known separator instead of branching on the existing suffix.
Source: mistake log entry [2026-08-14 21:45] compose_mistakes.py archive file missing blank line before first entry
