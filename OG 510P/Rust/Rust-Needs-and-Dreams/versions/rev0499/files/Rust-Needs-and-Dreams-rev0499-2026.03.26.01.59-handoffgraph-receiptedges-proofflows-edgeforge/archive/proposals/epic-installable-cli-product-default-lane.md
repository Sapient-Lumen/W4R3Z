# Epic proposal: Installable CLI product default lane

## Summary
Add a maintained **conservative installable CLI product** default card and first renewal receipt to the defaults corpus, backed by a thin design for release/distribution/route/ownership/update review.

Primary files:
- `design/installable-cli-product-default-lane.md`
- `defaults/conservative-installable-cli-product-2026Q1.md`
- `evidence/conservative-installable-cli-product-2026Q1-renewal-2026-03-22.md`

## Why this is an epic-level contribution
Rust is already visibly strong for CLI tools.
What it still lacks is a **boring, reusable, reviewable default lane for installable binary products**.

The contribution is epic-worthy because it sits at the intersection of:
- ecosystem navigation,
- Cargo install/package/uninstall semantics,
- release/distribution tooling,
- supply-chain receipts,
- and consumer lifecycle continuity.

Current official motion makes this unusually timely:
- the latest challenges post still says Rust is strong for CLI tools but navigation remains burdened by tacit knowledge and choice paralysis;
- Cargo docs already expose real route, lockfile, config-discovery, and uninstall differences;
- `cargo-dist` now provides a coherent plan/build/host/publish/announce model with machine-readable manifests and supply-chain hooks;
- `cargo-binstall` has matured into a real prebuilt-install route with metadata and signing support;
- and Cargo still treats installed-binary update support as a plugin ecosystem concern rather than a solved built-in story.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
  https://axodotdev.github.io/cargo-dist/book/
  https://axodotdev.github.io/cargo-dist/book/supplychain-security/index.html
  https://github.com/cargo-bins/cargo-binstall
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/

## The missing artifact family
The missing family is intentionally modest:
- default card for an installable CLI product lane;
- readable renewal receipt;
- optional later machine-readable route/ownership receipt schema;
- optional later helper command to gather those inputs.

## MVP
1. Publish `defaults/conservative-installable-cli-product-2026Q1.md`.
2. Publish its first renewal receipt.
3. Keep release/build truth, install-route truth, source-fallback truth, supply-chain truth, and ownership/update truth visibly separated.
4. Only after that, decide whether a helper command is useful.

## Not the goal
- not a universal installer;
- not a self-updater default for every Rust CLI;
- not a package-manager replacement;
- not a hidden “best release tool” score;
- not a substitute for project-specific package-admission or security review.
