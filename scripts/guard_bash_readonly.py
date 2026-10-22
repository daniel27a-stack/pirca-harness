#!/usr/bin/env python3
"""PreToolUse hook (Bash) for agents that only read: ba and architect.

Allows only: recording state with scripts/progress.py, read-only git commands, `date` and
read-only filters (head, tail, wc, sort, grep). Redirections to files are never allowed.
Every part of a compound command (&&, ||, ;, |) must be allowed. Exit 2 blocks the call.
"""
import json
import re
import shlex
import sys

GIT_READ_ONLY = {"status", "ls-files", "log", "diff", "show", "rev-parse", "branch", "worktree"}
FILTERS = {"head", "tail", "wc", "sort", "grep"}


def redirects(part: str) -> bool:
    """True if the command writes to a file with an unquoted > or >> (quoted text is fine)."""
    lexer = shlex.shlex(part, posix=True, punctuation_chars=True)
    try:
        return any(set(tok) <= set("<>&|;()") and ">" in tok for tok in lexer)
    except ValueError:
        return ">" in part


def allowed(tokens: list[str]) -> bool:
    if not tokens:
        return True
    if tokens[0] in FILTERS:
        return True
    if tokens[0] == "date":
        return True
    if tokens[:2] == ["python3", "scripts/progress.py"] and len(tokens) > 2 and tokens[2] in {"set", "log", "show", "check"}:
        return True
    if tokens[0] == "git":
        rest = tokens[1:]
        while rest[:1] == ["-C"] and len(rest) >= 2:
            rest = rest[2:]
        if not rest or rest[0] not in GIT_READ_ONLY:
            return False
        if rest[0] == "branch" and any(t in {"-d", "-D", "-m", "-M", "--delete", "--move"} for t in rest[1:]):
            return False
        if rest[0] == "worktree" and (len(rest) < 2 or rest[1] != "list"):
            return False
        return True
    return False


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    for part in re.split(r"&&|\|\||;|\||\n", command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        if redirects(part) or not allowed(tokens):
            print("Blocked by pirca-harness: this agent may only run scripts/progress.py "
                  "(set/log/show/check), read-only git commands, date and read-only filters. "
                  f"Not allowed: {part.strip()}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
