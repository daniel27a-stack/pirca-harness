#!/usr/bin/env python3
"""PreToolUse hook (Bash): block any `git push` that would update main/master.

Reads the hook payload from stdin. Exit code 2 blocks the tool call and sends
stderr back to Claude; exit code 0 lets it through.
"""
import json
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master"}


def targets_protected(refspec: str) -> bool:
    dest = refspec.split(":")[-1].lstrip("+")
    dest = dest.removeprefix("refs/heads/")
    return dest in PROTECTED


def current_branch(cwd: str, git_dir_args: list[str]) -> str:
    try:
        out = subprocess.run(
            ["git", *git_dir_args, "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd or None, capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def check_push(tokens: list[str], cwd: str) -> str | None:
    """Return a reason to block, or None."""
    i = tokens.index("git")
    git_dir_args = []
    j = i + 1
    while j < len(tokens) and tokens[j] != "push":
        if tokens[j] == "-C" and j + 1 < len(tokens):
            git_dir_args += ["-C", tokens[j + 1]]
            j += 2
            continue
        j += 1
    if j >= len(tokens):
        return None
    args = [t for t in tokens[j + 1:] if not t.startswith("-")]
    refspecs = args[1:]  # first positional is the remote
    if any(targets_protected(r) for r in refspecs):
        return "pushing to a protected branch (main/master)"
    if not refspecs and current_branch(cwd, git_dir_args) in PROTECTED:
        return "pushing the current branch, which is main/master"
    return None


def main() -> int:
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    cwd = payload.get("cwd", "")
    if "push" not in command:
        return 0
    # Inspect each simple command separately (&&, ||, ;, |, newlines).
    for part in re.split(r"&&|\|\||;|\||\n", command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        if "git" in tokens and "push" in tokens:
            reason = check_push(tokens, cwd)
            if reason:
                print(f"Blocked by pirca-harness: {reason}. "
                      "Changes reach main only through a pull request.", file=sys.stderr)
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
