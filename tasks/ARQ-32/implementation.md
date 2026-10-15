# ARQ-32 — Implementation plan

Repository: `java-skeleton` (`/home/daniel-jofre/Documentos/Desarrollo/java-skeleton`). Node generator
(`bin/cli.js`, commander ^12.1.0, @inquirer/prompts ^7.2.0, handlebars, fs-extra). No new dependency, so
no version to pin; `package.json` dependencies stay byte-identical (AC-27). Read before working:
`java-skeleton/CONTRIBUTING.md` (verification procedure) and `DEVLOG.md` (entry format).

## Approach

Rewrite `bin/cli.js` around three inputs (type, product, name) and derive everything else; shrink the
templates to what the card keeps. Facts verified in the code:

- `bin/cli.js` today: `-t -n -g -a -j -p -d -y --with-publish`, a `-h`/`-V` built in by commander,
  `manifest.templates[].prompts`, `className` via `toPascalCase`, success `console.log`, `fail()` exit 1,
  `ExitPromptError` -> exit 130, "existing folder" check, empty-`.hbs` skip in `renderDir`, `chmod 0o755`
  on `gradlew`. The last four protections are kept as they are.
- Templates: `spring-gradle` (used by `edge|flow|data|acl`), `java-library` (`lib`), `java-app` (removed).
  `className` is used only in file names/contents of `spring-gradle/.../{{className}}Application.java.hbs`
  and the three `java-library/.../{{className}}*.java.hbs` files. `port` is used in
  `spring-gradle/src/main/resources/application.yml.hbs` and `spring-gradle/README.md.hbs`.
  `withPublish` is used in `java-library/build.gradle.hbs`, `gradle/publish.gradle.hbs`, `README.md.hbs`.
  `javaVersion` is used in both `gradle/java.gradle.hbs` and `spring-gradle/README.md.hbs`.
- `archTest.excludeLayers` lives in each template's `gradle.properties` (`spring-gradle`: `repository,client`;
  `java-library`: `controller,service,repository,client`). They are not touched.

Design decisions taken here (all follow from the criteria, none add scope):

1. **Single place for Java version**: a constant `const JAVA_VERSION = '25';` at the top of `bin/cli.js`,
   passed to templates as `javaVersion`. Template files keep using `{{javaVersion}}`.
2. **Manifest shape**: `templates/manifest.json` becomes `{"types":[{"id","label","template"}, ...]}` with
   the five types in menu order `edge, flow, data, acl, lib`; `edge|flow|data|acl` -> `spring-gradle`,
   `lib` -> `java-library`. The CLI builds the menu and the valid-type list from it. A type is a lib when
   `id === 'lib'`.
3. **Commander setup**: `.version(pkg.version, '--version', ...)` and `.helpOption('--help', ...)` replace
   the built-in `-V`/`-h`; options `--yes`, `--type <type>`, `--name <name>`, `--product <product>` only;
   `.allowExcessArguments(false)` so stray positional arguments are rejected (nothing outside the list).
   Unknown options exit 1 from commander before any file is touched.
4. **Order of checks (all before any file is written)**:
   a. `--type|--name|--product` given without `--yes` -> `fail` (also with a TTY; A6).
   b. no TTY and no `--yes` -> `fail`, message mentions only `--yes --type <type> --name <name> [--product <product>]`
      (and the `docker run -it` hint for interactive mode).
   c. `--yes` mode, validate in this order: type missing; type unknown (message lists valid types); `--product`
      with `lib`; `--product` missing for a service; product pattern; name missing; name pattern. Each is a
      `fail(...)`, exit 1.
   d. Interactive mode: `select` type (choices from the manifest), then (non-lib only) `input` product with
      `validate`, then `input` name with `validate` for the chosen type. A `validate` returning a string makes
      @inquirer re-ask the same question (AC-20). No defaults, nothing else is asked.
   e. Output folder exists -> `fail` (existing message adapted: "choose another name or delete that folder").
