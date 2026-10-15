# ARQ-32 · java-skeleton: generador de pirca (solo tipo, producto y nombre)

- Trello id: 6aced4f4722b39d47b37fb46
- URL: https://trello.com/c/8f2ryH5o/37-arq-32-java-skeleton-generador-de-pirca-solo-tipo-producto-y-nombre
- List: Backlog (6acaad744a43ff3996630e87) at intake
- Labels: (none)

## Description

Repo destino: java-skeleton.

Necesidad
Que java-skeleton sea el generador de pirca y pida SOLO tres datos: tipo, producto y nombre.

Interfaz final (no existe nada fuera de esta lista)
- Dos modos, sin mezclas:
  - Interactivo (sin flags): pregunta tipo → producto (solo servicios) → nombre. El tipo es un menú con edge, flow, data, acl, lib.
  - No interactivo: --yes --type <t> --name <n> [--product <p>]. Pasar --type, --name o --product sin --yes es un error.
- Además solo --help y --version (sin los atajos -h ni -V).
- Tipos: edge, flow, data, acl (template spring-gradle) y lib (template java-library).

Se deduce
- Carpeta de salida (en la carpeta actual): <producto>-<tipo>-<nombre> (gastos-data-expense) o lib-<nombre> (lib-errors).
- Artifact ID y proyecto Gradle: <tipo>-<nombre> (data-expense, lib-errors).
- Group ID y paquete: cl.pirca.<producto> (servicios) o cl.pirca.lib.<nombre> (libs).
- serviceName: el nombre de la carpeta (gastos-data-expense, lib-errors).
- La versión de Java no se elige al generar: la define java-skeleton en un solo lugar (hoy 25).

Proyectos generados
- Servicios: la clase principal se llama siempre Application.java (sin prefijo derivado del nombre).
- Libs: la clase de ejemplo se llama Example.java, con ExampleTest e ExampleIntTest.
- Todos los proyectos generados parten en version = '1.0.0'.
- Las libs incluyen siempre la publicación (gradle/publish.gradle con maven-publish).
- Todos tienen archTest; las libs mantienen intTest.

Se elimina
- Flags, preguntas y atajos: --group, --artifact, --java, --port, --dir, --with-publish, --template, -t, -n, -y, -p, -g, -a, -j, -d, -h, -V.
- El mensaje de éxito: si todo sale bien, el generador no imprime nada. Solo imprime errores.
- El puerto en los templates: server.port y toda mención a un puerto; queda el valor por defecto de Spring Boot.
- java-app: la opción y la carpeta templates/java-app.

Se mantiene igual que hoy (son protecciones, no opciones)
- Error si no hay terminal interactiva y falta --yes; el mensaje menciona solo los flags nuevos.
- Error si la carpeta de salida ya existe, sin modificarla.
- Ctrl-C en una pregunta: el proceso termina (código 130) y no se crean archivos.
- Un .hbs que queda vacío no se escribe; gradlew queda ejecutable.

Validaciones
- Con flags: entrada inválida → mensaje claro, código ≠ 0 y sin crear archivos.
- En modo interactivo: un valor inválido vuelve a preguntar; nunca se crean archivos con datos inválidos.
- Casos: tipo desconocido (incluidos java-app, bc, mc); falta --type o --name; falta --product en un servicio; --product con lib.
- Producto: ^[a-z][a-z0-9]*$. Nombre de servicio: ^[a-z][a-z0-9]*(-[a-z0-9]+)*$. Nombre de lib: ^[a-z][a-z0-9]*$.

Documentación y metadata
- README.md: documenta solo la interfaz final; mantiene las secciones de uso con Docker, el alias y npx/npm, actualizadas a los flags nuevos.
- CONTRIBUTING.md: actualizado a los templates, variables y comandos nuevos.
- README.md y CONTRIBUTING.md no mencionan ninguna configuración de puerto (ni --port, ni server.port, ni localhost:<puerto>), ni los flags eliminados, ni java-app.
- templates/manifest.json: describe los cinco tipos y el template que usa cada uno; sin java-app.
- package.json: la descripción pasa a "Generates pirca projects: REST services (edge, flow, data, acl) and libraries".
- DEVLOG.md: una entrada nueva; las entradas antiguas no se modifican (son historia).

No cambia
- El endpoint y las clases de ejemplo de spring-gradle (salvo el nombre Application.java), los valores de archTest.excludeLayers de cada template, las dependencias y sus versiones, el Gradle wrapper, el Dockerfile, scripts/java-skeleton y el workflow de release.

Regla para el BA
Todo lo que no esté en esta card se elimina. Si encuentras algo no nombrado aquí, pregunta antes de conservarlo.

Fuera de alcance: todo lo no nombrado en esta card.
