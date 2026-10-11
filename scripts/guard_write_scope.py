#!/usr/bin/env python3
"""PreToolUse hook (Write|Edit) for agents that must not change code.

Allows writing only inside <harness>/tasks/. Anything else (target repositories,
harness configuration) is blocked with exit code 2.
"""
import json
import os
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    path = payload.get("tool_input", {}).get("file_path", "")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
    tasks_dir = os.path.realpath(os.path.join(root, "tasks"))
    target = os.path.realpath(path)
    if target == tasks_dir or target.startswith(tasks_dir + os.sep):
        return 0
    print(f"Blocked by pirca-harness: this agent may only write inside {tasks_dir}/ "
          f"(attempted: {path}). Report the needed change instead of making it.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
