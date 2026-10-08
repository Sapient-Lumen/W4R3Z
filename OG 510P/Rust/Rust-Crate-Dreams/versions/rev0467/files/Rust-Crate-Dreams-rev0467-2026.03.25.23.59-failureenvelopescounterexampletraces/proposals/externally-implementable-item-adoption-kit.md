---
id: P-0452
title: Externally Implementable Item Adoption Kit — customization-point registries, semver-aware migration receipts, and override bundles for Rust’s emerging EII substrate
status: idea
domains: [language, compiler, api, no-std, customization, migration, documentation]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
  - https://doc.rust-lang.org/reference/runtime.html
  - https://doc.rust-lang.org/reference/attributes.html
  - https://docs.rs/log/latest/log/fn.set_logger.html
---

# Problem

Rust is actively working on externally implementable items (EII) so that things like `#[panic_handler]`, global allocator hooks, and similar customization points become less magical and more like ordinary language/library surface.

That creates a valuable new direction for the ecosystem — but it also opens a migration and packaging seam:

- crate authors need a way to describe which customization points exist, what defaults they provide, and how override resolution works,
- maintainers will want semver-aware migration paths from linker hacks, globals, or bespoke runtime registration,
- downstream users will need clearer diagnostics and docs than “you can only call this once” or “some symbol overrides this somewhere”,
- and today’s substrate still lacks a reusable artifact for **customization-point contracts**.

The missing crate is not the EII language feature itself.

The missing crate is an **adoption kit** that helps ordinary crates expose and migrate customization points once EII-style substrate exists.

# What it provides

- `customization-points.toml` — declarative registry of externally implementable items, defaults, exclusivity rules, and override semantics.
- `override.receipt.json` — records which implementation won, why, and under what profile or target assumptions.
- `migration-plan.md` — semver-aware guidance for moving from globals / runtime setters / linker symbols to EII-style customization points.
- `diagnostics.map.json` — human-readable explanations for common override conflicts and missing implementations.
- `cargo eii-adopt doctor` — scans a crate for likely customization-point candidates and risky legacy patterns.
- `cargo eii-adopt scaffold` — creates registry and documentation templates for a candidate customization point.
- `cargo eii-adopt receipt` — emits a shareable artifact describing a chosen override layout.
- `*.eiibundle.zip` — shareable bundle for API review, no-std integration review, or migration planning.

# What the crate should provide other people

1. **A boring way to document override points** in crates that expose global-ish customization.
2. **A migration helper** for crates moving away from ad hoc linker or runtime patterns.
3. **A shared receipt format** for “which implementation was active, and why?”
4. **A diagnostic bridge** between language evolution and maintainer-facing ergonomics.
5. **A semver-aware planner** for evolving customization points without surprising downstreams.

# Persona / who it’s for

- maintainers of `no_std`, embedded, runtime, and systems crates
- libraries that expose singleton or global customization hooks
- release engineers managing breaking-change risk
- documentation authors explaining override behavior

# Users & user stories

- **Runtime crate maintainer**: “Declare a default handler and an override path without leaving the semantics implicit.”
- **Embedded maintainer**: “Generate a migration plan from today’s linker-symbol pattern to a future EII-like item.”
- **Downstream integrator**: “See which override won and why this build rejected multiple candidates.”
- **API reviewer**: “Check whether changing the signature or kind of a customization point has a backward-compatible path.”

# Prior art (and why it’s insufficient)

- The EII project goal explains the language direction and explicitly connects it to `#[panic_handler]`, global allocators, and ecosystem uses like `log`.
- The Rust Reference documents today’s runtime attributes.
- Existing crates such as `log` demonstrate the demand for overridable global behavior.

What remains missing is a **crate-facing adoption artifact layer** for documenting, migrating, and auditing these customization points.

# Design goals

1. **Customization-first** — model override points explicitly as public API surface.
2. **Semver-aware** — treat signature/kind changes as migration events, not hidden implementation detail.
3. **Diagnostics-friendly** — prefer clear receipts over linker mysteries.
4. **Zero-magic posture** — keep defaults, exclusivity, and override policy explicit.
5. **Language-agnostic enough** — useful before full stabilization by operating as planning and documentation substrate.

