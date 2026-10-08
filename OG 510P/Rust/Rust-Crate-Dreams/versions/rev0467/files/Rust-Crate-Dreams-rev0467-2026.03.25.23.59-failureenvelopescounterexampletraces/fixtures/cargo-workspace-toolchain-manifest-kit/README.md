# Cargo Workspace Toolchain Manifest Kit fixtures

This fixture family exists to keep **P-0055 Cargo Workspace Toolchain Manifest Kit** concrete.

The core claim is that workspace-scoped tool dependencies should be a **reviewable contract**, not a README convention, not a pile of shell aliases, and not a blind assumption that the requested command name resolved to the intended binary.

## Core review objects

- `install-root.receipt.json`
- `tool-route.receipt.json`
- `tool-run.receipt.json`
- `tool-upgrade.diff.json`
- `command-authority.receipt.json`
- `component-availability.report.json`
- `fallback-ceiling.report.json`
- `tool-support-bundle.manifest.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- the workspace declared a pinned tool,
- the tool was installed somewhere,
- the requested command resolved to the intended executable,
- the run happened under the intended rustup/toolchain context,
- the expected rustup component was actually installed for that toolchain,
- and no competing global, cargo-home, or PATH fallback route changed the real support claim.

## Scenario families

### `cargo_home_subcommand_precedence_can_shadow_workspace_managed_tool/`
A team can declare a workspace-managed `cargo-*` tool and still route through a global `$CARGO_HOME/bin` copy because Cargo custom-subcommand precedence is not the same as workspace intent.
The fixture keeps route authority explicit.

### `workspace_local_root_and_ephemeral_ci_root_must_not_share_same_install_root_posture/`
A workspace-local persistent root and an ephemeral CI root can both be valid, but they are not the same install-root claim.
The fixture keeps install-root posture explicit.

### `same_tool_binary_under_rustup_override_needs_distinct_route_context/`
The resolved binary path can stay the same while `cargo +beta` or a directory override changes the surrounding rustup/toolchain context.
The fixture keeps route authority and toolchain context from collapsing into one claim.

### `rust_analyzer_path_fallback_is_not_rustup_component_backing/`
A command can succeed through rustup-managed proxy logic while still ultimately running a PATH binary because the expected rustup component is missing.
The fixture keeps command authority, component availability, and fallback ceilings explicit.

### `cargo_home_subcommand_route_is_not_a_rustup_component_claim/`
A `cargo-*` tool resolved from `$CARGO_HOME/bin` is a real command route, but it is not proof that a rustup component-backed support lane exists.
The fixture keeps subcommand authority separate from component authority.

### `rustfmt_component_presence_changes_with_toolchain_selection/`
The same workspace policy can observe different optional-component posture under a default toolchain, a toolchain file, or an explicit `+toolchain` override.
The fixture keeps toolchain selection and component availability explicit.
