# Frontier salience scan — 2026-03-16 (crate pathfinder promoted as a first-class ecosystem-supportiveness lane)

This pass added a new top-level proposal: **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**.
It is the first recent promotion in this archive whose center of gravity is not Cargo internals or one narrow interoperability domain, but the broad problem of **task-oriented crate choice**.

## Main judgment

The strongest new cross-cutting contribution here is not:

- a registry fork,
- a universal blessed-crates list,
- a generic trust score,
- or a dependency-minimal façade crate by itself.

It is the boring crate that can hand other people:

- one task profile,
- one candidate import report,
- one interop-surface report,
- one ranked decision pack,
- one starter-set lock,
- and one explicit manual-review boundary.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0429 rustc_public Analysis Workbench Kit**
6. **P-0490 Cargo Lock Contention Witness Kit**
7. **P-0430 Build-Std Workbench Kit**
8. **P-0478 Cargo Future-Incompat Triage Kit**
9. **P-0470 Cargo Package Review Kit**
10. **P-0125 Cargo SBOM Precursor Workbench Kit**
11. **P-0011 Crate Health**
12. **P-0017 Trust Lens**
13. **P-0006 stdx-curated**

## Why P-0509 moved up

Fresh official Rust signals line up around four sharper truths:

- The December 2025 vision-doc work directly names crate selection as a supportiveness problem and says users lack a clear place to go for a starter set.
- The latest State of Rust surveys continue to show a growing, increasingly professional user base that still depends heavily on docs/source code and still reports productivity/supportiveness pain.
- Cargo/crates.io discovery substrate is still deliberately thin: a small metadata surface, textual search, and ergonomic dependency addition without task-oriented recommendations.
- crates.io’s own maintainers continue to describe search/ranking improvements as real but non-trivial, with current ranking still built from weighted text fields and open questions around popularity/order.

That means the lane is both:

- **timely** — the project is openly naming the pain,
- and **distinct** — the missing value is not search infrastructure alone, but a reviewable decision artifact above it.

## What changed in the archive

Added:
- `proposals/crate-ecosystem-pathfinder-kit.md`
- `meta/crate-decision-lanes-2026-03-16.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-24.md`
- `fixtures/crate-ecosystem-pathfinder-kit/`
- `entries/2026-03-16-195.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- per-crate maintenance truth,
- supply-chain trust/risk scoring,
- façade-crate curation,
- and governance-level “blessing” debates

into one fake curation crate.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/commands/cargo-search.html
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://github.com/rust-lang/crates.io/discussions/9325
