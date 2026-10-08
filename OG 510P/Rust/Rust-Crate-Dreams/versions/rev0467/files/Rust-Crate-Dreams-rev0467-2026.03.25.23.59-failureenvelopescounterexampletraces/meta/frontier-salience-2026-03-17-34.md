# Frontier salience scan — 2026-03-17 (crate authority surfaces promoted as the sandbox/offline/determinism-support lane)

This pass added a new top-level proposal: **P-0519 Crate Authority Surface Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding an eleventh distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), **P-0516** (configuration/setup scenarios), **P-0517** (performance envelopes), and **P-0518** (observability surfaces).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another sandbox runtime,
- another static authority linter,
- another capability-oriented replacement for `std`,
- another “secure by default” wrapper,
- or another org-wide policy platform.

It is the boring crate that can hand other people:

- one **authority pack**,
- one **authority-surface receipt**,
- one **authority-profile report**,
- one **determinism-surface report**,
- one **capability-injection report**,
- one **sandbox-recipe manifest**,
- one **authority-check report**,
- and one **authority diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0518 Crate Observability Surface Pack Kit**
9. **P-0519 Crate Authority Surface Pack Kit**
10. **P-0512 Crate Guidance Pack Kit**
11. **P-0513 Crate Runtime Handoff Pack Kit**
12. **P-0515 Crate Off-Ramp Pack Kit**
13. **P-0510 Crate Capability Contract & Interop Profile Kit**
14. **P-0511 Crate Interop Profile Pack Kit**
15. **P-0429 rustc_public Analysis Workbench Kit**

## Why P-0519 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, which makes host-authority posture a plausible crate support surface rather than mere security folklore.
- The 2025 survey says **docs and code** are still the main learning surfaces, while resource-usage and debugging problems remain meaningful; authority assumptions hidden in code paths or issue comments are therefore still too implicit.
- The Rust project-goals page on sandboxed build scripts says file-system and network access can be sandboxed and that doing so improves determinism, which shows ambient side effects and determinism are explicit design concerns in current Rust work.
- Cargo already documents large environment-variable and build-script surfaces, which means authority posture is already real but scattered.
- `ambient-authority`, `cap-std`, and `wasi-cap-std-sync` show there is meaningful capability-based substrate for filesystem, network, time, and host wiring.
- `rustix` explicitly says it does not restrict ambient authorities or impose sandboxing, which clarifies that low-level substrate is not the same thing as a receiver-facing crate contract.

That means the lane is both:

- **timely** — because the ecosystem already has enough substrate that the missing value is now the support artifact,
- and **distinct** — because the missing value is a crate-authored authority surface above capability/sandbox building blocks and below policy platforms.

## What changed in the archive

Added:
- `proposals/crate-authority-surface-pack-kit.md`
- `meta/crate-authority-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-34.md`
- `fixtures/crate-authority-surface-pack-kit/`
- `entries/2026-03-17-205.md`

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
- setup scenarios,
- observability surfaces,
- compile-time sandbox policy,
- capability-based runtime substrate,
- static authority scanning,
- and full sandbox/runtime host platforms

into one fake “Rust sandboxing solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
- https://docs.rs/cap-std/latest/cap_std/
- https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- https://docs.rs/rustix/latest/rustix/
- https://docs.rs/wasi-cap-std-sync/latest/wasi_cap_std_sync/
- https://docs.rs/getrandom/latest/getrandom/
