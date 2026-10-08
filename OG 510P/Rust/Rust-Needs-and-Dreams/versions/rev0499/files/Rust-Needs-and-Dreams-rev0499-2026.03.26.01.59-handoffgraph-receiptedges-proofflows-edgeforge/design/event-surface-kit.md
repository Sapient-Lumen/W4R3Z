# Design: Event Surface Kit (`cargo eventcheck`, `event-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust program’s supported event-driven surface: channels, producer/consumer roles, message identities, envelopes, header/key contracts, delivery semantics, checked examples, and evidence that the declared event surface still matches the program.

This should **not** replace `async-nats`, `rdkafka`, `lapin`, `sea-streamer`, `cloudevents-sdk`, schema registries, AsyncAPI, or broker products.
It should make them compose better and make support claims reviewable.

## References (signals)
- AsyncAPI 3.1.0 describes message-driven APIs in a machine-readable format and is protocol-agnostic across AMQP, MQTT, WebSockets, Kafka, STOMP, HTTP, and more.
  https://www.asyncapi.com/docs/reference/specification/v3.1.0
- AsyncAPI concept docs explicitly frame the document as a communication contract between senders and receivers.
  https://www.asyncapi.com/docs/concepts/asyncapi-document
- CloudEvents exists because publishers otherwise describe event data differently enough to hurt common libraries, tooling, and portability.
  https://cloudevents.io/
- `cloudevents-sdk` gives Rust a typed CloudEvents implementation.
  https://docs.rs/cloudevents-sdk
- `async-nats` exposes subjects, headers, messages, and JetStream semantics, including at-least-once and exactly-once-oriented lanes.
  https://docs.rs/async-nats
- `rdkafka` exposes low-level and high-level producers/consumers, explicit at-least-once guidance, and transactional/EOS workflows.
  https://docs.rs/rdkafka
- `lapin` gives Rust serious AMQP 0.9.1 / RabbitMQ coverage.
  https://docs.rs/lapin
- `sea-streamer` shows demand for backend-agnostic stream processors across Kafka/Redpanda and Redis with local-test-friendly tooling.
  https://docs.rs/sea-streamer
- `schema_registry_converter` shows Confluent-schema-registry-compatible encoding/decoding is already a normal Rust workflow.
  https://docs.rs/schema_registry_converter
- `testcontainers-modules` gives Rust practical ephemeral infrastructure for broker-backed integration tests.
  https://docs.rs/testcontainers-modules
- `asyncapi-rust` is emerging as a Rust code-first AsyncAPI generation lane for WebSockets and async protocols, which is a useful signal that appetite exists even though the broader substrate is still missing.
  https://github.com/mlilback/asyncapi-rust

## Core components

### 1) `event-surface/v0`
A design-time declaration of the supported event interface for a binary/service/workspace.

Required ideas:
- system/service identity
- deployment profile / environment class
- transports in scope:
  - Kafka / Redpanda-compatible
  - NATS / JetStream
  - AMQP / RabbitMQ
  - Redis streams / generic stream backends
  - WebSocket/event lanes as optional attachments in v0
  - HTTP/webhook emission/consumption as optional linked surfaces in v0
- perspective:
  - producer / sender
  - consumer / receiver
  - bidirectional / bridge / relay
- support levels:
  - supported
  - deprecated
  - experimental
  - internal
- linked attachments:
  - schema artifacts
  - CloudEvents profiles
  - AsyncAPI docs
  - settings references
  - observability fields
  - auth/credential assumptions

Design rule: preserve sender/receiver perspective explicitly. Do not derive one from the other by accident.

### 2) `channel-map/v0`
Stable identities for channels.

Each channel entry should capture:
- stable channel id
- transport family
- concrete address/name:
  - topic
  - subject
  - queue
  - exchange + routing-key pattern
  - stream name
  - wildcard/pattern rules
- role:
  - sends
  - receives
  - request/reply or command/reply attachment
- support level
- ownership / upstream / downstream notes
- partitioning or sharding scope when relevant
- retention or ephemeralness posture when relevant
- linked message ids / event ids
- linked delivery profile id
- linked settings or credential references

Design rule: keep channel identity separate from message schemas and separate from delivery rules. One channel may carry multiple event/message identities; one event identity may appear on multiple channels.

### 3) `event-catalog/v0`
Declared messages/events and their envelopes.

Each event entry should support:
- stable event/message id
- human-facing name + summary
- payload schema attachments (JSON Schema / Avro / Protobuf / raw serde type refs / custom refs)
- envelope family:
  - raw payload only
  - CloudEvents structured
  - CloudEvents binary
  - broker-native metadata + payload
  - custom envelope attachment
- key/header/attribute contracts:
  - partition key or routing key expectations
  - required correlation/request/causation ids
  - tracing fields
  - tenant/user identifiers when policy allows
  - content-type / schema-version / message-id attributes
- compatibility posture:
  - additive tolerated
  - strict
  - version-gated
  - subject to registry policy
- deprecation policy / replacement pointers
- links to raw AsyncAPI / CloudEvents / schema-registry subjects / schema-pack ids

Design rule: do not flatten CloudEvents metadata, broker headers, and payload schema into one fake canonical object. Preserve raw truth and normalize only enough to review it.

### 4) `delivery-profile/v0`
Transport and processing semantics that are part of the support promise.

Possible fields:
- delivery expectation:
  - at-most-once
  - at-least-once
  - exactly-once claimed
  - effectively-once / idempotency-based
- ordering scope:
  - none
  - per channel
  - per partition / key
  - per aggregate / entity id
