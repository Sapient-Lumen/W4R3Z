# V0 kernel brief: Build-State Pack

## Identity
- candidate: **Build-State Evidence**
- macro-program: **Evidence Spine**
- current verdict context: `advance`
- kernel codename: `build-state-pack/v0`

## Why this kernel and not a bigger build
The first honest build is not a hosted analytics service and not a remote cache product.
It is a **local-first companion tool** that captures what Cargo just did, diffs two sessions, and produces a doctor-style explanation packet for rebuilds and cache/layout pain.
That is justified because Cargo build analysis is still prototyping exactly the kind of metadata the ecosystem needs, Cargo is still iterating on build-dir layout and locking, and Cargo already documents stable external-tool seams (`cargo metadata`, JSON messages, custom subcommands).
Relevant sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Repo shape
Suggested first repo tree:
- `crates/build-state-cli/` — user-facing binary, plausibly exposed as `cargo buildstate`
- `crates/build-state-model/` — canonical session-pack types and diff types
- `crates/build-state-import/` — adapters for stable Cargo seams plus optional unstable-report adapters
- `crates/build-state-doctor/` — heuristic explanations and caveat labels
- `schemas/build-state-pack-v0.schema.json` — machine-readable pack schema
- `fixtures/sessions/` — captured example sessions across proving grounds
- `fixtures/layout-migrations/` — build-dir-layout-v2 and legacy comparisons
- `docs/proving-grounds.md` — how to reproduce the first proving-ground runs

## User surfaces
The first user surfaces should be three commands only:
1. `capture` — record one build/check/test session into a machine-readable pack
2. `diff` — compare two packs and explain what changed
3. `doctor` — summarize likely causes of rebuild / contention / artifact-path surprises

The pack should expose at least:
- package/workspace identity
- enabled features and target/profile information
- artifact messages and `fresh` posture from JSON output
- build-script outputs that affect downstream compilation
- explicit caveat labels when information came from unstable `cargo report *` surfaces

## Import seams
Required stable imports:
- `cargo metadata --format-version=1`
- `cargo ... --message-format=json`
- environment/config receipts used by the build run

Optional unstable imports with caveat labels:
- `cargo report timings`
- `cargo report rebuild`
- `cargo report sessions`
- build-dir-layout-v2 specific path receipts when available

Do **not** link Cargo as a library for the first build.
Cargo's own docs say the library API is unstable and recommend the CLI interface for third-party tools.

## Proof assets
The kernel should emit:
- one `build-state-pack.json`
- one human-readable diff summary
- one doctor note with explicit unsupported-state receipts
- one migration receipt when layout assumptions are implicated

The first schema should privilege **explainability over completeness**.
It does not need to encode every Cargo internal.

## Proving grounds
Run first in four environments:
1. local iterative `cargo check` / `cargo build` loops on a medium workspace
2. Cargo vs Rust Analyzer contention cases
3. CI-local comparisons where target/build-dir placement differs
4. nightly `-Zbuild-dir-new-layout` runs against the same project

## Owner shape / upkeep
Best first owner:
- small build-infra team or external tool maintainer comfortable with Cargo churn

Immediate upkeep tax:
- adapter churn around unstable report surfaces
- layout-migration receipts
- schema versioning
- proof fixtures for mixed local/CI environments

## Refused expansions
Do not let v0 become:
- a remote telemetry pipeline
- a cache-management platform
- a universal performance oracle
- or a claim that Cargo's prototype report surfaces are already stable contracts

## Exit criteria
This kernel has earned stage advancement when it can show:
- repeatable packs across at least three real proving grounds
- useful diffs on build-layout and rebuild changes without excessive false certainty
- explicit support posture for stable-only vs unstable-enhanced runs
- and at least one maintained migration receipt for build-dir-layout churn

