# repos/

One profile per target repository: `repos/<repo-name>.md`, where `<repo-name>` is the `name` of
the repo in `task.json`. A target repository carries only facts about itself (`CONTRIBUTING.md`);
its profile carries what agents need on top of that. The orchestrator passes the profile to
`architect`, `coder` and `qa`. A card whose repository has no profile stops before `architect`:
profiles are written with the user, not by agents.

Sections, in this order:

| Section | Content |
|---|---|
| `## Kind` | What kind of repository it is, in one or two lines |
| `## Edit` | What agents change in it |
| `## Do not touch` | What agents never change |
| `## Verify` | How a change is verified (usually a pointer to its `CONTRIBUTING.md`) |
| `## Skills` | Harness skills to read before working on it, beyond the preloaded ones (`.claude/skills/<name>/SKILL.md`) |
| `## QA commands` | One command prefix per bullet, in backticks. `qa` runs commands that start with these without a permission prompt (`scripts/allow_qa_commands.py`); anything else still asks |
