---
id: P-0387
title: OpenLineage + Marquez + Facet Evidence Kit — lineage locks, facet-schema discipline, and replayable incident bundles
status: idea
domains: [data, lineage, interoperability, observability, metadata, validation]
last_reviewed: 2026-03-06
evidence:
  - https://openlineage.io/docs/
  - https://openlineage.io/docs/spec/object-model
  - https://openlineage.io/docs/spec/facets/custom-facets/
  - https://github.com/MarquezProject/marquez
---

# Problem

OpenLineage has grown into a real interoperability surface for lineage metadata, with a core model around jobs, runs, datasets, and extensible facets. Marquez provides a widely recognized reference backend and UI. That means the basic substrate now exists.

But operators still lose time at the seam between:

- **runtime lineage events and design-time/job metadata**,
- **naming strategy differences for datasets and namespaces**,
- **facet sprawl and custom-facet schema drift**,
- **what one producer emits and what another consumer or backend actually understands**,
- and **incident handoff artifacts that currently consist of screenshots, raw JSON blobs, and guesses**.

The missing Rust contribution is not another lineage backend. It is an **evidence workbench** that turns lineage events, facet schemas, naming assumptions, and backend behavior into boring, portable artifacts.

# What it provides

- `lineage.lock` — pins OpenLineage spec version, required standard facets, allowed custom-facet prefixes, schema URLs, naming rules, and backend expectations.
- `lineage-ir` — normalized IR connecting `RunEvent`, `JobEvent`, dataset identifiers, lifecycle states, and facet payloads.
- `facet-lint` — validates `_schemaURL`, prefix hygiene, required fields, and version drift across emitted events.
- `graph-diff` — computes explainable semantic diffs between two lineage bundles without pretending JSON-equality is semantic-equality.
- `cargo lineage-evidence` — emits `*.lineagebundle.zip` with normalized events, findings, redactions, and optional Marquez snapshots.

# What the crate should provide other people

1. **A boring incident bundle for lineage bugs**.
2. **Explicit rules for custom-facet governance** instead of “we just added a field”.
3. **Naming-strategy diffs** for dataset/job identity drift.
4. **Portable validation outputs** that survive handoff across orchestration, platform, and data-governance teams.
5. **A Rust-native way to compare emitted lineage with what a backend/UI actually rendered or retained**.

# Persona / who it’s for

- Data-platform engineers instrumenting jobs
- Maintainers of Rust-based pipeline/orchestration integrations
- Metadata/governance teams reviewing lineage quality
- Support engineers debugging broken lineage graphs

# Users & user stories

- **Integration maintainer**: “Show me whether the bug is in event emission, naming strategy, or custom-facet schema drift.”
- **Platform engineer**: “Pin which facets and schema URLs production is allowed to emit.”
- **Governance team**: “Compare what the producer emitted with what the backend retained.”
- **Support engineer**: “Send a compact redacted artifact instead of asking for a full Marquez export and app logs.”

# Prior art (and why it’s insufficient)

- OpenLineage defines the core event model, schema surfaces, and facet extensibility.
- Marquez provides a reference metadata service and visualization layer.
- Various ecosystems already emit OpenLineage events.

What Rust still lacks is a **single evidence-grade layer** for event normalization, custom-facet discipline, naming-strategy locks, semantic diffs, and incident bundles.

# Design goals

1. **Schema-aware, not blob-aware** — reason about entity/facet semantics, not raw JSON only.
2. **Facet-discipline first** — custom facets must be explicit, versioned, and explainable.
3. **Backend-neutral** — useful with or without Marquez, while still being able to compare against Marquez.
4. **Redaction-friendly** — evidence must work for production incidents.
5. **Lineage-graph honest** — distinguish missing events, collapsed identifiers, and unsupported facets.

# MVP surface

- Minimal types: `LineageLock`, `NormalizedEvent`, `FacetFinding`, `GraphDiff`, `LineageBundle`
- Minimal functions:
  - `ingest_events()`
  - `lint_facets()`
  - `diff_graphs()`
  - `write_bundle()`
- Feature flags:
  - `openlineage-json`
  - `marquez`
  - `redaction`
  - `schema-cache`

# Compatibility story

- Works above OpenLineage emitters and backends; does not replace them.
- Accepts runtime and design-time OpenLineage events.
- Can optionally compare emitted events against a Marquez snapshot/export.
- Treats custom facets as first-class but policy-controlled.

# Conformance & fixtures

- Tiny corpora for namespace drift, duplicated run IDs, missing lifecycle events, incompatible custom facets, and dataset version disagreements.
- Goldens for “same semantic lineage, different JSON ordering or producer metadata”.
- Public fixtures for producer-specific facet shapes.
- Adapter tests against Marquez ingestion/export behavior when practical.

# Path to boring stability

- Stabilize `lineage.lock` and bundle layout before broadening adapters.
- Keep the MVP at event/facet/graph evidence, not full catalog features.
- Version custom-facet policy aggressively.
- Make redaction deterministic and visible in every bundle.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that ingest OpenLineage events, pin facet/naming assumptions, explain semantic diffs, and emit compact `*.lineagebundle.zip` artifacts for incident handoff.

# De-risk plan

1. Start with raw OpenLineage JSON + schema validation.
2. Add custom-facet policy and naming-strategy linting before backend adapters.
3. Keep Marquez comparison optional.
4. Use digest-only mode for sensitive payloads.

# Non-goals

- Not a metadata catalog.
- Not a lineage graph database.
- Not a replacement for Marquez or other backends.
- Not a universal data-governance platform.

# Architecture & API sketch

```rust
pub struct LineageLock {
    pub spec_version: String,
    pub required_facets: Vec<String>,
    pub custom_facet_prefixes: Vec<String>,
    pub naming_profile: String,
}

pub fn ingest_events(input: EventInput) -> Result<LineageBundle>;
pub fn lint_facets(bundle: &LineageBundle, lock: &LineageLock) -> Vec<FacetFinding>;
pub fn diff_graphs(a: &LineageBundle, b: &LineageBundle) -> GraphDiff;
```

Bundle draft: `lineage.lock`, `events.ndjson`, `normalized/graph.json`, `schemas/`, `findings.json`, `redactions.json`, `notes.md`.

# Security / safety model

- Support digest-only evidence and payload redaction.
- Cache facet schemas by explicit URL/version, not best-effort scraping.
- Mark producer/backend versions in every bundle.
- Treat event ordering and timestamp claims as evidence, not truth.

# Maintenance & governance plan

- Keep the core about lockfiles, normalization, and evidence.
- Version producer adapters independently if necessary.
- Maintain a small public corpus of tricky facet and naming cases.
- Resist drift into backend hosting, catalog UX, or policy warehousing.

# Milestones

## 0.1
- OpenLineage JSON ingestion
- `lineage.lock`
- custom-facet linting

## 0.2
- graph diffing
- redaction support
- Marquez comparison adapter

## 1.0
- stable `*.lineagebundle.zip`
- documented naming-profile policy
- public fixture corpus

# Open questions

- How strict should schema fetching/caching be for custom facets?
- What is the smallest stable IR that still preserves graph semantics?
- Which producer-specific quirks are worth first-class adapters?

# Sources

- OpenLineage docs: https://openlineage.io/docs/
- OpenLineage object model: https://openlineage.io/docs/spec/object-model
- OpenLineage custom facets: https://openlineage.io/docs/spec/facets/custom-facets/
- Marquez reference implementation: https://github.com/MarquezProject/marquez
