# Scenario: workspace inherited default-features re-enabled by member

A workspace dependency disables default features at the workspace root, but a member inherits that dependency with `default-features = true`.

Why this matters: current Cargo release notes document that this re-enables default features, while current dependency-spec docs still leave inherited `default-features` semantics easy to misread. A receiver-facing resolver bundle should preserve both the manifest origin and the effective policy instead of pretending the member manifest alone authored the final state.