5. **Derived values** (output always in `process.cwd()`):
   - service: folder = `<product>-<type>-<name>`; `artifactId` = `<type>-<name>`; `groupId` = `cl.pirca.<product>`;
     `serviceName` = folder.
   - lib: folder = `lib-<name>`; `artifactId` = `lib-<name>`; `groupId` = `cl.pirca.lib.<name>`; `serviceName` = folder.
   - `packagePath` = `groupId` with `.` -> `/`. Template context: `serviceName, groupId, artifactId, javaVersion, packagePath`
     only (`port`, `withPublish`, `className` are removed).
6. **Patterns**: `PRODUCT_RE = /^[a-z][a-z0-9]*$/`, `SERVICE_NAME_RE = /^[a-z][a-z0-9]*(-[a-z0-9]+)*$/`,
   `LIB_NAME_RE = /^[a-z][a-z0-9]*$/`. Remove `GROUP_RE`, `ARTIFACT_RE`, `JAVA_VERSIONS`, `validatePort`,
   `validateJava`, `toPascalCase`, the `confirm` import and `ask()`.
7. **Silence on success**: delete the final `console.log` block (and the `rel` variable). `fail()` stays
   (stderr, exit 1). The `main().catch` handler (130 on `ExitPromptError`) stays.
8. Keep `renderDir`/`renderName` and the "renders empty -> not written" skip; only update its comment (it
   no longer cites `{{#if flag}}`). `renderName` still resolves `{{packagePath}}` in directory names.

## Files

Change in `java-skeleton`:
- `bin/cli.js` — rewrite per the Approach.
- `templates/manifest.json` — new `types` shape, five types, no `java-app`, no `prompts`.
- `templates/spring-gradle/src/main/java/{{packagePath}}/{{className}}Application.java.hbs` — rename (git mv) to
  `Application.java.hbs`; contents: `public class Application`, `SpringApplication.run(Application.class, args)`.
- `templates/spring-gradle/build.gradle.hbs` — `version = '1.0.0'`.
- `templates/spring-gradle/src/main/resources/application.yml.hbs` — remove the `server:`/`port:` block and the blank
  line; keep `spring.application.name: {{serviceName}}`.
- `templates/spring-gradle/README.md.hbs` — replace the line ``The service runs at `http://localhost:{{port}}`.``
  with `The service exposes:` (keep the `GET /hello` bullet). Nothing else changes.
- `templates/java-library/src/main/java/{{packagePath}}/{{className}}.java.hbs` -> `Example.java.hbs`;
  `.../src/test/.../{{className}}Test.java.hbs` -> `ExampleTest.java.hbs`;
  `.../src/intTest/.../{{className}}IntTest.java.hbs` -> `ExampleIntTest.java.hbs` (git mv). In contents replace
  `{{className}}` with `Example`; the javadoc `{{artifactId}}` stays.
- `templates/java-library/build.gradle.hbs` — `version = '1.0.0'`; `id 'maven-publish'` and
  `apply from: 'gradle/publish.gradle'` unconditional (drop both `{{#if withPublish}}` blocks).
- `templates/java-library/gradle/publish.gradle.hbs` — drop only the first and last lines (`{{#if withPublish}}`,
  `{{/if}}`); body, including the commented GitHub Packages block with `{{artifactId}}`, is unchanged (A3).
- `templates/java-library/README.md.hbs` — "Publish" section: keep the `publishToMavenLocal` text and the
  `repositories` sentence, drop `{{#if}}/{{else}}` and the "does not include maven-publish ... `--with-publish`" branch (A1).
- `package.json` — `description` exactly `Generates pirca projects: REST services (edge, flow, data, acl) and libraries`.
  Nothing else (version, keywords, dependencies unchanged; A4).
- `README.md` — rewrite (see Steps 7).
- `CONTRIBUTING.md` — update (see Steps 8).
- `DEVLOG.md` — append one entry at the end (see Steps 9).

Delete: `templates/java-app/` (whole directory).

