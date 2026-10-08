# Gap: event-driven surfaces and delivery contracts

## What is missing
Rust has real clients and frameworks for queues, streams, pub/sub, and event envelopes, but it still lacks a **shared event-surface contract**.

Today there is no standard way to describe, exchange, diff, and review:
- which topics/subjects/queues/channels a program officially publishes to or consumes from,
- which messages/events are supported on each channel,
- which envelope and header conventions are part of the support promise,
- which delivery semantics matter (at-most-once, at-least-once, exactly-once aspirations, ordering scope, dedup/idempotency assumptions, ack/retry/DLQ posture),
- which schema attachments and compatibility rules are in force,
- which example message flows and failure/replay cases were actually checked,
- and what evidence exists that the declared channel/message surface still matches the shipped system.

That missing layer matters because event-driven interfaces are not niche glue anymore. AsyncAPI explicitly treats message-driven APIs as machine-readable communication contracts, and CloudEvents exists because event publishers otherwise describe events differently enough to hurt portability and tooling. Rust already has credible broker clients and event abstractions, but the ecosystem still lacks one portable review layer above them.

Sources:
- https://www.asyncapi.com/docs/reference/specification/v3.1.0
- https://www.asyncapi.com/docs/concepts/asyncapi-document
- https://cloudevents.io/
- https://docs.rs/async-nats
- https://docs.rs/rdkafka
- https://docs.rs/lapin
- https://docs.rs/sea-streamer
- https://docs.rs/testcontainers-modules

## The current seam is awkward
The ecosystem clearly has ingredients:
- `async-nats` exposes subjects, headers, core messages, and JetStream semantics including at-least-once and exactly-once-oriented delivery lanes,
- `rust-rdkafka` exposes producer/consumer roles, at-least-once guidance, and transactional/exactly-once-aware workflows,
- `lapin` gives serious AMQP/RabbitMQ support,
- `sea-streamer` shows there is demand for backend-agnostic stream processing across Kafka/Redpanda and Redis while keeping local testing practical,
- `cloudevents-sdk` gives Rust a typed CloudEvents lane,
- `schema_registry_converter` and related crates show schema-registry-backed message compatibility is already a real concern,
- and `testcontainers-modules` makes ephemeral Kafka/NATS/RabbitMQ-style test environments practical.

But real systems still hand-assemble their support story out of:
- broker-specific client setup,
- topic/subject/queue naming conventions,
- CloudEvents or ad hoc envelopes,
- schema registry subjects and migration lore,
- idempotency keys, retry/DLQ rules, and ordering assumptions,
- tracing/correlation headers,
- AsyncAPI or prose docs if they exist,
- integration tests for some happy/failure paths,
- and production runbooks for replay/backfill/poison-message handling.

The result is not that Rust lacks messaging crates.
The result is that there is no portable way to say:
- “these are the supported channels and roles,”
- “these are the message identities and schema attachments,”
- “this is the delivery/ordering/ack/dedup contract we claim,”
- “these examples and replay/failure paths were actually checked,”
- or “this deployment still matches the declared event surface.”

AsyncAPI helps, but it does not fully solve the Rust support problem by itself. AsyncAPI documents sender/receiver operations and protocol bindings, while CloudEvents standardizes event envelopes, but neither by itself captures all the Rust-side reality around local adapters, schema registries, delivery waivers, replay evidence, or transport-specific check results. That is the exact archive pattern worth elevating: strong parts, weak shared boundary.

Sources:
- https://www.asyncapi.com/docs/reference/specification/v3.1.0
- https://www.asyncapi.com/docs/concepts/asyncapi-document
- https://cloudevents.io/
- https://docs.rs/cloudevents-sdk
- https://docs.rs/async-nats
- https://docs.rs/rdkafka
- https://docs.rs/lapin
- https://docs.rs/sea-streamer
- https://docs.rs/schema_registry_converter
- https://docs.rs/testcontainers-modules

## Why this matters
This gap is bigger than “better broker docs.”
It affects:
1. **compatibility review** — renaming channels, changing message keys/headers, tightening required fields, or changing delivery/ordering assumptions can be real breaking changes;
2. **transport portability** — teams should be able to preserve supported event surfaces while moving between Kafka, NATS/JetStream, RabbitMQ, Redis streams, WebSocket event lanes, or hybrid HTTP+event systems;
3. **schema honesty** — message payload compatibility is only one part of the contract; envelope shape, metadata, correlation ids, keying, and retry/DLQ semantics also matter;
4. **testing realism** — many teams have producer/consumer integration tests, but not one portable artifact saying which channels, roles, and failure/replay behaviors were checked;
5. **operations clarity** — replay, dead-letter handling, backfill, partitioning/ordering scope, and idempotency are support claims, not invisible implementation details;
6. **ecosystem composition** — Schema Contract Kit, Service Surface Kit, Runtime Settings Kit, Identity Surface Kit, Diagnostic Surface Kit, and Observability Kit all need an event/service boundary without owning it.

AsyncAPI even explicitly warns against deriving a receiver document from a sender one or vice versa, which is a strong signal that perspective, channel identity, and supported operations are part of the contract rather than incidental metadata. Rust needs a native review layer that respects those distinctions.

Sources:
- https://www.asyncapi.com/docs/reference/specification/v3.1.0
- https://docs.rs/rdkafka
- https://docs.rs/async-nats
- https://docs.rs/sea-streamer
- https://cloudevents.io/

## What “good” looks like
A worthy contribution here is **not** another broker client, another hosted schema registry, another queue abstraction, or another message generator.

It is a shared event-surface boundary:
- one `event-surface/v0` describing service/app identity, supported transports, and the official event roles in scope,
- one `channel-map/v0` giving stable channel identities (topic/subject/queue/stream/address), producer/consumer role declarations, support levels, and links to attached schema/envelope/delivery artifacts,
- one `event-catalog/v0` describing message identities, envelope families (raw JSON, CloudEvents, broker-native headers, etc.), schema attachments, key/header contracts, and deprecation posture,
- one `delivery-profile/v0` describing ordering scope, ack/commit semantics, retry posture, DLQ/backoff/replay assumptions, idempotency expectations, retention assumptions, and exactly-once claims/limits,
- one `event-example-catalog/v0` containing canonical publish/consume flows, negative paths, poison-message examples, and replay/backfill examples,
- one `event-check-plan/v0` describing which transports/environments/checks were exercised,
- one `event-check-report/v0` recording schema/envelope drift, checked channel coverage, delivery/retry/ordering/idempotency findings, and raw attachment pointers,
- one optional `event-diff-report/v0` for additive/breaking surface changes,
- and one `event-pack/v0` bundle for CI, docs, release review, ops handoff, and later archaeology.

That would let Rust teams treat event-driven interfaces as reviewable support surfaces instead of a pile of broker config, schemas, AsyncAPI fragments, and incident folklore.
