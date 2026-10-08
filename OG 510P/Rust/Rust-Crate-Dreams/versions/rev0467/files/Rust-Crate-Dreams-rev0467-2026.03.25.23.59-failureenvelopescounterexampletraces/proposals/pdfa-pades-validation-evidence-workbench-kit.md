---
id: P-0385
title: PDF/A + PAdES Validation & Evidence Workbench Kit — profile locks, signature-scope diffs, and compliance-grade bundles
status: idea
domains: [documents, signatures, archives, compliance, validation, security, publishing]
last_reviewed: 2026-03-06
evidence:
  - https://verapdf.org/
  - https://docs.verapdf.org/validation/
  - https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf
  - https://www.etsi.org/deliver/etsi_ts/119100_119199/11914404/01.01.01_60/ts_11914404v010101p.pdf
  - https://ec.europa.eu/digital-building-blocks/DSS/webapp-demo/doc/dss-documentation.html
  - https://docs.rs/lopdf/latest/lopdf/
  - https://crates.io/crates/pdf_signing
---

# Problem

Rust already has PDF parsing/manipulation substrate and even early signing crates. Outside Rust, the ecosystem has mature validator surfaces: veraPDF for PDF/A and PDF/UA validation, ETSI PAdES requirements and test assertions, and the European Commission’s DSS stack for advanced signature creation and validation.

But day-to-day pain still happens at the seam between:

- **PDF/A archival conformance and actual incremental-update / signature workflows**,
- **PAdES level claims and what the validator or relying party really observes**,
- **byte-range scope, revision boundaries, timestamps, and detached trust material**,
- **tool disagreement across validators and policy profiles**,
- and **audit/debug evidence that is still passed around as giant PDFs, screenshots, and prose**.

The missing Rust contribution is not another full PDF renderer or trust-service suite. It is a **validation and evidence workbench** that normalizes validator outputs, models signature scope and revision boundaries, and emits compliance-grade bundles.

# What it provides

- `pdfsig.lock` — pins PDF/A profile, PAdES level/policy, validator set, timestamp/trust assumptions, and redaction rules.
- `pdfsig-irx` — neutral IR for document revisions, byte ranges, signature dictionaries, validation findings, and archival profile findings.
- `validator-normalizer` — imports and compares outputs from veraPDF, DSS, and native Rust checks.
- `scope-diff` — explains which bytes/revisions are covered, which are not, and why a signature or archival claim failed.
- `cargo pdf-evidence` — emits `*.pdfsigbundle.zip` with lockfile, normalized findings, policy notes, and minimal attachments.

# What the crate should provide other people

1. **A boring bundle for PDF/A/PAdES validation incidents**.
2. **Profile locks** so “valid PDF/A” or “PAdES-compliant” always means a pinned policy set.
3. **Scope diffs** for revision, timestamp, and byte-range questions.
4. **Validator normalization** across external tools and Rust-native checks.
5. **Evidence small enough for CI, audits, and vendor handoff.**

# Persona / who it’s for

- Developers building signing/archive workflows in Rust
- Compliance and records teams
- Digital-signature integrators
- Support engineers debugging validator disagreement

# Users & user stories

- **Implementer**: “Tell me whether the failure is archival profile, signature profile, timestamp material, or signature scope.”
- **Auditor**: “Capture a small evidence pack that proves which profile/policy was tested and what the tool actually said.”
- **Maintainer**: “Compare validator outputs over the same document without guessing which tool is more strict.”
- **Product team**: “Show whether this incremental update broke PDF/A, PAdES, both, or neither.”

# Prior art (and why it’s insufficient)

- veraPDF formalizes PDF/A and PDF/UA “shall” requirements as validation profiles.
- ETSI publishes PAdES baseline requirements and testing-conformance documents.
- DSS provides creation and validation support for advanced electronic signatures.
- Rust already has `lopdf` and early PDF signing crates.

What Rust still lacks is a **portable evidence layer** that glues profile locks, validator outputs, revision/scope analysis, and compact bundle generation into one boring tool.

# Design goals

1. **Policy-pinned** — every result must name the exact archival/signature profile.
2. **Revision-aware** — incremental updates and signature byte ranges are first-class.
3. **Validator-neutral** — normalize rather than re-implement everything.
4. **Audit-friendly** — bundles should be small, durable, and reproducible.
5. **Rust-complementary** — sit above `lopdf`/signing crates and external validators.

