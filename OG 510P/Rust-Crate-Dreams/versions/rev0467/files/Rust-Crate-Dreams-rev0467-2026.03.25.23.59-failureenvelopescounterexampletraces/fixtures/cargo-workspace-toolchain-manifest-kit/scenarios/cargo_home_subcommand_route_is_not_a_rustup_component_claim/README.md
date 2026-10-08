# cargo_home_subcommand_route_is_not_a_rustup_component_claim

A requested `cargo-nextest` command resolves from `$CARGO_HOME/bin` because Cargo external-subcommand discovery prioritizes that directory.

That is a real route claim, but it should not be upgraded into a rustup-component or workspace-managed support claim.