Check, then handle: `.idea/libraries/gradle_wrapper.xml` references `templates/java-app/gradle/wrapper/gradle-wrapper.jar`.
`.gitignore` does not list `.idea`. Run `git ls-files .idea`: if it is tracked, repoint that path to
`templates/spring-gradle/gradle/wrapper/gradle-wrapper.jar` (forced by the removal, AC-15); if untracked, leave it alone.

Do not touch: `Dockerfile`, `scripts/java-skeleton`, `.github/workflows/release.yml`, `package-lock.json`, any
`gradle/*` file other than those named, any `gradle.properties`, wrapper files, `ArchitectureTest`, `Hello*`,
`ExternalServiceStubIntTest`, `.gitignore.hbs`, `settings.gradle.hbs`, existing DEVLOG entries.

## Steps

1. **Remove `java-app` and reshape the manifest** — AC-15, AC-24. Delete `templates/java-app/`; rewrite
   `templates/manifest.json` (`types` array, labels e.g. `edge`, `flow`, `data`, `acl`, `lib` with a short
   description, `template` field); resolve the `.idea` item above.
2. **Service template changes** — AC-8, AC-10, AC-13, AC-27. Rename `Application.java.hbs`, set `version = '1.0.0'`,
   remove the port from `application.yml.hbs` and `README.md.hbs`.
3. **Library template changes** — AC-9, AC-10, AC-11, AC-12. Rename the three `Example*` files and update contents,
   `build.gradle.hbs`, `publish.gradle.hbs`, `README.md.hbs` as listed under Files.
4. **Rewrite `bin/cli.js`** — AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-14, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21.
   Implement decisions 1-8. Description string for `.description()`: the same text as the package.json description.
5. **`package.json` description** — AC-25.
6. **Self-check before handing over** (coder runs it, qa re-runs it independently): rebuild the image and generate
   `--yes --type data --product gastos --name expense` and `--yes --type lib --name errors` into a temp dir; run
   `./gradlew build` in both. Then `grep -rniE "java-app|--port|server\.port|localhost:|with-publish|className|withPublish" `
   over the repo (excluding `.git`, `node_modules`, old DEVLOG entries) must be empty — AC-13, AC-15.
7. **`README.md`** — AC-22. Sections only: intro (what it is, five types, wrapper embedded), "Usage with Docker"
   (interactive `docker run --rm -it ...`; non-interactive with
   `--yes --type data --product gastos --name expense`; keep the `-it`, `-u`, `-v` bullets), "Short alias"
   (`java-skeleton` interactive and `java-skeleton --yes --type lib --name errors`), "Usage with npx / npm"
   (keep the existing `npm create java-service@latest` / `npx java-skeleton` lines; A4), and "Usage" (final
   interface: the two modes, `--yes --type <t> --name <n> [--product <p>]`, `--help`, `--version`, the table of
   five types -> templates, what is derived: folder/artifact/group/package). Remove the "Flags", "Generated project:
   test suites" and "Development" sections (including the trailing release/DEVLOG lines). No mention of port,
   removed flags, or `java-app`.
8. **`CONTRIBUTING.md`** — AC-23. Update: templates are `spring-gradle` and `java-library` (types -> templates in
   `manifest.json`); variables `groupId, artifactId, serviceName, javaVersion, packagePath` (no `className`);
   the Java version lives in `JAVA_VERSION` in `bin/cli.js`; replace the `publish.gradle.hbs` / `--with-publish`
   empty-render example with the general rule (an `.hbs` that renders empty is not written; no current template
   relies on it); "How to verify a change" keeps its 4 steps, step 3 becomes `--yes --type data --product gastos --name expense`
   (and the lib command), "use JDK 25" derived from `JAVA_VERSION`; the variant rule becomes exactly two variants:
   one service type (`spring-gradle`, e.g. `data`) and `lib` (publishing always on). Same prohibitions as AC-22.
9. **`DEVLOG.md`** — AC-26. Append at the end, after the ARQ-28 entry, a section
   `## <date> — ARQ-32: pirca generator (type, product, name)` with **What:** / **Why:** / **Verification:**
   (and **Unchanged:** if useful), same style as the existing entries. Do not modify any existing byte.
   Mention of `java-app` is allowed here (history).

