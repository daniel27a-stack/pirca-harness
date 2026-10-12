# ARQ-12 QA report (attempt 1)

Worktree: /home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-12 (commit 61f3b08), image java-skeleton:arq12
rebuilt by qa, 4 variants regenerated fresh (Java 25, bash, Gradle 9.5.1). Raw outputs in `evidence/`.

## Commands and results
- Per variant (demo-spring, demo-app, demo-lib, demo-libpub): `./gradlew clean test|intTest|archTest` each alone: exit 0.
  tests (XML): spring test 2 (controller+service), intTest 1, archTest 6; app/lib/libpub test 1, intTest 1, archTest 1; 0 failures.
- `./gradlew clean check --console=plain`: BUILD SUCCESSFUL in 4 variants; task order `:test, :archTest, :intTest, :check`
  (test first, all executed).
- Reverse order control `./gradlew clean intTest archTest test`: test still runs first (spring, app, lib).
- Classpath diff vs baseline/: compileClasspath, runtimeClasspath and testRuntimeClasspath byte-identical in all 4 variants.
- WireMock count in intTest/test/archTest runtime classpaths: app 0, lib 0, spring: only intTestRuntimeClasspath (1); no "wiremock" in app/lib files.
- Three ArchitectureTest.java copies: `diff` identical. spring testcases: controllerDoesNotCallRepositoryOrClient,
  controllerNamesEndWithController, serviceDoesNotCallController, serviceNamesEndWithService, noBusinessPackage, noPackageCycles.
- `-ParchTest.excludeLayers=service` drops only service testcases; `=controller` drops only controller ones; `=foo` fails with
  "unknown layer 'foo'". (Those runs exit 1 only because the repository/client layers are then not excluded and empty.)
- `=client` / `=repository`: BUILD FAILED, the other empty layer's two rules fail. Default run exit 0.
- AC-9 controls on copy of demo-spring: controller using FooClient -> controllerDoesNotCallRepositoryOrClient FAILED;
  service/Helper -> serviceNamesEndWithService FAILED; business/Foo -> noBusinessPackage FAILED; pkga<->pkgb -> noPackageCycles FAILED;
  untouched copy exit 0. Cycle also in demo-app -> noPackageCycles FAILED.
- demo-libpub `publishToMavenLocal` OK; demo-app `./gradlew run` prints `Hello, demo-app!`; demo-spring bootJar + java -jar:
  `curl /hello` = `Hello from demo-spring` = baseline. App stopped (port closed).
- Catalog: archunit 1.5.1 / wiremock 3.13.2 only in libs.versions.toml (0 literals in gradle/*.gradle); archTestRuntimeClasspath resolves archunit-junit5:1.5.1.

## Baseline comparison
Classpaths identical; before: only `test` (1 test), after: three suites.

## Notes (non-blocking)
- spring archTest runs 6 tests by default, not 9 as the plan note said (repository/client excluded); consistent with AC-7.
- noBusinessPackage is tagged layer-service.
- README table cell alignment is slightly uneven (cosmetic).

## Verdicts
| AC | Verdict | Evidence |
|---|---|---|
| AC-1 | met | each suite alone exit 0, >=1 test in every variant |
| AC-2 | met | check lists test, archTest, intTest executed |
| AC-3 | met | src/test, src/intTest, src/archTest with .java; separate XML dirs |
| AC-4 | met | ExternalServiceStubIntTest passes; WireMock only in spring intTest classpath |
| AC-5 | met | identical source; rules/suffixes/noBusinessPackage/noPackageCycles in all 3 |
| AC-6 | met | @ArchTag layer-*; exclude service/controller filters exactly those testcases |
| AC-7 | met | gradle.properties exact lists; app/lib only noPackageCycles; unknown name fails |
| AC-8 | met | excludeLayers=client or repository fails; failOnEmptyShould=true |
| AC-9 | met | 4 controls fail (client call, naming, business, cycle) + app cycle; revert green |
| AC-10 | met | HelloService in service, controller delegates, archTest green, /hello unchanged, both unit tests pass |
| AC-11 | met | diff vs baseline empty for compile/runtime classpath, 4 variants |
| AC-12 | met | versions only in catalog, resolve, suites green on Java 25 / Boot 4 |
| AC-13 | met | check green x4, publishToMavenLocal, run, bootJar + /hello |
| AC-14 | met | generated READMEs, repo README and DEVLOG document suites, excludeLayers, tag (English) |
| AC-15 | met | test before intTest/archTest in check and in reversed command line |

Verdict: done.
