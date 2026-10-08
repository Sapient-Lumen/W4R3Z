---
id: P-0400
title: VDA 5050 Master-Control ↔ AGV Interop & Evidence Kit — MQTT topic captures, order/state diffs, and fleet-onboarding receipts
status: idea
domains: [robotics, logistics, industrial, interoperability, validation, mqtt]
last_reviewed: 2026-03-06
evidence:
  - https://github.com/VDA5050/VDA5050
  - https://docs.rs/vda5050-types
  - https://docs.rs/vda5050-types/latest/vda5050_types/v2_0/factsheet/index.html
  - https://git.openlogisticsfoundation.org/silicon-economy/libraries/vda5050/libvda5050pp/-/tree/main/docs
---

# Problem

VDA 5050 is meant to make AGV/AMR fleets and master-control systems interoperable. In practice, the hard part is not just parsing the message schema. The hard part is the operational seam between orders, state transitions, instant actions, factsheets, MQTT topic discipline, and the real behavior of a vehicle versus the expectations of the master controller.

Rust already has some substrate. `vda5050-types` gives Rust-native types for the protocol, and there is meaningful non-Rust ecosystem tooling and reference code around the standard. But the painful failures still happen at the seam between:

- **the official message model and the real order/state/action lifecycle seen on MQTT topics**,
- **factsheet claims and what a vehicle/controller pair can actually coordinate**,
- **incremental order updates, action state retention, and vendor-specific assumptions**,
- **fleet-onboarding tests and the evidence that support teams can actually share**,
- and **“AGV does not react correctly” incidents that are still debugged from raw MQTT logs and screenshots.**

The missing Rust contribution is not another fleet manager. It is an **interop and evidence kit** for topic captures, order/state diffs, factsheet compatibility findings, and portable onboarding receipts.

# What it provides

- `vda5050.lock` — pins protocol version, topic/profile assumptions, factsheet overlays, and controller/vehicle capability expectations.
- `topic-capture` IR — normalized representation of order, state, instant-action, connection, visualization, and factsheet traffic.
- `order-graph-diff` — semantic comparison of intended order graphs and observed vehicle/controller progress.
- `factsheet-compat` — checks whether a controller and AGV factsheet/capability pair are mutually compatible.
- `cargo vda5050-evidence` — emits `*.vda5050bundle.zip` with captures, diffs, findings, and notes.

# What the crate should provide other people

1. **A boring incident bundle for AGV/controller interoperability failures**.
2. **Semantic diffs for orders, states, and instant actions**.
3. **Factsheet compatibility checks** before full-site rollout.
4. **Reusable onboarding receipts** for mixed-vendor fleets.
5. **A small fixture corpus** that future Rust and non-Rust implementations can share.

# Persona / who it’s for

- Rust teams building fleet-integration tools, gateways, or test harnesses
- AGV/AMR vendors validating controller compatibility
- Logistics-platform integrators onboarding mixed fleets
- QA/support teams debugging order/state behavior

# Users & user stories

- **Integrator**: “Show me whether the failure is topic discipline, order semantics, factsheet mismatch, or controller assumptions.”
- **Vehicle vendor**: “Capture one neutral receipt of the onboarding session without asking the customer for every raw MQTT trace.”
- **Controller team**: “Diff what we intended to send against what the AGV actually acknowledged and executed.”
- **Support engineer**: “Share a redacted bundle that still preserves the action/order timeline.”

# Prior art (and why it’s insufficient)

- The official VDA 5050 spec defines the message surfaces and lifecycle concepts.
- Rust already has type definitions for the standard.
- Other ecosystem libraries focus on implementation, not portable evidence.

What Rust still lacks is a **single coordination artifact** for lockfiles, normalized topic captures, factsheet compatibility, and explainable incident bundles.

# Design goals

1. **Lifecycle-aware** — orders, state, actions, and factsheets must be treated as linked surfaces.
2. **MQTT-honest** — topic and header sequencing details matter and must be preserved.
3. **Onboarding-friendly** — useful before a production rollout, not just after incidents.
4. **Vendor-neutral** — stay above one controller or vehicle implementation.
5. **Redactable** — support customer-site evidence sharing.

