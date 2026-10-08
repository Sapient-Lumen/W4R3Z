---
id: P-0416
title: CloudEvents + CESQL + CDEvents Interop Workbench Kit — filter locks, event-family receipts, and replayable routing evidence
status: idea
domains: [eventing, cloud, ci-cd, streaming, interoperability, testing, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://github.com/cloudevents/spec
  - https://cloudevents.io/blog/2024-07-15/
  - https://docs.rs/cloudevents-sdk
  - https://docs.rs/cloudevents-sdk-reqwest
  - https://docs.rs/cdevents-sdk
---

# Problem

CloudEvents has a real ecosystem now, not just a spec PDF. The spec is mature, CloudEvents SQL (CESQL) reached v1.0 in 2024, Rust has an active CloudEvents SDK with transport bindings, and Rust also has a CDEvents SDK that maps domain CI/CD events onto CloudEvents.

But the painful failures still happen at the seam between:

- **an event envelope that is valid and the filter semantics another system actually applies**,
- **generic CloudEvents and domain-specific event families like CDEvents**,
- **transport bindings and the routing/debug traces operators need**,
- **declared event schemas and the real field subsets a rule or router depends on**,
- and **“the event didn’t match” explanations that never pin the filter, projection, or event family interpretation.**

The missing Rust contribution is not another SDK. It is an **interop workbench** for filter locks, event-family mapping receipts, replay bundles, and explainable CESQL/routing diagnostics.

# What it provides

- `ce.lock` — pins CloudEvents version, CESQL profile, transport assumptions, and event-family overlays.
- `filter-receipt` — normalized record of a CESQL expression, projection assumptions, and match results.
- `family-receipt` — explicit mapping between a generic CloudEvent and a domain family such as CDEvents.
- `route-replay` — replayable transcript for ingest, filter, route, and delivery decisions.
- `cargo ce-evidence` — emits `*.cebundle.zip` with locks, events, filters, replays, and notes.

# What the crate should provide other people

1. **A boring artifact for “why did this event match or not?”**
2. **Version-pinned filter receipts** for CESQL behavior.
3. **Portable mapping receipts** between generic CloudEvents and domain-specific event families.
4. **Replayable routing/debug bundles** for brokers, gateways, and CI/CD event pipelines.
5. **A Rust-native coordination layer above existing event SDKs.**

# Persona / who it’s for

- platform and eventing engineers
- CI/CD integration maintainers
- broker/gateway developers
- interoperability and QA teams

# Users & user stories

- **Platform engineer**: “Capture the exact filter and event payload that caused this route to fail.”
- **Integrator**: “See whether the mismatch came from CESQL, transport binding, or family mapping.”
- **CI/CD team**: “Replay a CDEvents sequence locally without the whole pipeline.”
- **Reviewer**: “Diff how this rule behaved before and after a filter/profile change.”

# Prior art (and why it’s insufficient)

- CloudEvents already has a mature core spec.
- CESQL 1.0 exists and SDK support is emerging.
- Rust already has CloudEvents and CDEvents SDKs.

What Rust still lacks is a **portable evidence layer** for filter pinning, family mapping, replayable routing decisions, and explainable mismatches.

# Design goals

1. **Filter-explicit** — the match logic must be pinned and inspectable.
2. **Family-aware** — domain event families must not be flattened into anonymous JSON payloads.
3. **Transport-aware** — keep HTTP/Kafka/etc. facts as overlays on top of the event core.
4. **Replay-first** — make event routing failures reproducible with one bundle.
5. **Small and boring** — optimize for receipts and diffs, not another full broker framework.

# MVP surface

- Minimal types: `CeLock`, `FilterReceipt`, `FamilyReceipt`, `RouteReplay`, `CeBundle`
- Minimal functions:
  - `capture_event()`
  - `evaluate_filter()`
  - `map_family()`
  - `replay_route()`
  - `write_bundle()`
- Feature flags:
  - `cesql`
  - `cdevents`
  - `http`
  - `kafka`
  - `redaction`

# Compatibility story

- Works above existing CloudEvents Rust SDKs and transport bindings.
- Treats CESQL as a pinned filter profile, not hand-rolled ad hoc matching.
- Supports CDEvents as an event-family overlay.
- Does not require a new broker or workflow engine.

# Conformance & fixtures

- Goldens for filter mismatch, missing extension attribute, domain-family projection drift, and route regression.
- Tiny corpora for CloudEvents core and selected CDEvents families.
- Redacted public bundles for issue reports and CI.
- Replay fixtures that compare routing outcomes across SDK/profile revisions.

# Path to boring stability

- Stabilize the lockfile and filter receipt schema first.
- Keep transport details as overlays.
- Start with offline replay and deterministic filter evaluation.
- Resist drift into becoming a general event-processing runtime.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A Rust library and CLI that pin CloudEvents/CESQL assumptions, capture event-family mappings, replay routing/filter decisions, explain mismatches, and emit compact `*.cebundle.zip` artifacts.

# De-risk plan

1. Start with offline filter evaluation and event capture.
2. Add event-family receipts before multi-transport integrations.
3. Keep CESQL behavior pinned to explicit profiles.
4. Pilot with synthetic CloudEvents/CDEvents corpora and small routing rules.

# Non-goals

- Not another CloudEvents core SDK.
- Not a broker or stream processor.
- Not a universal schema registry.
- Not a full observability backend.

# Architecture & API sketch

```rust
pub struct CeLock {
    pub spec_version: String,
    pub cesql_profile: String,
    pub family_overlays: Vec<String>,
}

pub fn capture_event(bytes: &[u8]) -> Result<CapturedEvent>;
pub fn evaluate_filter(lock: &CeLock, expr: &str, event: &CapturedEvent) -> FilterReceipt;
pub fn map_family(event: &CapturedEvent) -> Result<FamilyReceipt>;
```

Bundle draft: `ce.lock`, `events.jsonl`, `filter-receipt.json`, `family-receipt.json`, `route-replay.json`, `notes.md`.

# Security / safety model

- Support payload redaction and field hashing for sensitive event data.
- Distinguish observed routing facts from inferred family mappings.
- Preserve enough context to reproduce matches without leaking all payloads by default.
- Keep credentials and broker secrets out of bundles.

# Maintenance & governance plan

- Track CloudEvents/CESQL/CDEvents revisions explicitly.
- Keep a tiny public fixture corpus.
- Separate core receipts from transport-specific adapters.
- Avoid baking in one broker or gateway worldview.

# Milestones

## 0.1
- `ce.lock`
- event capture schema
- CESQL filter receipts

## 0.2
- CDEvents family receipts
- route replay bundles
- redacted public corpus

## 1.0
- stable `*.cebundle.zip`
- compatibility policy for CESQL and family overlays
- CI-friendly diff/report workflow

# Open questions

- Which CESQL feature subsets deserve first-class profile locks for an MVP?
- How much event-family mapping logic should be explicit schema versus optional adapters?
- What is the best bundle shape for multi-event routing decisions without becoming huge or unreadable?

# Sources

- CloudEvents spec repository: https://github.com/cloudevents/spec
- CESQL v1.0 announcement: https://cloudevents.io/blog/2024-07-15/
- `cloudevents-sdk`: https://docs.rs/cloudevents-sdk
- `cloudevents-sdk-reqwest`: https://docs.rs/cloudevents-sdk-reqwest
- `cdevents-sdk`: https://docs.rs/cdevents-sdk
