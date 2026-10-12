# pirca-harness

Agentic workflow that executes pirca architecture cards (`ARQ-n`) end to end:
from a Trello card to a reviewable pull request in the target repository.

## Usage

Start Claude Code **inside this repository** (agents, the command and hooks are project-scoped),
next to the target repositories:

```
~/Documentos/Desarrollo/
├── pirca-harness/     ← run `claude` here
└── java-skeleton/     ← target repository (worktrees are created next to it)
```

```
/run-card ARQ-12     # run or resume a card
```

The card must have a `Necesidad` section in Trello: the BA agent turns it into acceptance
criteria and the flow waits for your approval before designing anything. See `CLAUDE.md` for the flow
and rules, `tasks/README.md` for the files each card produces, and `DEVLOG.md` for decisions.
