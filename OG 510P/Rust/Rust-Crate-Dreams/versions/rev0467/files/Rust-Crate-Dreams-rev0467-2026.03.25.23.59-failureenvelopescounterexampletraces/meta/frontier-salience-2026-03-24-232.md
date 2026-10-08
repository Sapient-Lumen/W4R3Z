# Frontier salience update — 2026-03-24 (232)

This pass deepened the archive around **receiver personas**, **first-adopter programs**, and **restricted-delivery evidence**.
It makes one notable practical promotion:
**P-0496 Cargo Vendor & Source Parity Kit** is back in the active practical frontier.

## Main judgment

The strongest ecosystem-worthy missing crates are still mostly **control-plane crates**.
What changed is how the archive now measures buildability:

- not just by broad usefulness,
- but by whether the crate serves clear receiver classes with reviewable packets and a believable first-adopter loop.

That additional filter did **not** dislodge the leading top block.
But it did make restricted-delivery evidence look more urgent again.

## Salience board

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
2. **P-0486 Debuggability Support Contract Kit**
3. **P-0538 Concurrency Contract Kit**
4. **P-0472 Docs.rs Build Parity & Evidence Kit**
5. **P-0536 Crate Knowledge Pack Kit**
6. **P-0496 Cargo Vendor & Source Parity Kit**
7. **P-0535 Dependency Lifecycle Transition Kit**
8. **P-0489 Cargo Build-Dir Consumer Transition Kit**
9. **P-0484 Toolchain & Target Support Contract Kit**
10. **P-0058 Native Deps Kit**
11. **P-0046 Buildscript UX Kit**
12. **P-0125 Cargo SBOM Precursor Workbench Kit**

## Practical queue

1. **P-0509** — receiver-facing decision packets
2. **P-0536** — pinned citations, answer boundaries, and machine-usable support packets
3. **P-0486** — debug capability packets for the same review flows
4. **P-0496** — restricted-delivery / source-parity bundles
5. **P-0472** — docs.rs parity doctor and hosted/local gap bundles
6. **P-0489** — build-dir dual-support transition
7. **P-0535** — lifecycle / off-ramp packets
8. **P-0484** — target/support truth for hard domains
9. **P-0058** — native provenance and prerequisites

## Why P-0496 moved back up

The new signal is not just “security matters”.
It is that multiple official sources now strengthen the same missing seam from different angles:

- Rust’s challenge interviews still say users struggle to know which crates they can trust and that some domains remain immature.
- The survey still says documentation is canonical, while build/resource pain remains significant.
- crates.io now has a Security tab, stronger Trusted Publishing controls, and `pubtime` in the index.
- Cargo is actively warning that many tools depend on unspecified build-dir details.
- the mirror-verification effort is explicitly about letting people use local mirrors without tampering.
- the latest Cargo extraction CVE reminds us that dependency acquisition and unpacking are part of the real risk surface.
- safety-critical and other hard-domain adopters still thin out at tooling and evidence boundaries.

Together, those do not prove that one new “supply chain crate” solves everything.
They do prove that a boring **source identity + coverage + parity + restricted-delivery** bundle would help many real users.

## What did not change

### 1. Pathfinder still leads
Rust’s own notes continue to say people struggle to pick crates, know which ones fit, and know which ones they can trust.
That still makes **P-0509** the highest-leverage lane.

### 2. Knowledge packs remain near the front
Because online documentation remains the preferred canonical reference and docs.rs exposes structured rustdoc JSON, **P-0536** remains central to keeping pathfinder and other support crates grounded.

### 3. Debuggability remains a top control-plane need
The ecosystem still treats debugging as a major missing productivity surface, and the compiler team’s 2026 survey reinforces that the area needs focused improvement.

## Watchlist just below the practical core

These remain important, but still best treated as adjacent or scenario-driven until a sharper artifact seam appears:

1. local-first conflict evidence
2. robotics / digital-twin control-vs-ops bundles
3. media timeline / transcoding support contracts
4. geospatial provenance and loss accounting
5. open-table / lakehouse interop evidence

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rust-vision-doc.html
- https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
