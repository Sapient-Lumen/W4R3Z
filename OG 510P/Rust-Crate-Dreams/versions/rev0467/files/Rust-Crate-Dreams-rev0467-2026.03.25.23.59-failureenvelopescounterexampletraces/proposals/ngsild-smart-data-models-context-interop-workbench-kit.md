---
id: P-0418
title: NGSI-LD + Smart Data Models Context Interop Workbench Kit — context locks, @context receipts, and broker-portable semantic diffs
status: idea
domains: [iot, digital-twins, linked-data, smart-cities, context, interoperability, semantics]
last_reviewed: 2026-03-06
evidence:
  - https://ngsi-ld.org/
  - https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.09.01_60/gs_CIM009v010901p.pdf
  - https://smart-data-models.github.io/data-models/
  - https://github.com/FIWARE/context.Orion-LD
  - https://docs.rs/json-ld
---

# Problem

NGSI-LD is now a real cross-domain context API and information model, not a speculative smart-city curiosity. ETSI keeps publishing the API, Smart Data Models keep providing reusable model families and `@context` material, and production context brokers such as Orion-LD already exist.

But real deployments still fail at the seam between:

- **JSON payloads that look similar and payloads that expand to materially different linked-data graphs**,
- **model-family examples and the exact `@context` set a broker or client actually resolved**,
- **entity snapshots and the subscriptions / query semantics that produced them**,
- **cross-broker interoperability stories and the vendor-specific behavior hidden in pagination, expansion, temporal queries, or patch semantics**,
- and **digital-twin claims that collapse into screenshots, curl snippets, and manually hosted context files.**

The missing Rust contribution is not yet another context broker. It is a **context-interop workbench** that pins NGSI-LD revision, Smart Data Model assumptions, `@context` resolution, entity/query fixtures, and semantic diffs into one boring bundle.

# What it provides

- `ngsild.lock` — pins API revision, context sources, data-model pack, broker assumptions, and transport/profile options.
- `context-receipt` — records remote `@context` retrieval, caching, expansion, and compaction assumptions.
- `entity-diff` — semantic diff between two NGSI-LD payloads after JSON-LD processing.
- `query-replay` — compact artifact for replaying entity, subscription, and temporal-query cases.
- `cargo ngsild-workbench` — emits `*.ngsildbundle.zip` with fixtures, receipts, resolved contexts, and broker notes.

# What the crate should provide other people

1. **A boring interop bundle for context APIs**.
2. **A stable semantic diff** that sees more than raw JSON shape changes.
3. **Portable proof of which `@context` values were actually used**.
4. **A model-pack bridge** between ETSI NGSI-LD and Smart Data Model ecosystems.
5. **A Rust-native validation core** for CI, regression tests, and conformance labs.

# Persona / who it’s for

- digital-twin platform engineers
- context-broker and API implementers
- smart-city / smart-industry integrators
- linked-data and schema-governance teams

# Users & user stories

- **Integrator**: “Show me whether this is a real semantic incompatibility or just JSON formatting drift.”
- **Broker implementer**: “Replay the exact query/subscription fixture that failed against another broker.”
- **Model maintainer**: “Pin the `@context` set and example corpus used for this release.”
- **Incident responder**: “Package the failing entity/query/context interaction into one portable archive.”

# Prior art (and why it’s insufficient)

- NGSI-LD defines the information model and API.
- Smart Data Models define reusable model packs and examples.
- Orion-LD and other brokers implement real runtime behavior.
- Rust has strong JSON-LD substrate.

What Rust still lacks is a **semantic evidence layer** that ties model packs, remote contexts, broker behaviors, and replayable fixtures together.

# Design goals

1. **Context-explicit** — remote/local `@context` assumptions must be first-class.
2. **Semantics-first** — diff expanded meaning, not just JSON bytes.
3. **Broker-honest** — capture runtime behavior differences without pretending they are all normative.
4. **Replayable** — entity and query fixtures should be portable across brokers.
5. **Offline-capable** — bundles should work without live network dependencies.

# MVP surface

