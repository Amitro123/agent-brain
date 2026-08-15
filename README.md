# agent-brain

This repo hosts `mistake-brain`, a Claude Code skill that gives an agent persistent, cross-session memory of its own mistakes. It combines a fixed-format failure log (`MISTAKES.md`) with a PARA-structured knowledge base (`.agent-brain/`), and only turns a repeated root cause into an enforced rule (`CLAUDE.md` / `.claude/rules/`) after 3+ occurrences and explicit approval.

Full workflow, command reference, and design rationale: [`.claude/skills/mistake-brain/SKILL.md`](.claude/skills/mistake-brain/SKILL.md).

## Getting Started / Cold Start

On a fresh install (a repo where `MISTAKES.md` is still empty), all four commands — `log`, `route`, `promote`, `dream` — run without error, but three of the four return trivial or no-op results. **That's expected, not a bug**, and worth understanding up front so an empty result doesn't look like something broke:

- **`log` works immediately.** It just appends an entry — there's no minimum history required. Run it after any real fix, revert, or correction from day one.
- **`route` has nothing to classify** until at least one entry with `Status: unrouted` exists. On a brand-new `MISTAKES.md`, that means zero — `route` will correctly report "nothing to do."
- **`promote` won't find a 3x-repeat cluster** until the same root cause has actually happened three times. `check_repetition.py`'s default threshold is genuinely 3 occurrences (or 2 + one archive match, see `promote.md`) — this realistically takes **weeks of real usage**, not something that happens on day one or even week one. An empty result here is the normal state for a long time, not evidence the mechanism is broken.
- **`dream` returns empty findings** until there's more than one PARA file to compare — cross-cutting-pattern detection and stale/oversized checks need something to compare *against*. With zero or one PARA file, there's nothing to find yet.
- **Automatic triggering is currently unreliable during this early period.** Measured should-trigger recall on the skill's description is ~27% (see `SKILL.md`'s description and the trigger-rate evaluation referenced in its history) — meaning Claude often won't invoke `mistake-brain` on its own after a fix or revert. Until that improves, **explicitly run `/mistake-brain log`** after any real fix/revert/correction rather than relying on automatic triggering, especially in the first weeks when there's no accumulated memory yet to make the cost of a missed entry more visible.

For a detailed day-1/week-1 walkthrough, exact command syntax, and an FAQ on the automatic-triggering gap, see [`.claude/skills/mistake-brain/references/onboarding.md`](.claude/skills/mistake-brain/references/onboarding.md).
