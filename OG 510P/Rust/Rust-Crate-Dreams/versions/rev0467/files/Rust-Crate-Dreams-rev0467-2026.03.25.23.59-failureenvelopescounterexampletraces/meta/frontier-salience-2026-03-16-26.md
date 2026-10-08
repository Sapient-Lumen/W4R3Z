# Frontier salience scan — 2026-03-16 (shared ecosystem interop profiles promoted as a distinct library-compatibility lane)

This pass added a new top-level proposal: **P-0511 Crate Interop Profile Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a third distinct supportiveness/interoperability lane next to **P-0509** (task-first crate choice) and **P-0510** (producer-side capability contracts).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another crate picker,
- another producer-side metadata contract,
- another semver linter,
- or another “bless these crates” curation argument.

It is the boring crate that can hand other people:

- one shared **interop profile pack**,
- one **static conformance receipt**,
- one **behavioral probe report**,
- one **pair-compatibility report**,
- and one **migration-hazards report**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0510 Crate Capability Contract & Interop Profile Kit**
6. **P-0511 Crate Interop Profile Pack Kit**
7. **P-0429 rustc_public Analysis Workbench Kit**
8. **P-0490 Cargo Lock Contention Witness Kit**
9. **P-0430 Build-Std Workbench Kit**
10. **P-0478 Cargo Future-Incompat Triage Kit**
11. **P-0470 Cargo Package Review Kit**
12. **P-0451 Cfg Availability Ledger Kit**
13. **P-0484 Toolchain & Target Support Contract Kit**
14. **P-0011 Crate Health**
15. **P-0017 Trust Lens**

## Why P-0511 moved up

Fresh official Rust signals line up around four sharper truths:

- The December 2025 vision-doc work explicitly says **better interop between libraries** is part of helping users navigate the ecosystem well.
- That same work points at **key interop traits** and **standard building blocks** like `http`, which implies a need for profile-shaped ecosystem contracts, not only per-crate facts.
- Active project-goal work on **externally implementable items** and **evolving trait hierarchies** shows the language and library design surface is moving toward more reusable extension points and more evolvable shared abstractions.
- `cargo-semver-checks` is getting stronger, but semver linting still is not the same thing as proving that a crate or crate pair still satisfies a shared ecosystem profile.

That means the lane is both:

- **timely** — because official guidance now names smoother library interop directly,
- and **distinct** — because the missing value is a shared ecosystem profile pack above per-crate capability contracts and below task-specific selection.

## What changed in the archive

Added:
- `proposals/crate-interop-profile-pack-kit.md`
- `meta/crate-interop-profile-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-26.md`
- `fixtures/crate-interop-profile-pack-kit/`
- `entries/2026-03-16-197.md`

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
- producer-side capability contracts,
- trait-evolution / EII migration planners,
- semver witness tooling,
- and domain-specific conformance kits

into one fake “ecosystem interop solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/http
- https://docs.rs/tower-service
- https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- https://docs.rs/serde
