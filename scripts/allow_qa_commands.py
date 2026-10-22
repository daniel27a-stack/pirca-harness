#!/usr/bin/env python3
"""PreToolUse hook (Bash) for qa: pre-approves the commands listed in the repository profiles.

A command is allowed without a permission prompt when every part of it (&&, ||, ;, |, &), and
every `$(...)` inside it, starts with a prefix from the `## QA commands` section of a profile in
repos/*.md or is a read-only filter, and nothing is redirected to a file (`2>&1` is fine). Anything else gets no decision from this hook, so the normal permission flow applies.
It never blocks.
"""
import glob
import json
import os
import re
import shlex
import sys

from guard_bash_readonly import FILTERS, redirects

ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
SUBSTITUTION = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
SEPARATORS = re.compile(r"&&|\|\||;|\||&|\n")


def prefixes(root: str) -> list[list[str]]:
    found = []
    for path in glob.glob(os.path.join(root, "repos", "*.md")):
        section = re.search(r"^## QA commands\n(.*?)(?=^## |\Z)", open(path).read(), re.M | re.S)
        if section:
            found += [m.split() for m in re.findall(r"^- `([^`]+)`", section.group(1), re.M)]
    return found


def command_of(part: str) -> list[str]:
    """Tokens of the command run by this part, without leading `NAME=value` assignments."""
    try:
        tokens = shlex.split(part)
    except ValueError:
        return []
    while tokens and ASSIGNMENT.match(tokens[0]):
        tokens = tokens[1:]
    return tokens or ["true"]


def parts_of(command: str) -> list[str]:
    """Every simple command, including those inside $(...) and backticks."""
    inner = [a or b for a, b in SUBSTITUTION.findall(command)]
    outer = SUBSTITUTION.sub("X", command.replace("2>&1", ""))
    return [p for c in [outer, *inner] for p in SEPARATORS.split(c) if p.strip()]


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    allowed = prefixes(root) + [["true"]] + [[f] for f in FILTERS]
    if "$(" in SUBSTITUTION.sub("", command):  # nested substitutions are not inspected
        return 0
    for part in parts_of(command):
        tokens = command_of(part)
        if redirects(part) or not any(tokens[:len(p)] == p for p in allowed):
            return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "listed in the QA commands of a repository profile"}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
