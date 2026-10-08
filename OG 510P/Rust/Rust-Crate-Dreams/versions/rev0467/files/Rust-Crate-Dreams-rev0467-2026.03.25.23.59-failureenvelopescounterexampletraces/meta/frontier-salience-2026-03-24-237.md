# Frontier salience — 2026-03-24 (237)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is still not a brand-new frontier lane.
It is a better answer to what happens **after a packet is emitted**.

The current substrate now makes consumer-side discipline unavoidable:
- Cargo plumbing is explicitly experimenting with programmatic stages instead of one giant porcelain blob,
- Cargo build analysis is explicitly planning to persist evolving machine data across invocations,
- `cargo metadata` and `.cargo_vcs_info.json` already come with compatibility / provenance caveats,
- the registry index explicitly differs from `cargo metadata` and the Publish API,
- and docs.rs now exposes both machine surfaces and downloadable materials whose caveats must survive import.

That does not change which ideas matter most.
It changes what now counts as a buildable **front door**.

## Salience board

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0538 Concurrency Contract Kit**
4. **P-0472 Docs.rs Build Parity & Evidence Kit**
5. **P-0536 Crate Knowledge Pack Kit**
6. **P-0535 Dependency Lifecycle Transition Kit**
7. **P-0496 Cargo Vendor & Source Parity Kit**
8. **P-0489 Cargo Build-Dir Consumer Transition Kit**
9. **P-0484 Toolchain & Target Support Contract Kit**
10. **P-0058 Native Deps Kit**
11. **P-0046 Buildscript UX Kit**
12. **P-0125 Cargo SBOM Precursor Workbench Kit**

## Practical build queue

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, basis locks, intake/materialization receipts, trigger intake, and recheck tickets
2. **P-0486** — debug witness bundles with comparable support checks and later import paths
3. **P-0496** — restricted-delivery / source-parity bundles that reuse intake/materialization honesty
4. **P-0472** — docs.rs parity doctor and hosted/local support bundles
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue sharpened

The leading packets are now strong enough that the sharper missing question is:

> once a packet arrives, how does a real consumer ingest it, materialize it, and preserve its ceilings instead of silently normalizing them away?

That is why the practical core should now treat these as first-class outputs:
- intake receipts,
- materialization plans,
- degradation / caveat visibility,
- and consumer contracts for downstream humans, tools, CI jobs, and assistants.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **consumer-contract quality** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- trigger/cadence discipline,
- first-adopter credibility,
- and refresh/transition honesty.

A packet-producing crate that cannot explain how another system imports and materializes its artifacts is now weaker than one that can.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
