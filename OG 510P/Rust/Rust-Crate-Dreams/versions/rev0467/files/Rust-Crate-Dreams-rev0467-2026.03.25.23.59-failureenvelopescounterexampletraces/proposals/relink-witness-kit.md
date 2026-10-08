---
id: P-0438
title: Relink Witness Kit — interface fingerprints, private-change receipts, and dependent-impact evidence above Cargo’s smarter rebuild future
status: idea
domains: [cargo, build-performance, ci, workspaces, devtools, compiler]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
  - https://github.com/cargo-public-api/cargo-public-api
  - https://github.com/obi1kenobi/cargo-semver-checks
  - https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
---

# Problem

Rust is actively working toward a future where many edits should **relink, not rebuild** reverse dependencies.

That future is strategically important, but ordinary maintainers still lack a user-facing artifact for one of the most common daily questions:

**Did this change alter the interface that downstream crates actually depend on, or was it only an internal change?**

Today, teams can reach for pieces of this problem:

- `cargo-public-api` can diff a crate’s public API,
- `cargo-semver-checks` can find semver-relevant API breakage,
- Cargo timings and build logs can show what *did* rebuild,
- and Cargo Impact Planner–style logic can estimate workspace blast radius.

But there is still no compact, boring artifact for saying:

- this edit changed no downstream-visible interface,
- these items changed but were private,
- these dependents would ideally only need relinking,
- and this receipt is what the decision was based on.

The missing crate is not a replacement for Cargo’s future rebuild intelligence.

The missing crate is a **witness layer** that makes interface-preserving edits legible to humans, CI, and future tooling.

# What it provides

- `relink-policy.toml` — declares what counts as interface-bearing for a workspace: public API, selected feature surfaces, exported symbols, optional doc/FFI overlays.
- `interface.fingerprint.json` — stable digest of the selected interface surface for one package/profile/feature set.
- `change.classification.json` — structured explanation of public, private, doc-only, build-only, or manifest-level changes.
- `relink.witness.json` — records whether a diff appears interface-preserving, caveated, or interface-changing.
- `dependent-impact.json` — conservative downstream classes: `no-downstream-interface-change`, `public-surface-changed`, `ffi-surface-changed`, `unknown`.
- `cargo relink-witness diff` — compares two revisions and emits fingerprints plus change classification.
- `cargo relink-witness explain` — tells a human why an edit was treated as interface-preserving or not.
- `relinkbundle.zip` — fingerprints, classification, selected API views, logs, and reproduction commands.

# What the crate should provide other people

1. **A reviewable witness** that a change was private or interface-bearing.
2. **A compact handoff artifact** for CI systems and code reviewers.
3. **A shared vocabulary** for “this should have only relinked” discussions.
4. **A bridge** between current public-API diff tools and Cargo’s future smarter rebuild work.
5. **A conservative planning primitive** that other tools can consume without scraping compiler internals.

# Persona / who it’s for

- maintainers of large Rust workspaces
- CI and build engineers
- compiler-performance enthusiasts
- library teams that want to separate internal churn from downstream-visible change

# Users & user stories

- **Maintainer**: “I only changed private implementation details; give me a receipt that says whether downstream-visible interface changed.”
- **Reviewer**: “Show me why this PR is being treated as public-surface-neutral.”
- **CI owner**: “Attach one artifact to a PR explaining why we ran a narrow or broad downstream plan.”
- **Cargo/tooling author**: “Reuse a stable witness schema instead of reinventing API fingerprint outputs.”

# Prior art (and why it’s insufficient)

- `cargo-public-api` provides strong public-API listing and diffs, but it is not aimed at producing a conservative **relink witness** for day-to-day workspace edits.
- `cargo-semver-checks` is excellent for release gating, but semver break detection is not the same as a compact classification of “private change versus downstream-visible surface drift.”
- Cargo itself is pursuing smarter rebuild behavior, but today’s users still need an artifact that explains the difference between what Cargo rebuilt and what a future smarter world would treat as interface-preserving.

What remains missing is a **fingerprint/classification/witness layer** designed specifically for this seam.

# Design goals

1. **Conservative first** — uncertain cases should be caveated, not over-optimized.
2. **Human-explainable** — every classification should come with reasons.
3. **Surface-selective** — support public API first, then optional FFI/doc/export overlays.
4. **Profile-aware** — record feature, target, and profile context explicitly.
5. **Future-friendly** — useful now without depending on Cargo internals becoming stable.

