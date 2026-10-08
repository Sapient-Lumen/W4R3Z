---
id: P-0445
title: Const Capability Ledger Kit — const-callable API ledgers, toolchain receipts, and upgrade diffs above const traits and rustdoc JSON
status: idea
domains: [const-eval, language, api, docs, devtools, embedded, no_std]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://docs.rs/crate/rustdoc-types/latest
  - https://crates.io/crates/rustdoc-json
  - https://docs.rs/crate/cargo-public-api/latest
  - https://doc.rust-lang.org/rustdoc/unstable-features.html
---

# Problem

Rust’s compile-time story is getting more ambitious. Const traits have been under active preparation for stabilization, and the 2026 flagships explicitly keep const traits moving toward stabilization.

That creates a practical library-maintainer problem that is still underserved:

- many crates want to advertise which public APIs are const-callable,
- compile-time capability often depends on toolchain version, feature flags, and target assumptions,
- downstream users want to know whether upgrading a crate or toolchain changed the const-usable surface,
- and current public-API tooling tells you *what* is public but not the more specific workflow question: **what became const-usable, stopped being const-usable, or stayed nightly-only?**

The missing crate is not “const traits implementation.”

The missing crate is a **ledger layer** that tracks a crate’s const-capable public surface and records the assumptions under which that claim is true.

# What it provides

- `const-profile.toml` — pins toolchain/channel, feature flags, target assumptions, and const-policy categories.
- `const-surface.json` — machine-readable public API ledger with const-callability categories.
- `const.diff.json` — changes between two const-surface ledgers across versions or toolchains.
- `const.receipt.json` — records how the ledger was produced and what caveats apply.
- `cargo const-ledger export` — emits a const-surface ledger for a crate/workspace.
- `cargo const-ledger compare` — compares two ledgers and highlights newly gained/lost const capability.
- `cargo const-ledger explain <item>` — tells a maintainer why an item was classified the way it was.
- `*.constbundle.zip` — shareable artifact for release review, docs, and embedded/no_std portability discussions.

# What the crate should provide other people

1. **A boring artifact** for saying “this API is const-usable under these assumptions.”
2. **Upgrade diffs** for const capability changes across crate or toolchain versions.
3. **A shared vocabulary** for stable, nightly-only, feature-gated, target-specific, and unknown const categories.
4. **A bridge** between public-API tooling and compile-time capability planning.
5. **Better release notes and docs** for crates serving embedded, no_std, and high-performance users.

# Persona / who it’s for

- library maintainers exposing const-friendly APIs
- embedded / no_std teams depending on compile-time execution
- release engineers comparing toolchain upgrades
- documentation and API review tooling authors

# Users & user stories

- **Library maintainer**: “Generate a ledger of which public functions and traits are const-usable today.”
- **Embedded user**: “Compare const capability between crate versions before I upgrade.”
- **Release engineer**: “Catch that a toolchain update changed our const surface.”
- **Docs/tooling author**: “Show const capability as a first-class report instead of a scattered set of annotations.”

# Prior art (and why it’s insufficient)

- `rustdoc-types` and `rustdoc-json` provide access to rustdoc JSON.
- `cargo-public-api` shows that public-surface extraction and diffing are already useful.
- The const-traits goals show why compile-time capability is moving.

What remains missing is a **const-capability ledger** with explicit policy categories, receipts, and upgrade diffs.

# Design goals

1. **Ledger before perfection** — record useful claims even while const language work evolves.
2. **Assumption-explicit** — toolchain/channel/features/target belong in the receipt.
3. **Public-surface scoped** — stay focused on public API first.
4. **Upgrade-friendly** — diffs and explanations matter as much as raw export.
5. **Honest about uncertainty** — do not silently classify unstable or inference-dependent cases as “stable const”.

# MVP surface

