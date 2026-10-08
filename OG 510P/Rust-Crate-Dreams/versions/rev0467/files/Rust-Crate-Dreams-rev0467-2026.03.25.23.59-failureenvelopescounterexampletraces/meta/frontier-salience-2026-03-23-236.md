# Frontier salience — 2026-03-23 (236)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is not a brand-new frontier lane.
It is a stronger answer to how the leading lanes stay honest **after** a frozen packet exists.

The current official substrate now supports a more concrete packet ops story:
- Cargo and docs.rs expose versioned or compatibility-governed machine surfaces,
- crates.io imports more trust and release-timing surfaces,
- and public policy/incident changes mean teams can no longer depend on noisy public announcement streams as their only refresh mechanism.

That does not change which ideas matter most.
It changes what it now takes for the practical core to count as buildable.

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

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, frozen basis locks, trigger intake, and recheck tickets
2. **P-0486** — debug capability packets with witness bundles and repeatable support checks
3. **P-0496** — restricted-delivery / source-parity bundles
4. **P-0472** — docs.rs parity doctor and issue bundles
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue changed

The leading packets are now strong enough that the sharper missing question is:

> what opens the next review, and how does that review begin without rewriting history?

That is why the practical core should now treat these as first-class outputs:
- trigger-intake receipts,
- recheck tickets,
- cadence/watch policies,
- and basis deltas that sit between freeze-time evidence and transition posture.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **trigger/cadence discipline** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- first-adopter credibility,
- and refresh/transition honesty.

A packet-producing crate that cannot say what later facts should open review is now weaker than one that can.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