# MVP surface

- Minimal types: `Vda5050Lock`, `TopicCapture`, `OrderFinding`, `FactsheetFinding`, `Vda5050Bundle`
- Minimal functions:
  - `capture_topics()`
  - `normalize_session()`
  - `diff_order_graph()`
  - `check_factsheet_compatibility()`
  - `write_bundle()`
- Feature flags:
  - `mqtt`
  - `factsheet`
  - `instant-actions`
  - `visualization`

# Compatibility story

- Works above `vda5050-types` and can ingest captures from generic MQTT clients.
- Supports offline trace analysis before live-site adapters.
- Keeps vendor-specific overlays out of the core schema.
- Can be used even where the runtime implementation is not written in Rust.

# Conformance & fixtures

- Goldens for order acceptance/rejection, header sequencing, action-state retention, cancel/instant-action handling, and reconnect behavior.
- Factsheet fixtures covering load limits, navigation capabilities, and communication assumptions.
- Tiny corpora for “same order intent, different observed progression”.
- Public redacted topic captures suitable for regression testing.

# Path to boring stability

- Stabilize the lockfile and topic-capture IR before pursuing deeper live integrations.
- Keep factsheet compatibility and order/state diffs central.
- Version vendor overlays independently.
- Avoid turning the project into a controller simulator.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 3/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that capture VDA 5050 topic traffic, pin onboarding assumptions, compute order/state and factsheet findings, and emit compact `*.vda5050bundle.zip` artifacts.

# De-risk plan

1. Start with offline MQTT capture ingestion and factsheet checks.
2. Support controller/vehicle identifiers as redactable metadata.
3. Keep topic normalization conservative and explicit.
4. Publish a small public onboarding corpus before deeper runtime adapters.

# Non-goals

- Not a fleet manager.
- Not an AGV simulator.
- Not a generic MQTT broker tool.
- Not a warehouse orchestration platform.

# Architecture & API sketch

```rust
pub struct Vda5050Lock {
    pub protocol_version: String,
    pub capability_overlays: Vec<String>,
    pub topic_profile: String,
}

pub fn capture_topics(input: CaptureInput) -> Result<TopicCapture>;
pub fn diff_order_graph(capture: &TopicCapture, lock: &Vda5050Lock) -> Vec<OrderFinding>;
pub fn check_factsheet_compatibility(capture: &TopicCapture) -> Vec<FactsheetFinding>;
```

Bundle draft: `vda5050.lock`, `topics.json`, `factsheet.json`, `order-diff.json`, `findings.json`, `notes.md`.

# Security / safety model

- Support redaction of site names, vehicle IDs, coordinates, and task-specific payloads.
- Preserve ordering/timing relationships even when payloads are partially hashed.
- Separate declared from observed capabilities in all findings.
- Keep evidence deterministic enough for CI and support exchange.

# Maintenance & governance plan

- Keep the core about evidence bundles and semantic diffs.
- Version protocol overlays explicitly as VDA 5050 evolves.
- Publish a small corpus of redacted onboarding and incident traces.
- Resist scope creep into “general fleet platform” behavior.

# Milestones

## 0.1
- `vda5050.lock`
- topic capture IR
- order/state diff prototype

## 0.2
- factsheet compatibility checks
- instant-action fixtures
- public corpus

## 1.0
- stable `*.vda5050bundle.zip`
- documented compatibility policy for overlays
- broader live adapter surface

# Open questions

- Which factsheet surfaces belong in the core lockfile versus overlay packs?
- How should controller-specific expectations be represented without corrupting the vendor-neutral core?
- What is the smallest credible replay slice for a mixed order/instant-action incident?

# Sources

- Official VDA 5050 repository/spec: https://github.com/VDA5050/VDA5050
- `vda5050-types`: https://docs.rs/vda5050-types
- `vda5050-types` factsheet module docs: https://docs.rs/vda5050-types/latest/vda5050_types/v2_0/factsheet/index.html
- `libVDA5050pp` docs: https://git.openlogisticsfoundation.org/silicon-economy/libraries/vda5050/libvda5050pp/-/tree/main/docs
