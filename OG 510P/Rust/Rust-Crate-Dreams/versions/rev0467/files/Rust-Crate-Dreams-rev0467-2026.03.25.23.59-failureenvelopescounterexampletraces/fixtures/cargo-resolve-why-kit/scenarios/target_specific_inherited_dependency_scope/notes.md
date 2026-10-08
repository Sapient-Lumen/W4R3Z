# Scenario: target-specific inherited dependency scope

A workspace dependency is inherited in two target-specific sections, one of which uses `default-features = false` for a wasm target.

Why this matters: issue history shows target-specific inherited dependencies can still be where effective feature/default-feature behavior becomes conservative or manual-review territory. A resolver bundle should freeze that ambiguity instead of flattening it into one universal dependency policy.
