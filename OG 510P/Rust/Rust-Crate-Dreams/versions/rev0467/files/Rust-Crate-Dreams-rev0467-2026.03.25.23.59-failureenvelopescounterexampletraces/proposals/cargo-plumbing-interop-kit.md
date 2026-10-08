---
id: P-0432
title: Cargo Plumbing Interop Kit — blocker-aware phase snapshots, edited-input receipts, and adapters above Cargo’s emerging plumbing commands
status: idea
domains: [cargo, devtools, build, tooling, interoperability]
last_reviewed: 2026-03-16
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
  - https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  - https://docs.rs/cargo_metadata
  - https://docs.rs/cargo-manifest
---

# Problem

Cargo plumbing has moved from vague wish to concrete prototype work.

The official project-goal page split a build into distinct stages like:

1. locate project,
2. read manifests,
3. read lockfile,
4. lock dependencies,
5. write lockfile,
6. resolve features,
7. plan build,
8. execute build,
9. stage final artifacts.

That is already a strong design signal: Cargo’s missing value is not one giant “tooling API”, but a set of phase-shaped surfaces.

By late 2025, the direction was even more concrete:

- `cargo locate-manifest` and `cargo read-manifest` had been merged,
- the GSoC plumbing prototype had implemented seven subcommands,
- and the maintainers were explicit that real blockers remained around how Cargo’s current Rust APIs expose state.

That combination reveals a sharper ecosystem gap.

Tool authors still do not have a boring way to hand another person artifacts answering:

- which phase outputs were *actually* captured,
- whether a command consumed the caller’s intended inputs or re-read files from disk,
- which parts came from official command output versus reconstruction or fallback,
- how a feature-resolution or build-plan result changed across Cargo versions,
- and whether a tool is depending on a current Cargo API compromise rather than a durable phase contract.

The missing crate is **not** a reimplementation of Cargo.
The missing crate is **not** just another wrapper over `cargo metadata`.
The missing crate is a **Cargo Plumbing Interop Kit**: a blocker-aware adapter layer that captures phase outputs, records where Cargo had to re-read or ignore caller-provided inputs, and gives downstream tools one stable-on-top receipt vocabulary.

# Main judgment after the 2026-03-16 refresh

This proposal got stronger once the prototype work exposed concrete compromises.

The key signal is not merely that plumbing commands exist.
It is that the prototype documented where the current Cargo API shape blocks the ideal design — for example, commands re-reading manifests instead of consuming only the caller-provided representation.

That means the worthy crate is not just “serialize more Cargo internals”.
It is the **edited-input receipt / blocker-aware adapter / phase snapshot** layer above evolving Cargo commands.

# What it provides

- `cargo-phase.lock` — pins Cargo version, command set, schema versions, and accepted phase vocabulary.
- `phase-input.intent.json` — records what the caller intended to pass into a phase, including any edited or filtered manifest/lockfile representation.
- `manifest.snapshot.json` — normalized workspace-manifest view.
- `lockfile.snapshot.json` — normalized lockfile view and provenance.
- `feature-resolution.snapshot.json` — normalized resolved-feature graph and relevant caveats.
- `build-plan.snapshot.json` — normalized plan/build-unit surface for downstream tools.
- `plumbing.receipt.json` — records command invocations, source-of-truth lanes, reread-versus-consumed behavior, fallbacks, unsupported fields, and blocker notes.
- `plumbing.diff.json` — compares two phase bundles and classifies `phase_changed`, `cargo_version_changed`, `edited_input_ignored`, `fallback_used`, `schema_mismatch`, and `manual_review_required`.
- `cargo plumbing capture` — capture one phase bundle.
- `cargo plumbing compare <old> <new>` — compare bundles across Cargo versions or workflow assumptions.
- `cargo plumbing doctor-inputs` — explain where the current command path re-read files or otherwise diverged from the caller’s intended inputs.
- `*.plumbingbundle.zip` — portable artifact for tool authors, CI, and upstream bug reports.

# What the crate should provide other people

1. **A stable-on-top phase receipt** while Cargo plumbing commands continue to evolve.
2. **A blocker-aware interop layer** that says where Cargo honored or ignored edited inputs.
3. **A shared schema vocabulary** for manifests, lockfiles, feature resolution, and build planning.
4. **A diffable phase bundle** for debugging tool breakage across Cargo versions.
5. **A compact handoff artifact** for upstream discussions about what plumbing still cannot express cleanly.

# Persona / who it’s for

- Cargo-adjacent tool authors
- IDE / editor integration maintainers
- CI and policy-tool builders
- workspace and build-analysis crate maintainers
- upstream contributors testing future Cargo plumbing design

# Users & user stories

- **Tool author**: “Tell me whether my custom manifest edits were actually consumed or whether Cargo re-read from disk.”
- **IDE maintainer**: “Diff feature resolution and build planning across Cargo versions without reverse-engineering raw outputs again.”
- **CI engineer**: “Freeze one plumbing bundle for a failing workflow and attach it to an issue.”
- **Upstream contributor**: “Show me exactly which phase boundary or API blocker forced a fallback in this prototype.”

# Prior art (and why it’s insufficient)

- `cargo_metadata` is useful but intentionally does not model the full phase taxonomy that Cargo plumbing is moving toward.
- `cargo-manifest` helps parse manifests, but it does not provide a phase bundle or blocker-aware receipt surface.
- The official Cargo plumbing goal defines a phased direction, but not the shared downstream artifact layer.
- The GSoC plumbing prototype proved out commands and also proved out blocker classes.
- The archive now also has **P-0507 Cargo Fix Campaign Kit**, but that crate sits **above** Cargo execution and edit orchestration; it should consume plumbing receipts, not replace them.

