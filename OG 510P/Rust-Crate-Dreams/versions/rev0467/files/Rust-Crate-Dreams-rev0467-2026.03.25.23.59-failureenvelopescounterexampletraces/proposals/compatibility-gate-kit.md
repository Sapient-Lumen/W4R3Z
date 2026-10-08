---
id: P-0089
title: Compatibility Gate Kit — semver/ABI/behavioral regression gating for Rust crate releases
status: idea
domains: [cargo, devtools, release, semver, supply-chain]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/cargo-semver-checks
  - https://github.com/obi1kenobi/cargo-semver-checks/releases
  - https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
  - https://opensourcesecurity.io/2025/2025-04-cargo-semver-checks-predrag-gruevski/
---

## Problem
Rust has strong SemVer norms, but shipping non-breaking upgrades still causes real pain:
- Maintainers accidentally publish breaking API changes (even if small).
- “Not breaking” can still break in practice: feature-flag combos, MSRV drift, ABI expectations in plugin-ish scenarios, or subtle behavioral changes.
- Consumers lose trust and delay upgrades, which worsens security and ecosystem velocity.

`cargo-semver-checks` is a strong start, and is on a path toward deeper Cargo integration — but the ecosystem still lacks a **batteries-included, opinionated, end-to-end compatibility gate** that crate authors can adopt with minimal effort and *high confidence*.

## What it provides
A crate + cargo subcommand (and a ready-to-use CI profile) that gives other people:

1) **Compatibility report artifact (`.compat.json` + HTML summary)**
   - API surface diff results (powered by `cargo-semver-checks`).
   - MSRV / feature-matrix audit summary.
   - “Behavioral contract” test results (see below).
   - Signed/attested report option for supply-chain workflows.

2) **`cargo compat gate`**
   - Runs a standard pipeline and produces the report artifact.
   - Profiles: `quick`, `release`, `paranoid` (tunable but standardized defaults).

3) **Behavioral-regression hooks**
   - Optional “golden” tests: determinism checks, text/binary fixture round-trips, stable ordering invariants.
   - Snapshot-driven harness: outputs a machine-checkable evidence bundle for maintainers and downstreams.

4) **Feature-matrix + MSRV conformance**
   - Enumerate important feature combinations (user-declared “support tiers”) and run compile/tests across them.
   - Hard fail on MSRV policy violations (crate declares intent; tool enforces).

5) **Publish-time ergonomics**
   - GitHub Actions templates + local “doctor” mode.
   - “Explain like I’m a maintainer” failure messages: direct links to the relevant SemVer rule and suggested remedies.

## Users & user stories
- **Library maintainer:** “Before I publish, I want a single command that tells me if I broke someone.”
- **Enterprise adopter:** “I want policy gates that prevent accidental breaking changes and help us upgrade faster.”
- **Tooling ecosystem:** “I want a stable report format I can aggregate across many crates.”

## Prior art (and why it’s insufficient)
- `cargo-semver-checks` provides semver-focused API break detection and is evolving rapidly. The missing piece is the **opinionated wrapper** that standardizes *the rest*: report artifacts, feature/MSRV matrices, behavioral hooks, CI presets, and evidence bundles.  
  Evidence: crates.io and upstream project goals for integration path.

## Design sketch
### Core architecture
- **Library layer**: runs pipelines and emits structured report (`compat-report` crate).
- **CLI layer**: `cargo-compat` subcommand orchestrating compilation, diff, tests.
- **Adapters**:
  - `semver` adapter: shells out to `cargo-semver-checks` initially; later can link via library API if/when it stabilizes.
  - `matrix` adapter: uses `cargo-hack`-style strategies (optional dependency) or built-in resolver enumeration.

### Artifact formats
- `compat.json`: versioned schema (include tool version + inputs + outcomes).
- Optional `compat.bundle.zip`: logs + minimized reproducer (when possible) + machine info.

### Conformance
- Provide a small suite of “fixture crates” in-repo that ensure the tool catches known classes of breaks (API/feature/MSRV).
- CI for the tool itself must run those fixtures on stable/beta/nightly to prevent regressions in the gate.

## MVP scope (8–12 weeks)
- `cargo compat gate --profile quick`:
  - run `cargo-semver-checks`
  - run declared MSRV compile
  - run a small user-declared feature matrix
  - emit `compat.json` + short human summary
- GitHub Actions template + docs

## v1 scope (epic)
- Standardized behavioral hooks + golden fixture runner
- Signed/attested reports (optional)
- “Downstream simulation” mode: run a curated set of reverse-deps smoke tests (opt-in, cached)

## Risks & tradeoffs
- Toolchain instability (nightly features, rustdoc JSON changes): mitigate with adapter layers + pinned workflows.
- False positives that annoy maintainers: mitigate with profiles and precise, actionable diagnostics.

## Why this is “epic”
It makes *publishing compatible crates boring* — by giving maintainers and enterprises a single, trusted gate with standardized artifacts, enabling faster upgrades and better ecosystem health.
