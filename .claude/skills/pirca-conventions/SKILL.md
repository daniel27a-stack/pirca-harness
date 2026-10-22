---
name: pirca-conventions
description: Architecture and working conventions of pirca. Preloaded into every pirca-harness agent; load it whenever working on a pirca repository.
---

# pirca conventions

## Architecture
- Artifact types (ARQ-34). One repository per artifact, no parent Gradle project.

  | Type | Role |
  |---|---|
  | `edge` | Entry point for one channel (web, app, API). The **only** artifact exposed outside |
  | `flow` | Orchestrates a business process |
  | `data` | Owns its data (the only type with a database) |
  | `acl` | Anti-corruption layer: isolates an external or legacy system |
  | `lib` | Transversal technical library |

- Ecosystem: `channel → edge → flow → data | acl`. Dependency direction: `edge` calls `flow`;
  `flow` composes `data` and `acl`; `data` and `acl` know no other artifact type.
  Artifacts talk at runtime (HTTP/events), never through `project(':...')` dependencies.
- Exposure (ARQ-33): `flow`, `data` and `acl` are internal and are never reached directly from
  outside. External access (web, app, API key or other) goes only through an `edge`, and
  external security lives there.
- `edge` authenticates (who you are); `flow` authorizes (what you may see and do, e.g. per tenant
  and role). That is why an `edge` never calls a `data` directly, not even for simple reads:
  it would bypass authorization. A pass-through `flow` is an accepted cost.
- `edge`, `flow`, `data` and `acl` always belong to **one product**. Only `lib` is shared between
  products. A `lib` is technical only; business logic in a lib is forbidden ("mortar").
- Names: repositories `<product>-<type>-<name>` (e.g. `gastos-flow-expense-claims`), libraries
  `lib-<name>`.
- Java package = groupId: services use the product's groupId (`cl.pirca.gastos`), with no
  sub-package per artifact (each service runs in its own JVM). Each library has its own groupId
  (`cl.pirca.lib.<name>`), so no package is ever split between two jars.
- Older cards and notes use the previous names: TP = `edge`, BC = `flow`, MC = `data`.

## Inside each artifact — layers (ARQ-25)
- `controller → service → repository | client` (`→` = may call). `repository` only in `data`
  (the data owner); `client` for HTTP calls to other artifacts or systems (`edge`, `flow`, `acl`).
- `controller` never calls `repository` or `client` directly; no layer calls upwards.
  Components may live in any layer without a rule of their own.
- Naming: `..controller..` → `*Controller`, `..service..` → `*Service` (the package is always
  `service`, never `business`), `..repository..` → `*Repository`, `..client..` → `*Client`.
- This is a layered design, not hexagonal. Hexagonal (ports and adapters) is a future option for
  a `flow` with rich business rules; do not introduce it without a decision.
- `archTest` is one general suite for every artifact: each layer rule carries the JUnit Platform
  tag `layer-<name>` (`@ArchTag` on `@ArchTest` fields); an artifact without a layer opts out explicitly with
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

## Where things live (ARQ-28)
- Target repositories carry only **facts about the repository**, in `CONTRIBUTING.md`: what it is,
  how it works, how a change is verified. Read it before working on a repository.
- Rules for agents live in pirca-harness (this skill, agents, orchestrator), never in target repos.
- Every change adds an entry to the repository's `DEVLOG.md`, following its format.
  `README.md` changes only when usage, commands or flags change.

## Git and delivery
- `feature/<CARD-ID>` → PR → `main` (squash) → tag `vX.Y.Z`. Merging certifies, a tag publishes.
- `main` is protected by a repository ruleset; nobody pushes to it directly.
- Commit, push and PR details: skill `pirca-forge`.
- Everything inside a repository is written in English.

## Verification habits that worked
- Before changing a build, capture a **baseline** (resolved dependencies of the relevant
  configurations, test results) and compare after the change: "identical" is a checkable claim.
- For generator repos (`java-skeleton`): follow its `CONTRIBUTING.md` — rebuild the image, generate
  every variant, build each generated project, and run the app when relevant.
- Prove negative claims with a control test (e.g. show that the old setup fails where the new one passes).
