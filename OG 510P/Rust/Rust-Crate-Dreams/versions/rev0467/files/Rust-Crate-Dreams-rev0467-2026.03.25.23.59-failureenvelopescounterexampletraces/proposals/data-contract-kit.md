---
id: P-0024
title: data-contract-kit
status: idea
domains: [data, distributed-systems, schema, validation]
last_reviewed: 2026-03-01
evidence:
  - https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
  - https://lib.rs/crates/schema-registry-validation
  - https://yokota.blog/2025/04/16/using-data-contracts-with-the-rust-schema-registry-client/
  - https://crates.io/crates/schema-registry-compatibility
---

# Problem
In event-driven and streaming systems, **schema evolution** is a daily risk:
- producers ship new schemas,
- consumers break on subtle incompatibilities,
- teams reinvent compatibility rules and test harnesses per project.

Rust has building blocks (schema validation engines, schema registry clients), but there’s no “default kit” that makes data contracts ergonomic and safe across formats.

# Users & user stories
- **Producer team**: “Before deploying, I want a contract test that my new schema is backward compatible.”
- **Consumer team**: “I want a typed Rust model with a safe migration path and clear failure modes.”
- **Platform team**: “I want a reusable policy engine that enforces compatibility modes in CI.”

# Prior art (and why it’s insufficient)
- Schema registry compatibility concepts are well-defined, but tooling is often language-specific.
- Existing Rust crates focus on either *validation* or *registry access*, not on an integrated developer workflow:
  - compatibility checks + diffs,
  - contract tests,
  - migration helpers,
  - CI policy gates.

# Design goals
1. Support common formats: **JSON Schema**, **Avro**, **Protobuf** (phased).
2. Provide a unified compatibility model: backward/forward/full/transitive modes (where applicable).
3. Offer a **contract test harness** that fits CI and dev workflows.
4. Provide **clear diffs** explaining *why* compatibility fails (not just “false”).
5. Integrate with registries but remain usable **without** a registry (local schema sets).

# Non-goals
- Becoming a full schema registry server.
- Auto-generating perfect migrations for all formats (but provide hooks).

# Architecture & API sketch
## Core types
- `SchemaFormat` trait (parse, canonicalize, validate)
- `CompatibilityMode` enum
- `Contract<T>`: links Rust type `T` (optional) to schema and rules
- `Report`: structured explanation of compatibility results

## Example API
```rust
use data_contract_kit::{Contract, CompatibilityMode, formats::JsonSchema};

let contract = Contract::new("user-events")
    .format(JsonSchema)
    .mode(CompatibilityMode::Backward);

let report = contract.check_compatibility(old_schema, new_schema)?;
assert!(report.is_ok(), "{report:?}");
```

## CLI (optional)
- `cargo contract check` — check compatibility in CI
- `cargo contract diff` — explain incompatibilities
- `cargo contract register` — publish schema if a registry is configured

# Security / safety model
- Canonicalization to reduce “equivalent but different” pitfalls.
- Strict input size limits and fuzz-friendly parsers (format backends should be fuzzable).
- Avoid remote code execution / scripting surfaces.

# Maintenance & governance plan
- Keep format backends behind feature flags to manage dependencies.
- Provide a conformance test suite for each format backend.
- Establish “compatibility policy fixtures” so regressions are caught.

# Milestones
- **0.1**: JSON Schema backend (via `schemars`-compatible inputs) + local compatibility checks + diff report.
- **0.2**: Avro backend + compatibility modes + registry integration (Confluent).
- **0.3**: Protobuf backend + transitive checks + example migration hooks.
- **0.4**: Contract-test harness + CI templates.
- **1.0**: Stable report schema + plugin interface for additional registries.

# Open questions
- How to best model Protobuf “wire compatibility” vs semantic compatibility?
- How much of “Rust type ↔ schema” mapping should be derived vs explicitly defined?

# Sources
- Schema evolution and compatibility concepts — https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- Rust validation engine covering JSON Schema/Avro/Protobuf — https://lib.rs/crates/schema-registry-validation
- Data contracts with Rust schema registry client — https://yokota.blog/2025/04/16/using-data-contracts-with-the-rust-schema-registry-client/
- Rust schema compatibility crate (prior art) — https://crates.io/crates/schema-registry-compatibility
