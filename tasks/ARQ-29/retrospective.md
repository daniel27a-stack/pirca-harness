# ARQ-29 retrospective

## Summary
Card: inverse naming rules in `archTest` of `java-skeleton` (a `*Controller/*Service/*Repository/*Client`
outside its layer package must fail). Merged as PR #7 (squash) with no review comments and no
requested changes: the final PR contains exactly the 4 template files plus DEVLOG.md that `coder` and
`docs` produced. 10 ACs, all met in QA on the first attempt. Only stage retried: `ba` (3 attempts:
1 blocked on questions, 1 criteria round with 3 user corrections). Total 1,492,532 tokens, 569 s.

## What went well
- Zero blockers after criteria approval; coder, qa and docs each ran once; no QA failure.
- QA verified with real scenarios (stray class per suffix, nested class, `UserServiceImpl`, excluded
  layers, both variants) and a baseline captured in prep proved the gap existed ("stray controller passes").
- The "Fix in docs" path (qa-report) worked: AC-10 marked "met for now" and DEVLOG delegated to docs;
  the PR body states the post-docs diff honestly.
- User review needed no PR changes: the approval of criteria was where scope was shaped.

## What went wrong (evidence)
1. BA attempt 1 blocked with 6 questions (resolutions.md, 23:46Z). Answers 2-5 were "yes / same as the
   existing rules" (top-level only, suffix match, sub-packages, same tag): derivable from the existing
   `ArchitectureTest` and `pirca-conventions` (layers, tags). Only #1 (tag/defaults effect) and #6
   (which docs) needed the user. Cost: 224k tokens, the most expensive `ba` run, plus a round trip.
2. Criteria approval round 1 needed 3 corrections (resolutions.md, 23:49Z), all about criteria form:
   - AC-7 contained an unverifiable half ("never pass silently on an empty set");
   - AC-2 described the how rather than the observable outcome;
   - AC-8 asked to verify "all variants" instead of the 2 variants defined in `java-skeleton/CONTRIBUTING.md`.
   The BA wrote criteria that were not checkable or were broader than the repo's own verification contract.
   This cost a third `ba` run (116k).
3. `ba` added assumption A6 "not requested" to criteria; fine and disclosed, but shows the BA records
   architect-owned decisions inside criteria text.
4. `metrics.json` has no API request count or tool-use count per run, so cost causes below are inferred
   from artifacts only, not measured. No run has `output_tokens_reliable: false` (field absent), so
   output tokens are taken as reliable.

## Cost per stage run
| Stage | Att. | Status | Input | Output | Cache read | Cache creation | Total | Time |
|---|---|---|---|---|---|---|---|---|
| ba | 1 | blocked | 20 | 3,995 | 191,362 | 28,880 | 224,257 | 50 s |
| ba | 2 | done | 14 | 3,552 | 120,323 | 12,427 | 136,316 | 34 s |
| ba | 3 | done | 12 | 2,609 | 100,819 | 12,361 | 115,801 | 30 s |
| architect | 1 | done | 14 | 6,982 | 137,514 | 32,004 | 176,514 | 60 s |
| prep | 1 | done | 14 | 3,497 | 125,357 | 24,962 | 153,830 | 78 s |
| coder | 1 | done | 24 | 7,031 | 295,509 | 30,625 | 333,189 | 152 s |
| qa | 1 | done | 18 | 5,817 | 212,289 | 30,304 | 248,428 | 136 s |
| docs | 1 | done | 10 | 2,510 | 80,153 | 21,524 | 104,197 | 30 s |
| Total | | | 126 | 35,993 | 1,263,326 | 193,087 | 1,492,532 | 569 s |

Cache read is 85% of tokens (cheap); output is 2.4%; cache creation 13%.

Why the expensive stages cost what they did:
- coder (333k, highest): 295k cache read means many turns each re-reading a growing context; the
  change itself is small (4 rule blocks x 2 identical files, 2 README sentences, +64 lines). Likely
  causes: building the image / generating and running archTest to self-check plus editing two
  identical files separately. Partly justified (generator repo needs a real build); could be cheaper if
  prep's baseline/generation script were reused instead of regenerated. Not measurable without tool-use counts.
- qa (248k): ~13 scenarios, each a Gradle run; justified by the criteria (AC-1..AC-6 each need a stray-class
  scenario). Duplicated work with coder's self-check is the only avoidable part.
- ba attempt 1 (224k): large because it explored the repo and then blocked; 3 of 6 questions were avoidable (see above).
- ba in total 476k (32% of the card) for a one-rule change, caused by the question round and the
  criteria-form corrections. This is the cheapest place to save.
- architect (177k, 7k output): justified; it decided empty-set behaviour (`allowEmptyShould(true)`).
- docs (104k) for one DEVLOG entry: acceptable.

## Root causes
- Weak agent instruction: `ba` asks about points already fixed by existing code/conventions, and writes
  criteria that describe implementation or are not verifiable.
- Missing convention: the repo's verification contract (variants in CONTRIBUTING.md) is not referenced
  when the BA scopes "verify" criteria.
- Missing tooling data: metrics lack request/tool-use counts.

## Proposals
1. `.claude/agents/ba.md`: add: "Before asking, check whether the existing code, `pirca-conventions` or
   the target repo's CONTRIBUTING.md already answers the question; state such answers as assumptions
   (A1..) instead of questions. Ask only what changes scope or behaviour and cannot be derived."
   Effect: attempt 1 would have asked ~2 questions, probably avoiding the blocked run (~100k+ tokens) or making it shorter.
2. `.claude/agents/ba.md`: add a criteria checklist: "Each AC states an observable outcome (not the
   implementation), is verifiable with a command, and any 'verify in variants/environments' AC uses
   exactly the set defined in the target repo's CONTRIBUTING.md. Do not add conditions you cannot
   observe (e.g. internal rule behaviour); leave those to the architect as an assumption."
   Effect: removes the criteria-approval round (one `ba` run, ~116k tokens, and a user round).
3. `scripts/agent_usage.py`: record per run `requests` (API calls) and `tool_uses`, and write them in
   `metrics.json`. Effect: next retrospective can explain coder/qa cost with measurements.
4. `.claude/agents/coder.md` (to evaluate with proposal 3 data first): tell the coder to reuse the
   prep baseline/generation steps and to leave full multi-scenario verification to QA, limiting its own
   check to the build plus one failing and one passing case. Effect: coder cost nearer 200k.
