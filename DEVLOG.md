# pirca-harness devlog

Log of changes and decisions for the harness. Each entry states **what** changed, **why**,
and **how it was verified**.

## Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-11 | Separate repository that operates on target repos through git worktrees | Agents and their rules live in one place; target repos stay free of harness files |
| 2026-10-11 | Orchestrator is the `/run-card` command in the main session, not a subagent | Subagents have no `AskUserQuestion`; blockers must come back to the session that talks to the user |
| 2026-10-11 | Rules enforced by mechanism where possible (hooks, tool scopes, `maxTurns`) | Instructions alone can be ignored; a hook that exits 2 cannot |
| 2026-10-11 | All agents on Sonnet | Start cheap; switch a stage to a stronger model only if `metrics.json` and retrospectives show the need |
| 2026-10-11 | State in `tasks/<CARD-ID>/progress.md`, measured cost in `metrics.json`, both committed | Resume after blockers across sessions; keep a record of how each card was done and what it cost |
| 2026-10-11 | The user writes the **need**; the BA agent writes `criteria.md`; **the user approves the criteria** before the architect runs. The architect writes `implementation.md`; `coder` receives both | Criteria define the scope, so they are a contractual decision: a wrong criterion would propagate to design, code and QA. Separating what (criteria) from how (implementation) keeps each agent's job clear |
| 2026-10-11 | QA failure → one automatic retry of `coder`, then stop | Cheap fixes happen alone; repeated failures need a human |
| 2026-10-11 | Retrospective runs after the merge and only proposes | The user's review changes are the best signal; changing agents is a user decision |
| 2026-10-11 | No agent teams or dynamic workflows yet | The flow is sequential and needs user input mid-run, which workflows do not allow |
| 2026-10-22 | Card state in `progress.json`, written only by `scripts/progress.py`; `progress.md` is generated from it | Agents edited `progress.md` by hand and wrote invented timestamps; one writer makes state consistent and checkable |
| 2026-10-22 | Board and code hosting only through the skills `pirca-board` and `pirca-forge` | Tool commands and ids were repeated across agents, the orchestrator and `CLAUDE.md`; changing tool means changing one skill |
| 2026-10-22 | `Co-Authored-By` names the model that actually wrote the change (Sonnet 5.5 for flow agents, the session model for work done in conversation) | Attribution should be truthful |

| 2026-10-22 | What agents need to know about a target repository lives in a profile in the harness (`repos/<repo>.md`); a repository without a profile stops before `architect` | The repository keeps only facts (`CONTRIBUTING.md`, ARQ-28); agents must not deduce what a repo is by exploring |
| 2026-10-22 | A card is understood by its content, never by titles or keywords | Requiring a `Necesidad` section rejected clear cards; asking is the BA's job |
| 2026-10-23 | The user no longer approves criteria: the BA understands the need, asks only when it does not, and writes the criteria on its own. Replaces the 2026-10-11 approval gate | The approval rounds were slow and asked the user to confirm what was deducible (ARQ-29: 6 questions, 5 deducible, plus a correction round). The user reviews the result in the PR |
---

## 2026-10-11 — ARQ-11: First version of the harness

**What:** `CLAUDE.md`, `pirca-conventions` skill (preloaded into every agent), seven agents
(`refinement`, `architect`, `prep`, `coder`, `qa`, `docs`, `retrospective`), the `/run-card`
orchestrator, `tasks/README.md` (file formats), and three scripts:
- `block_push_main.py` — `PreToolUse` hook that blocks any `git push` to main/master.
- `guard_write_scope.py` — `PreToolUse` hook for agents that must not change code
  (`refinement`, `architect`, `qa`, `retrospective`): writes allowed only under `tasks/`.
- `agent_usage.py` — measured tokens, model and duration of a subagent run from its transcript.

**Verification so far:**
- `block_push_main.py`: blocks `push origin main`, `src:main`, `HEAD:refs/heads/main`, `-f +main`,
  `git -C <repo> push ... :master` and a bare `git push` on main; allows feature branches,
  a branch named `feature/main-fix`, non-push commands and a bare push on a feature branch.
- `guard_write_scope.py`: allows `tasks/ARQ-12/qa-report.md`, blocks a target repo's `build.gradle`.
- `agent_usage.py`: on a real subagent transcript, reports model, 4 API requests (deduplicated),
  tokens by type and 82.4 s duration.
- Pending: end-to-end run of ARQ-12 (acceptance criterion 10 of ARQ-11).

## 2026-10-11 — ARQ-11: Need-based intake, criteria approval gate, fixes from the first run

**What:**
- Cards carry a `Necesidad` section; `refinement` acts as BA and writes `criteria.md`; the user
  approves the criteria before `architect` runs; `architect` writes `implementation.md`;
  `coder` and `qa` work from both.
