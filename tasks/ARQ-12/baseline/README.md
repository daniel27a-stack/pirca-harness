# ARQ-12 baseline (unmodified main)

- java-skeleton main HEAD: 019f61b4e536aa37e1b31e557faaac8d58c7ab99
- Image: java-skeleton:arq12-base, id sha256:58fdbc3bc65c19dc594ee9334939f4431719601c3393c28f61d4c015a8d64f14
- Run at 2026-10-12T00:54Z. JDK: 25.0.4-tem (sdkman, JAVA_HOME exported for gradle runs).
- Variants generated with `--yes --group com.acme --artifact <name> --java 25`: demo-spring (spring-gradle),
  demo-app (java-app), demo-lib (java-library), demo-libpub (java-library --with-publish).
- Per variant: `./gradlew dependencies --configuration {compileClasspath,runtimeClasspath,testRuntimeClasspath} --console=plain -q`
  -> `<variant>-<config>.txt`; `./gradlew clean check --console=plain` -> `<variant>-check.txt`; file list -> `<variant>-files.txt`.
- All commands exit 0; all four `check` runs BUILD SUCCESSFUL, only task `test` runs, 1 test each (XML tests="1").
- demo-spring: `bootJar`, `java -jar`, `curl -s localhost:8080/hello` -> `Hello from demo-spring` (demo-spring-hello.txt); app stopped.
- Generated projects live in the scratchpad (arq12/before), not in the repo.