- ack / commit / confirm posture
- consumer-group / durable-subscription assumptions
- retry/backoff policy references
- dead-letter / poison-message policy
- replay/backfill policy
- dedup/idempotency assumptions
- transaction boundary or outbox/inbox references
- retention / compaction / expiration assumptions
- unsupported / best-effort notes

Design rule: exactly-once claims must record prerequisites and limits explicitly. Do not let “transactional producer exists” silently turn into a blanket support claim.

### 5) `event-example-catalog/v0`
Small canonical examples and checked scenarios.

Possible contents:
- example published message
- example consumed message
- example CloudEvents structured/binary representations
- example key/header sets
- retry / DLQ / poison-message cases
- replay / backfill example
- schema evolution example
- provenance labels:
  - illustrative only
  - generated
  - checked in CI
  - captured from fixture replay

Design rule: keep examples small and scrubbed. Do not dump production event logs.

### 6) `event-check-plan/v0`
A concrete plan for what is checked.

Required ideas:
- channels/events selected
- transport environments exercised
- schema/envelope validators used
- delivery/ordering/retry/idempotency checks performed
- checked broker fixtures or ephemeral test environments
- AsyncAPI/CloudEvents/schema-registry comparison steps
- unsupported or intentionally omitted lanes
- perspective coverage:
  - producer-only
  - consumer-only
  - round-trip / end-to-end

This is where the kit stops pretending “we have a topic and a schema” means “the event interface is reviewed.”

### 7) `event-check-report/v0`
Evidence from tests, comparisons, and runtime checks.

Possible contents:
- channel coverage summary
- event/schema/envelope drift findings
- required-header / key / attribute mismatches
- checked ordering or replay findings
- retry / DLQ / poison-message check outcomes
- CloudEvents or AsyncAPI conformance findings
- end-to-end flow pass/fail results
- raw attachments:
  - AsyncAPI docs
  - CloudEvents fixtures
  - broker metadata dumps
  - schema-registry subject snapshots
  - test transcripts
  - captured messages from local fixtures

### 8) `event-diff-report/v0` (optional)
For compatibility-sensitive changes:
- channel added/removed/renamed
- role changed (producer/consumer)
- event identity added/removed/renamed
- header/key requirement changed
- schema compatibility changed
- delivery/ordering/retry policy changed
- support level changed
- deprecation/sunset notes added or removed

Should distinguish:
- additive changes
- breaking changes
- transport/configuration-only changes
- documentation-only drift
- manual rollout/backfill coordination required

### 9) `event-pack/v0`
Bundle format containing:
- `event-surface/v0`
- `channel-map/v0`
- `event-catalog/v0`
- one or more `delivery-profile/v0`
- optional `event-example-catalog/v0`
- one or more `event-check-report/v0`
- optional `event-diff-report/v0`
- optional raw attachments: AsyncAPI docs, CloudEvents examples, schema-registry snapshots, broker test fixtures, replay artifacts, and check transcripts

This is the unit that should travel through CI, docs, release review, ops handoff, and later archaeology.

### 10) `cargo eventcheck`
Reference UX:
- `cargo eventcheck init`
- `cargo eventcheck channels`
- `cargo eventcheck envelopes`
- `cargo eventcheck delivery`
- `cargo eventcheck examples`
- `cargo eventcheck diff`
- `cargo eventcheck pack`

`cargo eventcheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true broker client, schema registry, or event generator.

## Default policy
- **Separate channel identity, event identity, and delivery semantics.**
- **Preserve sender vs receiver perspective explicitly.**
- **Preserve raw AsyncAPI / CloudEvents / schema-registry truth as attachments** rather than flattening everything into one fake canonical event format.
- **Treat headers, keys, ordering scope, retries, DLQs, and replay posture as support surfaces**, not just implementation details.
- **Distinguish checked examples from illustrative examples** so docs stay honest.
- **Prefer transport adapters over transport replacement** in v0.

## What the kit should provide to others
- **Schema Contract Kit:** attach payload-schema and compatibility artifacts to stable event ids without pretending schema alone is the whole event contract.
- **Service Surface Kit:** link HTTP/webhook or request/reply boundaries to message-driven boundaries without flattening them into one protocol model.
- **Runtime Settings Kit:** reference broker addresses, credential sources, subject prefixes, retention knobs, and feature flags without absorbing runtime config itself.
- **Identity Surface Kit:** attach auth/credential/tenant claims where they affect channel access, but keep broader auth models separate.
- **Observability Kit:** align tracing/correlation ids and message metadata with the declared event surface without making telemetry the source of truth.
- **Diagnostic Surface Kit:** map poison-message, validation, and replay failures to public diagnostics without treating error formatting as the event contract.
- **Replay Kit / DST Kit:** reuse checked message-flow artifacts and failure cassettes without taking ownership of the declared interface.

## Overlap boundaries
- **Not another broker client:** client/runtime ergonomics remain with `async-nats`, `rdkafka`, `lapin`, `redis`, and friends.
- **Not another queue abstraction:** generic traits like `sea-streamer` remain transport abstractions; this kit is the review/evidence layer above them.
- **Not AsyncAPI itself:** AsyncAPI remains the protocol-agnostic API description format; this kit adapts to it and adds Rust-side evidence, checks, and pack conventions.
- **Not CloudEvents itself:** CloudEvents remains the common event envelope/spec; this kit records when and how it is used and validated.
- **Not Schema Contract Kit:** payload/schema compatibility remains distinct from channel identity, delivery guarantees, and replay/DLQ posture.
- **Not Service Surface Kit:** request/response HTTP service boundaries remain separate even when linked to event/webhook flows.
