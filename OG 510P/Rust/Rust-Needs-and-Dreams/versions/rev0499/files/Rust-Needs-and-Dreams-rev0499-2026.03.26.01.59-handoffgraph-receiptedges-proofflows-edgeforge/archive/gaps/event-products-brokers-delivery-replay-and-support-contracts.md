# Gap: event products, brokers, replay, and support contracts

## What is missing
Rust already has credible event and messaging ingredients, and this archive already has an **Event Surface Kit** for channels, envelopes, delivery profiles, and checked message-flow evidence.

What is still missing is the **productization layer above that kit**.

Today, Rust teams still do not have one portable way to describe, exchange, diff, and review:
- which broker families and runtime lanes are officially part of a product;
- which channels/subjects/topics/streams/queues are support promises versus internal plumbing;
- which schema/envelope combinations are merely accepted versus truly supported;
- which replay, backfill, dead-letter, idempotency, and consumer-position assumptions belong to the support contract;
- which runtime settings, credentials, TLS roots, topology modes, or local-test adapters materially change behavior;
- which observability and incident artifacts prove that the declared event product still matches reality;
- and which docs/examples are canonical enough for release review, operator handoff, and downstream consumers.

That missing layer matters because the ecosystem is no longer a single transport or a single style of event system:
- AsyncAPI 3.1.0 explicitly frames the document as a **communication contract** for message-driven APIs;
- CloudEvents explicitly exists because publishers otherwise describe events differently enough to hurt portability;
- `async-nats` already spans pub/sub plus JetStream, key-value, object-store, and service lanes;
- `rdkafka` already spans async production/consumption plus idempotent and transactional EOS workflows;
- `lapin` already spans AMQP 0.9.1 with runtime and TLS-backend diversity;
- `zenoh` already blends pub/sub, query/reply, storage, and computation, and its configuration surface is explicitly unstable;
- `cloudevents-sdk` for Rust is real but still explicitly unstable;
- `sea-streamer` and `testcontainers` show that backend-agnostic and ephemeral-test lanes are already part of normal Rust practice.

The missing contribution is therefore **not** another broker client, schema registry, transport abstraction, or hosted event platform.
It is the portable boring layer that keeps **event truth + runtime truth + replay truth + support truth** separate while still letting them compose.

Sources:
- https://www.asyncapi.com/docs/reference/specification/latest
- https://www.asyncapi.com/docs/concepts/asyncapi-document
- https://cloudevents.io/
- https://docs.rs/async-nats/latest/async_nats/
- https://docs.rs/rdkafka/latest/rdkafka/
- https://docs.rs/lapin/latest/lapin/
- https://docs.rs/zenoh/latest/zenoh/
- https://github.com/cloudevents/sdk-rust
- https://docs.rs/sea-streamer
- https://docs.rs/testcontainers/latest/testcontainers/
- https://docs.rs/crate/testcontainers-modules/latest

## The current seam is awkward
The archive can already describe a message-driven interface reasonably well with `event-surface`, `channel-map`, `event-catalog`, `delivery-profile`, and `event-check-report`.

But real products are still forced to assemble their support story out of:
- transport- and broker-specific client setup;
- topic/subject/queue naming conventions;
- CloudEvents or ad hoc envelope rules;
- schema registry subjects and compatibility policy;
- consumer-group, durable-subscription, retention, replay, and ordering lore;
- environment variables, credentials, TLS roots, and cluster/topology settings;
- checked local fixtures, ephemeral broker tests, or staging-only runbooks;
- lag/retry/DLQ/poison-message observability;
- and README/setup docs that are usually the only operator-facing product surface.

That is a productization smell.
The ecosystem does **not** lack event libraries.
It lacks a portable way to say:
- “this is the official event product surface,”
- “these are the runtime/topology/settings assumptions that activate it,”
- “these are the replay/recovery/incident guarantees we actually support,”
- “these are the checked docs/examples/traces that back those claims,”
- and “these are the downstream consumers that may import the result.”

