# Frontier salience scan — 2026-03-16 (crate configuration scenarios promoted as the setup-support lane)

This pass added a new top-level proposal: **P-0516 Crate Configuration Scenario Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding an eighth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), and **P-0515** (deprecation/successor off-ramp packs).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another generic Cargo config receipt tool,
- another feature-powerset runner,
- another docs.rs build note helper,
- another feature documentation macro,
- or another raw `cargo metadata` wrapper.

It is the boring crate that can hand other people:

- one **scenario pack**,
- one **config-surface receipt**,
- one **scenario-profile report**,
- one **scenario-recipe manifest**,
- one **scenario-check report**,
- one **scenario-conflict report**,
- one **scenario diff**,
- and one explicit **manual-review boundary** when the crate’s configuration surface is more fragmented than its docs admit.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0512 Crate Guidance Pack Kit**
8. **P-0513 Crate Runtime Handoff Pack Kit**
9. **P-0515 Crate Off-Ramp Pack Kit**
10. **P-0510 Crate Capability Contract & Interop Profile Kit**
11. **P-0511 Crate Interop Profile Pack Kit**
12. **P-0429 rustc_public Analysis Workbench Kit**
13. **P-0490 Cargo Lock Contention Witness Kit**
14. **P-0430 Build-Std Workbench Kit**
15. **P-0478 Cargo Future-Incompat Triage Kit**

## Why P-0516 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, and a real support interface includes how crates present their intended setup/configuration lanes.
- The 2025 survey says **online documentation** is still the preferred canonical reference, followed by **studying the code itself**, which makes crate setup surfaces a first-class product concern.
- Cargo’s feature docs explicitly say features should normally be additive and describe runtime/configuration alternatives when features conflict, which means configuration shape is already recognized as a design problem.
- The Inside Rust `hint-mostly-unused` post says feature flags add complexity for users and are part of a crate’s stable interface.
- Cargo already exposes raw substrate for features, env vars, required-features, docs.rs metadata, and stable `cargo metadata` output, but it still does not define a stable receiver-facing **scenario contract**.
- Existing tools like `cargo-hack`, `cargo-feature-combinations`, and `document-features` cover matrix testing or rendering slices, but they still do not define named scenarios, checked recipes, and explicit conflict classes.

That means the lane is both:

- **timely** — because Cargo’s configuration substrate keeps growing while setup clarity is still mostly folklore,
- and **distinct** — because the missing value is a receiver-facing scenario artifact above raw Cargo/config/docs knobs.

## What changed in the archive

Added:
- `proposals/crate-configuration-scenario-pack-kit.md`
- `meta/crate-configuration-scenario-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-31.md`
- `fixtures/crate-configuration-scenario-pack-kit/`
- `entries/2026-03-16-202.md`

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

- task-first crate choice,
- producer-side support claims,
- shared ecosystem profiles,
- compile-time guidance,
- runtime handoff,
- upgrade packs,
- off-ramp packs,
- generic Cargo config provenance,
- feature-powerset testing,
- and feature-doc rendering

into one fake “crate setup solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/reference/features.html
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/cargo/commands/cargo-build.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/reference/resolver.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
- https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://docs.rs/crate/cargo-hack/latest
- https://docs.rs/crate/document-features/latest
- https://docs.rs/cargo-feature-combinations
