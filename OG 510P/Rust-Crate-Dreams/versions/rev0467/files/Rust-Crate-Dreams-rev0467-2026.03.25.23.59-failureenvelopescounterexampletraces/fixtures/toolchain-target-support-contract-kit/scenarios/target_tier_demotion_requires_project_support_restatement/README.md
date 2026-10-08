# Scenario — target-tier demotion requires project support restatement

This scenario exists to keep **Rust-project target tier** separate from **project support class**.

The project ships macOS artifacts and still downloads the `x86_64-apple-darwin` toolchain, but Rust 1.90 demoted that target to Tier 2 with host tools.
A serious support-contract crate should therefore force the project to restate its own support class instead of silently inheriting an older expectation of Tier 1 behavior.
