# ARQ-32 — Acceptance criteria

## Need
java-skeleton becomes the pirca generator and asks for ONLY three data: type, product and name.
Everything not named in the card is removed; anything not named that someone wants to keep must be
asked first.

Final interface (nothing exists outside this list):
- Two modes, never mixed:
  - Interactive (no flags): asks type, then product (services only), then name. Type is a menu with
    `edge`, `flow`, `data`, `acl`, `lib`.
  - Non-interactive: `--yes --type <t> --name <n> [--product <p>]`. Passing `--type`, `--name` or
    `--product` without `--yes` is an error.
- Besides those, only `--help` and `--version` (no `-h` or `-V` shortcuts).
- Types: `edge`, `flow`, `data`, `acl` (template `spring-gradle`) and `lib` (template `java-library`).

## Scope
Repository: `java-skeleton` (`bin/cli.js`, `templates/`, `README.md`, `CONTRIBUTING.md`,
`DEVLOG.md`, `package.json`, `templates/manifest.json`).
- New generator interface, derived values, validations and protections as listed below.
- Template changes: `Application.java`, `Example*` for libs, version `1.0.0`, always-on publishing
  for libs, no port, `java-app` removed.
- Removal of all flags, questions, shortcuts and the success message not in the final interface.
- Documentation and metadata updates.

## Acceptance criteria

### Interface
- AC-1: `java-skeleton --help` lists only `--yes`, `--type`, `--name`, `--product`, `--help`,
  `--version`. None of `--group --artifact --java --port --dir --with-publish --template` nor
  `-t -n -y -p -g -a -j -d -h -V` is accepted: each exits with code != 0 (unknown option) and
  creates no files. `--version` prints the package.json version.
- AC-2: Non-interactive mode `--yes --type <t> --name <n> [--product <p>]` generates the project
  with no prompts. Without a TTY and without `--yes`, it fails with code != 0, creates no files,
  and the message mentions only the new flags (`--yes`, `--type`, `--name`, `--product`).
- AC-3: Passing `--type`, `--name` or `--product` without `--yes` exits with a clear error,
  code != 0, and no files created (also when a TTY is present).
- AC-4: Interactive mode (TTY, no flags) asks in this order: type (menu with exactly `edge`,
  `flow`, `data`, `acl`, `lib`), product (asked only when type is not `lib`), name. It asks nothing
  else (no group, artifact, Java, port, directory, publish questions).

### Derived values
- AC-5: For a service (`edge|flow|data|acl`) with product `gastos`, type `data`, name `expense`:
  output folder `gastos-data-expense` in the current directory; Gradle project name and
  artifactId `data-expense`; groupId and Java package `cl.pirca.gastos`; `serviceName` =
  `gastos-data-expense`.
- AC-6: For `lib` with name `errors`: output folder `lib-errors`; Gradle project name and
  artifactId `lib-errors`; groupId and Java package `cl.pirca.lib.errors`; `serviceName` =
  `lib-errors`.
- AC-7: The Java version is not an input. It is defined in a single place in java-skeleton (today
  25) and the generated `java.gradle` uses it.

### Generated projects
- AC-8: Service projects (all four service types) have the main class `Application.java` (no
  name-derived prefix) in the product package, and the generated project builds with
  `./gradlew build`. The example endpoint and classes of `spring-gradle` are otherwise unchanged.
- AC-9: Lib projects have example class `Example.java`, with `ExampleTest` (unit) and
  `ExampleIntTest` (`intTest`), and build with `./gradlew build`.
- AC-10: Every generated project (services and libs) has `version = '1.0.0'` in `build.gradle`.
- AC-11: Every generated lib includes `gradle/publish.gradle` with `maven-publish` applied from
  `build.gradle`, with no option to omit it; `./gradlew publishToMavenLocal` succeeds.
- AC-12: Every generated project has the `archTest` suite; libs keep `intTest`. The
  `archTest.excludeLayers` values of each template are unchanged, and `./gradlew check` passes in
  every generated variant.
- AC-13: No generated file mentions a port: no `server.port` in `application.yml`, no
  `localhost:<port>` in the generated README, no other port reference. Spring Boot's default
  applies.

