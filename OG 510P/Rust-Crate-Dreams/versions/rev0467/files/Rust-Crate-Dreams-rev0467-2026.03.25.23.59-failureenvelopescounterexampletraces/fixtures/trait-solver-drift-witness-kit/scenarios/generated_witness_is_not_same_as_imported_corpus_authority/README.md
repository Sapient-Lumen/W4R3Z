# Scenario: generated witness is not the same as imported corpus authority

This scenario keeps witness-generation and imported-corpus truth separate.

A generated witness crate can be the right way to force rustc to decide a hard type-level question, but it should not be flattened into “the same kind of authority” as an imported `ui_test` or `trybuild` case.
