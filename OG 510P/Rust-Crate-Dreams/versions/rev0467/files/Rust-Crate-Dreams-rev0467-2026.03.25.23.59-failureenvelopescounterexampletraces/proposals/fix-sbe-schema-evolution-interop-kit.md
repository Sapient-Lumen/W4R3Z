---
id: P-0401
title: FIX SBE Schema-Evolution Interop Kit — template locks, acting-version receipts, and zero-copy message evidence bundles
status: idea
domains: [finance, low-latency, binary-formats, interoperability, codegen, validation]
last_reviewed: 2026-03-06
evidence:
  - https://www.fixtrading.org/standards/sbe-online/
  - https://github.com/aeron-io/simple-binary-encoding
  - https://docs.rs/rustysbe
  - https://docs.rs/sbe_gen
  - https://crates.io/crates/sbe-codegen
---

# Problem

Simple Binary Encoding already has a serious formal surface: XML schemas, field/type encoding rules, acting-version semantics, repeating groups, composites, variable data, and reference implementations. Rust now also has meaningful substrate: generators, codecs, and even reference-implementation support. But the painful failures still happen at the seam between:

- **an SBE XML schema and the exact code generated from it**,
- **template evolution rules and what a decoder with a different acting version actually does**,
- **wire-level bytes and the semantic meaning of defaults, nulls, constants, and extensions**,
- **exchange/vendor dialects that share “SBE” branding but differ in template assumptions**,
- and **performance-sensitive debugging that still falls back to hex dumps and hand-matched schema docs.**

The missing Rust contribution is not another code generator. It is an **interop kit** for template locks, schema-evolution diffs, acting-version receipts, and evidence bundles small enough for real low-latency workflows.

# What it provides

- `sbe.lock` — pins schema hash, template IDs, acting-version expectations, null/default/constant conventions, and dialect overlays.
- `schema-ir` — normalized model of messages, fields, composites, groups, varData segments, and version gates independent of one generator.
- `schema-diff` — semantic diff that explains compatibility, extension safety, and likely decode ambiguity.
- `message-proof` — compact evidence artifact linking bytes, template, acting version, and decoded semantic view.
- `cargo sbe-evidence` — emits `*.sbebundle.zip` with locks, diffs, sample messages, and findings.

# What the crate should provide other people

1. **A boring artifact for SBE compatibility and migration bugs**.
2. **Semantic schema diffs** instead of raw XML diff churn.
3. **Acting-version receipts** that make decoder behavior explainable.
4. **A generator-neutral IR** for comparing Rust and non-Rust toolchains.
5. **Tiny, zero-copy-friendly message proofs** that can survive support handoff.

# Persona / who it’s for

- Rust developers building low-latency market-data or order-entry systems
- Teams maintaining SBE code generation pipelines
- QA/integration teams validating schema upgrades
- Engineers debugging binary-message compatibility across services

# Users & user stories

- **Protocol maintainer**: “Show me whether this schema change is extension-safe or decode-breaking.”
- **Runtime engineer**: “Explain why a decoder with acting version X interpreted these bytes differently.”
- **Integrator**: “Compare Rust-generated codecs against another language/toolchain without diffing raw XML by hand.”
- **Support engineer**: “Share one compact proof bundle instead of a packet capture plus tribal knowledge.”

# Prior art (and why it’s insufficient)

- The FIX SBE materials and Aeron reference implementation define the formal substrate.
- Rust generators and runtime crates already exist.
- Vendor teams have internal schema migration procedures.

What Rust still lacks is a **single evidence-grade coordination artifact** for schema locks, generator-neutral IR, acting-version receipts, and semantic diffs.

# Design goals

1. **Schema-evolution explicit** — versioning rules must be first-class, not hidden in generator output.
2. **Generator-neutral** — compare multiple Rust and non-Rust pipelines against one IR.
3. **Wire-linked** — findings must stay grounded in actual sample bytes.
4. **Performance-aware** — artifacts should be compact and zero-copy-friendly.
5. **Dialect-aware** — exchange/vendor overlays must be explicit, not implied.

