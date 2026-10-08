# Epic proposal: Event Surface Kit

## Thesis
Rust’s event-driven ecosystem is mature enough that the missing contribution is no longer “yet another Kafka/NATS/RabbitMQ client.”
The higher-leverage missing piece is a **portable event-surface contract** that lets teams declare, diff, validate, and ship what their event-driven systems actually promise: channel identities, producer/consumer roles, message identities, envelope/header/key contracts, delivery semantics, checked message flows, and linked schema/runtime evidence.

In other words: Rust needs a boring, attachable `event-pack/v0` more than it needs another thin wrapper over one broker or one schema registry.

## Why now
The ecosystem signals line up:
- AsyncAPI is explicit that message-driven APIs are communication contracts between senders and receivers.
- CloudEvents exists because inconsistent event description harms portability and tooling.
- Rust already has serious clients for NATS/JetStream, Kafka, and AMQP/RabbitMQ.
- Rust also has typed CloudEvents support, schema-registry helpers, and backend-agnostic stream abstractions.
- ephemeral broker-backed tests are practical through `testcontainers-modules`.
- emerging Rust AsyncAPI generation work (`asyncapi-rust`) suggests demand is real, even if the broader substrate is still early.

That means the missing substrate is not raw capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://www.asyncapi.com/docs/reference/specification/v3.1.0
- https://www.asyncapi.com/docs/concepts/asyncapi-document
- https://cloudevents.io/
- https://docs.rs/async-nats
- https://docs.rs/rdkafka
- https://docs.rs/lapin
- https://docs.rs/sea-streamer
- https://docs.rs/schema_registry_converter
- https://docs.rs/testcontainers-modules
- https://github.com/mlilback/asyncapi-rust

## What should be built
A first credible version should ship:
1. `event-surface/v0`, `channel-map/v0`, `event-catalog/v0`, `delivery-profile/v0`, optional `event-example-catalog/v0`, `event-check-plan/v0`, `event-check-report/v0`, optional `event-diff-report/v0`, and `event-pack/v0`
2. adapters for common Rust transports and adjacent surfaces (`async-nats`, `rdkafka`, `lapin`, `sea-streamer`, CloudEvents, AsyncAPI docs, schema-registry snapshots, ephemeral broker tests)
3. docs/reference generation for supported channels, producer/consumer roles, message identities, headers/keys, and delivery expectations
4. validation/reporting support for channel drift, envelope/header drift, schema attachment mismatch, replay/DLQ/idempotency check outcomes, and sender-vs-receiver perspective mistakes
5. release/CI examples showing event packs attached to services, consumers, background workers, and ops handoff

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one Kafka/Redpanda service using `rdkafka` plus schema-registry-backed payloads and end-to-end producer/consumer checks
- one NATS/JetStream worker using subjects, headers, and retry/replay semantics captured explicitly
- one RabbitMQ/AMQP pipeline using `lapin` with DLQ/poison-message behavior modeled as support data rather than runbook prose
- one backend-agnostic `sea-streamer` pilot proving the artifacts are not transport-exclusive
- one CloudEvents-first service or bridge proving that envelope-level interoperability can attach cleanly to the same pack

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve channel identity, sender/receiver posture, event ids, and delivery claims
2. **v0.2 adapters**
   - support `async-nats`, `rdkafka`, `lapin`, CloudEvents attachments, and ephemeral broker-backed tests
   - support raw AsyncAPI and schema-registry attachments without flattening either one
3. **v0.3 cross-kit integration**
   - integrate with Schema Contract, Service Surface, Runtime Settings, Observability, Diagnostic Surface, and Replay workflows
   - support diff/baseline workflows across transports and deployment modes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one broker stack

## Success metrics
- Teams can review event-interface changes as explicit artifacts instead of reading broker config diffs, schema snippets, and prose.
- Supported channels, envelopes, and delivery assumptions remain documented from one declared source.
- Replay/backfill/DLQ behavior becomes easier to trust because checked and illustrative material stay distinct.
- Transport migrations become easier because support claims survive beyond one broker client or local test harness.
- Rust event-driven systems become easier to hand off to platform, documentation, client-generation, and ops workflows without bespoke glue.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Schema Contract Kit covers payload/schema compatibility,
- Service Surface Kit covers HTTP/application service boundaries,
- Runtime Settings Kit covers config,
- Identity Surface Kit covers access,
- Observability Kit covers telemetry,
- and Replay/DST/Device-Lab-style kits cover execution evidence.

But none of those is the portable contract for the **composed event-driven boundary itself**.
Event Surface Kit is the missing substrate that keeps channels, roles, envelopes, schemas, and delivery evidence attached to one reviewable interface without absorbing them into one mega-format.
