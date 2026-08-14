# MISTAKES.md

Raw, append-only log of failures, corrections, and reverted changes for this agent. Newest entries go directly below this header — never edit or delete a past entry's content, only update its `Status` and `PARA route` fields as it gets processed.

This file is the *inbox*. It is not meant to be read top-to-bottom for context — durable lessons live in `.agent-brain/` (see `.claude/agent-memory/<agent>/MEMORY.md` for the index). This file exists so nothing gets lost before it's been triaged.

- Format: see `.claude/skills/mistake-brain/references/format-spec.md`
- How entries get here: `.claude/skills/mistake-brain/SKILL.md` → `/mistake-brain log`
- How entries get triaged into PARA: `.claude/skills/mistake-brain/router.md` → `/mistake-brain route`
- How repeats become rules: `.claude/skills/mistake-brain/promote.md` → `/mistake-brain promote`

<!-- mistake-brain: new entries are inserted immediately below this line -->

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