- `architect` gets `WebFetch` (Maven Central and the Gradle plugin portal only) and must pin exact
  versions; placeholders such as `<1.4.x>` are not allowed.
- Timestamps: agents never invent them (`date -u` or the `<ts>` placeholder, replaced by the
  orchestrator after each stage).
- Questions to the user follow a fixed format (`❓ Pregunta`, numbered options with a recommended
  one, `✅ Responde` with one copy-ready block).
- `pirca-conventions` gains the ecosystem view and the layer convention (ARQ-25).

**Why (first, aborted run of ARQ-12):**
- `architect` had no way to look up versions and left placeholders, pushing a design decision to `coder`.
- Agents without a shell wrote made-up timestamps (`2026-10-11T00:00Z`) in `progress.md`.
- `architect` assumed hexagonal package names that pirca had never decided; the orchestrator
  correctly stopped and asked, which produced ARQ-25.
- The user pasted the wrong block of an answer because several versions had been offered.
- The harness was modified while the run was in progress, so the session mixed the old and new
  flow. Rule since then: never change the harness while a card is running.

**Verification:** run leftovers removed (`tasks/ARQ-12/`, empty agent memory); ARQ-12 reset to
Backlog with a `Necesidad` section; `settings.json` valid. The flow itself is verified by the next
ARQ-12 run.

## 2026-10-13 — ARQ-35: pirca-conventions updated with the decisions of Oct 12-13

**What:** the `pirca-conventions` skill (preloaded into every agent) now reflects the decisions
taken in conversation with the user:
- Artifact types `edge` / `flow` / `data` / `acl` / `lib` (ARQ-34), replacing TP / BC / MC / ACL,
  with a mapping note for older cards.
- Only `edge` is exposed outside; `flow`, `data` and `acl` are internal (ARQ-33).
- `edge` authenticates, `flow` authorizes; an `edge` never calls a `data` directly, even for
  simple reads (decided with the user; pass-through flows are an accepted cost).
- Java package = groupId: product groupId for services, one groupId per library.
- Where things live (ARQ-28): target repos carry facts in `CONTRIBUTING.md`; agent rules live in
  this harness; `DEVLOG.md` gets an entry in every change, `README.md` only when usage changes.
- Layer rules reference the new types; the archTest tag wording matches the implementation
  (`@ArchTag` on `@ArchTest` fields).

**Why:** the skill contradicted the cards (old type names and a wrong package rule), which would
have made ARQ-32 run with two conflicting sources of truth.

**How:** done in conversation, not by the agentic flow, because it changes the rules every agent
follows; no card was running at the time.

**Verification:** no old type names left outside `tasks/` (historical records); the real check is
the next card (ARQ-32) running without contradictions between the card and the skill.

## 2026-10-22 — ARQ-30: BA improvements and rename `refinement` → `ba`

**What:**
- The BA agent is now `ba` (`.claude/agents/ba.md`, renamed from `refinement.md` with its history).
  Current references (`CLAUDE.md`, `/run-card`, `tasks/README.md`) say `ba`; records of past cards
  under `tasks/` and older DEVLOG entries keep `refinement`, since they are history.
- New section "Rules that prevent rework" in the BA, one rule per lesson from earlier cards:
  1. Interface changes: list every existing element and ask keep/remove (ARQ-32).
  2. New deliverables: ask for name, audience and location (ARQ-28).
  3. Examples and requested rules are verified against the source, citing file and line (ARQ-28).
  4. "Nothing else changes" criteria allow the docs-stage DEVLOG entry (ARQ-28).
  5. Nothing user-visible that the card does not name, unless listed as an assumption (ARQ-32).
  6. All open questions at once, with bulk-confirmable assumptions (ARQ-32).
- The BA reads the target repository's `CONTRIBUTING.md` first.

**Why:** the BA stage was the most expensive and the source of most rework (four criteria rounds in
ARQ-28; three restarts and a PR closed without merge in ARQ-32). The agent was always meant to be
"the BA", but its name never changed.

**Verification:** no current reference to `refinement` remains outside history; the real check is
the next card's BA run.

## 2026-10-22 — ARQ-40: Encapsulate the harness (stage protocol, state, board, forge, commits)

