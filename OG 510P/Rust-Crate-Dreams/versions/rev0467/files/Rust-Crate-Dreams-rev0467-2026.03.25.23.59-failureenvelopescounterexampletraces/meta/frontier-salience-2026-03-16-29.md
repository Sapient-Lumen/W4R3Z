# Frontier salience scan — 2026-03-16 (crate upgrade packs promoted as the release-to-release supportiveness lane)

This pass added a new top-level proposal: **P-0514 Crate Upgrade Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a sixth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), and **P-0513** (runtime handoff/support bundles).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another semver checker,
- another public-API report,
- another changelog generator,
- another release bot,
- or a universal codemod framework.

It is the boring crate that can hand other people:

- one **upgrade pack**,
- one **upgrade-hazards report**,
- one **fixup-hints receipt**,
- one **migration-recipe manifest**,
- one **upgrade-check report**,
- one **upgrade diff**,
- and one explicit **manual-review boundary**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0512 Crate Guidance Pack Kit**
7. **P-0513 Crate Runtime Handoff Pack Kit**
8. **P-0510 Crate Capability Contract & Interop Profile Kit**
9. **P-0511 Crate Interop Profile Pack Kit**
10. **P-0429 rustc_public Analysis Workbench Kit**
11. **P-0490 Cargo Lock Contention Witness Kit**
12. **P-0430 Build-Std Workbench Kit**
13. **P-0478 Cargo Future-Incompat Triage Kit**
14. **P-0470 Cargo Package Review Kit**
15. **P-0451 Cfg Availability Ledger Kit**

## Why P-0514 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, and release-to-release support is one of the biggest gaps still missing from that idea.
- The 2025 survey says **online documentation** is still the preferred canonical reference and **studying the code itself** is next, which means upgrade support needs structure, not just scattered release prose.
- The Rust project is actively moving `cargo-semver-checks` toward `cargo publish`, which raises the value of downstream-facing upgrade artifacts above raw compatibility verdicts.
- Cargo’s SemVer guidance and the `hint-mostly-unused` write-up make it clear that **features are part of the stable interface**, so upgrade hazards are not just about item-level API diffs.
- `cargo fix`, edition-migration guidance, `rustc` JSON diagnostics, and `rustfix` prove that suggestion-backed upgrades can be captured and replayed in a structured way.
- Existing release tools such as `release-plz` and `cargo-release` improve publishing workflows, but they still do not define a stable receiver-facing bundle for hazards, machine-fix lanes, checked recipes, and explicit manual-review zones.

That means the lane is both:

- **timely** — because Cargo and the Rust project are getting stricter about compatibility evidence while users still need better upgrade support,
- and **distinct** — because the missing value is a receiver-facing migration pack above semver/public-API slices and separate from release automation.

## What changed in the archive

Added:
- `proposals/crate-upgrade-pack-kit.md`
- `meta/crate-upgrade-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-29.md`
- `fixtures/crate-upgrade-pack-kit/`
- `entries/2026-03-16-200.md`

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

- semver witness evidence,
- public-API readiness review,
- release automation,
- changelog generation,
- compile-time guidance packs,
- runtime handoff packs,
- and domain-specific migration kits

into one fake “upgrade tooling solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://doc.rust-lang.org/cargo/reference/semver.html
- https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
- https://doc.rust-lang.org/beta/rustc/json.html
- https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- https://docs.rs/rustfix/latest/rustfix/
- https://release-plz.dev/docs/usage/update
- https://crates.io/crates/cargo-release
