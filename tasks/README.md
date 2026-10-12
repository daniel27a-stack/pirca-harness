# tasks/

One folder per card: `tasks/<CARD-ID>/`. Everything an agent needs to resume a card lives here,
and the folder is committed as the record of how the card was done.

| File | Written by | Content |
|---|---|---|
| `card.md` | orchestrator | Snapshot of the Trello card (title, labels, description, URL) |
| `task.json` | refinement (+ architect, prep) | Structured task data (schema below) |
| `progress.md` | every stage | Stage status table + log. **Source of truth for resuming** |
| `resolutions.md` | orchestrator | Answers from the user to blockers, in order |
| `criteria.md` | refinement (BA) | Need, scope, acceptance criteria (AC-n), out of scope, assumptions. **Approved by the user** before architect runs |
| `implementation.md` | architect | Approach, files, ordered steps per AC, **verification plan** (baseline + after) |
| `prep-report.md` | prep | Worktree, branch, baseline results |
| `baseline/` | prep | Raw baseline outputs (dependency trees, test results) |
| `coder-summary.md` | coder | What changed, files, commits |
| `qa-report.md` | qa | Results of the verification plan and one verdict per acceptance criterion |
| `docs-summary.md` | docs | What was documented |
| `metrics.json` | orchestrator | Tokens, model and time per stage run |
| `retrospective.md` | retrospective | What went wrong, cost analysis, proposed improvements |

## `task.json`

```json
{
  "task_id": "ARQ-12",
  "title": "Step 3: intTest and archTest source sets",
  "trello_card_id": "6acaad8d1f9ff103ef74f881",
  "repos": [
    {
      "name": "java-skeleton",
      "path": "/home/.../Desarrollo/java-skeleton",
      "worktree": "/home/.../Desarrollo/java-skeleton-ARQ-12",
      "branch": "feature/ARQ-12"
    }
  ],
  "scope": "One paragraph in English"
}
```

Acceptance criteria live in `criteria.md` only (single source of truth).

## `progress.md`

```markdown
# ARQ-12 progress

Status: in-progress | blocked | in-review | done

| Stage | Status | Attempts | Updated |
|---|---|---|---|
| refinement | done | 2 | 2026-10-11T23:10Z |
| criteria-approval | done | 2 | 2026-10-11T23:25Z |
| architect | blocked | 1 | ... |
| prep | pending | 0 | |
...

## Blocker
(only while blocked) stage, question(s) for the user, what is needed to continue

## Log
- 2026-10-11T23:25Z criteria-approval: approved on round 2 (user narrowed AC-3)
```

Stage status values: `pending`, `done`, `blocked`, `failed` (qa only).

## `metrics.json`

```json
{
  "task_id": "ARQ-12",
  "runs": [
    {
      "stage": "coder",
      "attempt": 1,
      "agent_id": "a1b2c3",
      "models": ["claude-sonnet-5"],
      "tokens": { "input": 0, "output": 0, "cache_read": 0, "cache_creation": 0, "total": 0 },
      "api_requests": 0,
      "tool_uses": 0,
      "started_at": "...",
      "ended_at": "...",
      "duration_s": 0,
      "status": "done"
    }
  ],
  "totals": { "tokens": 0, "duration_s": 0, "runs": 0 }
}
```

Each run's numbers come from `python3 scripts/agent_usage.py <agent-id>`, which reads the
subagent transcript, so they are measured, not estimated.
