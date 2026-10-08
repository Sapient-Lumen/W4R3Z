# Epic Proposal: Schema Contract Kit (`cargo schema`)

## One-sentence pitch
Turn Rust data and service contracts into first-class release artifacts: export them, diff them, validate compatibility, attach migrations/vectors, and ship the result as a portable pack.

## Deliverables
- `cargo-schema` reference implementation
- Schemas:
  - `schema-intent/v0`
  - `schema-surface/v0`
  - `schema-compat-report/v0`
  - `schema-vectors/v0`
  - `schema-migration/v0`
  - `schema-pack/v0`
- Adapters/integrations:
  - Serde / `serde-reflection`
  - `schemars`
  - `utoipa`
  - `typify`
  - `progenitor`
  - `prost-build` / `prost-reflect`
  - optional schema-registry adapters (git / OCI / HTTP)
- Docs:
  - compatibility policy guide by boundary type
  - reason-code reference
  - release / CI patterns

## Why now (signals)
- Serde remains the center of gravity for Rust serialization.
  https://serde.rs/
- `serde-reflection` explicitly positions extracted formats as version-controlled artifacts that can prevent unintended format changes.
  https://docs.rs/serde-reflection
- `schemars`, `utoipa`, `typify`, and `progenitor` show that Rust now has credible JSON Schema and OpenAPI generation/consumption paths on both producer and consumer sides.
  https://docs.rs/schemars
  https://docs.rs/utoipa
  https://docs.rs/typify
  https://docs.rs/progenitor
- crates.io now publishes an experimental OpenAPI description generated with `utoipa`, which is a strong signal that machine-readable contract artifacts are becoming normal even in core Rust infrastructure.
  https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- `prost-build` and `prost-reflect` make protobuf descriptors a real Cargo-native substrate instead of an external afterthought.
  https://docs.rs/prost-build
  https://docs.rs/prost-reflect
- `schema-registry-client` shows that Rust-side registry workflows now span Avro, Protobuf, and JSON Schema, including migration and rule hooks, but there is still no shared Cargo-native pack/diff/report layer.
  https://docs.rs/schema-registry-client
- Cargo’s own `cargo-util-schemas` crate shows that versioned schema crates maintained for wider ecosystem use are already part of the Rust toolchain culture.
  https://docs.rs/crate/cargo-util-schemas/0.10.2

## Non-goals
- Replacing Serde or forcing one wire format
- Standardizing one universal hosted registry service in v0
- Pretending OpenAPI, JSON Schema, protobuf descriptors, and Serde formats are all identical
- Solving every contract-testing need in one mega-tool

## Strategic value
This kit has strong leverage because it connects:
- service/API review
- persisted-data evolution
- event compatibility
- release evidence
- downstream test baselines
- and multi-language consumer generation

It also gives the archive a missing “machine-readable boundary” lane that is distinct from Rust public API evolution.

## Milestones
1. **v0**
   - wrap existing tools
   - export `schema-pack/v0`
   - stable compatibility reason codes
2. **v0.2**
   - richer adapters for OpenAPI / protobuf / Serde-first workflows
   - migration attachment conventions
   - git + OCI baseline adapters
3. **v1**
   - better policy presets by boundary type
   - deeper release / downstream-testing integration
   - conformance corpus for compatibility engines
