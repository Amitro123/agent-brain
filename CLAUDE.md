# CLAUDE.md

Guidance for Claude Code working in this repository.

## Mistake memory

Log mistakes in MISTAKES.md (what happened, root cause, consequence, prevention rule) — see `.claude/skills/mistake-brain/SKILL.md` for the full workflow (`/mistake-brain log|route|promote|dream`).

## Rules

- Before retrying a flaky test that touches a shared resource (a DB lock, a migration, a seed-data fixture), wait for confirmation the previous attempt's lock has been released instead of retrying immediately.
