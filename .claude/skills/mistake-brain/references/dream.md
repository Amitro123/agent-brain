# dream.md — reflect across the whole memory

Invoked by `/mistake-brain dream`, name and spirit borrowed from [agent-brain](https://github.com/renenel/agent-brain)'s `dream` command. Unlike `log`/`route`/`promote`, which each process one thing at a time, `dream` is a periodic, zoomed-out pass over the *entire* memory. Run it occasionally — end of a long session, when MEMORY.md feels out of date, or when the user asks for a "reflection" — not after every failure.

## Why this is separate from `route`/`promote`

`route` and `promote` are reactive and local: they look at one new entry, or one repetition group, in isolation. `dream` is the only pass that looks at the *shape* of the whole memory — whether Areas have grown too broad, whether a Project is actually done and should archive, whether the same Resource-worthy principle is showing up scattered across multiple Area files without anyone noticing. That kind of pattern is invisible from inside a single `route` or `promote` run.

## Procedure

1. Read `.claude/agent-memory/<agent>/MEMORY.md` fully, then read every file it indexes across all four PARA folders. Also skim `MISTAKES.md` for anything still `unrouted` (flag it — dream doesn't route on its own, but should tell the user routing is overdue).

2. Look for, and note as findings (don't act on any of these without asking — see below):
   - **Stale Projects**: a Project file whose project appears finished, merged, or abandoned (no recent related activity, or the user mentions it's done). Candidate to move to Archives, or to Areas if its lessons turned out to be general rather than project-specific.
   - **Oversized or fragmented Areas**: an Area file that's grown long enough to be hard to skim, or the same domain split unnecessarily across two files. Candidate to split or merge.
   - **Cross-cutting principles**: the same underlying lesson appearing independently in two or more different Area/Project files. This is exactly the pattern that should have become a Resource — surface it as a candidate.
   - **Promotion candidates**: run `scripts/check_repetition.py` as part of this pass too (dream is a good time to catch repeats that individual `promote` runs might have missed since MEMORY.md was last updated).
   - **Contradictions**: two lessons that give conflicting guidance. Flag explicitly — don't silently pick a winner.

3. Regenerate MEMORY.md's index sections (Projects/Areas/Resources/Archives one-liners, lesson counts, last-updated dates) to match current reality — this part you can just do, since MEMORY.md is derived/summary data, not a source of truth in itself. Add a `## Last dream` entry at the bottom with today's date and a short summary of what you found.

4. Present the findings from step 2 to the user as a numbered list of proposed actions (archive this, merge these two, split this, promote this). Ask which ones to act on — this is the same confirmation posture as `promote.md` for anything that would move or delete content in `.agent-brain/`, and the mandatory posture for anything touching `CLAUDE.md`/`.claude/rules/`. Regenerating MEMORY.md's own summaries (step 3) doesn't need confirmation; restructuring the underlying PARA files does.

5. Only make the changes the user actually approves, then re-run step 3 to reflect the result.

## What "good" looks like

A useful dream pass ends with MEMORY.md being something a future session could read cold and immediately know where to look — not a bigger pile of unreviewed suggestions. If a dream pass surfaces the same "you should really split Areas/ci.md" finding three times in a row without the user acting on it, that's worth mentioning plainly rather than re-surfacing silently forever.
