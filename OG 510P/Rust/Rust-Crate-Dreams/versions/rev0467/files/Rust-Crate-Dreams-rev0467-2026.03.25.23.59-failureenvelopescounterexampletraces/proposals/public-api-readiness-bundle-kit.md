---
id: P-0483
title: Public API Readiness Bundle Kit — public-surface snapshots, semver verdicts, dependency-boundary receipts, docs-readiness reports, and waiver-aware release bundles
status: idea
domains: [cargo, rustdoc, semver, api-design, release, docs, devtools, workspaces]
last_reviewed: 2026-03-19
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
  - https://docs.rs/crate/cargo-public-api/latest
  - https://docs.rs/crate/cargo-semver-checks/latest
  - https://doc.rust-lang.org/cargo/reference/unstable.html#public-dependency
  - https://doc.rust-lang.org/cargo/commands/cargo-add.html
  - https://doc.rust-lang.org/beta/rustc/lints/listing/warn-by-default.html#exported-private-dependencies
  - https://doc.rust-lang.org/rustdoc/unstable-features.html
  - https://doc.rust-lang.org/cargo/reference/semver.html
  - https://rust-lang.github.io/rfcs/3516-public-private-dependencies.html
---

# Problem

Rust’s public-contract tooling is now good enough that the sharper missing gap is **not** “find one more analyzer.”

Today we already have meaningful substrate:

- the Rust project’s 2026 flagship goals explicitly group **control over public API dependencies** and **breaking change detection** in one supply-chain track,
- `cargo-semver-checks` is on an explicit path toward Cargo integration, but still has blocker work and witness-heavy edge cases,
- `cargo-public-api` can list and diff the public API of a crate against releases and commits,
- Cargo’s `public-dependency` work is real enough that `cargo add --public` / `--no-public`, `cargo tree --edges public`, and metadata surfaces are all moving,
- rustc already explains the `exported_private_dependencies` contract,
- and rustdoc already exposes experimental JSON and coverage JSON.

But release review still feels scattered.

Maintainers who ask “is this release actually ready for our public API contract?” still end up stitching together:

- one semver report,
- one public-API diff,
- one public/private dependency check,
- one docs/examples report,
- and a pile of human judgment around waivers, intended breaks, and ambiguous public-surface growth.

That is not the same thing as lacking tools.
It means the ecosystem still lacks a **public API readiness bundle**: one boring artifact that answers, for a candidate release:

- what the public surface is,
- how it changed,
- which dependencies are now part of that surface,
- what docs/example debt matters for users of that surface,
- which waivers or intended breaks exist,
- and whether the release is ready, ready-with-waivers, not-ready, or manual-review-only.

This is **not** the same as the broader compatibility universe.
This proposal is narrower and sharper: it is about **public-surface release review**.

# What it provides

- `public-api-policy.toml` — declares semver intent, docs thresholds, waiver rules, and blocking/advisory posture.
- `public-surface.snapshot.json` — normalized public-item inventory with reexports, deprecations, and provenance.
- `semver-verdict.report.json` — imported/computed semver-check results, witness posture, and uncertainty classes.
- `public-dependency-boundary.report.json` — dependencies believed to be public, ambiguous, or private, with reason categories.
- `docs-readiness.report.json` — docs/examples readiness focused on the public API surface.
- `waiver-ledger.receipt.json` — explicit waivers with owner, rationale, expiry, and blocking/advisory posture.
- `release-readiness.verdict.json` — the joined release-review answer.
- `api-ready.diff.json` — compares two bundles and classifies public-contract drift.
- `cargo api-ready capture` — emit one release-review bundle.
- `cargo api-ready diff <old> <new>` — compare public-contract readiness across releases or branches.
- `cargo api-ready gate` — apply policy and emit `ready`, `ready_with_waivers`, `manual_review_required`, or `not_ready`.
- `cargo api-ready explain <item>` — explain why an item or dependency matters to the public contract.
- `*.apiready.zip` — portable artifact for PR review, release approval, or downstream communication.

# What the crate should provide other people

1. **One joined review artifact** for public API release readiness.
2. **A reusable vocabulary** connecting semver checks, public dependencies, docs readiness, and waiver posture.
3. **A waiver ledger** so intended breaks or temporary docs debt do not disappear into chat or CI logs.
4. **A bridge** from nightly-heavy analyzers to a maintainable release habit.
5. **A release verdict** that reviewers can act on without running multiple tools by hand.
6. **Evidence-class honesty** about what was measured, imported, or inferred.

# Persona / who it’s for

- maintainers of public libraries and SDKs
- release engineers approving crate publishes
- API reviewers and semver stewards
- workspace owners trying to standardize release review
- tooling authors building release bots or changelog helpers

# Users & user stories

- **Library maintainer**: “Before publishing, show me whether our public surface changed in a way that matches our intended semver story.”
- **Reviewer**: “Give me one bundle that joins API diff, public dependencies, docs readiness, and waivers.”
- **Workspace owner**: “Normalize how our crates document and review public-contract changes.”
- **Downstream consumer**: “Tell me whether this release is larger or riskier than the changelog makes it sound.”

# Prior art (and why it’s insufficient)

- `cargo-semver-checks` is excellent at semver-focused API analysis.
- `cargo-public-api` is excellent at listing and diffing the public surface.
- public/private dependency work sharpens what a public surface even is.
- rustdoc JSON and coverage JSON make more public-surface facts machine-readable.

