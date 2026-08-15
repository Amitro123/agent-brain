# router.md — classify MISTAKES.md entries into PARA

Invoked by `/mistake-brain route`. Goal: take every entry in `MISTAKES.md` still marked `Status: unrouted` and give it a permanent home in `.agent-brain/<agent>/`, so the raw log can stay a fast inbox instead of the thing anyone has to actually search.

Applies uniformly to all four `Type`s (`mistake`, `success`, `decision`, `handoff`) — the PARA decision tree below doesn't branch on `Type` at all. A `handoff` entry gets exactly the same routing treatment as a `mistake` entry; there's no separate lifecycle or destination for it (see `SKILL.md`'s Concurrency section for why a special handoff status was rejected).

## Procedure

MISTAKES.md is append-only — routed and promoted entries stay in it, they just get their `Status` flipped in place. Left unchecked that means both the file and the cost of reading it grow forever, even though only a shrinking fraction of it (the still-unrouted entries) is ever relevant to a route pass. Two independent fixes, run in order:

1. Run `python .claude/skills/mistake-brain/scripts/compose_mistakes.py MISTAKES.md` first. This is a mechanical, no-judgment-required step — the script itself decides whether the file is even over its line threshold (default 400 lines) and, if so, moves the oldest already-`routed`/`promoted` entries (never `unrouted` ones — those have no other copy yet) into a single `MISTAKES-archive.md`. Below threshold, it's a no-op. This keeps the active file bounded by size, not by an agent tracking dates or deciding what still "matters" — that judgment call is exactly the kind of thing worth keeping out of a routine pass, since it just adds cost without a payoff (see `promote.md` for the one tradeoff this creates).
2. `Grep` `MISTAKES.md` for the pattern `^- \*\*Status:\*\*\s*unrouted\s*$` (matching the actual rendered field text from `format-spec.md`, bold markers included, anchored to the whole line) with 5 lines of context before each match (`-B 5`, content mode). The line anchors matter: an unanchored substring match will also fire inside a free-text field that happens to quote the field format as an example (this has already happened once — see MISTAKES.md), pulling back a bogus "entry" that doesn't parse. Each real match's context block is a complete entry — header, all fields, through the `Status` line — so this pulls back exactly the entries that need routing and nothing else. If there are no matches, say so and stop — nothing to do.
3. For each unrouted entry, in oldest-to-newest order (so earlier context isn't lost if two entries are related), apply the decision tree below to pick exactly one PARA category and destination file. Do this classification for *all* pending entries before writing anything.
4. Group the classified entries by destination file. For each destination file touched by one or more entries (create it if it doesn't exist yet, following the format in that folder's README.md): read it once, then write all of that file's new lesson blocks in a single edit — not a separate read-then-edit per entry. If three entries all land in `Areas/ci.md`, that's one read and one edit of `Areas/ci.md`, not three. Each lesson block:
   ```md
   ## [YYYY-MM-DD] <short title, can reuse the MISTAKES.md title>
   - Added: YYYY-MM-DD HH:MM
   <the actionable takeaway, rewritten as an imperative instruction, 1-2 sentences>
   Source: mistake log entry [YYYY-MM-DD HH:MM] <title>
   ```
   The one-line takeaway comes from whichever field carries it for that entry's `Type` (see `references/format-spec.md`): `Prevention rule` for `mistake`, `Repeat guidance` for `success`, `Rationale` for `decision`, `Next steps` for `handoff`. Insert newest-first within that file too. Cite the entry by date and title, not by file path — `compose_mistakes.py` may later move the entry itself from `MISTAKES.md` into `MISTAKES-archive.md`, and the citation should stay meaningful either way.

   The `Added` field is what lets `dream.md` assess an individual entry's freshness — independent of `MEMORY.md`'s own per-file "last updated" date, which only tells you when a file was *last touched at all*, not how old any given entry inside it is. A PARA file can look "recently updated" in `MEMORY.md` because of one new entry while everything else in it is stale; `Added` is the signal that catches that.
5. Go back to `MISTAKES.md` and, for each routed entry, use a targeted `Edit` to update its two fields in place (nothing else in the entry changes) — `Edit` sends only the diff, not the whole file, so this stays cheap regardless of how large MISTAKES.md has grown:
   ```md
   - **PARA route:** <Project|Area|Resource|Archive>: <file path>
   - **Status:** routed
   ```
6. After all entries are processed, update `.claude/agent-memory/<agent>/MEMORY.md`: for each PARA file you touched, add or refresh its one-line index entry (summary, lesson count, last-updated date). This is a full regeneration of that file's line, not an append — the index should always reflect current state, not history.
7. Report a short summary to the user: how many entries were routed and where (and, if step 1 archived anything, mention that too). Don't ask for confirmation for this pass — routing into `.agent-brain/` is knowledge classification, not a change to agent behavior, so it's low-stakes and easily corrected on the next `dream` pass (see SKILL.md's "Safety" section for the full route-vs-promote asymmetry — the confirmation gate is only for `promote`, which changes behavior going forward).

## Decision tree

Ask these in order; stop at the first "yes."

1. **Is this tied to a specific piece of work that's still open right now** — the current task, an active branch, an open ticket, a feature not yet shipped? → **Project**. File: `.agent-brain/<agent>/Projects/<project-slug>.md`. Name the slug after whatever the project is actually called in this session (branch name, ticket ID, feature name) — don't invent a new name if one is already in use elsewhere in the codebase or conversation.

2. **Is this about a domain the agent will keep coming back to, independent of which project** — authentication, CI/CD, database migrations, a specific external service, testing conventions? → **Area**. File: `.agent-brain/<agent>/Areas/<area-slug>.md`. Reuse an existing Area file if one already covers this domain; check `MEMORY.md`'s Areas section before creating a new one, since fragmenting one domain across two files defeats the purpose.

3. **Is this a general principle that would still be true in a completely different codebase** — a security practice, an error-handling convention, a review habit? → **Resource**. File: `.agent-brain/<agent>/Resources/<topic-slug>.md`.

4. **Otherwise — is this closed and unlikely to recur** (a one-off incident, an external outage, a bug in a dependency that's since been patched, a project that no longer exists)? → **Archive**. File: `.agent-brain/<agent>/Archives/<year>/<slug>.md`.

If none of these feel right after honestly working through them in order, default to **Area** — an overly broad Area file is easy to split later during `/mistake-brain dream`, whereas a lesson stuck in Archive is effectively invisible to future work.

## Judgment calls worth pausing on

- **Project vs. Area**: if you're not sure whether the current work is really a one-off project or actually a recurring domain, ask: "will this lesson matter once this specific task is done?" If yes, it's an Area, not a Project.
- **Area vs. Resource**: an Area lesson mentions a specific system by name ("our auth service always returns 200 on failed login"). A Resource lesson would read the same with the specifics genericized ("don't trust HTTP status codes alone to detect failure — check the body").
- **Ambiguous entries**: if an entry genuinely spans two categories (e.g. a project-specific instance of a general principle), route it to the more specific one (Project or Area) and only promote it to a Resource later if `/mistake-brain promote` or `/mistake-brain dream` notices the same principle recurring across *different* projects/areas.
- Never invent a fifth category or a subfolder structure beyond `<year>/` under Archives. If the PARA files start feeling unwieldy, that's what `/mistake-brain dream` is for — don't solve it ad hoc during a routing pass.
