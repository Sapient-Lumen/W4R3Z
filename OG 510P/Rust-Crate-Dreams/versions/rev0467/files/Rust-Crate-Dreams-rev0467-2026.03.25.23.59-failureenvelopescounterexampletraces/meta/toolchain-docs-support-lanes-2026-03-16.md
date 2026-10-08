# Toolchain/docs support lanes — 2026-03-16

This note exists to stop future passes from flattening several neighboring “support” ideas into one fake crate.

## Main judgment

The Rust ecosystem now has enough official substrate that several support-adjacent missing crates look tempting at once.
The right move is usually **not** to merge them.
The missing value is often the **review artifact** above each lane, not one giant support kitchen sink.

## Lane 1: project support contract

**Proposal:** `P-0484 Toolchain & Target Support Contract Kit`

This lane answers:

- what toolchain the repo intends to use,
- which rustup profile/components/targets matter,
- which targets are `fully_supported`, `ci_verified`, `docs_default_surface`, `docs_only`, or `compile_only`,
- and what drifted between two revisions.

This lane is about **project promises** and **bootstrap truth**.
It is not primarily about reproducing docs.rs failures.

## Lane 2: docs.rs parity and issue bundles

**Proposal:** `P-0472 Docs.rs Build Parity & Evidence Kit`

This lane answers:

- what docs.rs-facing metadata was active,
- what the current documented docs.rs limits and target rules imply,
- whether a run depended on `#[cfg(docsrs)]` / `DOCS_RS` assumptions,
- and how local preflight differed from hosted docs.rs behavior.

This lane is about **hosted documentation behavior**, not the full project support matrix.

## Lane 3: linker / external toolchain setup

**Proposal:** `P-0504 Linker Lane Contract & Diagnosis Kit`

This lane answers:

- which non-rustup linker or SDK was required,
- how target-specific linker lanes differed,
- and whether a target is blocked on external setup rather than rustup components.

Do not hide this inside a generic toolchain-support contract.
A target can have Rust stdlibs installed and still be only `manual_setup_required`.

## Lane 4: workspace/config discovery

**Proposal:** `P-0506 Cargo Workspace Boundary Doctor Kit`

This lane answers:

- which parent manifest was found,
- which `.cargo/config.toml` files were probed,
- and how cwd / `--manifest-path` changed behavior.

That is a **boundary-discovery** problem, not a support-policy problem.

## Lane 5: single-file package portability

**Proposal:** `P-0435 Cargo Script Workbench Kit`

This lane answers:

- what Cargo inferred for one-file packages,
- how to bundle or export them,
- and how to preserve editor/CI receipts for scripts.

It is about **single-file package portability**, not the same thing as toolchain support or docs.rs parity.

## Working rules

When a future revision touches one of these frontiers, state explicitly:

1. whether the crate owns **project support promises** or **hosted-doc parity**,
2. whether the main artifact is a **bootstrap/support bundle**, a **docs.rs issue bundle**, a **linker diagnosis bundle**, or a **workspace-boundary trace**,
3. and whether default-target drift, rustup profile drift, and docs.rs failure drift are being treated as the same thing (they should not be).

## Sources

- rustup 1.29: https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- rustup overrides: https://rust-lang.github.io/rustup/overrides.html
- rustup profiles: https://rust-lang.github.io/rustup/concepts/profiles.html
- rustup components: https://rust-lang.github.io/rustup/concepts/components.html
- rustup cross-compilation: https://rust-lang.github.io/rustup/cross-compilation.html
- docs.rs builds: https://docs.rs/about/builds
- docs.rs metadata: https://docs.rs/about/metadata
- docs.rs target changes: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
