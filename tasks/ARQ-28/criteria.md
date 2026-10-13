# ARQ-28 — Acceptance criteria

## Need
Target repository: java-skeleton. Any agent must be able to understand that java-skeleton is a
generator (Node + Handlebars `.hbs` templates, `{{packagePath}}`, optional files using `{{#if}}`)
and how it is verified (Docker image, generate, compile).

## Scope
Add a `CLAUDE.md` at the root of the java-skeleton repository that gives an agent the context of
the generator: what it is, how its templates work, how a change is verified, and what an agent
may and may not touch. Documentation only; no change to the generator, templates or build.

## Acceptance criteria
- AC-1: `CLAUDE.md` exists at the root of java-skeleton, is written in English, and is tracked by git.
- AC-2: It states that java-skeleton is a project generator (not a product application) implemented
  in Node, whose entry point is `bin/cli.js`, producing projects from the templates in
  `templates/` (`spring-gradle`, `java-app`, `java-library`).
- AC-3: It explains the template mechanics, each point matching what the repository really does
  (`bin/cli.js`, `templates/`):
  (a) template files use the `.hbs` extension, which is removed in the generated output;
  (b) `{{packagePath}}` appears in directory names (for example
  `templates/spring-gradle/src/main/java/{{packagePath}}/`) and is resolved to the package path;
  (c) optional files/blocks are controlled with `{{#if}}`;
  (d) an `.hbs` file that renders empty is not written (this is how optional files with `{{#if}}`
  work). Example: `templates/java-library/gradle/publish.gradle.hbs` renders empty and is NOT
  written when the project is generated WITHOUT `--with-publish`; with `--with-publish` it is written;
  (e) files without `.hbs` are copied verbatim (for example `gradlew`, `gradle-wrapper.jar`);
  (f) the variables available to templates are `groupId`, `artifactId`, `serviceName`,
  `javaVersion`, `port`, `withPublish`, `className` and `packagePath`, and `{{className}}` is also
  used in file names (for example `{{className}}Application.java.hbs`).
- AC-4: It documents how a change is verified, as ordered, runnable steps: build the Docker image,
  generate a project from each affected template using the image (non-interactive `--yes` mode),
  and compile/verify the generated project with `./gradlew build` (including that only a JDK is
  needed). The commands in the file are the same ones that work in the repository (consistent with
  the README "Development" section) and the README's non-interactive flags. It also states that:
  the Docker image contains a copy of `templates/`, so after changing a template the image must be
  rebuilt before generating (otherwise the old version is verified); and generated projects are
  created in a temporary directory, never inside the repository, and are not committed.
- AC-5: It states that the full verification is 4 variants — `spring-gradle`, `java-app`,
  `java-library` and `java-library` with `--with-publish` — all generated and built when a shared
  aspect changes, and that a template is not considered verified until its generated project builds.
- AC-6: Every file, directory, flag and command named in `CLAUDE.md` exists or works in the
  repository as written (no references to nonexistent paths or options).
- AC-7: `CLAUDE.md` does not duplicate the README at length: it points to `README.md` (usage,
  flags) and `DEVLOG.md` (changes and decisions) instead of copying them.
- AC-8: `CLAUDE.md` has a section "Scope for agents" that states: what kind of repository this is
  (a generator, not a product application); which files are edited (the templates under
  `templates/`; generator code only when the change is to the generator itself; and `README.md`
  and `DEVLOG.md`, which are updated in every change following their existing format); what is not
  touched (generated projects, and `bin/cli.js` unless the change is to the generator); and that
  the `pirca-conventions` skill must be loaded.
- AC-9: The only changes in java-skeleton are the new `CLAUDE.md` and the DEVLOG entry added by the
  docs stage; no template, script, build or README change. This constrains this card only; the rule
  in AC-8 about updating `README.md` and `DEVLOG.md` describes how agents work on future changes.

## Out of scope
- Changes to the generator code, templates, Dockerfile, CI workflow or README (in this card). The
  DEVLOG entry added by the docs stage is in scope; README is still not changed in this card.
- Documenting Gradle build conventions of generated projects beyond what verification needs
  (those live in the pirca conventions of pirca-harness).
- Adding new verification tooling or automated checks for `CLAUDE.md`.
- A CLAUDE.md in any other repository.

## Assumptions
- The file is a single root `CLAUDE.md` (no nested ones, no `.claude/` directory).
- "Verified" means the manual flow already described in the README (image, generate, `./gradlew build`),
  not a new script.
- Content depth is a concise orientation guide, not a full manual.
- (Confirmed by the user in round 1.)
