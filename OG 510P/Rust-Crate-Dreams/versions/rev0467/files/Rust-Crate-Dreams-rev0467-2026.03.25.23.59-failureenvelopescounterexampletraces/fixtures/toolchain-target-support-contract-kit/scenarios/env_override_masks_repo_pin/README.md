# Scenario: environment override masks repository pin

The repository checks in `rust-toolchain.toml = stable`, but a contributor or CI lane exports `RUSTUP_TOOLCHAIN=beta` or uses `cargo +nightly`.
The support contract must preserve that the effective toolchain came from a higher-precedence selector rather than silently pretending the repository pin won.
