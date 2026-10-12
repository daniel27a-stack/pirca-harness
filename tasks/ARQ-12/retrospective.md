# ARQ-12 retrospective

## Summary
Added `intTest` and `archTest` suites (plus WireMock in spring-gradle and a general ArchUnit layer
suite) to the 3 java-skeleton templates. 15 AC, all met by QA on attempt 1. PR #3 squash-merged
with no review comments and no extra commits (2 commits: coder, docs). Total 2.49M tokens, ~14.5 min
of agent time (7 runs, no retries after refinement).

## What went well
- No QA failures, no coder retries, no blockers in `progress.md`; the PR was merged unchanged.
- Baseline captured in prep made "main dependencies unchanged" (AC-11) a checkable claim
  (classpaths byte-identical in 4 variants).
- QA ran control tests (violations that must fail, empty-layer exclusion, reversed task order),
  as the conventions ask.
- The one real design question (unknown-layer GradleException) was escalated and resolved with a
  single user answer.

## What went wrong
1. Criteria needed 2 rounds. Round 1 corrections (resolutions.md): a missing criterion (test runs
   before intTest/archTest), an over-specified tag annotation in AC-6, and an unneeded sentence in
   AC-3. The first is a user addition (not a BA defect); AC-6 and AC-3 were BA over-specification
   (implementation choice and an unverifiable claim in criteria).
2. `progress.md` log is out of chronological order: "criteria-approval approved 00:48Z" is logged
   after the architect 00:52Z line, and the table says criteria-approval attempts 2 / approval at 00:48
   while the architect run started 00:48:40. Timestamps came from different writers; log order is
   misleading for resuming.
3. Commit attribution inconsistency: coder commit is `Claude Sonnet 5.5`, docs commit is
   `Claude Sonnet` (different Co-Authored-By name/ email-less form of the model).
4. Minor plan/reality drift: plan note said spring archTest runs 9 tests, actual 6 (QA noted it,
   non-blocking). README table alignment cosmetic issue noted by QA and not fixed (docs reported
   "aligned" at 01:08).
5. Docs commit message is only `ARQ-12: Update DEVLOG` although it also changed READMEs/templates
   READMEs (README +18, templates README +26 each).

## Cost
| Stage | Attempt | Tokens | Duration | Notes |
|---|---|---|---|---|
| refinement | 1 | 136,334 | 32s | |
| refinement | 2 | 88,269 | 21s | caused by user corrections |
| architect | 1 | 617,714 | 218s | 55 tool uses, 17k output; justified (pinned versions, design) |
| prep | 1 | 271,003 | 119s | baseline for 4 variants |
| coder | 1 | 692,568 | 217s | most tokens; justified, 4 variants |
| qa | 1 | 555,563 | 228s | slowest; justified by controls and regenerating variants |
| docs | 1 | 132,203 | 30s | |
| Total | | 2,493,654 | 865s | |

Cache reads dominate (>90% of tokens); output is small. Most expensive: coder, then architect and
QA, all proportionate to a 3-template change verified in 4 variants. Orchestrator time (user waits)
is not in metrics.json: wall clock card was ~27 min (00:41 to 01:08).

## Proposals
1. `.claude/agents/refinement.md`: add "Criteria state observable behaviour only. Do not prescribe
   annotations, libraries or mechanisms; leave those to the architect. Do not add sentences that
   the criteria do not verify." Effect: avoids AC-6/AC-3 type corrections in round 1.
2. `.claude/agents/refinement.md`: add a checklist item "if the need mentions several tasks/suites,
   ask whether execution order matters and cover it with a criterion". Effect: the AC-15 class of
   omission is caught before the user sees the draft. (Judgement call: it was a user addition,
   low priority.)
3. `.claude/commands/run-card.md` (orchestrator): when appending to `progress.md` log, insert in
   chronological order or use the real `date -u` at write time, and update the table row at the same
   time. Effect: log and table consistent for resuming.
4. `.claude/agents/docs.md` and `coder.md`: use the exact Co-Authored-By line from the session's
   attribution reminder (or one fixed string in `pirca-conventions`), and require the docs commit
   message to name all areas touched (e.g. `ARQ-n: Update DEVLOG and READMEs`). Effect: uniform
   history.
5. `.claude/agents/architect.md`: when the plan states expected counts (e.g. "9 archTests"), state
   them per default configuration, or omit them. Effect: no QA note on drift.
6. `.claude/agents/qa.md`: cosmetic findings that are cheap to fix (README alignment) should be
   reported to the orchestrator as "fix in docs" instead of left as a note, so PRs go out clean.
