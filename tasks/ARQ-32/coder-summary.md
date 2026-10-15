# ARQ-32 coder summary

Worktree `/home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-32`, branch `feature/ARQ-32`, one commit `dd6cde0` (not pushed).

## Changes (java-skeleton)
- `bin/cli.js` rewritten (type/product/name, `--yes --type --name --product`, `--help`/`--version` only, `JAVA_VERSION` constant, no success output).
- `templates/manifest.json` new `types` shape (5 types); `templates/java-app/` deleted.
- spring-gradle: `Application.java.hbs` (renamed), `version = '1.0.0'`, port removed from `application.yml.hbs` and `README.md.hbs`.
- java-library: `Example.java.hbs`, `ExampleTest.java.hbs`, `ExampleIntTest.java.hbs` (renamed), `build.gradle.hbs` (1.0.0, publish unconditional), `gradle/publish.gradle.hbs`, `README.md.hbs`.
- `package.json` description; `README.md`; `CONTRIBUTING.md`; `DEVLOG.md` (29 added lines, existing bytes untouched).
- `.idea` untracked: not touched.

## Tests run (image `java-skeleton:arq32-dev`, JDK 25)
- `--help` lists only the 6 options; `-h -V -t --port --template` and stray positional `foo` exit 1; `--version` prints 0.1.0.
- Without `--yes`: `--type/--name/--product` rejected (exit 1); no TTY without `--yes` rejected with new-flag message; all AC-19/21 negative cases exit 1 with message and no files; empty `--name ""` rejected.
- `--yes` success prints nothing (stdout/stderr empty); existing folder fails exit 1.
- Generated `data`, `edge`, `lib`: `./gradlew build check` BUILD OK for gastos-data-expense and lib-errors; `publishToMavenLocal` produced `lib-errors/1.0.0`; `gradlew` mode 755; `application.yml` has only app name.
- Resolved dependencies (compile/runtime/test/intTest/archTest) identical to baseline for spring and lib.
- pty (docker -it): interactive flow type -> product -> name works, invalid values re-asked (inquirer keeps text, user must erase), valid result created `gastos-edge-expense-claims`; Ctrl-C at product prompt and at lib name prompt exits 130, no files.
- Final grep for removed terms is clean outside old DEVLOG entries and the new DEVLOG entry.

## Not run
- `gradlew check` for `edge` and `flow`/`acl` variants (same template as `data`); `edge` was generated only. Empty-.hbs skip control test (code unchanged). AC-7 control with JAVA_VERSION 21. `bootRun` curl check.

## Notes for QA
- `docker build -t` in CONTRIBUTING.md matches the `-t\b` grep (docker flag, not a removed generator flag).
- Interactive prompts echo questions in a TTY (AC-14 verified in `--yes` mode, as planned).
