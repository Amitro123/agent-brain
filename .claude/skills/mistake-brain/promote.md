# promote.md — repeated root causes → hard rules

Invoked by `/mistake-brain promote`. Goal: catch the failures that keep happening despite being logged and routed, and turn them into something that actually changes future behavior — a rule in `CLAUDE.md` (if it should apply everywhere) or `.claude/rules/<slug>.md` (if it's scoped to one area).

The reasoning: a lesson sitting in `.agent-brain/Areas/ci.md` only helps if something reads that file before touching CI. A rule in CLAUDE.md is read every session, unconditionally. That's a much stronger guarantee, which is exactly why it needs a much higher bar — three independent failures with the same root cause, not one bad afternoon.

**Scope tradeoff, by design:** `check_repetition.py` only scans the active `MISTAKES.md`, never `MISTAKES-archive.md` (see `router.md` step 1 / `scripts/compose_mistakes.py`). This means a root cause that repeats with a very long gap — long enough that its earlier instances got archived out before this run — won't be caught automatically. That's an accepted tradeoff, not an oversight: scanning the archive too would mean re-reading unboundedly growing history on every `promote` run, which is exactly the cost `compose_mistakes.py` exists to avoid. If you suspect an old, archived pattern is recurring, grep `MISTAKES-archive.md` by hand rather than folding it into the routine scan.

## Procedure

1. Run the repetition scanner from the repo root:
   ```bash
   python .claude/skills/mistake-brain/scripts/check_repetition.py MISTAKES.md --json
   ```
   This groups all MISTAKES.md entries (routed or not — promotion looks at the whole log, not just fresh ones) by similarity of their `Root cause` field and reports every group with 3 or more members, along with the entry titles/dates and a representative root-cause snippet.

2. If there are no groups ≥3, tell the user "no root cause has repeated 3+ times yet" and stop. Don't force a promotion out of 2 similar-but-not-quite entries — that's what makes this signal trustworthy.

3. For each qualifying group, draft a candidate rule:
   - Write it as a single imperative sentence, the way you'd want to read it in CLAUDE.md — not a description of the bug, an instruction for next time. ("Before running a DB migration in CI, check for an existing lock file" — not "CI migrations sometimes fail due to lock contention.")
   - Decide scope: if the repeated root cause is genuinely general (would apply regardless of which part of the codebase you're in), it's a CLAUDE.md candidate. If it's scoped to one area (only matters for auth code, only matters for the frontend build), it belongs in `.claude/rules/<area-slug>.md` instead — check whether a rules file for that area already exists before creating a new one.
   - Cite the evidence: list the specific MISTAKES.md entries (date + title) that justify this rule. This is what makes it a proposal grounded in repetition, not a guess.

4. Present each candidate to the user for approval — **do not write anything yet**. Show:
   - The exact rule text.
   - Exactly where it would go (which file, and whether it's a new file or an addition to an existing one).
   - The evidence list.

   Check `AGENT_AUTO_IMPROVE` first (`echo $AGENT_AUTO_IMPROVE`): if it's not `1`, this presentation is mandatory and you must wait for an explicit yes/no per candidate before writing anything — see SKILL.md's Safety section for why this gate exists and isn't optional by default. If `AGENT_AUTO_IMPROVE=1`, you may write directly, but still show what you wrote afterward so it's visible, not silent.

5. On approval, write the rule:
   - **CLAUDE.md**: append under an existing `## Rules` heading if one exists, otherwise create one. Keep the file's existing structure and tone — don't reformat unrelated parts of the file.
   - **.claude/rules/<slug>.md**: create or append to the area-specific file, one rule per bullet.

6. After writing, close the loop on the source entries: for each MISTAKES.md entry that justified the rule, update its `Status` field to `promoted` (leave `PARA route` as-is — promotion doesn't undo routing). Then add one line to `.claude/agent-memory/<agent>/MEMORY.md` under "Rules promoted so far" recording the rule, where it went, and which entries justified it — this is the audit trail back from "why does this rule exist" to the actual failures.

## What NOT to do

- Don't promote off a single dramatic failure, no matter how costly — the threshold is repetition, not severity. A one-off catastrophe belongs in Archives with a strong prevention note, not in CLAUDE.md.
- Don't silently rewrite or merge existing CLAUDE.md rules while you're in there for an unrelated promotion — scope your edit to the addition you proposed.
- Don't treat "the user said yes once before" as standing approval for future promotions — each candidate gets its own explicit confirmation, every run, unless `AGENT_AUTO_IMPROVE=1` is set.
- Don't invent a root-cause grouping the scanner didn't find in order to hit the threshold faster — if two failures feel related but the scanner split them into different groups, that's a signal the root causes aren't actually the same; describing them more precisely (not lumping them together) is the fix.
