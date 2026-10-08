---
id: P-0146
title: MLS Deployment Kit
status: idea
domains: [security, e2ee, messaging, local-first, protocols, conformance, ops]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/openmls
  - https://openmls.tech/
  - https://dr-knz.net/mls-investigation.html
---

# Problem

**Messaging Layer Security (MLS)** is an IETF standard protocol for end-to-end encrypted group messaging.
Rust has a serious MLS implementation (OpenMLS), but there is still a large gap between “protocol library” and
“productionable group messaging subsystem”: storage, group state lifecycle, delivery semantics, interop fixtures,
and operational debugging artifacts.

Teams repeatedly rebuild the same *missing middle layer* and end up with incompatible group state encodings and
non-reproducible bug reports.

# What it provides

A batteries-included *deployment layer* above OpenMLS that other projects can depend on:

- A stable **Group State Storage** trait + reference implementations
  - `sqlite` (desktop/server), `sled` (embedded-ish), and a `wasm` KV adapter
- A versioned **group state envelope** format (`.mlsgroup`), focused on:
  - forward/backward-compatible encoding
  - explicit key schedule / epoch metadata
  - safe migration hooks
- A **delivery + fanout contract**:
  - “best-effort” transport adapters (WebSocket, HTTP polling, QUIC datagrams)
  - explicit semantics: ordering, replay tolerance, idempotency
- A shareable debugging artifact format: `*.mlsbundle.zip`
  - redacted transcript (commit hashes, epoch transitions, message types)
  - group state fingerprint + version
  - reproducible “replay script” (local harness)
- An **interop & conformance suite**
  - vectors derived from RFC expectations + cross-impl matrix runner hooks
  - fuzz + mutation harness for group-state envelopes

# Users & user stories

- **App teams**: “I want group E2EE without becoming an MLS expert.”
- **Infra teams**: “I need reproducible incident artifacts to debug group desyncs.”
- **Library authors**: “I want stable storage/transport traits to build adapters.”

# Prior art (and why it’s insufficient)

- **OpenMLS**: protocol correctness focus, not a deployment UX or ops layer.
- Ad-hoc “mls-chat”-style demos: illustrate usage but don’t standardize artifacts, storage, or migrations.

# Design goals

- Treat **artifacts as the collaboration unit** (`mlsbundle.zip` + deterministic replay).
- Provide a **safe migration story** for group state and storage.
- Keep crypto backend choice explicit and pluggable (align with OpenMLS backends).

# Non-goals

- Not a full messenger application.
- Not a bespoke crypto scheme; stick to MLS and well-reviewed primitives.

# Architecture & API sketch

- `mls_deploy::storage::{GroupStore, Transaction}` (async, fallible, migration-aware)
- `mls_deploy::envelope::{GroupEnvelopeV1, Fingerprint}` (versioned encoding)
- `mls_deploy::transport::{Outbound, Inbound, DeliverySemantics}`
- `mls_deploy::bundle::{BundleWriter, BundleReader}` for `mlsbundle.zip`

# Security / safety model

- Redaction must be *default-on* for bundles (no raw secrets, no private keys).
- “Replay harness” runs in a sandboxed mode and never transmits network traffic unless explicitly configured.

# Maintenance & governance plan

- Start as a single crate with feature-gated adapters; split once interfaces stabilize.
- Require interop tests to remain green before merging envelope/storage changes.

# Milestones

- **MVP**: storage trait + sqlite impl, envelope v1, `mlsbundle.zip` capture.
- **v0.5**: delivery contract + websocket adapter + replay harness.
- **v1.0**: conformance suite + migration tooling + docs/playbooks.

# Open questions

- How to best represent “delivery semantics” without overfitting to one messenger architecture?
- What minimal redaction policy keeps bundles useful but safe?

# Sources

- OpenMLS crate (MLS RFC 9420 implementation): https://crates.io/crates/openmls
- OpenMLS project overview: https://openmls.tech/
- Deployment gap analysis / practical investigation: https://dr-knz.net/mls-investigation.html
