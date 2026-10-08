# Frontier salience — 2026-03-24 (239)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is still not another top frontier lane.
It is a better answer to what happens when a team must say:

> “we cannot satisfy the ideal review or support posture yet, but we do want a temporary, bounded, reviewable exception.”

The current substrate now makes exception quality unavoidable:
- Cargo build analysis is explicitly about storing machine-readable build metadata across invocations;
- crates.io now exposes trust and timing surfaces such as Trusted Publishing and `pubtime`;
- docs.rs exposes build limits and build metadata knobs that often explain why a public support surface is partial;
- Cargo Vet already has exemptions, trust entries, and renewals;
- cargo-deny already has ignore lists with reasons and per-crate exceptions;
- cargo-semver-checks is pursuing witness-bearing publish checks and explicit overrides;
- and safety-critical Rust adoption explicitly describes later internalization, replacement, and managed drift.

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

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, basis locks, intake/materialization receipts, adjudication sessions, policy-exception receipts, carry-forward receipts, expiry tickets, and recheck tickets
2. **P-0486** — debug witness bundles with comparable support checks and bounded-exception honesty
3. **P-0496** — restricted-delivery / source-parity bundles that can justify temporary exceptions only when sunset conditions stay visible
4. **P-0472** — docs.rs parity doctor and hosted/local support bundles that can enter the same exception/carry-forward flow
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue sharpened

The leading packets are now strong enough that the sharper missing question is:

> once a packet arrives and another packet or local policy still leaves a gap, how does a real team grant narrow temporary relief without turning that relief into permanent support truth?

That is why the practical core should now treat these as first-class outputs:
- policy-exception receipts,
- exception owner/scope records,
- expiry or renewal triggers,
- removal-path notes,
- and budget/visibility reports.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **exception quality** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- intake/materialization honesty,
- adjudication quality,
- trigger/cadence discipline,
- and carry-forward clarity.

A packet-producing crate that cannot say who owns a temporary exception, when it expires, and what removes it is now weaker than one that can.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://mozilla.github.io/cargo-vet/commands.html
- https://mozilla.github.io/cargo-vet/performing-audits.html
- https://embarkstudios.github.io/cargo-deny/cli/init.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/cargo-semver-checks/latest/cargo_semver_checks/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