# MVP surface

- Minimal types: `SbeLock`, `SchemaIr`, `SchemaFinding`, `MessageProof`, `SbeBundle`
- Minimal functions:
  - `load_schema()`
  - `diff_schema()`
  - `prove_message()`
  - `write_bundle()`
- Feature flags:
  - `xml`
  - `codegen`
  - `runtime-proof`
  - `dialect-overlays`

# Compatibility story

- Works above existing Rust generators/runtimes instead of replacing them.
- Can ingest SBE XML, generator metadata, and sample wire messages.
- Supports digest-only or truncated message proofs where payload sensitivity matters.
- Keeps dialect overlays separate from base SBE semantics.

# Conformance & fixtures

- Goldens for field presence rules, repeating groups, composites, varData, enum extension, and sinceVersion behavior.
- Tiny corpora for null/default/constant ambiguity and acting-version edge cases.
- Sample bundles comparing two generators against one schema.
- Public fixtures derived from non-sensitive schemas and messages.

# Path to boring stability

- Stabilize `sbe.lock`, `schema-ir`, and `schema-diff` before broad toolchain integration.
- Start with offline schema/message evidence rather than live transport capture.
- Version dialect overlays independently.
- Keep the first release focused on correctness and explanation, not benchmark competition.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that pin SBE schema assumptions, compute semantic compatibility diffs, link sample bytes to acting-version decode outcomes, and emit compact `*.sbebundle.zip` artifacts.

# De-risk plan

1. Start with XML schema normalization and semantic diffs.
2. Add message proofs next using small synthetic fixtures.
3. Keep generator adapters thin and optional.
4. Treat exchange/vendor dialects as explicit overlays from day one.

# Non-goals

- Not a trading gateway.
- Not a market-data transport stack.
- Not a new SBE code generator trying to replace every existing one.
- Not a benchmark suite.

# Architecture & API sketch

```rust
pub struct SbeLock {
    pub schema_hash: String,
    pub acting_version: u16,
    pub template_ids: Vec<u16>,
    pub dialect_overlays: Vec<String>,
}

pub fn load_schema(path: &std::path::Path) -> Result<SchemaIr>;
pub fn diff_schema(old: &SchemaIr, new: &SchemaIr) -> Vec<SchemaFinding>;
pub fn prove_message(lock: &SbeLock, bytes: &[u8]) -> Result<MessageProof>;
```

Bundle draft: `sbe.lock`, `schema.xml`, `schema-ir.json`, `schema-diff.json`, `message-proof.json`, `notes.md`.

# Security / safety model

- Support partial or hashed retention of payload bytes.
- Preserve enough header/template metadata for deterministic interpretation.
- Keep dialect-specific assumptions explicit in all findings.
- Avoid accidental inclusion of proprietary venue credentials or session metadata.

# Maintenance & governance plan

- Keep the core about schema locks, diffs, and message proofs.
- Version dialect overlays and compatibility rules carefully.
- Publish a small public corpus of schema/message fixtures.
- Resist drift into live transport or exchange-specific platform logic.

# Milestones

## 0.1
- `sbe.lock`
- schema IR
- semantic schema diff

## 0.2
- message proofs
- dialect overlays
- public fixture corpus

## 1.0
- stable `*.sbebundle.zip`
- documented compatibility policy for overlays and acting-version semantics
- broader generator/runtime adapters

# Open questions

- Which schema-evolution findings should be hard errors versus warnings?
- How much of acting-version behavior can be inferred without generator-specific metadata?
- What is the smallest useful proof shape for real low-latency support workflows?

# Sources

- FIX SBE online standard materials: https://www.fixtrading.org/standards/sbe-online/
- Aeron reference implementation (includes Rust support): https://github.com/aeron-io/simple-binary-encoding
- `rustysbe`: https://docs.rs/rustysbe
- `sbe_gen`: https://docs.rs/sbe_gen
- `sbe-codegen`: https://crates.io/crates/sbe-codegen
