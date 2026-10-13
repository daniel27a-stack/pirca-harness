# ARQ-28 resolutions

## 2026-10-12T22:28Z — criteria-approval round 1: corrections (verbatim)

Corregir:
- AC-4: agregar que la imagen Docker contiene una copia de templates/; después de cambiar
  una plantilla hay que reconstruir la imagen antes de generar, o se verifica la versión
  vieja. Los proyectos se generan en un directorio temporal, nunca dentro del repo, y no se
  commitean.
- AC-3: agregar (d) un .hbs que queda vacío al renderizarse no se escribe (así funcionan los
  archivos opcionales con {{#if}}); (e) los archivos sin .hbs se copian tal cual; (f) la
  lista de variables disponibles (groupId, artifactId, serviceName, javaVersion, port,
  withPublish, className, packagePath) y que {{className}} también se usa en nombres de
  archivo.
- AC-5: la verificación completa son 4 variantes: spring-gradle, java-app, java-library
  y java-library con --with-publish.
- Nuevo AC: una sección "Scope for agents" que declare qué tipo de repo es, qué archivos se
  editan, qué no se toca (proyectos generados, bin/cli.js salvo que el cambio sea del
  generador) y que se debe cargar la skill pirca-conventions.
Los supuestos están bien, los confirmo.

## 2026-10-12T22:30Z — criteria-approval round 2: corrections (verbatim)

Corregir:
- AC-3 (d): el ejemplo está invertido. Debe decir que templates/java-library/gradle/publish.gradle.hbs
  queda vacío y NO se escribe cuando el proyecto se genera SIN --with-publish (con el flag sí se escribe).
- AC-8: en "qué se edita" agregar README.md y DEVLOG.md, que se actualizan en cada cambio
  según su formato.
El resto lo apruebo como está.

## 2026-10-12T22:32Z — criteria-approval round 3: AC-9 vs docs stage DEVLOG entry

Question: AC-9 (as reworded in refinement attempt 3) forbids any DEVLOG change, but the docs stage
always adds a DEVLOG entry. Option 1 (recommended): AC-9 allows the DEVLOG entry added by the docs
stage — "The only changes in java-skeleton are the new CLAUDE.md and the DEVLOG entry added by the
docs stage; no template, script, build or README change." Option 2: keep AC-9 and skip DEVLOG in docs.

User answer (verbatim):
1

## 2026-10-12T22:36Z — criteria-approval round 4: approval

User answer (verbatim):
1
