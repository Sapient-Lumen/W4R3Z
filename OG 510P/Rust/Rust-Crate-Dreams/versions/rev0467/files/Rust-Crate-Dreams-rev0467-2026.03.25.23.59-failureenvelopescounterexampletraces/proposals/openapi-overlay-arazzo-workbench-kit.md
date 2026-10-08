---
id: P-0402
title: OpenAPI Overlay + Arazzo Workflow Workbench Kit — deterministic transforms, workflow locks, and explainable API-pipeline receipts
status: idea
domains: [api, interoperability, tooling, workflow, validation, automation]
last_reviewed: 2026-03-06
evidence:
  - https://spec.openapis.org/overlay/latest.html
  - https://spec.openapis.org/arazzo/latest.html
  - https://www.openapis.org/blog/2025/01/24/announcing-arazzo-specification-version-1-0-1
  - https://docs.rs/arazzo-models
  - https://docs.rs/openapiv3
---

# Problem

The OpenAPI ecosystem is no longer just “one spec and some generators.” There is now a serious multi-specification surface: OpenAPI descriptions, Overlay documents for deterministic transformations, and Arazzo workflows for multi-step API stories. Rust has started to grow substrate here too—`openapiv3` is widely used for OAS models and `arazzo-models` now gives Rust a native foothold for workflow documents.

But the painful failures still happen at the seam between:

- **a source OpenAPI document and the exact overlay actions that transformed it**,
- **workflow descriptions and the concrete API versions they were written against**,
- **human-facing API guidance and machine-applied transformation pipelines**,
- **JSON Schema validation and the semantic meaning of ordered overlay actions or workflow step dependencies**,
- and **toolchains that can parse pieces of the stack but still cannot emit a boring, explainable receipt for what changed and why.**

The missing Rust contribution is not another OpenAPI parser. It is a **workflow-and-transform workbench** for overlay locks, workflow/source pinning, semantic diffs, and portable evidence bundles.

# What it provides

- `api-pipeline.lock` — pins OpenAPI source hashes, Overlay version/features, Arazzo document version, source-description bindings, and transform ordering.
- `overlay-ir` — normalized representation of ordered overlay actions and their semantic targets.
- `workflow-receipt` — portable artifact linking Arazzo steps to the exact API descriptions and transformed operations they referenced.
- `semantic-diff` — explains meaningful API changes after overlays are applied, not just text diffs before/after.
- `cargo api-pipeline-evidence` — emits `*.apipipelinebundle.zip` with locks, transformed outputs, findings, and notes.

# What the crate should provide other people

1. **A boring receipt for API-document pipelines**.
2. **Deterministic overlay application** with explainable action ordering.
3. **Workflow pinning** that makes Arazzo descriptions auditable against real source documents.
4. **Semantic diffs after transformation**, not only before/after YAML churn.
5. **A neutral artifact for review, CI, and handoff** across API teams.

# Persona / who it’s for

- API platform teams managing description pipelines
- Rust backend teams generating or checking OpenAPI documents in CI
- Tool authors building validators, SDK generators, or governance layers
- Integration teams debugging workflow breakage across API revisions

# Users & user stories

- **Platform engineer**: “Show me exactly which overlay action changed this operation and whether the result still matches the workflow.”
- **Integrator**: “Pin the exact API documents my Arazzo workflow was validated against.”
- **Tool author**: “Apply overlays deterministically and compare semantic results without inventing my own IR.”
- **Reviewer**: “Open one bundle and see sources, transforms, workflow bindings, and compatibility findings.”

# Prior art (and why it’s insufficient)

- The OpenAPI Initiative now publishes Overlay and Arazzo specifications with schemas and active release cadence.
- Rust already has `openapiv3` and `arazzo-models` as meaningful substrate.
- Existing tooling tends to validate or transform one layer at a time.

What Rust still lacks is a **coordination artifact** for pinned source documents, ordered transforms, workflow/source receipts, and semantic post-transform diffs.

# Design goals

1. **Order-explicit** — overlay action ordering must be first-class, not an implementation detail.
2. **Workflow-grounded** — Arazzo steps must be linked to real, pinned API descriptions.
3. **Semantic-first** — compare operation meaning, not only raw YAML/JSON text.
4. **Layer-honest** — OpenAPI, Overlay, and Arazzo must remain distinct surfaces in the model.
5. **Incrementally adoptable** — useful even before deep runtime/test execution integrations exist.

# MVP surface

