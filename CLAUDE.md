# pirca-harness

This repository holds the agentic workflow that executes pirca cards end to end.
It never contains product code: it operates on *target repositories* (for example
`../java-skeleton`) through git worktrees.

## How work flows

```
/run-card ARQ-n   (main session = orchestrator)
  refinement → architect → prep → coder → qa → docs → push + PR → card to "En revisión"
  after the user merges:  /run-card ARQ-n  → retrospective → record PR → card to "Hecho"
```

- Architecture and business decisions are made **in conversation with the user**.
  Agents only execute what is already decided.
- When an agent hits something undecided it **stops** and reports it. The orchestrator
  brings it to the user and, once resolved, re-runs **the same stage**.
- All state lives in `tasks/<CARD-ID>/` (see `tasks/README.md`), so a card can be
  resumed in a later session.

## Non-negotiable rules

- Everything written inside a repository is in **English** (code, comments, docs, commits).
  Conversation with the user and Trello content may be in Spanish.
- Branches are named exactly `feature/<CARD-ID>` (e.g. `feature/ARQ-12`). Commits and PR titles
  start with the card ID.
- **Never push to `main`** of any repository. Changes reach `main` only through a PR that the
  user merges (squash). A hook enforces this.
- Never report something as done, passing or verified without having run it and seen the output.
- Never invent scope, acceptance criteria or design decisions. Missing information is a blocker.

## External tools

- Trello: `trello` CLI (board `Pirca`, id `6acaad73f66ba8b8e05028ab`). Lists:
  - Decisiones pendientes `6acaad73e4f33371281d313b`
  - Backlog `6acaad744a43ff3996630e87`
  - En curso `6acaad741c64496dc010018d`
  - En revisión `6acc12e157a0d4c2f0cbb377`
  - Hecho `6acaad76706ac9f975335df4`
- GitHub: `gh` CLI, owner `daniel27a-stack`.
- Commit author email in pirca repos: `pirca.dev@gmail.com` (set per repo, never globally).
