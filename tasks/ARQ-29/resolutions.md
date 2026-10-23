## 2026-10-22T23:46Z — ba blocker (attempt 1)

1. (a) Inverse rules carry the same tag layer-<name>. Note: with the current defaults (spring-gradle excludes repository,client; java-library excludes all four layers), the inverse rule is active only for controller and service in a freshly generated service, and inactive in libraries. That is accepted.
2. Both templates.
3. Same scope as the existing rules (top-level classes).
4. Yes, suffix match.
5. Yes, ..<layer>.. including sub-packages; a *Service in ..controller.. also fails.
6. Update the generated READMEs where they describe the naming rules (spring-gradle/README.md.hbs:38, java-library/README.md.hbs:24). CONTRIBUTING.md does not describe them: no change.
A1-A4 confirmed.

## 2026-10-22T23:49Z — criteria approval, round 1 corrections

Correcciones a los criterios:
1. AC-7: eliminar la primera mitad ("never pass silently on an empty set..."), no es verificable. Dejar solo: las reglas existentes, sus tags y las claves de gradle.properties no cambian. Cómo se comportan las reglas inversas cuando no hay clases fuera de lugar lo resuelve el architect; lo observable ya está en AC-8 (proyecto limpio pasa).
2. AC-8: verificar las 2 variantes que define CONTRIBUTING.md de java-skeleton (un servicio, data, y lib), no todos los tipos.
3. AC-2: describir el resultado, no el cómo: "con las cuatro capas activas, una clase de cada sufijo fuera de su paquete de capa hace fallar archTest".
El resto, aprobado.

## 2026-10-23T00:31Z — user review of the retrospective

No crees ninguna card, ya estan cubiertas en otras, ojo, el architecto agrego esto en un test de arquitecture ->  allowEmptyShould(true) y esto salta una convención, eso no debio pasar