- Minimal types: `ApiPipelineLock`, `OverlayIr`, `WorkflowReceipt`, `SemanticFinding`, `ApiPipelineBundle`
- Minimal functions:
  - `load_openapi()`
  - `apply_overlay()`
  - `bind_workflow_sources()`
  - `diff_semantics()`
  - `write_bundle()`
- Feature flags:
  - `openapi`
  - `overlay`
  - `arazzo`
  - `json-schema`

# Compatibility story

- Works above existing Rust OpenAPI/Arazzo model crates.
- Supports source docs in YAML or JSON.
- Can start as an offline workbench for description files and generated artifacts.
- Keeps runtime execution and HTTP testing out of the core model.

# Conformance & fixtures

- Goldens for overlay action ordering, target misses, copy/update/remove behavior, and transform conflicts.
- Mini corpora for workflow/source binding drift and missing operation references.
- Fixtures where the same source OpenAPI plus different overlays produce materially different workflow validity outcomes.
- Public bundles small enough for CI artifact review.

# Path to boring stability

- Stabilize the lockfile, overlay IR, and semantic diff schema before expanding runtime adapters.
- Start with offline transforms and workflow/source binding checks.
- Keep document transformation and workflow validation separate but linkable.
- Treat OpenAPI 4.0 / future Arazzo revisions as overlays, not hidden assumptions.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin OpenAPI/Overlay/Arazzo inputs, deterministically apply overlays, bind workflows to their real source descriptions, compute semantic diffs, and emit compact `*.apipipelinebundle.zip` artifacts.

# De-risk plan

1. Start with OpenAPI + Overlay only.
2. Add Arazzo source binding and workflow receipts next.
3. Keep JSON Schema validation as an adapter, not the core source of truth.
4. Pilot in CI and review pipelines before expanding into runtime execution tooling.

# Non-goals

- Not an API gateway.
- Not an SDK generator.
- Not a full workflow execution engine.
- Not a replacement for the OpenAPI Initiative’s own specifications or schemas.

# Architecture & API sketch

```rust
pub struct ApiPipelineLock {
    pub openapi_sources: Vec<String>,
    pub overlay_version: String,
    pub arazzo_version: Option<String>,
    pub source_hashes: Vec<String>,
}

pub fn load_openapi(path: &std::path::Path) -> Result<OpenApiIr>;
pub fn apply_overlay(doc: &OpenApiIr, overlay: &OverlayIr) -> Result<OpenApiIr>;
pub fn bind_workflow_sources(lock: &ApiPipelineLock, workflow: &ArazzoIr) -> Vec<SemanticFinding>;
```

Bundle draft: `api-pipeline.lock`, `openapi-source.json`, `overlay.yaml`, `transformed-openapi.json`, `workflow-receipt.json`, `findings.json`, `notes.md`.

# Security / safety model

- Support redaction of internal server URLs, auth hints, and proprietary vendor extensions.
- Distinguish source-of-truth descriptions from transformed outputs in every bundle.
- Preserve action ordering and source hashes so receipts are replayable.
- Keep workflow execution out of scope unless explicitly adapter-backed.

# Maintenance & governance plan

- Keep the core about locks, transforms, workflow binding, and semantic diffs.
- Version OpenAPI, Overlay, and Arazzo surfaces independently.
- Publish a tiny public corpus of overlay/workflow fixtures.
- Resist drift into becoming a monolithic API platform.

# Milestones

## 0.1
- `api-pipeline.lock`
- overlay IR
- deterministic transform + semantic diff

## 0.2
- Arazzo source binding
- workflow receipts
- public fixture corpus

## 1.0
- stable `*.apipipelinebundle.zip`
- documented compatibility policy for OpenAPI / Overlay / Arazzo versions
- CI-friendly gating outputs

# Open questions

- What is the best stable IR for post-overlay semantic comparison?
- How much of Arazzo step validation should be structural versus execution-aware?
- Should vendor/tool-specific extensions live as overlays or as namespaced receipt attachments?

# Sources

- Overlay Specification latest: https://spec.openapis.org/overlay/latest.html
- Arazzo Specification latest: https://spec.openapis.org/arazzo/latest.html
- Arazzo 1.0.1 release note: https://www.openapis.org/blog/2025/01/24/announcing-arazzo-specification-version-1-0-1
- `arazzo-models`: https://docs.rs/arazzo-models
- `openapiv3`: https://docs.rs/openapiv3
