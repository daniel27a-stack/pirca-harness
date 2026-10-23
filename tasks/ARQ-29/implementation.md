# ARQ-29 — Implementation plan

Repo: `/home/daniel-jofre/Documentos/Desarrollo/java-skeleton` (generator; Java lives in templates).
No new libraries, so no version pinning (ArchUnit stays at 1.5.1).

## Approach
Add four inverse naming rules to the single `ArchitectureTest.java.hbs` (identical in both
templates; keep them identical). Each rule sits in its layer's section, next to the existing
`*NamesEndWith*` rule, and carries the same `@ArchTag("layer-<layer>")`, so `archTest.excludeLayers`
already disables it with no build change.

Rule shape (controller shown):

```java
// Top-level classes named *Controller live in the controller package.
@ArchTest
@ArchTag("layer-controller")
static final ArchRule controllerClassesLiveInControllerPackage = classes()
        .that().haveSimpleNameEndingWith("Controller").and().areTopLevelClasses()
        .should().resideInAPackage("..controller..")
        .allowEmptyShould(true);
```
Same for `Service`/`..service..` (`serviceClassesLiveInServicePackage`), `Repository`/`..repository..`
(`repositoryClassesLiveInRepositoryPackage`), `Client`/`..client..` (`clientClassesLiveInClientPackage`).

Decision on A6 (empty set): the set "classes with this suffix" is legitimately empty in a clean
project (e.g. a `data` service has no `*Client`), and an empty set here means "no stray class",
which is a pass. So these four rules use `.allowEmptyShould(true)` per rule, overriding the global
`archRule.failOnEmptyShould=true`. The existing layer rules keep failing on an empty layer (unchanged).
This does not weaken the convention "layer rules never pass silently on an empty layer": that
concerns the layer being present, which the existing rules still check.

Why this matches the ACs: `resideInAPackage("..x..")` matches the package or any sub-package (AC-3);
`haveSimpleNameEndingWith` is suffix on simple name (AC-4); `areTopLevelClasses()` skips nested (AC-5);
no package-less filter, so root-package classes are flagged (AC-1). `import` lines already present
(`classes`, `ArchTag`, `ArchTest`, `ArchRule`): no new imports.

## Files
Change (only these, plus DEVLOG):
- `templates/spring-gradle/src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs` — 4 rules.
- `templates/java-library/src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs` — same 4 rules.
- `templates/spring-gradle/README.md.hbs` (lines 37-38) and `templates/java-library/README.md.hbs`
  (lines 23-24) — in "Architecture tests", extend the sentence, e.g.:
  "`ArchitectureTest` enforces the layered design `controller -> service -> repository | client`
  (naming, in both directions: a class in a layer package has that layer's suffix, and a class with
  a layer's suffix lives in that layer's package; no upward calls, no `business` package) and forbids
  package cycles." Keep it short; do not touch the tag/excludeLayers text.
- `DEVLOG.md` — entry per its format (docs stage; what, why, verification).
Do not touch: `CONTRIBUTING.md`, `README.md`, `gradle/*`, `gradle.properties`, `bin/cli.js`, the
existing rules.

## Steps
1. Edit the spring-gradle `ArchitectureTest.java.hbs`: add each inverse rule right after the
   corresponding `...NamesEndWith...` rule, inside its section. (AC-1..AC-6)
2. Copy the identical change into the java-library template; verify the two files are identical
   with `diff`. (AC-2, AC-6)
3. Update both generated READMEs as described. (AC-9)
4. DEVLOG entry (docs stage). (AC-10)

## Verification plan
All shell snippets are plain commands; where a loop is needed use `bash -c '...'`.

### Baseline (prep, before any change)
1. `git -C <repo> status --short` and `git -C <repo> rev-parse HEAD` → `baseline/git.txt`.
2. `docker build -t java-skeleton:dev .` in the repo; save tail of output.
3. `D=$(mktemp -d)`; generate both variants per CONTRIBUTING.md
   (`--yes --type data --product gastos --name expense`; `--yes --type lib --name errors`).
4. In each generated project run `./gradlew archTest` → `baseline/archTest-data.txt`,
   `baseline/archTest-lib.txt` (expected: BUILD SUCCESSFUL).
5. Control for the problem: in the `data` project add `src/main/java/cl/pirca/gastos/StrayController.java`
   (`package cl.pirca.gastos; class StrayController {}`; check the real package under `src/main/java`),
   run `./gradlew archTest` → `baseline/archTest-data-stray.txt` (expected today: passes). Remove the file.
6. Save `ArchitectureTest.java` of each generated project as `baseline/ArchitectureTest-<variant>.java`.

### After (qa)
Rebuild the image first (the image holds a copy of the templates), regenerate both variants into a
new temp dir. Each stray class is added alone, `./gradlew archTest` run, file removed.
Stray files go under `src/main/java/<package path>/` of the data project.

- AC-1: root-package `StrayController`, then `StrayService` → archTest fails (BUILD FAILED), output
  names `StrayController` / `StrayService`. Control: baseline step 5 passed.
- AC-2: temporarily set `archTest.excludeLayers=` (empty) in the temp data project's
  `gradle.properties` (read the file first to see the real key format) so all four layers are active;
  add stray `StrayRepository` and `StrayClient` (root package) one at a time → each fails naming the class.
  Also controller and service again with all layers active.
- AC-3: `UserService` inside `...controller` package → fails (inverse rule; the existing
  controller-naming rule would also fail, so confirm the output names `resideInAPackage("..service..")`
  violation). `FooController` inside `...controller.sub` → passes.
- AC-4: `UserServiceImpl` in root package → passes; `StrayController` → fails (AC-1).
- AC-5: root-package `class Outer { static class InnerController {} }` → passes.
- AC-6: `grep -c 'ArchTag("layer-' ` on generated test: each new rule has the same tag as its layer
  (`grep -n -B3 'LiveIn' ...`). With default excludes, stray `StrayClient` passes in the data project if
  `client` is excluded by default there (read gradle.properties to confirm) and fails after
  removing `client` from `archTest.excludeLayers`. In the `lib` project (all layers excluded by
  default) stray `StrayController` passes.
- AC-7: `diff` of old vs new `ArchitectureTest.java.hbs` (`git diff` in the repo) shows only added lines
  in the rule section; `git diff --stat` shows no change in `gradle.properties`/`gradle/` files.
- AC-8: unmodified `data` and `lib` projects: `./gradlew build` and `./gradlew archTest` → BUILD
  SUCCESSFUL (also proves allowEmptyShould works for empty suffix sets). Expected test counts only for
  default configuration if reported: not asserted.
- AC-9: `git diff` of both README templates shows the naming sentence extended; `sed -n` of the generated
  READMEs shows it; `git diff --stat` shows no change in `CONTRIBUTING.md`.
- AC-10: `git diff --name-only main...HEAD` lists exactly the 4 template files and `DEVLOG.md`.

## Risks and invariants
- Without `.allowEmptyShould(true)`, a clean `data`/`lib` project would fail (empty set); AC-8 catches it.
  If the ArchUnit 1.5.1 API lacks that method on `ArchRule` the build fails visibly (it exists since 0.23).
- The two `ArchitectureTest.java.hbs` files must stay identical.
- Existing rules, tags, `gradle.properties` keys, default `excludeLayers`, resolved dependencies unchanged.
- Handlebars: the added Java contains no `{{`; no escaping needed.
- Generated projects and temp strays live only in `mktemp` dirs; never commit them.
