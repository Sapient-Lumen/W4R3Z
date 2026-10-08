---
id: P-0360
title: VCF 4.5 + BCF 2.2 + CSI/Tabix Interop & Evidence Kit — annotation-aware diffs, index locks, and replayable variant-exchange bundles
status: idea
domains: [bioinformatics, genomics, file-formats, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://samtools.github.io/hts-specs/
  - https://samtools.github.io/hts-specs/VCFv4.5.pdf
  - https://crates.io/crates/noodles
  - https://crates.io/crates/noodles-vcf
  - https://crates.io/categories/science%3A%3Abioinformatics
---

# Problem

Rust has strong HTS format substrate, but day-to-day interoperability failures for variant data still happen at the seam between:

- textual VCF and binary BCF encodings,
- CSI/Tabix indexing expectations and actual region-query behavior,
- INFO/FORMAT/header declarations versus body records,
- tool-specific normalization of alleles, phasing, missing values, and annotations,
- and bug reports that share giant files instead of compact, reproducible evidence.

The missing Rust contribution is not another parser. It is a **variant-exchange workbench** that can pin headers, indexes, query regions, and semantic expectations in portable bundles.

# What it provides

- `variant-ir` — stable IR for headers, records, query slices, index metadata, and normalized annotations.
- `variant-lock` — lockfiles pinning VCF/BCF version, header invariants, index type, contig ordering, and annotation expectations.
- `variant-check` — validation of headers, field declarations, index compatibility, region-query behavior, and encoding drift.
- `variant-diff` — semantic diffs such as “same variants, different header semantics”, “region query mismatch”, or “annotation loss during conversion”.
- `variant-replay` — portable replay of region queries and format conversions.
- `cargo variant-evidence` — emit `*.variantbundle.zip` for CI, pipeline regressions, or tool-vendor bug reports.

# What the crate should provide other people

1. **A boring artifact for variant-format interoperability bugs**.
2. **Pinned expectations for headers, indexes, and annotations**.
3. **Region-query replay** without redistributing full production cohorts.
4. **Explainable diffs between VCF and BCF surfaces**.
5. **A neutral bridge from HTS crates to evidence-grade QA workflows**.

# Persona / who it’s for

- Bioinformatics pipeline authors
- Variant-calling and annotation tool maintainers
- Clinical/research data-platform teams
- Rust genomics tool builders
- QA engineers validating conversions or region-query behavior

# Users & user stories

- **Pipeline maintainer**: “Show me whether this regression is in the header, index, or records.”
- **Tool author**: “Replay the exact failing region query in CI and diff the semantics, not just bytes.”
- **Data steward**: “Share a compact, redacted repro bundle instead of a giant dataset.”
- **Annotation engineer**: “Catch loss or reinterpretation of INFO/FORMAT fields during conversion.”

# Prior art (and why it’s insufficient)

- HTS specs clearly define VCF/BCF/index surfaces and current VCF 4.5 is published.
- Rust has deep format substrate in `noodles` and its component crates.
- But Rust still lacks a boring-default crate for **header/index locks + semantic conversion diffs + query replay + portable evidence bundles**.

# Design goals

1. **Semantics over bytes** — focus on variants, annotations, and query behavior rather than raw file diffs.
2. **Index-aware** — treat CSI/Tabix compatibility as first-class.
3. **Reproducible** — support tiny redacted slices and synthetic fixtures.
4. **Header-conscious** — many real bugs are declaration/body mismatches, not parser failures.
5. **Pipeline-friendly** — outputs must be deterministic and CI-usable.

# MVP surface

- Minimal types: `VariantLock`, `VariantSlice`, `VariantReport`, `VariantDiffFinding`, `IndexSnapshot`
- Minimal functions:
  - `snapshot_header()`
  - `check_index()`
  - `run_region_query()`
  - `diff_variant_surfaces()`
  - `write_bundle()`
- Feature flags:
  - `vcf`
  - `bcf`
  - `csi`
  - `tabix`
  - `redaction`

# Compatibility story

- MVP should target VCF 4.5 / BCF 2.2 semantics with explicit downgrade support for common older files where practical.
- The crate should complement HTS reader/writer crates rather than replace them.
- Query replay should work against local files first, with remote/htsget adapters optional later.
- Bundle format should remain useful even for tiny synthetic slices.

# Conformance & fixtures

- Tiny VCF/BCF pairs with deliberate header/body inconsistencies.
- CSI and Tabix cases for region boundary behavior and contig ordering mismatches.
- Conversion goldens where annotations, phasing, or missing values may drift.
- Redacted slices exercising multiallelic sites, symbolic alleles, gVCF-style records, and edge-case INFO/FORMAT declarations.

# Path to boring stability

- Stabilize header/index/report schemas before broadening remote adapters.
- Keep early region-query semantics intentionally narrow and explainable.
- Freeze the bundle layout only after it works for both synthetic and real-world slices.
- Add richer annotation packs after the base lockfile and diff model prove durable.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 5/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 26/30**

# Minimum lovable MVP

A library and CLI that snapshot a VCF/BCF header and index, replay one or more region queries, compare the results against a pinned lockfile, and emit a compact `*.variantbundle.zip`.

# De-risk plan

1. Start with small region-query and header consistency checks.
2. Normalize semantic findings before chasing full byte-for-byte equivalence.
3. Use redacted and synthetic fixtures to avoid privacy and scale issues.
4. Keep remote-access support out of MVP.

# Non-goals

- Not a new variant caller.
- Not a full annotation engine.
- Not a replacement for `bcftools` or HTSlib.
- Not a petabyte-scale cohort management platform.

# Architecture & API sketch

```rust
pub struct VariantReport {
    pub lock_id: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<VariantDiffFinding>,
}

pub fn snapshot_header(input: &[u8], format: VariantFormat) -> Result<HeaderSnapshot>;
pub fn run_region_query(lock: &VariantLock, region: Region, path: &std::path::Path) -> Result<VariantReport>;
```

Bundle draft: `profile.toml`, `header.txt`, `index.json`, `query-regions.bed`, `records.ndjson`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat sample names, contigs, and annotations as potentially sensitive.
- Default to redaction and slicing rather than bundling full files.
- Record exact spec/version and index assumptions.
- Keep normalized findings deterministic and diff-friendly.

# Maintenance & governance plan

- Keep the core centered on header/index semantics, query replay, diffs, and bundle layout.
- Version remote-access or ecosystem-specific adapters separately.
- Grow a public corpus of tiny but semantically difficult fixtures.
- Avoid absorbing full downstream analysis or annotation workflows.

# Milestones

## 0.1
- header snapshot
- index checks
- bundle writer

## 0.2
- region-query replay
- semantic diffs
- conversion checks

## 1.0
- stable `*.variantbundle.zip`
- public fixture corpus
- documented compatibility policy for spec and annotation/profile packs

# Open questions

- Which annotation fields deserve special semantic treatment in the neutral core?
- How much of region-query behavior should be preserved verbatim versus normalized?
- Should tabix and CSI live in one lockfile type or sibling lockfile variants?

# Sources

- HTS format specifications overview: https://samtools.github.io/hts-specs/
- VCF 4.5 specification: https://samtools.github.io/hts-specs/VCFv4.5.pdf
- `noodles`: https://crates.io/crates/noodles
- `noodles-vcf`: https://crates.io/crates/noodles-vcf
- crates.io bioinformatics category: https://crates.io/categories/science%3A%3Abioinformatics
