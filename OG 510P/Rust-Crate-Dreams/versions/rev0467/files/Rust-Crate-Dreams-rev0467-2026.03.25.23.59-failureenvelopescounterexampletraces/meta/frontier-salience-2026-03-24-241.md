# Frontier salience — 2026-03-24 (241)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is still not another top frontier lane.
It is a better answer to what happens **after** a profile-aware packet says “conditional”, “manual review required”, or even a narrow “pass”.

The current substrate now makes **decision-program quality** unavoidable:

- the Rust challenges write-up still says users struggle with crate choice and that some domains remain immature;
- the survey still reports resource usage and debugging as meaningful productivity constraints while online docs remain the preferred canonical reference;
- the 2026 flagships keep pushing on secure supply chain, SBOM, safety-critical evidence, Wasm Components, async, and cargo plumbing;
- Cargo plumbing work explicitly decomposes operations into programmatic phases;
- Cargo build-analysis explicitly aims to record metadata across invocations so later reports can explain build behavior over time;
- Cargo Vet already models expiring renewals and policy criteria instead of one flat audited/not-audited state;
- cargo-deny already distinguishes target-scoped graph construction and offline behavior;
- safety-critical guidance explicitly describes staged narrowing, wrapping, and replace-later dependency patterns.

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

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, basis locks, profile packs, profile-satisfaction reports, decision-program runbooks, progression reports, adjudication sessions, policy-exception receipts, carry-forward receipts, expiry tickets, and recheck tickets
2. **P-0486** — debug witness bundles with stage-aware support checks instead of one flat posture
3. **P-0496** — restricted-delivery / source-parity bundles that become stage-entry requirements for enterprise-offline and safety-adjacent programs
4. **P-0472** — docs.rs parity doctor and hosted/local support bundles that satisfy part of a stage gate without pretending to satisfy the whole gate
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue sharpened

The leading packets are now strong enough that the sharper missing question is:

> how does another team move from an exploratory answer to a stronger operating posture without throwing away the earlier packet basis or silently smuggling in new claims?

That is why the practical core should now treat these as first-class outputs:
- decision-program runbooks,
- stage-entry checks,
- profile-progression reports,
- exit/posture reports,
- and reopen rules scoped to each stage rather than to the whole repo in the abstract.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **decision-program quality** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- intake/materialization honesty,
- adjudication quality,
- exception quality,
- trigger/cadence discipline,
- profile quality,
- and carry-forward clarity.

A packet-producing crate that cannot say how a team progresses or exits cleanly is now weaker than one that can.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://mozilla.github.io/cargo-vet/config.html
- https://mozilla.github.io/cargo-vet/commands.html
- https://embarkstudios.github.io/cargo-deny/checks/cfg.html
- https://embarkstudios.github.io/cargo-deny/cli/common.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
