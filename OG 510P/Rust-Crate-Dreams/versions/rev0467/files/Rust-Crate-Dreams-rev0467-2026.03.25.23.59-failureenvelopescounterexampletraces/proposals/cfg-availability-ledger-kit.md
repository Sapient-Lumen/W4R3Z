---
id: P-0451
title: Cfg Availability Ledger Kit — feature/target availability matrices, rustdoc-JSON receipts, and semver-aware API-surface diffs for conditional Rust APIs
status: idea
domains: [rustdoc, cargo, api, semver, documentation, tooling, features, targets]
last_reviewed: 2026-03-17
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
  - https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
  - https://docs.rs/about/rustdoc-json
  - https://crates.io/crates/rustdoc-json
  - https://docs.rs/doc-cfg
  - https://doc.rust-lang.org/rustdoc/advanced-features.html
  - https://docs.rs/about/builds
  - https://doc.rust-lang.org/cargo/reference/features.html
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
---

# Problem

Rust is finally moving toward first-class visibility of conditional API availability. The `doc_cfg` stabilization push and RFC 3631 make it much easier for humans to see *why* an item is available on one target or with one feature set but not another.

But that still leaves a practical gap for maintainers:

- large crates often expose different APIs across feature sets, targets, and docs.rs assumptions,
- documentation may show availability banners while CI and release review still lack a machine-readable ledger,
- semver review becomes much harder when an item disappears only under one target/feature combination,
- and today’s API-diff tools and rustdoc JSON consumers do not give teams a compact artifact for **availability drift**.

The missing crate is not another docs renderer.

The missing crate is an **availability ledger** that makes conditional API surface reviewable.

Treat `meta/cfg-availability-ledger-product-plan-2026-03-17.md` as the current implementation-oriented build sketch for this proposal.

# What it provides

- `availability-ledger.toml` — pins target triples, feature sets, docs.rs assumptions, and comparison policy.
- `availability.matrix.json` — item-level matrix of where an API is available, hidden, docs-visible-only, docs.rs-assumed-only, or inferred.
- `availability.diff.json` — categories such as `newly_available`, `newly_unavailable`, `docs_only_drift`, `feature_gate_changed`, `target_gate_changed`, `origin_changed`, and `fidelity_changed`.
- `availability.receipt.json` — rustdoc version, rustdoc JSON format version, target list, feature list, hosted-import caveats, and provenance.
- `availability.summary.md` — generated summary for changelogs, docs portals, or support replies.
- `availability-class.policy.json` — policy for what each availability class means.
- `availability-origin.receipt.json` — where a cell's visibility came from (`cfg`, `doc(cfg)`, `cfg(doc)`, docs.rs metadata, inference, etc.).
- `matrix-fidelity.report.json` — how much of the matrix is directly observed versus docs-only, hosted-imported, or inferred.
- `usability-witness.receipt.json` — records whether an item/slice is merely docs-visible or also same-crate-compilable, doctest-usable, and downstream-usable, plus what evidence backs each audience claim.
- `default-surface-drift.report.json` — records when docs.rs defaults or other hosted assumptions changed the default visible surface without proving new support.
- `cargo availability-ledger capture` — derive a ledger from rustdoc JSON plus Cargo/docs.rs configuration.
- `cargo availability-ledger diff` — compare two versions or two config matrices.
- `cargo availability-ledger doctor` — surface suspicious docs.rs / `cfg(doc)` / feature mismatches.
- `*.availabilityledger.zip` — shareable artifact for release review, documentation review, or issue reports.

# What the crate should provide other people

1. **A boring way to review conditional API drift** before releases.
2. **A machine-readable matrix** for feature-heavy and platform-heavy crates.
3. **A documentation handoff artifact** that can feed changelogs, docs portals, and support replies.
4. **A semver helper** for cases where only one availability slice changed.
5. **A bridge** between rustdoc-facing visibility improvements and maintainer-facing release workflows.
6. **A boring answer** to “can another team actually use this item, or is it only visible in docs?”.

