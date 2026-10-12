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
| 2026-10-11 | The user writes the **need**; the BA agent writes `criteria.md`; **the user approves the criteria** before the architect runs. The architect writes `implementation.md`; `coder` receives both | Criteria define the scope, so they are a contractual decision: a wrong criterion would propagate to design, code and QA. Separating what (criteria) from how (implementation) keeps each agent's job clear |
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

## 2026-10-11 — ARQ-11: Need-based intake, criteria approval gate, fixes from the first run

**What:**
- Cards carry a `Necesidad` section; `refinement` acts as BA and writes `criteria.md`; the user
  approves the criteria before `architect` runs; `architect` writes `implementation.md`;
  `coder` and `qa` work from both.
- `architect` gets `WebFetch` (Maven Central and the Gradle plugin portal only) and must pin exact
  versions; placeholders such as `<1.4.x>` are not allowed.
- Timestamps: agents never invent them (`date -u` or the `<ts>` placeholder, replaced by the
  orchestrator after each stage).
- Questions to the user follow a fixed format (`❓ Pregunta`, numbered options with a recommended
  one, `✅ Responde` with one copy-ready block).
- `pirca-conventions` gains the ecosystem view and the layer convention (ARQ-25).

**Why (first, aborted run of ARQ-12):**
- `architect` had no way to look up versions and left placeholders, pushing a design decision to `coder`.
- Agents without a shell wrote made-up timestamps (`2026-10-11T00:00Z`) in `progress.md`.
- `architect` assumed hexagonal package names that pirca had never decided; the orchestrator
  correctly stopped and asked, which produced ARQ-25.
- The user pasted the wrong block of an answer because several versions had been offered.
- The harness was modified while the run was in progress, so the session mixed the old and new
  flow. Rule since then: never change the harness while a card is running.

**Verification:** run leftovers removed (`tasks/ARQ-12/`, empty agent memory); ARQ-12 reset to
Backlog with a `Necesidad` section; `settings.json` valid. The flow itself is verified by the next
ARQ-12 run.
