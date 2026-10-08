---
id: P-0355
title: FITS 4.0 + WCS + VOTable Interop & Evidence Kit — coordinate-aware validation, semantic diffs, and archive-grade astronomy bug bundles
status: idea
domains: [astronomy, science-data, archival-formats, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://fits.gsfc.nasa.gov/fits_standard.html
  - https://fits.gsfc.nasa.gov/fits_wcs.html
  - https://www.ivoa.net/documents/VOTable/
  - https://docs.rs/fitsio
  - https://crates.io/crates/wcs
  - https://crates.io/crates/votable
---

# Problem

Rust can already read FITS files and increasingly handle WCS and VOTable data, but astronomy interoperability failures often happen across layers:

- a FITS file is technically valid yet carries broken or ambiguous WCS metadata,
- a VOTable export loses semantic links or coordinate assumptions from upstream FITS products,
- archive or pipeline changes preserve bytes while changing coordinate interpretation,
- and bug reports still rely on entire files or screenshots instead of minimized, coordinate-aware evidence.

The missing Rust contribution is a **coordinate-aware interop and evidence kit** spanning FITS, WCS, and VOTable workflows, not another isolated parser.

# What it provides

- `astro-ir` — canonical Rust IR for HDUs, selected header cards, WCS projections/axes, and related tabular metadata.
- `astro-profile` — lockfiles that pin supported FITS conventions, WCS assumptions, and export/import expectations.
- `fits-check` — structural and convention-aware checks over headers, HDUs, checksums, and selected registered conventions.
- `wcs-check` — semantic checks for coordinate-system completeness and transform plausibility.
- `astro-diff` — diffs such as “same pixels, changed sky coordinates”, “table export lost unit/UCD metadata”, or “header convention drift”.
- `cargo astro-evidence` — emit `*.fitsbundle.zip` bundles for archive ingest bugs, pipeline regressions, or cross-tool debugging.

# What the crate should provide other people

1. **A boring default artifact for astronomy-format interoperability bugs**.
2. **Pinned convention and coordinate assumptions** instead of tacit archive folklore.
3. **Semantic diffs** that distinguish data-payload stability from coordinate or metadata drift.
4. **Small-share bug bundles** for public archive, instrument-pipeline, or catalogue-export issues.
5. **One place to connect FITS images/tables, WCS semantics, and VOTable exports** in Rust-native tooling.

# Persona / who it’s for

- Astronomy archive and pipeline engineers
- Rust developers building scientific I/O tooling
- Observatory software maintainers
- Catalogue / table export tool authors
- QA teams pinning coordinate semantics across releases

# Users & user stories

- **Archive maintainer**: “Show me whether the regression is in FITS structure, WCS keywords, or VOTable export semantics.”
- **Pipeline engineer**: “Diff two products semantically and tell me whether coordinates changed even though the image payload did not.”
- **Catalogue exporter**: “Prove which metadata survived or was lost moving from FITS tables to VOTable.”
- **Support engineer**: “Send a small coordinate-aware bug bundle instead of the full instrument product.”

# Prior art (and why it’s insufficient)

- NASA / IAU maintain the official **FITS 4.0** standard and WCS materials.
- IVOA maintains the current **VOTable** recommendation surface.
- Rust has substrate in `fitsio`, `fitsrs`, `wcs`, and `votable`.
- But there is still no boring-default Rust crate family for **convention locks + WCS-aware validation + semantic diffs + portable evidence bundles**.

# Design goals

1. **Coordinate-aware** — payload bytes alone are not enough.
2. **Convention-aware** — record exactly which FITS conventions and WCS papers are assumed.
3. **Format-bridge aware** — track loss or reinterpretation across FITS ↔ VOTable flows.
4. **Archive-friendly** — useful for long-lived reproducible artifacts.
5. **Small-share first** — bundles should work with excerpted HDUs or table subsets.

# MVP surface

- Minimal types: `AstroProduct`, `WcsSummary`, `AstroProfile`, `AstroReport`, `AstroDiffFinding`
- Minimal functions:
  - `inspect_fits()`
  - `check_wcs()`
  - `compare_exports()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `fits`
  - `wcs`
  - `votable`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target core FITS 4.0 structures plus a bounded set of common WCS expectations.
- The crate should complement existing Rust I/O crates rather than replace them.
- VOTable coverage should begin with structural and metadata-preservation checks, not full VO-service ecosystems.
- Archive-specific or mission-specific convention packs can remain optional.

# Conformance & fixtures

- Tiny public FITS image and table files with pinned WCS metadata.
- Goldens for missing WCS axes, altered reference values, checksum/convention drift, and VOTable export loss.
- Excerpt fixtures that preserve problematic headers without needing full raw data products.
- Table fixtures that prove loss or reinterpretation of units, UCDs, or coordinate metadata.

# Path to boring stability

- Stabilize IR and findings vocabulary before broadening convention support.
- Keep early WCS checks focused on explainable structural/semantic issues.
- Freeze bundle layout only after it works for archive ingest and cross-tool debugging.
- Add richer convention packs only once the neutral core is solid.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A library and CLI that inspect a FITS product, summarize WCS semantics, optionally compare a related VOTable export, and emit a compact `*.fitsbundle.zip` that makes coordinate or export regressions reproducible.

# De-risk plan

1. Start with public fixtures and header/WCS checks before broader astronomy semantics.
2. Limit convention support to a few high-value cases first.
3. Treat VOTable as an interop boundary, not as an excuse to absorb the whole VO stack.
4. Prefer metadata excerpts over large science payloads.

# Non-goals

- Not an astronomy analysis suite.
- Not a VO service framework.
- Not a full visualization stack.
- Not a replacement for mature FITS or WCS libraries.

# Architecture & API sketch

```rust
pub struct AstroReport {
    pub profile_id: String,
    pub fits_findings: Vec<Finding>,
    pub wcs_findings: Vec<Finding>,
    pub export_findings: Vec<Finding>,
    pub diffs: Vec<AstroDiffFinding>,
}

pub fn check_wcs(product: &AstroProduct) -> Result<Vec<Finding>>;
pub fn compare_exports(base: &AstroProduct, vot: &AstroProduct) -> Result<Vec<Finding>>;
```

Bundle draft: `profile.toml`, `headers.json`, `wcs.json`, `table.json`, `export.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat FITS headers and tables as untrusted inputs.
- Default to excerpting headers, WCS summaries, and tiny table subsets.
- Record exact convention/profile assumptions in each bundle.
- Support masking or omission for proprietary mission metadata where needed.

# Maintenance & governance plan

- Keep core focused on IRs, findings, and bundle formats.
- Version optional convention packs separately.
- Maintain a small public corpus with known coordinate and export edge cases.
- Avoid overcommitting to mission-specific astronomy semantics in core.

# Milestones

## 0.1
- FITS inspector
- WCS checker
- bundle writer

## 0.2
- export-loss checks
- semantic diffs
- optional convention packs

## 1.0
- stable `*.fitsbundle.zip`
- public fixture corpus
- documented policy for convention/profile drift

# Open questions

- Which FITS conventions should be first-class in MVP?
- How much WCS plausibility checking belongs in core versus adapters?
- What minimum excerpt preserves enough semantics for reproducible archive bugs?

# Sources

- FITS standard: https://fits.gsfc.nasa.gov/fits_standard.html
- FITS WCS information: https://fits.gsfc.nasa.gov/fits_wcs.html
- FITS conventions registry: https://fits.gsfc.nasa.gov/fits_registry.html
- VOTable recommendation: https://www.ivoa.net/documents/VOTable/
- `fitsio`: https://docs.rs/fitsio
- `wcs`: https://crates.io/crates/wcs
- `votable`: https://crates.io/crates/votable
