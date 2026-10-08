---
id: P-0384
title: Substrait + Flight SQL + ADBC Interop Workbench Kit — plan portability locks, engine-capability diffs, and Arrow-native incident bundles
status: idea
domains: [data, analytics, query-engines, interoperability, sql, arrow, validation]
last_reviewed: 2026-03-06
evidence:
  - https://substrait.io/
  - https://substrait.io/spec/specification/
  - https://arrow.apache.org/docs/format/ADBC.html
  - https://arrow.apache.org/adbc/main/driver/flight_sql.html
  - https://docs.rs/crate/datafusion-substrait/latest
  - https://crates.io/crates/datafusion-flight-sql-server
---

# Problem

Rust already has first-class analytics substrate in DataFusion and the Arrow ecosystem. Substrait is increasingly the language for plan interchange, while Flight SQL and ADBC define Arrow-native transport and client access surfaces.

But the painful failures still happen at the seam between:

- **what one engine can serialize to Substrait and what another can faithfully consume**,
- **logical equivalence and physical execution capability**,
- **Flight SQL wire support and the ADBC feature surface exposed by specific drivers**,
- **extension functions or type variations that silently change meaning across systems**,
- and **debugging bundles that currently mix SQL text, engine-specific plans, transport traces, and Arrow snapshots with no shared schema**.

The missing Rust contribution is not another query engine. It is an **interop workbench** that turns query portability, capability diffs, and Arrow-native execution evidence into boring, shareable artifacts.

# What it provides

- `substrait.lock` — pins Substrait revision, extension/function packs, type-variation assumptions, Flight SQL features, and ADBC expectations.
- `plan-irx` — neutral IR connecting SQL text, engine plans, Substrait plans, parameter bindings, result schemas, and observed transport behavior.
- `capability-diff` — computes explainable mismatches between producer/consumer/server/client capability sets.
- `result-proof` — stores small Arrow or digest-based result evidence for reproducible portability checks.
- `cargo query-evidence` — emits `*.querybundle.zip` with locks, plans, traces, and findings.

# What the crate should provide other people

1. **A boring artifact for cross-engine query portability bugs**.
2. **Capability diffs** instead of vague “engine B doesn’t support this”.
3. **Lockfiles for extensions and type variations**.
4. **Wire-to-plan-to-result evidence** that survives handoff across teams.
5. **A way to compare DataFusion-native, Substrait, Flight SQL, and ADBC views of the same query.**

# Persona / who it’s for

- Rust analytics/database engine authors
- Platform teams embedding DataFusion or Arrow-native query services
- Driver and connector maintainers
- Integrators debugging cross-engine query portability

# Users & user stories

- **Engine maintainer**: “Show me whether the portability failure is SQL parsing, Substrait coverage, Flight SQL transport, or result-shape mismatch.”
- **Platform engineer**: “Pin the extension/function set used in production so upgrades are comparable.”
- **Driver maintainer**: “Demonstrate exactly which ADBC/Flight SQL features my server surface exposes or omits.”
- **User support engineer**: “Capture a small, shareable bundle for a failing query without sending an entire dataset.”

# Prior art (and why it’s insufficient)

- Substrait has a growing specification and community of engines.
- ADBC and Flight SQL define complementary Arrow-native access surfaces.
- DataFusion already ships Substrait support and there are Rust Flight SQL server crates.

What Rust still lacks is a **single evidence-grade workbench** for plan portability locks, extension packs, engine capability diffs, and result evidence.

# Design goals

1. **Semantics-first** — distinguish logical equivalence from transport and implementation details.
2. **Extension-aware** — function packs and type variations must be explicit.
3. **Dataset-light** — small evidence bundles should be possible without shipping raw data.
4. **Transport-honest** — ADBC API behavior and Flight SQL wire behavior must remain distinct.
5. **Engine-neutral** — the workbench must sit above DataFusion and future Rust engines/servers.

# MVP surface