**What:**
- `pirca-stage-protocol` skill, preloaded into every stage agent: what to read first (progress,
  `resolutions.md`, `task.json`, the target's `CONTRIBUTING.md`), recording state only through the
  script, blocking with all questions at once (options, recommendation, assumptions A1…), reporting
  only what was run, and the final `STATUS:` line. The seven agents now keep only what is specific
  to their stage.
- `scripts/progress.py`: the only writer of card state (`init`, `start`, `set`, `log`, `card`,
  `show`, `check`). `progress.json` is the source of truth; `progress.md` is generated and `check`
  detects hand edits. Timestamps come from the script (UTC, minutes). Cards from before ARQ-40
  are not migrated.
- `pirca-board` skill (`board.py`: `find`, `snapshot`, `move`, `comment`; ids in `board.json`).
  Descriptions are never rewritten; long comments are split, since the board API rejects long
  requests.
- `pirca-forge` skill (`forge.py`: `push`, `pr-create`, `pr-state`, `pr-review`; refuses
  main/master) and the commit conventions, including `Co-Authored-By` with the real model.
- `ba` and `architect` get Bash restricted by the new `guard_bash_readonly.py` hook: only
  `progress.py set|log|show|check`, read-only git, `date` and read-only filters; no redirections.
- `/run-card`, `CLAUDE.md` ("Where things live" table), `tasks/README.md` and `pirca-conventions`
  point to these pieces instead of repeating them. `settings.json` allows the three scripts
  instead of `trello`, `gh pr` and `git push`. The task field `trello_card_id` is now `board_card_id`.
- Absorbs ARQ-39 (board and forge skills).

**Why:** the same knowledge (tool commands, ids, honesty rules, timestamps, commit format) was
copied in several agents and the orchestrator, and drifted; agents wrote state by hand.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself; no
card was running.

**Verification:**
- YAML frontmatter of the 7 agents, 4 skills and `/run-card` parses, and every preloaded skill
  exists; `settings.json` parses; all scripts compile.
- `progress.py` dry run on a scratch copy: ba → criteria approval → architect blocked with a
  blocker file → card blocked; `check` passes, then flags a hand edit of `progress.md`;
  `set coder failed` is refused (only qa).
- `guard_bash_readonly.py`: allows `progress.py set` with a quoted `->` and
  `git -C … log | head`; blocks `echo > f`, `git push` and `rm -rf`.
- `board.py find ARQ-40` returns the card in `en-curso`; `forge.py push . main` is refused.
- Not yet verified: a full card run through the new flow (the next card is the real check).

## 2026-10-22 — ARQ-41: Orchestrator and repository profiles

**What:**
- `/run-card` launches every stage in the foreground and waits for it; nothing else runs meanwhile.
- `CLAUDE.md`: always talk to the user in Spanish, in every session, not only inside `/run-card`.
- Restarting a card archives instead of deleting: the folder goes to
  `tasks/<CARD-ID>/aborted/<UTC time>/`, clean worktrees are removed and their branches renamed
  `aborted/<CARD-ID>-<UTC time>`; a worktree with uncommitted changes stops the restart.
- Repository profiles: `repos/README.md` (format) and `repos/java-skeleton.md`. The orchestrator
  passes them to `architect`, `coder` and `qa`, and stops before `architect` if a repo has none.
- `scripts/allow_qa_commands.py`: `PreToolUse` hook for `qa` that pre-approves commands starting
  with a prefix from a profile's `## QA commands` (or a read-only filter), including every part of
  a compound command and every `$(...)`. Anything else, and any redirection to a file, still asks.
  It never blocks.
- No dependency on the word "Necesidad": the BA understands what the card asks however it is
  written and asks when it does not; the orchestrator no longer rejects a card for its format.

**Why:** items carried over from ARQ-27 (qa ran in the background in ARQ-12, a session answered in
English, aborted runs were lost, agents deduced each repo's nature by exploring, qa needed
permission for every verification command), plus cards being rejected for their wording.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself.

**Verification:**
- `allow_qa_commands.py` allows `docker build`, `D=$(mktemp -d)`, `docker run -u "$(id -u):$(id -g)" …`,
  `cd … && ./gradlew build 2>&1 | tail`, `java -jar … & sleep`, `curl … | head`; it leaves for
  the normal prompt `java -jar … & rm -rf /`, `curl $(rm -rf x)`, a nested `$(…$(rm x))`,
  `sed -i`, `cat f > g` and `X=1 rm f`.
- No reference to a `Necesidad` section remains in agents, the orchestrator or `CLAUDE.md`.
- Not yet verified: foreground stages, profile hand-off and restart archiving in a real run (the
  next card on `java-skeleton` is the check).

## 2026-10-22 — ARQ-42: BA and architect rules

**What:**
- `ba.md`, new rules 7–9: criteria state observable behavior only (no mechanisms, nothing
  unverifiable); ask whether the order between several tasks matters; the BA defines the criteria
  (it may add, change or remove any) and, from round 2 on, lists every change since the previous
  round and why, never as a clarification. `criteria.md` gets a "Changes since the previous round"
  section.
- `architect.md`: the plan is proportional to the change; test counts only for the default
  configuration, or none; commands behave the same in bash and zsh.

**Why:** items carried over from ARQ-27, each from rework in ARQ-12 or ARQ-28.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself.

**Verification:** agent frontmatter parses. The real check is the next card's BA and architect runs.

## 2026-10-22 — ARQ-43: QA "fix in docs" and docs commit messages

**What:**
- `qa.md`: a cheap cosmetic defect in documentation or text that breaks no acceptance criterion
  goes under `## Fix in docs` in `qa-report.md` (file, line, exact fix) instead of a loose note;
  it does not fail the card. Anything needing a code change is not a "fix in docs".
- `docs.md`: applies every "fix in docs" item, and its commit message names every file it changes.

**Why:** items carried over from ARQ-27. In ARQ-12 the orchestrator passed QA's note to docs by
hand, and the docs commit said "Update DEVLOG" while it also changed READMEs.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself.

**Verification:** agent frontmatter parses. The real check is the next card's QA and docs runs.
Still pending from ARQ-11 (AC-7): the automatic qa → coder retry, the first time QA fails.


## 2026-10-22 — ARQ-44: Reliable output tokens and cost per stage

**What:**
- Output-token source investigated. Claude Code telemetry (`api_request` events) gives the final
  output tokens of every API request, with its `request_id` and agent name. In three probe runs on
  Claude Code 2.1.307 (one or several requests, with and without thinking), the subagent
  transcript matched it exactly per request (e.g. 140/261/1872 and 95/142/206 in both). The
  under-count came from older versions, which stored the usage from the start of each response.
  So the transcript stays the source (no telemetry setup needed), and `agent_usage.py` now reports
  `claude_code_version` and `output_tokens_reliable` (2.1.307 or later), with a `warning` otherwise.
- ARQ-12 and ARQ-28 (2.1.296) and ARQ-32 (2.1.300) cannot be recalculated: their transcripts never
  stored the final output and no telemetry was recorded. Their `metrics.json` get an
  `output_tokens_note` saying so; the data is unchanged.
- `retrospective.md`: a per-stage cost table by token type, and for each expensive stage why it
  cost what it did (with evidence) and whether it was justified; no conclusions from unreliable
  output tokens.

**Why:** items carried over from ARQ-27: output tokens (the most expensive ones) looked unmeasured
(80 for qa and docs in ARQ-28), and retrospectives only reported the total.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself.

**Verification:**
- The three telemetry probes above (`CLAUDE_CODE_ENABLE_TELEMETRY=1`, console exporter, headless
  runs with one subagent each).
- `agent_usage.py` on an ARQ-32 transcript: `2.1.300`, `output_tokens_reliable: false`, warning;
  on a 2.1.307 probe transcript: `true`, no warning.

## 2026-10-23 — ARQ-46: The BA understands the need; no criteria approval

**What:**
- `ba.md` rewritten around one job: understand what the card wants and why. Once it does, the BA
  writes the criteria on its own; it asks only when it does not understand the need or cannot
  identify the target repository. The rules that made it ask (keep/remove each element, name and
  audience, order between tasks, listing changes between rounds) became decisions it states in a
  new `## Decisions` section of `criteria.md`.
- The criteria approval gate is gone: `/run-card` goes from `ba` to `architect`, posting the
  criteria on the card as a comment. The stage `criteria-approval` is removed from
  `scripts/progress.py` (old `progress.json` files still pass `check`).
- `pirca-stage-protocol`: a stage blocks only in the cases its agent file lists; the rule "never
  pick an option yourself, not even as a sensible default" is removed.
- References to approved criteria updated in `CLAUDE.md`, `tasks/README.md`, `architect.md`,
  `coder.md`, `retrospective.md` and `pirca-board`.

**Why:** card ARQ-46: the BA does not have the user validate criteria; it only makes sure it
understands the need, and asks if it does not.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself.

**Verification:** frontmatter of agents, skills and `/run-card` parses; no reference to criteria
approval remains; `progress.py` runs `ba` → `architect` on a scratch card and refuses the old
stage; `check` still passes on ARQ-29's old `progress.json`. The real check is the next card's BA.

## 2026-10-23 — ARQ-47: The architect understands the need and follows the conventions

**What:** `architect.md`: the how is the architect's to decide, following the conventions
(`pirca-conventions`, the repository profile and its `CONTRIBUTING.md`). It asks only when it does
not understand the need or when its plan needs to skip a convention. It no longer blocks on
decisions it can make itself (dependency choices, trade-offs).

**Why:** card ARQ-47. In ARQ-29 the architect skipped a written convention
(`allowEmptyShould(true)` against `archRule.failOnEmptyShould=true`) without asking.

**How:** done in conversation, not by the agentic flow, because it changes the flow itself.

**Verification:** agent frontmatter parses. The real check is the next card's architect.

