# ARQ-32 retrospective

## Summary
Card "Pirca generator with only type, product and name" went from intake to merged PR (java-skeleton#6) in one attempt per stage after the single refinement block. Criteria were approved in round 1, QA passed all 27 ACs on attempt 1, and the PR merged with one commit and no review comments (nothing was corrected by the user in review). The defects are all in bookkeeping and tooling, not in the product.

## What went well
- Criteria approved in round 1 (resolutions.md has one question, Q1, answered "A" plus confirmation of A1-A6): the BA's assumption list worked.
- Zero rework: coder, qa and docs each ran once; QA evidence is broad (rejected flags with a control against the old image, 19 negative cases, generation plus build of variants).
- Coder compared a dependency baseline taken in prep.
- PR merged unchanged, so the diff the user saw matched coder/docs output.

## What went wrong (evidence)
1. Placeholders and non-standard state in agent-written files: refinement and architect have no Bash, so `<ts>` placeholders were left for the orchestrator; refinement also wrote Status "criteria-approval pending" (not a standard value) and left a Blocker section after Q1 was resolved.
2. Wrong timestamps in progress.md. metrics.json shows prep ended 01:40:47Z, but its row says 01:50Z; coder ended 01:48:16Z (row 01:48Z) so the table reads prep after coder. The "delivery" log line (01:54Z) precedes the docs line (01:55Z). Timestamps appear to have been guessed or filled in late instead of taken from `date`/metrics.
3. Trello: `cards update --desc` puts the description in the URL; the ~8.8KB criteria failed with HTTP 414 and were posted as a comment, leaving the card description with only a heading and pointer.
4. Architect had no Bash, so git state and `.idea` tracking were not checked and had to be deferred to prep/coder (progress.md log, architect line).
5. Coder left two pty test containers running (environment hygiene; QA/coder did not clean up).
6. The type menu shows descriptions that the card did not name (scope drift risk; it was covered by approved criteria but the origin of the wording is unclear).
7. Refinement attempt 1 spent 329k tokens (53 tool uses) only to block on a question the card could have answered; attempt 2 was cheap (58k).
8. Unverified observation: the PR file list contains both `ExampleTest.java.hbs` and `{{className}}Test.java.hbs` under java-library; I did not inspect whether one is a leftover. Worth a glance.

## Cost
| Stage | Attempts | Tokens | Duration (s) | Note |
|---|---|---|---|---|
| refinement | 2 | 329,133 + 58,295 = 387,428 | 76.9 + 26.9 | attempt 1 blocked |
| architect | 1 | 478,452 | 158.7 | 81 tool uses |
| prep | 1 | 188,267 | 58.6 | |
| coder | 1 | 1,447,541 | 439.3 | most expensive (38%) |
| qa | 1 | 1,248,604 | 290.2 | 33%; justified by breadth of checks |
| docs | 1 | 73,570 | 17.1 | verified only, no changes |
| Total | 7 runs | 3,823,862 | 1,067.7 | |

Coder and QA together are 70% of tokens, mostly cache reads from long sessions (28 and 25 requests); proportionate for a CLI rewrite with a many-variant matrix. Docs verified without change; cheap.

## Proposals
1. File: `.claude/skills/pirca-conventions/SKILL.md` ("Working inside pirca-harness"). Change: add "In progress.md write only the stage rows' `Status` values `pending|in-progress|done|blocked`; never invent other values; delete the `## Blocker` section when resolved." Effect: removes non-standard Status and stale Blocker.
2. File: orchestrator (`/run-card` command). Change: after each stage, replace every `<ts>` and set the row's Updated and the log timestamp from the `ended_at` in metrics.json (or `date -u`), never from memory. Add a final check: grep progress.md for `<ts>` and verify Updated times are monotonic. Effect: fixes out-of-order times.
3. File: `.claude/agents/refinement.md` and `architect.md`. Change: either grant read-only `Bash(git status:*, git ls-files:*, date:*)` or instruct them to list unchecked repo facts under "Verify in prep" explicitly. Effect: no placeholders; git state (e.g. `.idea`) checked at design time.
4. File: `.claude/agents/refinement.md`. Change: "Before blocking, collect ALL open questions in one pass, and list assumptions the user can confirm in bulk (as A1-A6 did)." Effect: avoids a 329k-token run that ends in a single question.
5. File: orchestrator Trello step (and any Trello helper skill). Change: when the description exceeds ~2KB, do not use `cards update --desc`; use the CLI's body/stdin option if it exists, otherwise put a heading and pointer in the description and the full text as a comment (what happened ad hoc here), written down as the standard procedure. Effect: no 414 failures, same outcome every time.
6. File: `.claude/agents/coder.md` and `qa.md`. Change: "Track every container/process you start (use `--rm` and a name prefix `arq<n>-`) and stop/remove them before finishing; report `docker ps` empty of your containers." Effect: no leftover pty containers.
7. File: `.claude/agents/refinement.md` (and the card template). Change: "Do not add user-visible text (menu labels, descriptions, messages) not named in the card; list any you need as an assumption for the user to approve." Effect: addresses menu descriptions appearing without being in the card.
