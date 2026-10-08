---
id: P-0471
title: Cargo Artifact Handoff Kit — stable build receipts, copied-output manifests, and CI/package-manager handoff bundles
status: idea
domains: [cargo, build, ci, packaging, external-tools, devtools, release-engineering]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  - https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
---

# Problem

Cargo now has enough output substrate that the absence of a **boring artifact handoff bundle** is harder to excuse.

Official signals line up unusually well:

- Cargo external-tools JSON already emits `compiler-artifact`, `build-script-executed`, and `build-finished` messages for machine consumers.
- The unstable `--artifact-dir` flag exists because predictably accessing final artifacts is still awkward if you only have raw Cargo output.
- The 2026 build-dir-layout-v2 testing push explicitly tells people to run tests and release processes that touch build-dir / target-dir against the new layout, which is a sign that downstream consumers still need a better final-artifact story.
- Current Cargo design work on custom final artifacts says build scripts cannot simply write directly into the artifact-dir because Cargo still needs collision reporting and concurrent-access safety.
- Build-analysis work is adding persistent session identifiers and replayable reports, which gives downstream tools a new way to link a handoff bundle to one specific Cargo invocation.

That combination means the missing crate is not “another release platform” and not “yet another log parser”.
The missing crate is a **Cargo Artifact Handoff Kit**: a stable receipt-and-bundle layer that turns one Cargo build into a compact, reviewable produced-artifact contract for packagers, CI jobs, external build systems, and downstream tooling.

# Main judgment

This crate is worthy because it solves a broad workflow seam that still shows up everywhere Rust is used seriously:

- CI jobs need one compact manifest of what a build produced.
- Packagers need to know which outputs are the real promoted artifacts.
- External build systems need a smaller contract than “parse every line of Cargo JSON correctly forever”.
- Teams testing build-dir changes need a clean escape hatch toward **final-artifact handoff** rather than ongoing layout scraping.
- Reviewers need to see whether bundle facts came from stable Cargo messages, unstable copied-output help, build-script metadata, or conservative filesystem reconstruction.

The missing value is **produced-artifact handoff exactness**.

# What it provides

- `artifact-handoff.lock` — pins Cargo/rustc versions, workspace/package selection, target/profile/features, requested artifact scope, and whether copied outputs came from raw JSON, `--artifact-dir`, imported build-analysis session data, or conservative reconstruction.
- `artifact-manifest.json` — canonical list of promoted artifacts with owner package, target kind, profile, platform context, executable/library classification, and copied-output locations when present.
- `artifact-origin.receipt.json` — explains, per artifact, which facts came from `compiler-artifact` messages, `build-script-executed` messages, `build-finished` observation, `--artifact-dir`, explicit build-script metadata, or manual review.
- `native-output.report.json` — normalized build-script / native output facts relevant to packagers and external toolchains.
- `handoff.receipt.json` — command lines, message-format expectations, observed `build-finished` state, session IDs when available, stdout-cleanliness caveats, redactions, and imported-report provenance.
- `artifact-layout.diff.json` — compare two bundles and classify `artifact_added`, `artifact_removed`, `copied_output_changed`, `owner_changed`, `origin_basis_changed`, `layout_drift_only`, and `manual_review_required`.
- `cargo artifact-handoff capture` — run or import one build and emit a reviewable handoff bundle.
- `cargo artifact-handoff explain <artifact>` — explain where one promoted output came from and why the bundle considers that explanation exact, conservative, or manual-review-only.
- `cargo artifact-handoff diff <old> <new>` — compare two builds as a shipping and integration surface instead of as logs.
- `*.artifacthandoff.zip` — portable artifact for CI, distro/package-manager handoff, support tickets, and downstream build orchestrators.

# What the crate should provide other people

