# router.md — classify MISTAKES.md entries into PARA

Invoked by `/mistake-brain route`. Goal: take every entry in `MISTAKES.md` still marked `Status: unrouted` and give it a permanent home in `.agent-brain/<agent>/`, so the raw log can stay a fast inbox instead of the thing anyone has to actually search.

## Procedure

1. Read `MISTAKES.md` fully. Collect every entry where `Status: unrouted`. If there are none, say so and stop — nothing to do.
2. For each unrouted entry, in oldest-to-newest order (so earlier context isn't lost if two entries are related), apply the decision tree below to pick exactly one PARA category.
3. Append a short lesson to the chosen file (create the file if it doesn't exist yet, following the format in that folder's README.md):
   ```md
   ## [YYYY-MM-DD] <short title, can reuse the MISTAKES.md title>
   <the prevention rule, rewritten as an imperative instruction, 1-2 sentences>
   Source: MISTAKES.md entry [YYYY-MM-DD HH:MM] <title>
   ```
   Insert newest-first within that file too.
4. Go back to the MISTAKES.md entry and update its two fields in place (nothing else in the entry changes):
   ```md
   - **PARA route:** <Project|Area|Resource|Archive>: <file path>
   - **Status:** routed
   ```
5. After all entries are processed, update `.claude/agent-memory/<agent>/MEMORY.md`: for each PARA file you touched, add or refresh its one-line index entry (summary, lesson count, last-updated date). This is a full regeneration of that file's line, not an append — the index should always reflect current state, not history.
6. Report a short summary to the user: how many entries were routed and where. Don't ask for confirmation for this pass — routing into `.agent-brain/` is low-stakes and easily corrected (see SKILL.md's Safety section — the confirmation gate is only for `promote`).

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
