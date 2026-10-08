# Cargo Workspace Toolchain Manifest Kit — frontier refresh (2026-03-23)

This note sharpens **P-0055 Cargo Workspace Toolchain Manifest Kit** with current rustup and Cargo signals.

## Core shift

The important gap is no longer only **workspace tool declaration** or **install-root policy**.
It is now also **command authority**:

- did the requested command come from a rustup proxy and component lane,
- from Cargo external-subcommand resolution,
- from a workspace-managed executable,
- or from plain PATH fallback?

Current official material makes that distinction concrete enough to deserve first-class artifacts.

## Why this is sharper now

- rustup 1.29 explicitly documents a `rust-analyzer` PATH fallback when a rustup-managed one is not found;
- the rustup book still distinguishes proxy-backed commands from optional components;
- the rustup book still defines a clear override order for which toolchain is active;
- Cargo still prioritizes `$CARGO_HOME/bin` for external `cargo-*` subcommands by default;
- `cargo install` still treats installation roots and source selection as explicit choices.

That means the same requested name can still hide very different support stories.

## Missing receiver-facing layer

A worthy crate in this lane should be able to hand another team:

1. a **command-authority receipt**,
2. a **component-availability report**,
3. a **fallback-ceiling report**,
4. and one portable bundle that keeps those separate from install-root posture and run receipts.

## What this lane should not become

Do not turn **P-0055** into:

- rustup replacement logic,
- editor-specific launcher code,
- global package management for every tool on a developer machine,
- or a hidden PATH mutator.

The missing value is still the reviewable contract layer above those substrates.
