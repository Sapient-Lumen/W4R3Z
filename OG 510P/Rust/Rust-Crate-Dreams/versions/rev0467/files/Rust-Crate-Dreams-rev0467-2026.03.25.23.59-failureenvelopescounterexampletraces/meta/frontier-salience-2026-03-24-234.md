# Frontier salience update — 2026-03-24 (234)

This pass deepened the archive around **basis witnesses** and **first-usable release contracts**.
It does not dramatically rerank the frontier, but it changes what the first practical slice must emit if it wants to count as buildable.

## Main judgment

The strongest ecosystem-worthy missing crates are still mostly **control-plane crates**.
What changed is the archive’s answer to what makes their packets operational.

The top build slice now needs more than receiver thinking and packet-family names.
It also needs a replayable answer to:
- what machine surfaces were consulted,
- what versions or packaged states were frozen,
- what target filters were applied,
- and what trust signals were imported without being mistaken for task fit.

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

1. **P-0509 + P-0536** — decision packets and review packets backed by replayable basis locks
2. **P-0486** — debug capability packets with comparable witness bundles
3. **P-0496** — restricted-delivery / source-parity bundles
4. **P-0472** — docs.rs parity doctor and issue bundles
5. **P-0489** — build-dir dual-support transition
6. **P-0535** — lifecycle / off-ramp packets
7. **P-0484** — hard-domain target/support truth
8. **P-0058** — native provenance and prerequisites

## Why basis witnesses matter now

The current official substrate makes this more practical and more necessary than before:

- Cargo’s external-tools and `cargo metadata` surfaces are versioned and explicitly intended for programmatic use.
- Cargo’s JSON message stream includes produced artifacts and build-script results.
- Cargo packaging now carries `.cargo_vcs_info.json` for packaged-state provenance.
- docs.rs hosts format-versioned rustdoc JSON and exposes build-recipe metadata and hosted-build caveats.
- the registry index now includes checksum-bearing release records and can carry publication time.
- crates.io trust surfaces are getting stronger, but they still do not settle task fit or review completeness.

Together, those signals say the missing crate is not just “better advice”.
It is a crate that emits **witness-bearing packets** above these surfaces.

## Why P-0536 matters more in practice than a flat ranking suggests

The archive already knew **P-0536** mattered.
What this pass clarifies is that it matters **inside the first usable release** for Pathfinder and later support crates, because a packet without a basis lock is too easy to:
- regenerate from drifting `latest` pages,
- flatten across targets,
- confuse trust signals with task fit,
- or hand to another engineer without enough context to review it.

That is why **P-0536** remains just below the top salience cluster in the flat ladder, but belongs inside the first practical build slice.

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
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/registries.html
- https://doc.rust-lang.org/cargo/reference/registry-index.html
- https://doc.rust-lang.org/cargo/reference/registry-web-api.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
