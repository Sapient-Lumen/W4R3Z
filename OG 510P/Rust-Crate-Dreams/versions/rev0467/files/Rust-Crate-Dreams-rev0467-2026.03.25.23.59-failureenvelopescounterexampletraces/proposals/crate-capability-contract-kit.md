---
id: P-0510
title: Crate Capability Contract & Interop Profile Kit — machine-readable support claims, interop export maps, and reviewable profile-conformance receipts
status: research
domains: [cargo, crates-io, docs, metadata, interop, discoverability, api, msrv, tooling]
last_reviewed: 2026-03-17
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://doc.rust-lang.org/cargo/reference/manifest.html
  - https://doc.rust-lang.org/cargo/reference/rust-version.html
  - https://docs.rs/about/metadata
  - https://docs.rs/about/rustdoc-json
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
  - https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
  - https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html
  - https://embarkstudios.github.io/cargo-deny/
  - https://github.com/cargo-public-api/cargo-public-api
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
---

# Problem

Rust now has two unusually clear official pressures at once:

1. users need better help **choosing crates** and getting oriented in the ecosystem,
2. and the project wants **better interop between libraries**, especially around widely shared building blocks.

The archive’s new **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** addresses the consumer side of that problem: task-first selection.
But that immediately exposes a second missing layer.

Today, crate authors still do not have one shared, boring way to publish machine-readable answers to questions like:

- Is this crate’s public API runtime-neutral, or does it really couple callers to Tokio or another executor?
- Is `no_std` real, `alloc`-only, docs-only, or only true on one target family?
- Does adopting this crate imply proc-macro use, `build.rs`, native linkage, external toolchains, or docs.rs-specific feature assumptions?
- Which interop ecosystems does the crate intentionally participate in: `serde`, `tracing`, `http`, `tower-service`, `bytes`, `futures-core`, `wasm-bindgen`, and so on?
- Which support claims are declared policy, which are directly observed, and which still require manual review?

Cargo/crates.io/docs.rs already expose **pieces** of this story:

- tiny manifest metadata (`keywords`, `categories`, `rust-version`, `build`, `links`, generic `package.metadata`),
- docs.rs build metadata,
- rustdoc JSON,
- crate-page security/SLOC/pubtime improvements,
- and a growing ecosystem of slice-specific tools such as `cargo-msrv`, `cargo-deny`, `cargo-public-api`, and `cargo-semver-checks`.

That is real substrate.
But it is still not a **joined crate-published support/interop contract** that other people can actually rely on.

The missing crate is therefore **not** another search engine, not another ranking formula, and not another README badge pack.
It is a **producer-side capability contract kit**: one schema and workflow that crate authors can publish, CI can check, and ecosystem tools can import.

# What it provides

## Core artifacts

- `capability-contract.toml` — author-declared support profiles, interop claims, and explicit manual-review zones; intended to round-trip from `package.metadata` when desired.
- `observed-capabilities.receipt.json` — normalized facts observed from `Cargo.toml`, docs.rs metadata, rustdoc JSON, and optional CI/build receipts.
- `interop-exports.report.json` — public interop surfaces the crate actually exposes or depends on for downstream use (for example `serde`, `http`, `tower-service`, `futures-core`, `tracing`).
- `profile-conformance.report.json` — whether each declared support profile is satisfied by observed facts, mismatched, or still requires manual review.
- `capability-diff.report.json` — how a crate’s published support/interop posture changed between two releases or branches.
- `claim-class.policy.json` — what claim classes mean and what evidence they require.
- `support-obligation.receipt.json` — normalized observation of build/native/docs/target/MSRV obligations.
- `profile-fidelity.report.json` — how complete each advertised support profile really is.
- optional `capability-summary.md` — a concise downstream-facing explanation for docs, issue templates, or release notes.

## Commands

- `cargo capability-contract init`
- `cargo capability-contract observe`
- `cargo capability-contract check`
- `cargo capability-contract doctor`
- `cargo capability-contract summary`
- `cargo capability-contract diff <old> <new>`
- `cargo capability-contract pack`

## First-class claim classes

This crate should preserve three visibly separate fact types:

1. **declared** — what maintainers say they support,
2. **observed** — what tools can confirm from manifests/docs/API outputs/CI receipts,
3. **inferred** — conservative deductions that should stay labeled as such.

# What the crate should provide other people

