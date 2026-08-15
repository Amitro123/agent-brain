# onboarding.md — first-week walkthrough

Supplement to the "Getting Started / Cold Start" section in the repo's root `README.md`. That section tells you *what to expect*; this file walks through *what it actually looks like*, day by day, with the real thresholds from the code — not vague descriptions of "eventually" or "enough."

## Day 1

A fresh `MISTAKES.md` looks like this — the full header, no entries below the marker (quoted verbatim, not paraphrased, so you can diff your own fresh file against it):

```md
# MISTAKES.md

Raw, append-only log of failures, corrections, and reverted changes for this agent. Newest entries go directly below this header — never edit or delete a past entry's content, only update its `Status` and `PARA route` fields as it gets processed.

This file is the *inbox*. It is not meant to be read top-to-bottom for context — durable lessons live in `.agent-brain/` (see `.claude/agent-memory/<agent>/MEMORY.md` for the index). This file exists so nothing gets lost before it's been triaged.

- Format: see `.claude/skills/mistake-brain/references/format-spec.md`
- How entries get here: `.claude/skills/mistake-brain/SKILL.md` → `/mistake-brain log`
- How entries get triaged into PARA: `.claude/skills/mistake-brain/router.md` → `/mistake-brain route`
- How repeats become rules: `.claude/skills/mistake-brain/promote.md` → `/mistake-brain promote`
- Synthetic validation data (used to exercise the promote gate during development): `tests/fixtures/mistake-brain/` — this file only ever holds real entries

<!-- mistake-brain: new entries are inserted immediately below this line -->
```

To log the first entry, either let the skill trigger automatically (unreliable right now — see the FAQ below) or run it yourself:

```
/mistake-brain log <one-line description of what happened>
```

That dispatches to `SKILL.md`'s `log` procedure: it fills in the four-field template (What happened / Root cause / Consequence / Prevention rule) from `references/format-spec.md` and inserts it right below the marker. `PARA route` and `Status` both start as `unrouted` — nothing else happens automatically. `route`, `promote`, and `dream` are separate, deliberately not fused into `log` (see `SKILL.md`'s `log` section for why: logging should be a fast, uninterrupting side effect of doing the actual work).

You can run `/mistake-brain route` any time after that first entry exists — even with just one entry, it'll correctly classify it into a PARA file. There's no minimum batch size for `route` to be useful; the "wait for volume" constraint is specific to `promote` and `dream`.

## Week 1 — expected state

By the end of a normal first week of real usage, expect:
- A handful of entries in `MISTAKES.md` — some `unrouted` (not yet routed), most probably `routed` (classified into a PARA file) if you've run `route` a few times.
- **Zero entries `promoted`.** This is normal, not a sign something's wrong — see the threshold below.
- One or two PARA files under `.agent-brain/<agent>/`, likely just one or two Projects/Areas, each with a small number of lessons.
- `dream` findings that are still mostly trivial ("no stale Projects, no oversized Areas") — there just isn't enough material yet for the interesting findings (cross-cutting patterns, staleness) to show up.

None of this means the mechanism isn't working. It means the mechanism is working exactly as designed for week 1 — the payoff (`promote`, and `dream`'s cross-file findings) is specifically about *patterns across time*, which requires time to pass.

## When `promote` starts being useful

`promote` calls `scripts/check_repetition.py`, which has two real, literal thresholds you can check yourself in the script:
- `--min-count`, default **3** — a root cause needs to appear 3 times (or 2 times plus one match in `MISTAKES-archive.md`, via `promote.md`'s archive-fallback step) before it's even reported as a candidate.
- `--threshold`, default **0.6** — a text-similarity score (0–1) between two entries' `Root cause` fields; below this, they're treated as different failures, not the same one repeating.

In practice this means: `promote` has nothing to offer until you've hit the *same* underlying bug three separate times, worded similarly enough in the `Root cause` field for the similarity check to recognize them as the same thing (see `references/format-spec.md`'s guidance on writing root causes consistently — this is the field that determines whether `promote` can ever find your repeats). For most projects, that's realistically **weeks**, not days — three-in-a-row-on-day-one would be an unusually bad week, not the normal onboarding path.

## When `dream` starts being useful

`dream.md`'s procedure doesn't hard-code a numeric minimum the way `check_repetition.py` does — its cross-cutting-pattern and stale/oversized checks are judgment calls, not a script threshold. But the practical floor is structural: with 0 or 1 PARA files, there is nothing to compare *against*, so the interesting findings (two files independently converging on the same principle, one file ballooning while others stay small) are mechanically impossible to surface. Useful signal realistically starts once you have **2+ PARA files** — which typically means you've run `route` across a couple of different domains, not just repeatedly into the same one file.

## FAQ

**Q: Why didn't the skill trigger automatically after I fixed a bug?**

Because it's currently unreliable at this specific job. A real, measured trigger-rate evaluation (20 queries, 60/40 train/validation split, described in the skill's development history) found should-trigger recall around **27%** — meaning roughly 3 in 4 real "I just fixed X" or "same bug again" moments won't cause Claude to invoke `mistake-brain` on its own, even though the description was rewritten specifically to improve this. Should-not-trigger accuracy is solid (no false positives observed), the gap is specifically under-triggering.

**Workaround, until this improves:** don't wait for automatic triggering. Explicitly run `/mistake-brain log <description>` yourself right after any real fix, revert, or correction. This matters more, not less, during the first weeks — a missed entry early on isn't just one lost data point, it's one less instance toward the 3x threshold that makes `promote` useful at all.
