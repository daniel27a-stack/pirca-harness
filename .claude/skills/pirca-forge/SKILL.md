---
name: pirca-forge
description: How pirca-harness works with code hosting (today GitHub) and the pirca commit conventions — push a feature branch, open a PR, read a PR's state and review data, write commits. Use it instead of calling git push or the hosting CLI directly.
---

# pirca forge

All hosting operations go through `scripts/forge.py` in this skill. Never call the hosting CLI
(`gh`) directly.

```
python3 .claude/skills/pirca-forge/scripts/forge.py push      <repo-path> feature/<CARD-ID>
python3 .claude/skills/pirca-forge/scripts/forge.py pr-create <repo-path> --title "<CARD-ID>: <title>" --body-file <path>
python3 .claude/skills/pirca-forge/scripts/forge.py pr-state  <pr-url>    # {"state", "merged", "merged_at"}
python3 .claude/skills/pirca-forge/scripts/forge.py pr-review <pr-url>    # title, body, reviews, comments, commits, files
```

Pushing to `main` is impossible: the script refuses it and a harness hook blocks it too. Changes
reach `main` only through a PR that the user merges (squash).

## Commit conventions (every pirca repository)
- Author email: `pirca.dev@gmail.com`, configured **per repository** (`git config user.email`),
  never globally. Check it before the first commit in a worktree.
- Branch: `feature/<CARD-ID>`. Message: first line `<CARD-ID>: <imperative summary>` in English,
  optional body with bullet points.
- Last line, naming the model that actually wrote the change:
  - agents of the flow (they run on Sonnet): `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`
  - work done in conversation with the user in the main session: the model of that session
    (e.g. `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).
- PR title `<CARD-ID>: <title>`; PR body in English, ending with
  `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
