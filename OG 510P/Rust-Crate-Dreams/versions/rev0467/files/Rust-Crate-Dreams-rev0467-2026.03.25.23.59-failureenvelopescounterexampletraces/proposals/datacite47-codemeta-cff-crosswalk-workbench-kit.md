---
id: P-0341
title: DataCite 4.7 + CodeMeta + CITATION.cff Crosswalk Workbench Kit — deterministic software-metadata translation, citation-quality diffs, and repository-to-DOI evidence bundles
status: idea
domains: [scholarly-metadata, research-software, citations, datacite, codemeta, cff, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://schema.datacite.org/
  - https://schema.datacite.org/versions.html
  - https://datacite.org/blog/get-started-with-schema-4-7/
  - https://support.datacite.org/docs/what-formats-can-i-use-to-submit-my-metadata-and-how-do-i-do-it
  - https://codemeta.github.io/crosswalk/
  - https://github.com/codemeta/codemeta
  - https://citation-file-format.github.io/
  - https://github.com/citation-file-format/citation-file-format
  - https://crates.io/crates/crate2bib
  - https://crates.io/crates/aeruginous
  - https://crates.io/crates/code-metadata
---

# Problem

Rust now has fragments of research-software citation tooling, but the painful failures in real scholarly metadata workflows still happen at the seam between **repository metadata, software-citation files, and DOI registration schemas**:

- `CITATION.cff` and `codemeta.json` disagree about authorship, identifiers, or versioning,
- repository metadata looks fine on GitHub but fails or degrades when translated into DOI-facing DataCite metadata,
- teams cannot explain which citation fields were lost, invented, or downgraded during conversion,
- software repositories lack a deterministic, testable way to ship “this is the metadata we meant” alongside a deposit or release,
- and today’s tooling is good at emitting a citation string, but not at producing **evidence-grade crosswalk artifacts**.

The worthy crate contribution is a **crosswalk workbench** that pins metadata mappings, performs deterministic translation and semantic diffing, and emits portable evidence bundles for repository-to-registry workflows.

# What it provides

- `citation-ir` — canonical Rust IR for software/project metadata spanning the overlap of DataCite, CodeMeta, and `CITATION.cff`.
- `crosswalk-lock` — lockfiles pinning mapping rules, controlled-vocabulary assumptions, fallback strategies, and lossy-field policies.
- `metadata-diff` — semantic diffs such as “author became contributor”, “identifier downgraded to free text”, or “relation type lost during DataCite projection”.
- `render-check` — verify that machine metadata still produces stable human-facing citation strings where expected.
- `deposit-bundle` — emit `*.citationbundle.zip` containing source metadata, normalized IR, target projections, findings, and redaction/override notes.
- `cargo citation-workbench` — inspect a repo, load `CITATION.cff`, `codemeta.json`, and related metadata, then produce translations and evidence.

# What the crate should provide other people

1. **A boring default for software-metadata crosswalks** instead of custom one-off scripts.
2. **Deterministic translation with explicit loss reporting** so teams know what changed and why.
3. **A single IR for repository, citation, and DOI deposit workflows** that Rust tools can build on.
4. **Portable evidence bundles** for repository managers, journal staff, or research-software infrastructure teams.
5. **A foundation for reproducible citation QA** across releases and registries.

# Persona / who it’s for

- Research software engineers
- Repository and DOI-infrastructure teams
- Scholarly-metadata tool authors
- Rust developers building citation/deposit helpers
- Labs or institutions trying to standardize software citation quality

# Users & user stories

- **Repository maintainer**: “Tell me whether my `CITATION.cff` and `codemeta.json` disagree materially.”
- **DOI platform engineer**: “Project this metadata into DataCite 4.7 and explain every lossy or inferred field.”
- **Research software office**: “Capture a release’s metadata state as a reproducible artifact for later auditing.”
- **Citation tooling author**: “Depend on one stable IR instead of writing separate ad hoc converters.”

# Prior art (and why it’s insufficient)

- DataCite 4.7 is now current and DataCite supports ingest from multiple metadata formats.
- CodeMeta exists specifically to standardize exchange across repositories and organizations, and it publishes crosswalks.
- `CITATION.cff` is a widely used repository-facing citation format, especially through GitHub.
- Rust has pieces like `crate2bib`, `aeruginous`, and `code-metadata`.
- But there is still no boring-default Rust crate family for **deterministic crosswalks + semantic citation diffs + repository-to-DOI evidence bundles**.

# Design goals

1. **Crosswalk-first** — mapping rules and losses must be explicit and pinned.
2. **IR over point converters** — the core should be reusable by many downstream tools.
3. **Citation-quality diagnostics** — not just “parsed successfully”, but “meaning changed here”.
4. **Adapter-first** — integrate with existing repository metadata and deposit workflows instead of replacing them.
5. **Auditability** — metadata state at release time should be preservable and comparable later.

# MVP surface

- Minimal types: `CitationGraph`, `CrosswalkLock`, `ProjectionReport`, `MetadataFinding`, `CitationDiff`
- Minimal functions:
  - `load_cff()`
  - `load_codemeta()`
  - `project_datacite()`
  - `diff_metadata()`
  - `write_bundle()`
- Feature flags:
  - `cff`
  - `codemeta`
  - `datacite`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target the current **DataCite 4.7** surface plus the published CodeMeta and CFF structures first.
- Projection to human-facing citations should stay secondary to machine-metadata fidelity.
- The crate should complement repository tooling and DOI deposit services rather than become a full scholarly platform.
- MVP should intentionally avoid becoming a general bibliography manager.

# Conformance & fixtures

- Tiny synthetic fixtures for authors, organizations, identifiers, funding, software versions, relation types, and licenses.
- Positive and negative fixtures for CFF↔CodeMeta disagreement and DataCite projection loss.
- Golden semantic diffs for common scholarly-metadata downgrades.
- Optional fixture packs drawn from public research-software repositories.

# Path to boring stability

- First stabilize the IR and crosswalk-lock vocabulary.
- Then prove that projections are deterministic and diffs are understandable.
- Freeze bundle format only after it supports real release/deposit auditing cases.
- Keep human-style citation rendering out of the core critical path.

# Scorecard

- Impact: 3/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A CLI and library that inspect one repository’s `CITATION.cff` and `codemeta.json`, normalize both into a shared IR, project the result into DataCite 4.7-compatible metadata, compute semantic diffs and loss notes, and emit a `*.citationbundle.zip` for release or deposit workflows.

# De-risk plan

1. Start with a narrow, high-value overlap of fields.
2. Make all lossy or inferred mappings explicit in lockfiles and findings.
3. Use public repositories and synthetic fixtures first.
4. Treat rendering convenience as optional adapters, not core logic.

# Non-goals

- Not a full DOI registration service.
- Not a general bibliography manager.
- Not a complete scholarly publishing platform.

# Architecture & API sketch

```rust
pub struct ProjectionReport {
    pub lock_id: String,
    pub source_findings: Vec<Finding>,
    pub projection_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn project_datacite(lock: &CrosswalkLock, graph: &CitationGraph) -> Result<ProjectionReport>;
pub fn diff_metadata(left: &CitationGraph, right: &CitationGraph) -> Vec<DiffFinding>;
```

Bundle draft: `lock.toml`, `sources/`, `normalized-ir.json`, `datacite.json`, `findings.json`, `diff.json`, `notes.md`.

# Security / safety model

- Preserve provenance for transformed fields so manual overrides are auditable.
- Bound remote metadata fetching by default.
- Record exact schema and crosswalk versions used.
- Support redaction of emails and private contributor notes while retaining structural metadata.

# Maintenance & governance plan

- Keep core focused on IRs, crosswalks, projections, and findings vocabularies.
- Version crosswalk packs separately from bundle schema.
- Encourage public example corpora and regression fixtures.
- Document how controlled-vocabulary changes are incorporated over time.

# Milestones

## 0.1
- CFF loader
- CodeMeta loader
- shared IR

## 0.2
- DataCite 4.7 projection
- semantic diffs
- bundle writer

## 1.0
- stable `*.citationbundle.zip`
- reproducible release/deposit auditing workflow
- documented crosswalk/version policy

# Open questions

- How much of DataCite’s larger schema should the core support before it becomes unwieldy?
- Should CodeMeta crosswalks be treated as data files shipped with the crate or compiled Rust logic?
- How opinionated should the workbench be about synthesizing missing fields?

# Sources

- DataCite schema: https://schema.datacite.org/
- DataCite release history: https://schema.datacite.org/versions.html
- Schema 4.7 announcement: https://datacite.org/blog/get-started-with-schema-4-7/
- DataCite supported metadata formats: https://support.datacite.org/docs/what-formats-can-i-use-to-submit-my-metadata-and-how-do-i-do-it
- CodeMeta crosswalks: https://codemeta.github.io/crosswalk/
- CodeMeta repository: https://github.com/codemeta/codemeta
- Citation File Format: https://citation-file-format.github.io/
- Citation File Format repository: https://github.com/citation-file-format/citation-file-format
- `crate2bib`: https://crates.io/crates/crate2bib
- `aeruginous`: https://crates.io/crates/aeruginous
- `code-metadata`: https://crates.io/crates/code-metadata
