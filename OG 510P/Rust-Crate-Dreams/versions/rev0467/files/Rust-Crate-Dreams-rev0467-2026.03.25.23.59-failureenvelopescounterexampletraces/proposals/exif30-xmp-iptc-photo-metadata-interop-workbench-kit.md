---
id: P-0414
title: Exif 3.0 + XMP + IPTC Photo Metadata Interop Workbench Kit — mapping receipts, normalization diffs, and redaction-safe image metadata bundles
status: idea
domains: [imaging, metadata, media, archives, photography, privacy, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://cipa.jp/std/documents/e/Exif3.0-Overview_E.pdf
  - https://www.cipa.jp/e/std/history_sec.html
  - https://www.iso.org/standard/75163.html
  - https://iptc.org/standards/photo-metadata/iptc-standard/
  - https://iptc.org/std/photometadata/documentation/mappingguidelines/
  - https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2025.1.html
  - https://docs.rs/kamadak-exif
  - https://docs.rs/xmp_toolkit
  - https://docs.rs/rexiv2
  - https://docs.rs/crate/image/latest/source/CHANGES.md
---

# Problem

Photo metadata is one of those ecosystems that looks solved until you try to preserve meaning across real files. Exif 3.0 is current, XMP remains the standardized extensible layer, IPTC’s photo metadata standard and mapping guidance are active, and Rust now has multiple ways to read pieces of the stack.

But practical failures still happen at the seam between:

- **embedded Exif tags and the XMP projection of those fields**,
- **legacy IPTC/IIM habits and XMP/IPTC Core+Extension semantics**,
- **camera-native timestamps/orientation/location and editorial/rights metadata**,
- **read support and honest write/update semantics**,
- and **“we preserved the metadata” claims that never say what was normalized, dropped, duplicated, or guessed.**

The missing Rust contribution is not one more metadata parser. It is a **loss-aware interop workbench** for mapping receipts, normalization diffs, redaction-safe bundles, and explicit round-trip limits across Exif/XMP/IPTC families.

# What it provides

- `photo-meta.lock` — pins Exif/XMP/IPTC revision assumptions, mapping tables, namespace packs, and container-format expectations.
- `mapping-receipt` — field-by-field record of direct copies, normalized transformations, conflicts, and dropped values.
- `metadata-diff` — structured explanation of how two files differ semantically, not just bytewise.
- `redaction-bundle` — portable artifact for privacy review, newsroom/legal review, or bug reproduction.
- `cargo photo-meta-evidence` — emits `*.photometabundle.zip` with locks, extracted metadata, mappings, and notes.

# What the crate should provide other people

1. **An honest answer to “what metadata survived?”**
2. **A stable mapping layer** across Exif, XMP, and IPTC families.
3. **Privacy-aware redaction workflows** for geolocation, identifiers, and rights-sensitive fields.
4. **Semantic metadata diffs** for archives, DAM systems, and processing pipelines.
5. **A Rust-native coordination artifact** above multiple partial readers/writers.

# Persona / who it’s for

- digital-asset and DAM engineers
- newsroom/photo-agency tooling maintainers
- archive/library preservation teams
- privacy/compliance reviewers for image pipelines

# Users & user stories

- **Pipeline maintainer**: “Show exactly which fields changed when we rewrote this JPEG to WebP.”
- **Archivist**: “Preserve the editorial and rights semantics, not just the easy camera tags.”
- **Privacy reviewer**: “Redact location/creator IDs while keeping the rest reproducible.”
- **Developer**: “Get an explainable mapping receipt instead of guessing how fields were projected.”

# Prior art (and why it’s insufficient)

- Exif, XMP, and IPTC all have real active standards/guidance.
- Rust has pure and FFI-backed metadata readers plus broader image-format support.
- IPTC publishes mapping guidance across standards.

What Rust still lacks is a **portable artifact layer** for version-pinned mapping rules, conflict/loss reporting, semantic diffs, and redaction-safe evidence.

# Design goals

1. **Loss-explicit** — every mapping should say copy, normalize, duplicate, drop, or infer.
2. **Container-aware** — file format matters because not every carrier supports the same metadata families equally.
3. **Privacy-safe** — redaction should be first-class, not a post-hoc hack.
4. **Namespace-honest** — preserve XMP namespace details and IPTC schema versions explicitly.
5. **Tool-neutral** — work above existing parser/writer crates.

# MVP surface

- Minimal types: `PhotoMetaLock`, `MappingReceipt`, `MetadataDiff`, `RedactionBundle`, `PhotoMetaBundle`
- Minimal functions:
  - `extract_metadata()`
  - `apply_mapping_rules()`
  - `diff_metadata()`
  - `redact_bundle()`
  - `write_bundle()`
- Feature flags:
  - `exif`
  - `xmp`
  - `iptc`
  - `redaction`
  - `container-profiles`

# Compatibility story

- Works above pure-Rust or FFI-backed metadata extraction crates.
- Treats container-format support as an explicit profile layer.
- Can ingest broader image crate metadata extraction as partial evidence.
- Does not require a universal writer capable of perfect round-trips.

# Conformance & fixtures

- Goldens for timestamp, orientation, GPS, rights, creator, and caption field conflicts.
- Corpora for JPEG, TIFF, PNG, WebP, and HEIF/HEIC where supported.
- Redaction fixtures showing safe removal or hashing of sensitive fields.
- Mapping-table fixtures pinned to a specific IPTC guideline revision.

# Path to boring stability

- Stabilize mapping receipts before ambitious write-back support.
- Keep semantic diffs small and human-reviewable.
- Treat unsupported writes as first-class facts, not silent omission.
- Resist scope creep into a full DAM or raw-processing platform.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that extract Exif/XMP/IPTC metadata, apply pinned mapping rules, emit explicit conflict/loss receipts, support privacy redaction, and package results into compact `*.photometabundle.zip` artifacts.

# De-risk plan

1. Start read-only with extraction + mapping receipts.
2. Add redaction and semantic diff before write/update workflows.
3. Keep container-specific support matrices explicit.
4. Pilot with public sample images and archive/newsroom scenarios.

# Non-goals

- Not a raw image editor.
- Not a full DAM system.
- Not a universal metadata writer with perfect round-trips.
- Not a schema.org / web SEO metadata platform.

# Architecture & API sketch

```rust
pub struct PhotoMetaLock {
    pub exif_revision: String,
    pub xmp_revision: String,
    pub iptc_revision: String,
    pub mapping_pack: String,
}

pub fn extract_metadata(path: &std::path::Path) -> Result<ExtractedMetadata>;
pub fn apply_mapping_rules(meta: &ExtractedMetadata, lock: &PhotoMetaLock) -> MappingReceipt;
pub fn diff_metadata(a: &ExtractedMetadata, b: &ExtractedMetadata) -> MetadataDiff;
```

Bundle draft: `photo-meta.lock`, `extracted.json`, `mapping-receipt.json`, `metadata-diff.json`, `redaction-report.json`, `notes.md`.

# Security / safety model

- Default redaction support for GPS, serial numbers, creator identifiers, contact fields, and embedded rights-sensitive data.
- Preserve enough evidence to debug mappings without redistributing private media unnecessarily.
- Distinguish extracted facts from inferred normalizations.
- Avoid silent write-back or deletion in library defaults.

# Maintenance & governance plan

- Track Exif/XMP/IPTC revisions and mapping packs explicitly.
- Publish a compact cross-format sample corpus.
- Keep the core centered on extraction, mapping, diffs, and redaction.
- Avoid binding the project to one metadata backend.

# Milestones

## 0.1
- `photo-meta.lock`
- extraction model
- mapping receipt schema

## 0.2
- semantic diff engine
- redaction bundles
- public sample corpus

## 1.0
- stable `*.photometabundle.zip`
- compatibility policy for mapping-pack revisions
- CI-friendly loss reporting

# Open questions

- How should the crate represent multiple conflicting values that are all “technically present” across metadata families?
- Which inferred normalizations deserve first-class semantics versus free-form notes?
- How much container-specific knowledge belongs in the core versus optional profile packs?

# Sources

- Exif 3.0 overview: https://cipa.jp/std/documents/e/Exif3.0-Overview_E.pdf
- CIPA standards history: https://www.cipa.jp/e/std/history_sec.html
- ISO 16684-1:2019 (XMP): https://www.iso.org/standard/75163.html
- IPTC Photo Metadata Standard: https://iptc.org/standards/photo-metadata/iptc-standard/
- IPTC mapping guidelines: https://iptc.org/std/photometadata/documentation/mappingguidelines/
- IPTC Photo Metadata 2025.1: https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2025.1.html
- `kamadak-exif`: https://docs.rs/kamadak-exif
- `xmp_toolkit`: https://docs.rs/xmp_toolkit
- `rexiv2`: https://docs.rs/rexiv2
- `image` changelog: https://docs.rs/crate/image/latest/source/CHANGES.md