1. **One machine-readable support/interop contract** instead of README archaeology.
2. **A reusable vocabulary** for producer-side crate posture: runtime coupling, `std`/`alloc`/`core`, docs posture, proc-macro/build-script/native-linkage exposure, target classes, and interop exports.
3. **A conformance report** that tells downstream users where the crate’s stated support story matches reality and where it does not.
4. **A diffable change surface** so releases cannot silently tighten support, add new native obligations, or shift interop posture without review.
5. **A good import target** for pathfinder-style selection tools, docs generators, support bots, and LLM-based ecosystem guidance.

# Users & user stories

- **Crate maintainer**: “Publish one honest support contract for this crate instead of burying it across README tables, docs.rs metadata, and issue replies.”
- **Pathfinder / starter-set tool author**: “Import a stable producer-side artifact instead of scraping prose and heuristics.”
- **Application team**: “Tell us whether this crate is truly runtime-neutral and whether it pulls in `build.rs`, proc macros, or native linkage.”
- **Embedded / Wasm adopter**: “Show whether `no_std` means `core`-only, `alloc`, or ‘works locally but docs.rs builds with `std` assumptions’.”
- **Educator / docs author**: “Generate a concise, current support summary that matches the crate’s declared and observed posture.”
- **Security / platform team**: “Import support posture without confusing it with trust scoring, advisories, or provenance.”

# Prior art (and why it’s insufficient)

- **Cargo manifest metadata** already includes `keywords`, `categories`, `rust-version`, `build`, `links`, and a generic `package.metadata` table for external tools.
  That is valuable substrate, but it is intentionally generic and too small to express a shared support/interop contract.
- **docs.rs metadata** already allows crates to describe how docs should be built.
  That is useful for documentation hosting, but not the same thing as a downstream support claim.
- **rustdoc JSON** provides a programmatic view of public API.
  That is excellent observation substrate, but not a complete contract by itself.
- **crates.io** now exposes security advisories, SLOC, and publication time more directly.
  Those are good signals, but still not a producer-side interop/support profile.
- **RFC 1824** explicitly says crates.io should not attempt to judge “suitability for the current task”.
  That is one reason this lane should remain a separate crate artifact, not a demand that the registry magically know everything.
- **Slice tools** like `cargo-msrv`, `cargo-deny`, `cargo-public-api`, and `cargo-semver-checks` are already useful.
  But each covers one slice: MSRV, dependency/security policy, public API, or semver drift. None provides the joined contract that pathfinder-style tools and downstream adopters actually want.

# Design goals

1. **Producer-side honesty** — optimize for what crate authors can promise and what tools can verify.
2. **Small joined artifacts** — make the contract easy to publish, diff, cache, and import.
3. **Claim-class separation** — keep declared, observed, and inferred facts visibly distinct.
4. **Interop-aware** — shared ecosystem building blocks should be first-class, not prose footnotes.
5. **Import, don’t absorb** — MSRV policy, trust/risk, SBOM/provenance, and full semver diffing remain adjacent lanes.
6. **Task-adjacent, not task-solving** — the contract should help selection tools without becoming a ranking engine itself.
7. **Broad applicability** — the same schema should help CLI, async services, `no_std`, Wasm, GUI, data, and niche domain crates.

# Non-goals

- Replacing crates.io search or ranking.
- Producing a universal “best crate” answer for a task.
- Replacing `cargo-msrv`, `cargo-deny`, `cargo-public-api`, or `cargo-semver-checks`.
- Becoming a full per-item cfg-availability matrix; that belongs with **P-0451 Cfg Availability Ledger Kit**.
- Becoming a whole-project toolchain/target support contract; that belongs with **P-0484 Toolchain & Target Support Contract Kit**.
- Acting as a provenance, SBOM, or trusted-publishing system.

# Architecture & API sketch

## Crate split

- `capability-contract-core` — schema types, claim vocabulary, diff engine
- `capability-contract-observe` — imports from `Cargo.toml`, docs.rs metadata, rustdoc JSON, and optional CI receipts
- `capability-contract-interop` — detectors/mappers for common ecosystem contracts
- `cargo-capability-contract` — CLI workflow

## Core types