# MVP surface

- Minimal types: `CustomizationPoint`, `OverridePolicy`, `OverrideReceipt`, `MigrationPlan`, `DiagnosticHint`
- Minimal functions:
  - `scan_candidates()`
  - `build_registry()`
  - `render_migration_plan()`
  - `explain_override_conflicts()`
  - `write_receipt()`
- Feature flags:
  - `cargo`
  - `serde`
  - `markdown`
  - `doctor`

# Compatibility story

- Useful in “planning and documentation only” mode before EII is fully stable.
- Can model current attribute- and setter-based patterns as legacy sources.
- Should not require a particular final EII syntax to provide value.
- Must keep speculative future behavior clearly marked as assumption, not guarantee.

# Conformance & fixtures

- Panic-handler-like, allocator-like, and logger-like fixture crates.
- Goldens for “single override”, “multiple overrides”, “default used”, and “legacy runtime setter” cases.
- Example semver migrations: signature expansion, renamed hook, split hooks, deprecated legacy path.
- Diagnostic fixtures showing likely confusing failure modes.

# Path to boring stability

- Stabilize the registry and receipt schema before adding auto-rewrite features.
- Start with function-like customization points and a few legacy patterns.
- Keep generated diagnostics explanatory rather than overly clever.
- Separate “planning” from “actual compiler-backed enforcement”.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that let a crate author describe one customization point, emit a semver-aware migration plan and diagnostic hints, and export an override receipt bundle.

# De-risk plan

1. Start with explicit registry and docs generation, not enforcement.
2. Support a narrow set of legacy patterns first.
3. Keep migration plans manual-review-friendly.
4. Validate usefulness on one embedded/runtime crate and one logger-like crate.

# Non-goals

- Not the EII language feature implementation.
- Not a linker replacement.
- Not a full dependency-injection framework.
- Not a promise that the final stable EII surface will exactly match today’s experiments.

# Architecture & API sketch

```rust
pub struct CustomizationPoint {
    pub name: String,
    pub kind: ItemKind,
    pub default: Option<String>,
    pub exclusivity: OverridePolicy,
}

pub fn scan_candidates(root: &Path) -> Result<Vec<CustomizationPoint>>;
pub fn build_registry(points: &[CustomizationPoint]) -> Registry;
pub fn render_migration_plan(registry: &Registry) -> String;
pub fn write_receipt(registry: &Registry, out: &Path) -> Result<OverrideReceipt>;
```

Bundle draft: `customization-points.toml`, `override.receipt.json`, `migration-plan.md`, `diagnostics.map.json`, `notes.md`.

# Security / safety model

- No hidden build-system mutation in the MVP.
- Keep override assumptions explicit and exportable.
- Support redaction of private paths and symbols in shared bundles.
- Treat ambiguity as a reportable state, not silent resolution.

# Maintenance & governance plan

- Track EII experiment changes closely.
- Maintain templates for common patterns: handlers, allocators, loggers, singleton providers.
- Keep the schema small enough for manual review.
- Document where compiler/runtime behavior is assumed versus observed.

# Milestones

## 0.1
- registry schema
- migration-plan renderer
- one legacy-pattern scanner

## 0.2
- diagnostic hints
- receipt export
- more fixture families

## 1.0
- stable registry/receipt schema
- richer migration templates
- CI/review adapters

# Open questions

- What is the smallest useful abstraction for an externally implementable item from a crate author’s perspective?
- Which legacy override patterns are most worth modeling first?
- How should semver guidance represent a customization point changing kind, signature, or exclusivity?

# Sources

- Externally Implementable Items goal: https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- Rust Reference runtime attributes: https://doc.rust-lang.org/reference/runtime.html
- Rust Reference attributes: https://doc.rust-lang.org/reference/attributes.html
- `log::set_logger`: https://docs.rs/log/latest/log/fn.set_logger.html
