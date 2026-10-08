---
id: P-0495
title: Cargo Artifact Dependency Adoption Kit — bindeps manifests, target-matrix env-var receipts, and stable-fallback bundles
status: idea
domains: [cargo, build, packaging, cross-compilation, devtools]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/reference/unstable.html#artifact-dependencies
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://rust-lang.github.io/rfcs/3028-cargo-binary-dependencies.html
  - https://rust-lang.github.io/rfcs/3176-cargo-multi-dep-artifacts.html
  - https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
---

# Problem

Cargo now has real substrate for **artifact dependencies**.

The official unstable-features docs describe artifact dependencies as a way to include build artifacts into other build artifacts and build them for different targets. RFC 3028 spells out the basic model: depend on a binary or C ABI artifact from another package and receive it through environment variables in `build.rs`. RFC 3176 pushes this further by allowing multiple renamed dependencies on the same crate/version so that one package can consume multiple target-specific artifacts.

That is already far beyond “maybe someday Cargo could expose binaries.” But ordinary maintainers still do not have a boring workflow above it.

They still need to answer questions like:
- which artifact kinds are expected for which target triples,
- which environment variables should show up in `build.rs`,
- when stable Cargo needs a fallback path,
- whether a given artifact-dependency layout is host-only, target-specific, or mixed,
- and how to explain multi-target rename patterns without asking every consumer to reread RFCs.

That means the missing crate is not another build runner and not a generic packaging system.

The missing crate is a **Cargo artifact dependency adoption kit**: a crate and cargo-adjacent tool that turns “we depend on another package’s binary/cdylib/staticlib artifact” into a portable **contract, target matrix, env-var receipt, and fallback bundle**.

# What it provides

- `artifact-contract.toml` — declares the artifact kinds consumed (`bin`, `cdylib`, `staticlib`, etc.), rename strategy, target expectations, host/target mapping, and stable fallback posture.
- `artifact-target-matrix.json` — normalized manifest of which packages/artifacts are expected for which target triples and whether they are host-built, target-built, or multi-target.
- `artifact-env.receipt.json` — records the environment variables/materialized artifact paths a build script or wrapper actually observed.
- `artifact-adoption.report.json` — classifies the setup as `single_target_ok`, `multi_target_renamed`, `missing_env_binding`, `stable_fallback_required`, `target_contract_mismatch`, `artifact_kind_mismatch`, `delegate_bridge_required`, `parameter_binding_gap`, or `manual_review_required`.
- `stable-fallback.plan.json` — suggests concrete next steps such as `use_prebuilt_binary`, `split_contract_by_target`, `rename_multi_target_dep`, `defer_to_build_script_path`, or `nightly_only_experiment`.
- `artifact-adoption.diff.json` — compares two manifests/receipts across targets, toolchains, or package-graph revisions.
- `cargo artifact-adopt snapshot` — capture one artifact-dependency bundle.
- `cargo artifact-adopt doctor` — explain whether the current contract is internally coherent and whether stable fallback is needed.
- `cargo artifact-adopt diff <old> <new>` — compare adoption receipts.
- `*.artdeps.zip` — portable support artifact for build engineers, package maintainers, or downstream integrators.

# What the crate should provide other people

1. **A boring answer to “what artifact contract are we actually depending on?”** instead of scattered manifest snippets and build-script assumptions.
2. **A target-aware receipt** that explains host-vs-target artifact expectations.
3. **A stable fallback story** for teams that cannot assume nightly Cargo everywhere.
4. **A shared vocabulary** for env-var bindings and rename strategies across multi-target cases.
5. **A bridge** between RFC-level capability and everyday adoption/debugging.

# Persona / who it’s for

- maintainers consuming tool binaries or native ABI artifacts from other Cargo packages
- firmware and embedded teams needing per-target artifacts
- build engineers managing mixed host/target helper binaries
- crate authors experimenting with artifact dependencies without wanting a fragile one-off setup

# Users & user stories

