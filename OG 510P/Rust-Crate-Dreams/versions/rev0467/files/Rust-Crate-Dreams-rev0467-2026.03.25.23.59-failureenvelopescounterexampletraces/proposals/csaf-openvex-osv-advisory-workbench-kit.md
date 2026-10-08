---
id: P-0369
title: CSAF 2.0 + OpenVEX + OSV Advisory Workbench Kit — product matching, status crosswalks, and explainable vulnerability evidence bundles
status: idea
domains: [security, vulnerability-management, advisories, supply-chain, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html
  - https://www.csaf.io/tools/
  - https://openssf.org/projects/openvex/
  - https://ossf.github.io/osv-schema/
  - https://docs.rs/csaf-walker
  - https://docs.rs/openvex
  - https://docs.rs/osv
  - https://documentation.ubuntu.com/security/security-updates/vex/
---

# Problem

Rust now has meaningful pieces for security-advisory ecosystems, but the operational pain still sits at the seam between:

- vendor-style advisory documents (`CSAF`),
- minimal exploitability statements (`OpenVEX`),
- package/version-oriented vulnerability records (`OSV`),
- product matching, package identity, and version-range interpretation,
- and user complaints that arrive as “these feeds disagree” with no explainable artifact showing whether the disagreement is semantic, scoping-related, or simply a cross-format mismatch.

The missing Rust contribution is not another scanner and not another SBOM generator. It is an **advisory-and-crosswalk workbench** that makes structured vulnerability information comparable, traceable, and reviewable across formats.

# What it provides

- `advisory-lock` — lockfiles pinning advisory-feed snapshots, schema versions, product-matching policy, PURL/CPE/package-ecosystem assumptions, and supported status crosswalks.
- `advisory-irx` — a neutral IR for products, packages, versions, vulnerabilities, exploitability assertions, remediation states, and provenance.
- `crosswalk-check` — normalize one or more CSAF/OpenVEX/OSV documents into the neutral IR and report what matched, conflicted, or could not be mapped.
- `status-diff` — semantic diffs such as “same CVE, different product scope”, “same package, incompatible version-range interpretation”, or “same condition, no lossless OpenVEX expression”.
- `cargo advisory-evidence` — emits `*.advisorybundle.zip` with source documents, lockfile, normalized IR, mapping diagnostics, redaction-aware notes, and diffs.

# What the crate should provide other people

1. **A boring default artifact for advisory-feed disagreement**.
2. **Repeatable product and package matching policy** instead of one-off glue code.
3. **Explainable crosswalks** across CSAF, OpenVEX, and OSV without pretending they are semantically identical.
4. **Portable evidence bundles** for triage, supplier/customer exchange, and CI validation.
5. **A bridge from Rust advisory libraries to ecosystem-level vulnerability interchange workflows**.

# What makes this different from SBOM + VEX proposals

The sharp idea here is not “generate VEX from my Cargo tree.” It is **normalize, compare, and explain upstream/downstream advisory records across formats and feeds**, especially when product identity and scope differ. That is a different problem and deserves a different crate shape.

# Persona / who it’s for

- Product-security and PSIRT teams publishing or consuming machine-readable advisories
- Vulnerability-tool authors who need to reconcile multiple feed formats
- Platform teams building advisory ingestion, trust, or routing workflows
- Maintainers who need reproducible evidence when supplier and scanner claims disagree

# Users & user stories

- **Security engineer**: “Show me whether this conflict is about versions, products, exploitability, or simply format mismatch.”
- **Feed integrator**: “Pin our matching policy so we stop silently changing behavior after every parser tweak.”
- **Supplier**: “Ship one compact bundle that explains why our OpenVEX statement and a CSAF advisory do not actually disagree.”
- **Consumer platform**: “Normalize multiple documents into one reviewable intermediate form before policy decisions happen.”

# Prior art (and why it’s insufficient)

- CSAF is a real OASIS standard with validator and tool ecosystem.
- OpenVEX is a real, actively used minimal VEX format.
- OSV is a widely used vulnerability schema with Rust bindings.
- Rust has relevant building blocks in `csaf-walker`, `openvex`, and `osv`.
- But Rust still lacks a boring-default crate for **feed locks + product/package crosswalks + explainable status diffs + portable evidence bundles**.

# Design goals

1. **Cross-format honesty** — model what maps cleanly and what does not.
2. **Matching-policy explicitness** — product/package identity rules must be pinned and reviewable.
3. **Schema-neutral core** — the lockfile and IR should survive individual feed changes.
4. **Evidence over magic** — the output should help humans audit why the tool concluded what it concluded.
5. **Safe sharing** — bundles should support redaction of internal inventory details while preserving enough evidence to review mappings.

# MVP surface

- Minimal types: `AdvisoryLock`, `MatchingPolicy`, `AdvisoryBundle`, `MappingFinding`, `StatusDiffFinding`
- Minimal functions:
  - `ingest_document()`
  - `normalize_ir()`
  - `crosswalk_statuses()`
  - `diff_documents()`
  - `write_bundle()`
- Feature flags:
  - `csaf`
  - `openvex`
  - `osv`
  - `redaction`

# Compatibility story

- MVP should target CSAF 2.x, OpenVEX, and OSV surfaces that already have active ecosystems.
- The crate should complement feed-specific libraries rather than replace them.
- Matching rules should remain adapter-driven and configurable, not hardcoded to one organization’s taxonomy.
- Lossy or one-way mappings must be reported explicitly instead of quietly flattened.

# Conformance & fixtures

- Tiny fixtures for same-vulnerability/different-scope cases across CSAF, OpenVEX, and OSV.
- Cases for PURL/CPE mismatch, overlapping but non-identical version ranges, and exploitability assertions with no exact cross-format equivalent.
- Goldens for “same source fact, different status vocabulary” and “same CVE, different product identity”.
- Redaction tests for internal inventory/product aliases while preserving public vulnerability evidence.

# Path to boring stability

- Stabilize the lockfile, normalized IR, and crosswalk-loss reporting before adding many discovery or trust protocols.
- Start with a small public corpus of well-understood documents.
- Keep the schema adapters boring and the explanations sharp.
- Build confidence through diff quality, not through feature count.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and CLI that ingest one CSAF document plus one OpenVEX or OSV document, normalize them under a pinned matching policy, and emit a compact `*.advisorybundle.zip` with mapping diagnostics and semantic diffs.

# De-risk plan

1. Start with document ingestion + IR normalization before broad feed crawling.
2. Keep matching policy explicit and user-editable from day one.
3. Treat non-lossless mappings as a feature to expose, not a bug to hide.
4. Use a tiny public corpus with known disagreements to shape the explanations.

# Non-goals

- Not a vulnerability scanner.
- Not a universal security data lake.
- Not a replacement for SBOM generation.
- Not a full trust-distribution or disclosure-management platform.

# Architecture & API sketch

```rust
pub struct AdvisoryLock {
    pub schema_versions: Vec<String>,
    pub matching_policy: MatchingPolicy,
}

pub fn ingest_document(bytes: &[u8], format: AdvisoryFormat) -> Result<AdvisoryDoc>;
pub fn diff_documents(a: &AdvisoryDoc, b: &AdvisoryDoc, lock: &AdvisoryLock) -> AdvisoryDiff;
```

Bundle draft: `profile.toml`, `sources/`, `normalized.json`, `mapping.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat advisory input as untrusted data.
- Support redaction of internal package aliases, private inventory groupings, and customer-specific notes.
- Record exact schema and matching-policy versions in every bundle.
- Keep outputs deterministic enough for CI gates, supplier exchanges, and issue-tracker review.

# Maintenance & governance plan

- Keep the core centered on locks, IR, crosswalks, diffs, and bundle format.
- Version feed adapters separately as ecosystems evolve.
- Publish a small public corpus organized around product-scope and version-range disagreements.
- Avoid turning the crate into a full vulnerability-management product.

# Milestones

## 0.1
- document ingestion
- matching-policy lockfile
- normalized IR writer

## 0.2
- crosswalk diffs
- redaction support
- public fixture corpus

## 1.0
- stable `*.advisorybundle.zip`
- documented compatibility policy for supported CSAF/OpenVEX/OSV surfaces
- adapter packs for real feed snapshots

# Open questions

- What minimum shared semantic core across CSAF, OpenVEX, and OSV deserves first-class schema support?
- Which matching rules should be part of the stable lockfile versus extension policy packs?
- How should the crate represent “cannot be mapped losslessly” in a way that downstream tools can still automate against?

# Sources

- CSAF 2.0 standard: https://docs.oasis-open.org/csaf/csaf/v2.0/os/csaf-v2.0-os.html
- CSAF tools ecosystem: https://www.csaf.io/tools/
- OpenVEX project: https://openssf.org/projects/openvex/
- OSV schema: https://ossf.github.io/osv-schema/
- `csaf-walker`: https://docs.rs/csaf-walker
- `openvex`: https://docs.rs/openvex
- `osv`: https://docs.rs/osv
- Ubuntu OpenVEX feed: https://documentation.ubuntu.com/security/security-updates/vex/
