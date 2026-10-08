# Frontier salience — 2026-03-24 (240)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is still not another top frontier lane.
It is a better answer to what happens when one team asks for “the best crate” under an exploratory or teaching posture, while another asks under an offline, enterprise, or safety-heavy posture.

The current substrate now makes **policy-profile quality** unavoidable:

- the Rust challenges write-up still says users struggle with crate choice and that some domains remain immature;
- the survey still reports resource usage and debugging as meaningful productivity constraints while online docs remain the preferred canonical reference;
- the 2026 flagships keep pushing on secure supply chain, SBOM, safety-critical evidence, Wasm Components, async, and cargo plumbing;
- Cargo Vet already supports custom criteria, configurable policies for different subtrees, and multiple criteria sets;
- cargo-deny already exposes target-scoped checks plus advisory, ban, and license exception controls;
- Cargo, docs.rs, and the registry index already expose enough structured and versioned machine surfaces to support profile-aware review packets.

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

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, basis locks, profile packs, profile-satisfaction reports, adjudication sessions, policy-exception receipts, carry-forward receipts, expiry tickets, and recheck tickets
2. **P-0486** — debug witness bundles with profile-aware support checks rather than one flat “supported” claim
3. **P-0496** — restricted-delivery / source-parity bundles that become explicit evidence floors for air-gapped and mirror-heavy adopters
4. **P-0472** — docs.rs parity doctor and hosted/local support bundles that can satisfy visibility floors without pretending to settle offline or target truth
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue sharpened

The leading packets are now strong enough that the sharper missing question is:

> which floors are actually required for this adopter, and which missing surfaces should lead to “manual review required” rather than a fake universal answer?

That is why the practical core should now treat these as first-class outputs:
- policy-profile packs,
- evidence-floor declarations,
- profile-satisfaction reports,
- profile-diff reports,
- and exception-budget views scoped to each profile rather than to the whole repo in the abstract.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **profile quality** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- intake/materialization honesty,
- adjudication quality,
- exception quality,
- trigger/cadence discipline,
- and carry-forward clarity.

A packet-producing crate that cannot say which evidence floor applies to which adopter profile is now weaker than one that can.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://mozilla.github.io/cargo-vet/config.html
- https://mozilla.github.io/cargo-vet/audit-criteria.html
- https://mozilla.github.io/cargo-vet/how-it-works.html
- https://embarkstudios.github.io/cargo-deny/checks/advisories/index.html
- https://embarkstudios.github.io/cargo-deny/checks/bans/cfg.html
- https://embarkstudios.github.io/cargo-deny/checks/licenses/cfg.html