```rust
pub enum ClaimClass {
    Declared,
    Observed,
    Inferred,
}

pub struct SupportProfile {
    pub id: String,
    pub runtime_coupling: RuntimeCoupling,
    pub std_support: StdSupport,
    pub target_classes: Vec<String>,
    pub docs_posture: DocsPosture,
    pub native_obligations: Vec<NativeObligation>,
}

pub fn observe(root: &Path) -> Result<ObservedCapabilitiesReceipt>;
pub fn detect_interop_exports(receipt: &ObservedCapabilitiesReceipt) -> InteropExportsReport;
pub fn check_conformance(contract: &CapabilityContract, observed: &ObservedCapabilitiesReceipt) -> ProfileConformanceReport;
pub fn diff_contracts(old: &CapabilityBundle, new: &CapabilityBundle) -> CapabilityDiffReport;
```

## 0.1 profile vocabulary

A first version should make these axes explicit:

- runtime coupling (`neutral`, `tokio_coupled`, `executor_agnostic_but_futures_based`, `unknown`)
- `std` posture (`core_only`, `alloc`, `std_required`, `mixed`, `docs_only_claim`)
- native obligations (`none`, `build_rs`, `links`, `external_toolchain`, `manual_setup_required`)
- public interop exports (`serde`, `tracing`, `http`, `tower-service`, `bytes`, `futures-core`, `wasm-bindgen`, etc.)
- docs posture (`docsrs_default`, `docsrs_custom`, `local_only`, `manual_review_required`)

# Security / safety model

- Default to **read-first observation** and explicitly labeled imports.
- Never silently claim that a declared profile is verified without an observation source.
- Preserve path/source freshness and redaction support in receipts.
- Treat heuristic interop detection as advisory until a confidence threshold is met.
- Make “manual review required” a first-class successful output, not a failure.

# Maintenance & governance plan

- Keep the schema intentionally small and versioned.
- Version detector packs for common ecosystem contracts separately from the core schema.
- Maintain a fixture corpus that includes both easy wins and deceptive cases.
- Publish explicit guidance for how crates should evolve contracts across semver releases.
- Encourage consumers like pathfinder tools and docs portals to import the contract, not fork the vocabulary.

# Milestones

## 0.1
- core schema
- observation from manifest/docs.rs metadata/rustdoc JSON
- three common profile families (`runtime-neutral async lib`, `no_std`/`alloc`, `proc-macro + native obligations`)
- conformance report and diff support

## 0.2
- imports from MSRV/trust/public-API slice tools when available
- richer interop detectors
- markdown summary generator
- CI action for contract drift checks

## 1.0
- stable schema
- broad fixture corpus across at least six crate families
- published guidance for consumers like pathfinder/doc portals/LLMs
- explicit semver policy for contract evolution

# Open questions

- Should the canonical authoring surface live in `package.metadata`, a sidecar file, or both?
- Which interop ecosystems deserve first-class detectors in 0.1 without bloating the schema?
- How much CI/test evidence should be imported before the bundle stops feeling small and boring?
- How should the crate represent “documented support” versus “continuously verified support” without overpromising?
- What is the cleanest relationship between this crate’s contract and per-item availability ledgers like **P-0451**?

# Sources

- Rust vision-doc work on crate navigation and smoother interop: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Cargo manifest metadata, including `keywords`, `categories`, `build`, `links`, and `package.metadata`: https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo `rust-version` support expectations and third-party MSRV tooling note: https://doc.rust-lang.org/cargo/reference/rust-version.html
- docs.rs custom-build metadata: https://docs.rs/about/metadata
- docs.rs rustdoc JSON: https://docs.rs/about/rustdoc-json
- crates.io development update (security tab, SLOC, `pubtime`): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RFC 1824 crates.io default ranking (and why task suitability is separate): https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html
- cargo-deny: https://embarkstudios.github.io/cargo-deny/
- cargo-public-api: https://github.com/cargo-public-api/cargo-public-api
- cargo-semver-checks project goal: https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html


## Productization note — 2026-03-17

Treat `meta/crate-capability-contract-product-plan-2026-03-17.md` as the working build sketch for **P-0510**.
The key new planning detail is that a capability-contract crate should elevate **claim-class policy**, **support-obligation receipts**, and **profile-fidelity reports** into first-class artifacts rather than flattening everything into one generic support verdict.
A plausible `0.1` should stay centered on `init`, `observe`, `check`, `doctor`, `summary`, `diff`, and `pack` workflows above today's Cargo/docs.rs/rustdoc substrate.
