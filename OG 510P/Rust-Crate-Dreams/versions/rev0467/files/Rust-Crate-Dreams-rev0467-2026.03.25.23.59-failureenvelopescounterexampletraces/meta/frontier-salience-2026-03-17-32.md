# Frontier salience scan — 2026-03-17 (crate performance envelopes promoted as the performance-support lane)

This pass added a new top-level proposal: **P-0517 Crate Performance Envelope Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a ninth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), and **P-0516** (configuration/setup scenarios).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another benchmark runner,
- another profiler,
- another hosted regression service,
- another screenshot-heavy benchmark dashboard,
- or another scenario-pack variant with perf numbers bolted on.

It is the boring crate that can hand other people:

- one **perf pack**,
- one **perf-surface receipt**,
- one **perf-scenario report**,
- one **perf-recipe manifest**,
- one **perf-check report**,
- one **perf-budget report**,
- one **perf diff**,
- and one explicit **manual-review boundary** when hardware noise or workload representativeness make automatic verdicts dishonest.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0512 Crate Guidance Pack Kit**
9. **P-0513 Crate Runtime Handoff Pack Kit**
10. **P-0515 Crate Off-Ramp Pack Kit**
11. **P-0510 Crate Capability Contract & Interop Profile Kit**
12. **P-0511 Crate Interop Profile Pack Kit**
13. **P-0429 rustc_public Analysis Workbench Kit**
14. **P-0490 Cargo Lock Contention Witness Kit**
15. **P-0430 Build-Std Workbench Kit**

## Why P-0517 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, and performance expectations are one of the biggest missing supportive surfaces in Rust’s library ecosystem.
- The 2025 survey says **docs and code** are still the main learning surfaces while **resource usage** and debugging continue to show up as productivity pain.
- Cargo already has real benchmark and profile substrate, including custom harness support and first-class profile selection, which means the missing value is not “benchmarking exists nowhere”.
- Cargo’s profile docs explicitly warn that optimization settings can have surprising results and should be reevaluated over time, which makes stable performance posture a real review artifact rather than a one-time tweak.
- Current benchmark tools already cover multiple useful measurement philosophies: Criterion for statistical wall-time work, Iai-Callgrind for CI-stable instruction/cache-oriented work, Divan for stable modern benchmark authoring, and CodSpeed compatibility layers for CI-hosted execution.
- Existing tools still do not define the joined receiver-facing **performance envelope contract** above those surfaces.

That means the lane is both:

- **timely** — because Rust’s benchmark substrate and plugin ecosystem are mature enough that the next missing value is coordination and honesty,
- and **distinct** — because the missing value is a crate-authored performance contract above raw benchmark or profiling tools.

## What changed in the archive

Added:
- `proposals/crate-performance-envelope-pack-kit.md`
- `meta/crate-performance-envelope-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-32.md`
- `fixtures/crate-performance-envelope-pack-kit/`
- `entries/2026-03-17-203.md`

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
- support / interop claims,
- shared ecosystem profiles,
- configuration scenarios,
- compile-time guidance,
- runtime handoff,
- upgrade packs,
- off-ramp packs,
- generic benchmark frameworks,
- profiling evidence bundles,
- and hosted CI performance services

into one fake “Rust perf tooling solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
- https://docs.rs/criterion/latest/criterion/
- https://docs.rs/iai-callgrind/latest/iai_callgrind/
- https://docs.rs/crate/divan/latest
- https://docs.rs/crate/codspeed-criterion-compat/latest
- https://docs.rs/crate/codspeed-divan-compat/latest
