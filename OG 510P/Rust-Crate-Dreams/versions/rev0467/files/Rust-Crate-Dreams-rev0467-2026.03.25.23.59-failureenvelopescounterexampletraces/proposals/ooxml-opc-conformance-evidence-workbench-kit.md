---
id: P-0371
title: OOXML + OPC Conformance & Evidence Workbench Kit — package-relationship locks, validator normalization, and safe document bug bundles
status: idea
domains: [documents, office, packaging, standards, interoperability, validation, tooling, enterprise]
last_reviewed: 2026-03-06
evidence:
  - https://learn.microsoft.com/en-us/previous-versions/windows/desktop/opc/open-packaging-conventions-overview
  - https://www.iso.org/standard/59575.html
  - https://crates.io/crates/ooxmlsdk
  - https://docs.rs/ooxml-opc/latest/ooxml_opc/
  - https://crates.io/crates/ooxml
  - https://github.com/mikeebowen/OOXML-Validator
  - https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/1fd4a662-8623-49c0-82f0-18fa91b413b8
---

# Problem

Rust now has early but real OOXML and OPC substrate, yet the painful failures still happen at the seam between:

- package structure (`OPC`) and document vocabulary (`OOXML`),
- content types, relationships, and markup-compatibility assumptions,
- strict-conformance expectations versus real-world producer quirks,
- validator output versus what an implementer can act on,
- and support cases that arrive as “this `.docx`/`.xlsx`/`.pptx` opens in app A but not app B” with no compact, redactable evidence artifact.

The missing Rust contribution is not another office suite. It is a **package-and-evidence workbench** that makes OOXML package failures reproducible, comparable, and safe to share.

# What it provides

- `package-lock` — lockfiles pinning package structure, relationship rules, content-type expectations, conformance assumptions, and optional producer-profile quirks.
- `ooxml-irx` — a neutral IR for OPC package trees, OOXML parts, relationships, validator findings, and redaction boundaries.
- `validator-bridge` — adapters that ingest validator outputs or Rust-native checks and normalize them into one reviewable report.
- `package-diff` — semantic diffs such as “same document payload, different relationship graph”, “same package, incompatible content types”, or “same visible content, different markup-compat assumptions”.
- `cargo ooxml-evidence` — emits `*.ooxmlbundle.zip` with redacted package snapshots, lockfile, normalized findings, relationship maps, and notes.

# What the crate should provide other people

1. **A boring default artifact for OOXML interoperability bugs**.
2. **Explicit package/relationship locks** instead of vague “Office document support”.
3. **Normalized validator findings** so tool and platform differences become explainable.
4. **Safe document bug bundles** that preserve structure while redacting business content.
5. **A bridge from Rust OOXML/OPC crates to enterprise-ready interop workflows**.

# Persona / who it’s for

- Rust developers building document ingestion, transformation, or compliance tooling
- Teams debugging enterprise document-exchange failures
- Authors of conversion, validation, or archival pipelines
- Maintainers of Rust OOXML/OPC libraries

# Users & user stories

- **Platform engineer**: “Show me whether this failure is package structure, relationships, content types, or document markup.”
- **Support engineer**: “Produce a bug bundle that preserves the failing structure without leaking the document’s business content.”
- **Library maintainer**: “Diff two packages semantically instead of at raw ZIP-byte level.”
- **Pipeline owner**: “Pin the conformance surface we promise and catch drift in CI.”

# Prior art (and why it’s insufficient)

- OPC and OOXML are large, real standards with strict conformance surfaces and producer variance.
- Rust has meaningful early substrate in `ooxmlsdk`, `ooxml-opc`, and `ooxml`.
- External validator tooling exists, but Rust still lacks a boring-default crate for **package locks + validator normalization + semantic diffs + portable evidence bundles**.

# Design goals

1. **Package-first** — relationship graphs and content types matter as much as XML part parsing.
2. **Validator-honest** — normalize external validator findings instead of pretending one Rust parser alone settles conformance.
3. **Redaction-safe** — the structure should remain debuggable after sensitive content is removed.
4. **Deterministic bundles** — evidence should be stable enough for CI and support workflows.
5. **Producer-aware** — make it possible to pin real-world producer profiles without baking vendor lock-in into the core.

# MVP surface