## Verification plan

All runs use the Docker image as in `CONTRIBUTING.md` (the image copies `templates/`; rebuild after every change).
JDK 25 on the host for `./gradlew`. Scratch dirs under the session scratchpad, never inside the repo. A local
`node_modules` does not exist in java-skeleton, so do not rely on `node bin/cli.js` on the host; use the image.
For TTY-driven cases use a pty: `python3 -I` script (kept outside the generated dirs) that spawns
`docker run --rm -it -u ... -v $D:/work java-skeleton:dev` with `pty`, writes keystrokes and reads output;
`\x03` for Ctrl-C. Run non-TTY cases with `docker run --rm -i` (no `-t`) or without `-it`.

### Baseline (run by prep, on `main` before any change; save under `tasks/ARQ-32/baseline/`)

1. `git -C java-skeleton ls-files` > `files-before.txt`; `git status --short` > `status-before.txt`.
2. `sha256sum` of the files that must not change (AC-27): `Dockerfile`, `scripts/java-skeleton`,
   `.github/workflows/release.yml`, `package-lock.json`, every `templates/*/gradlew*`, `gradle/wrapper/*`,
   `gradle.properties`, `gradle/*.gradle`/`libs.versions.toml` (all that are not `.hbs` and not renamed), and all
   `src/archTest`, `src/intTest/.../ExternalServiceStub*`, `Hello*` templates > `unchanged-sha256.txt`.
3. Copy of the current `DEVLOG.md` as `DEVLOG.before.md` (for AC-26 prefix comparison).
4. Old `--help` output: `docker run --rm java-skeleton:dev --help` > `help-before.txt` (image built from `main`).
5. Generate with the old CLI, build, and capture dependency resolution so "identical" is checkable:
   - `--yes --template spring-gradle --name demo --group cl.pirca.gastos --artifact data-expense --java 25`
   - `--yes --template java-library --name demo --group cl.pirca.lib.errors --artifact lib-errors --java 25 --with-publish`
   For each: `find . -type f | sort` > `<id>-files.txt`; `sha256sum` of all files > `<id>-sha256.txt`;
   `./gradlew build` > `<id>-build.txt`; `./gradlew dependencies --configuration compileClasspath`,
   `runtimeClasspath`, `testRuntimeClasspath` (and `intTestRuntimeClasspath`, `archTestRuntimeClasspath`) >
   `<id>-<config>.txt`; for the lib also `./gradlew publishToMavenLocal` > `lib-errors-publish.txt`.
   Use ids `spring` and `lib`.
6. Record the `archTest.excludeLayers` line of each template (`grep -H excludeLayers templates/*/gradle.properties`)
   > `excludeLayers-before.txt`.

### After (run by qa; one evidence item per AC; save under `tasks/ARQ-32/evidence/`)

Setup: rebuild the image from the `feature/ARQ-32` worktree (`docker build -t java-skeleton:dev .`); `D=$(mktemp -d)`
in the scratchpad. `RUN="docker run --rm -u $(id -u):$(id -g) -v $D:/work java-skeleton:dev"`. After every
failing case check `ls -A $D` is empty (or unchanged) and the exit code is `!= 0`.

- **AC-1**: `$RUN --help` lists exactly `--yes`, `--type`, `--name`, `--product`, `--help`, `--version` (diff against
  `help-before.txt` shows the old ones gone). Loop over `--group x --artifact x --java 25 --port 80 --dir /x
  --with-publish --template spring-gradle -t -n -y -p -g -a -j -d -h -V`: each exits `!= 0`, prints "unknown option",
  `$D` stays empty (`-h`/`-V` must not print help/version and exit 0). `$RUN --version` equals `version` in `package.json` (0.1.0).