- Minimal types: `ConstProfile`, `ConstSurface`, `ConstItem`, `ConstClass`, `ConstReceipt`, `ConstDiff`
- Minimal functions:
  - `export_const_surface()`
  - `classify_item()`
  - `compare_ledgers()`
  - `explain_item()`
  - `write_receipt()`
- Feature flags:
  - `rustdoc-json`
  - `serde`
  - `cargo`
  - `public-api`

# Compatibility story

- Builds on rustdoc JSON instead of inventing a new extraction pipeline.
- Can ingest nightly-only rustdoc outputs while still recording that requirement.
- Should interoperate with `cargo-public-api`-style workflows conceptually, but keeps const capability as a separate report.
- Keeps target-specific and feature-specific caveats visible.

# Conformance & fixtures

- Fixtures for plainly const functions, non-const functions, feature-gated const items, target-sensitive const items, and trait-bound-heavy cases.
- Goldens for “newly const”, “lost const”, “nightly-only”, and “unknown because of unstable analysis” cases.
- Cross-version comparisons on small example crates.
- Example report snippets for docs and release notes.

# Path to boring stability

- Stabilize the `ConstClass` taxonomy early.
- Keep the first export surface narrow: public functions, methods, traits, and impl markers.
- Treat explanations and caveats as first-class.
- Add deeper inference only after the basic ledger proves useful.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that use rustdoc JSON plus explicit profile assumptions to export a public `const-surface.json`, compare two ledgers, and emit an explanation-rich receipt.

# De-risk plan

1. Start with a narrow const-class taxonomy.
2. Restrict the MVP to public items only.
3. Record nightly/toolchain assumptions explicitly instead of hiding them.
4. Validate usefulness on one const-heavy library and one embedded-friendly library.

# Non-goals

- Not a const-traits implementation.
- Not a promise that rustdoc JSON exposes every needed semantic detail forever.
- Not a replacement for general public-API diff tooling.
- Not a full static proof of compile-time behavior.

# Architecture & API sketch

```rust
pub enum ConstClass {
    StableConst,
    NightlyConst,
    FeatureGatedConst,
    TargetSpecificConst,
    NonConst,
    Unknown,
}

pub fn export_const_surface(profile: &ConstProfile, manifest: &Path) -> Result<ConstSurface>;
pub fn classify_item(item: &PublicItem, ctx: &AnalysisContext) -> ConstClass;
pub fn compare_ledgers(old: &ConstSurface, new: &ConstSurface) -> ConstDiff;
pub fn write_receipt(surface: &ConstSurface, profile: &ConstProfile) -> ConstReceipt;
```

Bundle draft: `const-profile.toml`, `const-surface.json`, `const.diff.json`, `const.receipt.json`, `notes.md`.

# Security / safety model

- Never classify an item as stable-const without recording the toolchain basis.
- Support redaction of local paths in receipts.
- Keep inference and unknown categories visible.
- Make unstable/nightly requirements explicit in every exported bundle.

# Maintenance & governance plan

- Track const-traits stabilization and rustdoc JSON surface changes carefully.
- Keep the classification taxonomy small and versioned.
- Maintain a public fixture corpus with cross-toolchain comparisons.
- Publish docs guidance for embedding ledger outputs into release notes and API docs.

# Milestones

## 0.1
- export ledger
- narrow classification taxonomy
- compare workflow

## 0.2
- richer explanations
- docs/report adapters
- fixture corpus

## 1.0
- stable receipt schema
- release-note integration guidance
- broader capability matrix support

# Open questions

- Which const categories are worth standardizing in the MVP?
- How much inference is safe to automate versus leaving as “unknown”? 
- Should trait-level const capability be reported separately from item-level const callability?

# Sources

- Prepare const traits for stabilization: https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `rustdoc-types`: https://docs.rs/crate/rustdoc-types/latest
- `rustdoc-json`: https://crates.io/crates/rustdoc-json
- `cargo-public-api`: https://docs.rs/crate/cargo-public-api/latest
- Rustdoc unstable features: https://doc.rust-lang.org/rustdoc/unstable-features.html