- Minimal types: `SubstraitLock`, `PlanBundle`, `CapabilityDiff`, `ResultProof`
- Minimal functions:
  - `capture_query()`
  - `diff_capabilities()`
  - `prove_results()`
  - `write_bundle()`
- Feature flags:
  - `substrait`
  - `flight-sql`
  - `adbc`
  - `result-proof`
  - `redaction`

# Compatibility story

- Works above DataFusion and Arrow-native services, not instead of them.
- Can ingest SQL, engine-native plans, Substrait plans, or Flight SQL sessions.
- Treats result proofs as optional and digest-based when data cannot be shipped.
- Keeps driver/server capability claims explicit in one lockfile.

# Conformance & fixtures

- Tiny fixtures for type-variation mismatches, extension-function disagreements, prepared statements, partitioned results, and schema-order drift.
- Goldens for “same logical query, different physical capability path”.
- Public conformance corpus with small Arrow snapshots and digest proofs.
- Adapters for DataFusion-native and Flight SQL sessions around one stable bundle schema.

# Path to boring stability

- Stabilize lockfile and capability-diff schema before broadening engine adapters.
- Start with query portability and result-schema correctness, not full benchmarking.
- Keep result evidence small and digest-friendly.
- Version extension/function packs aggressively.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that pin query portability assumptions, capture SQL/plan/transport/result evidence, explain capability mismatches, and emit compact `*.querybundle.zip` artifacts.

# De-risk plan

1. Start with DataFusion + Substrait + Flight SQL adapters.
2. Keep large datasets out of scope; use Arrow snapshots and digests.
3. Treat extension packs as explicit, versioned overlays.
4. Separate semantic failures from performance concerns.

# Non-goals

- Not a new SQL engine.
- Not a benchmark suite.
- Not a universal database proxy.
- Not a replacement for Arrow Flight or ADBC implementations.

# Architecture & API sketch

```rust
pub struct SubstraitLock {
    pub substrait_revision: String,
    pub extension_pack: String,
    pub flight_sql_profile: String,
    pub adbc_expectations: Vec<String>,
}

pub fn capture_query(input: QueryCaptureInput) -> Result<PlanBundle>;
pub fn diff_capabilities(bundle: &PlanBundle, lock: &SubstraitLock) -> CapabilityDiff;
pub fn prove_results(bundle: &PlanBundle) -> ResultProof;
```

Bundle draft: `substrait.lock`, `query.sql`, `plans/`, `transport.json`, `capability-diff.json`, `result-proof.json`, `notes.md`.

# Security / safety model

- Support digest-only and schema-only evidence modes.
- Mark redacted SQL literals and parameters explicitly.
- Record engine, adapter, and extension-pack versions in every bundle.
- Keep captured transport traces deterministic and bounded.

# Maintenance & governance plan

- Keep the core about lockfiles, plan/result evidence, and capability diffs.
- Version engine adapters independently if necessary.
- Publish a small public portability corpus.
- Resist scope creep into benchmarking or warehouse orchestration.

# Milestones

## 0.1
- DataFusion adapter
- Substrait lockfile
- capability diff prototype

## 0.2
- Flight SQL / ADBC evidence capture
- result proofs
- public fixture corpus

## 1.0
- stable `*.querybundle.zip`
- documented compatibility policy for extensions and type variations
- broader engine adapter surface

# Open questions

- Which extension/function registry layout should the lockfile use?
- What is the smallest credible result-proof format for multi-engine debugging?
- How much prepared-statement and partitioned-result behavior belongs in MVP?

# Sources

- Substrait overview: https://substrait.io/
- Substrait specification: https://substrait.io/spec/specification/
- Arrow ADBC format docs: https://arrow.apache.org/docs/format/ADBC.html
- Arrow Flight SQL ADBC driver docs: https://arrow.apache.org/adbc/main/driver/flight_sql.html
- `datafusion-substrait`: https://docs.rs/crate/datafusion-substrait/latest
- `datafusion-flight-sql-server`: https://crates.io/crates/datafusion-flight-sql-server
