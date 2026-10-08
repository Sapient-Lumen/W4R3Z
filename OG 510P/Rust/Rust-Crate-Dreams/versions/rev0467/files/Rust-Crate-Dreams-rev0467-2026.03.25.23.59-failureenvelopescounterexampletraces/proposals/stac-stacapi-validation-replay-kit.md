---
id: P-0334
title: STAC 1.1 + STAC API Validation & Replay Kit — profile-pinned geospatial catalogs, semantic item diffs, and reproducible search/evidence bundles
status: idea
domains: [geospatial, metadata, catalogs, stac, api, interoperability, remote-sensing]
last_reviewed: 2026-03-06
evidence:
  - https://www.ogc.org/standards/stac/
  - https://github.com/radiantearth/stac-spec/releases
  - https://github.com/radiantearth/stac-api-spec
  - https://github.com/stac-utils/stac-check
  - https://docs.rs/stac
  - https://docs.rs/stac-api
  - https://crates.io/crates/stac-server
---

# Problem

The STAC ecosystem is now mature enough that the hard problem is rarely “can I serialize an Item?” The operational pain is in **profiles, extensions, API behavior, and dataset drift**:

- catalogs that are structurally valid JSON but semantically inconsistent,
- STAC APIs that return different shapes or link relations than clients expect,
- extension-heavy items whose asset semantics drift across provider releases,
- search bugs that depend on a particular query sequence rather than a single static JSON file,
- and bug reports that still move around as screenshots or pasted responses instead of replayable search evidence.

Rust already has real STAC substrate, including data structures and servers. The missing worthy contribution is a **validation and replay kit** that turns STAC documents and STAC API interactions into deterministic, explainable, portable evidence.

# What it provides

- `stac-ir` — canonical Rust IR for catalogs, collections, items, item-assets, common metadata, links, and extension declarations.
- `api-lockfile` — pinning for STAC API features, supported conformance classes, extension expectations, auth/base-URL assumptions, and query examples.
- `validator-adapter` — normalized wrappers for STAC validation/linting surfaces into stable Rust verdicts.
- `query-replay` — deterministic capture/replay for search requests, pagination, sort, field selection, and response summaries.
- `stac-diff` — semantic diffs: “asset role changed”, “item-assets moved into core fields”, “projection metadata disappeared”, “search results no longer stable under same query”.
- `cargo stac-evidence` — emit `*.stacbundle.zip` for provider onboarding, CI, or cross-team debugging.

# What the crate should provide other people

1. **A boring way to debug STAC incidents** across both static JSON and live APIs.
2. **Profile pinning** for the exact extension and conformance assumptions a client/server depends on.
3. **Semantic diffs** for evolving catalogs and collections.
4. **Replayable query evidence** instead of hand-written curl examples.
5. **A neutral layer** above storage backends, STAC servers, and provider-specific pipelines.

# Persona / who it’s for

- Geospatial platform engineers
- Remote-sensing data providers
- Client/SDK authors
- Catalog/search infrastructure teams
- Rust developers building STAC tooling

# Users & user stories

- **Provider engineer**: “Prove that our STAC API still satisfies the pinned profile after this backend migration.”
- **Client author**: “Replay the exact search sequence that produced a bad pagination or field-selection bug.”
- **Data steward**: “Diff these two collection releases semantically, not just by raw JSON.”
- **Integrator**: “Package a minimal, reproducible STAC incident without exporting the whole catalog.”

# Prior art (and why it’s insufficient)

- STAC 1.1 is stable and public.
- The STAC API spec is explicit about composable conformance classes.
- Community validation/lint tools exist.
- Rust has `stac`, `stac-api`, and `stac-server` substrate.
- But there is still no boring-default Rust crate family for **profile pinning + validation normalization + query replay + semantic STAC diffs + portable evidence bundles**.

# Design goals

1. **Document + API continuity** — static STAC and live STAC API behaviors must be representable together.
2. **Extension explicitness** — extension assumptions should never be implicit.
3. **Semantic diffs over JSON diffs** — findings should talk like geospatial metadata, not line-oriented patches.
4. **Replayable search behavior** — because many failures only emerge across request sequences.
5. **Implementation neutrality** — useful for static hosting, databases, lambda/serverless stacks, or full servers.

