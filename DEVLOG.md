# pirca-harness devlog

Log of changes and decisions for the harness. Each entry states **what** changed, **why**,
and **how it was verified**.

## Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-11 | Separate repository that operates on target repos through git worktrees | Agents and their rules live in one place; target repos stay free of harness files |
| 2026-10-11 | Orchestrator is the `/run-card` command in the main session, not a subagent | Subagents have no `AskUserQuestion`; blockers must come back to the session that talks to the user |
| 2026-10-11 | Rules enforced by mechanism where possible (hooks, tool scopes, `maxTurns`) | Instructions alone can be ignored; a hook that exits 2 cannot |
| 2026-10-11 | All agents on Sonnet | Start cheap; switch a stage to a stronger model only if `metrics.json` and retrospectives show the need |
| 2026-10-11 | State in `tasks/<CARD-ID>/progress.md`, measured cost in `metrics.json`, both committed | Resume after blockers across sessions; keep a record of how each card was done and what it cost |
| 2026-10-11 | Acceptance criteria are mandatory on every card | They define the scope; without them the flow stops before refinement |
| 2026-10-11 | QA failure → one automatic retry of `coder`, then stop | Cheap fixes happen alone; repeated failures need a human |
| 2026-10-11 | Retrospective runs after the merge and only proposes | The user's review changes are the best signal; changing agents is a user decision |
| 2026-10-11 | No agent teams or dynamic workflows yet | The flow is sequential and needs user input mid-run, which workflows do not allow |

---

## 2026-10-11 — ARQ-11: First version of the harness

**What:** `CLAUDE.md`, `pirca-conventions` skill (preloaded into every agent), seven agents
(`refinement`, `architect`, `prep`, `coder`, `qa`, `docs`, `retrospective`), the `/run-card`
orchestrator, `tasks/README.md` (file formats), and three scripts:
- `block_push_main.py` — `PreToolUse` hook that blocks any `git push` to main/master.
- `guard_write_scope.py` — `PreToolUse` hook for agents that must not change code
  (`refinement`, `architect`, `qa`, `retrospective`): writes allowed only under `tasks/`.
- `agent_usage.py` — measured tokens, model and duration of a subagent run from its transcript.

**Verification so far:**
- `block_push_main.py`: blocks `push origin main`, `src:main`, `HEAD:refs/heads/main`, `-f +main`,
  `git -C <repo> push ... :master` and a bare `git push` on main; allows feature branches,
  a branch named `feature/main-fix`, non-push commands and a bare push on a feature branch.
- `guard_write_scope.py`: allows `tasks/ARQ-12/qa-report.md`, blocks a target repo's `build.gradle`.
- `agent_usage.py`: on a real subagent transcript, reports model, 4 API requests (deduplicated),
  tokens by type and 82.4 s duration.
- Pending: end-to-end run of ARQ-12 (acceptance criterion 10 of ARQ-11).
