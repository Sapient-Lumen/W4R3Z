---
id: P-0176
title: Fediverse Ops Kit — production-ready ActivityPub federation “missing middle” (queueing, retries, safety, observability, test corpora)
status: idea
domains: [fediverse, networking, web, reliability, security, observability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/activitypub/
  - https://crates.io/crates/activitypub-federation
  - https://docs.rs/activitypub_federation/
  - https://github.com/LemmyNet/activitypub-federation-rust/issues/31
---

## What it should provide others

A **production “federation substrate”** that sits *above* low-level ActivityPub request/response helpers and makes
real deployments boring:

- A durable **outbox queue** and retry engine (persisted, deduped, backoff, per-instance circuit breakers).
- A standard **delivery contract**:
  - “at least once” delivery semantics + idempotency keys,
  - canonical activity normalization and signature verification hooks,
  - replay-safe storage of inbound/outbound envelopes.
- A pluggable **anti-abuse / safety layer**:
  - per-instance policies (rate limits, content-type allowlists, signature requirements),
  - safe defaults for fetches (timeouts, size limits, content sniffing policy),
  - configurable *quarantine* for unknown instances.
- Observability batteries:
  - `tracing` spans for every request/queue state transition,
  - metrics for retry debt, per-instance failure modes, and queue age,
  - portable redacted `*.fediversebundle.zip` incident artifacts (request traces + queue state + policy snapshot).

The aim: “You write your app logic; the kit makes federation operationally safe.”

## Why this is still missing

ActivityPub is standardized and widely deployed, but federation is where apps get fragile:

- deployers need durable retries and instance-level policies (and frequently re-invent them),
- “works in dev” doesn’t survive hostile or flaky peers,
- debugging incidents requires reconstructing *what happened* across async queues and signature checks.

Even mature Rust-fediverse projects keep discovering missing operational pieces (e.g., persistent activity queues).

## MVP scope

- **Queue engine**
  - durable store trait (sled/sqlite/postgres backends),
  - retry scheduler + backoff + dead-letter queue,
  - idempotency key strategy + dedupe index.
- **Policy layer**
  - per-instance rule evaluation (deny/allow/quarantine, rate limits),
  - safe fetch defaults and hard limits.
- **Incident bundle**
  - `fediversebundle` format: redacted HTTP transcript, queue snapshot, policy config, and minimal reproduction notes.

## v1 scope

- Interop test harness: replay corpora of real-world exchanges (signed activities, fetches, redirects, weird headers).
- “Federation doctor”: validate instance config (timeouts, signature algorithms, clock skew, DNS).
- Optional E2EE storage for incident bundles (teams can share safely).

## Design notes

- Keep app/storage choices modular: the substrate should integrate with Axum/Actix/etc.
- Prefer “policy as data” (TOML/JSON) with a small stable schema, not “policy as Rust code” by default.
- Make **artifact-first debugging** the default: if a bug can’t be reproduced from the bundle, improve the bundle.
