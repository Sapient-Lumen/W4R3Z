---
id: P-0373
title: Protobuf Editions + ProtoJSON + gRPC Transcoding Conformance Workbench Kit — descriptor locks, cross-format diffs, and gateway replay artifacts
status: idea
domains: [protobuf, api-infrastructure, schema, codegen, interoperability, testing, rpc, json]
last_reviewed: 2026-03-06
evidence:
  - https://protobuf.dev/editions/overview/
  - https://protobuf.dev/editions/implementation/
  - https://protobuf.dev/programming-guides/json/
  - https://github.com/tokio-rs/prost
  - https://github.com/tokio-rs/prost/issues/1031
  - https://docs.cloud.google.com/apis/design
  - https://cloud.google.com/apis/design/custom_methods
---

# Problem

Rust has strong protobuf substrate in `prost` and related crates, but the painful failures are no longer just “can I parse the wire format?” They sit at the seam between:

- schema editions and feature settings,
- descriptor sets and generated Rust APIs,
- binary protobuf and ProtoJSON behavior,
- `google.api.http` transcoding rules and actual gateway behavior,
- and compatibility claims that are easy to make but hard to prove across versions.

The missing Rust contribution is not another protobuf runtime. It is a **descriptor- and evidence-centered conformance workbench** that makes cross-format and cross-edition drift visible.

# What it provides

- `schema-lock` — lockfiles pinning edition/features, descriptor set hashes, well-known type assumptions, and gateway/transcoding overlays.
- `proto-irx` — a neutral IR for descriptors, field presence, unknowns, JSON mapping findings, and transcoding expectations.
- `conformance-pack` — replayable cases for binary, ProtoJSON, enum/unknown behavior, oneofs, maps, WKTs, and HTTP mappings.
- `gateway-diff` — semantic diffs between descriptor intent, JSON behavior, and HTTP/gRPC transcoding surfaces.
- `cargo proto-evidence` — emits `*.protobundle.zip` with descriptors, lockfile, test vectors, normalized findings, and compatibility notes.

# What the crate should provide other people

1. **A boring default artifact for protobuf compatibility claims**.
2. **Explicit edition/feature locks** instead of hand-wavy “proto2/proto3 compatible”.
3. **Cross-format diffs** for binary, JSON, and transcoded HTTP behavior.
4. **Gateway debugging artifacts** that explain which mapping rule actually changed.
5. **A shared conformance surface for Rust protobuf libraries and API teams**.

# Persona / who it’s for

- API platform teams using protobuf + REST/gRPC gateways
- Rust maintainers building protobuf, reflection, or gateway tooling
- CI/release engineers proving schema-compatibility promises
- Infra teams migrating between protobuf editions or gateway stacks

# Users & user stories

- **API maintainer**: “Show me whether this schema change is binary-safe but JSON-unsafe.”
- **Gateway operator**: “Diff the intended `google.api.http` surface against the actual deployed behavior.”
- **Library maintainer**: “Run a stable conformance corpus against `prost`-based tooling.”
- **Upgrade owner**: “Pin exactly which edition/features are in scope for this release.”

# Prior art (and why it’s insufficient)

- Protobuf editions formalize language evolution.
- ProtoJSON has a canonical spec plus additional conformance-suite edge cases.
- Rust has strong protobuf generation/runtime substrate in `prost` and friends.
- HTTP/gRPC transcoding has long-running design guidance and broad deployment.

What Rust still lacks is a **boring default workbench** for descriptor locks, JSON/transcoding diffs, and evidence bundles that other teams can exchange.

# Design goals

1. **Descriptor-first** — the descriptor set is the core review surface.
2. **Cross-format honest** — binary compatibility does not imply JSON or transcoding compatibility.
3. **Edition-aware** — edition/features belong in the lockfile, not in tribal memory.
4. **Gateway-grounded** — compare descriptor intent with observed HTTP behavior.
5. **Runtime-neutral** — help `prost`-based ecosystems without demanding one runtime or gateway.

# MVP surface

