#!/usr/bin/env python3
"""PostToolUse hook: deterministically draft a MISTAKES.md entry after a
revert-like Bash command, so logging doesn't depend entirely on Claude
noticing via the skill description (measured 27-73% trigger recall
depending on how much of CLAUDE.md/description was reinforced - never
100%, and never will be, since it's a model judgment call).

Scope, deliberately narrow: only fires on unambiguous git commands that
discard/undo work (`git revert`, `git reset --hard`, `git checkout --
<path>`, `git clean -f`). Edit/Write-based revert detection was
considered and rejected - there's no reliable deterministic signal for
"this edit reverts a prior change" from tool_input alone (would need
diffing against git history / semantic understanding, which isn't a
hook's job). Bash git commands are the one place a mistake-shaped event
is mechanically detectable without judgment.

The resulting entry is deliberately low-detail - a draft, not a real
log entry - since a hook has no access to *why* the revert happened,
only that it did. `/mistake-brain route` (or a human) fills in the real
story later; `[auto-draft]` in the title makes these easy to grep for
and never mistake for something Claude wrote with real context.

Known interaction: this hook applies to ANY claude session running with
this project as cwd, including nested/test sessions (e.g. skill-creator
eval harnesses). If a nested session ever runs a matching git command
for real (not just quoted text), it will draft an entry into the real
MISTAKES.md. None of this skill's own eval queries currently do that,
but it's a real edge case worth knowing about, not a hidden one.

Known limitation, found by actually triggering it: matching is a regex
over the raw command string with quoted spans stripped (see
strip_quoted_spans) - a heuristic, not a real shell parser. Unusual
quote nesting/concatenation can still produce a false positive or
false negative. Prefer under-triggering caution over trying to make
this bulletproof; a missed auto-draft just falls back to the normal
trigger-or-manual-log path, which is the existing behavior everywhere
else in this skill.

Never blocks the tool call - always exits 0, hook failures are silent
by design (a missing MISTAKES.md, an unwritable file, anything) rather
than surfacing an error mid-task for a background convenience feature.
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

REVERT_PATTERNS = [
    r"\bgit\s+revert\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+checkout\s+--\s+\S",
    r"\bgit\s+clean\s+-[a-zA-Z]*f",
]

MARKER = "<!-- mistake-brain: new entries are inserted immediately below this line -->"


def strip_quoted_spans(command: str) -> str:
    """Remove content inside single- or double-quoted spans before matching.

    Without this, a command that merely *mentions* a revert pattern as text
    - echoing a JSON payload for a test, printing a commit message, a heredoc
    - matches just as readily as actually running one. This bit the hook's
    own author: testing it by piping `echo '{"command":"git reset --hard
    HEAD~1"}'` into the script matched the regex on the quoted example text
    and drafted a bogus entry into the real MISTAKES.md. This is a heuristic,
    not a real shell parser - deeply nested or unusually concatenated quoting
    can still slip past it - but it closes the common case (echo/printf/
    heredoc containing example command text) without needing full shell
    grammar."""
    return re.sub(r"'[^']*'|\"[^\"]*\"", "", command)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command:
        return 0
    unquoted = strip_quoted_spans(command)
    if not any(re.search(p, unquoted) for p in REVERT_PATTERNS):
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".")
    mistakes_path = project_dir / "MISTAKES.md"
    if not mistakes_path.exists():
        return 0

    text = mistakes_path.read_text(encoding="utf-8")
    if MARKER not in text:
        return 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_command = command.strip().replace("\n", " ")[:200]

    entry_block = (
        f"## [{now}] [auto-draft] Revert-like command detected: `{safe_command}`\n"
        f"- **Type:** mistake\n"
        f"- **What happened:** [auto-draft, needs detail] Ran a revert/reset-like command "
        f"(`{safe_command}`) — this hook only detected *that* something was reverted, not "
        f"*why*. Fill in the real story.\n"
        f"- **Root cause:** [auto-draft, needs detail] — not yet known; describe what made "
        f"the revert necessary.\n"
        f"- **Consequence:** [auto-draft, needs detail]\n"
        f"- **Prevention rule:** [auto-draft, needs detail]\n"
        f"- **PARA route:** unrouted\n"
        f"- **Status:** unrouted\n"
    )

    text = text.replace(MARKER, MARKER + "\n\n" + entry_block, 1)
    text = re.sub(r"\n{3,}", "\n\n", text)  # same normalization compose_mistakes.py uses
    mistakes_path.write_text(text, encoding="utf-8")

    print(f"[mistake-brain] auto-drafted a MISTAKES.md entry for: {safe_command}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
