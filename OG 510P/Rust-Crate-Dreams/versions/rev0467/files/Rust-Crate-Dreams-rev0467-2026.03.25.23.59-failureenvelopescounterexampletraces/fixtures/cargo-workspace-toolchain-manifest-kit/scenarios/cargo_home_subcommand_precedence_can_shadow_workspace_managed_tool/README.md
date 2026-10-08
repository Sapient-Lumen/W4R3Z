# cargo_home_subcommand_precedence_can_shadow_workspace_managed_tool

A workspace can declare `cargo-nextest` in its own manifest and still route through a globally installed `$CARGO_HOME/bin/cargo-nextest` because Cargo custom subcommands are discovered externally and Cargo prefers `$CARGO_HOME/bin` by default.

This fixture keeps **requested tool name** separate from **actual resolved route**.