What remains missing is a **shared interop layer** that can preserve the phase outputs, caveats, and blocker evidence in a form other tools can actually rely on.

# Design goals

1. **Phase-shaped** — manifests, lockfiles, feature resolution, and build planning should stay visibly distinct.
2. **Blocker-aware** — where Cargo APIs force compromises must be first-class data.
3. **Intent-versus-observation explicit** — record what the caller wanted to feed in and what Cargo actually consumed.
4. **Fallback-explicit** — if the crate reconstructs or approximates a phase, that must be obvious.
5. **Cargo-adjacent** — wrap official commands and libraries rather than shadowing Cargo internals.
6. **Useful to many tools** — editors, fix orchestrators, policy tools, and build analyzers should all benefit.

# MVP surface

- Minimal types: `CargoPhaseLock`, `PhaseInputIntent`, `ManifestSnapshot`, `LockfileSnapshot`, `FeatureResolutionSnapshot`, `BuildPlanSnapshot`, `PlumbingReceipt`, `PlumbingDiff`
- Minimal functions:
  - `capture_manifest_phase()`
  - `capture_lockfile_phase()`
  - `capture_feature_resolution_phase()`
  - `capture_build_plan_phase()`
  - `record_phase_input_intent()`
  - `diff_phase_outputs()`
- Feature flags:
  - `cargo-metadata`
  - `cargo-manifest`
  - `serde`
  - `diff`
  - `markdown`

# Compatibility story

- Works above today’s Cargo commands and prototype plumbing surfaces rather than requiring Cargo internals.
- Can record when a phase came from a reconstructed or reread path instead of an ideal direct phase input.
- Keeps its own lock and receipt schema stable even when Cargo output details evolve.
- Should later adopt official plumbing subcommands more directly when those interfaces stabilize.

# Conformance & fixtures

- One fixture where edited manifest intent is not preserved because the command path re-reads from disk.
- One fixture covering `locate-manifest` + `read-manifest` + `read-lockfile` coherence.
- One fixture for feature-resolution drift across Cargo versions.
- One fixture for `plan-build` capture with explicit fallback notes.
- Goldens for `edited_input_ignored`, `phase_changed`, `schema_mismatch`, and `manual_review_required`.

# Path to boring stability

- Stabilize `cargo-phase.lock`, `phase-input.intent.json`, and `plumbing.receipt.json` before widening the phase taxonomy.
- Keep the first normalized snapshots intentionally small.
- Prefer explicit blocker notes over fake completeness.
- Treat intent-versus-observation mismatches as core value, not an edge case.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A crate that captures manifest, lockfile, feature-resolution, and build-plan-adjacent outputs into normalized snapshots, records whether the caller’s intended inputs were actually consumed, and emits one blocker-aware receipt bundle.

# De-risk plan

1. Start with read-only capture and diffing.
2. Keep phase schemas minimal and avoid over-normalization.
3. Exercise the crate against current Cargo plumbing prototypes and stable Cargo fallbacks.
4. Adopt official phase commands opportunistically rather than blocking on them.

# Non-goals

- Not a reimplementation of Cargo.
- Not a promise of permanent forward compatibility with every Cargo output.
- Not a build executor.
- Not a universal project-model standard for every language ecosystem.

# Architecture & API sketch

```rust
pub struct PhaseInputIntent {
    pub phase: String,
    pub edited_inputs_present: bool,
    pub expected_consumption_mode: String,
}

pub fn capture_manifest_phase(cx: &CaptureContext) -> Result<ManifestSnapshot>;
pub fn capture_lockfile_phase(cx: &CaptureContext) -> Result<LockfileSnapshot>;
pub fn capture_feature_resolution_phase(cx: &CaptureContext) -> Result<FeatureResolutionSnapshot>;
pub fn capture_build_plan_phase(cx: &CaptureContext) -> Result<BuildPlanSnapshot>;
pub fn diff_phase_outputs(a: &PhaseBundle, b: &PhaseBundle) -> PhaseDiff;
```

Bundle draft: `cargo-phase.lock`, `phase-input.intent.json`, `manifest.snapshot.json`, `lockfile.snapshot.json`, `feature-resolution.snapshot.json`, `build-plan.snapshot.json`, `plumbing.receipt.json`, `plumbing.diff.json`, `notes.md`.

# Security / safety model

- Preserve exact Cargo version and schema provenance so tool failures are diagnosable.
- Support redaction of private paths and workspace details in shared receipts.
- Keep reread-versus-consumed behavior explicit so tools do not silently overclaim edited-input support.
- Avoid silently dropping unknown fields when normalizing snapshots.

# Maintenance & governance plan

- Track Cargo plumbing evolution and supported phase sources in a compact matrix.
- Maintain fixtures that capture edited-input, workspace, and feature-resolution edge cases.
- Keep adapters thin and aggressively versioned.
- Publish guidance for downstream tools on which fields are safe to treat as durable contracts.

# Milestones

## 0.1
- capture manifest and lockfile phases
- record phase input intent
- receipt writer
- schema/version pinning

## 0.2
- feature-resolution snapshot
- build-plan snapshot
- diffing across Cargo versions

## 1.0
- stable lock/receipt schema
- broader downstream-tool examples
- official phase-command adapters where available

# Open questions

- What is the smallest phase vocabulary that stays useful across many tool classes?
- Which fields should remain raw passthrough versus normalized core schema?
- How much edited-input support is worth modeling before the crate becomes too magical?

# Sources

- Cargo plumbing project goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- July 2025 goals update (`locate-manifest`, `read-manifest` merged): https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- GSoC 2025 results (`cargo-plumbing` prototype and blockers): https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo 1.90 development cycle update: https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- `cargo_metadata`: https://docs.rs/cargo_metadata
- `cargo-manifest`: https://docs.rs/cargo-manifest