- **AC-2**: `$RUN --yes --type data --product gastos --name expense` exits 0, no prompt, folder created. Without
  TTY and without `--yes`: `docker run --rm -i ... java-skeleton:dev </dev/null` exits `!= 0`, `$D` empty, the message
  contains `--yes`, `--type`, `--name`, `--product` and none of `--template --group --artifact --java`.
- **AC-3**: `--type data`, `--name x`, `--product gastos` each alone, and `--type lib --name errors`, without `--yes`,
  both without TTY and under the pty (`-it`): clear error, exit `!= 0`, `$D` empty.
- **AC-4**: pty session: the first prompt is a list with exactly `edge flow data acl lib`; choosing `data` gives next
  prompt product, then name; choosing `lib` skips product (type -> name). No other prompt appears. Capture the
  transcript.
- **AC-5**: generate `gastos` / `data` / `expense`: folder `gastos-data-expense` in cwd; `settings.gradle` has
  `rootProject.name = 'data-expense'`; `build.gradle` `group = 'cl.pirca.gastos'`; sources under
  `src/main/java/cl/pirca/gastos/` with `package cl.pirca.gastos;`; `application.yml` has
  `name: gastos-data-expense`; README title `# gastos-data-expense`. Repeat with `edge`, `flow`, `acl` (folder and
  artifact change, `diff -r` of the four trees only differs in names).
- **AC-6**: `--yes --type lib --name errors`: folder `lib-errors`; `rootProject.name = 'lib-errors'`; `group = 'cl.pirca.lib.errors'`;
  `package cl.pirca.lib.errors;` in main/test/intTest/archTest; README title `# lib-errors`; `./gradlew publishToMavenLocal`
  publishes `cl/pirca/lib/errors/lib-errors/1.0.0` in `~/.m2` (use `-Dmaven.repo.local` pointing at a scratch dir).
- **AC-7**: `grep -n "JAVA_VERSION" bin/cli.js` shows one definition; generated `gradle/java.gradle` has
  `JavaLanguageVersion.of(25)` for service and lib; `grep -rn "'25'\|\b25\b" bin/cli.js` shows no second place.
  Control: change `JAVA_VERSION` to `'21'` in a scratch copy of the repo, rebuild a scratch image tag, regenerate:
  `java.gradle` shows `of(21)`.
- **AC-8**: generated service has `Application.java` in `src/main/java/cl/pirca/gastos/` (no `ExpenseApplication` or
  other prefix, `find -name '*Application*'` returns one file); `./gradlew build` exits 0 > `service-build.txt`.
  Compare file list with `spring-files.txt` baseline: only names/packages differ, plus `Application.java`; example
  classes (`HelloController`, `HelloService`, tests, `ExternalServiceStubIntTest`) have the same sha256 once the
  baseline groupId is aligned (baseline used `cl.pirca.gastos`, so hashes are directly comparable).
- **AC-9**: generated lib has `Example.java`, `ExampleTest.java` (src/test), `ExampleIntTest.java` (src/intTest);
  `./gradlew build` exits 0 and its output/test reports show `ExampleTest` and `ExampleIntTest` executed.
- **AC-10**: `grep -n "version = " build.gradle` -> `version = '1.0.0'` in service and lib.
- **AC-11**: lib has `gradle/publish.gradle`, `build.gradle` contains `id 'maven-publish'` and
  `apply from: 'gradle/publish.gradle'`, no `{{`; `./gradlew publishToMavenLocal` exits 0 and the jar/pom for
  version 1.0.0 exist. Lib README Publish section has no `--with-publish` text. Compare against `lib-errors-sha256.txt`
  baseline: `gradle/publish.gradle` identical.
- **AC-12**: `./gradlew check` exits 0 in the service and lib (`archTest`, `intTest`, `test` all executed; show task
  lines). `diff` of `grep excludeLayers templates/*/gradle.properties` against `excludeLayers-before.txt` is empty
  (apart from the removed java-app line). Also run `check` for one more service type (`edge`) to cover "every
  generated variant".
