---
id: P-0479
title: Cargo Artifact Sidecar Contract Kit — association locks, schema drift receipts, and ship-vs-local attachment bundles
status: idea
domains: [cargo, build-artifacts, sidecars, sbom, ci, packaging, interoperability]
last_reviewed: 2026-03-16
evidence:
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
---

# Problem

Cargo now has enough real artifact-adjacent substrate that “sidecars” are no longer hypothetical:

- external-tools JSON emits `compiler-artifact` messages with package/target/profile context and produced filenames,
- unstable `--artifact-dir` exists because downstream tools genuinely need a more predictable place to look for promoted outputs,
- unstable `-Z sbom` emits `<artifact>.cargo-sbom.json` files beside executable and linkable outputs,
- `CARGO_SBOM_PATH` gives build-time discovery of generated precursor sidecars,
- and Cargo changelog work is still tightening the sidecar-adjacent contract, including clarifying that SBOM package IDs are fully qualified.

But downstream consumers still do not get one boring answer to the practical questions:

- which companion files belong to which promoted artifact,
- whether that association is exact, conservative, or ambiguous,
- which sidecars should ship with the artifact versus stay local to CI or review,
- what schema/version or stability label applies to each sidecar family,
- and how to diff sidecar surface changes across builds without reimplementing Cargo-specific heuristics.

Today most teams still do some messy mixture of:

- parsing Cargo JSON,
- scanning target or artifact directories,
- guessing filename relationships,
- special-casing SBOM precursors,
- and hardcoding organization-local “ship these, ignore those” rules.

That means the missing crate is not another artifact manifest and not another SBOM generator.

The missing crate is an **artifact sidecar contract kit**: a narrower layer that freezes **artifact↔sidecar association truth, schema/stability truth, and shipping-policy truth** into reviewable artifacts other tools can depend on.

# Main judgment

A worthy crate here should provide other people with **one compact, diffable contract** for companion files.

That contract should answer:

1. which primary artifact a sidecar belongs to,
2. how the crate knows that,
3. whether the sidecar is safe/expected to ship,
4. which schema/version/stability lane the sidecar is in,
5. and what changed between two builds.

If the crate cannot say those five things, it is still just a directory scanner.

# What it provides

- `sidecar-contract.lock` — pins workspace/package scope, profile, toolchain, acquisition mode, and the artifact discovery mode used for association.
- `artifact-sidecar.index.json` — canonical mapping from promoted artifacts to attached sidecars, including association basis and ambiguity flags.
- `sidecar-schema.report.json` — schema ids, versions, stability class, consumer hints, and expected review posture for each sidecar family.
- `sidecar-attachment.receipt.json` — the ship/local/manual-review policy for each sidecar and the reason it received that classification.
- `sidecar-association.receipt.json` — where each mapping came from (`compiler_artifact_stream`, `artifact_dir_scan`, `env_hint`, `manual_mapping`) and whether the association is exact or approximate.
- `sidecar-surface.diff.json` — compare two builds and classify `sidecar_added`, `sidecar_removed`, `association_changed`, `schema_changed`, `attachment_policy_changed`, and `manual_review_required`.
- `cargo artifact-sidecars capture` — observe one build or imported output tree and emit a reviewable sidecar bundle.
- `cargo artifact-sidecars verify <bundle>` — re-check ship/local/manual-review policy and schema expectations.
- `cargo artifact-sidecars diff <old> <new>` — compare sidecar surfaces across toolchains, targets, or release profiles.
- `*.sidecars.zip` — portable bundle for CI, packagers, provenance tools, or downstream release systems.

# What the crate should provide other people

1. **A boring sidecar index** so consumers do not reverse-engineer naming conventions.
2. **Association exactness receipts** so downstream tools know whether a mapping is exact or guessed.
3. **Attachment policy receipts** so ship-with-artifact versus local-analysis decisions become reviewable.
4. **Schema/stability labels** so consumers know which sidecars can be automated against.
5. **A diff surface** so new or missing sidecars are treated like a release-surface change, not an incidental filesystem surprise.

# Persona / who it’s for

- CI and release engineers
- distro / package-manager maintainers
- authors of provenance, signing, or review-bundle tooling
- teams integrating Rust artifacts into larger non-Cargo build pipelines

# Users & user stories

- **Packager**: “Tell me which companion files should ship with this binary and why.”
- **CI owner**: “Show me when a build started emitting a new sidecar or stopped emitting an expected one.”
- **Tool author**: “Give me one sidecar bundle instead of asking me to infer relationships from raw Cargo messages.”
- **Reviewer**: “Was this sidecar association exact, or did the tool fall back to filename matching?”

# Prior art (and why it’s insufficient)

- **P-0471 Cargo Artifact Handoff Kit** addresses the broader question of “what outputs did this build produce”, but that lane is wider than the missing vocabulary for sidecar association and shipping policy.
- **P-0125 Cargo SBOM Precursor Workbench Kit** owns SBOM-specific precursor capture and transform-loss honesty, but it should not become the generic contract for all artifact companions.
- Cargo external-tools JSON exposes artifacts, but not a durable ship/local/manual-review contract for companion files.
- `-Z sbom` proves that sidecar conventions are real, but it does not define a general association or attachment layer.
- Local release scripts can scan directories, but they do not create a shared, versioned contract that other tools can implement.

What remains missing is the **sidecar-specific contract layer** above artifact production and below broader provenance or release-review systems.

# Design goals

