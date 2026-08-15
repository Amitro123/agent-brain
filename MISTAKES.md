# MISTAKES.md

Raw, append-only log of failures, corrections, and reverted changes for this agent. Newest entries go directly below this header — never edit or delete a past entry's content, only update its `Status` and `PARA route` fields as it gets processed.

This file is the *inbox*. It is not meant to be read top-to-bottom for context — durable lessons live in `.agent-brain/` (see `.claude/agent-memory/<agent>/MEMORY.md` for the index). This file exists so nothing gets lost before it's been triaged.

- Format: see `.claude/skills/mistake-brain/references/format-spec.md`
- How entries get here: `.claude/skills/mistake-brain/SKILL.md` → `/mistake-brain log`
- How entries get triaged into PARA: `.claude/skills/mistake-brain/router.md` → `/mistake-brain route`
- How repeats become rules: `.claude/skills/mistake-brain/promote.md` → `/mistake-brain promote`
- Synthetic validation data (used to exercise the promote gate during development): `tests/fixtures/mistake-brain/` — this file only ever holds real entries

<!-- mistake-brain: new entries are inserted immediately below this line -->

## [2026-08-15 11:28] draft_mistake_on_revert.py's own regex matched its test payload's quoted example text
- **What happened:** While manually testing the new PostToolUse hook (which drafts a MISTAKES.md entry after a revert-like git command), the test command itself — a Bash one-liner that `echo`'d a JSON payload *containing* the string `git reset --hard HEAD~1` as quoted example text — matched the hook's own regex and drafted a bogus entry into the real MISTAKES.md.
- **Root cause:** The hook matched its revert-pattern regex against the raw Bash command string with no distinction between "this text is actually being invoked as a command" and "this text merely appears, quoted, inside a larger command" (an echo, a JSON literal, a heredoc). This is the exact same class of bug already logged twice before in this project (2026-08-14 21:53 and 22:32) — an unanchored/unscoped pattern match firing on quoted example text instead of the real thing — reproduced in a new script because the lesson wasn't generalized into a checklist, just fixed twice in the one place it had already happened.
- **Consequence:** would have permanently baked a fake, self-referential entry into the project's own mistake log if not caught by manually reviewing `git diff` before committing — ironic for a tool whose entire purpose is catching exactly this kind of thing.
- **Prevention rule:** when matching a pattern against a shell command string (not just a markdown field, which is where this bit us the first two times), strip quoted spans before matching — quoted example text inside echo/printf/heredoc is functionally identical to the "quoted illustration inside a free-text field" problem, just in a different file format. More generally: when the same *shape* of bug (unscoped pattern matching hitting quoted example text) recurs a third time across unrelated files, that's exactly what `/mistake-brain promote` is for — checking whether "always test pattern matches against realistic input, including text that merely mentions the pattern" deserves to become a standing rule, not just three separate one-off fixes.
- **PARA route:** unrouted
- **Status:** unrouted

## [2026-08-14 23:10] CI cluster promoted to CLAUDE.md despite the scope rubric indicating Area-scope
- **What happened:** During the AGENT_AUTO_IMPROVE=1 gate demonstration, the CI retry-wrapper cluster was scoped to CLAUDE.md's Rules section, even though it names a specific system ("the CI retry wrapper") — which promote.md's own scope rubric classifies as Area-scoped (`.claude/rules/<area>.md`), same as the payments cluster.
- **Root cause:** Deliberately chose CLAUDE.md for the CI cluster specifically to exercise both promotion destinations in the demo, overriding the honest classification the rubric had already produced (both clusters were independently identified as Area-scoped moments earlier in the same reasoning pass).
- **Consequence:** shipped an inconsistent example of the mechanism — one promoted rule followed the documented scope rule, the other didn't, for a reason (test coverage) unrelated to the rule itself. Caught on review, not by the mechanism itself.
- **Prevention rule:** never override a classification decision to manufacture test-path coverage — if a procedure's own rubric produces the same answer for two cases, that's the correct answer for both; broaden the test scenario with different data instead of contradicting the rubric on live output.
- **PARA route:** Project: .agent-brain/claude/Projects/mistake-brain-skill.md
- **Status:** routed

## [2026-08-14 22:45] Shell-quoting escape syntax leaked into SKILL.md's YAML frontmatter
- **What happened:** Rewriting SKILL.md's description, an apostrophe inside the new text needed escaping. Used the bash single-quote-escape idiom (`'"'"'`) directly in the file content instead of a YAML-appropriate escape, so those literal characters got written into the file.
- **Root cause:** Reached for a shell-quoting technique while writing file content through a non-shell tool (Edit) — the two contexts don't share escaping rules, and the tool doesn't interpret shell syntax at all.
- **Consequence:** would have shipped a SKILL.md with corrupted YAML frontmatter (visibly wrong to a human, but caught before commit by explicitly parsing it with a YAML loader rather than eyeballing the diff).
- **Prevention rule:** after editing YAML frontmatter (or any structured/parseable format) with an escaped special character, validate by actually parsing it, not by visual inspection — and use the target format's own escape convention (YAML: double the quote), not a habit borrowed from a different context (shell).
- **PARA route:** unrouted
- **Status:** unrouted

