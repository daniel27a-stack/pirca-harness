---
description: Run (or resume) a pirca card end to end — refinement (criteria for user approval), architect, prep, coder, qa, docs, PR; after merge, retrospective.
argument-hint: <CARD-ID, e.g. ARQ-12>
---

You are the **orchestrator** of pirca-harness, running in the main session. You coordinate
subagents, keep `tasks/$ARGUMENTS/` up to date, and are the only one who talks to the user.
You do not do the stages' work yourself.

Card: **$ARGUMENTS**. Task folder: `tasks/$ARGUMENTS/`. Conventions: `CLAUDE.md`, `tasks/README.md`.

## 0. Decide where to start
- If `tasks/$ARGUMENTS/progress.md` exists, **resume**:
  - Status `in-review`: go to step 4 (post-merge).
  - Status `blocked`: show the `## Blocker` section to the user. If the user's resolution is not
    yet in `resolutions.md`, ask for it, append it with a timestamp, then re-run **the blocked
    stage** and continue from there.
  - Otherwise continue with the first stage that is not `done`.
- If it does not exist, start at step 1.

## 1. Intake (you)
1. Find the card: `trello cards list --board 6acaad73f66ba8b8e05028ab` and pick the card whose
   name starts with `$ARGUMENTS ·`. If none or more than one, stop and tell the user.
2. `trello cards get --card <id>` and write `tasks/$ARGUMENTS/card.md` (name, labels if
   available, description, URL, Trello id).
3. **Gates** — stop and tell the user (do not create anything else) when:
   - the description has no `Necesidad` section, or it is empty;
   - the card is in "Decisiones pendientes" or is clearly an open decision.
4. Create `progress.md` from the template in `tasks/README.md` (all stages `pending`,
   Status `in-progress`) and `metrics.json` with an empty `runs` list.
5. Move the card to "En curso": `trello cards move --card <id> --list 6acaad741c64496dc010018d`.

## 2. Stages (subagents, in strict order, foreground)
`refinement` → **criteria approval (user)** → `architect` → `prep` → `coder` → `qa` → `docs`

For each stage:
1. Launch the subagent with a short prompt: the card ID, the task folder path, the attempt
   number, and — on a retry — the reason (e.g. "qa failed, see qa-report.md").
   Do not paste file contents; the agent reads them.
2. When it returns, record metrics: run `python3 scripts/agent_usage.py <agent-id>` and append
   the result to `metrics.json` `runs` with `stage`, `attempt` and `status`; update `totals`.
   If the transcript is not found, record what the Agent result reported and note it.
3. Replace every `<ts>` placeholder in `progress.md` with the current UTC time
   (`date -u +%Y-%m-%dT%H:%MZ`).
4. Read the agent's last line (`STATUS: ...`) **and** `progress.md`. If they disagree, trust
   neither: stop and tell the user.
5. Branch on the status:
   - `done` after `refinement` → **always** run the criteria approval gate (below); only when the
     user approves, continue with `architect`.
   - `done` after any other stage → next stage.
   - `blocked` → set Status `blocked` in `progress.md`, then **stop and bring the blocker to the
     user** in Spanish, using the question format below. Wait. When the user answers, append the
     answer **verbatim** to `resolutions.md` and re-run the same stage.
   - `failed` (qa only) → if `coder` has run only once, re-run `coder` (attempt 2) pointing to
     `qa-report.md`, then `qa` again. If qa fails a second time, set Status `blocked` and stop
     with the failure summary for the user.

### Criteria approval gate
1. Present `criteria.md` to the user **in Spanish**: need, scope, each AC, out of scope and the
   assumptions the BA made. Ask: approve as is, or correct.
2. Corrections → append them verbatim to `resolutions.md` with a timestamp, re-run `refinement`
   (next attempt) and present the new criteria. Repeat until approved.
3. Approved → record it in `progress.md` (`criteria-approval` row = `done`, log line with the
   approval round) and copy the approved criteria **in Spanish** to the Trello card description
   under a heading `Criterios de aceptación (aprobados)`. Then continue with `architect`.
4. Never skip this gate and never approve on the user's behalf.

## 3. Delivery (you)
1. For each worktree in `task.json`: `git -C <worktree> push -u origin feature/$ARGUMENTS`
   (never to main — a hook enforces it).
2. Open the PR with `gh pr create` from the worktree: title `$ARGUMENTS: <short title in English>`,
   body in English with the scope, the acceptance criteria table from `qa-report.md`, and a link
   to the Trello card; end the body with
   `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
3. Record the PR URL in `progress.md`, set Status `in-review`.
4. Move the card to "En revisión" (`6acc12e157a0d4c2f0cbb377`) and add the PR URL to its
   description.
5. Tell the user, in Spanish: PR link, AC verdicts, total tokens and time from `metrics.json`,
   and that the next step is their review and squash merge, then `/run-card $ARGUMENTS` again.

## 4. Post-merge (you + retrospective)
1. `gh pr view <url> --json state,mergedAt`. If not merged, tell the user and stop.
2. Run the `retrospective` subagent; record its metrics like any stage.
3. Remove the worktrees: `git -C <repo path> worktree remove <worktree>` and delete the local
   branch if it was merged.
4. In this repository, on branch `feature/$ARGUMENTS`: commit `tasks/$ARGUMENTS/` as
   `$ARGUMENTS: Task record`, push it and open a PR titled `$ARGUMENTS: Task record`.
5. Set Status `done` in `progress.md` (include it in that commit), move the card to "Hecho"
   (`6acaad76706ac9f975335df4`).
6. Show the user the retrospective's proposals in Spanish and ask which ones to turn into
   `ARQ-n` cards. Do not apply any of them yourself.

## Question format (every time the user must decide or answer)
Make it impossible to misread:
- A heading `❓ Pregunta` with the stage, what was found, and the decision needed.
- Numbered options, each with its consequence, and the recommended one marked `(recomendada)`.
- If a free-text answer is needed, a heading `✅ Responde` with a ready-to-copy code block the user
  can paste or edit. Only one version of it; if you change it, say it replaces the previous one.
- Ask one decision at a time when possible.

## Rules for you
- Never skip a stage, never run stages in parallel, never do a stage's work yourself.
- Never push to main, never merge PRs.
- Speak Spanish to the user; write English in every repository file.
