# ARQ-29 prep report

## Worktree
- Repo: /home/daniel-jofre/Documentos/Desarrollo/java-skeleton (main checkout untouched; only untracked .idea/ pre-existing)
- Worktree: /home/daniel-jofre/Documentos/Desarrollo/java-skeleton-ARQ-29, branch feature/ARQ-29 from origin/main (a6a8ceb). Newly created.
- user.email set to pirca.dev@gmail.com in the worktree.

## Baseline (raw outputs in baseline/)
- git.txt: clean worktree at a6a8ceb.
- docker build -t java-skeleton:dev . : OK (layers cached; docker-build-tail.txt).
- Generated data (gastos-data-expense) and lib (lib-errors) into /tmp/tmp.fF7mfaZvRl (tmpdir.txt).
- ./gradlew archTest data: BUILD SUCCESSFUL (archTest-data.txt). excludeLayers=repository,client.
- ./gradlew archTest lib: BUILD SUCCESSFUL (archTest-lib.txt). excludeLayers=controller,service,repository,client.
- Control: root-package StrayController (cl.pirca.gastos) in data: archTest BUILD SUCCESSFUL, i.e. the gap exists today (archTest-data-stray.txt). File removed.
- ArchitectureTest-data.java / ArchitectureTest-lib.java saved.
- Note: data project's main package dir is src/main/java/cl/pirca/gastos/ (Application.java, controller/, service/).
