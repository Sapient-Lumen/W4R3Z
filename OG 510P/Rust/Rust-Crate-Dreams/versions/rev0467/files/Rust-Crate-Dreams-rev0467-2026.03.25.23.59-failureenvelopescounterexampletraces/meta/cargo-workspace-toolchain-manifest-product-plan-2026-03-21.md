# Cargo Workspace Toolchain Manifest Kit — product plan (2026-03-21)

This note sharpens **P-0055 Cargo Workspace Toolchain Manifest Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0055** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace rustup, become a universal binary installer, or silently rewrite a developer’s shell PATH.
It should provide one boring, reviewable **workspace tool dependency contract** above today’s Cargo-install, external-subcommand, and rustup-override substrate.

`0.1` should make five things first-class:

1. **declared tool intent** — what tools the workspace expects, at what versions/sources, and for what commands;
2. **install-root posture** — whether tools live in a workspace-local root, shared user cache, `$CARGO_HOME/bin`, ephemeral CI root, or custom path;
3. **tool-route authority** — which executable actually won resolution for a requested command and why;
4. **toolchain context** — which rustup override, `rust-toolchain.toml`, or `+toolchain` selection shaped the run;
5. **shadowing / collision visibility** — whether a workspace-managed tool, cargo-home tool, or other PATH tool was present but did not win.

## What `0.1` should provide other people

- one compact `Toolchain.toml`
- one compact `toolchain.lock`
- one compact `tool-sync.plan.json`
- one compact `install-root.receipt.json`
- one compact `tool-route.receipt.json`
- one compact `tool-run.receipt.json`
- one compact `tool-upgrade.diff.json`
- one rendered `toolchain.summary.md`
- a portable support / onboarding bundle

## Commands worth shipping first

- `cargo toolchain plan`
- `cargo toolchain sync`
- `cargo toolchain route <tool>`
- `cargo toolchain run <tool> -- ...`
- `cargo toolchain doctor`
- `cargo toolchain diff`
- `cargo toolchain bundle`

## What to import, not reinvent

- Cargo install-root rules and lockfile behavior
- Cargo custom-subcommand discovery rules and `$CARGO_HOME/bin` precedence
- rustup directory-override / toolchain-file / `+toolchain` context
- optional install strategy adapters from tools like `cargo-binstall`
- optional project-local execution helpers such as `cargo-run-bin`, normalized into one workspace policy surface

## Suggested `0.1` doctor warnings

- `tool_route_resolved_from_cargo_home_not_workspace_root`
- `workspace_declares_tool_but_no_route_receipt_exists`
- `same_command_name_has_multiple_candidate_executables`
- `rustup_override_changed_runner_context`
- `cargo_install_root_used_for_project_scoped_claim`
- `binstall_or_manual_binary_acquisition_missing_source_receipt`
- `packaged_lockfile_ignored_for_source_install`

## First proving-ground scenarios

1. **A global `cargo-nextest` in `$CARGO_HOME/bin` shadows the workspace-managed tool route**
2. **A workspace-local root and an ephemeral CI root must not share the same install-root claim**
3. **The same binary path still needs a different route receipt because `cargo +beta` changed the active toolchain context**
4. **A project uses `cargo-run-bin` for local execution but still needs one normalized route receipt**
5. **A prebuilt-binary acquisition path via `cargo-binstall` remains traceable instead of pretending to be identical to source install**

## What to leave for later

- automatic PATH mutation or shell integration by default
- background tool auto-updates
- a general package-manager UI for non-Rust tools
- remote policy registries or organization-wide tool marketplaces
- pretending rustup policy and workspace tool policy are the same thing
