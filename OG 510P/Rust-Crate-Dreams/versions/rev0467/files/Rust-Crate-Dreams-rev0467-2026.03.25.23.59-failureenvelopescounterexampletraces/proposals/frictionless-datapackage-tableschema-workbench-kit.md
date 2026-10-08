---
id: P-0396
title: Frictionless Data Package + Table Schema Workbench Kit — package locks, validation receipts, and profile-aware dataset bundles
status: idea
domains: [data, open-data, metadata, validation, packaging, interoperability]
last_reviewed: 2026-03-06
evidence:
  - https://specs.frictionlessdata.io/
  - https://specs.frictionlessdata.io/data-package/
  - https://frictionlessdata.io/specs/table-schema/
  - https://specs.frictionlessdata.io/profiles/
  - https://specs.frictionlessdata.io/patterns/
  - https://frictionlessdata.io/blog/2024/06/26/datapackage-v2-release/
  - https://frictionlessdata.io/blog/2025/04/07/frictionless-summit/
  - https://docs.rs/wacksy/latest/wacksy/datapackage/
---

# Problem

Frictionless Data remains one of the cleanest open standards families for shipping portable datasets: Data Package, Data Resource, Table Schema, profiles, and related patterns all give a usable metadata contract for data exchange. Data Package v2 has also re-opened the question of what a modern, well-scoped core library should look like.

Rust, however, still lacks a boring default for this ecosystem. There are pockets of overlap — for example WACZ-related Rust code that emits Frictionless-compatible `datapackage.json` structures — but not a general workbench for package validation, profile handling, schema diffing, and portable evidence.

The pain is concentrated at the seam between:

- **package metadata and the actual referenced files or remote resources**,
- **Table Schema intent and the real CSV/JSON/tabular payloads people ship**,
- **profile and pattern usage that may be common but not fully formalized**,
- **v1 versus v2 expectations and what downstream tooling actually accepts**,
- and **dataset handoff workflows where people need receipts, not just yes/no validation output**.

The missing Rust contribution is not a warehouse or notebook platform. It is a **package/schema workbench** for locks, validation receipts, diffs, and profile-aware bundles.

# What it provides

- `datapackage.lock` — pins Data Package surface, Table Schema expectations, profile usage, dialect assumptions, and resource digests.
- `package-ir` — normalized representation of package/resource descriptors, schema references, dialect metadata, and resource inventory.
- `validation-receipt` — explainable findings for schema, profile, path, digest, and tabular-shape mismatches.
- `resource-proof` — compact evidence tying descriptors to local or remote resources without copying giant datasets by default.
- `cargo datapackage-evidence` — emits `*.dpbundle.zip` with lockfile, normalized descriptors, validation receipts, diffs, and notes.

# What the crate should provide other people

1. **A boring validation and handoff artifact** for dataset packaging bugs.
2. **Explicit version/profile pinning** across evolving Frictionless surfaces.
3. **Explainable receipts** instead of one-shot CLI errors.
4. **Portable resource proofs and diffs** for open-data and research exchange.
5. **A Rust-native coordination layer** that other data tools can reuse.

# Persona / who it’s for

- Rust maintainers building data portals, open-data tooling, or publishing pipelines
- Research software teams exchanging dataset bundles across institutions
- Validators and conversion-tool authors who need stable receipts
- Archivists and reproducibility engineers who need metadata-anchored handoff artifacts

# Users & user stories

- **Data publisher**: “Tell me exactly why this package validates locally but fails for a downstream consumer.”
- **Portal maintainer**: “Pin the exact profile and schema assumptions accepted by our ingestion pipeline.”
- **Research engineer**: “Ship a dataset receipt that proves which files and schemas were intended without embedding everything inline.”
- **Archivist**: “Compare two package revisions and identify what changed semantically, not just textually.”

# Prior art (and why it’s insufficient)

- Frictionless publishes the spec suite, profiles, and patterns.
- Data Package v2 and the 2025 ecosystem discussion both highlight the need for a well-scoped core implementation surface.
- Rust has narrow overlap in areas like WACZ datapackage modeling.

What Rust still lacks is a **single workbench** for lockfiles, validation receipts, semantic diffs, and profile-aware evidence bundles.

# Design goals

1. **Descriptor plus resource honesty** — keep metadata and referenced content connected.
2. **Profile-aware** — distinguish base spec behavior from profile or pattern overlays.
3. **Version-aware** — make v1/v2 assumptions explicit.
4. **Dataset-light** — support digest- and sample-based evidence rather than forcing full copies.
5. **Reusable foundation** — useful to portals, CLIs, and archive pipelines alike.

