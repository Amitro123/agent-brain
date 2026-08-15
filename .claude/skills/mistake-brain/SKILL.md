---
name: mistake-brain
description: 'Use when: a fix just landed, a bug got reverted, the same bug happened again, a regression needs its root cause traced, or the user corrects your approach mid-session. Invoke this proactively, without being asked, to log the failure to MISTAKES.md (what happened / root cause / consequence / prevention rule), classify it into PARA memory (.agent-brain/<agent>/Projects|Areas|Resources|Archives), and — only once the same root cause has repeated 3+ times — propose a hard rule for CLAUDE.md or .claude/rules/ (never written without explicit approval unless AGENT_AUTO_IMPROVE=1). Also use for the explicit commands `/mistake-brain log`, `/mistake-brain route`, `/mistake-brain promote`, and `/mistake-brain dream`. Do not use when: there''s no fix, revert, repeat failure, or correction in play — plain feature requests, general Q&A, or a first-time issue with no established pattern yet to log against don''t need this skill.'
---

<!-- Keep this file's body under 500 lines (the progressive-disclosure cap skills are meant to respect) —
     push detail into references/ instead of growing this file. Check with: wc -l SKILL.md -->

# mistake-brain

Persistent failure memory for this agent. It combines two ideas into one pipeline:

1. **MISTAKES.md** — a flat, append-only inbox. Every failure gets logged in a fixed four-field format the moment it happens, with zero judgment calls. Fast to write, cheap to never lose anything.
2. **PARA memory** (`.agent-brain/`, structure inspired by [agent-brain](https://github.com/renenel/agent-brain)) — where lessons actually *live*, organized as Projects / Areas / Resources / Archives, indexed by `.claude/agent-memory/<agent>/MEMORY.md`.

MISTAKES.md entries that repeat the same root cause 3+ times graduate into hard rules in CLAUDE.md or `.claude/rules/`. That promotion step is the payoff: without it you just have a diary; with it, patterns become enforced behavior instead of things you vaguely remember happened before.

```
failure happens → log (MISTAKES.md, fast, unstructured triage)
                → route (classify into PARA, .agent-brain/<agent>/…)
                → promote (3+ repeats of the same root cause → CLAUDE.md / .claude/rules/)
dream = periodic reflection across all of the above, run occasionally, not per-failure
```

## Files this skill owns

| Path | Role |
|---|---|
| `MISTAKES.md` (repo root) | Active, chronological log. Newest first. Append-only — never rewrite past entries, only update their `Status`/`PARA route` fields. |
| `MISTAKES-archive.md` (repo root) | Overflow for already-routed/promoted entries, moved out automatically by `scripts/compose_mistakes.py` once `MISTAKES.md` crosses a line threshold, so the active log stays a manageable size. One file, not one per period — see `router.md` step 1. |
| `.agent-brain/<agent>/Projects/*.md` | Lessons tied to a specific, currently active project or feature. |
| `.agent-brain/<agent>/Areas/*.md` | Lessons tied to an ongoing responsibility (auth, CI, DB migrations...) that never really finishes. |
| `.agent-brain/<agent>/Resources/*.md` | General, reusable principles that would hold true in a different codebase too. |
| `.agent-brain/<agent>/Archives/*.md` | Closed, one-off lessons unlikely to recur. |
| `.claude/agent-memory/<agent>/MEMORY.md` | The index over all four PARA folders. Read this first — never grep the raw folders as a first step. |
| `CLAUDE.md` / `.claude/rules/*.md` | Hard rules. Only ever written after a 3+ repeat *and* explicit user approval (see Safety below). |

`<agent>` defaults to `claude`, matching the folders already created (`.agent-brain/claude/`, `.claude/agent-memory/claude/`). If this repo is ever shared by more than one distinct agent persona, give each its own `<agent>` folder rather than mixing memories.

## Concurrency: single-writer assumption

Every file this skill writes to — `MISTAKES.md`, everything under `.agent-brain/<agent>/`, `MEMORY.md`, and `.claude/rules/` — is designed for **single-writer-per-file access**. There is no locking mechanism here; `log`/`route`/`promote`/`dream` all read-then-write with no protection against a concurrent writer changing the file in between.

This is fine under the assumption this skill was built for: one agent identity (`claude`), operating serially, one command at a time. It stops being fine the moment two agent *sessions* run `mistake-brain` concurrently against the same file — e.g. an `arch-lead` sub-agent and a `ui-designer` sub-agent both logging failures and routing at the same time. Two concurrent `route` passes reading `MISTAKES.md`, computing a diff, and writing it back can race and silently drop one of them; two concurrent `promote` passes under `AGENT_AUTO_IMPROVE=1` could both decide to write the same rule.

If you're extending this to multiple concurrent named agents, you have two real options, not a default to fall back on:
1. **Keep each agent's namespace fully separate** — already true structurally for `.agent-brain/<agent-name>/` and `.claude/agent-memory/<agent-name>/MEMORY.md`, since each agent gets its own folder. This alone is sufficient as long as agents never share a *file*.
2. **Add explicit serialization** before allowing concurrent `route`/`promote` passes on files that *are* shared across agents by design — the top-level `MISTAKES.md` and repo-wide `CLAUDE.md`/`.claude/rules/` are the ones that don't naturally partition per-agent.

Don't assume this is handled — it isn't, on purpose, because the single-agent-serial case is what this skill was actually built and tested against.

## Command dispatch

`/mistake-brain <subcommand> [args]`. If no subcommand is given, or the trigger was an actual failure rather than a typed command, default to `log`.

| Subcommand | What it does | Detail |
|---|---|---|
| `log <description>` | Append a new entry to MISTAKES.md | inline below |
| `route` | Classify unrouted MISTAKES.md entries into PARA | `router.md` |
| `promote` | Find 3+ repeated root causes, propose a rule | `promote.md` |
| `dream` | Reflect across the whole memory, tidy it up | `references/dream.md` |

## `log` — record a new mistake

This is the one you'll run constantly, so it's fully inline here (the others are less frequent and get their own files).

Run this immediately after any of:
- a fix you just applied for something that broke
- the user correcting your approach ("no, don't do X", "that's wrong", "revert that")
- a change that got reverted or undone, by you or the user
- a test failure you had to chase down
- realizing mid-task that an earlier assumption was wrong

Don't wait to be asked, and don't skip small ones — the whole point of `promote` is catching patterns across *small*, easy-to-dismiss failures that no one would remember to escalate on their own.

Steps:
1. Read the current top of `MISTAKES.md` (just enough to know where to insert — you don't need the whole file).
2. Fill in the template from `references/format-spec.md`:
   ```md
   ## [YYYY-MM-DD HH:MM] <short title>
   - **What happened:** <concrete, factual — what broke or what was wrong>
   - **Root cause:** <the actual underlying reason, not just the symptom>
   - **Consequence:** <what it cost — time lost, what broke downstream, what the user had to notice/fix>
   - **Prevention rule:** <one sentence — what would have caught or prevented this>
   - **PARA route:** unrouted
   - **Status:** unrouted
   ```
   Use the local date/time. Keep every field to 1-2 sentences — this is a log entry, not a postmortem doc. If you don't know the root cause yet, write your best hypothesis rather than leaving it blank; router.md and promote.md both depend on this field being filled in, even approximately.
3. Insert the new entry immediately below the `<!-- mistake-brain: new entries are inserted immediately below this line -->` marker, so the file stays newest-first.
4. Don't route or promote in the same step — that's a separate, batched pass (see below). Logging should be a fast, un-interrupting side effect of doing the actual work.

You can log more than one entry per session. Each is independent.

## `route` — classify into PARA

See `router.md`. In short: for every MISTAKES.md entry with `Status: unrouted`, decide Project / Area / Resource / Archive, append a short lesson to the matching `.agent-brain/<agent>/...` file, update the MEMORY.md index, then flip the MISTAKES.md entry's `Status` to `routed` and fill in `PARA route`. This can run standalone (`/mistake-brain route`) or you can run it automatically at natural checkpoints (end of a task, before compacting context) — but always as a distinct pass over possibly-several entries, not fused into `log`.

## `promote` — repeated root cause → hard rule

See `promote.md`. In short: run `scripts/check_repetition.py` over MISTAKES.md, look for root causes appearing 3+ times, draft a one-sentence rule, show the user exactly what would be added and where, and only write it after they say yes.

## `dream` — reflect on the whole memory

See `references/dream.md`. A periodic, not per-failure, pass: read MEMORY.md and all PARA files, look for stale Projects that should archive, Areas that have grown unwieldy, and anything promote.md would flag — then update MEMORY.md's summaries and report findings to the user. Never rewrites PARA content without confirmation; MEMORY.md's own index/summary section is the one thing it's allowed to regenerate freely, since it's derived data.

## Safety: confirm before writing durable rules

**Design principle, stated explicitly rather than left implicit:** `route` writes to `.agent-brain/` without requiring user approval, because those writes are *knowledge classification*, not a behavior change — reversible, low-stakes, easily corrected on the next `dream` pass. `promote` requires explicit approval (or `AGENT_AUTO_IMPROVE=1`) before writing to `CLAUDE.md` or `.claude/rules/`, because those writes *change agent behavior going forward*, for every future session, not just this one. The asymmetry is deliberate — it's not that `promote` is "more important," it's that its writes are a different kind of thing.

`log` and `route` only ever touch `MISTAKES.md` and `.agent-brain/`, which are low-stakes, easily-corrected working memory — write to them freely.

`promote` is different: it writes to `CLAUDE.md` or `.claude/rules/`, which change how every future session behaves. Before writing either of those:

1. Check whether `AGENT_AUTO_IMPROVE=1` is set in the environment (`echo $AGENT_AUTO_IMPROVE`).
2. If it is **not** set (the default), show the user the exact diff you want to make and wait for explicit approval before writing. Do not proceed on an ambiguous or implied yes.
3. If it **is** set, you may write directly, but still log what you did (which entries justified it, what you wrote) in MEMORY.md's "Rules promoted so far" section so it's auditable after the fact.

This default-to-asking behavior applies only to `CLAUDE.md` and `.claude/rules/`. It does not apply to `MISTAKES.md` or `.agent-brain/`.

## PARA classification cheat sheet

Full decision tree lives in `router.md`; quick version:

- **Project** — tied to work that's still open right now (a branch, a ticket, a feature in progress).
- **Area** — tied to a domain you'll keep coming back to regardless of which project (auth, CI, deploys, a specific service).
- **Resource** — a principle that would still apply in a different codebase entirely.
- **Archive** — closed, unlikely to recur (an incident, an outage, a project that's finished or dead).

`references/para-guide.md` has worked examples for the ambiguous cases (e.g. "is this a Project lesson or an Area lesson?").