# Persona / who it’s for

- maintainers of feature-heavy libraries
- platform-specific crate authors
- release engineers and semver reviewers
- docs maintainers and docs.rs-focused crate owners
- tooling authors building API portals or compatibility bots

# Users & user stories

- **Library maintainer**: “Tell me whether this release removed any public item on `wasm32` or behind our `tls` feature.”
- **Docs maintainer**: “Generate an availability summary that matches what docs.rs shows and flags anything suspicious.”
- **Release engineer**: “Distinguish ‘removed everywhere’ from ‘only no longer available with one feature combo’.”
- **Downstream team**: “Show which features/targets are needed to access this API on the version we depend on.”

# Prior art (and why it’s insufficient)

- RFC 3631 and the `doc_cfg` stabilization work improve visibility in rustdoc itself.
- `rustdoc-json` and docs.rs rustdoc JSON give a machine-readable substrate.
- `doc-cfg` has helped crate authors bridge the old gap.

What remains missing is a **release-grade ledger/diff/receipt layer** that treats conditional availability as part of the API surface rather than an afterthought.

# Design goals

1. **Availability-first** — model what is reachable where, not just what names exist.
2. **Origin-explicit** — every important claim should say whether it came from real `cfg`, docs markers, docs.rs assumptions, or inference.
3. **Fidelity-explicit** — every matrix cell should say whether it was directly observed, docs-only observed, hosted-imported, or inferred.
4. **Audience-legible** — keep docs-visible, doctest-usable, and downstream-usable truth separate.
5. **Semver-legible** — make conditional removals and additions obvious in review.
6. **Renderer-neutral** — artifacts should be useful outside rustdoc HTML.
7. **Conservative** — when availability cannot be inferred confidently, mark it as uncertain.

# MVP surface

- Minimal types: `AvailabilityProfile`, `AvailabilityMatrix`, `AvailabilityCell`, `AvailabilityDiff`, `AvailabilityReceipt`, `AvailabilityOriginReceipt`, `MatrixFidelityReport`, `UsabilityWitnessReceipt`, `DefaultSurfaceDriftReport`
- Minimal functions:
  - `capture_matrix()`
  - `merge_rustdoc_json()`
  - `classify_origin()`
  - `classify_fidelity()`
  - `diff_matrices()`
  - `render_summary()`
  - `run_doctor()`
  - `derive_usability_witness()`
  - `detect_default_surface_drift()`
- Feature flags:
  - `rustdoc-json`
  - `cargo`
  - `serde`
  - `markdown`

# Compatibility story

- Uses rustdoc JSON and Cargo metadata rather than compiler internals where possible.
- Should remain useful whether `doc_cfg` is stable or still partially rolling out.
- Can operate in “docs.rs assumptions only” mode when local target matrices are unavailable.
- Must keep rustdoc JSON format/version information visible in receipts.

# Conformance & fixtures

- Crates with feature-gated modules, platform-only APIs, docs.rs-only visibility shims, `cfg(doc)` visibility, and mixed feature dependencies.
- Goldens for “new item only on one target”, “feature gate changed”, “docs-only mismatch”, “docs.rs-assumed-only slice”, “default hosted surface drift”, and “unavailable everywhere” cases.
- Fixture matrices for `no_std`, `std`, `wasm32`, `unix`, and Windows-oriented APIs.
- Example generated `availability.summary.md` reports.

# Path to boring stability

- Stabilize the matrix schema before adding fancy visualizers.
- Start with public-item presence/absence and gate explanation.
- Treat inferred availability carefully and visibly.
- Keep docs.rs-specific assumptions as an optional explicit profile, not a hidden default.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 28/30**

# Minimum lovable MVP

A library and cargo subcommand that build an item-by-item feature/target availability matrix from rustdoc JSON, diff two versions, and export a release-review receipt plus human-readable summary.

