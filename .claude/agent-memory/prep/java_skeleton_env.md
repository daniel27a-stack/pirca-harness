---
name: java-skeleton-prep-environment
description: Facts about the java-skeleton environment that prep needs (main checkout state, email config, baseline commands, docker image tag)
metadata:
  type: project
---

java-skeleton main checkout is often behind origin/main (ARQ-15: checked out `a6a8ceb`, origin/main `e9a4feb`). Prep always branches from `origin/main`, never from the local checkout.

**Why:** the local main checkout is not kept current; basing a worktree on it would silently miss merged cards.

**How to apply:** after `git fetch origin`, run `git worktree add ... origin/main`. Do not pull or reset the main checkout.

The main checkout has a local `user.email` = `pirca.dev@gmail.com` already, so `git config user.email` inside a worktree writes the same value into the shared `.git/config`. The global email is the user's personal one; do not change it.

The main checkout has an untracked `.idea/` directory. It is not part of any card; leave it alone.

Baseline docker image tag used on ARQ-15: `java-skeleton:base`. Generated projects go in `mktemp -d` (under /tmp), and their path is recorded in `tasks/<CARD>/baseline/workdir.txt`.

Host `java` is 21 on this machine; the templates' Gradle build passed on it (ARQ-15 baseline).