1. **A boring machine-readable produced-artifact contract** above Cargo build output.
2. **A stable manifest** for final artifacts that other jobs can consume without rescraping raw logs.
3. **An origin receipt** that says which artifact facts are direct Cargo truth versus reconstruction or unstable convenience.
4. **A bridge from build-dir/layout churn to final-artifact stability**.
5. **A diffable review layer** when artifact shape or ownership changes unexpectedly.
6. **A session-linkable bundle** that can join one handoff result to one Cargo invocation when build-analysis data is available.

# Persona / who it’s for

- CI and release engineers
- distro/package-manager maintainers
- teams integrating Cargo into larger non-Cargo build systems
- authors of Cargo-adjacent packaging or deployment tools
- maintainers migrating consumers away from target/build-dir scraping

# Users & user stories

- **CI owner**: “Give me one manifest of what this build produced so later jobs do not scrape logs.”
- **Packager**: “Tell me which output is the real promoted artifact and what evidence supports that mapping.”
- **External build-system maintainer**: “Consume a stable handoff bundle instead of reimplementing Cargo JSON handling.”
- **Reviewer**: “Show me how the artifact surface changed between two commits or toolchains, and whether the change is layout-only or real.”
- **Build-dir migration owner**: “Tell me whether this consumer can stop touching build-dir internals and switch to final-artifact handoff.”

# Prior art (and why it’s insufficient)

- Cargo external-tools JSON is powerful, but it is still streaming output that downstream tools must capture and normalize themselves.
- `--artifact-dir` is promising, but it is nightly-only, copied-output oriented, and not a full handoff contract.
- Build-analysis sessions add durable identifiers and replayable context, but they are about historical build analysis, not a shared produced-artifact manifest for downstream consumers.
- Build-dir-layout-v2 work and custom-final-artifact design work prove the need is real, but those are upstream substrate and transition mechanics, not a boring bundle format for ordinary teams.
- Release-specialized tools may already produce manifests, but that is a bigger opinionated surface than many users need.

What remains missing is the small, explicit **manifest + origin receipt + diff bundle** above Cargo’s existing artifact substrate.

# Design goals

1. **Handoff-first** — optimize for downstream consumers, not dashboards.
2. **Origin-explicit** — every artifact fact should preserve where it came from.
3. **Build-dir-escape-oriented** — make it easier for consumers to stop depending on internal layout details.
4. **Diff-friendly** — output-surface changes should be easy to classify and review.
5. **Cargo-adjacent** — wrap Cargo’s CLI/output substrate instead of pretending Cargo as a library is stable.
6. **Session-linkable** — when build-analysis data exists, preserve the join key without requiring it.

# MVP surface

- Minimal types:
  - `ArtifactHandoffLock`
  - `ArtifactManifest`
  - `ArtifactRecord`
  - `ArtifactOriginReceipt`
  - `NativeOutputReport`
  - `HandoffReceipt`
  - `ArtifactLayoutDiff`
  - `ArtifactHandoffBundle`
