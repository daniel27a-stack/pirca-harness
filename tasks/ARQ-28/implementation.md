# ARQ-28 — Implementation plan

## Approach
Documentation-only card: create one root `CLAUDE.md` in java-skeleton (`/home/daniel-jofre/Documentos/Desarrollo/java-skeleton`).
No generator, template, Dockerfile, CI, script or README change (AC-9). The only other change in
that repo is the DEVLOG entry added later by the docs stage (not by coder).

Facts confirmed in the repo (the file must state only these; every claim is re-checked in QA):
- `bin/cli.js` is the entry point (Node ESM; `commander`, `handlebars`, `fs-extra`, `@inquirer/prompts`).
  Templates are listed in `templates/manifest.json`: `spring-gradle`, `java-app`, `java-library`.
- `renderDir` (cli.js ~L107-131): `.hbs` files are compiled with Handlebars (`noEscape: true`); the
  `.hbs` suffix is stripped by `renderName` (also from directory names); `{{token}}` in file or
  directory names is replaced from the context (`\w+` keys, unknown key becomes empty); a rendered
  result that is empty after `trim()` is NOT written (L123-124); files without `.hbs` are copied
  verbatim (`fs.copyFile`), e.g. `gradlew`, `gradle/wrapper/gradle-wrapper.jar`.
- Context variables (cli.js L158-167): `serviceName`, `groupId`, `artifactId`, `javaVersion`, `port`,
  `withPublish`, `packagePath` (groupId with `.` -> `/`), `className` (PascalCase of artifactId).
  Existing names with tokens: `templates/spring-gradle/src/main/java/{{packagePath}}/{{className}}Application.java.hbs`,
  `templates/java-app/src/main/java/{{packagePath}}/Main.java.hbs`.
- Optional-file example: `templates/java-library/gradle/publish.gradle.hbs` is wholly wrapped in
  `{{#if withPublish}}...{{/if}}`; `withPublish` is true only with `--with-publish` (cli.js L152-156;
  only the `java-library` template lists `withPublish` in `prompts`).
- Non-interactive: without a TTY, `--yes` is mandatory (cli.js L44). With `--yes` defaults are:
  template = first in manifest (`spring-gradle`), name `my-service`, group `com.example`, java `25`, port `8080`.
- `Dockerfile` copies `bin` and `templates` into the image (`COPY templates ./templates`) -> image holds
  a copy; rebuild after any template change. `.dockerignore` excludes `*.md`, so `CLAUDE.md` never enters the image.
- README "Development" flow: `docker build -t java-skeleton:dev .`, `D=$(mktemp -d)`, `docker run --rm -u "$(id -u):$(id -g)" -v "$D:/work" java-skeleton:dev --yes --template ... --name ... --group ... --artifact ... --java 25`, then `cd "$D/<artifact>" && ./gradlew build`.
- Existing files: `README.md`, `DEVLOG.md`, `Dockerfile`, `.dockerignore`, `package.json`, `scripts/java-skeleton`,
  `.github/workflows/release.yml`. There is NO `CLAUDE.md` and no `.claude/` today.
- Conventions: pirca-harness `pirca-conventions` skill (name verified in `.claude/skills/pirca-conventions`).

Style: English, concise orientation guide (well under ~120 lines), no long copies of the README
(AC-7): point to `README.md` for usage/flags and `DEVLOG.md` for changes/decisions.

## Files
- Create: `CLAUDE.md` (root of the java-skeleton worktree). Nothing else is changed by coder.
- (Docs stage, later) `DEVLOG.md`: one entry following its existing format (`## <date> — <title>` with
  What / Why / Verification). Not part of coder steps.

## Steps
All steps are done by coder in the java-skeleton worktree created by prep.

1. Write `CLAUDE.md` with these sections in this order (AC-1, AC-2, AC-7):
   - Title + "What this repo is": a project **generator** (not a product application), implemented in
     Node, entry point `bin/cli.js`, producing projects from `templates/` (`spring-gradle`, `java-app`,
     `java-library`, registered in `templates/manifest.json`). Pointers: usage and flags -> `README.md`;
     changes and decisions -> `DEVLOG.md`.
2. Section "How templates work" with the six points (AC-3), each matching the Approach facts above:
   (a) `.hbs` extension, removed in output; (b) `{{packagePath}}` in directory names, example path
   `templates/spring-gradle/src/main/java/{{packagePath}}/`, resolved to the package path;
   (c) optional files/blocks with `{{#if}}`; (d) an `.hbs` that renders empty is not written; example
   `templates/java-library/gradle/publish.gradle.hbs` is NOT written without `--with-publish`, written with it;
   (e) files without `.hbs` copied verbatim (`gradlew`, `gradle-wrapper.jar`);
   (f) variables list exactly `groupId`, `artifactId`, `serviceName`, `javaVersion`, `port`, `withPublish`,
   `className`, `packagePath`; `{{className}}` also used in file names (`{{className}}Application.java.hbs`).