- **Build engineer**: “Show me which artifact paths and env bindings actually appeared for this build script.”
- **Embedded maintainer**: “Explain whether my renamed multi-target artifact dependencies are coherent.”
- **Library author**: “Give me one artifact contract I can hand to downstream users instead of an unstable-feature tribal-knowledge document.”
- **Support engineer**: “Tell me whether this failed because the wrong artifact kind or wrong target mapping was requested, or because stable fallback is required.”

# Prior art (and why it’s insufficient)

- Cargo’s unstable docs and RFCs explain the underlying capability, but not the boring maintainer workflow above it.
- The archive already has **P-0471 Cargo Artifact Handoff Kit**. That proposal is about **final artifacts produced by your build for downstream systems**.
- The archive already has **P-0479 Cargo Artifact Sidecar Contract Kit**. That proposal is about **sidecars attached to primary artifacts**.
- The archive already has **P-0457 External Toolchain Handshake Kit**. That proposal is about **non-Cargo orchestrators and compile-unit handshakes**.

What remains missing is the **artifact-dependency adoption layer** that answers: “which artifact contract, which target mapping, which env vars, and what fallback?”

## 2026-03-16 delegation bridge refresh

The newer upstream signals make this proposal sharper in one specific way: artifact dependencies are no longer just “consume another package's binary.”
They are also becoming part of the **future delegation story for build logic**.

The GSoC 2025 results say the next steps after multiple build scripts are parameter passing via manifest metadata and then delegating to external build-script packages using artifact dependencies.
Cargo 1.93 then adds a concrete polyfill-shaped design discussion around build-script artifact directives and how they might connect back to artifact dependencies.

That means this crate should not stop at:

- target-aware env-var capture,
- rename patterns,
- and stable fallback posture.

It should also explicitly help with the awkward seam where artifact dependencies become the **bridge substrate** between a package and a reusable external build helper.

So the proposal now needs to stay honest about three distinct lanes inside one adoption bundle:

1. **ordinary artifact consumption**
2. **multi-target / renamed artifact consumption**
3. **delegate-helper bridge posture**

That is still one worthy crate because the main question is the same:

> what artifact contract did we ask for, what bindings did we actually observe, and what fallback or bridge posture does this require?

# Design goals

1. **Contract-first** — make artifact expectations explicit and reviewable.
2. **Target-aware** — treat host/target/multi-target cases as first-class.
3. **Fallback-aware** — record when nightly Cargo is required and when a stable path exists.
4. **Interop-friendly** — useful for build scripts, wrappers, and CI.
5. **Conservative** — do not overclaim what unstable Cargo guarantees long-term.

# MVP surface

- Minimal types: `ArtifactContract`, `ArtifactTargetMatrix`, `ArtifactEnvReceipt`, `ArtifactAdoptionReport`, `StableFallbackPlan`, `ArtifactAdoptionDiff`, `ArtifactAdoptionBundle`
- Minimal functions:
  - `capture_artifact_env_receipt()`
  - `build_artifact_target_matrix()`
  - `classify_artifact_adoption()`
  - `suggest_stable_fallback_plan()`
  - `diff_artifact_adoption_receipts()`
- Feature flags:
  - `cargo`
  - `serde`
  - `markdown`
  - `build-script`

# Compatibility story

- Must remain useful even while artifact dependencies stay unstable.
- Must distinguish host-built helper artifacts from target-built runtime artifacts.
- Must understand RFC 3176-style renamed multi-target dependencies without assuming every possible future Cargo syntax is fixed.
- Should support a stable-only “planning mode” that validates the contract and fallback story without needing the unstable feature to run.
- Should treat missing env bindings as data, not as silent failure.

# Conformance & fixtures

- one fixture with a simple `bin` artifact dependency exposed through `build.rs`
- one fixture with multiple renamed dependencies on the same crate/version for different targets
- one fixture with artifact-kind mismatch (`bin` versus `cdylib`)
- one fixture where stable fallback requires a prebuilt artifact path instead of Cargo bindeps
- one fixture where a reusable build helper is consumed through an artifact-dependency-style bridge
- goldens for `single_target_ok`, `multi_target_renamed`, `target_contract_mismatch`, `missing_env_binding`, `stable_fallback_required`, `delegate_bridge_required`, and `parameter_binding_gap`

