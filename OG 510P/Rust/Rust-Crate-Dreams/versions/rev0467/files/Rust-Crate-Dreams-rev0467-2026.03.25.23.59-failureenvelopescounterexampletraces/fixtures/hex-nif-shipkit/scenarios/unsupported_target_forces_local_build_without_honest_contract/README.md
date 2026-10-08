# Scenario — unsupported target forces local build without honest contract

The package ships common Linux/macOS/Windows artifacts, but a FreeBSD target is uncovered. `rustler_precompiled` falls back to a local build, yet the package still claims “no Rust toolchain required”.

Expected verdict: `unsupported_target_forces_local_build`.