# MVP surface

- Minimal types: `RelinkPolicy`, `InterfaceFingerprint`, `ChangeClassification`, `RelinkWitness`, `DependentImpact`
- Minimal functions:
  - `fingerprint_revision()`
  - `classify_change()`
  - `write_witness()`
  - `explain_witness()`
  - `bundle_witness()`
- Feature flags:
  - `rustdoc-json`
  - `ffi`
  - `git`
  - `serde`
  - `html-report`

# Compatibility story

- Starts above `cargo-public-api` / rustdoc-JSON style tooling.
- Can ingest semver-check outputs as an advisory overlay, not as the sole truth source.
- Integrates cleanly with workspace impact planners and CI policy tools.
- Must not claim exact equivalence with future Cargo/rustc rebuild behavior.

# Conformance & fixtures

- Fixture crates covering doc-only edits, private-function edits, public-signature edits, re-export changes, feature-gated surface changes, and FFI symbol/header changes.
- Goldens for `private-only`, `public-api-changed`, `ffi-overlay-changed`, and `unknown/caveated` outcomes.
- Multi-package fixtures showing downstream impact classification across a workspace.
- Replay bundles for disagreements between witness output and actual build behavior.

# Path to boring stability

- Stabilize `interface.fingerprint.json` and `relink.witness.json` early.
- Keep the initial reason taxonomy intentionally small.
- Avoid pretending to model rustc incremental internals.
- Treat caveats as first-class, especially around macros, generated code, and unstable tool outputs.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A crate and cargo subcommand that compare two revisions of a crate, emit an interface fingerprint and a conservative “private change versus downstream-visible change” witness, and bundle the reasons into one artifact.

# De-risk plan

1. Start with public API plus feature/profile context only.
2. Keep FFI/doc overlays opt-in until the witness core is trusted.
3. Validate on real open-source workspaces with known private-only versus public-surface changes.
4. Treat `unknown` as a valid and healthy outcome.

# Non-goals

- Not a replacement for Cargo’s rebuild logic.
- Not an exact model of rustc incremental compilation.
- Not a full semver certification framework.
- Not a generic benchmark/timing tool.

# Architecture & API sketch

```rust
pub struct RelinkWitness {
    pub package: String,
    pub old_fingerprint: InterfaceFingerprint,
    pub new_fingerprint: InterfaceFingerprint,
    pub classification: ChangeClassification,
    pub dependent_impact: Vec<DependentImpact>,
    pub caveats: Vec<String>,
}

pub fn fingerprint_revision(input: &RevisionInput, policy: &RelinkPolicy) -> Result<InterfaceFingerprint>;
pub fn classify_change(old: &InterfaceFingerprint, new: &InterfaceFingerprint) -> ChangeClassification;
pub fn explain_witness(witness: &RelinkWitness) -> String;
```

Bundle draft: `relink-policy.toml`, `interface.old.json`, `interface.new.json`, `change.classification.json`, `relink.witness.json`, `dependent-impact.json`, `notes.md`.

# Security / safety model

- Support redaction of private paths and private crate names in shared bundles.
- Distinguish strong claims from caveated inference.
- Never silently convert `unknown` into “safe to skip.”
- Preserve toolchain/profile provenance for every fingerprint.

# Maintenance & governance plan

- Keep the reason taxonomy versioned and small.
- Track rustdoc/public-API substrate changes explicitly.
- Maintain a small corpus of known-private and known-public-change fixtures.
- Publish caveat guidance for macros, generated code, and FFI overlays.

# Milestones

## 0.1
- public-surface fingerprint
- private/public change classification
- witness bundle export

## 0.2
- feature/profile overlays
- downstream impact classes
- HTML explainer report

## 1.0
- stable witness schema
- optional FFI/doc overlays
- CI adapters

# Open questions

- What is the smallest useful fingerprint that remains reviewable?
- Should feature-gated surfaces live inside one fingerprint or multiple named variants in the MVP?
- How much foreign-item / cross-crate surface tracking should be first-class at launch?

# Sources

- Relink don’t rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- `cargo-public-api`: https://github.com/cargo-public-api/cargo-public-api
- `cargo-semver-checks`: https://github.com/obi1kenobi/cargo-semver-checks
- Cargo semver-checks project goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
