# ARQ-28 QA report (attempt 1)

Worktree: /home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-28, branch feature/ARQ-28, commit 32af92b. JDK 25.0.4-tem (SDKMAN).

## Commands and results
- `docker build -t java-skeleton:dev .` -> success. `docker run --rm --entrypoint ls java-skeleton:dev /app/templates` -> `java-app java-library manifest.json spring-gradle`.
- CLAUDE.md steps run literally (`D=$(mktemp -d)`, docker run `--yes --template <t> --name demo --group com.acme --artifact <a> --java 25`, plus `--with-publish`): 4 generations, all exit 0.
- `./gradlew build` in demo-spring, demo-app, demo-lib, demo-lib-pub: all `BUILD SUCCESSFUL`.
- AC-3(d) control: `demo-lib/gradle/` has no publish.gradle; `demo-lib-pub/gradle/publish.gradle` exists and is non-empty. `gradlew` executable; `gradle-wrapper.jar` `cmp` identical to template.
- Code checks in bin/cli.js: `.hbs` strip `slice(0,-4)` L135; empty skip `rendered.trim()===''` L124; `copyFile` L128; context L158-167 has exactly the 8 variables; 7 flags used exist as `.option` (L25-33); `--yes` mandatory without TTY (L44).
- Paths exist: bin/cli.js, templates/manifest.json (3 ids), templates/spring-gradle/src/main/java/{{packagePath}}/ (with {{className}}Application.java.hbs), publish.gradle.hbs (`{{#if withPublish}}`), README.md, DEVLOG.md, .claude/skills/pirca-conventions (in pirca-harness).
- Language: grep for Spanish words returns nothing. `wc -l` = 71. grep `ghcr.io|npm create` -> nothing.
- `git ls-files --error-unmatch CLAUDE.md` -> ok. `git diff --name-status origin/main..HEAD` -> `A CLAUDE.md` only. `git status --short` clean. `git ls-files -s` vs baseline/tracked-files.txt: only the added CLAUDE.md line.

## Baseline comparison
sha256 lists of the 4 freshly generated trees (from the freshly built image) vs baseline/generated-demo-{spring,app,lib,lib-pub}.sha256: all IDENTICAL. Builds equal baseline (BUILD SUCCESSFUL).

## Per-AC verdicts
| AC | Verdict | Evidence |
|---|---|---|
| AC-1 | met | file at root, tracked, English (no Spanish words) |
| AC-2 | met | CLAUDE.md L5-7; cli.js and manifest ids verified |
| AC-3 | met | (a)-(f) each present at L16-27 and confirmed against cli.js and runtime control for (d), cmp for (e) |
| AC-4 | met | steps L34-51 executed literally and succeeded; match README Development; only README flags; image copy/rebuild L55-56 (Dockerfile `COPY templates ./templates`), temp dir/not committed L57-58; only JDK needed L31 |
| AC-5 | met | L59-62 list the 4 variants; all 4 generated and built OK |
| AC-6 | met | all paths/flags/commands verified above; no reference without a match |
| AC-7 | met | 71 lines, pointers to README.md and DEVLOG.md, no flag table, no ghcr/npm create |
| AC-8 | met | `## Scope for agents` L64-71 contains all required points incl. pirca-conventions |
| AC-9 | met | only `A CLAUDE.md` in diff; generated output identical to baseline |

Minor non-blocking note: CLAUDE.md says "use JDK 25 for --java 25"; consistent with DEVLOG; the host default JDK here was 21 so SDKMAN was needed (accurate).

Verdict: done.