- Minimal types: `SchemaLock`, `DescriptorReport`, `JsonMappingFinding`, `TranscodingFinding`, `ProtoBundle`
- Minimal functions:
  - `inspect_descriptors()`
  - `run_protojson_cases()`
  - `diff_schema_locks()`
  - `write_bundle()`
- Feature flags:
  - `protojson`
  - `transcoding`
  - `reflection`
  - `well-known-types`
  - `recording`

# Compatibility story

- Builds above existing descriptor/protobuf crates instead of replacing them.
- Can start with descriptor sets generated elsewhere.
- Treats gateway or transcoder integrations as adapters.
- Supports edition/feature overlays incrementally as Rust substrate matures.

# Conformance & fixtures

- Tiny fixtures for enums, unknown values, presence, oneofs, maps, WKTs, and field-name casing.
- Goldens for “binary-compatible but ProtoJSON-breaking” and “same schema, different HTTP surface”.
- Descriptor diff fixtures for added/removed/renamed fields and option changes.
- Gateway fixtures for path captures, body mappings, custom methods, and repeated query params.

# Path to boring stability

- Stabilize descriptor lockfile and finding schema before adding many runtime integrations.
- Keep the first scope tightly on descriptor inspection, ProtoJSON, and a narrow transcoding subset.
- Ship with public conformance vectors and explainable diff categories.
- Avoid reinventing protobuf compilation or full gateway serving.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that inspect a descriptor set, run a narrow ProtoJSON/transcoding corpus, and emit a `*.protobundle.zip` describing edition/features, compatibility deltas, and gateway-facing changes.

# De-risk plan

1. Begin from descriptor sets and public test vectors, not from code generation.
2. Keep gateway adapters optional and narrow.
3. Start with the most failure-prone JSON/transcoding seams rather than every protobuf rule.
4. Treat edition support as explicit lockfile data, never hidden inference.

# Non-goals

- Not a new protobuf runtime.
- Not a replacement for `prost`.
- Not a full API gateway.
- Not a schema registry product.

# Architecture & API sketch

```rust
pub struct SchemaLock {
    pub edition: Option<String>,
    pub feature_overlays: Vec<String>,
    pub descriptor_digest: String,
}

pub fn inspect_descriptors(bytes: &[u8]) -> Result<DescriptorReport>;
pub fn diff_schema_locks(a: &SchemaLock, b: &SchemaLock) -> SchemaDiff;
```

Bundle draft: `schema.lock`, `descriptors.pb`, `report.json`, `protojson-findings.json`, `transcoding-findings.json`, `notes.md`.

# Security / safety model

- Treat descriptors and test payloads as untrusted input.
- Record generator/runtime/transcoder versions in each bundle.
- Support redaction of payload examples while preserving structural evidence.
- Prefer deterministic bundle generation for CI and code review.

# Maintenance & governance plan

- Keep the core centered on lockfiles, findings, and evidence bundles.
- Version gateway adapters separately from core descriptor semantics.
- Publish a public fixture corpus that clearly separates binary, JSON, and transcoding surfaces.
- Resist turning the project into another giant codegen framework.

# Milestones

## 0.1
- descriptor inspection
- schema lockfile
- ProtoJSON case runner

## 0.2
- HTTP/gRPC transcoding diffing
- compatibility classification
- evidence bundle writer

## 1.0
- stable `*.protobundle.zip`
- public fixture corpus
- documented compatibility policy across supported surfaces

# Open questions

- Which edition/feature settings matter enough to pin in the MVP?
- How much gateway behavior can be normalized without overfitting one implementation?
- What is the right public corpus for proving JSON- and transcoding-level compatibility?

# Sources

- Protobuf editions overview: https://protobuf.dev/editions/overview/
- Implementing editions support: https://protobuf.dev/editions/implementation/
- ProtoJSON format guide: https://protobuf.dev/programming-guides/json/
- `prost`: https://github.com/tokio-rs/prost
- `prost` editions support issue: https://github.com/tokio-rs/prost/issues/1031
- Google API design guide: https://docs.cloud.google.com/apis/design
- Google custom methods / transcoding guidance: https://cloud.google.com/apis/design/custom_methods
