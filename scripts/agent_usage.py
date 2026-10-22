#!/usr/bin/env python3
"""Summarize a subagent run from its Claude Code transcript.

Usage: agent_usage.py <agent-id>

Finds ~/.claude/projects/*/*/subagents/agent-<agent-id>.jsonl and prints JSON with the
model(s), token usage (deduplicated per API request), start/end timestamps and duration.

Output tokens are reliable only for transcripts written by Claude Code 2.1.307 or later: there,
the last entry of each request matches the `api_request` telemetry event exactly (checked with and
without thinking). Transcripts from 2.1.300 and earlier keep the usage from the start of the
response, so their output tokens are under-counted; the result says so in `warning`.
"""
import glob
import json
import os
import sys
from datetime import datetime

RELIABLE_OUTPUT_SINCE = (2, 1, 307)


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def version_tuple(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in value.split("."))
    except ValueError:
        return ()


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1
    agent_id = sys.argv[1].removeprefix("agent-")
    pattern = os.path.expanduser(f"~/.claude/projects/*/*/subagents/agent-{agent_id}.jsonl")
    files = glob.glob(pattern)
    if not files:
        print(json.dumps({"agent_id": agent_id, "error": "transcript not found"}))
        return 2

    usage_by_request: dict[str, dict] = {}
    models: set[str] = set()
    timestamps: list[datetime] = []
    tool_uses = 0
    version = None
    for line in open(files[0], encoding="utf-8"):
        entry = json.loads(line)
        version = version or entry.get("version")
        if entry.get("timestamp"):
            timestamps.append(parse_ts(entry["timestamp"]))
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        if isinstance(message.get("content"), list):
            tool_uses += sum(1 for b in message["content"] if b.get("type") == "tool_use")
        usage = message.get("usage")
        if usage:
            models.add(message.get("model", "unknown"))
            key = entry.get("requestId") or message.get("id") or str(len(usage_by_request))
            usage_by_request[key] = usage  # streamed blocks repeat the same usage

    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    for u in usage_by_request.values():
        totals["input"] += u.get("input_tokens", 0)
        totals["output"] += u.get("output_tokens", 0)
        totals["cache_read"] += u.get("cache_read_input_tokens", 0)
        totals["cache_creation"] += u.get("cache_creation_input_tokens", 0)
    totals["total"] = sum(totals.values())

    started = min(timestamps) if timestamps else None
    ended = max(timestamps) if timestamps else None
    reliable = version_tuple(version or "") >= RELIABLE_OUTPUT_SINCE
    result = {
        "agent_id": agent_id,
        "claude_code_version": version,
        "output_tokens_reliable": reliable,
        "models": sorted(models),
        "api_requests": len(usage_by_request),
        "tool_uses": tool_uses,
        "tokens": totals,
        "started_at": started.isoformat() if started else None,
        "ended_at": ended.isoformat() if ended else None,
        "duration_s": round((ended - started).total_seconds(), 1) if started else None,
    }
    if not reliable:
        result["warning"] = ("output tokens under-counted: transcript written by Claude Code "
                             f"{version}, reliable only since 2.1.307")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
