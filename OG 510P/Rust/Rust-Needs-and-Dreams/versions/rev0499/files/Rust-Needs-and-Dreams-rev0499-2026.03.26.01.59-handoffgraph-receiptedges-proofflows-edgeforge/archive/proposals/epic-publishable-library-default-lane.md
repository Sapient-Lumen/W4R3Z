# Epic proposal: Publishable library default lane

## Summary
Add a maintained **conservative publishable library** default card and renewal discipline to the defaults corpus, backed by a thin design for manifest/docs/semver/public-API/package-identity review.

Primary files:
- `design/publishable-library-default-lane.md`
- `defaults/conservative-publishable-library-2026Q1.md`
- `evidence/conservative-publishable-library-2026Q1-renewal-2026-03-22.md`

## Why this is an epic-level contribution
Rust has many excellent library crates.
What it still lacks is a **boring, reusable, reviewable contract default** for authors who intend to publish reusable crates.

The contribution is epic-worthy because it sits at the intersection of:
- ecosystem navigation,
- canonical documentation,
- semver discipline,
- supply-chain posture,
- and package-admission hygiene.

Current official motion makes this unusually timely:
- ecosystem navigation remains burdened by choice paralysis and tacit knowledge;
- docs remain the canonical learning source;
- public/private dependencies and SBOM are active 2026 “secure your supply chain” work;
- `cargo-semver-checks` is on an official merge path toward Cargo;
- crates.io now exposes better review surfaces;
- and docs.rs now has documented build/config patterns plus a CI helper.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://docs.rs/about/builds
  https://docs.rs/about/metadata
  https://docs.rs/crate/cargo-docs-rs/latest

## The missing artifact family
The missing family is intentionally modest:
- default card for a publishable library lane;
- readable renewal receipt;
- optional later machine-readable receipt schema;
- optional later helper command to collect the inputs.

## MVP
1. Publish `defaults/conservative-publishable-library-2026Q1.md`.
2. Publish its first renewal receipt.
3. Keep manifest truth, docs truth, semver truth, public API truth, and package-identity truth visibly separated.
4. Only after that, decide whether a helper command is useful.

## Not the goal
- not a “best crates” page for all library concerns;
- not a universal release bot;
- not a permanent security score;
- not a substitute for project-specific package admission.
