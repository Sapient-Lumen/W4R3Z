---
id: P-0357
title: RDF 1.2 + SPARQL 1.2 + SHACL 1.2 Conformance & Evidence Kit — graph canonicalization, validator normalization, and replayable linked-data bug bundles
status: idea
domains: [knowledge-graphs, linked-data, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://www.w3.org/TR/rdf12-concepts/
  - https://www.w3.org/TR/rdf12-interop/
  - https://www.w3.org/TR/sparql12-query/
  - https://www.w3.org/TR/shacl12-core/
  - https://crates.io/crates/oxigraph
  - https://crates.io/crates/rio_turtle
  - https://docs.rs/oxrdfio
---

# Problem

Rust has enough RDF and SPARQL substrate to parse, store, and query linked data, but real interoperability failures still tend to happen at the seam between:

- RDF syntax and dataset-model choices,
- SPARQL query/update behavior and endpoint quirks,
- SHACL validation expectations and processor-specific reporting,
- RDF 1.2 / triple-term adoption versus older RDF 1.1-era assumptions,
- and bug reports that arrive as vague “this graph fails there but not here” complaints.

The missing Rust contribution is not another graph store or parser. It is a **conformance-and-evidence workbench** that makes linked-data failures reproducible, comparable, and portable across tools.

# What it provides

- `graph-ir` — a stable IR for RDF graphs/datasets, SHACL findings, SPARQL result sets, and endpoint capability surfaces.
- `shape-lock` — lockfiles pinning RDF/SPARQL/SHACL feature assumptions, syntax subsets, entailment expectations, and validator/runtime quirks.
- `graph-normalize` — canonicalization and stable serialization for datasets, prefixes, blank nodes, result sets, and validator findings.
- `graph-check` — run parse/query/validate suites against files or endpoints and normalize the outputs into stable findings.
- `graph-diff` — semantic diffs such as “same triples, different blank-node layout”, “query semantics drift”, or “SHACL report mismatch”.
- `cargo graph-evidence` — emit `*.rdfbundle.zip` for CI, endpoint regressions, or cross-vendor bug reports.

# What the crate should provide other people

1. **A boring default artifact for linked-data interoperability bugs**.
2. **Pinned graph/query/shape expectations** that survive tool upgrades.
3. **Canonical graph and report normalization** so diffs mean something.
4. **Cross-tool validation replay** without bespoke shell scripts and local conventions.
5. **A clean bridge from parser/store/query crates to evidence-grade workflows**.

# Persona / who it’s for

- Knowledge-graph and semantic-web teams
- Data-publishing and linked-data portal maintainers
- SHACL / RDF validator authors
- SPARQL endpoint operators
- Tool authors building graph ingestion or data-quality systems in Rust

# Users & user stories

- **Portal operator**: “Tell me whether this failure is RDF syntax, SHACL semantics, or endpoint behavior.”
- **Validator maintainer**: “Diff our findings against another implementation without arguing about blank nodes or report formatting.”
- **Graph publisher**: “Pin the accepted syntax/features for this dataset and catch drift in CI.”
- **Query engineer**: “Replay a failing SPARQL case against multiple endpoints and compare only the semantic differences.”

# Prior art (and why it’s insufficient)

- W3C publishes active RDF 1.2, SPARQL 1.2, and SHACL 1.2 surfaces.
- Rust has real substrate in `oxigraph`, `oxrdfio`, and Rio-family crates.
- But the ecosystem still lacks a boring-default Rust crate for **lockfiles + canonicalization + validation/query replay + evidence bundles**.

# Design goals

1. **Model-first** — separate semantic graph equality from syntax/layout noise.
2. **Validator-aware** — normalize SHACL findings without flattening meaningful detail.
3. **Replayable** — every failing case should be portable into CI or another toolchain.
4. **Subset-aware** — explicitly pin RDF 1.1, RDF 1.2, SHACL Core, and optional extension expectations.
5. **Storage-neutral** — work with files, in-process stores, and remote SPARQL endpoints.

# MVP surface

- Minimal types: `GraphLock`, `GraphBundle`, `GraphReport`, `ValidationFinding`, `GraphDiffFinding`
- Minimal functions:
  - `normalize_dataset()`
  - `run_shape_check()`
  - `run_query_case()`
  - `diff_reports()`
  - `write_bundle()`
- Feature flags:
  - `rdf12`
  - `sparql`
  - `shacl`
  - `endpoint`
  - `redaction`

# Compatibility story

- MVP should target a practical subset of RDF 1.2 / SPARQL 1.2 / SHACL 1.2 with clear downgrade paths for older tooling.
- The crate should complement graph stores and parsers rather than replace them.
- Endpoint- and validator-specific adapters can remain optional packs on top of the neutral IR.
- Canonicalization must remain deterministic across OS and locale differences.

# Conformance & fixtures

- Tiny graph fixtures that differ only in blank-node allocation, prefixes, or triple-term syntax.
- SHACL cases for datatype, cardinality, node kind, and SPARQL-based constraints.
- SPARQL suites for result-set normalization, update behavior, and federated query edge cases.
- Goldens for “same data, different syntax”, “same violation, different report wording”, and “feature not supported versus malformed input”.

# Path to boring stability

- Stabilize the report and bundle schemas before broadening the supported standards surface.
- Keep MVP findings narrowly explainable.
- Freeze canonicalization rules only after testing against multiple Rust and non-Rust implementations.
- Add extension packs after the base RDF/query/shape loop becomes dependable.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that normalize an RDF dataset, run one or more SHACL/SPARQL checks against it, and emit a compact `*.rdfbundle.zip` with stable findings and semantic diffs.

# De-risk plan

1. Start with dataset normalization and SHACL Core instead of every extension.
2. Keep endpoint replay optional in the first version.
3. Treat blank-node and report canonicalization as the hardest early design problem.
4. Use tiny W3C-style fixtures before large public datasets.

# Non-goals

- Not a new graph database.
- Not a full ontology editor or triplestore product.
- Not a replacement for W3C test suites.
- Not a generic reasoning engine for every entailment regime.

# Architecture & API sketch

```rust
pub struct GraphReport {
    pub lock_id: String,
    pub findings: Vec<ValidationFinding>,
    pub diffs: Vec<GraphDiffFinding>,
}

pub fn normalize_dataset(input: &[u8], syntax: RdfSyntax) -> Result<NormalizedDataset>;
pub fn run_shape_check(lock: &GraphLock, dataset: &NormalizedDataset, shapes: &NormalizedDataset) -> Result<GraphReport>;
```

Bundle draft: `profile.toml`, `dataset.nq`, `shapes.ttl`, `report.json`, `query-results.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat graphs, queries, and validator outputs as untrusted input.
- Support redaction of IRIs, literals, and endpoint URLs in bundles.
- Record exact standard/profile versions and feature flags.
- Keep canonicalization deterministic to support trustworthy diffs.

# Maintenance & governance plan

- Keep the core centered on graph IR, canonicalization, findings, and bundle format.
- Version endpoint and validator adapters separately.
- Build a public fixture corpus around small but semantically tricky cases.
- Avoid coupling the crate to one graph store or one SHACL engine.

# Milestones

## 0.1
- dataset normalization
- SHACL Core finding normalization
- bundle writer

## 0.2
- SPARQL query/update replay
- semantic diffs
- optional endpoint adapters

## 1.0
- stable `*.rdfbundle.zip`
- public fixture corpus
- documented compatibility policy for RDF 1.1/1.2 and shape/query feature packs

# Open questions

- What minimum canonicalization is enough before full RDF dataset canonicalization support?
- Which SHACL extensions belong in the core crate versus optional packs?
- How much endpoint transport detail should be preserved in normalized replay traces?

# Sources

- RDF 1.2 Concepts and Abstract Data Model: https://www.w3.org/TR/rdf12-concepts/
- RDF 1.2 Interoperability: https://www.w3.org/TR/rdf12-interop/
- SPARQL 1.2 Query Language: https://www.w3.org/TR/sparql12-query/
- SHACL 1.2 Core: https://www.w3.org/TR/shacl12-core/
- `oxigraph`: https://crates.io/crates/oxigraph
- `rio_turtle`: https://crates.io/crates/rio_turtle
- `oxrdfio`: https://docs.rs/oxrdfio
