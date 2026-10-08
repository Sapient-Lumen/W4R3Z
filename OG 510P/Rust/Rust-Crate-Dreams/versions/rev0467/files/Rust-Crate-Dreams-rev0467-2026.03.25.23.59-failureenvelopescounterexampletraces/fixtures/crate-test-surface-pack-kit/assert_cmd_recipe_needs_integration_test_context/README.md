# Scenario family — assert_cmd recipe depends on integration-test context and cargo-built binaries

This fixture family exists for CLI crates where the official smoke-test recipe uses `assert_cmd` cargo helpers.

It is meant to catch support drift such as:

- docs implying the same recipe works from arbitrary unit-test helpers,
- omitting the cargo-built-binary assumption,
- or forgetting to declare temp-state/env-mutation requirements for CLI tests.

A good test-surface pack should make the integration-test context visible instead of burying it in helper code.