1. **Sidecar-specific, not artifact-general** — stay narrower than artifact handoff.
2. **Association-honest** — preserve whether mapping came from stable Cargo messages, unstable copied-output structure, env hints, or manual mapping.
3. **Attachment-first** — ship/local/manual-review policy must be visible, not buried in notes.
4. **Schema-explicit** — sidecar families must carry schema/version/stability facts.
5. **Diff-friendly** — a changed sidecar surface should be reviewable like a changed package surface.

# MVP surface

- Minimal types:
  - `SidecarContractLock`
  - `ArtifactSidecarIndex`
  - `SidecarRecord`
  - `SidecarSchemaReport`
  - `SidecarAttachmentReceipt`
  - `SidecarAssociationReceipt`
  - `SidecarSurfaceDiff`
  - `ArtifactSidecarBundle`
- Minimal functions:
  - `capture_sidecar_bundle()`
  - `index_artifact_sidecars()`
  - `build_sidecar_schema_report()`
  - `build_attachment_receipt()`
  - `build_association_receipt()`
  - `diff_sidecar_bundles()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `sbom`
  - `artifact-dir`
  - `markdown`
  - `ci`

# Compatibility story

- Must work on top of stable Cargo JSON artifact messages first.
- May optionally import unstable signals like `--artifact-dir` placement or SBOM sidecars, but must preserve their provenance.
- Must distinguish `exact_association`, `conservative_association`, and `manual_review_required`.
- Should remain useful even if Cargo stabilizes additional sidecar families, because shipping policy and schema drift still need a shared receipt layer.

# Conformance & fixtures

The fixture pack for this proposal should freeze:

- one direct binary + SBOM/debug sidecar case,
- one multi-artifact split-sidecar case,
- one schema-version drift case,
- and one missing-expected-sidecar case that stays manual-review-required.

Goldens should cover:

- `ship_with_artifact`,
- `analysis_only`,
- `manual_review`,
- `exact_association`,
- `conservative_association`,
- `schema_changed`,
- and `sidecar_removed`.

# Path to boring stability

- Start SBOM-plus-symbol/debug sidecars first; resist inventing a huge taxonomy.
- Stabilize the attachment vocabulary before adding many adapters.
- Treat ambiguous association as a first-class outcome, not as an implementation failure to hide.
- Prefer explicit provenance and policy reasons over pretending every sidecar is equally automatable.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that capture one build, associate promoted artifacts with their discovered sidecars, classify those sidecars as ship/local/manual-review, label schema/stability facts, and export a diffable bundle for CI or packagers.

# De-risk plan

1. Start with SBOM precursor sidecars plus one debug/symbol sidecar family.
2. Refuse silent association when more than one plausible artifact owner exists.
3. Validate on one distro/package-manager handoff, one CI release flow, and one imported artifact-dir bundle.
4. Keep the first schema registry tiny and explicit.

# Non-goals

- Not a replacement for **P-0471 Cargo Artifact Handoff Kit**.
- Not an SBOM generator or CycloneDX/SPDX policy engine.
- Not a general artifact store.
- Not a promise that all sidecar families are already stable in Cargo.

# Architecture & API sketch

```rust
pub struct SidecarRecord {
    pub primary_artifact: String,
    pub sidecar_path: String,
    pub sidecar_kind: String,
    pub association_basis: String,
    pub attachment_policy: String,
}

pub fn capture_sidecar_bundle(root: &Path) -> Result<ArtifactSidecarBundle>;
pub fn index_artifact_sidecars(bundle: &ArtifactSidecarBundle) -> Result<ArtifactSidecarIndex>;
pub fn build_sidecar_schema_report(bundle: &ArtifactSidecarBundle) -> SidecarSchemaReport;
pub fn build_attachment_receipt(bundle: &ArtifactSidecarBundle) -> SidecarAttachmentReceipt;
pub fn diff_sidecar_bundles(old: &ArtifactSidecarBundle, new: &ArtifactSidecarBundle) -> SidecarSurfaceDiff;
```

Bundle draft:

- `sidecar-contract.lock`
- `artifact-sidecar.index.json`
- `sidecar-schema.report.json`
- `sidecar-attachment.receipt.json`
- `sidecar-association.receipt.json`
- `sidecar-surface.diff.json`
- `notes.md`

# Security / safety model

- Treat Cargo output and discovered sidecar files as untrusted input.
- Support path redaction and package-name redaction for exported bundles.
- Never imply a sidecar is safe to ship only because it exists next to an artifact.
- Keep unstable-source provenance visible so downstream tools can make conservative decisions.

# Maintenance & governance plan

- Track Cargo external-tools JSON, `artifact-dir`, SBOM precursor evolution, and any new sidecar-producing features.
- Keep the sidecar taxonomy compact and versioned.
- Maintain fixtures for ambiguous association, missing expected sidecars, and schema drift.
- Publish guidance for packagers and CI owners about advisory versus required sidecars.

# Milestones

## 0.1
- sidecar capture
- artifact-to-sidecar index
- attachment receipt

## 0.2
- schema report
- association receipt
- sidecar diffing

## 1.0
- stable bundle schema
- curated sidecar corpus
- downstream adapters for packagers, CI, and provenance tools

# Open questions

- What is the smallest durable sidecar taxonomy above SBOM and debug/symbol files?
- Which sidecar families deserve first-class schema ids versus just kind labels?
- How much ambiguity should the crate tolerate before requiring explicit manual mapping?

# Sources

- Cargo external tools JSON / `compiler-artifact` messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo unstable features (`artifact-dir`, `sbom`, `CARGO_SBOM_PATH`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (`-Z sbom` fully-qualified package IDs): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust in 2026 / supply-chain & SBOM direction: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
