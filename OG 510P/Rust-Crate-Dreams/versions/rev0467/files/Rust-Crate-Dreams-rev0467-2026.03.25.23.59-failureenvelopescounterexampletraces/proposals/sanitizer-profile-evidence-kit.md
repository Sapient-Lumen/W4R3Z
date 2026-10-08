---
id: P-0434
title: Sanitizer Profile & Evidence Kit — version-pinned profiles, suppressions, symbolized receipts, and CI bundles for Rust sanitizer workflows
status: idea
domains: [security, testing, safety, ci, cargo, tooling]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/
  - https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

---

# Problem

Rust is finally getting closer to a real sanitizer story, but the workflow is still much too folkloric for ordinary teams.

Today, teams that want to use sanitizers in anger often have to manually coordinate:

- which sanitizer profile to run on which target,
- whether an instrumented standard library is required,
- how `--target` should be used so build scripts and proc macros are not accidentally instrumented,
- which suppressions or known caveats apply,
- how to symbolize and archive reports,
- and how to explain what exactly was or was not covered in CI.

The Rust project is explicitly working on stabilizing MemorySanitizer and ThreadSanitizer support and on shipping instrumented standard libraries through rustup. The unstable-book docs are also already opinionated about practical footguns such as instrumented std, `--target`, and symbolization.

That means the sharper ecosystem gap is no longer “invent Rust sanitizers.”

The missing crate is a **sanitizer workflow-and-evidence kit** that turns the substrate into a boring, reviewable default.

# What it provides

- `sanitizer-profile.toml` — declares sanitizer kind, target, whether instrumented std is required or expected, symbolizer settings, environment variables, and CI policy.
- `sanitizer.receipt.json` — exact rustc/Cargo/rustup/toolchain/profile/suppressions/symbolizer context for a run.
- `sanitizer.caveats.json` — known caveats by sanitizer/target/toolchain/profile.
- `instrumentation-scope.receipt.json` — what code, dependencies, `std`, build scripts, and proc macros were actually on the sanitizer lane.
- `runtime-linkage.receipt.json` — whether Rust’s default compiler runtime was used or whether mixed-language routing needed an explicit external lane.
- `symbolization-route.receipt.json` — whether reports were fully symbolized, partially symbolized, or raw-PC only.
- `suppression-policy.receipt.json` — active suppressions, reasons, owners, and review dates.
- `sanitizer.suppressions/` — portable suppression files and redaction-aware stack filters.
- `sanitizer.reportbundle.zip` — symbolized reports, receipts, caveats, raw logs, and reproduction commands.
- `cargo sanitize profile <name>` — runs the chosen sanitizer workflow with the right environment and target splitting.
- `cargo sanitize diff` — compares receipts and caveats across toolchain upgrades or platform changes.

# What the crate should provide other people

1. **A sane default workflow** for ASan/LSan/MSan/TSan/CFI-class runs without every team re-learning the docs.
2. **Instrumentation-scope truth** so another engineer can tell what was actually covered and what was not.
3. **Runtime-linkage truth** for mixed-language or external-runtime routes instead of linker folklore.
4. **Suppression and caveat hygiene** that is explicit, reviewable, and portable.
5. **Symbolized report bundles** that can be handed from CI to developers or security engineers.
6. **A bridge** between Cargo/rustup/build-std realities and the day-to-day work of ordinary maintainers.

# Persona / who it’s for

- maintainers of systems crates and applications
- security-conscious CI owners
- teams doing FFI-heavy or mixed-language integration
- safety/security review groups that need more than raw stderr

# Users & user stories

- **Maintainer**: “Run our workspace’s ASan and TSan jobs without remembering a pile of shell incantations.”
- **CI engineer**: “Archive one bundle that records target, toolchain, suppressions, and symbolizer context.”
- **Security engineer**: “Compare sanitizer evidence before and after a toolchain upgrade.”
- **FFI-heavy project owner**: “Record whether a run used instrumented std, external runtimes, and C/C++ coverage or not.”

# Prior art (and why it’s insufficient)

- Rust documents sanitizer flags and many of the sharp practical constraints, but documentation is not a reusable artifact.
- `cargo-llvm-cov` demonstrates how valuable a focused Cargo workflow wrapper can be, but it is aimed at coverage collection rather than sanitizer receipts and suppressions.
- Ad hoc shell scripts and CI YAML often exist per project, but they are fragile, unshareable, and poor at preserving caveat context.

What remains missing is a **profile + receipt + suppression + report-bundle layer** for sanitizer use in Rust.

# Design goals

1. **Workflow-first** — make the common sanitizer runs reproducible without a custom shell maze.
2. **Scope-first** — record exactly what was and was not instrumented.
3. **Caveat-first** — record partial instrumentation, platform quirks, and unsupported combinations explicitly.
4. **Runtime-linkage honesty** — keep mixed-language and external-runtime routing visible.
5. **Target-aware** — respect the distinction between host tools, proc macros, build scripts, and instrumented targets.
6. **Bundle-oriented** — a sanitizer result should be easy to hand to another person.
7. **Upstream-aligned** — sit above rustc/Cargo/rustup rather than competing with them.

# MVP surface