# Path to boring stability

- Freeze the contract and verdict vocabularies before adding fancier orchestration.
- Make stable fallback explicit from day one.
- Keep environment-variable mapping visible rather than implicit.
- Start with host/target mapping and renamed multi-target cases before broadening the scope.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and cargo subcommand that read one artifact contract, capture the environment-variable/materialized-path result of a bindeps-style build, classify host/target mismatches, and emit a fallback plan for users who cannot rely on nightly Cargo.

# De-risk plan

1. Start with one `build.rs`-consumed binary artifact case.
2. Add renamed multi-target dependencies only after the single-target contract format feels stable.
3. Keep stable fallback explicit and modest.
4. Avoid designing new Cargo syntax; work above documented/RFC substrate.

# Non-goals

- Not a replacement for Cargo’s artifact-dependency implementation.
- Not a general package manager or binary distributor.
- Not a guarantee that unstable Cargo behavior will never change.
- Not another generic final-artifact exporter.

# Architecture & API sketch

```rust
pub enum ArtifactAdoptionClass {
    SingleTargetOk,
    MultiTargetRenamed,
    MissingEnvBinding,
    StableFallbackRequired,
    TargetContractMismatch,
    ArtifactKindMismatch,
    ManualReviewRequired,
}

pub fn capture_artifact_env_receipt(root: &Path, contract: &ArtifactContract) -> Result<ArtifactEnvReceipt>;
pub fn build_artifact_target_matrix(contract: &ArtifactContract) -> ArtifactTargetMatrix;
pub fn classify_artifact_adoption(contract: &ArtifactContract, receipt: &ArtifactEnvReceipt) -> ArtifactAdoptionReport;
pub fn suggest_stable_fallback_plan(report: &ArtifactAdoptionReport) -> StableFallbackPlan;
```

Bundle draft: `artifact-contract.toml`, `artifact-target-matrix.json`, `artifact-env.receipt.json`, `artifact-adoption.report.json`, `stable-fallback.plan.json`, `artifact-adoption.diff.json`, `notes.md`.

# Security / safety model

- Treat artifact paths and target metadata as potentially sensitive and support redaction.
- Do not claim that observing an env var proves the downstream integration is correct.
- Make nightly/stable status explicit in all receipts.
- Prefer portable artifacts over live mutation of build systems in the MVP.

# Maintenance & governance plan

- Track Cargo unstable docs around artifact dependencies.
- Track RFC 3028 and RFC 3176 implementation drift as it lands.
- Keep the contract vocabulary small and concrete.
- Maintain fixtures for single-target, multi-target, and stable-fallback cases.

# Milestones

## 0.1
- artifact contract format
- env receipt capture
- target-matrix export
- adoption classification

## 0.2
- diff support
- renamed multi-target fixtures
- stable planning mode

## 0.3
- richer build-script guidance
- contract redaction controls
- support-bundle docs for downstream integrators

# Open questions

- What is the smallest stable vocabulary that captures host/target/multi-target artifact contracts without overfitting current unstable syntax?
- How much of the environment-variable naming scheme should the crate treat as normative versus observed?
- Should stable fallback planning support prebuilt artifacts only, or also wrapper-based generation patterns?

# Sources

- Cargo unstable docs (`artifact dependencies`): https://doc.rust-lang.org/cargo/reference/unstable.html#artifact-dependencies
- Cargo changelog (`-Z bindeps`): https://doc.rust-lang.org/cargo/CHANGELOG.html
- RFC 3028 (`cargo binary dependencies`): https://rust-lang.github.io/rfcs/3028-cargo-binary-dependencies.html
- RFC 3176 (`cargo multi dep artifacts`): https://rust-lang.github.io/rfcs/3176-cargo-multi-dep-artifacts.html
- This Development-cycle in Cargo: 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
