---
id: P-0475
title: Rustdoc Mergeable Info Handoff Kit — doc.parts manifests, finalize receipts, and cross-crate documentation handoff bundles
status: idea
domains: [rustdoc, cargo, docs, build-systems, ci, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rfcs/3662-mergeable-rustdoc-cross-crate-info.html
  - https://doc.rust-lang.org/rustdoc/unstable-features.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/commands/cargo-doc.html
---

# Problem

Rustdoc and Cargo now have real substrate for cross-crate documentation work beyond the old “everything mutates one shared `target/doc` tree” model.

That substrate is newly meaningful:

- RFC 3662 defines mergeable cross-crate information and the `doc.parts` concept,
- rustdoc exposes `--merge`, `--parts-out-dir`, and `--include-parts-dir`,
- Cargo now has nightly `-Z rustdoc-mergeable-info` to leverage this for `cargo doc`,
- and the motivating use cases include large workspaces, distributed build systems, non-Cargo build systems, better caching, and more parallel documentation builds.

But ordinary maintainers and tool authors still lack a boring answer to questions like:

- which crates produced which `doc.parts`,
- whether all parts came from the same rustdoc/toolchain generation,
- which parts were included in a final merge and which were stale or missing,
- why the final documentation surface changed after only one crate was re-documented,
- how to hand docs-merge evidence from one CI/build system stage to another,
- and how to debug cross-crate trait-impl/search-index drift without reverse-engineering the doc root.

So the missing crate is not another docs portal.

The missing crate is a **rustdoc mergeable-info handoff kit**: a small crate and cargo-adjacent tool that turns `doc.parts` workflows into reviewable manifests, merge receipts, and CI handoff bundles.

# What it provides

- `docparts-profile.toml` — pins merge mode, toolchain expectations, part compatibility policy, and redaction options.
- `docparts.manifest.json` — lists produced parts by crate, version, source package, toolchain fingerprint, and output location.
- `docparts-compat.report.json` — flags rustdoc version mismatches, missing included parts, duplicate crate identities, and suspicious stale parts.
- `docparts-finalize.receipt.json` — records which parts were included in a finalize step, what cross-crate information was expected, and whether the merge was complete or partial.
- `docparts-diff.json` — compare two manifests/finalize receipts to classify docs-surface drift after a rebuild.
- `cargo docparts capture` — collect produced parts and emit a handoff bundle.
- `cargo docparts finalize` — consume declared parts, run or wrap a finalize step, and emit a receipt.
- `cargo docparts doctor` — flag stale/missing/mixed-version parts and suspicious output-topology mistakes.
- `*.docpartsbundle.zip` — portable artifact for CI stage handoff, build-system interop, workspace docs caching, or upstream bug reports.

# What the crate should provide other people

1. **A boring `doc.parts` manifest** instead of ad-hoc directory walking.
2. **A finalize receipt** explaining what cross-crate documentation data was merged.
3. **A compatibility report** for mixed toolchains, stale parts, and missing includes.
4. **A handoff artifact** for distributed or multi-stage docs pipelines.
5. **A bridge** between rustdoc’s mergeable-info substrate and maintainer-facing docs workflows.

# Persona / who it’s for

- large workspace maintainers with expensive docs builds
- CI/release engineers splitting docs generation across stages or machines
- build-system authors outside Cargo
- maintainers debugging cross-crate search-index or trait-impl drift
- tool authors experimenting with mergeable rustdoc flows while the upstream surface matures

# Users & user stories

- **Workspace maintainer**: “Show me which crate’s doc parts changed and whether we can safely finalize without rebuilding everything.”
- **CI owner**: “Archive one artifact from the per-crate docs stage and another from the finalize stage.”
- **Build-system author**: “Consume a stable manifest of `doc.parts` without scraping unstable directory shapes by hand.”
- **Rustdoc issue filer**: “Attach a compact bundle proving which parts were merged, which were stale, and which rustdoc version produced them.”

# Prior art (and why it’s insufficient)

- `cargo doc` already builds docs into `target/doc`, but its output is cumulative and traditionally shared-state oriented.
- rustdoc’s unstable mergeable-info flags and RFC 3662 define the underlying model.
- Cargo’s nightly `-Z rustdoc-mergeable-info` can leverage that substrate.

That is important progress, but it is still mostly **execution substrate**, not a compact **manifest / compatibility / finalize-receipt workflow**. The RFC explicitly says `doc.parts` contents are unstable and versioned, which makes a cautious handoff layer more valuable, not less.

# Design goals

1. **Handoff-first** — optimize for passing docs parts safely between stages, machines, and tools.
2. **Compatibility-explicit** — toolchain/version assumptions must always be visible.
3. **Diff-friendly** — one changed crate should produce a reviewable docs-surface change artifact.
4. **Build-system-neutral** — useful for Cargo, Buck2-like systems, and custom orchestrators.
5. **Honest about instability** — never pretend `doc.parts` internals are stable across rustdoc versions.

# MVP surface

- Minimal types: `DocPartsProfile`, `DocPartEntry`, `DocPartsManifest`, `DocPartsCompatReport`, `FinalizeReceipt`, `DocPartsDiff`, `DocPartsBundle`
- Minimal functions:
  - `capture_docparts_manifest()`
  - `check_docparts_compatibility()`
  - `finalize_docparts_bundle()`
  - `diff_docparts_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `nightly-adapter`
  - `markdown`
  - `redaction`

# Compatibility story

- Works above rustdoc/Cargo rather than replacing either.
- Can begin in a nightly-oriented mode while keeping the receipt explicit about unstable dependencies.
- Must preserve the distinction between “observed part facts”, “toolchain compatibility inference”, and “finalize outcome”.
- Should remain useful even if Cargo later stabilizes more mergeable-info support, because manifest/handoff/receipt workflows still matter.

# Conformance & fixtures

- One fixture with two crates where cross-crate trait implementation info is expected after finalize.
- One fixture with intentionally stale or mixed-version parts.
- One fixture with a missing include that should force a partial/failed finalize receipt.
- One fixture mimicking a split build pipeline: capture on one machine/stage, finalize on another.
- Goldens for `mixed_toolchain_parts`, `missing_part`, `finalize_drift`, and `manual_review_required`.

# Path to boring stability

- Stabilize the manifest/compat/finalize schema before adding UI layers.
- Start with capture and doctor workflows before trying to own every finalize mode.
- Keep the first compatibility vocabulary small and conservative.
- Prefer explicit uncertainty over fake guarantees about unstable rustdoc internals.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo-adjacent CLI that capture produced `doc.parts`, verify part compatibility and completeness, and emit one finalize receipt plus a diffable handoff bundle.

# De-risk plan

1. Start with manifest capture and compatibility checks before deeper finalize automation.
2. Treat rustdoc version/toolchain mismatch as first-class data, not a hidden implementation detail.
3. Keep the first finalize vocabulary binary and conservative: complete, partial, stale, incompatible.
4. Validate on one small workspace and one build-system-like split pipeline.

# Non-goals

- Not a replacement for rustdoc or Cargo.
- Not a general docs-hosting platform.
- Not a promise that unstable `doc.parts` internals are portable forever.
- Not another local docs portal or search UI.

# Architecture & API sketch

```rust
pub struct FinalizeReceipt {
    pub success: bool,
    pub included_parts: Vec<String>,
    pub incompatible_parts: Vec<String>,
    pub notes: Vec<String>,
}

pub fn capture_docparts_manifest(root: &Path) -> Result<DocPartsManifest>;
pub fn check_docparts_compatibility(bundle: &DocPartsBundle) -> DocPartsCompatReport;
pub fn finalize_docparts_bundle(bundle: &DocPartsBundle, out: &Path) -> Result<FinalizeReceipt>;
pub fn diff_docparts_bundles(old: &DocPartsBundle, new: &DocPartsBundle) -> DocPartsDiff;
```

Bundle draft: `docparts-profile.toml`, `docparts.manifest.json`, `docparts-compat.report.json`, `docparts-finalize.receipt.json`, `docparts-diff.json`, `notes.md`.

# Security / safety model

- Treat imported part bundles and logs as untrusted input.
- Support redaction of local paths and unpublished crate names in exported bundles.
- Preserve rustdoc/Cargo version facts prominently so mixed-version merges are not misread as equivalent.
- Never claim that finalize output is complete when required parts were absent or incompatible.

# Maintenance & governance plan

- Track RFC 3662 implementation progress, rustdoc mergeable-info changes, and Cargo’s `-Z rustdoc-mergeable-info` evolution.
- Keep schemas compact and versioned.
- Maintain fixtures for split pipelines, stale parts, version mismatch, and cross-crate-info drift.
- Publish guidance for build systems on artifact retention and toolchain pinning.

# Milestones

## 0.1
- part manifest capture
- compatibility report
- bundle export

## 0.2
- finalize receipts
- bundle diffing
- basic CI/build-system adapters

## 1.0
- stable handoff schema
- curated split-pipeline corpus
- upstream issue-template integrations

# Open questions

- What is the smallest useful compatibility vocabulary for unstable `doc.parts` workflows?
- Should the tool invoke finalize itself or remain import-and-report first?
- Which final docs-surface deltas are stable enough to report without overfitting rustdoc internals?

# Sources

- RFC 3662 mergeable cross-crate rustdoc info: https://rust-lang.github.io/rfcs/3662-mergeable-rustdoc-cross-crate-info.html
- rustdoc unstable merge flags: https://doc.rust-lang.org/rustdoc/unstable-features.html
- Cargo unstable `-Z rustdoc-mergeable-info`: https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo doc` reference: https://doc.rust-lang.org/cargo/commands/cargo-doc.html
