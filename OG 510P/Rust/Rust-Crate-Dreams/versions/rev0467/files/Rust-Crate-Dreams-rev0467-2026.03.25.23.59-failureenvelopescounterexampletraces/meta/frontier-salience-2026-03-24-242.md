# Frontier salience — 2026-03-24 (242)

## Main judgment

This pass does **not** justify a major salience rerank.

The sharper missing layer is still not another top frontier lane.
It is a better answer to what happens **after** a profile-aware, stage-aware packet says “conditional”, “hold”, or “manual review required”.

The current substrate now makes **gap-closure quality** unavoidable:

- the Rust challenges write-up still says users struggle with crate choice and that some domains remain immature;
- the survey still reports resource usage and debugging as meaningful productivity constraints while online docs remain the preferred canonical reference;
- the 2026 flagships keep pushing on secure supply chain, SBOM, safety-critical evidence, async, and cargo plumbing;
- Cargo plumbing work explicitly decomposes operations into programmatic phases;
- Cargo build-analysis explicitly aims to record metadata across invocations so later reports can explain build behavior over time;
- docs.rs exposes queue state, hosted build posture, custom metadata, versioned rustdoc JSON, and download caveats;
- crates.io exposes Security-tab, Trusted Publishing, and `pubtime` timing signals;
- Cargo Vet already models review backlog, exemptions, imported audits, trusted publishers, and expiring renewals.

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

1. **P-0509 + P-0536 + minimal P-0535 loop** — comparator packets, basis locks, profile packs, profile-satisfaction reports, decision-program runbooks, adjudication sessions, policy-exception receipts, progression reports, evidence-gap reports, evidence-campaign plans, gap-closure receipts, expiry tickets, and recheck tickets
2. **P-0486** — debug witness bundles with explicit support gaps and stage-aware closure plans instead of one flat posture
3. **P-0496** — restricted-delivery / source-parity bundles that can satisfy specific gap items inside enterprise-offline and safety-adjacent stages
4. **P-0472** — docs.rs parity doctor and hosted/local support bundles that open bounded campaign items instead of pretending to settle whole stages
5. **P-0489** — build-dir dual-support transition
6. **P-0484** — hard-domain target/support truth
7. **P-0058** — native provenance for offline and mixed-language stacks

## Why the practical queue sharpened

The leading packets are now strong enough that the sharper missing question is:

> once a team knows why a stage is blocked, how does another team close the missing evidence in a bounded, replayable way instead of just carrying a vague “manual review” forever?

That is why the practical core should now treat these as first-class outputs:
- evidence-gap reports,
- evidence-campaign plans,
- gap-closure receipts,
- authority-route mappings,
- and stop conditions that prevent campaign automation from becoming fake certainty.

## What did not change

- **P-0509** is still the most important missing control-plane crate.
- **P-0486** still deserves its high position because debugging remains a live official pain point.
- **P-0538** still matters a lot in salience because async remains central to Rust’s future.
- build/docs/native/source-parity lanes still matter because current substrate gives them unusually concrete seams.

## New ranking input after this pass

Future practical promotion should consider **gap-closure quality** alongside:
- receiver coverage,
- basis witnesses,
- packet-family discipline,
- intake/materialization honesty,
- adjudication quality,
- exception quality,
- trigger/cadence discipline,
- profile quality,
- progression quality,
- and carry-forward clarity.

A packet-producing crate that can state open gaps but cannot bound the closure plan is now weaker than one that can.

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
- https://docs.rs/releases/queue
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://mozilla.github.io/cargo-vet/config.html
- https://mozilla.github.io/cargo-vet/commands.html
- https://mozilla.github.io/cargo-vet/wildcard-audit-entries.html
- https://embarkstudios.github.io/cargo-deny/cli/common.html
