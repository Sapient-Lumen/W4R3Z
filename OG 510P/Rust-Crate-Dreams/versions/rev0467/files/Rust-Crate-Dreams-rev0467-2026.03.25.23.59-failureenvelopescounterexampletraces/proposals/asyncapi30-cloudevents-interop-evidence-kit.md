---
id: P-0340
title: AsyncAPI 3.0 + CloudEvents Interop & Evidence Kit — event-contract lockfiles, binding-aware diffs, and replayable cross-transport bundles
status: idea
domains: [event-driven, asyncapi, cloudevents, messaging, apis, interoperability, conformance]
last_reviewed: 2026-03-06
evidence:
  - https://www.asyncapi.com/docs/reference/specification/v3.0.0
  - https://www.asyncapi.com/docs/migration/migrating-to-v3
  - https://cloudevents.io/
  - https://github.com/cloudevents/spec
  - https://crates.io/crates/asyncapi-rust
  - https://crates.io/crates/asyncapiv3
  - https://crates.io/crates/cloudevents-sdk
---

# Problem

Rust can now model or even generate pieces of event-driven API descriptions, and it has an official CloudEvents SDK path, but the painful failures in production systems sit above raw serialization:

- AsyncAPI documents drift from what services actually publish or consume,
- protocol bindings encode the same logical event differently across Kafka, HTTP, MQTT, or WebSocket paths,
- CloudEvents metadata survives one hop but silently degrades on the next,
- migrations from AsyncAPI v2 to v3 change operation/channel semantics in ways that are hard to diff,
- and teams still debug event-contract failures with screenshots, sample payloads, and tribal knowledge instead of portable artifacts.

The worthy crate contribution is an **interop and evidence kit** that pins event contracts, validates transport/binding behavior, and emits replayable bundles that compare logical events across transports.

# What it provides

- `event-contract-lock` — lockfiles pinning AsyncAPI document versions, selected bindings, allowed message schemas, and CloudEvents metadata expectations.
- `event-ir` — canonical Rust IR for AsyncAPI operations/channels/messages plus logical CloudEvent representations independent of transport.
- `binding-check` — compare observed traffic against pinned bindings and contract assumptions.
- `cloudevents-bridge` — normalize structured and binary CloudEvents across supported transports into one stable findings vocabulary.
- `event-replay` — deterministic replay for captured messages against pinned AsyncAPI/CloudEvents contracts.
- `event-diff` — semantic diffs such as “same logical event, different CloudEvents attribute fidelity” or “AsyncAPI channel binding does not match observed headers/routing keys”.
- `cargo event-evidence` — emit `*.eventbundle.zip` for CI, provider handoff, or cross-team debugging.

# What the crate should provide other people

1. **A boring default for event-contract debugging** instead of format-specific ad hoc tooling.
2. **One place to pin AsyncAPI and CloudEvents assumptions** across teams and transports.
3. **Transport-neutral semantic diffs** that explain what changed in the actual event contract.
4. **Replayable evidence bundles** that make cross-service bugs portable.
5. **A migration workbench** for AsyncAPI v2→v3 and binding/profile drift.

# Persona / who it’s for

- Platform engineers for event-driven systems
- API governance teams
- SDK/tooling authors
- Rust developers using AsyncAPI or CloudEvents crates
- QA teams validating broker or transport migrations

# Users & user stories

- **Platform team**: “Show whether this Kafka event and this HTTP webhook are the same CloudEvent semantically.”
- **Governance lead**: “Fail CI when a service drifts from the pinned AsyncAPI contract or downgrades CloudEvents fidelity.”
- **SDK author**: “Replay a captured message set against a contract and explain exactly which binding assumptions broke.”
- **Migration owner**: “Compare an AsyncAPI v2 description and its v3 migration semantically, not just textually.”

# Prior art (and why it’s insufficient)

- AsyncAPI 3.0 is current and has migration guidance from v2.
- CloudEvents provides a shared event model and has an official Rust SDK.
- Rust has emerging AsyncAPI crates (`asyncapi-rust`, `asyncapiv3`) plus `cloudevents-sdk`.
- But there is still no boring-default Rust crate family for **contract lockfiles + transport-aware replay + CloudEvents normalization + portable evidence bundles**.

# Design goals

1. **Contract-first** — observed events should be judged relative to explicit pinned contracts.
2. **Transport-aware, model-neutral** — preserve transport detail while still normalizing to logical event semantics.
3. **Migration-friendly** — AsyncAPI version drift should be explainable.
4. **Adapter-first** — reuse existing SDKs and parsers where possible.
5. **Implementation neutrality** — useful even when the producers/consumers are not written in Rust.

