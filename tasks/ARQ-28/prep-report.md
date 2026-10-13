# ARQ-28 prep report

## Worktree
- Repo: java-skeleton. Worktree: `/home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-28`, branch `feature/ARQ-28`, created new from `origin/main` (e83ca0e, "ARQ-12: Add intTest and archTest suites to the templates (#3)"). Main checkout untouched (only `git fetch`).
- `user.email` in the worktree set at repository level to `pirca.dev@gmail.com` (verified).

## Environment
- Docker running (client 29.7.2). Default JDK is 21; JDK `25.0.4-tem` is installed in SDKMAN and was selected with `sdk use java 25.0.4-tem` (as the plan allows). Not a blocker.

## Baseline (raw outputs in `tasks/ARQ-28/baseline/`)
- `tracked-files.txt` (git ls-files -s), `status.txt` (empty, as expected), `claude-md.txt` (`absent`).
- `docker build -t java-skeleton:base` succeeded (`docker-build.txt`).
- Generated 4 variants with `--yes --name demo --group com.acme --java 25` into a temp dir (path in `tmpdir.txt`; sha256 lists taken before building): `generated-demo-spring.sha256` (25 files), `generated-demo-app.sha256` (22), `generated-demo-lib.sha256` (21), `generated-demo-lib-pub.sha256` (22). `gen-*.log` are the generator outputs (all exit 0).
- `./gradlew build` in each: `build-demo-spring.txt`, `build-demo-app.txt`, `build-demo-lib.txt`, `build-demo-lib-pub.txt`; all `BUILD SUCCESSFUL`.
- Observed: `gradle/publish.gradle` absent in demo-lib and present in demo-lib-pub.
