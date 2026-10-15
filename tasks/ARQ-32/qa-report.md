# ARQ-32 QA report (attempt 1)

Worktree `/home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-32`, commit `dd6cde0`, clean status.
Image rebuilt as `java-skeleton:arq32-qa`; control image `java-skeleton:arq32-base`; JDK 25.0.4-tem via JAVA_HOME.
All scratch output is in the session scratchpad (`.../scratchpad/ev/`), not in the repo.

## Commands and results (all run by QA)
- `--help`: lists only `--version --yes --type --name --product --help`. `--version` prints `0.1.0` (= package.json).
- Rejected with `unknown option`, exit 1, no files: `--group --artifact --java --port --dir --with-publish --template -t -n -y -p -g -a -j -d -h -V`; stray positional also exit 1. Control: old image accepted `-t spring-gradle -n demo -g .. -a .. -j 25 -y` (exit 0, project created).
- No TTY, no `--yes`: exit 1, no files, message names only `--yes --type --name [--product]` (plus the `-it` docker hint).
- `--type|--name|--product` without `--yes` (4 cases) exit 1, no files; also under a pty (`docker run -it`).
- 19 negative `--yes` cases (java-app, bc, mc, foo, missing type/name/product, product with lib, bad product/name patterns, lib `my-lib`/`Errors`, empty `--name ""`, `--yes` alone, `a--b`, `a-`, `-a`): all exit 1 with a clear message, no files.
- Positive: `gastos/expense`, `gastos/expense-claims`, `a/a1-b2`, lib `errors` for data/edge/flow/acl/lib: exit 0. Success run stdout and stderr both 0 bytes.
- Generated `gastos-data-expense`, `lib-errors`: `./gradlew build check` BUILD SUCCESSFUL (test, archTest, intTest executed). `check` also green for `edge`, `flow`, `acl`.
- `publishToMavenLocal` (scratch m2): `cl/pirca/lib/errors/lib-errors/1.0.0/` jar, pom, module, sources, javadoc.
- `dependencies --configuration compile/runtime/testRuntime/intTestRuntime/archTestRuntime` for service and lib: diff against baseline is empty (all 10).
- pty sessions (python3 -I): data flow type -> product -> name creates `gastos-data-expense`; lib flow type -> name only; invalid values re-ask (error shown, same question) and nothing is created until valid; Ctrl-C at type, product, name (service) and lib name: exit 130, no files.
- Existing folder (marker.txt added): exit 1, folder hash identical before/after.
- Scratch copy with `JAVA_VERSION='21'` and an `EMPTY.txt.hbs` (`{{#if never}}x{{/if}}`): generated `java.gradle` has `of(21)`; `EMPTY.txt` absent, rest present.
- `bootRun` of the generated service: `curl localhost:8080/hello` -> `Hello from gastos-data-expense`; stopped, port freed.
- Repo checks: `sha256sum -c unchanged-sha256.txt` all OK except `templates/manifest.json` (expected change); excludeLayers diff vs baseline only loses the java-app lines; DEVLOG prefix identical (`cmp -n`), only one removed line (the diff header), one new `## ` heading; `package.json` diff is the description line only; `git grep java-app` only in DEVLOG; `templates/` has no java-app; no `.idea` tracked.

## AC table
| AC | Verdict | Evidence |
|---|---|---|
| 1 | met | help lists 6 options; all removed flags and shortcuts exit 1 "unknown option", no files; `-h`/`-V` rejected; `--version` 0.1.0; old image control accepted them |
| 2 | met | `--yes --type data --product gastos --name expense` exit 0 no prompt; no-TTY no-`--yes` exit 1, no files, new flags only |
| 3 | met | 4 cases without `--yes`, no TTY and pty: exit 1, no files |
| 4 | met | pty transcript `ev/pty-data.txt`, `ev/pty-lib.txt`: menu edge/flow/data/acl/lib (labels carry a short description), product skipped for lib, nothing else asked |
| 5 | met | folder `gastos-data-expense`, `rootProject.name='data-expense'`, group `cl.pirca.gastos`, package, yml name, README title; edge/flow/acl trees differ only in names |
| 6 | met | `lib-errors`, `rootProject.name='lib-errors'`, `cl.pirca.lib.errors` in main/test/intTest/archTest, README title, published path `cl/pirca/lib/errors/lib-errors/1.0.0` |
| 7 | met | single `JAVA_VERSION` (bin/cli.js:17); java.gradle `of(25)`; control with `'21'` gives `of(21)` |
| 8 | met | one `Application.java`; build green; Hello*/test/archTest/stub hashes: Controller, stub, ArchitectureTest identical to baseline, HelloService/tests differ only by the baseline project name `demo` (template files not in `git diff --stat`, so unchanged) |
| 9 | met | Example, ExampleTest, ExampleIntTest present; test-results XML for both; build green |
| 10 | met | `version = '1.0.0'` in service and lib build.gradle |
| 11 | met | publish.gradle sha identical to baseline, maven-publish applied, publishToMavenLocal ok, README has no `--with-publish` |
| 12 | met | `build check` green for data and lib; `check` green for edge, flow, acl; excludeLayers unchanged |
| 13 | met | grep for port/localhost/`{{` over both generated trees empty; application.yml only app name; control: main template had `server.port` and `localhost:{{port}}` |
| 14 | met | stdout and stderr 0 bytes in `--yes` mode; pty transcript ends at last answer |
| 15 | met | no `templates/java-app`; `--type java-app` rejected; `git grep` only old DEVLOG entries and the new entry (which names it as removed history) |
| 16 | met | exit 1, folder hash unchanged |
| 17 | met | exit 130, no files at all 4 prompts |
| 18 | met | EMPTY.txt not written (control); gradlew mode 755 in service and lib |
| 19 | met | 19 negative cases |
| 20 | met | pty re-ask transcripts `ev/pty-invalid.txt`, `ev/pty-lib-invalid.txt`; no files after invalid + Ctrl-C |
| 21 | met | valid and invalid examples, boundaries `a`, `a1-b2`, `a--b`, `a-`, `-a` |
| 22 | met | README headings: intro, Docker, alias, npx/npm, Usage; forbidden-term grep empty; the two README commands (Docker non-interactive form and alias lib form) equal ones executed above |
| 23 | met | grep clean except `docker build -t` (docker flag, not a generator flag; noted by coder); two variants only; steps equal to what was executed |
| 24 | met | manifest has 5 ids, 4x spring-gradle, lib java-library, no java-app |
| 25 | met | description exact; diff is that line only |
| 26 | met | prefix identical, one new heading, additions only |
| 27 | met | stat/sha checks above; dependency classpaths identical; bootRun default 8080 works |

## Observations (no verdict impact)
- The new DEVLOG entry is dated 2026-10-15 and the system date is 2026-10-15 UTC; consistent.
- Two containers `java-skeleton:arq32-dev` from the coder's earlier pty runs were still up (not killed by QA).
- Inquirer keeps the invalid text in the input on re-ask; the user erases it (library behavior).

STATUS: done
