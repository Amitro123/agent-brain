# CLAUDE.md

Guidance for Claude Code working in this repository.

## Mistake memory

**Standing instruction, not optional guidance:** the moment you fix a bug, revert a change, hit the same bug again, or the user corrects your approach — run `/mistake-brain log <description>` immediately, in that same turn, before moving on. Don't wait to be asked, don't skip small ones, and don't decide a fix is "too minor" to log — do this by default. This applies even when you're unsure the skill's own trigger conditions are met; false positives here are cheap (an easily-corrected log entry), false negatives are not (a lost data point toward `promote`'s 3x threshold).

Full workflow (`route`/`promote`/`dream`), the entry format, and why this gate exists: `.claude/skills/mistake-brain/SKILL.md`.

## Rules

_(no promoted rules yet — populated by `/mistake-brain promote` after a root cause repeats 3+ times, always with explicit approval first)_