# MVP surface

- Minimal types: `PdfSigLock`, `PdfRevisionMap`, `ValidatorFinding`, `PdfSigBundle`
- Minimal functions:
  - `inspect_revisions()`
  - `normalize_validator_output()`
  - `diff_signature_scope()`
  - `write_bundle()`
- Feature flags:
  - `pdfa`
  - `pades`
  - `verapdf`
  - `dss`
  - `redaction`

# Compatibility story

- Uses external validators as adapters around one stable evidence schema.
- Allows pure-Rust structural inspection even when external tools are unavailable.
- Keeps policy/profile names explicit in locks and reports.
- Treats archival conformance and signature conformance as related but distinct surfaces.

# Conformance & fixtures

- Tiny fixtures for byte-range errors, timestamp omissions, incremental-update surprises, attachment/metadata profile problems, and invalid profile claims.
- Goldens for “same PDF, different validator output”.
- Public corpus with synthetic signed/archive documents safe to share.
- Policy fixtures for PDF/A profile selection and PAdES baseline levels.

# Path to boring stability

- Stabilize the lockfile, revision map schema, and normalized finding model first.
- Start with PDF/A + baseline PAdES rather than every trust-service standard.
- Prefer tool adapters over re-implementing ETSI/ISO logic in core.
- Keep bundles compact and document-focused.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that inspect PDF revisions and signature scope, import validator findings from veraPDF/DSS, pin exact profile assumptions, and emit compact `*.pdfsigbundle.zip` artifacts.

# De-risk plan

1. Start with normalization and scope analysis.
2. Keep trust-policy and certificate-validation details modular.
3. Use synthetic public fixtures first.
4. Treat archival and signing checks as separate layers joined by one bundle format.

# Non-goals

- Not a full PDF renderer.
- Not a complete CA/TSA/trust-service product.
- Not a replacement for veraPDF or DSS.
- Not a general PDF sanitizer (that is a different problem space).

# Architecture & API sketch

```rust
pub struct PdfSigLock {
    pub pdfa_profile: String,
    pub pades_profile: String,
    pub validator_set: Vec<String>,
    pub trust_policy: String,
}

pub fn inspect_revisions(input: &[u8]) -> Result<PdfRevisionMap>;
pub fn normalize_validator_output(tool: &str, input: &[u8]) -> Result<Vec<ValidatorFinding>>;
pub fn diff_signature_scope(map: &PdfRevisionMap) -> ScopeDiff;
```

Bundle draft: `pdfsig.lock`, `revision-map.json`, `findings.json`, `scope-diff.json`, `policy-notes.json`, `attachments/`, `notes.md`.

# Security / safety model

- Treat all documents and validator outputs as sensitive by default.
- Support structural summaries without shipping full PDFs when possible.
- Record exact validator versions and profile names in every bundle.
- Make omitted trust material explicit to avoid false confidence.

# Maintenance & governance plan

- Keep the core about locks, normalized findings, revision/scope maps, and bundle format.
- Version validator adapters separately if needed.
- Publish a public synthetic conformance corpus.
- Resist scope creep into generic PDF editing suites.

# Milestones

## 0.1
- revision inspection
- profile lockfile
- normalized validator findings

## 0.2
- scope diffs
- DSS adapter
- public fixture corpus

## 1.0
- stable `*.pdfsigbundle.zip`
- documented compatibility policy
- broader policy/profile coverage

# Open questions

- Which subset of DSS outputs should be normalized first?
- How much trust-policy detail belongs in the stable lockfile?
- What is the minimum safe bundle when the PDF itself cannot be shared?

# Sources

- veraPDF: https://verapdf.org/
- veraPDF validation docs: https://docs.verapdf.org/validation/
- ETSI EN 319 142-1: https://www.etsi.org/deliver/etsi_en/319100_319199/31914201/01.02.01_60/en_31914201v010201p.pdf
- ETSI TS 119 144-4: https://www.etsi.org/deliver/etsi_ts/119100_119199/11914404/01.01.01_60/ts_11914404v010101p.pdf
- DSS documentation: https://ec.europa.eu/digital-building-blocks/DSS/webapp-demo/doc/dss-documentation.html
- `lopdf`: https://docs.rs/lopdf/latest/lopdf/
- `pdf_signing`: https://crates.io/crates/pdf_signing