The Rust-side evidence points in the same direction:
- `async-nats` now exposes JetStream, key-value store, object store, and service API examples, while also deprecating the old sync client;
- `rdkafka` exposes exactly-once semantics via idempotent/transactional producers and read-committed consumers, but is still explicit that its APIs are under active development;
- `lapin` has runtime and TLS-backend choice baked into the crate surface;
- `zenoh` mixes pub/sub with query/reply and storage/computation while explicitly saying configuration is unstable;
- `cloudevents-sdk` supports some protocol bindings and not others while explicitly warning that the crate is WIP and unstable.

That is exactly the archive pattern worth elevating: **strong ingredients, weak shared product boundary**.

Sources:
- https://docs.rs/async-nats/latest/async_nats/
- https://docs.rs/rdkafka/latest/rdkafka/
- https://docs.rs/lapin/latest/lapin/
- https://docs.rs/zenoh/latest/zenoh/
- https://docs.rs/zenoh/latest/zenoh/struct.Config.html
- https://github.com/cloudevents/sdk-rust
- https://docs.rs/sea-streamer

## Why this matters
This is bigger than “better broker docs”.
It affects:
1. **product support honesty** — changing channel names, delivery posture, replay guarantees, or required metadata can be as real a breaking change as changing an HTTP route;
2. **transport diversity without fiction** — Kafka, NATS/JetStream, RabbitMQ, Zenoh, Redis-stream lanes, and HTTP/webhook bridges should not be forced into one fake universal runtime model;
3. **replay and incident response** — replay, backfill, DLQ, poison-message, retention, and consumer-position assumptions are support contracts, not invisible implementation details;
4. **runtime activation clarity** — event products often depend on cluster topology, TLS roots, credentials, durable names, stream provisioning, and env/config precedence that deserve explicit artifacts;
5. **observability reuse** — lag, ack, retry, DLQ, consumer-group, and message-correlation evidence should be importable instead of rediscovered from dashboards and ad hoc tracing;
6. **cross-stack composition** — Service, Protocol, Local-First, Media, Agent, Client, and Data productization stacks all need event products as attachments without redefining them.

AsyncAPI explicitly describes the AsyncAPI document as a **communication contract between senders and receivers**, and CloudEvents explicitly standardizes event metadata to improve consistency, accessibility, and portability. Rust needs a product boundary that respects those distinctions all the way through runtime activation, replay posture, and support claims.

Sources:
- https://www.asyncapi.com/docs/concepts/asyncapi-document
- https://cloudevents.io/
- https://docs.rs/async-nats/latest/async_nats/
- https://docs.rs/rdkafka/latest/rdkafka/

## What “good” looks like
A worthy contribution here is **not** another queue abstraction, broker client, schema registry, or hosted event platform.

It is a thin event-productization layer above the Event Surface Kit:
- one `event-envelope/v0` declaring the supported broker family, channel/event boundary, imported schema/envelope/delivery artifacts, and the product subject in scope;
- one `event-activation-report/v0` recording runtime-selection truth: broker topology, credentials/TLS posture, consumer-group or durable-subscription assumptions, provisioning notes, local-vs-CI-vs-prod mode, and redaction-aware settings capture;
- one `event-replay-report/v0` recording supported replay/backfill/DLQ/poison-message/import/export posture and the exact evidence that was checked;
- one `event-support-report/v0` or imported support/docproof attachment making canonical setup, examples, support levels, and non-goals explicit;
- one optional `event-product-diff/v0` explaining what changed between releases or profiles;
- and one `event-product-pack/v0` that bundles the imported lower-layer artifacts and preserves which facts came from Event Surface, Schema Contract, Runtime Settings, Observability, and Support Envelope.

That would let Rust teams review event products as products instead of as a pile of client setup, schema lore, replay runbooks, and dashboard screenshots.
