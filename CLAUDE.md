# pirca-harness

This repository holds the agentic workflow that executes pirca cards end to end.
It never contains product code: it operates on *target repositories* (for example
`../java-skeleton`) through git worktrees.

## How work flows

```
/run-card ARQ-n   (main session = orchestrator)
  ba (criteria.md) → USER APPROVES CRITERIA → architect (implementation.md)
  → prep → coder → qa → docs → push + PR → card to "En revisión"
  after the user merges:  /run-card ARQ-n  → retrospective → record PR → card to "Hecho"
```

- The user states the **need** in the card (section `Necesidad`). The BA (`ba` agent) turns it into
  acceptance criteria, and **the user approves them** before any design or code: they define the scope.
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
- Never report what was not run, and never invent scope or decisions (see `pirca-stage-protocol`).

## Where things live

Each piece of knowledge lives in one place; agents and the orchestrator use it, never copy it.

| Topic | Lives in |
|---|---|
| Architecture and working conventions | skill `pirca-conventions` |
| What every stage reads, records, reports and how it blocks | skill `pirca-stage-protocol` |
| Board (today Trello): cards, lists, ids, comments | skill `pirca-board` |
| Code hosting (today GitHub): push, PRs; commit conventions | skill `pirca-forge` |
| Card state (`progress.json` → `progress.md`) | `scripts/progress.py` (the only writer) |
| Measured cost per stage | `scripts/agent_usage.py` |
