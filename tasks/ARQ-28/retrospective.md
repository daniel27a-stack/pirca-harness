# ARQ-28 retrospective

## Summary
Card: add a context file to java-skeleton for agents. The flow ran cleanly (no blockers, no QA retries, every stage attempt 1 except refinement = 4), PR #4 merged (squash) 2026-10-13T00:12Z. But the **delivered artifact differs materially from the approved criteria**: in review the user (commit d5d8b5a, ~2h after the PR opened) renamed `CLAUDE.md` to `CONTRIBUTING.md`, replaced the "Scope for agents" section with "Making a change", moved agent-specific rules to pirca-harness, and fixed the README/DEVLOG rule. QA verified 9/9 AC, yet AC-1/AC-8 were themselves the wrong thing. The defect is upstream of the code: the need was under-decided before criteria were written.

## What went well
- No blockers, no QA failures, no coder retries; the whole run took 391 s of agent time.
- QA was strong: ran the CLAUDE.md steps literally, built all 4 variants, compared sha256 against the prep baseline, ran a control for AC-3(d).
- Refinement attempts 2-4 were fast (21-36 s) and verified claims against bin/cli.js.
- Round 3 was a genuine contradiction caught by refinement (AC-9 vs docs-stage DEVLOG entry) and surfaced as a numbered question with a recommendation.

## What went wrong (evidence)
1. **Four criteria rounds, then still reworked in review.** resolutions.md: round 1 (AC-3/4/5 + new "Scope for agents" AC-8), round 2 (AC-3(d) example inverted, AC-8 add README/DEVLOG), round 3 (AC-9 vs DEVLOG), round 4 approval. Then in review the user dropped the file name and the AC-8 section entirely. Root cause: the card did not decide *file name / audience* (agents-only CLAUDE.md vs human CONTRIBUTING.md) nor *where agent rules live* (target repo vs pirca-harness). These are architecture decisions; the BA should have asked, not assumed.
2. **Inverted example in AC-3(d)** (round 2): the BA wrote the opposite of the real behaviour of publish.gradle.hbs. Attempt 1 evidently did not verify the example against the template; attempt 3 did (cli.js L124).
3. **Wrong rule about README** (round 2, user-requested "README.md and DEVLOG.md updated in every change") was corrected in review: README only when usage/commands/flags change. The BA transcribed it literally without checking README conventions; AC-9 / the architect / QA then enforced a rule that was later reversed. QA cannot catch a wrong criterion.
4. **Circularity in AC-9 vs docs stage** (round 3): a card-level "only CLAUDE.md changes" criterion collides with the standing docs stage. Known pattern, not in the BA instructions.
5. **Co-Authored-By trailers inconsistent**: first two commits say "Claude Sonnet", the review commit "Claude Opus 5.5", while the harness reminder specifies "Claude Sonnet 5.5". Minor, but trailers do not match the model that did the work.
6. **Metrics gaps**: coder/qa/docs show output tokens 280/80/80 despite 8-20 tool calls and real output (qa-report, commit). Output tokens look under-reported (likely last streamed chunk only), so cost per stage is not trustworthy. The user's review-time rework (done in the main session) is not in metrics.json at all.

## Cost
| Stage | Attempts | Tokens (total) | Duration |
|---|---|---|---|
| refinement | 4 | 128,101 + 109,205 + 91,988 + 130,374 = 459,668 | 114.7 s |
| architect | 1 | 200,029 | 72.6 s |
| prep | 1 | 117,804 | 59.1 s |
| coder | 1 | 104,970 | 23.0 s |
| qa | 1 | 179,501 | 101.9 s |
| docs | 1 | 91,869 | 20.0 s |
| **Total** | 9 runs | **1,153,841** | **391.3 s** |

Refinement was the most expensive stage (40% of tokens), and mostly avoidable: 3 of 4 runs were rework from under-specified need and the user's own corrections. Architect (200k, 9k output) for a single 71-line markdown file is heavy; implementation.md is 13 KB for a one-file change. QA (180k) was justified. Cost is dominated by cache reads (~825k of 1.15M); each run re-reads the full context.

## Proposals
1. **`.claude/agents/refinement.md` - ask about undecided placement/naming before drafting.** Add: "For any card that creates a new file or document, if the Necesidad does not state the file name, audience (humans / agents / both) and where it lives (target repo vs pirca-harness), list them in `## Blocker` as numbered questions with options and a recommendation instead of choosing." Effect: this card would have decided CONTRIBUTING.md vs CLAUDE.md in round 0 instead of in review.
2. **`.claude/agents/refinement.md` - verify examples and user-requested rules.** Add: "Every example in a criterion must be checked against the source (file/line) before writing it. When the user asks for a process rule (e.g. when README/DEVLOG are updated), check it against the repo's README/DEVLOG conventions and flag conflicts." Effect: avoids the inverted AC-3(d) and the wrong README rule.
3. **`.claude/agents/refinement.md` - scope-limit criterion template.** Add: "A 'nothing else changes' criterion must list the docs-stage DEVLOG entry as allowed." Effect: removes round 3.
4. **`tasks/README.md` / card template - Necesidad prompts.** Add optional lines "Name/format of deliverable", "Audience", "Location (repo)". Effect: need is decided before refinement.
5. **Convention (`pirca-conventions` skill) - where agent instructions live.** Record the decision taken in this review: target repositories carry only repository facts (CONTRIBUTING.md); agent-specific rules live in pirca-harness. Also: README changes only when usage/commands/flags change; DEVLOG gets an entry in every change. Effect: future cards and the BA/docs agents start from the decided rule.
6. **`.claude/agents/architect.md` - proportionality.** Add: "For a change of one new file, implementation.md stays under ~3 KB: files, steps, verification commands; do not restate criteria." Effect: cuts ~100k tokens on small cards.
7. **Metrics script (harness tooling) - investigate output-token undercount and include main-session review work** (or add a `review` run entry when the user asks for post-PR changes). Effect: reliable cost and visibility of review rework, the strongest signal of criteria quality.
8. **Commit trailer**: have `docs`/`coder` use the trailer from the session reminder verbatim, and note in the orchestrator that review fixes made in the main session carry the actual model. Effect: consistent attribution.

No agent, skill, setting or target repo was modified by this retrospective.
