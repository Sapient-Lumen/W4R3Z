---
id: P-0358
title: OData 4.01/4.02 + CSDL Conformance & Replay Kit — query lockfiles, metadata drift diffs, and portable API evidence bundles
status: idea
domains: [enterprise, apis, data-models, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://oasis-tcs.github.io/odata-specs/odata-protocol/odata-protocol.html
  - https://docs.oasis-open.org/odata/odata-csdl-json/v4.02/odata-csdl-json-v4.02.html
  - https://docs.oasis-open.org/odata/odata-json-format/v4.02/odata-json-format-v4.02.html
  - https://crates.io/crates/odata-params
  - https://docs.rs/odata_client_codegen
  - https://docs.rs/reso-client
---

# Problem

Rust can already parse pieces of OData and generate typed clients from some metadata surfaces, but the operational pain in OData ecosystems usually lives between:

- `$metadata` / CSDL evolution and client expectations,
- query-option support (`$filter`, `$select`, `$expand`, paging, ordering) versus actual runtime behavior,
- JSON payload shapes and annotation behavior,
- vendor/profile quirks in enterprise APIs,
- and API regressions that are difficult to replay outside the original service.

The missing crate is not “yet another OData client.” It is a **metadata-aware conformance and replay workbench** for OData services and generated Rust consumers.

# What it provides

- `odata-ir` — stable IR for CSDL, service capabilities, request cases, and normalized payload/result shapes.
- `odata-lock` — lockfiles pinning protocol version, metadata hashes, supported query options, annotation expectations, and vendor/profile overlays.
- `odata-replay` — import/export portable request cases with expected semantics and normalized result sets.
- `odata-check` — compare live service behavior against a pinned lock or fixture pack.
- `odata-diff` — semantic diffs such as “metadata changed but query still works”, “server now rejects ordered collections”, or “payload annotations drifted”.
- `cargo odata-evidence` — emit `*.odatabundle.zip` for CI, codegen regeneration, and vendor support escalations.

# What the crate should provide other people

1. **A boring artifact for OData API regressions**.
2. **Pinned metadata and query-surface expectations** for generated or hand-written clients.
3. **Replayable request cases** independent of a specific frontend or application.
4. **Explainable diffs between metadata revisions and runtime behavior**.
5. **A neutral bridge between OData services, Rust codegen, and CI policy**.

# Persona / who it’s for

- Rust teams consuming or exposing OData APIs
- Enterprise integration engineers
- API platform and metadata-governance maintainers
- Codegen authors
- Teams integrating with OData-heavy ecosystems such as SAP, Microsoft, or RESO-style APIs

# Users & user stories

- **Integration engineer**: “Show me whether the breakage came from metadata drift or actual query behavior.”
- **Client maintainer**: “Pin this service’s supported options so a regenerated client cannot silently assume more.”
- **Platform engineer**: “Replay a real failing request against staging and prod and diff the semantics.”
- **QA maintainer**: “Compare two service versions without hand-checking large JSON payloads.”

# Prior art (and why it’s insufficient)

- OData has official protocol, CSDL, and JSON-format specifications.
- Rust already has `odata-params`, older client/codegen crates, and domain-specific OData consumers such as `reso-client`.
- But Rust still lacks a boring-default crate for **metadata locks + request replay + semantic diffs + portable evidence**.

# Design goals

1. **Metadata-first** — treat CSDL drift as a first-class source of bugs.
2. **Query-surface aware** — focus on real OData semantics, not just HTTP snapshots.
3. **Vendor-neutral core** — support profile/quirk packs without baking them into the IR.
4. **Replayable and deterministic** — cases must survive service upgrades and CI reruns.
5. **Codegen-friendly** — useful whether clients are generated or hand-written.

# MVP surface

- Minimal types: `ODataLock`, `MetadataSnapshot`, `ReplayCase`, `ODataReport`, `ODataDiffFinding`
- Minimal functions:
  - `snapshot_metadata()`
  - `normalize_payload()`
  - `run_replay_case()`
  - `diff_services()`
  - `write_bundle()`
- Feature flags:
  - `csdl-json`
  - `csdl-xml`
  - `query`
  - `codegen`
  - `redaction`

# Compatibility story

- MVP should target stable OData 4.01 behavior plus explicit watch-mode support for 4.02-era metadata and payload surfaces.
- The core should work with both generated clients and generic HTTP-driven cases.
- Vendor-specific annotations or query extensions can live in optional profile packs.
- The crate should complement existing codegen/client crates rather than replace them.

# Conformance & fixtures

- Tiny metadata documents with deliberate drift in entity sets, nullable fields, or annotations.
- Query cases covering `$filter`, `$orderby`, `$top`, `$skip`, `$expand`, and paging.
- Payload goldens for annotation presence/absence and ordered versus unordered collections.
- Cases for “metadata says allowed, runtime rejects”, “runtime changed ordering semantics”, and “codegen hash changed but behavior did not”.

# Path to boring stability

- Freeze the replay-case and diff schemas before growing vendor packs.
- Keep the early query surface intentionally narrow and explainable.
- Prefer metadata and payload normalization over lots of custom rule logic.
- Add deeper query coverage only after the lockfile format is useful in real services.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that capture a service’s metadata, replay a small suite of OData queries, compare the results against a pinned lockfile, and emit a compact `*.odatabundle.zip`.

# De-risk plan

1. Start with read/query semantics rather than create/update/delete coverage.
2. Keep vendor quirks out of the core schema.
3. Treat metadata hashing and payload normalization as foundational before broadening query grammar support.
4. Validate the bundle model against one generated-client workflow and one generic HTTP workflow.

# Non-goals

- Not a new generic OData client framework.
- Not a full OData server implementation.
- Not a replacement for business-domain SDKs.
- Not an API gateway product.

# Architecture & API sketch

```rust
pub struct ODataReport {
    pub lock_id: String,
    pub findings: Vec<Finding>,
    pub diffs: Vec<ODataDiffFinding>,
}

pub fn snapshot_metadata(metadata: &[u8], format: CsdlFormat) -> Result<MetadataSnapshot>;
pub fn run_replay_case(lock: &ODataLock, case: &ReplayCase) -> Result<ODataReport>;
```

Bundle draft: `profile.toml`, `metadata.json`, `metadata.xml`, `cases.jsonl`, `responses.json`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat service metadata and payloads as untrusted input.
- Default to redaction of hostnames, bearer tokens, and PII-like fields.
- Record exact protocol/profile versions and metadata hashes.
- Keep normalized results deterministic and diff-friendly.

# Maintenance & governance plan

- Keep the core focused on metadata IR, replay, diffing, and bundle layout.
- Version vendor/profile packs separately.
- Build a small public corpus of tricky metadata/query cases.
- Avoid binding the crate to one HTTP client or one codegen path.

# Milestones

## 0.1
- metadata snapshotting
- query-case runner
- bundle writer

## 0.2
- semantic diffs
- codegen compatibility hooks
- optional vendor overlays

## 1.0
- stable `*.odatabundle.zip`
- public fixture corpus
- documented policy for 4.01 base support and 4.02 overlay packs

# Open questions

- What is the minimum useful representation of capabilities without modeling every vocabulary?
- How much of pagination and server-driven paging should be normalized versus preserved verbatim?
- Which annotation families belong in neutral core support?

# Sources

- OData Version 4.02 Part 1: Protocol: https://oasis-tcs.github.io/odata-specs/odata-protocol/odata-protocol.html
- OData CSDL JSON Representation 4.02: https://docs.oasis-open.org/odata/odata-csdl-json/v4.02/odata-csdl-json-v4.02.html
- OData JSON Format 4.02: https://docs.oasis-open.org/odata/odata-json-format/v4.02/odata-json-format-v4.02.html
- `odata-params`: https://crates.io/crates/odata-params
- `odata_client_codegen`: https://docs.rs/odata_client_codegen
- `reso-client`: https://docs.rs/reso-client
