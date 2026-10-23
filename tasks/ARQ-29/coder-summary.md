# ARQ-29 coder summary

Commit 7cb2db3 on feature/ARQ-29 (worktree java-skeleton-ARQ-29), not pushed.

Files changed (4): both `ArchitectureTest.java.hbs` (identical, 4 inverse rules each, with
`@ArchTag("layer-<layer>")` and `.allowEmptyShould(true)`) and both `README.md.hbs`
(naming rules described in both directions). DEVLOG.md left for the docs stage.

Verified (image rebuilt, both variants regenerated in /tmp/tmp.lPOoI7gpjZ):
- data and lib: `./gradlew build` BUILD SUCCESSFUL (data); lib archTest SUCCESSFUL.
- Default data (controller/service active): StrayController and StrayService in root fail; the report names the class (XML/HTML report; console shows rule name only).
- StrayClient with default excludes (repository,client) passes.
- With excludeLayers empty and valid repository/client packages added: clean passes; StrayController/Service/Repository/Client each fail; UserService in controller fails.
- UserServiceImpl with nested InnerController in root passes; FooController in controller.sub passes.
- lib with StrayController: passes (all layers excluded).
Note: StrayClient failing after emptying excludeLayers was first confounded by existing rules failing on empty layers (by design); retested with populated packages.