# MVP surface

- Minimal types: `CatalogSnapshot`, `ApiSnapshot`, `StacProfile`, `ValidationReport`, `ReplayCase`
- Minimal functions:
  - `load_catalog()`
  - `run_validator()`
  - `capture_query()`
  - `verify_profile()`
  - `diff_catalogs()`
  - `write_bundle()`
- Feature flags:
  - `stac`
  - `api`
  - `geojson`
  - `serde`
  - `redaction`

# Compatibility story

- MVP should target **STAC 1.1** and the core STAC API conformance classes first.
- It should consume existing Rust or non-Rust STAC servers via HTTP adapters and snapshot files.
- It should complement validators and hosted servers rather than trying to replace them.
- MVP should intentionally avoid becoming another full STAC server product.

# Conformance & fixtures

- Tiny static catalog fixtures with collections/items that exercise core fields, item-assets, and selected extensions.
- API replay fixtures covering pagination, item search, filter/query parameters, and response invariants.
- Positive/negative examples for link relations, asset roles, bbox/geometry mismatches, and extension drift.
- Optional adapters for stac-check or similar validator outputs.

# Path to boring stability

- First stabilize the IR and finding vocabulary.
- Then prove query-replay bundles remain useful across a small set of servers/backends.
- Freeze bundle layout only after redaction and response summarization remain stable.
- Keep extension packs additive and clearly versioned.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A CLI and library that validate one STAC catalog or API against a pinned 1.1 profile, capture and replay a small search sequence, diff the catalog against a prior snapshot, and emit a redactable `*.stacbundle.zip`.

# De-risk plan

1. Start with static catalogs plus read-only API replay.
2. Wrap existing validation surfaces rather than creating a new canonical validator first.
3. Keep extension coverage narrow and explicit in profiles.
4. Prove the replay model on one static host and one Rust STAC server.

# Non-goals

- Not a full STAC server replacement.
- Not a data-ingestion pipeline.
- Not a full geospatial analytics engine.

# Architecture & API sketch

```rust
pub struct ValidationReport {
    pub profile_id: String,
    pub document_findings: Vec<Finding>,
    pub api_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_profile(profile: &StacProfile, catalog: &CatalogSnapshot) -> ValidationReport;
pub fn capture_query(profile: &StacProfile, request: &HttpRequest) -> Result<ReplayCase>;
```

Bundle draft: `profile.toml`, `catalog/`, `queries/`, `responses/`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact signed URLs, bearer tokens, and internal endpoints.
- Bound response capture sizes and external link traversal.
- Preserve enough query/response structure for semantic debugging after redaction.
- Record validator and server/profile assumptions explicitly.

# Maintenance & governance plan

- Keep extension packs and API conformance assumptions data-driven.
- Separate HTTP replay from STAC semantics so the core stays maintainable.
- Use small public fixture catalogs as regression seeds.
- Treat server-specific quirks as profiles/adapters unless they recur across implementations.

# Milestones

## 0.1
- STAC IR
- validator adapter
- static bundle writer

## 0.2
- API replay
- semantic diffs
- redaction support

## 1.0
- Stable `*.stacbundle.zip`
- regression corpus across multiple servers/providers
- documented extension/profile policy

# Open questions

- Which extension families should be first-class in MVP versus left to profile packs?
- How much of API replay belongs in core versus a shared evidence-bundle layer?
- Can field-level result diffs stay semantic without becoming provider-specific?

# Sources

- OGC STAC overview: https://www.ogc.org/standards/stac/
- STAC spec releases: https://github.com/radiantearth/stac-spec/releases
- STAC API spec: https://github.com/radiantearth/stac-api-spec
- `stac-check`: https://github.com/stac-utils/stac-check
- `stac`: https://docs.rs/stac
- `stac-api`: https://docs.rs/stac-api
- `stac-server`: https://crates.io/crates/stac-server
