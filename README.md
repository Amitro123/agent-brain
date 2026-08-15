# agent-brain

This repo hosts `mistake-brain`, a Claude Code skill that gives an agent persistent, cross-session memory — not just of its mistakes, but of anything worth carrying forward: mistakes, confirmed successes, real decisions, and handoffs. It combines a fixed-format event log (`MISTAKES.md`, one of four entry `Type`s — see below) with a PARA-structured knowledge base (`.agent-brain/`), and only turns a repeated root cause or confirmed success pattern into an enforced rule (`CLAUDE.md` / `.claude/rules/`) after 3+ occurrences and explicit approval.

**Why `MISTAKES.md` if it's not just mistakes?** The name predates the four-type schema and stayed on purpose — renaming it would break every existing cross-reference and git history for no functional gain. Think of it as the project's name for "the raw inbox," the way a team might keep calling a channel `#incidents` after it starts also being used for postmortems and decisions. The `Type` field is what actually distinguishes entries, not the filename.

Full workflow, command reference, and design rationale: [`.claude/skills/mistake-brain/SKILL.md`](.claude/skills/mistake-brain/SKILL.md).

## Getting Started / Cold Start

On a fresh install (a repo where `MISTAKES.md` is still empty), all four commands — `log`, `route`, `promote`, `dream` — run without error, but three of the four return trivial or no-op results. **That's expected, not a bug**, and worth understanding up front so an empty result doesn't look like something broke:

- **`log` works immediately.** It just appends an entry — there's no minimum history required. Run it after any real fix, revert, or correction from day one.
- **`route` has nothing to classify** until at least one entry with `Status: unrouted` exists. On a brand-new `MISTAKES.md`, that means zero — `route` will correctly report "nothing to do."
- **`promote` won't find a 3x-repeat cluster** until the same root cause (a `mistake`) or the same confirmed pattern (a `success`) has actually happened three times — `decision` and `handoff` entries are never promotion candidates. `check_repetition.py`'s default threshold is genuinely 3 occurrences (or 2 + one archive match, see `promote.md`) — this realistically takes **weeks of real usage**, not something that happens on day one or even week one. An empty result here is the normal state for a long time, not evidence the mechanism is broken.
- **`dream` returns empty findings** until there's more than one PARA file to compare — cross-cutting-pattern detection and stale/oversized checks need something to compare *against*. With zero or one PARA file, there's nothing to find yet.
- **Automatic triggering is not, and will never be, 100% reliable.** Measured should-trigger recall started at ~27% on the bare skill description; reinforcing the same instruction in `CLAUDE.md` (which loads unconditionally into every session, unlike a skill description competing for attention) raised it to ~73% in the same measurement. Both numbers are small-sample, directional signals, not guarantees — this is a model judgment call and always will be. Until/unless it's even higher, **explicitly running `/mistake-brain log`** after a fix/revert/correction remains the reliable fallback, not automatic triggering alone.

### Architectural note: `MISTAKES.md` is a single point of failure

`route`, `promote`, and `dream` have **zero independent discovery mechanism**. Each one's entry condition is gated entirely on data already sitting in `MISTAKES.md`: `route` classifies existing unrouted entries, `promote` clusters existing entries by root cause, `dream` compares existing PARA files derived from those entries. None of them go looking for a mistake on their own. If `log` never fires — whether from a skill-trigger miss or nobody remembering to run it manually — **the entire chain stays frozen, not degraded.** A `dream` pass reporting "no findings" looks identical whether nothing's wrong or logging silently stopped three weeks ago; there is no independent signal distinguishing the two without a heartbeat check.

Two mitigations exist for this, neither of which is a full fix:
- **A deterministic fallback that doesn't depend on the skill triggering at all**: a `PostToolUse` hook (`.claude/hooks/draft_mistake_on_revert.py`, registered in `.claude/settings.json`) auto-drafts a low-detail `MISTAKES.md` entry whenever an unambiguous revert-like `git` command runs (`git revert`, `git reset --hard`, `git checkout -- <path>`, `git clean -f`). It's narrow by design — Edit/Write-based revert detection has no reliable deterministic signal, so this only catches the subset of mistakes that show up as a specific git command, not "the user said this was wrong in chat."
- **`dream`'s heartbeat check** (see `references/dream.md`): if `MISTAKES.md` hasn't been touched in 7+ days, `dream` reports that explicitly as a finding — "no log activity in N days" — instead of silently reporting "nothing new," which is the one thing that tells a quiet system apart from a broken one.

Neither mitigation makes the single-point-of-failure go away — they narrow the blast radius (git-command reverts are caught deterministically; a stalled log gets surfaced within a week instead of indefinitely) without solving the general case of "Claude never noticed and nobody ran the command."

For a detailed day-1/week-1 walkthrough, exact command syntax, and an FAQ on the automatic-triggering gap, see [`.claude/skills/mistake-brain/references/onboarding.md`](.claude/skills/mistake-brain/references/onboarding.md).
