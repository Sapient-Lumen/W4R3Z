---
id: P-0213
title: DICOMweb + DIMSE Interop & Evidence Kit
status: idea
domains: [healthcare, imaging, protocols, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://www.dicomstandard.org/using/dicomweb
  - https://dicom.nema.org/medical/dicom/current/output/html/part18.html
  - https://www.dicomstandard.org/using/dicomweb/restful-structure
  - https://crates.io/crates/dicom
  - https://github.com/Enet4/dicom-rs
  - https://crates.io/crates/dicom-test-files
---

# Problem

Rust has a solid base for **DICOM file/object** manipulation, but teams building PACS/VNA gateways, viewers, and pipelines often need:

- DICOMweb (QIDO-RS/WADO-RS/STOW-RS) behavior validated against multiple servers,
- deterministic normalization for payloads/metadata (so diffs are meaningful),
- a safe way to capture **PHI-sensitive** failures as shareable artifacts.

Interop debugging today is largely ad-hoc (curl scripts + private captures), and reusable fixtures are scarce.

# What it provides

A crate + CLI that standardizes **DICOMweb/DIMSE interoperability** tests as portable evidence.

- `dicomlab` CLI
  - run QIDO/WADO/STOW scenario suites against endpoints
  - optional DIMSE proxy mode (test a DIMSE SCP behind a DICOMweb facade)
  - emit `*.dicombundle.zip` (redaction-first repro bundles)

- Rust library
  - HTTP client + auth adapters (mTLS, bearer, basic; pluggable)
  - canonicalization of responses (sorted JSON metadata, stable multipart boundaries, hash references for bulk)
  - dataset readers/writers powered by `dicom-rs` modules (for parsing/validation)

# Bundle format

`dicombundle.zip`:
- `manifest.json` (suite id, endpoint, auth mode, redaction policy)
- `requests/` (sanitized request summaries)
- `responses/` (normalized metadata + status; bulk data referenced by hashes)
- `fixtures/` (input instances or links to `dicom-test-files` ids)
- `report.json` (per-transaction verdicts; conformance notes)

# Scorecard (initial)

- Impact: 4
- Neglectedness: 3
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4

# Minimum lovable MVP (4–8 weeks)

1. Support QIDO-RS SearchForStudies/Series/Instances + basic WADO-RS metadata retrieval.
2. Canonicalize metadata and emit `dicombundle.zip` + `dicomlab diff`.
3. Redaction profiles: remove patient identifiers; hash UIDs; strip private tags.
4. Fixture pack using `dicom-test-files` + a tiny synthetic generator.

# De-risk plan

- Start with metadata-only flows (avoid bulk pixel data early).
- Validate redaction pipeline with an explicit “PHI leak test” suite.

# Non-goals

- Implementing a full PACS/VNA.
- Replacing medical device certification—this is an engineering interop workbench.
