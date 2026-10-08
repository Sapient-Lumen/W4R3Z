---
id: P-0361
title: Amazon Ion + PartiQL Canonicalization & Evidence Kit — query/data lockfiles, semantic diffs, and replayable semi-structured bundles
status: idea
domains: [databases, semi-structured-data, query-languages, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://amazon-ion.github.io/ion-docs/docs/spec.html
  - https://partiql.org/assets/PartiQL-Specification.pdf
  - https://crates.io/crates/ion-rs
  - https://crates.io/crates/partiql
  - https://crates.io/crates/partiql-extension-ion
---

# Problem

Rust now has real Ion and PartiQL substrate, but interoperability failures still tend to happen at the seam between:

- Ion text versus binary encodings,
- annotated/semi-structured data and query-engine expectations,
- PartiQL semantics over missing values, bags, structs, and path navigation,
- host-system subsets that only support part of PartiQL or part of Ion,
- and bug reports that are hard to replay because they mix data, query text, host assumptions, and result semantics.

The missing Rust contribution is not another database or parser. It is a **semantic canonicalization and replay workbench** for Ion-backed PartiQL workflows.

# What it provides

- `partiql-ir` — stable IR for Ion values, PartiQL queries, host capability packs, and normalized results.
- `query-lock` — lockfiles pinning Ion/PartiQL version assumptions, host subsets, missing-value semantics, and function availability.
- `ion-normalize` — stable normalization for Ion text/binary surfaces and semantic comparison of annotated values.
- `query-replay` — portable query cases with pinned datasets and expected semantic outcomes.
- `partiql-diff` — semantic diffs such as “same data, different annotations”, “missing versus null behavior changed”, or “host subset rejected feature”.
- `cargo ion-evidence` — emit `*.ionbundle.zip` for CI, engine comparison, or integration debugging.

# What the crate should provide other people

1. **A boring artifact for Ion/PartiQL interoperability bugs**.
2. **Pinned host/query expectations** instead of vague “supports PartiQL”.
3. **Canonicalization across Ion text and binary forms**.
4. **Replayable query cases** that capture the data, semantics, and host subset together.
5. **Explainable diffs for semi-structured edge cases** such as annotations, missing values, and bag ordering.

# Persona / who it’s for

- Query-engine authors
- Rust teams using Ion or PartiQL in storage, APIs, or local query tools
- Data-platform and format-tooling maintainers
- QA engineers comparing engine behavior
- Teams standardizing semi-structured interchange in Rust

# Users & user stories

- **Engine maintainer**: “Replay the failing query against two engines and compare only the semantic differences.”
- **Integration engineer**: “Pin what subset of PartiQL and Ion this system actually supports.”
- **Format maintainer**: “Show whether the drift is in encoding, annotations, or query semantics.”
- **QA engineer**: “Share a tiny repro bundle with data, query, and expected behavior all in one place.”

# Prior art (and why it’s insufficient)

- Amazon Ion publishes a specification and Rust has `ion-rs`.
- PartiQL has a public specification and experimental Rust crate families now exist.
- But Rust still lacks a boring-default crate for **semantic locks + canonicalization + replay + evidence bundles**.

# Design goals

1. **Semantic-first** — do not confuse text/binary or surface formatting with value/query meaning.
2. **Host-subset aware** — most real systems support only part of PartiQL or Ion features.
3. **Replayable** — each failure should travel as a compact, deterministic artifact.
4. **Extensible** — function packs and host quirks should be overlays, not core assumptions.
5. **Encoding-neutral** — compare Ion text and binary without flattening meaningful annotations.

# MVP surface

- Minimal types: `QueryLock`, `IonSnapshot`, `ReplayCase`, `IonReport`, `IonDiffFinding`
- Minimal functions:
  - `normalize_ion()`
  - `parse_query_case()`
  - `run_query_case()`
  - `diff_results()`
  - `write_bundle()`
- Feature flags:
  - `ion-text`
  - `ion-binary`
  - `partiql`
  - `ion-hash`
  - `redaction`

# Compatibility story

- MVP should target the published Ion spec and a practical subset of PartiQL with explicit host capability packs.
- The crate should complement `ion-rs` and PartiQL crates rather than replace them.
- Host-specific adapters can remain optional.
- Canonicalization must remain deterministic across platforms and encodings.

# Conformance & fixtures

- Tiny Ion text/binary pairs with equivalent and intentionally non-equivalent annotation/layout cases.
- Query cases for path navigation, missing/null, bags/lists, and struct-field behavior.
- Goldens for “same value, different encoding”, “same query, different host subset”, and “annotation preserved versus lost”.
- Synthetic cases that stress result normalization and semantic hashing.

# Path to boring stability

- Stabilize the replay-case and report schemas before broadening function coverage.
- Keep early query semantics intentionally small and explainable.
- Freeze canonicalization only after checking against multiple encoders/decoders.
- Add richer function and host packs once the core lockfile model is useful.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that normalize Ion data, replay one or more PartiQL query cases against a pinned capability lock, and emit a compact `*.ionbundle.zip` with stable findings and semantic diffs.

# De-risk plan

1. Start with read/query semantics rather than write/update surfaces.
2. Keep host-specific extensions out of the neutral core.
3. Treat missing/null/bag semantics as first-class in the report model.
4. Use tiny synthetic fixtures before real application datasets.

# Non-goals

- Not a new database engine.
- Not a full PartiQL optimizer.
- Not a replacement for `ion-rs` or existing PartiQL parser/executor crates.
- Not a generic data-lake query framework.

# Architecture & API sketch

```rust
pub struct IonReport {
    pub lock_id: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<IonDiffFinding>,
}

pub fn normalize_ion(input: &[u8], encoding: IonEncoding) -> Result<NormalizedIon>;
pub fn run_query_case(lock: &QueryLock, case: &ReplayCase) -> Result<IonReport>;
```

Bundle draft: `profile.toml`, `data.ion`, `data.10n`, `query.sqlp`, `results.json`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat data and query cases as untrusted input.
- Support redaction of literals, field names, and host identifiers in bundles.
- Record exact encoding and capability-pack versions.
- Keep normalized results deterministic for trustworthy diffs.

# Maintenance & governance plan

- Keep the core centered on Ion normalization, query locks, replay, and bundle schemas.
- Version host adapters and function packs separately.
- Build a public corpus of tiny semantic edge cases.
- Avoid coupling the crate to one storage engine or one cloud product.

# Milestones

## 0.1
- Ion normalization
- query lockfiles
- bundle writer

## 0.2
- query replay
- semantic diffs
- host capability packs

## 1.0
- stable `*.ionbundle.zip`
- public fixture corpus
- documented compatibility policy for encoding and host-subset overlays

# Open questions

- What is the minimum neutral representation of PartiQL results across hosts?
- How much Ion annotation behavior should be normalized versus preserved verbatim?
- Should ion-hash-compatible outputs be part of the core or an optional overlay?

# Sources

- Amazon Ion specification: https://amazon-ion.github.io/ion-docs/docs/spec.html
- PartiQL specification: https://partiql.org/assets/PartiQL-Specification.pdf
- `ion-rs`: https://crates.io/crates/ion-rs
- `partiql`: https://crates.io/crates/partiql
- `partiql-extension-ion`: https://crates.io/crates/partiql-extension-ion