- **AC-13**: `grep -rniE "port|localhost" ` over each generated tree (service and lib), excluding `gradlew*` and the
  wrapper jar: no port reference (`server.port`, `localhost:`); `application.yml` is exactly
  `spring:\n  application:\n    name: gastos-data-expense`. Same grep over the repo's README/CONTRIBUTING/templates.
  (Review any hit of the bare word "port" such as "import"; match word `\bport\b` and `server.port`.)
- **AC-14**: success run (`--yes ...`): stdout and stderr both empty (`docker run ... >out 2>err; wc -c out err` = 0).
  Note: in a TTY the @inquirer prompts necessarily echo the questions; AC-14 is verified in `--yes` mode, and in the
  pty run check that nothing is printed after the last answer (no "created"/"cd"/"./gradlew build" text).
- **AC-15**: `test ! -e templates/java-app`; `$RUN --yes --type java-app --name x --product p` -> "unknown type", exit
  `!= 0`, `$D` empty; `git grep -n "java-app"` returns hits only in `DEVLOG.md` old entries and in the new DEVLOG entry
  (if it names it). Also `grep -rn java-app .idea` as appropriate. Control: `git grep` on `main` shows the hits that
  disappeared.
- **AC-16**: create `$D/gastos-data-expense/marker.txt`, run the same generate command: exit `!= 0`, message names the
  folder; `find` + `sha256sum` of the folder identical before/after.
