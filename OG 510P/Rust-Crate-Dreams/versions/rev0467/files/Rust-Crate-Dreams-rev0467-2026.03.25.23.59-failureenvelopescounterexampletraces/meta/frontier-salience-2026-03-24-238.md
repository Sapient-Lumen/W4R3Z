# Frontier salience — 2026-03-24 (238)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is still not another top frontier lane.
It is a better answer to what happens when packet facts **disagree** or when later review must preserve both the old basis and the new judgment.

The current substrate now makes adjudication quality unavoidable:
- Cargo plumbing work explicitly decomposes Cargo into programmatic phases rather than one opaque operation;
- Cargo build analysis is explicitly about storing build metadata across invocations, which strengthens the case for multi-packet comparison and adjudication;
- `cargo metadata` still requires format pinning, the registry index still differs from `cargo metadata`, and Cargo JSON message streams distinguish build observations whose freshness/cached status matters;
- docs.rs still offers convenient `latest` and semver routes that must be resolved into pinned review basis;
- crates.io trust/timing surfaces improve visibility but do not settle task fit or local policy.

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

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, basis locks, intake/materialization receipts, adjudication sessions, carry-forward receipts, trigger intake, and recheck tickets
2. **P-0486** — debug witness bundles with comparable support checks and later adjudication paths
3. **P-0496** — restricted-delivery / source-parity bundles that reuse intake/materialization and disagreement honesty
4. **P-0472** — docs.rs parity doctor and hosted/local support bundles that can enter the same carry-forward flow
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue sharpened

The leading packets are now strong enough that the sharper missing question is:

> once a packet arrives and another packet or later signal disagrees, how does a real team adjudicate the difference without overwriting history?

That is why the practical core should now treat these as first-class outputs:
- disagreement ledgers,
- adjudication sessions,
- carry-forward receipts,
- unresolved/manual-review zones,
- and explicit inheritance versus supersession.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **adjudication quality** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- intake/materialization honesty,
- trigger/cadence discipline,
- and carry-forward clarity.

A packet-producing crate that cannot say how conflicting claims are resolved later is now weaker than one that can.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
