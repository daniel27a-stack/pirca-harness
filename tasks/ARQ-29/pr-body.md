## Scope

Inverse naming rules in `archTest`: a top-level class named `*Controller`, `*Service`,
`*Repository` or `*Client` outside its layer package (`..<layer>..`) now makes `archTest` fail.
Before this change, `StrayController` in the root package passed.

- `templates/spring-gradle` and `templates/java-library`: `ArchitectureTest.java.hbs` gets four
  inverse rules, one per suffix. Each carries the same `@ArchTag("layer-<layer>")` as its layer's
  existing rule, so `archTest.excludeLayers` also disables it. They use `allowEmptyShould(true)`:
  no class with the suffix means no stray class.
- Generated READMEs of both templates describe the rule in both directions.
- `DEVLOG.md` entry.

Unchanged: existing rules, their tags, `gradle.properties` keys and the default `excludeLayers`.

## Acceptance criteria (from QA)

| AC | Verdict | Evidence |
|---|---|---|
| AC-1 | met | StrayController and StrayService fail, report names them; baseline passed |
| AC-2 | met | all four layers active: each suffix stray fails |
| AC-3 | met | UserService in controller fails; FooController in controller.sub passes |
| AC-4 | met | UserServiceImpl passes, StrayController fails |
| AC-5 | met | nested InnerController passes |
| AC-6 | met | each rule has `@ArchTag("layer-<layer>")` (diff); StrayClient passes with client excluded, fails when not; lib passes |
| AC-7 | met | diff has no removed lines in ArchitectureTest; no gradle.properties/gradle/ changes |
| AC-8 | met | data and lib build and archTest pass unmodified |
| AC-9 | met | both README templates extended; CONTRIBUTING.md unchanged |
| AC-10 | met for now (QA, before docs) | changed files are exactly the 4 listed; DEVLOG.md entry was pending the docs stage. After docs, `git diff --stat origin/main..HEAD` shows those 4 files plus DEVLOG.md |

Card: https://trello.com/c/bRhbVc56/34-arq-29-java-skeleton-regla-inversa-de-nombres-en-archtest

🤖 Generated with [Claude Code](https://claude.com/claude-code)