- Minimal types: `SanitizerProfile`, `SanitizerReceipt`, `InstrumentationScopeReceipt`, `RuntimeLinkageReceipt`, `SymbolizationRouteReceipt`, `SuppressionPolicyReceipt`, `SuppressionSet`, `SanitizerCaveat`, `ReportBundle`
- Minimal functions:
  - `load_profile()`
  - `prepare_env()`
  - `run_profile()`
  - `capture_instrumentation_scope()`
  - `capture_runtime_linkage()`
  - `capture_symbolization_route()`
  - `capture_suppression_policy()`
  - `symbolize_reports()`
  - `write_receipt()`
  - `bundle_reports()`
- Feature flags:
  - `serde`
  - `rustup`
  - `build-std`
  - `ffi`
  - `nextest`

# Compatibility story

- Works with existing sanitizer support from rustc and Cargo.
- Records whether the run relied on instrumented std, prebuilt sanitizer libraries, or partially instrumented code.
- Keeps host-build-helper exclusion and mixed-language runtime-linkage visible instead of flattening them into one success bit.
- Should degrade honestly: unsupported combinations become caveated receipts, not silent success.
- Can integrate with workspace-specific wrappers or CI orchestrators.

# Conformance & fixtures

- Tiny fixtures for heap UAF, double free, data race, uninitialized read, CFI mismatch, and mixed Rust/C interop cases.
- Goldens for `instrumentation_scope_strong`, `instrumentation_scope_partial`, `external_clangrt_route`, `symbolized`, `unsymbolized`, and `owned_suppression_debt` outcomes.
- Matrix fixtures for Linux/macOS/Windows where practical.
- Suppression corpus with reason annotations and expected stack redaction behavior.

# Path to boring stability

- Stabilize `sanitizer-profile.toml` and `sanitizer.receipt.json` first.
- Keep the first version focused on profiles, receipts, and report bundling rather than ambitious orchestration.
- Make unsupported combinations explicit and normal in the artifact model.
- Expand only after real teams trust the receipts.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A crate and cargo subcommand that run one sanitizer profile reproducibly, emit version-pinned core receipts plus instrumentation/runtime/symbolization/suppression receipts, and bundle reports plus caveats for CI handoff.

# De-risk plan

1. Start with ASan/LSan and one or two Tier 1 targets.
2. Treat MSan/TSan and FFI-heavy runs as caveat-rich profiles instead of pretending they are turnkey.
3. Keep suppressions and caveats explicit and versioned.
4. Add richer matrix support only after receipt fidelity proves valuable.

# Non-goals

- Not a replacement for rustc sanitizer support.
- Not a guarantee that every sanitizer works on every target.
- Not a general-purpose security certification framework.
- Not a coverage tool.

# Architecture & API sketch

```rust
pub struct SanitizerReceipt {
    pub toolchain: ToolchainInfo,
    pub profile: SanitizerProfile,
    pub caveats: Vec<SanitizerCaveat>,
    pub reports: Vec<ReportRef>,
}

pub fn run_profile(profile: &SanitizerProfile, cx: &RunContext) -> Result<SanitizerReceipt>;
pub fn symbolize_reports(receipt: &mut SanitizerReceipt, sym: &SymbolizerConfig) -> Result<()>;
pub fn bundle_reports(receipt: &SanitizerReceipt, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `sanitizer-profile.toml`, `sanitizer.receipt.json`, `sanitizer.caveats.json`, `instrumentation-scope.receipt.json`, `runtime-linkage.receipt.json`, `symbolization-route.receipt.json`, `suppression-policy.receipt.json`, `reports/`, `suppressions/`, `repro.sh`, `notes.md`.

# Security / safety model

- Preserve exact toolchain and target provenance.
- Distinguish unsupported, partially instrumented, suppressed, unsymbolized, and clean outcomes.
- Permit path redaction and source-path remapping in exported bundles.
- Never turn suppressions into invisible success.

# Maintenance & governance plan

- Keep a small versioned caveat index tied to public rustc/project-goal progress.
- Maintain adapters to rustup/build-std/symbolizer discovery and mixed-language runtime routing as thin layers.
- Publish clear guidance on when receipts are strong enough for CI gating versus advisory only.
- Add new sanitizer kinds only when fixture coverage exists.

# Milestones

## 0.1
- profile format
- receipt writer
- instrumentation/runtime/symbolization/suppression receipts
- report bundling for ASan/LSan

## 0.2
- suppressions and symbolizer support
- profile diffing
- richer CI export

## 1.0
- stable receipt schema
- caveat taxonomy
- cross-target profile packs

# Open questions

- How should the crate model “instrumented std recommended” versus “required” for different sanitizers?
- What is the smallest useful suppression schema that still remains portable?
- Should the bundle format include optional minimized repro fixtures, or is that a later layer?

# Sources

- Rust sanitizer stabilization goal: https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- Rust sanitizer docs: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- Build-std project goal: https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- `cargo-llvm-cov`: https://github.com/taiki-e/cargo-llvm-cov


Treat `meta/sanitizer-profile-evidence-product-plan-2026-03-22.md` as the working build sketch for **P-0434**.
The key new planning detail is that a worthy sanitizer workflow crate should elevate **instrumentation scope**, **runtime linkage**, **symbolization route**, and **suppression policy** into first-class artifacts rather than flattening everything into one generic sanitizer receipt.
