---
id: P-0411
title: OpenDocument ODF + OpenFormula Conformance Workbench Kit — package locks, formula receipts, and modality-aware office-document evidence
status: idea
domains: [documents, office, interoperability, validation, xml, packaging, formulas]
last_reviewed: 2026-03-06
evidence:
  - https://www.oasis-open.org/2025/12/03/oasis-approves-open-document-format-odf-v1-4-standard-marking-20-years-of-interoperable-document-innovation/
  - https://docs.oasis-open.org/office/OpenDocument/v1.4/os/v1.4-os.html
  - https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part2-packages/OpenDocument-v1.4-os-part2-packages.html
  - https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part4-formula/OpenDocument-v1.4-os-part4-formula.html
  - https://docs.rs/spreadsheet_ods
  - https://docs.rs/calamine
  - https://crates.io/crates/open-document
---

# Problem

OOXML gets plenty of ecosystem attention, but OpenDocument remains a major open document family and has just advanced again with ODF 1.4. The standard spans package structure, schema, and OpenFormula semantics across text, spreadsheet, and presentation modalities.

Rust already has meaningful pieces here—`spreadsheet_ods` and `calamine` for ODS, and `open-document` as an early general-format effort—but the painful failures still happen at the seam between:

- **ZIP/package structure, manifest/signature metadata, and per-modality XML semantics**,
- **spreadsheet formula meaning and what downstream tools actually recalculate**,
- **text/spreadsheet/presentation variants that share one family name but not one practical contract**,
- **partial Rust support for one modality and silent assumptions about the rest**,
- and **document interop debugging that still revolves around “LibreOffice opens it” instead of a portable receipt.**

The missing Rust contribution is not another one-off ODS writer. It is a **conformance workbench** for package locks, modality-aware receipts, formula/profile findings, and shareable evidence bundles.

# What it provides

- `odf.lock` — pins ODF version, package/schema/formula assumptions, modality targets, and compatibility overlays.
- `package-receipt` — normalized record of package members, manifests, mimetype, signatures, and key XML parts.
- `formula-receipt` — explicit record of OpenFormula usage, unsupported function surfaces, recalculation assumptions, and drift findings.
- `modality-findings` — tells you whether the issue is package-level, schema-level, spreadsheet-formula-level, or modality-specific support drift.
- `cargo odf-evidence` — emits `*.odfbundle.zip` with locks, receipts, findings, and notes.

# What the crate should provide other people

1. **A boring artifact for OpenDocument interoperability bugs**.
2. **Explicit separation of package, schema, and formula layers**.
3. **Modality-aware conformance receipts** for text, spreadsheet, and presentation families.
4. **Partial-support honesty** instead of pretending one ODS library solves ODF.
5. **A Rust-native review/CI layer** above existing format crates.

# Persona / who it’s for

- Rust document-processing tool authors
- data and reporting pipelines touching ODS/ODT/ODP
- archival and migration teams
- QA engineers validating document compatibility

# Users & user stories

- **Spreadsheet tool author**: “Show me whether the breakage is package structure, formula semantics, or unsupported styling/content.”
- **Migration engineer**: “Pin the exact ODF assumptions this pipeline expects before converting or mutating files.”
- **Archival engineer**: “Produce a compact evidence bundle that shows a document is structurally sound and where support is partial.”
- **Reviewer**: “Compare two generated ODS files without diffing giant XML trees by hand.”

# Prior art (and why it’s insufficient)

- ODF 1.4 is now a current OASIS standard family with explicit package, schema, and formula parts.
- Rust already has useful ODS-centric crates and early more general efforts.
- Existing Rust support is strongest in the spreadsheet corner and much thinner across the rest of the family.

What Rust still lacks is a **family-aware artifact model** for package locks, formula receipts, and modality-specific conformance findings.

# Design goals

1. **Layer-honest** — package, schema, and formula layers must stay separate.
2. **Modality-aware** — text, spreadsheet, and presentation should not be flattened into one pretend surface.
3. **Partial-support explicit** — missing coverage is data, not embarrassment.
4. **Archive-friendly** — bundles should help long-lived validation and review workflows.
5. **Incrementally adoptable** — useful first for ODS, then extensible.

