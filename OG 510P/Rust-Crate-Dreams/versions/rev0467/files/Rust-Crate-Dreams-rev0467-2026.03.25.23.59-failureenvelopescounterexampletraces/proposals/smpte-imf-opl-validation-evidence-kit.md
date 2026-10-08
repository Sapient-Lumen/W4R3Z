---
id: P-0424
title: SMPTE IMF Package + OPL Validation & Evidence Kit — package locks, application receipts, and deliverable-safe diffs
status: idea
domains: [media, video, packaging, archival, conformance, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://www.smpte.org/standards/st2067
  - https://www.smpte.org/technology-reports-downloads
  - https://www.smpte.org/blog/new-and-revised-smpte-standards
  - https://docs.rs/imferno-core/latest/imferno_core/
  - https://lib.rs/crates/imferno-core
---

# Problem

Interoperable Master Format is mature enough that the harder operational problem is no longer “can we parse a CPL?” The failures that still cost real time and money happen above raw parsing:

- a package is “valid enough” for one workflow but not another,
- an **Output Profile List (OPL)** or application constraint is assumed rather than pinned,
- QC teams, transcode teams, and archive teams talk past one another because they have different implicit deliverable assumptions,
- and debugging a bad package still means emailing screenshots, XML fragments, and ad hoc validation logs.

Rust now has real IMF validation substrate. The missing crate is a **package-and-evidence kit** that pins application/profile assumptions, validation findings, and deliverable transforms into one portable review artifact.

# What it provides

- `imf.lock` — pins ST 2067 application assumptions, referenced constraints, OPL/profile overlays, and validation policy.
- `package.receipt.json` — records AssetMap, PKL, CPL, sidecar references, and essence/header digests.
- `deliverable.receipt.json` — records the exact OPL/profile assumptions used for a downstream deliverable check.
- `finding-set.json` — normalized validator findings with severity, affected asset, and policy origin.
- `interop.corpus/` — tiny packages for core constraints, application constraints, OPL edge cases, and sidecars.
- `cargo imf-evidence` — emits `*.imfbundle.zip` with manifests, findings, digests, and safe review notes.

# What the crate should provide other people

1. **A boring handoff artifact for IMF package investigations**.
2. **Application/profile locks** that make validation scope explicit.
3. **Deliverable-facing receipts** for OPL and downstream packaging assumptions.
4. **A Rust-native normalized finding model** that QC, archival, and transcode tools can all reuse.
5. **Portable evidence** for incident review and CI gating.

# Persona / who it’s for

- media pipeline and mastering engineers
- QC / validation tool builders
- archive and preservation teams
- broadcast / postproduction pipeline maintainers

# Users & user stories

- **QC engineer**: “Package the exact reasons this IMF set failed our validation policy without sharing all the source essence.”
- **Pipeline maintainer**: “Show whether a mismatch is core-package breakage, application-profile drift, or OPL/deliverable-policy drift.”
- **Archive reviewer**: “See which findings are preservation-significant versus workflow-local.”
- **Tool builder**: “Emit one normalized finding format instead of custom XML and text logs.”

# Prior art (and why it’s insufficient)

- SMPTE ST 2067 is a large, real standards family.
- OPL and application profiles are established parts of IMF workflows.
- `imferno-core` provides Rust parsing and validation substrate.

What Rust still lacks is a **portable evidence layer** that turns package state, profile assumptions, and validator output into one reviewable artifact other tools can depend on.

# Design goals

1. **Constraint-explicit** — application and OPL assumptions must be pinned.
2. **Finding-normalized** — validator output should be comparable across tools.
3. **Deliverable-aware** — downstream output assumptions matter and must be receipted.
4. **Review-safe** — allow sharing metadata-heavy evidence without shipping all media essence.
5. **Policy-separable** — distinguish standard violations from local house rules.

# MVP surface

- Minimal types: `ImfLock`, `PackageReceipt`, `DeliverableReceipt`, `FindingSet`, `ImfBundle`
- Minimal functions:
  - `inspect_package()`
  - `validate_against_policy()`
  - `capture_opl_receipt()`
  - `diff_findings()`
  - `write_bundle()`
- Feature flags:
  - `core`
  - `opl`
  - `sidecars`
  - `app-profiles`
  - `redaction`

# Compatibility story

- Treats ST 2067 core constraints as the normative base.
- Treats application constraints, OPL processing, and local policies as pinned overlays.
- Allows ingestion of findings from existing validators instead of forcing one validation engine.
- Keeps transcoding/rendering systems out of scope.

# Conformance & fixtures

- Tiny packages for AssetMap/PKL/CPL consistency, missing/duplicate assets, sidecar references, and OPL-related checks.
- Goldens for policy-vs-standard finding classification.
- Corpora showing the same package under different application or deliverable assumptions.
- Redacted example bundles safe for support tickets and CI.

# Path to boring stability

- Stabilize `imf.lock` and `finding-set.json` before broad adapter work.
- Start with metadata and header-level evidence capture.
- Keep policy packs separate from the core bundle schema.
- Avoid becoming a full media processing stack.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that inspect one IMF package, run a narrow validation policy, normalize findings, and emit a review-safe bundle with package and deliverable receipts.

# De-risk plan

1. Start with metadata-only evidence capture.
2. Treat OPL and sidecar layers as explicit overlays, not always-on assumptions.
3. Reuse existing Rust validation substrate wherever possible.
4. Publish a tiny public fixture set instead of chasing every application at once.

# Non-goals

- Not a media transcoder.
- Not a full IMF authoring suite.
- Not a replacement for house QC systems.
- Not a DRM or signing framework.

# Architecture & API sketch

```rust
pub struct ImfLock {
    pub st2067_profile: String,
    pub application_profile: Option<String>,
    pub opl_profile: Option<String>,
    pub validation_policy_digest: String,
}

pub fn inspect_package(path: &std::path::Path) -> Result<PackageReceipt>;
pub fn validate_against_policy(pkg: &PackageReceipt, policy: &ValidationPolicy) -> FindingSet;
pub fn capture_opl_receipt(pkg: &PackageReceipt, opl: &OplSpec) -> Result<DeliverableReceipt>;
pub fn write_bundle(bundle: &ImfBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `imf.lock`, `package.receipt.json`, `deliverable.receipt.json`, `finding-set.json`, `asset-digests.json`, `notes.md`.

# Security / safety model

- Support redaction of essence payloads while preserving digests and structural evidence.
- Keep local facility policies separate from normative-standard findings.
- Mark findings that may affect preservation or deliverable integrity distinctly from naming/house-style issues.
- Enable safe sharing of validator evidence without full package disclosure.

# Maintenance & governance plan

- Track ST 2067 application/profile revisions explicitly.
- Keep policy packs data-driven.
- Maintain a small public corpus covering high-confusion package and OPL failures.
- Avoid tying the core format to a single validator implementation.

# Milestones

## 0.1
- `imf.lock`
- package receipt
- normalized finding set

## 0.2
- deliverable / OPL receipts
- policy classification
- redacted example bundles

## 1.0
- stable `*.imfbundle.zip`
- cross-validator finding importers
- CI-friendly package gates

# Open questions

- What is the smallest finding schema that still preserves useful validator nuance?
- Which OPL assumptions belong in the core lockfile versus optional deliverable overlays?
- How much essence/header detail is needed for reproducible bug reports without over-sharing media assets?

# Sources

- SMPTE ST 2067 family overview: https://www.smpte.org/standards/st2067
- SMPTE technology reports downloads (including OPL-related reports): https://www.smpte.org/technology-reports-downloads
- SMPTE recent standard/revision activity: https://www.smpte.org/blog/new-and-revised-smpte-standards
- `imferno-core` docs: https://docs.rs/imferno-core/latest/imferno_core/
- `imferno-core` package overview: https://lib.rs/crates/imferno-core
