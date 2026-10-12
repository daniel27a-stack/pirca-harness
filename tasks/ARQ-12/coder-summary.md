# ARQ-12 coder summary

Repo: java-skeleton worktree /home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-12, branch feature/ARQ-12.
Commit: 61f3b08 "ARQ-12: Add intTest and archTest suites to the templates" (not pushed).

## Changes
- All 3 templates: `gradle/{libs.versions.toml,sources.gradle,dependencies.gradle,tests.gradle}`, new `gradle.properties`,
  `src/archTest/{java/.../ArchitectureTest.java.hbs,resources/archunit.properties}`, intTest sample, `README.md.hbs`.
- spring-gradle: `HelloService`, `HelloController` delegation, `HelloControllerTest` (@Import), `HelloServiceTest`,
  `ExternalServiceStubIntTest` (WireMock standalone 3.13.2).
- java-app: `MainIntTest`; java-library: `{{className}}IntTest`.
- Repo `README.md` and `DEVLOG.md` (Step 3 entry, decisions).

## Deviations from the plan
- `sources.gradle`: suites declare `dependencies { implementation project() }`. Without it the main classes were not
  on the intTest/archTest classpath (archTest failed "failed to check any classes"). The plan allowed this fix.
- spring-gradle archTest has 6 tests by default (controller 2 + service 3 + cycles 1), not 9 as the plan's AC-5 note said
  (repository/client rules are excluded by default).

## Verification run (generated with image java-skeleton:arq12, Java 25, bash)
- `./gradlew clean check` BUILD SUCCESSFUL in demo-spring, demo-app, demo-lib, demo-libpub; tasks test, archTest, intTest executed (test first).
  Test counts: spring test 2 (controller + service), intTest 1, archTest 6; app/lib test 1, intTest 1, archTest 1.
- compileClasspath and runtimeClasspath diff vs baseline/: identical in all 4 variants.
- demo-spring `-ParchTest.excludeLayers=service|controller` removes exactly the layer-service / layer-controller testcases;
  `=foo` fails with "unknown layer 'foo'"; `=client` / `=repository` fail on the other empty layer.
- Control (throwaway copy): business package + A<->B cycle make archTest fail on noBusinessPackage and noPackageCycles.
- bootJar runs, `curl /hello` = `Hello from demo-spring`.
- WireMock not on testRuntimeClasspath (spring) nor intTest/test classpaths of demo-app (grep count 0).
- Not run: publishToMavenLocal, remaining AC-9 controls (client call, naming), `gradlew run` for java-app: left to qa.