## [2026-08-14 22:32] router.md's unrouted grep pattern false-matches quoted example text
- **What happened:** Re-running the unrouted-detection grep during a dream pass found 2 matches instead of the expected 1. The second match was inside the "Root cause" field of the entry that documents the *original* grep-pattern bug — that field quotes the literal field text `- **Status:** unrouted` as an example, which the unanchored pattern happily matched too.
- **Root cause:** The grep pattern `\*\*Status:\*\* unrouted` matches anywhere in the file, including mid-sentence inside a free-text field that merely quotes the pattern as an illustration — not just the actual structural field line at the end of an entry template.
- **Consequence:** low real-world risk right now (the false match's `-B 5` context wouldn't parse as a valid entry so it'd likely just get skipped or error out downstream), but it's exactly the kind of silent-corruption risk that should be closed rather than left to luck, especially since a future entry could easily quote this same field name in its description again.
- **Prevention rule:** anchor structural-field grep patterns to match the whole line (`^- \*\*Status:\*\*\s*unrouted\s*$`), not just a substring — so the pattern can only match the real field line, never a quotation of it inside another field's descriptive text.
- **PARA route:** unrouted
- **Status:** unrouted

## [2026-08-14 22:30] check_repetition.py keeps re-flagging already-promoted clusters
- **What happened:** Running `/mistake-brain dream`, the repetition scan (step 2's promotion-candidate check) re-reported both the payments and CI clusters as fresh 3x candidates, even though both had already been promoted to rules minutes earlier in the same session.
- **Root cause:** `check_repetition.py` clusters by root-cause similarity without filtering on `Status` — it has no concept of "already actioned," so a promoted cluster looks identical to a brand-new one on every subsequent scan.
- **Consequence:** every future `/mistake-brain promote` or `/mistake-brain dream` run will keep re-presenting the same already-promoted clusters as if they were new, wasting a review cycle each time (and, worse, could prompt writing a duplicate/near-duplicate rule if not caught by memory of having seen it before).
- **Prevention rule:** `check_repetition.py` should exclude entries whose `Status` is `promoted` from the "new candidate" grouping — or, better, report them separately as "already promoted, no action needed" rather than mixing them into the same output as unactioned repeats.
- **PARA route:** Project: .agent-brain/claude/Projects/mistake-brain-skill.md
- **Status:** routed

## [2026-08-14 21:53] router.md's grep pattern for unrouted entries never matched anything
- **What happened:** Running `/mistake-brain route` for the first time, the Grep step (pattern `Status: unrouted`) returned zero matches even though MISTAKES.md had unrouted entries sitting right there.
- **Root cause:** The actual field text is `- **Status:** unrouted` — the markdown bold markers (`**`) sit between the colon and the value, so the literal substring `Status: unrouted` never occurs in the file. Wrote the grep pattern from the conceptual field name instead of the literal rendered text.
- **Consequence:** would have made `/mistake-brain route` silently do nothing, forever, on every real repo — the most-used non-log command in the skill would have been dead on arrival if this hadn't been caught by actually running it once.
- **Prevention rule:** when writing a grep/regex pattern against a markdown template defined elsewhere in the same skill, copy the literal template text (including formatting markers) instead of re-deriving the pattern from memory — and test the pattern against a real file before shipping it.
- **PARA route:** Project: .agent-brain/claude/Projects/mistake-brain-skill.md
- **Status:** routed

## [2026-08-14 21:47] compose_mistakes.py left orphaned blank-line gaps after removing entries
- **What happened:** After compose_mistakes.py moved entries out of MISTAKES.md, the active file accumulated multiple consecutive blank lines where each removed entry used to be.
- **Root cause:** entry.text was built with `body.rstrip("\n")`, which stripped the trailing blank-line separator out of the text being removed, leaving the original separator orphaned in place instead of collapsing with it.
- **Consequence:** caught in testing (cat -A showed 6 stray blank lines after removing 6 entries); would have made the active log visually noisy if shipped.
- **Prevention rule:** after any text-removal operation between fixed separators, always normalize consecutive blank lines afterward rather than assuming the removal is clean.
- **PARA route:** Project: .agent-brain/claude/Projects/mistake-brain-skill.md
- **Status:** routed

## [2026-08-14 21:45] compose_mistakes.py archive file missing blank line before first entry
- **What happened:** on first run against a repo with no existing MISTAKES-archive.md, the archive header text was glued directly to the first moved entry with no blank line separating them.
- **Root cause:** an `endswith("\n\n")` branch sliced off only one trailing newline from a two-newline header, then appended the entry text directly, instead of normalizing to a fixed separator regardless of what the existing suffix happened to be.
- **Consequence:** caught in testing before commit; would have produced a malformed-looking archive file (header running straight into a `##` heading) if shipped.
- **Prevention rule:** when composing text with fixed separators, always rstrip and re-append a known separator instead of branching on the existing suffix.
- **PARA route:** Project: .agent-brain/claude/Projects/mistake-brain-skill.md
- **Status:** routed