- Minimal functions:
  - `capture_artifact_handoff()`
  - `import_cargo_messages()`
  - `build_artifact_manifest()`
  - `build_origin_receipt()`
  - `summarize_native_outputs()`
  - `diff_artifact_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `artifact-dir`
  - `build-analysis`
  - `build-script`
  - `ci`

# Compatibility story

- Must work on top of stable Cargo JSON messages first.
- May optionally import unstable `--artifact-dir` copied outputs, but must preserve that provenance explicitly.
- May optionally import session identifiers or replay context from build-analysis reports, but must still function when no persisted build history exists.
- Must distinguish `exact_from_cargo_messages`, `exact_from_artifact_dir_copy`, `conservative_reconstruction`, and `manual_review_required`.
- Should remain useful even if Cargo later stabilizes more output helpers, because downstream review, handoff, and diffing still live above the raw substrate.

# Conformance & fixtures

The fixture pack for this proposal should freeze:

- one single-binary copied-output case,
- one multi-target / multi-profile workspace case,
- one build-script-created final-artifact case that still needs explicit origin labeling,
- and one imported-session case that proves session IDs are optional but valuable.

Goldens should cover:

- `exact_from_cargo_messages`,
- `exact_from_artifact_dir_copy`,
- `conservative_reconstruction`,
- `manual_review_required`,
- `layout_drift_only`,
- `owner_changed`,
- and `session_linked`.

# Path to boring stability

- Start with promoted artifacts, not every transient file in target/build-dir.
- Keep origin vocabulary tiny and reviewable.
- Treat manual review as a first-class result when build-script uplift or copied-output inference is not enough.
- Let sidecar, SBOM, publish-identity, and docs/debug promises compose on top instead of expanding this crate until it becomes a release platform.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one build, normalize promoted artifacts into a stable manifest, record exactly where each fact came from, preserve optional build-session linkage, and export a diffable bundle that CI, packagers, or external build systems can consume without rescraping raw Cargo output.

# De-risk plan

1. Start with `compiler-artifact` and `build-finished` messages before adding imported session joins.
2. Support `--artifact-dir` only as an explicitly labeled enhancement, never as invisible truth.
3. Validate on one distro/package-manager handoff, one CI copied-output flow, and one build-dir-layout-v2 migration test.
4. Keep build-script-created final artifacts conservative until the upstream custom-final-artifact story is clearer.

# Non-goals

- Not a replacement for **P-0479 Cargo Artifact Sidecar Contract Kit**.
- Not a replacement for **P-0489 Cargo Build-Dir Consumer Transition Kit**.
- Not a release orchestration platform.
- Not a generic artifact store or CDN.
- Not a promise that all build-script-produced artifacts already have a stable upstream contract.

# Architecture & API sketch

```rust
pub struct ArtifactRecord {
    pub artifact_path: String,
    pub owner_package_id: String,
    pub target_kind: String,
    pub profile: String,
    pub origin_basis: String,
}

pub fn capture_artifact_handoff(root: &Path) -> Result<ArtifactHandoffBundle>;
pub fn build_artifact_manifest(bundle: &ArtifactHandoffBundle) -> Result<ArtifactManifest>;
pub fn build_origin_receipt(bundle: &ArtifactHandoffBundle) -> ArtifactOriginReceipt;
pub fn summarize_native_outputs(bundle: &ArtifactHandoffBundle) -> NativeOutputReport;
pub fn diff_artifact_bundles(old: &ArtifactHandoffBundle, new: &ArtifactHandoffBundle) -> ArtifactLayoutDiff;
```

Bundle draft:

- `artifact-handoff.lock`
- `artifact-manifest.json`
- `artifact-origin.receipt.json`
- `native-output.report.json`
- `handoff.receipt.json`
- `artifact-layout.diff.json`
- `notes.md`

# Security / safety model

- Treat Cargo output, copied artifacts, and filesystem scans as untrusted input.
- Support path redaction and package-name redaction for exported bundles.
- Never imply that a copied output is authoritative if the origin basis is only reconstructed.
- Preserve whether a fact depends on unstable Cargo features or imported report databases.
- Keep session IDs and command lines redactable for shared CI artifacts.

# Maintenance & governance plan

- Track Cargo external-tools JSON, `artifact-dir`, build-analysis session/report changes, and build-dir-layout transition work.
- Maintain fixtures for copied-output exactness, owner changes, build-script uplift ambiguity, and session-linked captures.
- Publish guidance for CI owners and packagers about when to trust exact manifests and when to fall back to manual review.
- Keep the manifest vocabulary compact rather than accreting release-policy semantics that belong in neighboring crates.

# Milestones

## 0.1
- artifact capture from stable Cargo messages
- artifact manifest
- handoff receipt

## 0.2
- origin receipt
- layout diffing
- optional `--artifact-dir` import

## 0.3
- build-analysis session linking
- build-script/native output summaries
- migration guidance for build-dir consumers

## 1.0
- stable bundle schema
- curated fixture corpus
- downstream adapters for CI and package-manager handoff

# Open questions

- What is the smallest durable origin vocabulary that stays honest about copied-output help, build-script uplift, and manual review?
- Which bundle facts should optionally join to build-analysis sessions without coupling the crate to unstable historical storage formats?
