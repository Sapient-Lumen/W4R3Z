---
id: P-0335
title: LAS 1.4/1.5 + LAZ 1.4 + COPC Interop & Evidence Kit — profile-pinned point clouds, semantic header diffs, and reproducible spatial bug bundles
status: idea
domains: [geospatial, lidar, pointclouds, las, laz, copc, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://community.asprs.org/leadership-restricted/leadership-content/public-documents/standards
  - https://asprslas.org/
  - https://downloads.rapidlasso.de/doc/LAZ_Specification_1.4_R1.pdf
  - https://copc.io/
  - https://copc.io/copc-specification-1.0.pdf
  - https://docs.rs/las
  - https://crates.io/crates/copc-rs
  - https://docs.rs/las-crs
---

# Problem

Rust can already read and write LAS-family point clouds, but the expensive interoperability failures live above raw parsing:

- files that technically open but drift in CRS/VLR semantics, scale/offset assumptions, or extra-bytes usage,
- LAZ/COPC conversions that change header meaning or break partial-read expectations,
- cloud-hosted point clouds that only fail under range-requested or windowed access,
- and support escalations that still pass around huge binary files without a compact, reproducible explanation of what changed.

The worthy crate contribution is a **point-cloud interop and evidence kit** that pins LAS/LAZ/COPC assumptions, explains header/VLR-level drift semantically, and packages replayable, portable bug bundles.

# What it provides

- `pointcloud-ir` — canonical Rust IR for headers, point formats, scale/offset, bounds, CRS/VLR state, extra bytes, classification summaries, and chunk/index metadata.
- `cloud-profile` — lockfiles pinning LAS version expectations, LAZ/COPC packaging assumptions, CRS policies, and ingest/export rules.
- `header-verify` — semantic checks for header/VLR/EVLR consistency, CRS expectations, extra-bytes descriptions, and point-format compatibility.
- `copc-replay` — deterministic capture/replay for COPC hierarchy navigation and partial-read/range-request scenarios.
- `pointcloud-diff` — semantic diffs: “scale/offset changed”, “WKT CRS disappeared”, “point format upgraded”, “extra bytes schema drifted”, “COPC hierarchy no longer matches header summary”.
- `cargo pointcloud-evidence` — emit `*.pointbundle.zip` for conversion debugging, QA, or provider handoff.

# What the crate should provide other people

1. **A boring way to debug point-cloud interoperability** without redistributing giant datasets.
2. **Profile pinning** for the exact LAS/LAZ/COPC assumptions a workflow depends on.
3. **Semantic diffs** that talk like point-cloud metadata, not raw binary bytes.
4. **Cloud-access replay** for COPC and range-oriented failures.
5. **A neutral layer** above local tools, cloud object stores, and conversion pipelines.

# Persona / who it’s for

- Lidar/photogrammetry platform engineers
- Geospatial data providers
- Conversion-tool authors
- QA and archive teams for point-cloud data
- Rust developers building geospatial infrastructure

# Users & user stories

- **Conversion engineer**: “Show me what changed semantically when we rewrote LAS into COPC.”
- **Provider**: “Replay the exact partial-read failure without shipping the full source cloud.”
- **Archive maintainer**: “Diff the headers and CRS metadata between two deliveries.”
- **Integrator**: “Pin which LAS/COPC features our pipeline promises to preserve.”

# Prior art (and why it’s insufficient)

- LAS has active official revision work and current published lines.
- LAZ 1.4 and COPC 1.0 define concrete packaging/compression/indexing expectations.
- Rust has `las`, `las-crs`, and `copc-rs` substrate.
- But there is still no boring-default Rust crate family for **profile pinning + semantic header/VLR diffs + COPC replay + portable evidence bundles**.

# Design goals

1. **Metadata-first** — most interoperability pain is about meaning, not just bytes.
2. **Cloud-aware** — COPC partial-read and hierarchy semantics are first-class.
3. **CRS explicitness** — spatial-reference policy should never be implicit.
4. **Package-bound scope** — focus on interchange and QA, not rendering/analysis.
5. **Implementation neutrality** — useful whether the surrounding tools are PDAL, QGIS, custom services, or Rust CLIs.

# MVP surface

- Minimal types: `PointCloudSnapshot`, `CopcSnapshot`, `CloudProfile`, `ValidationReport`, `PointCloudDiff`
- Minimal functions:
  - `inspect_las()`
  - `inspect_copc()`
  - `verify_profile()`
  - `replay_ranges()`
  - `diff_snapshots()`
  - `write_bundle()`
- Feature flags:
  - `las`
  - `laz`
  - `copc`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **LAS 1.4R16 semantics** and **COPC 1.0 over LAZ 1.4** first.
- It should observe the emerging **LAS 1.5** line as a future compatibility profile rather than assume full support on day one.
- It should complement existing conversion tools and viewers rather than replace them.
- MVP should intentionally avoid becoming a full visualization or analytics stack.

# Conformance & fixtures

- Tiny LAS/LAZ fixtures covering point-format variants, CRS presence/absence, extra bytes, and header inconsistencies.
- COPC fixtures exercising hierarchy traversal, range reads, and metadata summaries.
- Positive/negative examples for CRS/VLR drift, scale/offset changes, and chunk/index corruption scenarios.
- Golden semantic verdicts for conversions between LAS, LAZ, and COPC snapshots.

# Path to boring stability

- First stabilize the snapshot IR and finding vocabulary.
- Then prove range-replay and redaction are useful on small public datasets.
- Freeze bundle layout only after binary sampling and metadata summaries preserve reproducibility.
- Keep LAS 1.5 support explicitly versioned and gated.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that inspect one LAS/LAZ/COPC file, verify it against a pinned profile, diff it against a previous snapshot, optionally replay a few COPC range-read operations, and emit a redactable `*.pointbundle.zip`.

# De-risk plan

1. Start with header/VLR semantics before touching full point-stream analysis.
2. Keep COPC replay read-only and bounded in MVP.
3. Treat LAS 1.5 as an explicit future profile, not an assumed baseline.
4. Use public sample clouds and synthetic fixtures first.

# Non-goals

- Not a viewer or renderer.
- Not a full spatial-analysis engine.
- Not a new point-cloud storage service.

# Architecture & API sketch

```rust
pub struct ValidationReport {
    pub profile_id: String,
    pub header_findings: Vec<Finding>,
    pub range_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_profile(profile: &CloudProfile, snapshot: &PointCloudSnapshot) -> ValidationReport;
pub fn replay_ranges(snapshot: &CopcSnapshot, windows: &[RangeWindow]) -> Result<Vec<ReplayFinding>>;
```

Bundle draft: `profile.toml`, `snapshot.json`, `copc/`, `ranges/`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Never copy full point payloads into bundles by default; prefer metadata summaries and bounded samples.
- Redact internal URLs or delivery paths for cloud-hosted datasets.
- Bound range-replay sizes and decompression behavior.
- Record exact profile and parser versions for reproducibility.

# Maintenance & governance plan

- Keep binary-format parsing separated from semantic policy checks.
- Version CRS/policy packs explicitly.
- Encourage small public fixtures and vendor-donated redacted incidents.
- Treat tool-specific quirks as adapter data unless they recur across ecosystems.

# Milestones

## 0.1
- LAS/COPC snapshot IR
- header verification
- bundle writer

## 0.2
- semantic diffs
- COPC range replay
- redaction support

## 1.0
- Stable `*.pointbundle.zip`
- regression fixtures across common point formats
- explicit compatibility matrix for LAS/LAZ/COPC support

# Open questions

- How much LAS 1.5 support belongs in core versus a future companion crate?
- Should CRS normalization be adapter-based or fully native in MVP?
- What is the smallest binary sample needed to preserve reproducibility?

# Sources

- ASPRS standards listing: https://community.asprs.org/leadership-restricted/leadership-content/public-documents/standards
- LAS specification site: https://asprslas.org/
- LAZ 1.4 specification: https://downloads.rapidlasso.de/doc/LAZ_Specification_1.4_R1.pdf
- COPC overview: https://copc.io/
- COPC 1.0 specification: https://copc.io/copc-specification-1.0.pdf
- `las`: https://docs.rs/las
- `copc-rs`: https://crates.io/crates/copc-rs
- `las-crs`: https://docs.rs/las-crs
