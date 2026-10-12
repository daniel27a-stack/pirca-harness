# ARQ-12 — Implementation plan

Repo: `java-skeleton` (`/home/daniel-jofre/Documentos/Desarrollo/java-skeleton`). Only `templates/*`,
`README.md` and `DEVLOG.md` change. `bin/cli.js` does not change: it renders `*.hbs` and copies every
other file verbatim (so `gradle.properties` and `archunit.properties` need no `.hbs`).

## Approach

Facts verified in the repo:
- Each template already has `gradle/{repositories,java,sources,dependencies,constraints,tests}.gradle`,
  applied from `build.gradle.hbs` in that order. `gradle/sources.gradle` is an empty placeholder whose
  comment says "intTest, archTest declared with the JVM Test Suite plugin (`testing { suites { ... } }`)".
- `gradle/tests.gradle` only does `tasks.named('test') { useJUnitPlatform() }`.
- Wrapper is Gradle 9.5.1. `spring-gradle` imports the Boot BOM as `platform(libs.spring.boot.bom)`;
  `java-app`/`java-library` use `platform(libs.junit.bom)` (JUnit 6.1.3).
- No template has `gradle.properties` today. `spring-gradle` has `controller/HelloController` only
  (no service); `HelloControllerTest` is a `@WebMvcTest(HelloController.class)`.

Design (same structure in the 3 templates):
1. **JVM Test Suite plugin**, as the repo already announced: `sources.gradle` registers
   `testing { suites { intTest(JvmTestSuite) ; archTest(JvmTestSuite) } }`. Each suite gets its own
   source set (`src/intTest`, `src/archTest`), its own `intTestImplementation` / `archTestImplementation`
   configurations and its own task. New suites see the main classes automatically. Their dependencies
   are declared in `dependencies.gradle` (not in the suite block), main/`test` dependencies untouched.
2. **Wiring in `tests.gradle`**: `tasks.withType(Test).configureEach { useJUnitPlatform() }`;
   `check.dependsOn(intTest, archTest)` (only `test` is wired to `check` automatically);
   `intTest.mustRunAfter(test)` and `archTest.mustRunAfter(test)` (AC-15).
3. **One general `ArchitectureTest`** (identical source in the 3 templates), using
   `archunit-junit5` with `@ArchTest` fields. Each layer rule has `@ArchTag("layer-<layer>")`, which
   ArchUnit exposes as a JUnit Platform tag.
4. **Opt-out = tag exclusion.** `archTest.excludeLayers` (in `gradle.properties`) is read in
   `tests.gradle`, validated against `controller,service,repository,client` (unknown name ->
   `GradleException`, so a typo never silently disables nothing) and mapped to
   `useJUnitPlatform { excludeTags 'layer-<layer>' ... }` on the `archTest` task. The test source never
   changes between templates; only the property does. A missing property means "exclude nothing".
