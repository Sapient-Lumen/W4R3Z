---
id: P-0437
title: Codegen Backend Matrix Workbench Kit — comparable receipts, diff bundles, and fallback policies across LLVM, Cranelift, and GCC backends
status: idea
domains: [compiler, devtools, performance, ci, portability]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
  - https://github.com/rust-lang/rustc_codegen_cranelift
  - https://github.com/rust-lang/rustc_codegen_gcc
  - https://rust-lang.github.io/rust-project-goals/
---

# Problem

Rust is no longer a one-backend world in practice.

LLVM remains the default, Cranelift is now explicitly being pushed toward production-ready local development use, and the GCC backend remains strategically valuable for broader architecture coverage and alternative optimization/back-end behavior.

But the typical developer experience for experimenting with multiple backends is still rough:

- backend selection is scattered across config and environment choices,
- results are hard to compare cleanly,
- compile-time and runtime differences are easy to mis-measure,
- missing-feature failures are hard to summarize or minimize,
- and teams lack a boring artifact for saying “this workspace works on backend X, fails on Y for reason Z, and falls back under policy P.”

The missing crate is not another backend.

The missing crate is a **backend comparison and policy workbench** that helps developers, CI owners, and compiler-adjacent projects use the growing backend diversity intentionally.

# What it provides

- `backend-matrix.toml` — declares backends, profiles, targets, fallback rules, measurements, and expected caveats.
- `backend.receipt.json` — exact backend/toolchain/config/profile/target information for one run.
- `backend.diff.json` — structured comparison of compile success, compile time, artifact size, caveats, and test outcomes.
- `backend.caveats.json` — known unsupported features or maturity notes by backend/target/profile.
- `backend.bundle.zip` — receipts, measurements, minimized repro commands, and logs for one backend matrix run.
- `cargo backend-matrix run` — executes the matrix across LLVM/Cranelift/GCC where configured.
- `cargo backend-matrix explain` — shows why a project fell back to another backend or why a backend is excluded.

# What the crate should provide other people

1. **A repeatable way to compare backends** without hand-built shell matrices.
2. **A fallback policy artifact** for teams that want faster local builds but safe CI defaults.
3. **A compact repro bundle** for backend bugs or unsupported-feature reports.
4. **A shared vocabulary** for backend capability and maturity claims.
5. **A bridge** from experimental backend support to ordinary project adoption.

# Persona / who it’s for

- maintainers of large Rust workspaces
- CI/build engineers
- compiler-adjacent developers and toolsmiths
- projects targeting unusual architectures or faster local edit-build-test loops

# Users & user stories

- **Developer**: “Use Cranelift for local dev where possible, but know exactly when and why we fall back.”
- **CI owner**: “Track compile-time deltas and unsupported-feature regressions across backends.”
- **Backend contributor**: “Get one artifact that captures config, failure mode, and repro command.”
- **Portability-focused project**: “Record which backends and targets are viable for this workspace.”

# Prior art (and why it’s insufficient)

- The Cranelift backend now has explicit project-goal support and documented ways to enable it.
- The GCC backend already exists and is valuable for architecture reach and alternative optimization behavior.
- Projects can already hand-roll benchmark matrices in CI, but those are usually bespoke, hard to compare, and poor at packaging caveats or repros.

What remains missing is a **matrix/receipt/fallback layer** above the backends themselves.

# Design goals

1. **Policy over hype** — describe what a workspace can actually do with each backend, not what fans hope it can do someday.
2. **Compare like with like** — make config, profile, and target context first-class.
3. **Fallback-friendly** — encode “prefer X, allow Y” policies cleanly.
4. **Bug-report ready** — every failed backend run should be easy to hand off.
5. **Backend-neutral** — treat LLVM, Cranelift, and GCC as matrix entries, not as special cases glued into bespoke scripts.

# MVP surface

