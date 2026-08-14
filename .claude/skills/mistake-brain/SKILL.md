---
name: mistake-brain
description: Maintains a persistent, cross-session memory of mistakes for this agent. Logs every failure, bug fix, user correction, or reverted change into MISTAKES.md in a fixed format (what happened / root cause / consequence / prevention rule), routes each lesson into a PARA-structured knowledge base (.agent-brain/<agent>/Projects|Areas|Resources|Archives), and — only when the same root cause repeats 3 or more times — proposes a hard rule for CLAUDE.md or .claude/rules/. Invoke this proactively, without being asked, right after any failure, bug fix, user correction, or reverted/undone change happens in the session, via `/mistake-brain log`. Also use for `/mistake-brain route` (classify pending log entries into PARA), `/mistake-brain promote` (scan for repeated root causes and propose a rule), and `/mistake-brain dream` (periodic reflection across the whole memory). Trigger on phrases like "log this mistake", "we keep hitting this bug", "why does this keep happening", "check for repeated failures", "update the rules file", "organize what you've learned", or "reflect on your memory".
---

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
