# ARQ-12 · Paso 3: suites intTest y archTest

- Trello id: 6acaad8d1f9ff103ef74f881
- URL: https://trello.com/c/xhQwVmuo/5-arq-12-paso-3-suites-inttest-y-archtest
- Labels: not available in CLI output
- List at intake: Backlog (6acaad744a43ff3996630e87)

## Description

Repo destino: java-skeleton (templates spring-gradle, java-app, java-library).

Necesidad
Que los proyectos generados por java-skeleton separen tres tipos de pruebas: unitarias (test), de integración (intTest) y de arquitectura (archTest), cada una ejecutable por separado y todas incluidas en el check del build. Las de integración de spring-gradle deben poder simular servicios HTTP externos con WireMock. Las de arquitectura deben validar la convención de capas de pirca (ARQ-25) con un archTest general en los 3 templates, desactivando de forma explícita las capas que un template no tiene. Agregar esto no debe cambiar las dependencias de main de ningún template.

Decisiones ya tomadas (contexto para el BA)
- archTest e intTest en los 3 templates; WireMock solo en spring-gradle.
- Convención de capas ARQ-25: controller → service → repository | client; sufijos Controller/Service/Repository/Client; paquete siempre 'service'; cada regla de capa con @tag(layer-<capa>); opt-out con archTest.excludeLayers en gradle.properties; allowEmptyShould=false (una regla nunca pasa en silencio); regla 'sin ciclos entre paquetes' en todos.
- Capas a excluir: spring-gradle → repository,client (agregar un HelloService de ejemplo: HelloController → HelloService); java-app y java-library → controller,service,repository,client (solo regla de ciclos).
- Las versiones nuevas van en libs.versions.toml y deben funcionar con Java 25 y Spring Boot 4.

Fuera de alcance: calidad (paso 4), JaCoCo, pipeline, hexagonal.
