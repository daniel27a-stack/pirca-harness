# ARQ-12 prep report

## Worktree
- java-skeleton: /home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-12, branch feature/ARQ-12 from origin/main (019f61b). New, not reused. Main checkout untouched.
- user.email = pirca.dev@gmail.com (repository-level; already set).

## Baseline (see baseline/README.md for details)
- Docker image built from the worktree: java-skeleton:arq12-base.
- Generated demo-spring, demo-app, demo-lib, demo-libpub (Java 25).
- dependencies for compileClasspath, runtimeClasspath, testRuntimeClasspath: exit 0, saved.
- `./gradlew clean check` in each: BUILD SUCCESSFUL, only `:test` executed, 1 test each.
- demo-spring /hello -> `Hello from demo-spring`.
- Note: the plan's `set -- $v` loop must run in bash (zsh does not word-split); the generation script was run with bash. Generated projects are at
  /tmp/claude-1000/-home-daniel-jofre-Documentos-Desarrollo-pirca-harness/66e05665-e7da-40e1-9ec7-0e2b04ce93ae/scratchpad/arq12/before.
- Host default java is 21; Gradle runs used JAVA_HOME=25.0.4-tem.
