# Current dossier: Build-State Evidence

## Identity
- candidate: **Build-State Evidence**
- macro-program: **Evidence Spine**
- current archive posture: `advance`

## Why this candidate is still load-bearing
- Cargo build analysis still aims to record build metadata across invocations and add unstable `cargo report` subcommands for rebuild reasons and timing history.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout-v2 testing call says many projects still rely on unspecified build-dir details because features are missing in Cargo, and explicitly asks people to test real workflows against nightly.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo still presents narrow third-party seams: `cargo metadata`, `--message-format`, and custom subcommands.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo 1.94 still lists plumbing commands among focus areas without progress, which means the seam remains valuable but not yet upstream-complete.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Current working judgment
This is still the clearest first serious build because the kernel is narrow, the proving grounds are real, and the artifact family can improve local developer decisions before any platform or service story exists.

## Next concrete move
Write or refresh one **live packet** for a bounded `build-state-pack/v0` family that includes:
- one import spine from `cargo metadata --format-version=1` plus JSON build messages;
- one adapter path for unstable build-analysis outputs with explicit caveat tags;
- one pack/diff/doctor trio;
- and one proving-ground README covering local-vs-CI and Cargo-vs-Rust-Analyzer contention cases.

## Earned proof
- current public substrate direction exists;
- proving grounds are obvious and current;
- the contribution can stay local-first and companion-first.

## Missing proof
- no stable upstream schema exists for the newest analysis surfaces;
- the archive still needs more concrete pack examples for mixed local/CI and shared-cache workflows.

## Owner shape / upkeep reality
- first owner shape: small build-infra companion team or strong external tool maintainer
- upkeep tax: adapter churn, caveat tracking, proving-ground refresh, documentation of unsupported states

## Refused larger forms
- hosted build analytics control plane
- remote cache empire
- pretending prototype goals already guarantee stable interfaces

## Reissue triggers
- Cargo stabilizes or materially changes report/build-analysis surfaces
- build-dir-layout changes downstream assumptions materially
- a better official plumbing seam appears

## Source candor
- Cargo Book external-tools docs: narrow operational seam
- project goals and testing call: directional/prototype evidence, not stable contract
- Cargo 1.94 cycle: current priority/focus evidence, not implementation proof
