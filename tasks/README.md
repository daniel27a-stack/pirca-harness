# tasks/

One folder per card: `tasks/<CARD-ID>/`. Everything an agent needs to resume a card lives here.
The folders stay local (`.gitignore`) and are never pushed; the folders of cards finished before
ARQ-50 remain in the repository as history.

| File | Written by | Content |
|---|---|---|
| `card.md` | orchestrator (pirca-board `snapshot`) | Snapshot of the card (title, list, description, URL) |
| `task.json` | ba (+ architect, prep) | Structured task data (schema below) |
| `progress.json` | `scripts/progress.py` only | Card and stage state, blocker, log. **Source of truth for resuming** |
| `progress.md` | `scripts/progress.py` only | Generated from `progress.json` for people to read. Never edited by hand |
| `blocker-<stage>.md` | the blocked stage | All open questions, with options, recommendation and assumptions |
| `resolutions.md` | orchestrator | Answers from the user to blockers, in order |
| `criteria.md` | ba | Need, scope, acceptance criteria (AC-n), out of scope, decisions. Written by the BA on its own; also posted on the card |
| `implementation.md` | architect | Approach, files, ordered steps per AC, **verification plan** (baseline + after) |
| `prep-report.md` | prep | Worktree, branch, baseline results |
| `baseline/` | prep | Raw baseline outputs (dependency trees, test results) |
| `coder-summary.md` | coder | What changed, files, commits |
| `qa-report.md` | qa | Results of the verification plan and one verdict per acceptance criterion |
| `docs-summary.md` | docs | What was documented |
| `metrics.json` | `scripts/agent_usage.py --append` | Full measured result of every stage run, and totals |
| `retrospective.md` | retrospective | What went wrong, cost analysis, proposed improvements |
| `pr-body.md` | orchestrator | Body of the PR opened with pirca-forge |
| `aborted/<UTC time>/` | orchestrator | Everything from a run the user restarted from scratch, archived as it was. Its branch is renamed `aborted/<CARD-ID>-<UTC time>` |

## `task.json`

```json
{
  "task_id": "ARQ-12",
  "title": "Step 3: intTest and archTest source sets",
  "board_card_id": "6acaad8d1f9ff103ef74f881",
  "repos": [
    {
      "name": "java-skeleton",
      "path": "/home/.../Desarrollo/java-skeleton",
      "worktree": "/home/.../Desarrollo/java-skeleton-ARQ-12",
      "branch": "feature/ARQ-12"
    }
  ],
  "scope": "One paragraph in English",
  "path": "full"
}
```

Each repo's `name` is also the name of its profile, `repos/<name>.md`.

`path` is `full` or `short`, chosen by `ba`. In the short path, `architect`, `prep` and `docs` are
skipped and `coder` does their work.

Acceptance criteria live in `criteria.md` only (single source of truth).

## `progress.json` and `progress.md`

Written only by `scripts/progress.py` (see its `--help`). Timestamps come from the system clock in
UTC; nobody writes them by hand.

```
python3 scripts/progress.py init  ARQ-12                      # orchestrator, at intake
python3 scripts/progress.py start ARQ-12 coder                # orchestrator, before each attempt
python3 scripts/progress.py skip  ARQ-12 architect prep docs --note "short path"   # orchestrator
python3 scripts/progress.py set   ARQ-12 coder done --note "commit dd6cde0, tests green"   # the stage
python3 scripts/progress.py set   ARQ-12 ba blocked --note "2 questions" --blocker-file tasks/ARQ-12/blocker-ba.md
python3 scripts/progress.py card  ARQ-12 in-review --pr <url> # orchestrator
python3 scripts/progress.py check ARQ-12                      # valid values, ordered log, no hand edits
```

- Card status: `in-progress`, `blocked`, `in-review`, `done`.
- Stages, in order: `ba`, `architect`, `prep`, `coder`, `qa`, `docs`,
  `retrospective`. Stage status: `pending`, `in-progress`, `done`, `blocked`, `failed` (qa only),
  `skipped` (`architect`, `prep` and `docs` in the short path).
- A stage set to `blocked` must carry its questions; setting that stage to `done` clears the blocker.
- Cards recorded before ARQ-40 have only a hand-written `progress.md` (and the stage `refinement`);
  they are history and are not migrated.

## `metrics.json`

```json
{
  "task_id": "ARQ-12",
  "runs": [
    {
      "stage": "coder",
      "attempt": 1,
      "agent_id": "a1b2c3",
      "claude_code_version": "2.1.307",
      "output_tokens_reliable": true,
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
  "totals": { "tokens": 0, "output_tokens": 0, "duration_s": 0, "runs": 0 }
}
```

Each run is written by `python3 scripts/agent_usage.py <agent-id> --append <metrics.json> --stage
<stage> --attempt <n> --status <status>`, which reads the subagent transcript and stores its whole
result, so the numbers are measured, not estimated, and nothing is left out. Output tokens are reliable only for
Claude Code 2.1.307 or later (`output_tokens_reliable`); the metrics of ARQ-12, ARQ-28 and ARQ-32
were recorded with 2.1.296 and 2.1.300, under-count output tokens and cannot be recalculated:
those transcripts never stored the final output.
