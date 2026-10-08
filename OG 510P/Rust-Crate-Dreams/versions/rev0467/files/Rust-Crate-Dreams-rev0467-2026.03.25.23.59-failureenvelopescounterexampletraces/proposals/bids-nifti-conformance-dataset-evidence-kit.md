---
id: P-0333
title: BIDS + NIfTI Conformance & Dataset Evidence Kit — profile-pinned neuroimaging datasets, explainable validator findings, and replayable curation bundles
status: idea
domains: [science, neuroimaging, datasets, bids, nifti, reproducibility, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://bids.neuroimaging.io/standards/bids_specification/index.html
  - https://bids-standard.github.io/bids-validator/
  - https://github.com/bids-standard/bids-validator
  - https://nifti.nimh.nih.gov/nifti-1/
  - https://nifti.nimh.nih.gov/nifti-2.html
  - https://crates.io/crates/nifti
  - https://docs.rs/nifti
---

# Problem

Neuroimaging teams increasingly automate BIDS curation, but the frustrating failures happen in the gap between **dataset layout rules, sidecar semantics, and image-header reality**:

- datasets that almost validate except for opaque path or metadata findings,
- NIfTI headers whose affine/orientation or extension details create secondary validator failures,
- dataset revisions that shuffle filenames, JSON sidecars, and TSVs in ways humans struggle to diff semantically,
- and support/debug artifacts that still involve giant datasets, PHI-sensitive names, and ad hoc “can you run the validator again?” loops.

Rust already has meaningful NIfTI substrate, but the missing epic crate contribution is a **dataset conformance and evidence layer** that wraps validator output, inspects image/header semantics, and packages reproducible, redactable curation evidence.

# What it provides

- `dataset-ir` — canonical Rust IR for BIDS dataset structure, subject/session naming, modality-specific file groups, JSON sidecars, TSV tables, and provenance notes.
- `image-ir` — NIfTI-aware IR for headers, dimensionality, orientation/affine metadata, intent codes, and extension presence.
- `bids-profile` — lockfiles pinning the target BIDS release, local lab conventions, required metadata subsets, and optional validator/version expectations.
- `validator-adapter` — stable parsing and normalization for BIDS Validator findings into Rust-native verdicts with line/file provenance.
- `header-verify` — NIfTI-focused checks that can explain image-level causes behind higher-level dataset failures.
- `dataset-diff` — semantic diffs: “task event TSV changed schema”, “sidecar field vanished”, “subject label renamed”, “affine/header inconsistency introduced”.
- `cargo bids-evidence` — emit `*.bidsbundle.zip` for curation review, CI, or cross-lab support.

# What the crate should provide other people

1. **A boring artifact for dataset-validation incidents** instead of manually shipping huge datasets.
2. **One place to pin BIDS assumptions** for a lab, pipeline, or repository.
3. **Explainable findings** that connect validator output to concrete files and headers.
4. **Semantic diffs** for dataset revisions instead of raw directory churn.
5. **Redactable reproducibility** so subject identifiers can be scrubbed while keeping bugs reproducible.

# Persona / who it’s for

- Neuroimaging platform engineers
- Research software engineers
- Data-curation teams
- Repository/archive maintainers
- Rust developers building scientific data tooling

# Users & user stories

- **Curation engineer**: “Tell me why this dataset fails under the pinned BIDS profile and which NIfTI header fields are contributing.”
- **Lab maintainer**: “Diff this dataset revision against the last accepted submission in semantics, not just filenames.”
- **Repository operator**: “Redact subject IDs and site names but keep the validator failure reproducible.”
- **Pipeline author**: “Run this in CI before uploading a terabyte-scale dataset.”

# Prior art (and why it’s insufficient)

- BIDS has an active specification and an official validator surface.
- NIfTI-1.1 and NIfTI-2 remain the crucial image container standards underneath many BIDS datasets.
- Rust has a real `nifti` crate and adjacent scientific-data infrastructure.
- But there is still no boring-default Rust crate family for **BIDS profile pinning + validator normalization + NIfTI-aware semantic checks + replayable dataset evidence bundles**.

# Design goals

1. **Dataset-first** — BIDS directory/file semantics are first-class, not an afterthought to image parsing.
2. **Header-aware diagnostics** — validator findings should be connectable to NIfTI reality.
3. **Privacy-conscious reproducibility** — redaction must be part of the artifact model.
4. **Version explicitness** — BIDS release and validator version must always be visible.
5. **Implementation neutrality** — useful whether the rest of the stack is Python, MATLAB, shell, or Rust.

# MVP surface

- Minimal types: `DatasetSnapshot`, `ImageSnapshot`, `BidsProfile`, `ValidationReport`, `DatasetDiff`
- Minimal functions:
  - `scan_dataset()`
  - `inspect_nifti()`
  - `run_validator()`
  - `verify_dataset()`
  - `diff_datasets()`
  - `write_bundle()`
- Feature flags:
  - `nifti`
  - `nifti2`
  - `tables`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target the current public BIDS spec line and official validator surface first.
- It should work best with **NIfTI-1.1** immediately, while treating **NIfTI-2** support as explicit and test-backed.
- It should complement existing curation pipelines rather than replacing BIDS Validator.
- MVP should intentionally avoid becoming a full scientific workflow engine.

# Conformance & fixtures

- Tiny synthetic BIDS datasets covering MRI/EEG-style directory patterns, sidecar requirements, and TSV edge cases.
- Positive/negative fixtures for subject/session naming, metadata inheritance, sidecar drift, and image/header inconsistencies.
- Small NIfTI fixtures covering affine/orientation issues, dimensionality mismatches, and extension handling.
- Optional adapters for validator JSON/text outputs with golden normalized verdicts.

# Path to boring stability

- First stabilize the dataset/header IRs and finding vocabulary.
- Then prove redaction preserves enough structural information for reproducibility.
- Freeze bundle layout only after validator normalization remains stable across several releases.
- Keep modality-specific rule packs separate and additive.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A CLI and library that scan one BIDS dataset, inspect its NIfTI files, normalize official validator findings into stable Rust-native verdicts, diff the dataset against a previous accepted snapshot, and emit a redactable `*.bidsbundle.zip`.

# De-risk plan

1. Start with offline local datasets only.
2. Wrap the official validator instead of trying to replace it.
3. Keep the first semantic checks tight: header sanity, sidecar linkage, and naming/profile conformance.
4. Use synthetic datasets before touching any real lab data.

# Non-goals

- Not a neuroimaging analysis framework.
- Not a replacement for BIDS Validator.
- Not a repository ingestion platform.

# Architecture & API sketch

```rust
pub struct ValidationReport {
    pub profile_id: String,
    pub validator_findings: Vec<Finding>,
    pub header_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_dataset(profile: &BidsProfile, dataset: &DatasetSnapshot) -> ValidationReport;
pub fn inspect_nifti(path: &std::path::Path) -> Result<ImageSnapshot>;
```

Bundle draft: `profile.toml`, `dataset-map.json`, `images/`, `validator/report.json`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact subject/site identifiers and free-text metadata by default where requested.
- Never copy voxel payloads into bundles unless explicitly asked; prefer headers and minimal structural evidence.
- Bound file scanning and decompression behavior.
- Record exact validator and ruleset versions for reproducibility.

# Maintenance & governance plan

- Keep modality-specific rule packs versioned and optional.
- Separate header parsing from dataset semantics so the core stays tractable.
- Encourage redacted synthetic and public challenge datasets as fixtures.
- Treat validator adapters as compatibility layers with explicit version tests.

# Milestones

## 0.1
- Dataset scanner
- NIfTI header inspection
- validator adapter and bundle writer

## 0.2
- semantic dataset diffs
- redaction support
- modality-specific profile packs

## 1.0
- Stable `*.bidsbundle.zip`
- CI-ready conformance fixtures
- clear support matrix for BIDS + validator + NIfTI variants

# Open questions

- How much NIfTI-2 support belongs in core MVP versus a companion crate?
- Should TSV/schema checks remain generic or become modality-aware early?
- What is the smallest useful redaction layer that still preserves reproducibility?

# Sources

- BIDS specification hub: https://bids.neuroimaging.io/standards/bids_specification/index.html
- BIDS Validator web app: https://bids-standard.github.io/bids-validator/
- BIDS Validator repository: https://github.com/bids-standard/bids-validator
- NIfTI-1.1: https://nifti.nimh.nih.gov/nifti-1/
- NIfTI-2: https://nifti.nimh.nih.gov/nifti-2.html
- `nifti`: https://crates.io/crates/nifti
- `nifti` docs: https://docs.rs/nifti