5. **Never silent on empty layers**: `src/archTest/resources/archunit.properties` with
   `archRule.failOnEmptyShould=true` (ArchUnit's default, made explicit; this is `allowEmptyShould=false`).
   Rules are written so their `that()` set is non-empty whenever the layer exists. If a layer's
   rules are not excluded and the layer has no classes, the rule fails (AC-8).
6. **WireMock** only in `spring-gradle` `intTestImplementation`, artifact
   `org.wiremock:wiremock-standalone` (shaded jar). Reason: the plain `wiremock` artifact pulls Jetty 11
   transitively and the Spring Boot BOM (imported as platform) would force a different Jetty, a classic
   breakage; the standalone jar has no transitive dependencies, so BOM and WireMock cannot collide.
   Stable line is 3.x (4.x is beta-only on Maven Central).
7. **Cycles rule** `slices().matching("(**)")` = one slice per package. This is non-empty even in
   `java-app` / `java-library` (single root package), so the rule runs and passes without needing
   `allowEmpty`.

Pinned versions (read from Maven Central `maven-metadata.xml`):
- `com.tngtech.archunit:archunit-junit5` **1.5.1** (latest release; its engine only depends on archunit
  1.5.1 + archunit api modules, no explicit JUnit pin in the POM).
- `org.wiremock:wiremock-standalone` **3.13.2** (highest non-beta; latest overall is `4.0.0-beta.40`,
  do not use).
- No other new library. JUnit versions stay as they are (Boot BOM / `junit-bom` 6.1.3).

## Files

All paths relative to `java-skeleton/templates/`. `<P>` = `src/<suite>/java/{{packagePath}}`.

### spring-gradle
- change `spring-gradle/gradle/libs.versions.toml`: add `[versions] archunit = "1.5.1"`,
  `wiremock = "3.13.2"`; libraries `junit-jupiter = { module = "org.junit.jupiter:junit-jupiter" }`,
  `junit-platform-launcher = { module = "org.junit.platform:junit-platform-launcher" }` (both
  BOM-managed, no version), `archunit-junit5 = { module = "com.tngtech.archunit:archunit-junit5", version.ref = "archunit" }`,
  `wiremock-standalone = { module = "org.wiremock:wiremock-standalone", version.ref = "wiremock" }`.
- change `spring-gradle/gradle/sources.gradle`: the two suites.
- change `spring-gradle/gradle/dependencies.gradle`: add the suite dependencies (below).
- change `spring-gradle/gradle/tests.gradle`: wiring, ordering, exclusion mapping.
- create `spring-gradle/gradle.properties`.
- create `spring-gradle/src/main/java/{{packagePath}}/service/HelloService.java.hbs`.
- change `spring-gradle/src/main/java/{{packagePath}}/controller/HelloController.java.hbs`.
- change `spring-gradle/src/test/java/{{packagePath}}/HelloControllerTest.java.hbs`: add
  `@Import(HelloService.class)` (otherwise the `@WebMvcTest` slice has no `HelloService` bean and fails).
- create `spring-gradle/src/test/java/{{packagePath}}/service/HelloServiceTest.java.hbs` (plain unit test).
- create `spring-gradle/src/intTest/java/{{packagePath}}/ExternalServiceStubIntTest.java.hbs`.
- create `spring-gradle/src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs`.
- create `spring-gradle/src/archTest/resources/archunit.properties`.
- change `spring-gradle/README.md.hbs`.

### java-app
- change `java-app/gradle/libs.versions.toml` (add `archunit`), `sources.gradle`, `dependencies.gradle`,
  `tests.gradle`; create `java-app/gradle.properties`.
- create `java-app/src/intTest/java/{{packagePath}}/MainIntTest.java.hbs` (runs `Main.main` with
  `System.out` captured, asserts the greeting line).
- create `java-app/src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs` (identical to
  spring-gradle's) and `java-app/src/archTest/resources/archunit.properties`.
- change `java-app/README.md.hbs`.

### java-library
- change `java-library/gradle/libs.versions.toml`, `sources.gradle`, `dependencies.gradle`,
  `tests.gradle`; create `java-library/gradle.properties`.
- create `java-library/src/intTest/java/{{packagePath}}/{{className}}IntTest.java.hbs` (trivial public
  API check, e.g. `new {{className}}().greet("world")` equals `Hello, world!`).
- create `java-library/src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs` and
  `java-library/src/archTest/resources/archunit.properties`.
- change `java-library/README.md.hbs`.

### Repo docs
- change `java-skeleton/README.md`: short "Generated project: test suites" section.
- change `java-skeleton/DEVLOG.md`: mark Step 3 done in the plan list, add decision rows and a
  "Step 3" entry (what / why / verification), in English, same format as Steps 1-2 (docs stage may
  finalize the verification text).

### Content to write (fixed, so coder takes no design decisions)

`sources.gradle` (identical in the 3 templates):
```groovy
// Additional source sets and their tasks, declared with the JVM Test Suite plugin.
//   test     src/test      unit tests
//   intTest  src/intTest   integration tests
//   archTest src/archTest  architecture tests (ArchUnit)
// Dependencies are declared in dependencies.gradle; wiring into `check` is in tests.gradle.
testing {
    suites {
        intTest(JvmTestSuite)
        archTest(JvmTestSuite)
    }
}
```
(The Gradle 9 plugin makes the main classes available to new suites. If it does not for any template,
the fix is `implementation project()` inside the suite's `dependencies {}`; do not change main
configurations.)

`dependencies.gradle` additions:
- spring-gradle:
  ```groovy
  intTestImplementation platform(libs.spring.boot.bom)
  intTestImplementation libs.junit.jupiter
  intTestImplementation libs.wiremock.standalone
  intTestRuntimeOnly libs.junit.platform.launcher

  archTestImplementation platform(libs.spring.boot.bom)
  archTestImplementation libs.junit.jupiter
  archTestImplementation libs.archunit.junit5
  archTestRuntimeOnly libs.junit.platform.launcher
  ```
- java-app / java-library (same pattern with the JUnit BOM; no WireMock):
  ```groovy
  intTestImplementation platform(libs.junit.bom)
  intTestImplementation libs.junit.jupiter
  intTestRuntimeOnly libs.junit.platform.launcher

  archTestImplementation platform(libs.junit.bom)
  archTestImplementation libs.junit.jupiter
  archTestImplementation libs.archunit.junit5
  archTestRuntimeOnly libs.junit.platform.launcher
  ```

`tests.gradle` (identical in the 3 templates):
```groovy
// Test task configuration shared by test, intTest and archTest.
tasks.withType(Test).configureEach {
    useJUnitPlatform()
}

// `test` runs first; intTest and archTest are part of `check`.
tasks.named('intTest') { mustRunAfter tasks.named('test') }
tasks.named('archTest') { mustRunAfter tasks.named('test') }
tasks.named('check') { dependsOn tasks.named('intTest'), tasks.named('archTest') }

// Layer opt-out: archTest.excludeLayers=<comma-separated layers> in gradle.properties.
// Each layer rule is tagged `layer-<layer>`, so excluding a layer excludes its tag.
def knownLayers = ['controller', 'service', 'repository', 'client']
def excludedLayers = (findProperty('archTest.excludeLayers') ?: '').toString()
        .split(',')*.trim().findAll { it }
excludedLayers.each { layer ->
    if (!(layer in knownLayers)) {
        throw new GradleException("archTest.excludeLayers: unknown layer '${layer}'. Known layers: ${knownLayers.join(', ')}")
    }
}
tasks.named('archTest') {
    useJUnitPlatform {
        excludedLayers.each { excludeTags "layer-${it}" }
    }
}
```
(Coder may adjust Groovy syntax to make it work on Gradle 9.5.1 while keeping behavior; the
behavior above is the contract.)

`gradle.properties` content:
- spring-gradle: comment lines explaining the property and the four layer names, then
  `archTest.excludeLayers=repository,client`
- java-app and java-library: `archTest.excludeLayers=controller,service,repository,client`

`archunit.properties` (all 3): `archRule.failOnEmptyShould=true` with a comment line saying a rule must
never pass silently on an empty layer.

`HelloService` (package `{{groupId}}.service`): `@Service public class HelloService { public String greeting() { return "Hello from {{serviceName}}"; } }`.
`HelloController`: constructor injection of `HelloService`; `hello()` returns `helloService.greeting()`.
Endpoint output stays exactly `Hello from {{serviceName}}`.

`ArchitectureTest` (package `{{groupId}}`, class package-private; identical in the 3 templates):
- `@AnalyzeClasses(packages = "{{groupId}}", importOptions = { ImportOption.DoNotIncludeTests.class, ArchitectureTest.ExcludeArchTestClasses.class })`
- nested `static final class ExcludeArchTestClasses implements ImportOption` whose `includes(Location l)`
  returns `!l.contains("/archTest/")` (`DoNotIncludeTests` does not recognize the `archTest` output dir,
  and the test class would otherwise be analyzed as part of the app).
- Rules as `@ArchTest @ArchTag("layer-<layer>") static final ArchRule <name> = ...;` with static imports of
  `ArchRuleDefinition.classes/noClasses` and `SlicesRuleDefinition.slices`:
  - `layer-controller`
    - `controllerDoesNotCallRepositoryOrClient`: `noClasses().that().resideInAPackage("..controller..").should().dependOnClassesThat().resideInAnyPackage("..repository..", "..client..")`
    - `controllerNamesEndWithController`: `classes().that().resideInAPackage("..controller..").and().areTopLevelClasses().should().haveSimpleNameEndingWith("Controller")`
  - `layer-service`
    - `serviceDoesNotCallController`: `noClasses().that().resideInAPackage("..service..").should().dependOnClassesThat().resideInAPackage("..controller..")`
    - `serviceNamesEndWithService`: same shape as the controller naming rule with `"..service.."` / `"Service"`
    - `noBusinessPackage`: `noClasses().should().resideInAPackage("..business..")` (no `that()`, so the
      set is never empty; the package is `service`, never `business`)
  - `layer-repository`
    - `repositoryDoesNotCallUpwardsOrSiblings`: `noClasses().that().resideInAPackage("..repository..").should().dependOnClassesThat().resideInAnyPackage("..controller..", "..service..", "..client..")`
    - `repositoryNamesEndWithRepository`
  - `layer-client`
    - `clientDoesNotCallUpwardsOrSiblings`: `noClasses().that().resideInAPackage("..client..").should().dependOnClassesThat().resideInAnyPackage("..controller..", "..service..", "..repository..")`
    - `clientNamesEndWithClient`
  - untagged: `noPackageCycles = slices().matching("(**)").should().beFreeOfCycles();`
- Each rule has a one-line English comment.

`ExternalServiceStubIntTest` (spring-gradle): JUnit 6 + `@WireMockTest`
(`com.github.tomakehurst.wiremock.junit5.WireMockTest`), method takes `WireMockRuntimeInfo`; stub
`stubFor(get("/external/greeting").willReturn(ok("pong")))`; call it with `java.net.http.HttpClient`
at `wmRuntimeInfo.getHttpBaseUrl()`; assert status 200 and body `pong`. Class doc comment: shows how to
simulate an external HTTP service. No Spring context, no other layers.

## Steps

1. Catalogs (`libs.versions.toml` x3) with the pinned versions. Serves AC-12.
2. `sources.gradle` x3 (suites). Serves AC-1, AC-3.
3. `dependencies.gradle` x3 (suite dependencies, WireMock only in spring-gradle). Serves AC-4, AC-11, AC-12.
4. `tests.gradle` x3 (JUnit Platform for all tests, `check` wiring, ordering, exclusion mapping). Serves
   AC-1, AC-2, AC-7, AC-15.
5. `gradle.properties` x3 with the exact exclusion lists. Serves AC-7.
6. `spring-gradle` main/test: `HelloService`, `HelloController` delegation, `HelloControllerTest`
   `@Import`, `HelloServiceTest`. Serves AC-10, AC-13.
7. `archunit.properties` x3 and `ArchitectureTest` x3 (identical source). Serves AC-5, AC-6, AC-7, AC-8, AC-9.
8. Sample integration tests: spring-gradle WireMock test; `MainIntTest` in java-app;
   `{{className}}IntTest` in java-library. Serves AC-1, AC-4.
9. Generated READMEs x3 (English): three suites, commands (`./gradlew test|intTest|archTest|check`),
   source directories, order (`test` first), `archTest.excludeLayers` with layer names and the
   `layer-<layer>` tag convention, WireMock note (spring-gradle). Root `README.md` section and
   `DEVLOG.md` Step 3 entry. Serves AC-14.
10. Local self-check by coder: rebuild image, generate the 4 variants (see Baseline), run
    `./gradlew check` in each; fix. Serves AC-13.

Every AC is covered: AC-1 (2,4,8), AC-2 (4), AC-3 (2), AC-4 (3,8), AC-5 (7), AC-6 (7), AC-7 (4,5),
AC-8 (7), AC-9 (7), AC-10 (6), AC-11 (3), AC-12 (1,3), AC-13 (6,10), AC-14 (9), AC-15 (4).

## Verification plan

Generation recipe (used for baseline and after; `$WT` = java-skeleton worktree, `$OUT` = a scratch dir
under the scratchpad). Build the image from the worktree, then generate 4 variants with Java 25:
```
docker build -t java-skeleton:arq12 $WT
for v in "spring-gradle demo-spring" "java-app demo-app" "java-library demo-lib"; do set -- $v
  docker run --rm -u "$(id -u):$(id -g)" -v "$OUT/<phase>:/work" java-skeleton:arq12 \
    --yes --template $1 --name $2 --group com.acme --artifact $2 --java 25
done
docker run ... --yes --template java-library --name demo-libpub --group com.acme --artifact demo-libpub --java 25 --with-publish
```
`<phase>` = `before` or `after`. Variants: `demo-spring`, `demo-app`, `demo-lib`, `demo-libpub`.

### Baseline (prep, on unmodified `main` before any change)

Save under `tasks/ARQ-12/baseline/`:
1. Generate the 4 variants into `$OUT/before` with the recipe above (image tag `java-skeleton:arq12-base`).
2. Per variant, in the project dir:
   - `./gradlew dependencies --configuration compileClasspath --console=plain -q > baseline/<variant>-compileClasspath.txt`
   - `./gradlew dependencies --configuration runtimeClasspath --console=plain -q > baseline/<variant>-runtimeClasspath.txt`
   - `./gradlew dependencies --configuration testRuntimeClasspath --console=plain -q > baseline/<variant>-testRuntimeClasspath.txt` (reference only)
   - `./gradlew clean check --console=plain > baseline/<variant>-check.txt 2>&1` (shows 1 test each
     and the task list: only `test`, no `intTest`/`archTest`).
   - `find . -path ./build -prune -o -path ./.gradle -prune -o -type f -print | sort > baseline/<variant>-files.txt`
3. For `demo-spring`: build the jar, start it (`java -jar build/libs/*.jar`), `curl -s localhost:8080/hello`
   saved to `baseline/demo-spring-hello.txt` (expected `Hello from demo-spring`), stop the app.
4. `baseline/README.md`: the commands run, Docker image id, `date -u` and `git rev-parse HEAD` of main.

### After (qa, on the implemented worktree; image `java-skeleton:arq12`, output in `$OUT/after`)

Run in each of the 4 variants unless stated. Save outputs under `tasks/ARQ-12/evidence/`.

- AC-1: `./gradlew clean test`, then `./gradlew clean intTest`, then `./gradlew clean archTest` each alone,
  each exits 0. For every suite, `build/test-results/<suite>/*.xml` exists and the summed `tests=` is >= 1
  (record the numbers: expected archTest in java-app/lib = 1 test only (cycles); spring-gradle archTest = 9).
- AC-2: `./gradlew clean check --console=plain` lists `> Task :test`, `> Task :intTest` and
  `> Task :archTest` as executed (not UP-TO-DATE/SKIPPED/NO-SOURCE).
- AC-3: `ls -d src/test src/intTest src/archTest` exist with `.java` files; `./gradlew properties`
  or `./gradlew -q printSourceSets`-equivalent not needed: the per-suite XML directories above plus the
  directory listing are the evidence.
- AC-4: spring-gradle `./gradlew clean intTest` -> `ExternalServiceStubIntTest` passes (XML shows 1 test,
  0 failures). Control (WireMock absent elsewhere): in `demo-app` and `demo-lib`,
  `./gradlew dependencies --configuration intTestRuntimeClasspath -q | grep -ic wiremock` = 0 and the same
  for `testRuntimeClasspath`; in `demo-spring` `testRuntimeClasspath` also has 0 (WireMock only in
  `intTest`). Also `grep -ri wiremock` over `demo-app`/`demo-lib` sources and gradle files finds nothing.
- AC-5: read the generated `ArchitectureTest.java`; `diff` the three generated copies = identical;
  from the archTest XML list the testcase names (rules for each layer, naming rules, `noBusinessPackage`,
  `noPackageCycles`). In `demo-spring` run `./gradlew archTest` with the exclusion overridden to empty
  after temporarily adding empty-layer samples is NOT needed here (see AC-8).
- AC-6: `grep -n 'ArchTag' ArchitectureTest.java` shows `layer-controller|service|repository|client`
  on the layer rules. Filtering proof: `./gradlew clean archTest -ParchTest.excludeLayers=service` in
  `demo-spring` drops exactly the `layer-service` testcases from the XML (controller ones remain);
  repeat with `controller` to drop the controller ones. (`-P` overrides `gradle.properties`.)
- AC-7: `cat gradle.properties` in each variant shows the exact list (spring-gradle
  `repository,client`; app/lib `controller,service,repository,client`). XML for `demo-app` / `demo-lib`
  archTest contains only `noPackageCycles`; `demo-spring` contains controller+service rules and no
  repository/client rules. Control: `-ParchTest.excludeLayers=foo` fails the build with the
  "unknown layer" message.
- AC-8: `demo-spring`: `./gradlew clean archTest -ParchTest.excludeLayers=client` (repository rules now
  run on an empty layer) -> BUILD FAILED with a "failed to check any classes" / empty-should message
  for the repository rules; same with `repository`. Baseline for contrast: the default run is green.
  `archunit.properties` contains `archRule.failOnEmptyShould=true`.
- AC-9 (each control in a throwaway copy of `demo-spring`, each makes `archTest` fail, then is reverted
  and `archTest` is green again):
  1. Add `...client/FooClient.java` (empty class) and make `HelloController` use it -> fails
     `controllerDoesNotCallRepositoryOrClient`.
  2. Add `...service/Helper.java` (class not ending in `Service`) -> fails `serviceNamesEndWithService`.
  3. Add `...business/Foo.java` -> fails `noBusinessPackage`.
  4. Add classes `pkga.A -> pkgb.B -> pkga.A` (packages under the group) -> fails `noPackageCycles`.
  Also the cycle control (4) in `demo-app` to show the general rule works in a template with all layers
  excluded.
- AC-10: `HelloService` is in `.../service/`; `HelloController` source takes `HelloService`; archTest in
  `demo-spring` green; start the app (see AC-13) and `curl /hello` = `Hello from demo-spring`
  (identical to `baseline/demo-spring-hello.txt`); `HelloControllerTest` and `HelloServiceTest` pass.
- AC-11: regenerate with the new image into `$OUT/after`; produce the same four files per variant as in
  the baseline (`compileClasspath`, `runtimeClasspath`) and `diff` against `baseline/` -> no output
  (byte-identical). Also `testRuntimeClasspath` for reference (it may differ only for the suites
  that did not exist; expected unchanged for `test`). Evidence = the diff outputs.
- AC-12: `grep -n 'archunit\|wiremock' gradle/libs.versions.toml` in each variant (versions 1.5.1 /
  3.13.2 only in the catalog; no version literal in `*.gradle` outside the catalog:
  `grep -rn "1.5.1\|3.13.2" gradle/*.gradle` empty). `./gradlew dependencies --configuration
  archTestRuntimeClasspath` resolves ArchUnit 1.5.1 on the generated Java 25 toolchain; all suites green
  (AC-1 results) is the proof of compatibility with Java 25 / Spring Boot 4 / JUnit 6.
- AC-13: for each of the 4 variants `./gradlew clean check` BUILD SUCCESSFUL; `demo-libpub` also
  `./gradlew publishToMavenLocal` OK. `demo-spring`: `./gradlew bootJar`, `java -jar build/libs/*.jar &`,
  `curl -s localhost:8080/hello` = `Hello from demo-spring`, stop the app. `java-app`: `./gradlew run`
  prints the greeting.
- AC-14: `grep -n 'intTest\|archTest\|excludeLayers' README.md` in each generated project, plus
  the repo `README.md` and `DEVLOG.md`; read them: English, mention three suites, how to run each,
  `archTest.excludeLayers`, the layer names, the `layer-<layer>` tag.
- AC-15: from the `check` output in AC-2 (`--console=plain`, no `--parallel`) the line order shows
  `> Task :test` before `> Task :intTest` and `> Task :archTest`. Control: running with
  `./gradlew intTest archTest test` (reverse order on the command line) still executes `test` first
  because of `mustRunAfter`.

## Risks and invariants

Invariants:
- `compileClasspath` and `runtimeClasspath` of every variant byte-identical to baseline (AC-11). Do
  not touch `implementation`/`api`/`runtimeOnly` lines. Only `intTest*` / `archTest*` configurations and
  catalog entries are added.
- Existing `/hello` response, `test` suite, wrapper version (9.5.1), plugin versions, JUnit and Boot
  versions stay as they are.
- Everything written in English.

Risks:
- ArchUnit 1.5.1 with JUnit Platform 6 (Boot 4 BOM / junit-bom 6.1.3): not documented in the POMs.
  If `archTest` does not discover/run, STOP and report as a blocker (options: pin a different
  `archunit-junit5` version, or use plain `archunit` with `@Test` methods plus `@Tag`); do not choose.
- Wrong JUnit versions on the new suites if the BOM platform is not applied to `intTest*`/`archTest*`
  (check `dependencies --configuration intTestRuntimeClasspath`).
- `slices().matching("(**)")` or the `ImportOption` nested class may need syntax adjustment; the
  behavior (one slice per package, non-empty in the flat templates; the archTest classes not analyzed)
  is the contract.
- `ArchTag` excluded via Gradle `excludeTags` must be verified on `@ArchTest` fields (AC-6 filter proof).
- `wiremock-standalone` on JDK 25: verify the sample passes; if not, report (do not switch artifact
  silently).
- `HelloControllerTest` must keep passing after the controller gets a constructor dependency.
- The `docker build` context excludes nothing relevant (`.dockerignore` not changed); `gradle.properties`
  is copied verbatim by `renderDir`.