# MVP surface

- Minimal types: `EventContract`, `ObservedMessage`, `CloudEventSnapshot`, `BindingFinding`, `ReplayReport`, `EventDiff`
- Minimal functions:
  - `load_contract()`
  - `normalize_event()`
  - `verify_binding()`
  - `replay_messages()`
  - `diff_contracts()`
  - `write_bundle()`
- Feature flags:
  - `asyncapi`
  - `cloudevents`
  - `serde`
  - `redaction`
  - `bindings-http`
  - `bindings-kafka`

# Compatibility story

- MVP should target **AsyncAPI 3.0** first, with explicit migration helpers for v2 sources rather than hidden dual behavior.
- CloudEvents support should focus on the stable core model and common transport encodings first.
- The crate should complement contract generation crates and SDKs rather than replace them.
- MVP should intentionally avoid becoming a universal broker emulator.

# Conformance & fixtures

- Tiny fixtures for HTTP, Kafka-like, and WebSocket-friendly transport examples where legal/public fixtures are available.
- Positive and negative cases for structured vs binary CloudEvents mappings.
- Contract fixtures covering channel/operation mismatches, header drift, routing-key drift, and schema mismatch.
- Golden semantic diffs for AsyncAPI v2→v3 migration cases.

# Path to boring stability

- First stabilize the logical event IR and findings vocabulary.
- Then prove transport-specific normalization does not erase too much evidence.
- Freeze bundle layout after a few real-world cross-transport debugging cases.
- Keep schema-generation ambitions secondary to contract validation and replay.

# Scorecard

- Impact: 3/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 4/5
- **Total: 22/30**

# Minimum lovable MVP

A CLI and library that ingest one AsyncAPI 3.0 document plus a small captured message set, normalize the messages into CloudEvents-aware IR, verify them against pinned bindings, and emit a redactable `*.eventbundle.zip` with semantic diffs and replay reports.

# De-risk plan

1. Start with two transports and a narrow CloudEvents subset.
2. Treat AsyncAPI migration as explicit tooling, not automatic magic.
3. Reuse existing message parsers and schema tooling rather than inventing new ones.
4. Keep replay at the message/contract level, not full broker simulation.

# Non-goals

- Not a broker or streaming platform.
- Not a general-purpose schema registry.
- Not a complete code generator for every AsyncAPI target.

# Architecture & API sketch

```rust
pub struct ReplayReport {
    pub contract_id: String,
    pub binding_findings: Vec<Finding>,
    pub event_findings: Vec<Finding>,
    pub diffs: Vec<DiffFinding>,
}

pub fn verify_binding(contract: &EventContract, observed: &[ObservedMessage]) -> ReplayReport;
pub fn normalize_event(message: &ObservedMessage) -> Result<CloudEventSnapshot>;
```

Bundle draft: `contract.yaml`, `messages.ndjson`, `normalized-events.json`, `findings.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact secrets, auth headers, and sensitive payload fields by default.
- Preserve contract-level routing and metadata context needed for debugging.
- Bound payload capture size and external schema fetching by default.
- Record exact AsyncAPI and CloudEvents crate/spec versions assumed.

# Maintenance & governance plan

- Keep core focused on IRs, replay, adapters, and findings vocabularies.
- Version binding packs separately from the bundle schema.
- Encourage public synthetic fixtures for transport examples.
- Document how new bindings or spec revisions are added without destabilizing old bundles.

# Milestones

## 0.1
- contract loader
- CloudEvents normalization
- bundle writer

## 0.2
- binding checks
- semantic diffs
- redaction support

## 1.0
- stable `*.eventbundle.zip`
- CI-ready fixture corpus
- documented version-migration policy

# Open questions

- How much of AsyncAPI’s document model belongs in the core IR versus adapter layers?
- Should CloudEvents normalization be lossy by default or preserve transport-specific detail alongside the common model?
- Which bindings deserve first-class support after HTTP and Kafka-like transports?

# Sources

- AsyncAPI 3.0 spec: https://www.asyncapi.com/docs/reference/specification/v3.0.0
- AsyncAPI migration to v3: https://www.asyncapi.com/docs/migration/migrating-to-v3
- CloudEvents project: https://cloudevents.io/
- CloudEvents spec repo: https://github.com/cloudevents/spec
- `asyncapi-rust`: https://crates.io/crates/asyncapi-rust
- `asyncapiv3`: https://crates.io/crates/asyncapiv3
- `cloudevents-sdk`: https://crates.io/crates/cloudevents-sdk
