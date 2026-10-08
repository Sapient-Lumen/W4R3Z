# Scenario: workspace-inherited dependency cannot carry `public`

The team centralizes versions in `workspace.dependencies`, but Cargo currently treats `public` as unsupported there.
The bundle must preserve that as a **workspace gap** rather than pretending the dependency was simply undeclared.
