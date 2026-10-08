---
id: P-0464
title: Sized Hierarchy & Extern-Type Readiness Kit — sizedness-surface audits, opaque-type migration receipts, and trait-bound readiness bundles for the refined `Sized` hierarchy
status: idea
domains: [ffi, language, traits, types, compiler, migration, libraries]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://doc.rust-lang.org/beta/unstable-book/language-features/sized-hierarchy.html
  - https://github.com/rust-lang/rust/issues/144404
  - https://rust-lang.github.io/rfcs/1861-extern-types.html
  - https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
---

# Problem

Rust is now explicitly working toward stabilizing the refined `Sized` trait hierarchy, and the 2026 flagships page spells out one immediate consequence: this work is meant to **unblock extern types**. The tracking issue also makes clear that migration strategy matters, including how default supertraits and existing trait bounds interact with opaque or exotically sized types.

That creates a practical gap for ordinary library and FFI maintainers:

- many crates implicitly assume today’s `Sized` / `?Sized` world is the whole space,
- public traits, helper abstractions, and wrapper types may accidentally exclude future extern-type or refined-sizedness use cases,
- maintainers lack a compact way to inventory where `Sized` assumptions are semver-relevant,
- and current FFI tooling focuses on binding generation, not on **readiness for the refined sizedness model**.

The missing crate is not a new binding generator and not a language experiment.

The missing crate is a **readiness kit** that helps maintainers audit their sizedness assumptions, record opaque-type constraints, and produce a migration receipt before the hierarchy changes become ordinary stable Rust.

# What it provides

- `sized-surface.toml` — declares the crate’s intended sizedness posture, opaque-type goals, and audit scope.
- `sized-audit.json` — inventory of public traits, type parameters, helper APIs, and wrapper types that encode `Sized` / `?Sized` assumptions.
- `opaque-readiness.json` — findings like `extern_type_blocked`, `default_supertrait_risk`, `thin_pointer_assumption`, `requires_manual_review`, and `ready_for_opaque_handle`.
- `trait-bound.diff.json` — compares two releases or two audit passes for changes in sizedness-related API posture.
- `ffi-handle-map.json` — records where opaque FFI handles, wrapper structs, or pointers appear and what assumptions surround them.
- `migration.receipt.json` — exact toolchain, nightly features (if any), tracking issue/RFC references, and unresolved caveats.
- `cargo sized-ready scan` — inventory sizedness-sensitive surfaces.
- `cargo sized-ready rehearse` — dry-run a refined-sizedness/extern-type readiness audit.
- `cargo sized-ready diff` — compare two releases or crates.
- `*.sizedbundle.zip` — shareable bundle for maintainers, reviewers, or upstream issue reports.

# What the crate should provide other people

1. **A boring audit artifact** for sizedness assumptions.
2. **An opaque-type readiness receipt** above today’s binding generators.
3. **A semver-aware view** of where `Sized` posture leaks into public APIs.
4. **A bridge** between current FFI practice and the refined hierarchy.
5. **A migration planner** for traits and wrappers that accidentally overconstrain future use cases.

# Persona / who it’s for

- FFI and systems-library maintainers
- crate authors exposing pointer- or wrapper-heavy APIs
- teams preparing for extern-type support
- compiler/language contributors who need real-world casebooks of sizedness assumptions

# Users & user stories

- **FFI maintainer**: “Show me where our public wrappers assume today’s sizedness model and may block opaque extern handles.”
- **Library reviewer**: “Compare the sizedness surface between two releases and tell me if we tightened or relaxed bounds.”
- **Language contributor**: “Collect real-world examples where default supertraits or wrapper patterns make extern-type adoption awkward.”
- **Systems team**: “Keep an inventory of APIs that are already opaque-handle-friendly versus those that need redesign.”

# Prior art (and why it’s insufficient)

- The unstable book and tracking issue now define a concrete feature surface for the sized hierarchy work.
- RFC 1861 established extern types long ago, but their practical use has remained constrained.
- Existing FFI tools like bindgen/cxx/autocxx help generate bindings, not sizedness-readiness receipts.

What remains missing is a **maintainer-facing audit layer**: the thing that says “here are our sizedness assumptions, here is where opaque extern types are blocked, and here is how that posture changes over time.”

# Design goals

1. **Audit-first** — inventory assumptions before suggesting rewrites.
2. **Semver-aware** — treat public trait bounds and wrapper posture as release concerns.
3. **Opaque-type-friendly** — center extern handles and future exotic sizedness use cases.
4. **Conservative** — preserve unknown/manual-review categories.
5. **Useful before stabilization** — work with current feature status and tracking issues.

