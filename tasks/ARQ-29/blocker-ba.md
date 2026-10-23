# ARQ-29 — BA blocker

Source checked: `java-skeleton/templates/{spring-gradle,java-library}/src/archTest/java/{{packagePath}}/ArchitectureTest.java.hbs`
(two identical files). Today each layer has a rule "classes in `..<layer>..` end with `<Suffix>`"
(lines 40-45, 56-61, 78-83, 94-99), limited to top-level classes and tagged `layer-<layer>`.
There is no inverse rule. No other template Java class violates the proposed rule
(`HelloController` in `controller`, `HelloService` in `service`).

## Questions

1. **Layer tag of the inverse rules.** Today `archTest.excludeLayers=client` disables every rule
   tagged `layer-client`.
   - (a) Inverse rules carry the same tag `layer-<name>`: an artifact that excludes `client` also
     stops checking that no stray `*Client` exists. Consistent with "opts out explicitly".
   - (b) Inverse rules are untagged (always run): a stray `*Client` fails even in an artifact that
     excluded the `client` layer. Stricter.
   Recommendation: (a).
2. **Which templates.** Apply to both `spring-gradle` and `java-library` (they carry identical
   rules today), or only `spring-gradle`? Recommendation: both.
3. **What counts as a "class".** Existing rules use top-level classes only (`areTopLevelClasses()`).
   Should the inverse rule also cover nested classes, interfaces, enums, records? Recommendation:
   same scope as the existing rules (top-level classes, which in ArchUnit includes interfaces,
   enums and records); nested classes are not checked.
4. **Name matching.** "Named `*Controller`" = simple name ends with `Controller` (so
   `StrayController` fails, `UserServiceImpl` does not). Confirm. Recommendation: yes, suffix match,
   same as the existing rules.
5. **"Its layer package".** A class is in place if it resides in `..<layer>..` (that package or any
   sub-package), exactly as the existing rules define it. A `*Service` in `..controller..` also fails.
   Confirm. Recommendation: yes.
6. **Documentation.** Besides the DEVLOG entry, should `CONTRIBUTING.md` / the generated README
   mention the new rule (only if they currently describe the archTest naming rules)? Recommendation:
   update only where the existing naming rules are already described.

## Assumptions (confirm in bulk)

- A1: Exactly four new rules, one per suffix (Controller, Service, Repository, Client); no change to
  existing rules, flags or `gradle.properties` keys.
- A2: Failure messages are ArchUnit's default; nothing user-visible is added.
- A3: Verification is by generating both variants, adding a stray class (e.g. `StrayController` in
  the root package) in a temporary directory, and seeing `./gradlew archTest` fail; generated clean
  projects keep passing.
- A4: Order between tasks does not matter (single suite).