# MVP surface

- Minimal types: `OdfLock`, `PackageReceipt`, `FormulaReceipt`, `OdfFinding`, `OdfBundle`
- Minimal functions:
  - `inspect_package()`
  - `inspect_formula_surface()`
  - `diff_document_semantics()`
  - `write_bundle()`
- Feature flags:
  - `ods`
  - `odt`
  - `odp`
  - `formula`
  - `signatures`

# Compatibility story

- Works above existing ODS-focused crates and raw ZIP/XML processing.
- Supports offline validation of generated or captured documents.
- Keeps modality-specific coverage explicit.
- Can start with ODS receipts without pretending full-family support already exists.

# Conformance & fixtures

- Goldens for malformed package structure, mimetype/manifest drift, unsupported formula functions, and modality-specific missing parts.
- Tiny corpora for ODS, ODT, and ODP sanity cases.
- Fixtures for “structurally valid package, semantically drifting formula content”.
- Public mini-corpus suitable for CI and archive checks.

# Path to boring stability

- Stabilize the lockfile and package/formula receipt schemas before broader transforms.
- Start with ODS and package-level validation.
- Add richer modality coverage only when the core artifact model is stable.
- Resist drift into becoming a full office suite.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that inspect ODF packages, pin package/schema/formula assumptions, emit modality-aware findings, and produce compact `*.odfbundle.zip` artifacts.

# De-risk plan

1. Start with ODS + package validation.
2. Add formula receipts before ambitious content transforms.
3. Model ODT/ODP as partial-support modalities with explicit coverage markers.
4. Pilot in generated-reporting pipelines and archive checks.

# Non-goals

- Not an office editor.
- Not a full rendering/layout engine.
- Not a replacement for LibreOffice.
- Not a one-shot file converter for every proprietary office format.

# Architecture & API sketch

```rust
pub struct OdfLock {
    pub odf_version: String,
    pub modalities: Vec<String>,
    pub package_profile: String,
    pub formula_profile: Option<String>,
}

pub fn inspect_package(path: &std::path::Path) -> Result<PackageReceipt>;
pub fn inspect_formula_surface(doc: &PackageReceipt) -> Result<FormulaReceipt>;
pub fn diff_document_semantics(a: &PackageReceipt, b: &PackageReceipt) -> Vec<OdfFinding>;
```

Bundle draft: `odf.lock`, `package-receipt.json`, `formula-receipt.json`, `findings.json`, `notes.md`.

# Security / safety model

- Support path and content redaction for confidential documents.
- Keep formula and package evidence small enough for review.
- Preserve exact package/signature metadata where it is central to validity.
- Mark unsupported or skipped sections explicitly.

# Maintenance & governance plan

- Keep the core about receipts, findings, and diffs.
- Version package/schema/formula assumptions separately.
- Publish a small conformance corpus with known-valid and known-problematic files.
- Resist scope creep into giant office-format universality claims.

# Milestones

## 0.1
- `odf.lock`
- package receipt schema
- ODS package/formula inspection

## 0.2
- modality findings
- ODT/ODP partial-support receipts
- public fixture corpus

## 1.0
- stable `*.odfbundle.zip`
- documented compatibility policy for package/schema/formula layers
- CI-friendly conformance gating

# Open questions

- What is the smallest stable formula receipt that still catches meaningful recalculation drift?
- Which modality-specific parts deserve first-class fields versus attachments?
- How should signatures and encryption-related package metadata fit into the MVP without derailing scope?

# Sources

- ODF 1.4 approval note: https://www.oasis-open.org/2025/12/03/oasis-approves-open-document-format-odf-v1-4-standard-marking-20-years-of-interoperable-document-innovation/
- ODF 1.4 family index: https://docs.oasis-open.org/office/OpenDocument/v1.4/os/v1.4-os.html
- ODF 1.4 package part: https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part2-packages/OpenDocument-v1.4-os-part2-packages.html
- ODF 1.4 formula part: https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part4-formula/OpenDocument-v1.4-os-part4-formula.html
- `spreadsheet_ods`: https://docs.rs/spreadsheet_ods
- `calamine`: https://docs.rs/calamine
- `open-document`: https://crates.io/crates/open-document

