# CLAUDE.md

Guidance for Claude Code working in this repository.

## Mistake memory

**Standing instruction, not optional guidance:** the moment you fix a bug, revert a change, hit the same bug again, or the user corrects your approach — run `/mistake-brain log <description>` immediately, in that same turn, before moving on. Don't wait to be asked, don't skip small ones, and don't decide a fix is "too minor" to log — do this by default. This applies even when you're unsure the skill's own trigger conditions are met; false positives here are cheap (an easily-corrected log entry), false negatives are not (a lost data point toward `promote`'s 3x threshold).

**Also applies beyond mistakes:** the same immediate, don't-wait-to-be-asked logging applies when an approach just worked cleanly and is worth repeating (`Type: success`), a real decision got made between genuine alternatives (`Type: decision`), or a task/session is ending with context a future session would need to pick up cold (`Type: handoff`) — see `references/format-spec.md` for the four types and their fields.

Full workflow (`route`/`promote`/`dream`), the entry format, and why this gate exists: `.claude/skills/mistake-brain/SKILL.md`.

## Rules

_(no promoted rules yet — populated by `/mistake-brain promote` after a root cause repeats 3+ times, always with explicit approval first)_
