# Design: Schema Contract Kit (`cargo schema`, `schema-pack/v0`)

## Goal
Define a portable contract-and-evolution boundary for Rust data and service schemas so Serde, JSON Schema, OpenAPI, and Protobuf workflows can export, diff, validate, and ship one reviewable evidence pack.

This should **not** replace Serde, `schemars`, `utoipa`, `typify`, `progenitor`, `prost-build`, or `prost-reflect`. It should make them easier to combine coherently.

## References (signals)
- Serde is the generic serialization substrate used across the Rust ecosystem.
  https://serde.rs/
- `cargo-util-schemas` is maintained by the Cargo team “for use by the wider ecosystem” and follows semver compatibility, which is a useful proof that versioned schema crates are a Rust-native pattern rather than an alien one.
  https://docs.rs/crate/cargo-util-schemas/0.10.2
- `schemars` generates JSON Schema from Rust types and currently defaults to JSON Schema 2020-12.
  https://docs.rs/schemars
- `utoipa` is the leading code-first OpenAPI generator for Rust APIs.
  https://docs.rs/utoipa
- The crates.io team now ships an experimental OpenAPI description generated with `utoipa`.
  https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- `typify` compiles JSON Schema into Rust types.
  https://docs.rs/typify
- `progenitor` generates Rust clients from OpenAPI descriptions.
  https://docs.rs/progenitor
- `prost-build` compiles `.proto` files in Cargo build scripts.
  https://docs.rs/prost-build
- `prost-reflect` turns protobuf descriptor sets into inspectable descriptors and dynamic messages.
  https://docs.rs/prost-reflect
- `schema-registry-client` shows that Rust-side schema registry workflows already exist across Avro, Protobuf, and JSON Schema, including migration/data-quality hooks.
  https://docs.rs/schema-registry-client

## Core components

### 1) `schema-intent/v0`
A design-time declaration of what contract surfaces a project intends to ship:
- source kinds in scope: `serde-format`, `json-schema`, `openapi`, `protobuf-descriptor`
- package/module/type selection rules
- compatibility policy per surface
- whether migrations are required for breaking changes
- target consumers: internal / public API / event stream / persisted state
- release attachment policy

This is the thing humans review before they trust the automation.

### 2) `schema-surface/v0`
A normalized manifest describing the exported contract surfaces:
- stable identifiers for each exported contract
- source kind and provenance
- path to raw attachments (OpenAPI document, JSON Schema, descriptor set, reflected registry)
- content hashes
- semantic labels (`request`, `response`, `event`, `config`, `state`, etc.)
- optional ownership / consumer metadata

Design rule: do **not** erase the original format. Normalize metadata and identity, then attach the raw source artifact.

### 3) `schema-compat-report/v0`
Machine-readable compatibility decisions:
- comparison target and policy mode (`backward`, `forward`, `full`, `exact`)
- pass/fail outcome
- reason codes
- affected symbols / endpoints / messages / fields
- severity and suggested remediations
- toolchain provenance

This is the explainable diff artifact.

### 4) `schema-vectors/v0`
Portable validation vectors:
- golden serialized payloads
- request/response examples
- descriptor-backed protobuf examples
- roundtrip expectations
- optional cross-version read/write checks

Design rule: use small canonical vectors for CI and review, not giant sample dumps.

### 5) `schema-migration/v0`
Optional migration attachment:
- from → to version range
- migration kind (`code`, `data-rewrite`, `consumer-rollout-note`, `manual`)
- code pointer or executable hook reference
- linked test vectors
- declared assumptions / rollout preconditions

v0 should allow migrations to be advisory attachments instead of forcing one runtime migration system.

### 6) `schema-pack/v0`
Bundle format:
- `schema-intent/v0`
- one or more `schema-surface/v0` entries
- `schema-compat-report/v0`
- optional `schema-vectors/v0`
- optional `schema-migration/v0`
- verification summary

This is the portable thing releases, CI jobs, downstream tests, and incident packs can attach.

### 7) `cargo schema`
Reference UX:
- `cargo schema init`
- `cargo schema export`
- `cargo schema diff --against <git|path|artifact>`
- `cargo schema check`
- `cargo schema vectors`
- `cargo schema pack`

`cargo schema` should start as an adapter, diff engine, and packer. It should not start life as a hosted registry product.

## Default policy
- **Export before publish** for crates/services that declare machine-readable contracts.
- **Diff in CI** against the last released or pinned baseline.
- **Carry raw artifacts forward** instead of flattening everything into one invented meta-schema.
- **Require explicit policy choice** (`backward`, `forward`, etc.) rather than assuming one default fits every boundary.
- **Treat migrations as attachments** that justify intentional breaks, not hidden magic.

## What the kit should provide to others
- **Service teams:** one way to review API/event contract drift without bespoke scripts.
- **Library authors:** a bridge from Rust types to machine-readable contract artifacts.
- **Platform teams:** reusable compatibility reason codes and release attachments.
- **Polyglot consumers:** raw OpenAPI / JSON Schema / protobuf artifacts plus normalized metadata.
- **Tool authors:** stable inputs for release, downstream testing, incident response, and policy kits.

## Overlap boundaries
- **Not Public API Kit:** that kit is about Rust item/public-dependency/MSRV boundaries; Schema Contract Kit is about machine-readable data and service boundaries.
- **Not Release Pipeline Kit:** release tooling should attach `schema-pack/v0`, not absorb it.
- **Not FuzzPack / Coverage / Perf Labs:** those kits may consume schema vectors or annotate schema changes, but they stay separate evidence families.
- **Not FFI Boundary Kit:** cross-language ABI/header contracts remain there; this kit targets serialized/service contracts.
- **Not Org Identity & Registry UX Kit:** this is not primarily about crates.io namespaces or alternate registries, which is why the concise archive renames the legacy “schema registry” idea into “schema contract”.

## Hard problems (explicitly scoped)
1. **Format divergence is real**
   - OpenAPI is not JSON Schema, and Serde semantics are not identical to either. v0 should preserve source-format truth instead of pretending one canonical schema language solves everything.
2. **Compatibility reasoning differs by boundary**
   - persisted state, event streams, and public HTTP APIs need different policies.
3. **Diff noise can destroy trust**
   - v0 needs stable ordering, stable reason codes, and source-hash provenance.
4. **Migrations are often operational, not purely codegen**
   - treat them as evidence attachments, not only generated transforms.
5. **Hosted registries are optional**
   - the pack must work with git, OCI, and local baselines before any dedicated service exists.
