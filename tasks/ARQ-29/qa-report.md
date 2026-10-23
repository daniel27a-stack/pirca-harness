# ARQ-29 QA report (attempt 1)

Worktree: /home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-29 (commit 7cb2db3).
Image rebuilt (`docker build -t java-skeleton:dev .`), both variants regenerated in a new mktemp dir
(generated test contains the 4 `LiveIn` rules). Stray files added one at a time to the data project, then removed.

## Results
| Scenario | Command | Result |
|---|---|---|
| data and lib unmodified | `./gradlew build`, `./gradlew archTest` | BUILD SUCCESSFUL (both) |
| root `StrayController` (default excludes) | `./gradlew archTest` | FAILED `controllerClassesLiveInControllerPackage`; XML report: "StrayController does not reside in a package '..controller..'" (baseline: passed) |
| root `StrayService` | same | FAILED `serviceClassesLiveInServicePackage` |
| `UserServiceImpl` root | same | BUILD SUCCESSFUL |
| root `Outer { static class InnerController }` | same | BUILD SUCCESSFUL |
| `UserService` in `..controller` | same | FAILED (`serviceClassesLiveInServicePackage`, plus existing `controllerNamesEndWithController`) |
| `FooController` in `controller.sub` | same | BUILD SUCCESSFUL |
| `StrayClient`, default excludes (repository,client) | same | BUILD SUCCESSFUL |
| excludeLayers empty, valid repository/client packages added, clean | same | BUILD SUCCESSFUL |
| excludeLayers empty, stray Controller / Service / Repository / Client in root | same | each FAILED with its own inverse rule; class named in report |
| excludeLayers=client, `StrayClient` | same | BUILD SUCCESSFUL |
| lib with `StrayController` (all layers excluded) | same | BUILD SUCCESSFUL |
| Diff | `git diff main...HEAD` | only 4 added rule blocks per ArchitectureTest (no removed lines, 2 files identical) and README sentence; `--name-only` lists 4 template files |

## Criteria
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
| AC-10 | met for now | changed files are exactly the 4 listed; DEVLOG.md entry is pending the docs stage (planned) |

## Fix in docs
- DEVLOG.md: add the ARQ-29 entry (what, why, verification) in java-skeleton, per its format.
