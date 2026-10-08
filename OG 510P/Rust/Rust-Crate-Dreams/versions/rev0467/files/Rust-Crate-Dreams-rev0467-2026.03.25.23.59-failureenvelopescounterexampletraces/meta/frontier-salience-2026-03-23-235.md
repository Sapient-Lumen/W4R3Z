# Frontier salience update — 2026-03-23 (235)

This pass deepened the archive around **comparison versus refresh versus transition**.
It does not dramatically rerank the frontier, but it changes what the first practical slice must do after a team freezes a decision.

## Main judgment

The strongest ecosystem-worthy missing crates are still mostly **control-plane crates**.
What changed is the archive’s answer to what happens after the first packet lands.

The top build slice now needs more than receiver thinking, packet-family names, and basis locks.
It also needs a replayable answer to:
- what changed later,
- whether that changed the old choice,
- and what transition posture applies if it did.

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

## Practical queue

1. **P-0509 + P-0536** — comparator packets and review packets backed by replayable basis locks
2. **P-0535** — refresh, revalidation, and transition packets for changing dependency posture
3. **P-0486** — debug capability packets with comparable witness bundles
4. **P-0496** — restricted-delivery / source-parity bundles
5. **P-0472** — docs.rs parity doctor and issue bundles
6. **P-0489** — build-dir dual-support transition
7. **P-0484** — hard-domain target/support truth
8. **P-0058** — native provenance and prerequisites

## Why P-0535 moved closer to the practical core

Current signals all point in the same direction:
- the challenges post says users still struggle with crate choice, trust, and missing domain support;
- the safety-critical write-up says many teams use crates earlier and more widely in low-criticality lanes, then contain or replace them later;
- crates.io trust surfaces are stronger, but still do not settle architecture or lifecycle posture;
- the new malicious-crate notification policy means teams should not assume every relevant event becomes a loud ecosystem-wide blog post;
- and the March 2026 Cargo advisory shows dependency acquisition and registry posture are still part of the real risk surface.

Together, those signals make lifecycle transition look less like a later luxury and more like a core missing control plane.

## Why the front-door pair still stays first

Even after this move, the first question is still usually:
- what are the plausible crates,
- what task profile matters,
- and what frozen evidence basis supports the choice?

That means **P-0509 + P-0536** still stay first.
But the archive should now treat them as incomplete without a later **revalidation / transition** story.

## Watchlist just below the practical core

These remain important, but still best handled as scenario packs or later packet families until a sharper artifact seam appears:

1. local-first conflict evidence
2. robotics / digital-twin control-vs-ops bundles
3. media timeline / transcoding support contracts
4. geospatial provenance and loss accounting
5. open-table / lakehouse interop evidence
6. GPU / numerics capability contracts

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
