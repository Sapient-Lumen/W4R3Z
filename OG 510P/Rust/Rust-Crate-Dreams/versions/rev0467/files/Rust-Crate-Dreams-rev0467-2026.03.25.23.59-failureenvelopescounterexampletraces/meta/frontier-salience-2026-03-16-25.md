# Frontier salience scan — 2026-03-16 (crate capability contracts promoted as a producer-side ecosystem-supportiveness lane)

This pass added a new top-level proposal: **P-0510 Crate Capability Contract & Interop Profile Kit**.
It sharpens the archive’s newest cross-cutting ecosystem lane by adding the missing **producer-side truth surface** next to **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**.

## Main judgment

The strongest new cross-cutting contribution here is not:

- another search/ranking engine,
- another registry badge pack,
- another health/trust score,
- or another generic “crate metadata” wrapper.

It is the boring crate that can hand other people:

- one producer-side capability contract,
- one observed-capabilities receipt,
- one interop export map,
- one profile conformance report,
- one capability diff,
- and one explicit manual-review boundary.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0510 Crate Capability Contract & Interop Profile Kit**
6. **P-0429 rustc_public Analysis Workbench Kit**
7. **P-0490 Cargo Lock Contention Witness Kit**
8. **P-0430 Build-Std Workbench Kit**
9. **P-0478 Cargo Future-Incompat Triage Kit**
10. **P-0470 Cargo Package Review Kit**
11. **P-0451 Cfg Availability Ledger Kit**
12. **P-0484 Toolchain & Target Support Contract Kit**
13. **P-0011 Crate Health**
14. **P-0017 Trust Lens**
15. **P-0006 stdx-curated**

## Why P-0510 moved up

Fresh official Rust signals line up around four sharper truths:

- The December 2025 vision-doc work explicitly says Rust needs both **better crate navigation** and **smoother interop between libraries**.
- Cargo manifest/docs.rs/rustdoc surfaces are real substrate, but they remain fragmented: tiny manifest metadata, generic `package.metadata`, docs.rs build controls, and rustdoc JSON.
- crates.io’s newest improvements (security tab, SLOC, `pubtime`) make more facts visible, but still do not amount to a shared producer-side support/interop contract.
- RFC 1824 explicitly frames task suitability as something crates.io itself should not magically assess, which makes a reusable crate-level contract lane more attractive rather than less.

That means the lane is both:

- **timely** — because official guidance now names the pain from both the consumer and interop sides,
- and **distinct** — because the missing value is a crate-published contract above today’s fragmented metadata substrate.

## What changed in the archive

Added:
- `proposals/crate-capability-contract-kit.md`
- `meta/crate-capability-contract-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-25.md`
- `fixtures/crate-capability-contract-kit/`
- `entries/2026-03-16-196.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- task-first decision packs,
- per-item cfg availability truth,
- whole-project toolchain support,
- public-API / semver slice tools,
- and health/trust imports

into one fake “crate metadata solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://doc.rust-lang.org/cargo/reference/rust-version.html
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html
