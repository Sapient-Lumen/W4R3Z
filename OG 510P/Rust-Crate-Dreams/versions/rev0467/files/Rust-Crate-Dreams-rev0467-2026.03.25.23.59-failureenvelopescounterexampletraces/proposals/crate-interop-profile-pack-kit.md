---
id: P-0511
title: Crate Interop Profile Pack Kit — shared library-ecosystem contracts, pairwise compatibility receipts, and migration-hazard reports
status: research
domains: [ecosystem, interop, libraries, cargo, docs, api, semver, async]
last_reviewed: 2026-03-17
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  - https://docs.rs/http
  - https://docs.rs/tower-service
  - https://docs.rs/tower/latest/tower/
  - https://docs.rs/axum/latest/axum/
  - https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
  - https://docs.rs/serde
---

# Problem

The archive now has two stronger ecosystem-supportiveness lanes:

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** for task-first crate choice,
2. **P-0510 Crate Capability Contract & Interop Profile Kit** for producer-side support and interop claims.

That progress reveals a third missing layer.

Rust’s latest official vision work explicitly says that helping users navigate crates is only *part* of the solution and that Rust also needs **better interop between libraries**.
It even names likely shapes of that work: **key interop traits** and **standard building blocks** such as the `http` crate.

But today the ecosystem still lacks a boring, shared way to say things like:

- “This crate participates in the **runtime-neutral async library** profile.”
- “This middleware crate really fits the **`tower-service` + `http`** service boundary.”
- “This model crate fits the **Serde data-model boundary** without leaking format-specific coupling.”
- “This release still conforms to the same interop profile as the previous one, or if not, here is the migration hazard.”

We have substrate, but not the joined interop contract:

- `http` already provides common HTTP types.
- `tower-service` already provides a core `Service` abstraction.
- `futures-core` already provides foundational async traits like `Stream`.
- Serde already provides a widely shared data-model bridge.
- official language/project-goal work is actively trying to make shared customization points and evolving library hierarchies easier to express and evolve.
- `cargo-semver-checks` is becoming more important for public-API drift.

Those are **building blocks** and **slice tools**.
They still do not create one shared, versioned answer to:

> what exactly does it mean for a crate to interoperate in this library ecosystem lane, and how can other people verify it?

The missing crate is therefore not another ranking engine, not another producer-side metadata schema, and not another semver linter.
It is a **shared interop-profile pack kit**: a crate that defines ecosystem profile packs, checks crate conformance against them, compares two crates or adapters under the same profile, and emits migration-hazard receipts.

# What it provides

## Core artifacts

- `interop-profile-pack.toml` — versioned definition of one ecosystem profile, including required public traits/types, forbidden coupling, optional adapters, and manual-review zones.
- `static-conformance.receipt.json` — facts observed from manifests, public API surfaces, rustdoc JSON, and feature layouts.
- `behavioral-probe.report.json` — optional compile/run probes that check whether a crate behaves like the profile promises.
- `pair-compatibility.report.json` — whether provider crate A and consumer crate B actually line up under the selected profile.
- `migration-hazards.report.json` — what changed across releases that could silently tighten lock-in, reduce compatibility, or force downstream rewrites.
- `interop-summary.md` — short human-facing profile explanation and caveats.

## Commands

- `cargo interop-profile init`
- `cargo interop-profile observe`
- `cargo interop-profile check --profile <profile>`
- `cargo interop-profile pair --profile <profile> --provider <crate> --consumer <crate>`
- `cargo interop-profile doctor`
- `cargo interop-profile diff <old> <new>`
- `cargo interop-profile summary --profile <profile>`
- `cargo interop-profile pack`

## 0.1 profile families

A first version should stay narrow and boring:

1. `async_runtime_neutral_public_api`
   - internal Tokio use may be fine,
   - public API should prefer `Future` / `Stream` / poll-style interfaces,
   - runtime lock-in must be explicit if it exists.
2. `tower_http_service_boundary`
   - service/middleware boundary built around `tower-service` and `http`,
   - request/response/body/error coupling made explicit,
   - tower-style layers and adapters treated as first-class.
3. `serde_data_model_boundary`
   - model crates that expose Serde-compatible data structures without quietly becoming format-specific frameworks.

# What the crate should provide other people

1. **Shared ecosystem contracts** for important library lanes instead of “tribal knowledge plus README hints”.
2. **A reusable profile vocabulary** that pathfinder-style tools, docs portals, and crate capability contracts can all import.
3. **Conformance receipts** that tell maintainers and adopters whether a crate really fits a profile or only claims to.
4. **Pairwise compatibility reports** so adapter seams and hidden lock-in become reviewable.
5. **Migration-hazard reports** that warn when a release silently narrows interoperability while remaining semver-ambiguous.
6. **Small, commit-able artifacts** that teams can review in CI or attach to release notes.

# Users & user stories

- **Library maintainer**: “Show that our crate stays runtime-neutral even though we use Tokio internally.”
- **Framework maintainer**: “Check whether our middleware and router still conform to the same `tower-service`/`http` profile as last release.”
- **App team**: “Verify that this provider crate and this consumer crate actually meet at the same boundary before we wire them together.”
- **Educator / docs author**: “Teach one HTTP stack or async stack without hand-waving what ‘compatible’ means.”
- **Pathfinder / curation tool author**: “Import shared interop profile results instead of inventing our own hidden rules.”

