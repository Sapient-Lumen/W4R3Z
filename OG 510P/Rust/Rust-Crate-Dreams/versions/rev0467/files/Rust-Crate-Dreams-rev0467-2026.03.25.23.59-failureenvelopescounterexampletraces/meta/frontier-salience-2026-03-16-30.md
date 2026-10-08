# Frontier salience scan — 2026-03-16 (crate off-ramp packs promoted as the deprecation/successor-support lane)

This pass added a new top-level proposal: **P-0515 Crate Off-Ramp Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a seventh distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), and **P-0514** (release-to-release upgrade packs).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another advisory client,
- another outdated-version checker,
- another deprecation note helper,
- another yank/publish wrapper,
- or a generic dependency-ban policy tool.

It is the boring crate that can hand other people:

- one **off-ramp pack**,
- one **successor-map report**,
- one **deprecation-surface receipt**,
- one **off-ramp recipe manifest**,
- one **successor-compat report**,
- one **sunset-check report**,
- one **off-ramp diff**,
- and one explicit **manual-review boundary** when there is no honest drop-in replacement.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0512 Crate Guidance Pack Kit**
7. **P-0513 Crate Runtime Handoff Pack Kit**
8. **P-0515 Crate Off-Ramp Pack Kit**
9. **P-0510 Crate Capability Contract & Interop Profile Kit**
10. **P-0511 Crate Interop Profile Pack Kit**
11. **P-0429 rustc_public Analysis Workbench Kit**
12. **P-0490 Cargo Lock Contention Witness Kit**
13. **P-0430 Build-Std Workbench Kit**
14. **P-0478 Cargo Future-Incompat Triage Kit**
15. **P-0470 Cargo Package Review Kit**

## Why P-0515 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, and a real support interface should include how maintainers ask users to leave a crate.
- The 2025 survey says **online documentation** is still the preferred canonical reference, followed by **studying the code itself**, so sunset guidance needs structure, not just scattered prose.
- Official Rust docs say deprecations should usually include a note on what to use instead, which implicitly points at a successor-planning problem larger than one free-text message.
- Cargo’s SemVer guidance already treats introduced deprecations as part of the update experience and even suggests feature-gated deprecations before removals.
- Cargo’s yank docs make clear that yanking does not delete a crate, and `cargo update` tells users to seek a non-yanked version or maintainer help, which means the ecosystem still lacks a better downstream handoff artifact.
- crates.io Security tabs, RustSec, `cargo-audit`, `cargo-deny`, and `cargo-outdated` can identify risk or staleness, but they still do not define a stable maintainer-authored **exit contract** for successor choice, stopgaps, and checked recipes.

That means the lane is both:

- **timely** — because official registry/advisory surfaces are getting stronger while maintainer-authored successor planning is still weak,
- and **distinct** — because the missing value is a receiver-facing off-ramp artifact above advisories, yanks, deprecations, and outdated checks.

## What changed in the archive

Added:
- `proposals/crate-offramp-pack-kit.md`
- `meta/crate-offramp-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-30.md`
- `fixtures/crate-offramp-pack-kit/`
- `entries/2026-03-16-201.md`

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

- crate health/succession metadata,
- task-first crate choice,
- compile-time guidance,
- runtime handoff,
- release-to-release upgrade packs,
- advisory detection,
- ban policies,
- publish/yank mechanics,
- and ad hoc migration notes

into one fake “deprecation support solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://doc.rust-lang.org/cargo/commands/cargo-yank.html
- https://doc.rust-lang.org/cargo/commands/cargo-update.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/crate/cargo-audit/latest
- https://docs.rs/crate/cargo-deny/latest
- https://docs.rs/crate/cargo-outdated/latest
- https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- https://docs.rs/sello/latest/sello/