- Minimal types: `BackendMatrix`, `BackendReceipt`, `BackendDiff`, `FallbackPolicy`, `BackendCaveat`
- Minimal functions:
  - `run_backend()`
  - `compare_receipts()`
  - `explain_fallback()`
  - `write_bundle()`
  - `record_measurements()`
  - `minimize_repro()`
- Feature flags:
  - `cranelift`
  - `gcc`
  - `timings`
  - `size`
  - `serde`

# Compatibility story

- Works above official backend selection mechanisms and backend-specific wrappers.
- Can model per-profile backend choices such as Cranelift for `dev` and LLVM for `release`.
- Should tolerate partial backend availability by producing caveated receipts.
- Must not promise correctness equivalence where the toolchain does not.

# Conformance & fixtures

- Tiny fixtures for unsupported intrinsics, unwinding, ABI-sensitive FFI, size/perf-sensitive binaries, and plain happy-path crates.
- Goldens for “backend supported”, “backend caveated”, “backend fallback”, and “backend hard-fail with repro” cases.
- Measurement fixtures using stable, low-variance commands.
- Replay bundles for filing backend bugs upstream.

# Path to boring stability

- Stabilize receipt and diff schemas before expanding measurement sophistication.
- Keep early performance claims comparative and contextual.
- Treat unsupported-feature findings as first-class outcomes.
- Add richer minimization or benchmarking only after users trust the basic matrix artifacts.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A crate and cargo subcommand that run a workspace against a configured backend matrix, emit receipts and diffs, and explain fallback or failure in one portable bundle.

# De-risk plan

1. Start with local-development profiles and compile/test success, not fancy benchmarking claims.
2. Treat measurements as advisory unless the environment is controlled.
3. Keep backend caveats explicit and versioned.
4. Use repro bundles to ensure failures are still productive outcomes.

# Non-goals

- Not a new codegen backend.
- Not a compiler benchmarking suite for all purposes.
- Not a guarantee of backend equivalence.
- Not a replacement for upstream backend issue trackers.

# Architecture & API sketch

```rust
pub struct BackendReceipt {
    pub backend: BackendKind,
    pub toolchain: ToolchainInfo,
    pub profile: String,
    pub target: String,
    pub outcome: BackendOutcome,
    pub caveats: Vec<BackendCaveat>,
}

pub fn run_backend(matrix: &BackendMatrix, entry: &BackendEntry) -> Result<BackendReceipt>;
pub fn compare_receipts(old: &BackendReceipt, new: &BackendReceipt) -> Result<BackendDiff>;
pub fn explain_fallback(policy: &FallbackPolicy, receipts: &[BackendReceipt]) -> Result<String>;
```

Bundle draft: `backend-matrix.toml`, `backend.receipts/`, `backend.diff.json`, `backend.caveats.json`, `repro/`, `notes.md`.

# Security / safety model

- Preserve exact backend and toolchain provenance.
- Distinguish measurement from capability from correctness.
- Permit path redaction and environment redaction in exported bundles.
- Never collapse caveated or unsupported backend runs into “pass.”

# Maintenance & governance plan

- Track upstream backend maturity and configuration changes.
- Keep the backend capability vocabulary small and explicit.
- Focus on artifacts that help users file better upstream reports.
- Avoid embedding too much backend-specific policy in the crate core.

# Milestones

## 0.1
- one-run receipt format
- matrix runner for LLVM and Cranelift
- fallback explanations

## 0.2
- GCC support
- diff bundles
- repro export

## 1.0
- stable receipt schema
- richer capability taxonomy
- CI-friendly matrix reports

# Open questions

- What is the smallest useful measurement set that avoids false confidence?
- Should fallback policy be per-profile only, or also per-package/target in the MVP?
- How much backend-specific caveat knowledge belongs in core versus external packs?

# Sources

- Cranelift backend goal: https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- `rustc_codegen_cranelift`: https://github.com/rust-lang/rustc_codegen_cranelift
- `rustc_codegen_gcc`: https://github.com/rust-lang/rustc_codegen_gcc
- Rust project goals overview: https://rust-lang.github.io/rust-project-goals/