3. Section "How to verify a change" as an ordered, runnable list (AC-4, AC-5, AC-6), commands copied from the
   README "Development" section and flags (no new flags):
   1. `docker build -t java-skeleton:dev .`
   2. `D=$(mktemp -d)` (temporary directory; never generate inside the repo, never commit generated projects)
   3. generate with the image in `--yes` mode, one command per affected variant, e.g.
      `docker run --rm -u "$(id -u):$(id -g)" -v "$D:/work" java-skeleton:dev --yes --template spring-gradle --name demo --group com.acme --artifact demo --java 25`
   4. `cd "$D/<artifact>" && ./gradlew build` (wrapper is embedded; only a JDK is needed).
   Also state: the image contains a copy of `templates/` -> rebuild after changing a template, otherwise the old
   version is verified; full verification = 4 variants (`spring-gradle`, `java-app`, `java-library`,
   `java-library` with `--with-publish`), all generated and built when a shared aspect changes; a template is
   not verified until its generated project builds. Use distinct `--artifact` names per variant
   (e.g. `demo-spring`, `demo-app`, `demo-lib`, `demo-lib-pub`) so they coexist in `$D`.
4. Section "Scope for agents" (AC-8), literally titled `## Scope for agents`:
   - what this is: a generator, not a product application;
   - edited: templates under `templates/`; generator code (`bin/cli.js`) only when the change is to the
     generator itself; `README.md` and `DEVLOG.md`, updated in every change following their existing format;
   - not touched: generated projects, and `bin/cli.js` unless the change is to the generator;
   - load the `pirca-conventions` skill.
5. Self-check before finishing (AC-6): every path, flag and command named in the file exists (use Glob/Grep;
   do not mention `scripts/` or `release.yml` unless verified, and do not mention any nonexistent option).
   `git status` in the worktree must show only `CLAUDE.md` as new/changed. Commit as
   `ARQ-28: Add CLAUDE.md with generator context` (author email per CLAUDE.md of pirca-harness).

AC coverage: AC-1 steps 1,5; AC-2 step 1; AC-3 step 2; AC-4 step 3; AC-5 step 3; AC-6 steps 3,5;
AC-7 steps 1,5; AC-8 step 4; AC-9 step 5.

## Verification plan

### Baseline (run by prep before any change, in the java-skeleton worktree; save under `tasks/ARQ-28/baseline/`)
Doc-only change, so the baseline proves "generator output is identical" afterwards.
1. `git -C <worktree> ls-files -s > baseline/tracked-files.txt` (tracked files with blob hashes) and
   `git -C <worktree> status --short > baseline/status.txt` (expected empty).
2. `test ! -e <worktree>/CLAUDE.md && echo absent > baseline/claude-md.txt`.
3. `docker build -t java-skeleton:base <worktree>` (tag `base`, to avoid clobbering `dev`).
4. For the 4 variants, generate into a temp dir `B=$(mktemp -d)` with `docker run --rm -u "$(id -u):$(id -g)" -v "$B:/work" java-skeleton:base --yes ...`:
   `--template spring-gradle --artifact demo-spring`, `--template java-app --artifact demo-app`,
   `--template java-library --artifact demo-lib`, `--template java-library --artifact demo-lib-pub --with-publish`
   (all with `--name demo --group com.acme --java 25`; if the host lacks JDK 25 use the SDKMAN JDK `25.0.4-tem`
   noted in DEVLOG). Save `cd "$B" && find . -type f | sort | xargs sha256sum > baseline/generated-<variant>.sha256`
   per variant (exclude `build/` and `.gradle/` by recording before building).
5. Build each: `cd "$B/<artifact>" && ./gradlew build` and save the tail of each output to
   `baseline/build-<variant>.txt` (expected `BUILD SUCCESSFUL`).

### After (run by qa in the same worktree)
Per-AC evidence:
- AC-1: `test -f CLAUDE.md`; `git ls-files --error-unmatch CLAUDE.md` (after the commit) succeeds; read file: English only
  (no Spanish text; `Grep` for common Spanish words such as ` el | la | de | que ` returns nothing relevant).
