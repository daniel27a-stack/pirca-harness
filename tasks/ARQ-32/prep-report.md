# ARQ-32 prep report

## Worktree
- Repo `java-skeleton`: worktree `/home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-32`, branch `feature/ARQ-32`, created new from `origin/main` (9e5b1d7, ARQ-28). Main checkout untouched (fetch only).
- `user.email` in the worktree is `pirca.dev@gmail.com` (already set, nothing changed).
- task.json updated with `worktree` and `branch`.

## `.idea` tracking
- `git ls-files .idea` returns nothing: `.idea/` is untracked in the main checkout (`?? .idea/`) and absent from the worktree. Per implementation.md, leave `.idea` alone (no repoint needed, nothing to commit).

## Environment
- Docker 29.7.2 available. Host default JDK is 21; JDK 25.0.4-tem exists in sdkman and was used via JAVA_HOME for all `./gradlew` runs.
- Baseline image built from the worktree (identical to main): `java-skeleton:arq32-base` (build ok). The pre-existing tags `base`/`dev` etc. were not overwritten or used. QA should use `java-skeleton:arq32-base` as the "before" image for control tests.

## Baseline commands and results (raw outputs in `tasks/ARQ-32/baseline/`)
1. `git ls-files` -> `files-before.txt`; `git status --short` -> `status-before.txt` (empty, clean). `.idea` state -> `idea-tracked.txt` (empty), `main-checkout-status.txt`.
2. `unchanged-sha256.txt`: sha256 of Dockerfile, scripts/java-skeleton, release.yml, package-lock.json, and non-`.hbs` template files plus gradle.properties/archTest/ExternalServiceStub/Hello*/gradlew files outside `java-app` (36 lines). Note: the `Hello*`/archTest/stub `.hbs` templates are only included where matched by name; the java-app template is excluded.
3. `DEVLOG.before.md` copy.
4. `help-before.txt`: old `--help` (exit 0) with `-V -t -n -g -a -j -p --with-publish -d -y -h`.
5. Old CLI generation (both exit 0, `gen-spring.txt`, `gen-lib.txt`):
   - spring: `--yes --template spring-gradle --name demo --group cl.pirca.gastos --artifact data-expense --java 25`
   - lib: `--yes --template java-library --name demo --group cl.pirca.lib.errors --artifact lib-errors --java 25 --with-publish`
   - Per id (`spring`, `lib`): `<id>-files.txt`, `<id>-sha256.txt` (taken before the build), `<id>-build.txt` (`./gradlew build`: BUILD SUCCESSFUL, exit 0 for both), `<id>-{compileClasspath,runtimeClasspath,testRuntimeClasspath,intTestRuntimeClasspath,archTestRuntimeClasspath}.txt` (all exit 0), `lib-errors-publish.txt` (`publishToMavenLocal` with scratch `-Dmaven.repo.local`, exit 0).
6. `excludeLayers-before.txt`: grep of `archTest.excludeLayers` in each template.

No failures. Generated projects live in the session scratchpad, not in the repo.

STATUS: done
