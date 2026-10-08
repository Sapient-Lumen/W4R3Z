# Cargo Workspace Toolchain Manifest Kit fixtures

These fixtures are for **P-0055 Cargo Workspace Toolchain Manifest Kit**.

The point is to freeze the layer above Cargo install and external subcommand discovery:

- workspace tool manifests,
- tool lockfiles,
- install-root receipts,
- and runner receipts.

These fixtures should stay distinct from:

- rustup compiler/toolchain support contracts,
- install-policy cooldown/waiver logic,
- and Cargo home cache GC.

Scenario families in this pass:
- `workspace_local_tool_root/`
- `shared_ci_tool_cache/`
- `cargo_plugin_shadowing/`
- `rustup_override_runner_context/`