- Minimal types: `PackageLock`, `ProducerProfile`, `OoxmlBundle`, `ValidationFinding`, `PackageDiffFinding`
- Minimal functions:
  - `inspect_package()`
  - `normalize_findings()`
  - `diff_packages()`
  - `write_bundle()`
- Feature flags:
  - `opc`
  - `wordprocessingml`
  - `spreadsheetml`
  - `presentationml`
  - `redaction`

# Compatibility story

- MVP should target package structure and a narrow set of high-value part/relationship checks first.
- The crate should complement OOXML/OPC crates rather than replace them.
- Validator adapters may ingest external tools while the lockfile and bundle schema stay Rust-native and stable.
- Producer-profile quirks should remain explicit overlays rather than silently changing core semantics.

# Conformance & fixtures

- Tiny package fixtures for missing relationships, bad content-type maps, broken part names, and strict-conformance edge cases.
- Goldens for “same content, different package graph” and “package accepted by one validator but not another”.
- Redaction tests that preserve relationship shape, counts, and content-type maps while blanking sensitive text or media.
- Public profile packs for narrow producer quirks where legally and technically appropriate.

# Path to boring stability

- Stabilize the lockfile, normalized report schema, and diff semantics before broadening document-feature coverage.
- Start with package and validator evidence, not full editing/rendering ambition.
- Use tiny public fixtures that exercise relationship/content-type seams clearly.
- Keep format-specific adapters modular.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that inspect one OOXML package, validate it against a pinned package/profile lock, normalize validator findings, and emit a compact `*.ooxmlbundle.zip` with relationship graphs and semantic diffs.

# De-risk plan

1. Start with OPC package inspection + normalized findings before going deep into document vocabularies.
2. Keep redaction and relationship-preservation policy explicit from day one.
3. Use tiny public fixtures instead of real business documents.
4. Treat validator-bridge quality as the main trust surface.

# Non-goals

- Not an office suite.
- Not a full document renderer.
- Not a replacement for every validator or every producer SDK.
- Not a generic document-management platform.

# Architecture & API sketch

```rust
pub struct PackageLock {
    pub opc_profile: String,
    pub producer_profile: Option<String>,
    pub content_type_policy: ContentTypePolicy,
}

pub fn inspect_package(bytes: &[u8]) -> Result<PackageReport>;
pub fn diff_packages(a: &PackageReport, b: &PackageReport, lock: &PackageLock) -> PackageDiff;
```

Bundle draft: `profile.toml`, `package/`, `report.json`, `relationships.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat OOXML packages and embedded parts as untrusted input.
- Support redaction of text runs, comments, metadata, and embedded media while preserving structural evidence.
- Record exact profile, validator, and normalization versions in every bundle.
- Keep outputs deterministic enough for enterprise support and regression testing.

# Maintenance & governance plan

- Keep the core centered on package locks, normalized findings, diffs, and bundle format.
- Version format-specific or producer-specific adapters separately.
- Publish a small public fixture corpus around package-structure and validator-disagreement cases.
- Avoid turning the workbench into a broad document-productivity SDK.

# Milestones

## 0.1
- package inspection
- package/profile lockfile
- normalized report writer

## 0.2
- semantic diffs
- redaction support
- validator adapters

## 1.0
- stable `*.ooxmlbundle.zip`
- public fixture corpus
- documented compatibility policy for supported package/profile surfaces

# Open questions

- Which smallest set of package/relationship checks makes the crate obviously useful?
- How much producer-specific behavior belongs in stable profile packs versus transient adapter notes?
- What is the best default redaction strategy for preserving structural evidence without leaking content?

# Sources

- Open Packaging Conventions overview: https://learn.microsoft.com/en-us/previous-versions/windows/desktop/opc/open-packaging-conventions-overview
- ISO/IEC 29500-1 strict conformance overview: https://www.iso.org/standard/59575.html
- `ooxmlsdk`: https://crates.io/crates/ooxmlsdk
- `ooxml-opc`: https://docs.rs/ooxml-opc/latest/ooxml_opc/
- `ooxml`: https://crates.io/crates/ooxml
- OOXML Validator: https://github.com/mikeebowen/OOXML-Validator
- Microsoft implementation information for OOXML: https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/1fd4a662-8623-49c0-82f0-18fa91b413b8
