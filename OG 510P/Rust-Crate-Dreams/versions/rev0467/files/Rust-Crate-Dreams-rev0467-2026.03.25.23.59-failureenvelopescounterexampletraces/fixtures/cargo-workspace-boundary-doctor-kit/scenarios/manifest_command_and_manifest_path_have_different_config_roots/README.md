# Scenario — manifest command and manifest path have different config roots

This scenario exists because `cargo path/to/Cargo.toml` and `cargo build --manifest-path path/to/Cargo.toml` are not the same invocation route.
The receiver needs an explicit invocation-mode report instead of a vague “used a manifest path” summary.