- **AC-17**: pty session: send `\x03` at the type prompt, at the product prompt and at the name prompt (three runs);
  each exits with code 130 (the `docker run` returns 130 for the container's 130) and `$D` is empty.
- **AC-18**: (a) control for the empty skip: scratch copy of the repo with an extra template file
  `templates/spring-gradle/EMPTY.txt.hbs` containing only `{{#if never}}x{{/if}}`; rebuild a scratch image tag,
  generate: `EMPTY.txt` is absent, other files present. (b) `stat -c %a gradlew` in the generated service and lib
  is `755` (and the template's own `gradlew` is not relied on).
- **AC-19**: with `--yes`, each of these exits `!= 0` with a message naming the cause and leaves `$D` empty:
  `--type java-app`, `--type bc`, `--type mc`, `--type foo`; no `--type`; no `--name`; `--type data --name x` (no
  product); `--type lib --name x --product p`; `--type data --product Gastos --name x`; `--product 1gastos`;
  `--product gas-tos`; `--type data --product p --name Expense`; `--name expense_x`; `--type lib --name my-lib`;
  `--type lib --name Errors`; `--yes` alone; empty value `--name ""`.
- **AC-20**: pty: at the product prompt type `Gastos<Enter>` -> error text and the same question is shown again; then
  `gastos`; at the name prompt type `Expense`, re-asked, then `expense-claims`; for lib, type `my-lib` -> re-asked,
  then `errors`. Final folder `gastos-data-expense-claims` / `lib-errors` exist only after the valid answer;
  before it `$D` is empty (check via a second run that is interrupted with Ctrl-C after the invalid answer).
- **AC-21**: positive: `gastos`/`expense-claims` (service) and lib `errors` generate (exit 0); negatives listed
  under AC-19 each fail. Boundary controls: product `a`, name `a1-b2`; name `a--b`, `a-`, `-a` fail.
- **AC-22**: `README.md` headings are exactly: title/intro, Docker, alias, npx/npm, final interface (`grep -n '^#'`);
  `grep -nE "Flags|test suites|Development|--port|server\.port|localhost|--java|--group|--artifact|--dir|--template|--with-publish|java-app|-y\b|-t\b"`
  returns nothing; each command shown in the README is executed once against the image (the Docker non-interactive
  example and the alias example flags), exit 0.
- **AC-23**: same grep on `CONTRIBUTING.md`; it names `spring-gradle` and `java-library`, variables list has no
  `port`, `withPublish`, `className`; verification examples use `--yes --type ... --name ... [--product ...]`;
  "How to verify a change" has exactly two variants. Execute its steps literally in a fresh scratch dir: build image,
  generate both variants, `./gradlew build` green.
- **AC-24**: `templates/manifest.json` parses (`node -e` in a `node:22-alpine` container, or `python3 -I -m json.tool`);
  contains the five ids with their template; `spring-gradle` for four, `java-library` for `lib`; no `java-app`.
- **AC-25**: `python3 -I -c` / `jq -r .description package.json` equals
  `Generates pirca projects: REST services (edge, flow, data, acl) and libraries`; `git diff main -- package.json` shows
  only that line.
- **AC-26**: `cmp` the first `wc -c DEVLOG.before.md` bytes of the new `DEVLOG.md` with `DEVLOG.before.md`: identical;
  `git diff main -- DEVLOG.md` is purely additions (no `-` lines other than the header); exactly one new `## ` heading.
- **AC-27**: `git diff --stat main` lists no change to `Dockerfile`, `scripts/java-skeleton`,
  `.github/workflows/release.yml`, `package-lock.json`, any `gradlew*`/wrapper, any `gradle.properties`,
  `gradle/dependencies.gradle`, `libs.versions.toml`, `constraints.gradle`; `sha256sum -c unchanged-sha256.txt`
  passes (rename of the template `Application`/`Example*` files excepted); compare generated
  `compileClasspath`, `runtimeClasspath`, `testRuntimeClasspath`, `intTestRuntimeClasspath`, `archTestRuntimeClasspath`
  of the new service and lib with the baseline files: `diff` empty (only the project-name header line may differ;
  use `diff <(sed 1,3d a) <(sed 1,3d b)` or filter the first lines). Example endpoint check: run the generated
  service jar (`./gradlew bootRun`, then `curl localhost:8080/hello` -> `Hello from gastos-data-expense`; Spring's default port).
  Remember to stop it.

Control tests for negative claims: AC-1 (a flag that exists in the old image is accepted there, rejected now:
`docker run main-image -t spring-gradle` works before, fails after — use a baseline image tag `java-skeleton:base`
built by prep from `main`), AC-13 (old generated tree contains `server.port` and `localhost:8080`, the new one does
not), AC-15 (old image accepts `--template java-app`).

## Risks and invariants

- Must not change (AC-27): dependencies and versions, `archTest.excludeLayers`, Gradle wrapper, Dockerfile,
  `scripts/java-skeleton`, `release.yml`, existing DEVLOG bytes, package.json fields other than `description`,
  and the example classes of `spring-gradle` other than `Application.java`.
- Resolved dependencies of the generated service and lib must be identical to the baseline (same templates for
  `gradle/dependencies.gradle`, `libs.versions.toml`, `constraints.gradle`).
- The four service types use the same template, so `data` gets `excludeLayers=repository,client` (no `repository`
  layer), as the card states "unchanged". That is intended, not a defect to fix here.
- AC-14 vs interactive mode: @inquirer prompts print the question and answer in a TTY. The criterion is verified in
  `--yes` mode plus "nothing after the last answer"; if the user reads AC-14 as "no output at all even in interactive
  mode", that needs a new decision (it is not achievable with prompts as they are).
- Commander: with `.helpOption('--help')`, `-h` must be rejected as unknown (verify, do not assume); `--version`
  must keep working. If commander 12.1 does not accept `.version(v, '--version')` for dropping `-V`, report it
  rather than inventing a workaround.
- `.allowExcessArguments(false)` is an implementation detail enforcing "nothing outside the list"; verify
  `java-skeleton foo` fails with code != 0.
- A product like `int` or `class` passes the pattern but is a Java keyword (invalid package). The card gives the
  patterns and does not mention reserved words; not handled (out of scope).
- Ctrl-C exit code 130 must be observed from the container exit code through `docker run -it`; if Docker maps it
  differently, check the process exit code with the generator run under the pty with a Node container
  (`docker run -it --entrypoint node` is not needed; the entrypoint already is `node cli.js`).
- No Bash was available to the architect, so the `.idea` tracked/untracked state and the git state of
  `java-skeleton` were not checked; prep/coder must check them first.