# MVP surface

- Minimal types: `SizedSurface`, `SizedAuditFinding`, `OpaqueReadiness`, `FfiHandleMap`, `SizedDiff`, `SizedBundle`
- Minimal functions:
  - `scan_sized_surface()`
  - `classify_opaque_readiness()`
  - `diff_bound_posture()`
  - `render_receipt()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `ffi`
  - `nightly-audit`
  - `rustdoc-json`

# Compatibility story

- Must be useful before stabilization by treating current hierarchy work as a readiness target, not a fixed stable guarantee.
- Should remain useful after stabilization because public APIs will still need audit and migration receipts.
- Must tolerate crates that are not FFI-facing but still encode restrictive sizedness assumptions.
- Should preserve “unknown” when the crate cannot confidently infer posture from syntax alone.

# Conformance & fixtures

- One thin-pointer / opaque-handle crate.
- One wrapper-heavy crate with public `Sized` assumptions.
- One intentionally extern-type-friendly fixture.
- Goldens for `extern_type_blocked`, `default_supertrait_risk`, `ready_for_opaque_handle`, and `manual_review_required`.
- A release-diff fixture showing a semver-relevant bound change.

# Path to boring stability

- Stabilize the audit vocabulary before any rewrite helpers.
- Start with inventory + classification + bundle export.
- Keep the sizedness taxonomy intentionally small.
- Add migration assists only after maintainers trust the receipts.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that inventory one crate’s sizedness-sensitive public surface, flag opaque-handle blockers conservatively, and emit a migration receipt plus compact review bundle.

# De-risk plan

1. Start with audit and classification only.
2. Focus first on public bounds, wrapper types, and opaque-handle patterns.
3. Validate on one real FFI crate with thin opaque handles.
4. Keep “unknown/manual review” first-class.

# Non-goals

- Not a replacement for bindgen, cxx, or autocxx.
- Not a promise that refined sizedness semantics are fully settled.
- Not a generic FFI safety framework.
- Not a new type-theory playground.

# Architecture & API sketch

```rust
pub enum OpaqueReadinessKind {
    Ready,
    Blocked,
    Unknown,
}

pub fn scan_sized_surface(root: &Path) -> Result<SizedSurface>;
pub fn classify_opaque_readiness(surface: &SizedSurface) -> Vec<SizedAuditFinding>;
pub fn diff_bound_posture(old: &SizedSurface, new: &SizedSurface) -> SizedDiff;
pub fn write_bundle(bundle: &SizedBundle, out: &Path) -> Result<()>;
```

Bundle draft: `sized-surface.toml`, `sized-audit.json`, `opaque-readiness.json`, `ffi-handle-map.json`, `trait-bound.diff.json`, `migration.receipt.json`, `notes.md`.

# Security / safety model

- Never claim extern-type readiness based on syntax alone when semantics remain unclear.
- Record exact toolchain, feature-gate, and source references used in the audit.
- Support path redaction in shared bundles.
- Distinguish observed posture from inferred future compatibility.

# Maintenance & governance plan

- Track the sized-hierarchy stabilization and tracking issue closely.
- Keep the audit vocabulary small and explanation-heavy.
- Maintain fixtures spanning opaque handles, wrappers, and public-trait surfaces.
- Publish guidance for interpreting default-supertrait and thin-pointer assumptions.

# Milestones

## 0.1
- surface scan
- readiness classification
- receipt export

## 0.2
- release diffing
- FFI handle maps
- bundle export

## 1.0
- stable receipt schema
- CI/report adapters
- curated casebook

# Open questions

- What is the smallest useful vocabulary for sizedness-readiness without overcommitting to final language semantics?
- Which public API patterns matter most semver-wise: explicit `Sized` bounds, wrapper types, default supertraits, or all three?
- How much of opaque-handle readiness can be inferred automatically versus requiring manual annotation?

# Sources

- Rust in 2026 flagships / sized hierarchy milestone: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Unstable book: `sized_hierarchy`: https://doc.rust-lang.org/beta/unstable-book/language-features/sized-hierarchy.html
- Tracking issue #144404: https://github.com/rust-lang/rust/issues/144404
- RFC 1861 extern types: https://rust-lang.github.io/rfcs/1861-extern-types.html
- 2025H2 project goals blog: https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