What remains missing is the **joined maintainer artifact** above all of these: the thing that says “this is the public contract we are shipping, here is how it changed, here is the docs posture for that surface, and here are the explicit waivers.”

# Design goals

1. **Release-review-first** — optimize for PRs and release signoff, not dashboards.
2. **Public-surface narrowness** — stay focused on public API, not the entire compatibility universe.
3. **Join, don’t replace** — use existing analyzers and reports where possible.
4. **Nightly-honest** — keep toolchain/version facts explicit whenever adapters rely on unstable substrate.
5. **Waiver-visible** — intended exceptions must be structured, reviewable, and expiring.
6. **Evidence-class explicitness** — measured, imported, and inferred facts must stay separable.

# MVP surface

- Minimal types: `PublicApiPolicy`, `PublicSurfaceSnapshot`, `SemverVerdictReport`, `PublicDependencyBoundaryReport`, `DocsReadinessReport`, `WaiverLedgerReceipt`, `ReleaseReadinessVerdict`, `ApiReadinessBundle`, `ApiReadinessDiff`
- Minimal functions:
  - `capture_api_readiness_bundle()`
  - `import_public_surface_snapshot()`
  - `import_semver_verdict()`
  - `compute_public_dependency_boundary_report()`
  - `compute_docs_readiness_report()`
  - `apply_release_gate()`
  - `diff_api_readiness_bundles()`
- Feature flags:
  - `cargo`
  - `serde`
  - `cargo-public-api`
  - `semver-checks`
  - `nightly-rustdoc`
  - `markdown`

# Compatibility story

- Stable-first mode should still work by importing existing tool outputs.
- Higher-fidelity mode can use nightly rustdoc JSON / coverage surfaces when present.
- The bundle must preserve which fields were **measured**, **imported**, or **inferred conservatively**.
- The crate should remain useful even if semver checks move into Cargo, because the joined review/waiver artifact still matters.

# Conformance & fixtures

- One fixture with a harmless patch release and no public-surface drift.
- One fixture with a new public dependency leaking through a reexport.
- One fixture with docs/example regressions on the public API only.
- One fixture with an intended major-version break plus explicit waiver metadata.
- One fixture where analyzer outputs conflict and the only honest result is `manual_review_required`.
- Goldens for `public_dep_leak`, `semver_break_intended`, `docs_regression_public`, `waiver_expired`, and `manual_review_required`.

# Path to boring stability

- Stabilize the bundle schema before adding bots or changelog generation.
- Start with capture/import/diff before trying to auto-decide every edge case.
- Keep the first waiver vocabulary strict and small.
- Treat “manual review required” as honest output, not product failure.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that join public-API diff facts, semver verdicts, public-dependency analysis, docs-surface readiness, and waiver metadata into one diffable release-review bundle.

# De-risk plan

1. Start by importing existing analyzer outputs rather than replacing them.
2. Keep public-dependency reasoning explicit and conservative.
3. Validate on one small library and one multi-crate workspace.
4. Add automatic gating only after the bundle is trusted as a review artifact.

# Non-goals

- Not a replacement for `cargo-semver-checks`, `cargo-public-api`, rustdoc, or changelog tooling.
- Not a general behavioral-compatibility platform.
- Not an MSRV or feature-matrix test runner.
- Not a promise that every semver edge case can be auto-classified perfectly.

# Architecture & API sketch

```rust
pub struct ReleaseReadinessVerdict {
    pub status: String,
    pub reasons: Vec<String>,
}

pub fn capture_api_readiness_bundle(root: &Path) -> Result<ApiReadinessBundle>;
pub fn import_semver_verdict(path: &Path) -> Result<SemverVerdictReport>;
pub fn diff_api_readiness_bundles(old: &ApiReadinessBundle, new: &ApiReadinessBundle) -> ApiReadinessDiff;
pub fn apply_release_gate(bundle: &ApiReadinessBundle) -> ReleaseReadinessVerdict;
```

Bundle draft: `public-api-policy.toml`, `public-surface.snapshot.json`, `semver-verdict.report.json`, `public-dependency-boundary.report.json`, `docs-readiness.report.json`, `waiver-ledger.receipt.json`, `release-readiness.verdict.json`, `api-ready.diff.json`, `notes.md`.

# Security / safety model

- Treat imported analyzer output as untrusted input.
- Never hide which facts came from nightly-only surfaces.
- Support redaction of local paths and unpublished crate names.
- Preserve exact tool versions and policy inputs so review bundles remain auditable.

# Maintenance & governance plan

- Track semver-checks integration work, public/private dependency stabilization, and rustdoc JSON/coverage evolution.
- Keep the schema compact and explanation-heavy.
- Maintain fixtures for reexports, deprecations, docs regressions, conflicting analyzer outputs, and ambiguous public dependencies.
- Publish guidance on which verdicts should block release versus stay advisory.

# Milestones

## 0.1
- public-surface snapshot import
- semver verdict import
- waiver ledger
- bundle export

## 0.2
- public-dependency boundary report
- docs-readiness report
- policy gate + release verdict

## 1.0
- stable bundle schema
- curated workspace fixtures
- release-bot integration helpers

See also: `meta/public-api-readiness-product-plan-2026-03-19.md` and `meta/public-api-readiness-lanes-2026-03-19.md`.
