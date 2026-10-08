---
id: P-0413
title: VSS + VISS v2 Capability & Replay Kit — signal-tree locks, transport overlays, and explainable subscription failures
status: idea
domains: [automotive, iot, connected-vehicle, protocols, telemetry, testing, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://covesa.global/project/vehicle-signal-specification/
  - https://www.w3.org/TR/viss2-core/
  - https://www.w3.org/TR/viss2-transport/
  - https://covesa.global/project/vehicle-information-service-specification/
  - https://docs.rs/vehicle-signals
---

# Problem

Connected-vehicle data stacks now have a real common-language story: VSS for the signal model and VISS v2 for access and transport. But practical failures still happen at the seam between the **tree people modeled**, the **transport/profile they actually exposed**, and the **authorization/rate/subscription behavior a client really encountered**.

The painful failures still happen between:

- **a nominal VSS tree and the curated branch/version a product actually shipped**,
- **path semantics and the transport binding used to serve them**,
- **capability claims and actual subscription/get/set behavior**,
- **server-side access controls and the client’s simplified error story**,
- and **vehicle/offboard deployments that all say “VISS” while differing materially in supported transports, filters, and permissions.**

The missing Rust contribution is not another server or WebSocket client. It is a **capability-and-replay kit** for VSS tree locks, VISS transport overlays, semantic path diffs, and replayable get/set/subscribe evidence.

# What it provides

- `vss.lock` — pins signal-tree revision, branch subset, naming overlays, and semantic-path assumptions.
- `viss-capabilities.json` — transport, operation, and auth/capability matrix for a concrete endpoint.
- `signal-replay` — normalized transcript for `get`, `set`, `subscribe`, and error responses across bindings.
- `path-diff` — structured explanation of renamed, missing, deprecated, or filtered signals.
- `cargo viss-evidence` — emits `*.vissbundle.zip` with locks, traces, capability matrices, and notes.

# What the crate should provide other people

1. **A boring client/server evidence artifact** for connected-vehicle APIs.
2. **Explicit capability matrices** instead of hand-wavy “supports VISS” claims.
3. **Semantic diffs for signal trees** that explain drift between releases or vendors.
4. **Replayable request/subscription bundles** for interoperability testing and bug reports.
5. **A Rust-native bridge between VSS trees and VISS runtime behavior**.

# Persona / who it’s for

- vehicle platform and middleware engineers
- client SDK and app developers
- interoperability/certification teams
- systems integrators debugging offboard/onboard mismatches

# Users & user stories

- **Client engineer**: “Capture what this endpoint actually supports before I write assumptions into my app.”
- **Integrator**: “See whether a failure came from a path mismatch, transport gap, or access-control decision.”
- **Release engineer**: “Diff last release’s VSS tree and current endpoint behavior.”
- **Vendor support**: “Share one redacted bundle instead of screenshots and partial logs.”

# Prior art (and why it’s insufficient)

- VSS gives a common model for signals.
- VISS v2 defines the message and transport layers.
- Rust has at least some VSS type-generation substrate.

What Rust still lacks is a **portable artifact layer** for tree-version pinning, endpoint capability capture, request/subscription replay, and explainable path drift.

# Design goals

1. **Tree-explicit** — pin the exact VSS subset and revision assumed.
2. **Transport-aware** — do not flatten HTTP, WebSocket, and MQTT behavior into one pretend surface.
3. **Auth-aware** — capability receipts must record access failures honestly.
4. **Client-friendly** — explain failures in terms of paths, permissions, filters, and operations.
5. **Redaction-safe** — support public evidence without leaking vehicle identifiers.

# MVP surface

- Minimal types: `VssLock`, `VissCapabilityMatrix`, `SignalReplay`, `PathDiff`, `VissBundle`
- Minimal functions:
  - `capture_tree()`
  - `probe_capabilities()`
  - `record_session()`
  - `diff_paths()`
  - `write_bundle()`
- Feature flags:
  - `http`
  - `websocket`
  - `mqtt`
  - `auth-redaction`

# Compatibility story

- Works above existing server/client implementations.
- Treats transport bindings as overlays on top of a pinned semantic tree.
- Supports offline replay from captured transcripts.
- Does not require a new VISS runtime.

# Conformance & fixtures

- Goldens for missing path, renamed path, filtered path, denied access, and subscription lifecycle failures.
- Tiny corpora for transport-specific behavior differences.
- Public redacted bundles with synthetic VIN/device identifiers.
- Capability matrices for server endpoints with explicit “unknown” versus “unsupported”.

# Path to boring stability

- Stabilize tree locks and capability receipts first.
- Keep transcript capture small and inspectable.
- Treat transport quirks as overlays, not reasons to fork the core schema.
- Resist scope creep into a full infotainment/vehicle platform stack.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that pin a VSS tree subset, probe or ingest VISS endpoint capabilities, capture replayable request/subscription sessions, explain path/auth failures, and emit compact `*.vissbundle.zip` artifacts.

# De-risk plan

1. Start with offline transcript ingestion plus static tree locks.
2. Add live probing only after the receipt schema is stable.
3. Keep auth redaction explicit from day one.
4. Pilot with synthetic/public trees before vendor-specific rollouts.

# Non-goals

- Not a new vehicle middleware platform.
- Not a full VISS server implementation.
- Not a fleet-management backend.
- Not a UI/infotainment framework.

# Architecture & API sketch

```rust
pub struct VssLock {
    pub tree_revision: String,
    pub roots: Vec<String>,
    pub naming_overlay: Vec<String>,
}

pub fn capture_tree(path: &std::path::Path) -> Result<VssLock>;
pub fn probe_capabilities(endpoint: &str) -> Result<VissCapabilityMatrix>;
pub fn diff_paths(a: &VssLock, b: &VssLock) -> PathDiff;
```

Bundle draft: `vss.lock`, `capabilities.json`, `session-replay.jsonl`, `path-diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Redact VINs, device identifiers, tokens, and proprietary path subsets by default.
- Preserve access-denied evidence without leaking raw policy.
- Separate observed endpoint behavior from inferred semantics.
- Keep transport credentials out of default bundles.

# Maintenance & governance plan

- Track VSS and VISS revisions explicitly.
- Keep capability matrices versioned and testable.
- Publish a tiny synthetic corpus for regression tests.
- Avoid trying to standardize vendor product behavior inside the crate itself.

# Milestones

## 0.1
- `vss.lock`
- capability-matrix schema
- transcript ingestion

## 0.2
- semantic path diff engine
- transport overlays
- redacted public corpus

## 1.0
- stable `*.vissbundle.zip`
- compatibility policy for tree and transport revisions
- CI-friendly replay/report tooling

# Open questions

- What is the best stable shape for a capability matrix across HTTP, WebSocket, and MQTT bindings?
- How much auth/policy detail is enough to explain failures without leaking internals?
- Which path changes deserve first-class “rename/move” semantics versus generic incompatibility reports?

# Sources

- COVESA Vehicle Signal Specification: https://covesa.global/project/vehicle-signal-specification/
- VISS v2 Core: https://www.w3.org/TR/viss2-core/
- VISS v2 Transport: https://www.w3.org/TR/viss2-transport/
- COVESA VISS project page: https://covesa.global/project/vehicle-information-service-specification/
- `vehicle-signals`: https://docs.rs/vehicle-signals
