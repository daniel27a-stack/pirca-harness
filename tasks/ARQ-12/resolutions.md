# ARQ-12 resolutions

## 2026-10-12T00:46Z criteria-approval round 1 — user corrections (verbatim)

Corregir:
1. Agregar criterio: en ./gradlew check, test se ejecuta antes que intTest y archTest
   (verificable en el orden de las tareas del build).
2. AC-6: cada regla de capa lleva el tag de JUnit Platform "layer-<capa>"
   (layer-controller, layer-service, layer-repository, layer-client). No exigir una
   anotación específica: el arquitecto elige la correcta para reglas de ArchUnit
   (por ejemplo @ArchTag en campos @ArchTest).
3. AC-3: quitar la frase "Un test que falla en una suite no afecta a las otras cuando se
   ejecutan por separado". Mantener solo lo de los source sets propios.
Los supuestos 1 a 5 están bien, los confirmo.

## 2026-10-12T00:48Z criteria-approval round 2 — user answer (verbatim)

1

## 2026-10-12T01:00Z architect — unknown-layer validation in archTest.excludeLayers (question raised by orchestrator; option 1 = keep the GradleException on unknown layer names)

User answer (verbatim):

1
