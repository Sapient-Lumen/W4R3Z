---
id: P-0172
title: NATS + JetStream Interop & Ops Kit — standard evidence bundles, stream policy linting, and deterministic repros
status: idea
domains: [messaging, distributed-systems, ops, interop]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/async-nats
  - https://crates.io/crates/async-nats
  - https://crates.io/crates/nats
  - https://github.com/nats-io/nats.rs/discussions/442
---

## What it should provide others

A “batteries-included” operational kit for Rust services using NATS/JetStream:

- **Policy-first stream/consumer configuration** (retention, limits, ack policy, redelivery, max_age).
- **Deterministic repro** for production failures: a portable evidence bundle that can replay message flows.
- **Interop sanity**: compatibility checks across client versions and common server settings.

Deliverables:

- `cargo nats doctor`:
  - connectivity/auth diagnostics,
  - server feature discovery,
  - JetStream account/limits snapshot,
  - “this config looks dangerous” lint (e.g., infinite redelivery + low max_ack_pending).
- `cargo nats capture` → `*.natsbundle.zip` (redacted):
  - normalized stream/consumer configs,
  - sampled message metadata (no bodies by default),
  - timing traces,
  - replay harness scripts + `report.json`.

## Why this is still missing

The ecosystem has solid clients, but teams still hand-roll:

- config linting and “safe profiles”,
- reproducible debugging bundles and replay harnesses,
- migration/compat notes between client variants (sync legacy vs native async).

## Design principles

- **Interop via artifacts**: bundles should be loadable by a small reference replayer and by CI.
- **Redaction knobs**: keep bodies off by default; allow hashing and sampling.
- **Ergonomics for incidents**: one command to capture and one to replay.

## MVP

- Config snapshot + linting.
- A minimal capture format for stream/consumer settings and message metadata.
- Replay harness against a disposable local NATS server.

## v1

- Support JetStream KV/ObjectStore capture.
- “Golden scenarios” for redelivery, consumer restart, and disaster recovery checks.
- Optional adapters for non-Tokio runtimes via feature flags.

## Key risks / sharp edges

- Sensitive data: must default to redacted/hashed; make any plaintext export explicit.
- Replay fidelity: prioritize message ordering + timing envelopes; be honest about what is and isn’t replayed.
