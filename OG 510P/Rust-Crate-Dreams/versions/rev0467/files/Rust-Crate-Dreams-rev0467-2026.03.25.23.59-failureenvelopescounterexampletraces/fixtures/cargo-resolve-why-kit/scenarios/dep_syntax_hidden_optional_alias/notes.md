# Scenario: `dep:` hides the optional-dependency feature alias

A package uses `dep:ravif` and `dep:rgb` inside another feature such as `avif`.

Why this matters: the manifest author intentionally made those optional dependencies internal details, but `cargo metadata` and downstream tools can easily flatten that into an apparent public feature name. A resolver bundle should preserve that the dependency exists, the implicit alias was suppressed, and the user-facing feature is the grouped feature instead.