# De-risk plan

1. Start with item presence/absence plus class/origin/fidelity, not full expression simplification.
2. Support one public-item source first: rustdoc JSON.
3. Keep the first diff categories few and semver-oriented.
4. Validate on one feature-heavy and one platform-heavy crate before broadening expression handling.
5. Treat `cfg(doc)` and docs.rs-specific slices as explicit special cases, not normal availability by default.

# Non-goals

- Not a replacement for rustdoc.
- Not a full solver for arbitrary `cfg` logic semantics.
- Not a docs.rs hosting platform.
- Not a generic semver checker for all API concerns.

# Architecture & API sketch

```rust
pub struct AvailabilityCell {
    pub item_id: String,
    pub targets: Vec<String>,
    pub features: Vec<String>,
    pub status: AvailabilityStatus,
}

pub fn build_matrix(profile: &AvailabilityProfile, root: &Path) -> Result<AvailabilityMatrix>;
pub fn diff_matrices(old: &AvailabilityMatrix, new: &AvailabilityMatrix) -> AvailabilityDiff;
pub fn render_summary(diff: &AvailabilityDiff) -> String;
pub fn run_doctor(matrix: &AvailabilityMatrix) -> Vec<AvailabilityFinding>;
```

Bundle draft: `availability-profile.toml`, `availability.matrix.json`, `availability.diff.json`, `availability.receipt.json`, `usability-witness.receipt.json`, `default-surface-drift.report.json`, `availability.md`, `notes.md`.

# Security / safety model

- No hidden network access in the MVP.
- Record rustdoc JSON format versions and target assumptions explicitly.
- Support path redaction in exported bundles.
- Avoid claiming reachability for expressions the tool cannot evaluate conservatively.

# Maintenance & governance plan

- Track rustdoc JSON evolution and docs.rs behavior carefully.
- Version the matrix schema independently of presentation templates.
- Maintain a public fixture corpus of conditional-API cases.
- Document what is inferred versus directly observed.

# Milestones

## 0.1
- rustdoc JSON ingestion
- matrix schema
- version-to-version diff

## 0.2
- doctor mode
- docs.rs assumption profiles
- markdown summary generation

## 1.0
- stable receipt schema
- richer target/feature templates
- CI/release adapters

# Open questions

- What is the smallest useful representation of conditional availability for semver review?
- How much `cfg` simplification should the crate attempt versus merely record?
- How should docs.rs-only visibility tricks be surfaced without confusing downstream users?

# Sources

- Stabilize rustdoc `doc_cfg` feature: https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- RFC 3631 rustdoc cfg handling: https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- docs.rs rustdoc JSON: https://docs.rs/about/rustdoc-json
- `rustdoc-json` crate: https://crates.io/crates/rustdoc-json
- `doc-cfg` crate: https://docs.rs/doc-cfg


## 2026-03-17 deepening note — slice witness, gate normalization, and re-export lineage

The earlier `0.1` sketch still needed three additional review objects to stay honest in practice:

1. **slice-witness receipts** — record which target/feature/docs profile was actually observed, whether the witness was local or hosted, and whether the evidence is docs-only or usable-slice evidence.
2. **gate-normalization reports** — record how raw `cfg` / `doc(cfg)` / `doc(auto_cfg)` / docs.rs overlays were simplified into the gate text a human sees.
3. **re-export-lineage reports** — record when an exported public path inherits a gate from a deeper defining path instead of declaring it locally.

Without those, a ledger still risks three false stories:

- “the displayed gate label is the whole truth,”
- “the final docs.rs crate view proves dependency-backed availability,”
- and “the top-level public path is unconditional because the `pub use` line looks unconditional.”

Treat `meta/cfg-availability-ledger-lanes-2026-03-17.md` as the boundary note for keeping this lane separate from whole-project support contracts, docs.rs parity bundles, capability contracts, and generic public-API diff tools.
