# Gap: Schema contracts and evolution across Rust service boundaries

## What is missing
Rust has excellent serialization and API-description building blocks, but it still lacks a **boring, end-to-end contract workflow** for data and service boundaries.

Today teams can separately:
- serialize almost anything with Serde,
- extract Serde-oriented format descriptions with `serde-reflection`,
- generate JSON Schema with `schemars`,
- generate OpenAPI with `utoipa`,
- compile protobuf definitions with `prost-build`,
- inspect descriptor sets and dynamic messages with `prost-reflect`,
- and even talk to an external schema registry with crates like `schema-registry-client`.

What is still missing is the shared layer that answers:
- what contract surfaces a project is claiming to ship,
- how those surfaces changed,
- whether the change is backward / forward / full compatible,
- what test vectors or migrations justify the claim,
- and how CI / release tooling should carry that evidence forward.

## Why it matters
This is not just an API-documentation problem.

Rust teams increasingly build network services, event pipelines, CLIs with machine-readable outputs, and long-lived stored-data formats. Those systems need change review across version skew. The current experience is fragmented: one team exports OpenAPI, another checks JSON Schema drift, another relies on protobuf descriptors, and Serde-heavy internal protocols often have no first-class compatibility artifact at all.

The leverage is high because this sits at the boundary between:
- libraries and applications,
- producers and consumers,
- Rust and non-Rust systems,
- and development-time intent versus release-time evidence.

## Existing building blocks worth composing
- Serde is the ecosystem’s generic serialization substrate.
  https://serde.rs/
- `serde-reflection` can extract format descriptions and explicitly says those descriptions can be stored under version control to prevent unintended format modifications.
  https://docs.rs/serde-reflection
- `schemars` generates JSON Schema from Rust types and currently targets JSON Schema 2020-12 by default.
  https://docs.rs/schemars
- `utoipa` generates OpenAPI from Rust code and positions itself as the code-first OpenAPI path for Rust APIs.
  https://docs.rs/utoipa
- The crates.io team now publishes an experimental OpenAPI description for the crates.io API generated with `utoipa`, which is a strong signal that these artifacts are no longer niche.
  https://blog.rust-lang.org/2025/02/05/crates-io-development-update/
- `typify` turns JSON Schema into Rust types, which is useful for schema-first workflows.
  https://docs.rs/typify
- `progenitor` generates Rust clients from OpenAPI.
  https://docs.rs/progenitor
- `prost-build` and `tonic-prost-build` keep protobuf/gRPC codegen very alive in normal Cargo workflows.
  https://docs.rs/prost-build
  https://docs.rs/tonic-build/latest/tonic_build/
- `prost-reflect` provides descriptor-pool and dynamic-message reflection over protobuf descriptors.
  https://docs.rs/prost-reflect
- `schema-registry-client` already exposes Rust-side Schema Registry integration for Avro, Protobuf, and JSON Schema, including migration-rule hooks.
  https://docs.rs/schema-registry-client

## Why existing tools are not yet the whole answer
The ecosystem has **format-specific tools**, but not the **shared contract / diff / evidence layer**:
- OpenAPI generators document HTTP APIs.
- JSON Schema tools describe JSON payloads.
- Protobuf tools generate and reflect descriptors.
- Serde tooling can describe internal formats.
- Registry clients can store schemas elsewhere.

But teams still have to invent their own answers for:
- normalized compatibility reason codes,
- CI-friendly diff artifacts,
- migration attachments,
- format-agnostic contract bundles,
- and release attachment conventions.

This is the same missing seam seen elsewhere in the archive: strong point tools, weak shared artifacts.

## Target outcome
A project should be able to say:
- “these are the data/service contracts this crate or service ships,”
- “this release changed them in these precise ways,”
- “this change is backward compatible under this policy,”
- “these migrations or vectors justify the claim,”
- and “this is the portable bundle CI, release, downstream testing, and incident tooling can consume.”

That is bigger than a derive macro and smaller than a new central platform.
