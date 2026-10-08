---
id: P-0279
title: NATS + JetStream Interop & Evidence Kit — canonical protocol traces and reproducible replay bundles
status: idea
domains: [messaging, streaming, nats, jetstream, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://docs.nats.io/nats-concepts/jetstream
  - https://beta-docs.nats.io/ref/protocols/jetstream
  - https://github.com/nats-io/nats.docs/blob/master/using-nats/jetstream/nats_api_reference.md
  - https://crates.io/crates/async-nats
  - https://crates.io/crates/nats
---

## What it should provide others

A **portable way to capture, replay, and diff** NATS Core + JetStream interactions across:
- client libraries (`async-nats`, legacy `nats`, others)
- server versions/configurations (JetStream enabled clusters)
- operational incidents (consumer lag, replay mismatches, stream config drift)

The missing piece is not another client; it is **standardized evidence artifacts** (`*.natsbundle.zip`) plus adapters and a runner.

## Proposed crate shape (workspace)

- `natskit-ir` — canonical event model for:
  - connect/auth negotiation (sanitized)
  - publish/subscribe, request/reply
  - JetStream management API interactions (streams/consumers)
  - acks, redeliveries, replay windows
- `natskit-capture` — adapter hooks for `async-nats` (middleware layer) and log parsers
- `natskit-runner` — scenario DSL + topology runner (single server → clustered)
- `natskit-diff` — semantic diff for “why did replay diverge?”
- `natskit-bundle` — `*.natsbundle.zip` IO + redaction presets for tokens/subjects/payloads

## Minimum lovable MVP (4–8 weeks)

1. Bundle schema + canonicalization for JetStream management API request/reply patterns
2. Capture adapter for `async-nats` publish/subscribe + JS publish/ack
3. Runner with 3 scenarios:
   - stream + durable consumer setup, produce N msgs, replay
   - ack policy + redelivery demonstration
   - stream config drift detector (before/after snapshots)

Deliverable: `cargo natskit run --scenario replay-smoke --out run.natsbundle.zip`.

## De-risk plan

- Start with **client-side capture** (SDK hooks) before server instrumentation.
- Pin server versions/config in fixtures; variability is the enemy of diffable artifacts.
- Use structured redaction so bundles can be shared outside the org.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 3
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