- Minimal types: `NgsiLock`, `ContextReceipt`, `EntityFixture`, `QueryReplay`, `SemanticDiff`, `NgsiBundle`
- Minimal functions:
  - `capture_contexts()`
  - `expand_entity()`
  - `diff_entities()`
  - `record_query_case()`
  - `write_bundle()`
- Feature flags:
  - `jsonld`
  - `subscriptions`
  - `temporal`
  - `smart-data-models`
  - `redaction`

# Compatibility story

- Builds above Rust JSON-LD substrate rather than requiring a Rust broker implementation.
- Supports offline corpus analysis and live-broker replay.
- Treats Smart Data Models as model packs and overlays, not as the core ontology.
- Keeps storage/indexing concerns out of the core.

# Conformance & fixtures

- Goldens for `@context` drift, compaction/expansion drift, relationship/property ambiguity, and temporal-query result changes.
- Tiny corpora for entities, subscriptions, and attribute patch/update cases.
- Broker fixture packs with local copies of resolved contexts.
- Redacted bundles safe for vendor bug reports.

# Path to boring stability

- Stabilize lockfiles, context receipts, and semantic diff output before broker adapters multiply.
- Start with offline semantic expansion + query fixture descriptions.
- Keep broker-specific transport notes as overlays.
- Resist drift into becoming a runtime platform.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 24/30**

# Minimum lovable MVP

A Rust library and CLI that pin an NGSI-LD revision plus `@context` set, expand entities through JSON-LD, emit semantic diffs, and package query fixtures and broker notes into `*.ngsildbundle.zip`.

# De-risk plan

1. Start with entity/context fixtures before full broker replay.
2. Vendor-neutralize around semantic diffs and receipts.
3. Ship local copies of contexts to avoid network flakiness.
4. Pilot with public Smart Data Model examples.

# Non-goals

- Not a context broker.
- Not a generic linked-data database.
- Not a digital-twin platform.
- Not a replacement for ETSI or FIWARE validators.

# Architecture & API sketch

```rust
pub struct NgsiLock {
    pub ngsi_ld_version: String,
    pub model_pack: String,
    pub context_digests: Vec<String>,
    pub broker_family: Option<String>,
}

pub fn capture_contexts(urls: &[String]) -> Result<ContextReceipt>;
pub fn expand_entity(doc: &str, receipt: &ContextReceipt) -> Result<ExpandedEntity>;
pub fn diff_entities(a: &ExpandedEntity, b: &ExpandedEntity) -> SemanticDiff;
pub fn write_bundle(bundle: &NgsiBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `ngsild.lock`, `contexts/`, `entities/`, `query-replay.json`, `semantic-diff.json`, `broker-notes.md`, `redaction-map.json`.

# Security / safety model

- Support redaction of identifiers, coordinates, tenant headers, and private endpoints.
- Capture remote `@context` material locally for evidence without live re-fetch.
- Keep observed broker behavior distinct from inferred semantic equivalence.
- Mark unresolved or partially expanded terms explicitly.

# Maintenance & governance plan

- Track ETSI NGSI-LD revisions explicitly.
- Treat Smart Data Models and broker fixtures as versioned overlays.
- Publish a tiny public corpus for regressions.
- Keep the core focused on locks, receipts, diffs, and replay.

# Milestones

## 0.1
- `ngsild.lock`
- context receipt
- semantic diff for entity fixtures

## 0.2
- query/subscription replay cases
- broker overlay notes
- redacted public corpus

## 1.0
- stable `*.ngsildbundle.zip`
- compatibility policy for context/model packs
- CI-friendly semantic approval gates

# Open questions

- Which broker behaviors belong in the portable core versus broker overlays?
- How should the bundle represent partial JSON-LD expansion when remote contexts are unavailable or intentionally pruned?
- What is the smallest common corpus that still catches real cross-broker semantic drift?

# Sources

- NGSI-LD home: https://ngsi-ld.org/
- ETSI NGSI-LD API 1.9.1: https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.09.01_60/gs_CIM009v010901p.pdf
- Smart Data Models catalogue: https://smart-data-models.github.io/data-models/
- Orion-LD broker: https://github.com/FIWARE/context.Orion-LD
- `json-ld` crate docs: https://docs.rs/json-ld
