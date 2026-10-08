# Frontier salience 211 — crate knowledge now needs build-surface and conditioned-availability honesty

## Main judgment

The next worthwhile deepening for **P-0536 Crate Knowledge Pack Kit** is not another docs portal, renderer, retrieval UX, or raw rustdoc-JSON wrapper.
It is a receiver-facing contract for **what exact build surface produced the visible docs/API/example view** and **under what conditions that view remains valid**.

## Why this matters now

- Rust’s March 2026 challenges write-up still identifies ecosystem navigation as tacit-knowledge-heavy and uneven across domains.
- The 2025 State of Rust survey still says online documentation is the preferred canonical reference.
- docs.rs build docs say hosted docs use nightly, that `cfg(docsrs)` only applies to the final rustdoc invocation, and that all non-linux-default targets are cross-compiled.
- docs.rs metadata docs say features, `all-features`, `no-default-features`, `default-target`, `targets`, and extra rustdoc/rustc args materially shape what gets hosted.
- docs.rs rustdoc JSON docs say consumers may see older `format_version` values and must inspect them.
- Cargo unstable docs and changelog make example scraping explicitly recipe-bound and target-level.
- Existing rustdoc-JSON-driven tools already show value, but they still do not export a portable support-contract layer for conditioned visibility truth.

## What the sharper crate should provide

A stronger **P-0536** should now publish:

- `build-surface.receipt.json`
- `conditioned-availability.report.json`
- doctor rules that reject fake “same item witness means same visible docs surface” stories
- bundle inventory that keeps build recipe, item witness, locator, and claim-trace lanes distinct

## Boundary reminder

This is still **not** a docs hosting service, not a crate-chat product, and not a replacement for `cargo-public-api` or `cargo-semver-checks`.
It is the support-contract layer that lets another engineer review:

- which docs/toolchain/feature/target recipe produced a surface,
- whether `cfg(docsrs)` assumptions only held for the documented crate,
- whether example presence depended on recipe/dev-dep posture,
- whether the machine-facing rustdoc JSON view is inside the consumer’s format window,
- and when manual review is still required.