# Prior art (and why it’s insufficient)

- The Rust vision-doc work explicitly says smoother library interop is part of the answer and even names key interop traits / standard building blocks like `http`.
- The `http`, `tower-service`, `futures-core`, and Serde crates already provide powerful shared substrate.
- The evolving-traits and EII goal work makes it easier to *introduce* or *evolve* shared extension points over time.
- `cargo-semver-checks` is improving the ability to detect public-API breakage and witness compatibility.

What remains missing is the small **profile-pack + conformance + pair-compatibility** layer above those pieces.

# Design goals

1. **Shared-profile first** — define ecosystem contracts once and reuse them across crates.
2. **Static plus behavioral honesty** — keep API-surface checks distinct from optional behavioral probes.
3. **Pairwise reality checks** — some interop only becomes obvious when provider and consumer are checked together.
4. **Import, don’t absorb** — capability contracts, semver linting, health, trust, and task ranking stay separate lanes.
5. **Versioned profile packs** — profile changes must be diffable and reviewable.
6. **Migration-aware** — the crate should help explain *why* interop got worse, not only fail with “not compatible”.
7. **Broad applicability** — the same substrate should work for async, HTTP, serialization, diagnostics, GUI event layers, and future ecosystem building blocks.

# Non-goals

- Choosing the best crate for a task.
- Replacing producer-side capability contracts.
- Replacing `cargo-semver-checks`, `cargo-public-api`, or trait-evolution planning.
- Becoming a domain-specific protocol conformance suite.
- Acting as a registry ranking engine or health/trust score.

# Architecture & API sketch

## Crate split

- `interop-profile-core` — schema, diff engine, profile vocabulary
- `interop-profile-observe` — Cargo / rustdoc JSON / manifest / feature imports
- `interop-profile-probe` — compile witnesses and optional runtime probes
- `interop-profile-catalog` — shipped profile packs for common ecosystem lanes
- `cargo-interop-profile` — CLI workflow

## Core types

```rust
pub enum EvidenceClass {
    StaticObserved,
    BehavioralObserved,
    Inferred,
}

pub struct InteropProfilePack {
    pub id: String,
    pub version: String,
    pub required_public_surfaces: Vec<String>,
    pub forbidden_public_coupling: Vec<String>,
    pub optional_adapter_surfaces: Vec<String>,
    pub manual_review_zones: Vec<String>,
}

pub fn check_profile(root: &Path, profile: &InteropProfilePack) -> Result<StaticConformanceReceipt>;
pub fn run_behavioral_probes(root: &Path, profile: &InteropProfilePack) -> Result<BehavioralProbeReport>;
pub fn compare_pair(profile: &InteropProfilePack, provider: &Path, consumer: &Path) -> Result<PairCompatibilityReport>;
pub fn diff_reports(old: &InteropBundle, new: &InteropBundle) -> MigrationHazardsReport;
```

## Static checks in 0.1

- manifest and feature inspection
- public type/trait scanning via rustdoc JSON or compile witnesses
- explicit detection of public runtime-specific or format-specific coupling
- adapter-feature declaration import

## Behavioral probes in 0.1

- tiny compile-witness programs
- optional probe crates for provider/consumer handshakes
- exact / conservative / manual-review result classes

# Security / safety model

- Default to read-first analysis and tiny witness programs.
- Keep probe execution opt-in and profile-scoped.
- Treat heuristic results as labeled evidence, not truth.
- Export redaction-friendly receipts for shared CI artifacts.
- Make `manual_review_required` a first-class successful outcome.

# Maintenance & governance plan

- Keep the core profile schema intentionally small.
- Version profile packs independently from the CLI.
- Maintain a public fixture corpus of both happy-path and deceptive cases.
- Require every built-in profile to document both **what counts as success** and **what still needs manual judgment**.
- Encourage other tools to import the profile vocabulary rather than forking it.

# Milestones

## 0.1
- profile-pack schema
- static conformance receipts
- pair-compatibility report
- three narrow built-in profiles
- migration-hazards diff

## 0.2
- compile-witness generator
- behavioral probe runner
- markdown summary exporter
- CI action for profile drift

## 1.0
- stable schemas
- public profile-pack registry process
- broad fixture corpus across at least six ecosystem lanes
- importer guidance for pathfinder/capability-contract/doc portals

# Open questions

- Which ecosystem building blocks deserve built-in profiles first without becoming political or bloated?
- How much pairwise probing is needed before profile results stop feeling small and boring?
- Which migration hazards should be classified as advisory versus hard incompatibility?
- Should built-in profiles live in the crate, a separate registry crate, or both?
- What is the cleanest division of labor between this crate, producer-side capability contracts, and task-first crate selection?

Treat `meta/crate-interop-profile-product-plan-2026-03-17.md` as the working build sketch for **P-0511**.

# Sources

- Rust vision-doc work on supportiveness, crate navigation, and smoother interop between libraries: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Externally Implementable Items goal: https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- Evolving trait hierarchies goal: https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- cargo-semver-checks goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- `http` crate docs: https://docs.rs/http
- `tower-service` crate docs: https://docs.rs/tower-service
- `futures-core::Stream` docs: https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- Serde docs: https://docs.rs/serde
