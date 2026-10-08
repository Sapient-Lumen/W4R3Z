# Current decision packet: Build-State Evidence (`advance`)

Status: **live current-decision packet**

## Identity
- candidate: **Build-State Evidence**
- macro-program: **Evidence Spine**
- packet role: `live-decision-packet/v0`
- requested verdict now: `advance`

## Why now
- Cargo build analysis still aims to record build metadata across invocations and add `cargo report` subcommands for rebuild reasons and timing history.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo 1.94 is still extending `cargo report timings`, `cargo report rebuild`, and `cargo report sessions`.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The build-dir-layout-v2 testing call says many tools still rely on unspecified build-dir details because features are missing in Cargo, which means a bounded companion layer is still useful.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo still documents stable companion seams: `cargo metadata`, `--message-format`, and custom subcommands.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- The 2025 State of Rust survey still keeps resource usage in the pain band.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Practical decision improved
A developer or build steward can answer:
- what rebuilt,
- why it rebuilt,
- what changed across two sessions,
- and whether cache layout, lock contention, or configuration drift is the likely source of pain.

## Bounded next move
Advance one bounded family:
- `build-state-pack/v0`
- `build-state-diff/v0`
- `build-state-doctor/v0`

The import spine should be:
- `cargo metadata --format-version=1`
- `--message-format=json`
- optional unstable `cargo report *` adapters with explicit caveat labels

## Earned proof
- strong upstream directional fit exists;
- stable integration seams already exist;
- proving grounds are obvious: local dev loops, CI/local comparisons, and Cargo-vs-Rust-Analyzer contention.

## Missing proof / blockers
- no stable final schema exists for the newest report surfaces;
- proving-ground examples still need more shared-cache and mixed-workflow coverage;
- some build-dir-layout-dependent workarounds remain in motion.

## Negative states and caveats
- unstable report/build-analysis surfaces must stay caveated;
- the pack may explain change and contention without prescribing the optimal fix;
- the build-dir-layout-v2 shift means adapters need explicit drift receipts.

## Owner shape / upkeep
- best first owner: small companion-tool or build-infra team
- upkeep tax: adapters, proving-ground refresh, unstable-surface caveat tracking, doc maintenance

## Refused larger forms
- hosted analytics control plane
- remote build-cache empire
- pretending prototype goals already equal stable contracts

## Reissue triggers
- Cargo stabilizes or materially renames report/build-analysis surfaces
- build-dir-layout-v2 changes the downstream assumptions again
- a better official plumbing seam lands

## Source candor
- Cargo Book external-tools docs: stable seam evidence
- project goals and Cargo cycle posts: in-flight direction, not final contract
- survey results: pain framing, not artifact proof

## Decision rationale
`advance` is the honest verdict because the kernel is narrow, the seam is real, and the next move can stay local-first and companion-first.
It is not a wider launch authorization.