- AC-2: Grep the file for `generator`, `bin/cli.js`, `templates/`, `spring-gradle`, `java-app`, `java-library`, and "not a product
  application" (or equivalent) -> all present; `test -f bin/cli.js`; ids match `templates/manifest.json`.
- AC-3: for each of (a)-(f) locate the sentence in the file and confirm against code:
  (a)(e) `Grep "endsWith('.hbs')" bin/cli.js` and `slice(0, -4)`, `copyFile`; (b) `Glob "templates/spring-gradle/src/main/java/{{packagePath}}/*"` finds a file;
  (c) `Grep "{{#if" templates/java-library/gradle/publish.gradle.hbs`; (f) the variable list in the file equals the `context` object in
  `bin/cli.js` (8 names) and `Glob "templates/spring-gradle/src/main/java/{{packagePath}}/{{className}}Application.java.hbs"` exists.
  (d) **runtime proof with control**: generate `java-library` WITHOUT `--with-publish` into a temp dir and
  `test ! -e <out>/demo-lib/gradle/publish.gradle` (not written); generate WITH `--with-publish` and
  `test -s <out>/demo-lib-pub/gradle/publish.gradle` (written, non-empty). Also `test -x gradlew` and `gradle/wrapper/gradle-wrapper.jar`
  byte-identical to the template (`cmp`) for (e).
- AC-4: execute, in order, the exact commands written in `CLAUDE.md` (copy them literally from the file, with `$D=$(mktemp -d)`):
  image builds; generation succeeds for each variant in `--yes` mode; `./gradlew build` ends `BUILD SUCCESSFUL`. Confirm
  the commands equal the README "Development" section (diff by eye) and use only flags listed in the README Flags table.
  Confirm the file states: image holds a copy of `templates/` (cross-check `Dockerfile` line `COPY templates ./templates`), rebuild required,
  temporary directory, generated projects not committed. Control for the rebuild claim: edit nothing in the repo; instead reason from
  Dockerfile (copy happens at build) and show `docker run --rm --entrypoint ls java-skeleton:dev /app/templates` lists the templates inside the image.
- AC-5: file lists exactly the 4 variants; qa generates and builds all 4 (same as AC-4) and all end `BUILD SUCCESSFUL`.
- AC-6: extract every path/flag/command in `CLAUDE.md` and check: each path with `Glob`/`test -e`; each flag appears in the README Flags
  table / `bin/cli.js` `.option(...)`; `docker`/`mktemp`/`./gradlew` commands ran in AC-4. Report any reference without a match as a failure.
- AC-7: file length is small (report `wc -l`, expected < ~120) and contains links/pointers to `README.md` and `DEVLOG.md`; no table
  of flags and no copied Usage/Docker sections from the README (Grep for `ghcr.io` and `npm create` returns nothing).
- AC-8: heading `## Scope for agents` exists and contains: generator not product app; edited = `templates/`, generator code only for generator changes,
  `README.md` and `DEVLOG.md` updated every change in their existing format; not touched = generated projects and `bin/cli.js` unless generator change;
  `pirca-conventions` skill loaded.
- AC-9: `git diff --stat main...HEAD` (or `git diff --name-status <base>..HEAD`) in the worktree shows only `A CLAUDE.md` before the docs
  stage (and after docs stage additionally `M DEVLOG.md`); no other path. Compare `git ls-files -s` against `baseline/tracked-files.txt`:
  differences are only `CLAUDE.md` (and `DEVLOG.md` after docs). Regenerate the 4 variants from a freshly built image and compare sha256 lists with
  the baseline: identical.

## Risks and invariants
- Invariant: generator output unchanged (sha256 of the 4 generated trees identical to baseline); no change to templates, `bin/cli.js`,
  `Dockerfile`, `.dockerignore`, `package*.json`, `scripts/`, workflow, `README.md`.
- Risk: accidental claims about things that do not exist (e.g. a `scripts/` alias purpose, `npx` usage, tests of the generator -
  there are none). Mitigation: coder only states items listed in Approach; AC-6 check in QA.
- Risk: `./gradlew build` needs a JDK 25 toolchain on the host; DEVLOG says JDK `25.0.4-tem` via SDKMAN, not default. If missing, prep
  or qa must report it as an environment blocker rather than lowering `--java`.
- Risk: the AC-3(d) example is easy to invert; the correct direction is: no `--with-publish` -> `publish.gradle` NOT written.
- Risk: README is not to be edited even though AC-8 says future changes update it; this applies to future cards only.
- No new libraries or plugins, so no versions to pin.
- Tooling note: the architect had no shell, so repo facts were verified with Read/Glob only; the baseline commands above are unexecuted
  and must be run by prep.