# MVP surface

- Minimal types: `DataPackageLock`, `PackageBundle`, `ValidationReceipt`, `ResourceProof`, `DpEvidence`
- Minimal functions:
  - `normalize_package()`
  - `validate_resources()`
  - `diff_packages()`
  - `write_bundle()`
- Feature flags:
  - `data-package`
  - `table-schema`
  - `profiles`
  - `digests`
  - `redaction`

# Compatibility story

- Works above existing Rust file/CSV/JSON stacks rather than replacing them.
- Supports local files, remote paths, and sample-based evidence.
- Keeps base spec, profile, and pattern assumptions distinct.
- Can emit schema-only or digest-only bundles when the data itself cannot be redistributed.

# Conformance & fixtures

- Tiny fixtures for broken paths, stale digests, schema drift, dialect mismatch, profile mismatch, and v1/v2 expectation differences.
- Goldens for semantic package diffs across descriptor revisions.
- Public sample bundles with local and remote resource references.
- WACZ-adjacent fixtures so archive/package ecosystems can share substrate.

# Path to boring stability

- Stabilize `datapackage.lock`, validation receipts, and resource proofs first.
- Start with normalization and explanation before adding converters.
- Keep profiles and patterns as explicit overlays.
- Avoid becoming a giant “data framework” clone.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that normalize a Data Package descriptor, validate referenced resources and Table Schemas, pin profile/version assumptions, compute semantic diffs, and emit compact `*.dpbundle.zip` artifacts.

# De-risk plan

1. Start with read-only validation and digests.
2. Support digest-only and sample-only evidence before embedding payloads.
3. Keep profile/pattern overlays explicit and separate from base validation.
4. Delay rich portal integrations until the receipt format is stable.

# Non-goals

- Not a notebook or data-analysis framework.
- Not a data warehouse.
- Not a generic ETL platform.
- Not a replacement for every Frictionless ecosystem tool.

# Architecture & API sketch

```rust
pub struct DataPackageLock {
    pub package_surface: String,
    pub table_schema_surface: String,
    pub profile_pack: String,
    pub resource_digest_policy: String,
}

pub fn normalize_package(input: &str) -> Result<PackageBundle>;
pub fn validate_resources(bundle: &PackageBundle) -> Result<ValidationReceipt>;
pub fn diff_packages(lhs: &PackageBundle, rhs: &PackageBundle) -> ValidationReceipt;
```

Bundle draft: `datapackage.lock`, `descriptor.json`, `resources.json`, `validation.json`, `diff.json`, `notes.md`.

# Security / safety model

- Treat package descriptors and referenced schemas as untrusted input.
- Support redaction or omission of sensitive URLs, tokens, and inline data.
- Record whether a bundle contains full resources, samples, or only digests.
- Keep outputs deterministic enough for CI and publishing workflows.

# Maintenance & governance plan

- Keep the core about locks, validation receipts, resource proofs, and diffs.
- Version v1/v2 and profile overlays separately.
- Publish a small public corpus of legal-to-share sample packages.
- Resist scope creep into portal hosting or general data transformation.

# Milestones

## 0.1
- descriptor normalization
- resource digesting
- validation receipts

## 0.2
- semantic package diffs
- profile overlays
- sample public corpus

## 1.0
- stable `*.dpbundle.zip`
- documented compatibility policy for v1/v2 and profile packs
- adapter story for archive/open-data pipelines

# Open questions

- How should the lockfile represent the practical gap between Data Package v1 specs and newer v2 ecosystem expectations?
- Which pattern-level behaviors deserve first-class overlays versus plain advisory notes?
- What is the smallest credible sample corpus for remote-resource validation and digest proofs?

# Sources

- Frictionless specs suite: https://specs.frictionlessdata.io/
- Data Package spec: https://specs.frictionlessdata.io/data-package/
- Table Schema: https://frictionlessdata.io/specs/table-schema/
- Profiles: https://specs.frictionlessdata.io/profiles/
- Patterns: https://specs.frictionlessdata.io/patterns/
- Data Package v2 release: https://frictionlessdata.io/blog/2024/06/26/datapackage-v2-release/
- 2025 ecosystem discussion: https://frictionlessdata.io/blog/2025/04/07/frictionless-summit/
- `wacksy` datapackage module: https://docs.rs/wacksy/latest/wacksy/datapackage/
