# ARQ-29 — Acceptance criteria

## Need
In `java-skeleton`, a class named `*Controller`, `*Service`, `*Repository` or `*Client` that lives
outside its layer package must make `archTest` fail. Today `StrayController` in the root package passes.

## Scope
- Templates `spring-gradle` and `java-library`: `src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs`
  (identical today) get four inverse naming rules, one per suffix.
- Generated READMEs: `templates/spring-gradle/README.md.hbs` (line 37-38) and
  `templates/java-library/README.md.hbs` (line 23-24), where the naming rules are described.
- `DEVLOG.md` entry (docs stage).

## Acceptance criteria
- AC-1: In a generated `spring-gradle` project, a top-level class `StrayController` in the root
  package makes `./gradlew archTest` fail, and the failure names that class. Same for a stray
  `*Service` (the `controller` and `service` layers are active by default there).
- AC-2: With all four layers active, a class of each suffix (`*Controller`, `*Service`,
  `*Repository`, `*Client`) outside its layer package makes `./gradlew archTest` fail.
- AC-3: A class is "in its layer" if it resides in `..<layer>..` (that package or any sub-package).
  A `*Service` inside `..controller..` fails; a `*Controller` inside `..controller.sub` passes.
- AC-4: Name matching is by suffix of the simple name: `StrayController` is flagged,
  `UserServiceImpl` is not.
- AC-5: The inverse rules cover top-level classes only, like the existing rules; nested classes are
  not checked.
- AC-6: Each inverse rule carries the same JUnit tag `layer-<layer>` as the existing rule of that
  layer. An artifact that excludes a layer via `archTest.excludeLayers` does not run that layer's
  inverse rule (running `./gradlew archTest` with a stray `*Client` passes when `client` is
  excluded, and fails when it is not).
- AC-7: The existing rules, their tags, and the `gradle.properties` keys are unchanged.
- AC-8: A freshly generated, unmodified project of each of the 2 variants defined in
  `java-skeleton/CONTRIBUTING.md` (one service type, for example `data`, and `lib`) still builds and
  passes `./gradlew archTest`.
- AC-9: The generated READMEs of both templates, where they describe the naming rules, state that a
  class with these suffixes outside its layer package also fails. No other documentation file
  (`CONTRIBUTING.md`) changes.
- AC-10: Only the files listed in Scope change in `java-skeleton`, plus its `DEVLOG.md` entry.

## Out of scope
- New flags, `gradle.properties` keys, layers or suffixes; changes to existing rules.
- Checking nested classes.
- Custom failure messages (ArchUnit defaults).
- Changing the default `archTest.excludeLayers` of any template.

## Assumptions
- A1: Exactly four new rules, one per suffix; no change to existing rules, flags or properties.
- A2: Failure messages are ArchUnit's default; nothing user-visible is added.
- A3: Verification is by generating both variants, adding a stray class in a temporary directory and
  running `./gradlew archTest`.
- A4: Order between tasks does not matter.
- A5 (from the user): with current defaults the inverse rule is active only for controller and service
  in a generated service, and inactive in libraries; accepted.
- A6: How the inverse rules behave when no misplaced class exists is decided by the architect; the
  observable result is covered by AC-8.

## Changes since the previous round
Requested by the user (resolutions.md, 2026-10-22T23:49Z):
- AC-2 changed: now states the outcome ("with all four layers active, a class of each suffix outside
  its layer package makes archTest fail") instead of how to get there.
- AC-7 changed: removed the unverifiable first half; only the unchanged existing rules, tags and
  `gradle.properties` keys remain.
- AC-8 changed: limited to the 2 variants defined in `java-skeleton/CONTRIBUTING.md` (one service
  type and `lib`) instead of all variants.
Added by me (not requested): A6 in Assumptions, recording that the empty-set behavior is left to the
architect, as the user said. No other criterion changed.
