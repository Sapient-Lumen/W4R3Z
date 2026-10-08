# Frontier salience update — 2026-03-24 (233)

This pass deepened the archive around the **front-door stack** and **packet-family discipline**.
It does not dramatically rerank the frontier, but it changes how the practical top of the queue should be read.

## Main judgment

The strongest ecosystem-worthy missing crates are still mostly **control-plane crates**.
What changed is the archive’s view of how the first practical slice should be built:

- **P-0509 Pathfinder** remains the highest-leverage receiver-facing lane;
- **P-0536 Crate Knowledge Pack** should now be treated as the packet substrate that keeps pathfinder and later support crates pinned, cited, and honest;
- the practical build order should therefore treat them as a paired front-door stack rather than as one product now and one optional polish layer later.

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

1. **P-0509 + P-0536** — front-door decision packets backed by pinned review packets
2. **P-0486** — debug capability packets aligned to the same packet family discipline
3. **P-0496** — restricted-delivery / source-parity bundles
4. **P-0472** — docs.rs parity doctor and issue bundles
5. **P-0489** — build-dir dual-support transition
6. **P-0535** — lifecycle / off-ramp packets
7. **P-0484** — hard-domain target/support truth
8. **P-0058** — native provenance and prerequisites

## Why the front-door pairing matters now

The current official substrate makes packet discipline more practical and more necessary than before:

- Rust’s goals process now explicitly frames goals as a front door for contributors and users, which reinforces the value of crates that turn ecosystem ambiguity into reviewable packets.
- The survey still says online docs are the preferred canonical reference and that resource usage and debugging remain major pain points.
- docs.rs now exposes explicit hosted build constraints, build metadata knobs, and a format-versioned rustdoc JSON surface.
- crates.io now exposes stronger trust surfaces like the Security tab, Trusted Publishing controls, and `pubtime` in the index.
- Cargo’s plumbing and build-analysis work emphasizes programmatic stages, schema evolution, and machine-readable outputs rather than pure porcelain UX.
- libtest JSON work shows there is real downstream dependence on programmatic output once a surface becomes operationally useful.

Together, those signals say the missing crate is not “another smart ranking layer”.
It is a family of crates that publish honest, replayable packets above today’s official surfaces.

## Why P-0536 matters more in practice than a flat ranking suggests

The archive already knew **P-0536** mattered.
What this pass clarifies is that it matters **early**, because the best pathfinder packet still drifts if it cannot say:

- what exact versions and hosted routes were used,
- what target and recipe limitations apply,
- what question classes are manual-review-only,
- and what claim traces and answer boundaries support the packet.

That is why **P-0536** now moves into a lockstep implementation relationship with **P-0509**, even though the flat salience ladder stays similar.

## Watchlist just below the practical core

These remain important, but still best handled as scenario packs or later packet families until a sharper artifact seam appears:

1. local-first conflict evidence
2. robotics / digital-twin control-vs-ops bundles
3. media timeline / transcoding support contracts
4. geospatial provenance and loss accounting
5. open-table / lakehouse interop evidence
6. GPU / numerics capability contracts

## Sources

- https://rust-lang.github.io/rust-project-goals/2026/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