### Removals
- AC-14: On success the generator prints nothing to stdout or stderr; only errors are printed.
- AC-15: `templates/java-app/` no longer exists; `--type java-app` is rejected as unknown type;
  nothing in the repository (except old `DEVLOG.md` entries) mentions `java-app`.

### Protections (unchanged behavior)
- AC-16: If the output folder already exists, the generator fails with code != 0 and the existing
  folder is not modified.
- AC-17: Ctrl-C at any prompt ends the process with code 130 and no files are created.
- AC-18: An `.hbs` template that renders empty is not written; `gradlew` in the generated project
  is executable.

### Validations
- AC-19: With flags, invalid input gives a clear message, code != 0 and no files created, for:
  unknown type (including `java-app`, `bc`, `mc`); missing `--type`; missing `--name`; missing
  `--product` with a service type; `--product` given with `lib`; and values failing the patterns
  below.
- AC-20: In interactive mode an invalid value re-asks the same question; no files are ever
  created with invalid data.
- AC-21: Patterns: product `^[a-z][a-z0-9]*$`; service name `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`;
  lib name `^[a-z][a-z0-9]*$`. Valid examples: `gastos`/`expense-claims`, lib `errors`. Invalid
  examples: `Gastos`, `1gastos`, `gas-tos` (product), `Expense`, `expense_x`, lib `my-lib`.

### Documentation and metadata
- AC-22: `README.md` documents only the final interface (two modes, `--yes --type --name
  [--product]`, `--help`, `--version`, the five types) and keeps the Docker, alias and npx/npm
  sections updated to the new flags. It does not mention port configuration (`--port`,
  `server.port`, `localhost:<port>`), any removed flag, or `java-app`. Its sections are only: intro,
  Docker, alias, npx/npm and the final interface; the "Generated project: test suites" and
  "Development" sections are removed.
- AC-23: `CONTRIBUTING.md` reflects the new templates (`spring-gradle`, `java-library`), variables
  and commands (verification examples use `--yes --type --name [--product]`; variant list no
  longer has `java-app` or `--with-publish`). Same prohibitions on port, removed flags and
  `java-app` as AC-22. Its "How to verify a change" procedure is kept, rewritten for the new flags,
  with exactly two variants: one service type (`spring-gradle`) and `lib` (publishing always on).
- AC-24: `templates/manifest.json` describes the five types and the template each uses; no
  `java-app`.
- AC-25: `package.json` description is exactly `Generates pirca projects: REST services (edge,
  flow, data, acl) and libraries`.
- AC-26: `DEVLOG.md` has one new entry following its format; existing entries are byte-identical.

### Unchanged
- AC-27: These are unchanged (verified by diff): the `spring-gradle` example endpoint and classes
  (except `Application.java`), each template's `archTest.excludeLayers`, dependencies and
  versions, the Gradle wrapper, the Dockerfile, `scripts/java-skeleton`, and
  `.github/workflows/release.yml`.

## Out of scope
Everything not named in the card, including: changing dependency versions, the Dockerfile,
alias script or release workflow; bumping the package.json version; new types, new flags, new
templates; hexagonal or other layering changes; any generated-project docs beyond what the removed
options force (port mention, `--with-publish` text).

## Assumptions
(A1-A6 confirmed by the user in resolutions.md; README/CONTRIBUTING sections resolved as option A.)
- A1: Generated-project READMEs (`templates/*/README.md.hbs`) are updated only where forced: the
  port line in `spring-gradle`, and the lib "Publish" section's `--with-publish` / "does not
  include maven-publish" text (publishing is always on).
- A2: `application.yml` keeps `spring.application.name: {{serviceName}}`; only the `server.port`
  block goes.
- A3: `gradle/publish.gradle` content (including the commented GitHub Packages block) stays as is,
  minus the `{{#if withPublish}}` wrapper.
- A4: package.json `version` (0.1.0), keywords, and the `npm create java-service@latest` line in
  README are not touched.
- A5: Error exit code for validation failures is 1 (as today); 130 for Ctrl-C.
- A6: `--yes` in a TTY still means non-interactive (no prompts), so a missing flag is an error.
