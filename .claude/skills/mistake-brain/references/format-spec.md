# MISTAKES.md entry format

Every entry, no exceptions, uses this exact template so `check_repetition.py` and `router.md` can parse it reliably:

```md
## [YYYY-MM-DD HH:MM] <short title>
- **What happened:** <one or two sentences, factual>
- **Root cause:** <the actual underlying reason, not the symptom>
- **Consequence:** <what it cost>
- **Prevention rule:** <one sentence, what would have caught this>
- **PARA route:** unrouted
- **Status:** unrouted
```

## Field guide

- **Title**: short, specific, greppable. "Forgot to await async DB write in checkout" not "Bug in checkout."
- **What happened**: describe the observable failure, not the fix. "Tests passed locally but failed in CI with a timeout" not "I fixed the flaky test."
- **Root cause**: this is the field everything downstream depends on — `check_repetition.py` clusters on it, and a vague root cause ("something was wrong with the config") will never match anything, defeating the whole point of `/mistake-brain promote`. Be as specific and consistent as you can: reuse the same phrasing you've used before for the same kind of failure when it's genuinely the same cause.
- **Consequence**: what it actually cost — time lost, what broke downstream, whether the user had to notice and correct it themselves. This is what makes `promote.md`'s evidence trail meaningful instead of just a list of similar bugs.
- **Prevention rule**: write this as an instruction, not a description. "Always await DB writes before returning a response" not "async writes can be missed."
- **PARA route** / **Status**: managed by `/mistake-brain route` and `/mistake-brain promote` — don't hand-edit these except when writing a brand-new entry (both start as `unrouted`).

## `Status` lifecycle

`unrouted` → `routed` (set by `router.md`) → `promoted` (set by `promote.md`, only for entries that became a CLAUDE.md/.claude/rules rule — most routed entries stay at `routed` forever, and that's fine).

## Worked example

```md
## [2026-08-14 21:40] CI migration step failed on concurrent lock
- **What happened:** The DB migration step in CI failed with a lock-timeout error after another job had started a migration on the same shared staging DB.
- **Root cause:** No lock file or mutex guarding concurrent migration runs against the shared staging database.
- **Consequence:** CI run had to be manually re-triggered; ~15 minutes lost, and it wasn't obvious from the error message what had actually gone wrong.
- **Prevention rule:** Before running a DB migration in CI, acquire a lock (or check for one) scoped to the target database.
- **PARA route:** unrouted
- **Status:** unrouted
```
