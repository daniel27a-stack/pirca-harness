---
name: pirca-conventions
description: Architecture and working conventions of pirca. Preloaded into every pirca-harness agent; load it whenever working on a pirca repository.
---

# pirca conventions

## Architecture
- Artifacts: **BC** (business capability), **MC** (micro capability), **ACL** (anti-corruption
  layer) and **lib-\*** (transversal technical libraries). One repository per artifact,
  no parent Gradle project.
- Dependency direction: ACL knows neither MC nor BC; MC knows no BC; BC composes MC and ACL.
  Artifacts talk at runtime (HTTP/events), never through `project(':...')` dependencies.
- BC, MC and ACL always belong to **one product**. Only `lib-*` is shared between products.
  A `lib-*` is technical only; business logic in a lib is forbidden ("mortar").
- Package / groupId: `cl.pirca.lib.<name>` for libs, `cl.pirca.<product>.<type>.<name>` for services.
- Ecosystem: `web/app → TP (touch point, future) → BC → MC | ACL`. MC owns its data; a BC never
  talks to a database directly.

## Inside each artifact — layers (ARQ-25)
- `controller → service → repository | client` (`→` = may call). `repository` only in the data
  owner (MC); `client` for HTTP calls to other artifacts or systems (BC, ACL, TP).
- `controller` never calls `repository` or `client` directly; no layer calls upwards.
  Components may live in any layer without a rule of their own.
- Naming: `..controller..` → `*Controller`, `..service..` → `*Service` (the package is always
  `service`, never `business`), `..repository..` → `*Repository`, `..client..` → `*Client`.
- This is a layered design, not hexagonal. Hexagonal (ports and adapters) is a future option for
  BCs with rich business rules; do not introduce it without a decision.
- `archTest` is one general suite for every artifact: each layer rule carries
  `@Tag("layer-<name>")`; an artifact without a layer opts out explicitly with
  `archTest.excludeLayers=<layers>` in `gradle.properties`. Layer rules never pass silently on an
  empty layer (`allowEmptyShould` stays false). A "no package cycles" rule applies everywhere.

## Build (Gradle) — three layers
1. `gradle/` — how to build and verify: `libs.versions.toml` (version catalog), `repositories.gradle`,
   `java.gradle`, `sources.gradle`, `dependencies.gradle`, `constraints.gradle`, `tests.gradle`,
   later `quality.gradle`. `build.gradle` only holds plugins, group, version and `apply from`.
2. `ci/` — how it is deployed and run (e.g. `ci/docker/Dockerfile`).
3. `.github/workflows/` — when things run; the pipeline only calls Gradle tasks.
- Spring Boot BOM is imported as a Gradle `platform()`; the `io.spring.dependency-management`
  plugin is not used.
- Forced versions: `constraints { ... because '...' }` by default;
  `resolutionStrategy.eachDependency` only as an escape hatch, also with `because`.
- Java 25 and Spring Boot 4 by default. `java-skeleton` is the canonical list of versions.

## Git and delivery
- `feature/<CARD-ID>` → PR → `main` (squash) → tag `vX.Y.Z`. Merging certifies, a tag publishes.
- `main` is protected by a repository ruleset; nobody pushes to it directly.
- Commit messages and PR titles start with the card ID: `ARQ-12: Add intTest suite`.
- Everything inside a repository is written in English.

## Working inside pirca-harness
- **Never invent timestamps.** If you have Bash, use `date -u +%Y-%m-%dT%H:%MZ`. If you do not,
  write the literal placeholder `<ts>`; the orchestrator replaces it with the real time.
- Questions for the user go in the `## Blocker` section of `progress.md`, numbered, each with the
  options and your recommendation, so the orchestrator can present them without rewording.

## Verification habits that worked
- Before changing a build, capture a **baseline** (resolved dependencies of the relevant
  configurations, test results) and compare after the change: "identical" is a checkable claim.
- For generator repos (`java-skeleton`): rebuild the image, generate every template, build each
  generated project, and run the app when relevant.
- Prove negative claims with a control test (e.g. show that the old setup fails where the new one passes).
