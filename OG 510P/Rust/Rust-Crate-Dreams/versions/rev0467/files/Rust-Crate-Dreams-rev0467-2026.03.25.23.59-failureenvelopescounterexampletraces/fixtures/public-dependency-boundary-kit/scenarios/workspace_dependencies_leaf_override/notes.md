# Scenario: `workspace_dependencies_leaf_override`

A shared workspace dependency is used in a public API, but current Cargo support keeps the `public` field out of `workspace.dependencies`.
The bundle should preserve that limitation and recommend a leaf-manifest migration strategy rather than faking a clean workspace-root fix.
