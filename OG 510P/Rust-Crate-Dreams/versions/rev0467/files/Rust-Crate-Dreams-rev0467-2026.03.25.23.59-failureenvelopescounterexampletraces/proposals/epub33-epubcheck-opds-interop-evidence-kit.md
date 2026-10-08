---
id: P-0332
title: EPUB 3.3 + EPUBCheck + OPDS 2.0 Interop & Evidence Kit — profile-pinned publications, explainable validation failures, and replayable reading-system bug bundles
status: idea
domains: [publishing, ebooks, libraries, epub, opds, xml, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://www.w3.org/TR/epub-33/
  - https://w3c.github.io/epub-specs/epub33/rs/
  - https://www.w3.org/publishing/epubcheck/releases/
  - https://www.w3.org/publishing/epubcheck/
  - https://specs.opds.io/
  - https://crates.io/crates/epub
  - https://docs.rs/opds/latest/opds/
---

# Problem

Rust can now read and manipulate EPUBs, but the painful failures in real e-book pipelines are rarely “could not unzip the file.” They usually live at the seam between **package structure, reading-system behavior, and catalog distribution**:

- EPUB files that mostly render but still fail official conformance checks,
- OPDS catalogs that advertise publications in ways real clients interpret differently,
- accessibility, navigation, and resource-manifest problems that are hard to explain to publishers,
- regressions that only show up in one reader or after a packaging tweak,
- and support escalations that still move around as giant sample files, screenshots, and email threads instead of deterministic evidence.

The worthy crate contribution is an **adapter-first interop and evidence kit** that wraps EPUBCheck, pins publication/catalog profiles, and turns reader-facing failures into replayable, redactable artifacts.

# What it provides

- `publication-ir` — a canonical Rust IR for package metadata, manifest/spine/nav relationships, media types, accessibility metadata, landmarks, page-list state, and linked acquisition/catalog metadata.
- `epub-profile` — lockfiles pinning EPUB 3.3 assumptions, optional reader-policy constraints, accessibility checks, and organization-specific packaging conventions.
- `epubcheck-adapter` — normalized invocation and parsing of EPUBCheck results into stable Rust findings and severity vocabularies.
- `opds-bridge` — support for OPDS 2.0 feed/publication documents with explicit linkage back to publication identities and distribution metadata.
- `reading-smoke` — deterministic resource/path checks and a minimal “will common readers even find the thing they need?” workflow.
- `publication-diff` — semantic diffs: “nav document disappeared”, “cover image media-type changed”, “a11y metadata regressed”, “catalog link no longer matches package identifier”.
- `cargo epub-evidence` — emit `*.epubbundle.zip` for CI, publisher/vendor handoff, or library support cases.

# What the crate should provide other people

1. **A boring default for EPUB debugging** instead of unpacking zip files by hand and diffing XML.
2. **One place to pin packaging assumptions** across production, QA, and catalog distribution.
3. **Explainable validation output** above raw EPUBCheck line-oriented messages.
4. **A bridge between publications and catalogs** so OPDS drift is diagnosable in the same artifact.
5. **Portable bug bundles** that can be shared without shipping an entire publishing stack.

# Persona / who it’s for

- Digital publishing engineers
- Reading-system and library-platform developers
- Accessibility QA teams
- Distribution/catalog engineers
- Rust developers building e-book tooling

# Users & user stories

- **Publisher engineer**: “Show me exactly why this EPUB passes our local smoke tests but fails the pinned EPUBCheck/reader profile.”
- **Library vendor**: “Diff the OPDS entry and the EPUB package and explain which identifiers or acquisition links drifted.”
- **QA lead**: “Redact author/content details, but keep the packaging bug reproducible.”
- **Reader-app maintainer**: “Replay a failing publication against a stable findings vocabulary in CI.”

# Prior art (and why it’s insufficient)

- EPUB 3.3 and EPUB Reading Systems 3.3 are explicit about package and reader conformance.
- EPUBCheck is the official conformance checker and should be wrapped, not ignored.
- OPDS has an official specifications hub and active OPDS 2.0 draft work.
- Rust has `epub`, `lib-epub`, and an `opds` crate.
- But there is still no boring-default Rust crate family for **profile pinning + EPUBCheck normalization + OPDS/package seam debugging + replayable evidence bundles**.

# Design goals

1. **Adapter-first** — use official validation surfaces instead of re-implementing everything from scratch.
2. **Publication/catalog continuity** — package and distribution metadata should be debugged together.
3. **Semantic diagnostics over raw XML churn** — findings should describe publishing problems, not just parser failures.
4. **Profile explicitness** — especially important because EPUB is stable while OPDS 2.0 is still draft-shaped.
5. **Implementation neutrality** — useful whether the wider stack is Java, JS, Python, or Rust.

# MVP surface

- Minimal types: `PublicationSnapshot`, `CatalogSnapshot`, `EpubProfile`, `ValidationReport`, `PublicationDiff`
- Minimal functions:
  - `load_epub()`
  - `load_opds()`
  - `run_epubcheck()`
  - `verify_publication()`
  - `diff_publications()`
  - `write_bundle()`
- Feature flags:
  - `epub`
  - `opds`
  - `serde`
  - `redaction`
  - `epubcheck`

# Compatibility story

- MVP should target **EPUB 3.3**, **EPUB Reading Systems 3.3**, and the current **EPUBCheck 5.x** line first.
- OPDS support should be explicit that **2.0 is draft-based** and therefore must always be pinned by profile/version notes.
- The crate should complement reader apps, distribution platforms, and QA scripts rather than trying to replace them.
- MVP should intentionally avoid becoming a full reader engine or EPUB editor.

# Conformance & fixtures

- Tiny fixture publications covering nav documents, media overlays, metadata, accessibility declarations, remote resources, and common packaging mistakes.
- Positive/negative fixtures for manifest/spine drift, media-type mismatches, broken links, and catalog/package identifier mismatches.
- Optional adapters for EPUBCheck JSON/text output normalization.
- Golden semantic verdicts for accessibility and distribution-facing regressions.

# Path to boring stability

- First stabilize the IR and finding vocabulary.
- Then prove that wrapped EPUBCheck results stay stable enough to diff meaningfully across versions.
- Freeze bundle layout only after redaction preserves enough context for support/debugging.
- Keep OPDS assumptions strictly profile-pinned and version-noted.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that ingest one EPUB 3.3 package plus an optional OPDS record, run a pinned EPUBCheck validation, normalize the results into stable findings, diff the package against a prior known-good snapshot, and emit a redactable `*.epubbundle.zip`.

# De-risk plan

1. Start with packaging and validation; leave true rendering behavior out of core MVP.
2. Wrap EPUBCheck rather than re-implementing official conformance logic.
3. Treat OPDS as an adapter layer first, because its 2.0 surface is still draft-based.
4. Prove usefulness on small public-domain fixture books before taking on real publisher corpora.

# Non-goals

- Not a reader application.
- Not a full EPUB editor or authoring suite.
- Not a catalog/distribution platform.

# Architecture & API sketch

```rust
pub struct ValidationReport {
    pub profile_id: String,
    pub packaging_findings: Vec<Finding>,
    pub catalog_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_publication(profile: &EpubProfile, publication: &PublicationSnapshot) -> ValidationReport;
pub fn run_epubcheck(profile: &EpubProfile, publication: &PublicationSnapshot) -> Result<ValidationReport>;
```

Bundle draft: `profile.toml`, `publication/`, `catalog.json`, `epubcheck/report.json`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact manuscript text and commercially sensitive metadata where required.
- Bound archive expansion and external-resource fetching by default.
- Record the exact validator version used.
- Preserve enough path and identifier context to keep failures reproducible after redaction.

# Maintenance & governance plan

- Keep the core focused on IRs, adapters, and finding vocabularies.
- Version profile packs separately from the bundle schema.
- Encourage public-domain and synthetic fixtures for regression testing.
- Treat draft-spec support as explicit and revocable unless pinned in a profile.

# Milestones

## 0.1
- EPUB IR
- EPUBCheck adapter
- basic bundle writer

## 0.2
- OPDS bridge
- semantic diffs
- redaction support

## 1.0
- Stable `*.epubbundle.zip`
- CI-ready regression corpus
- documented adapter policy for validator/version drift

# Open questions

- How much reader-system behavior should be represented without building a reader?
- Should accessibility checks remain entirely validator-wrapped, or add Rust-native semantic checks above them?
- How aggressively should OPDS draft support be pinned and versioned in profiles?

# Sources

- EPUB 3.3: https://www.w3.org/TR/epub-33/
- EPUB Reading Systems 3.3: https://w3c.github.io/epub-specs/epub33/rs/
- EPUBCheck releases: https://www.w3.org/publishing/epubcheck/releases/
- EPUBCheck project: https://www.w3.org/publishing/epubcheck/
- OPDS specs hub: https://specs.opds.io/
- `epub`: https://crates.io/crates/epub
- `opds`: https://docs.rs/opds/latest/opds/
