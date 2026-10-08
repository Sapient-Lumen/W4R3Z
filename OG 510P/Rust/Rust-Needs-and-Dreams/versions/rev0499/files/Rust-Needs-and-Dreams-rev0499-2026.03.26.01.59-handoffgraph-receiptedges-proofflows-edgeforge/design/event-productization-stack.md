# Design: Event Productization Stack (Event Surface + Schema Contract + Runtime Settings + Observability + Support Envelope)

## Goal
Turn Rust event-driven systems into a **portable productization stack** instead of leaving each project to express its broker, delivery, replay, schema, runtime, and support contract as a tangle of client builders, AsyncAPI fragments, CloudEvents helpers, schema-registry settings, queue runbooks, and incident folklore.

The stack should **not** replace `async-nats`, `rdkafka`, `lapin`, `zenoh`, `sea-streamer`, CloudEvents, AsyncAPI, testcontainers, broker products, or schema registries.
It should make them compose better and make supported event behavior reviewable.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust publish or consume messages?”
They say the missing problem is **what a Rust project can honestly claim to publish, consume, replay, recover, activate, observe, and support**:
- AsyncAPI 3.1.0 explicitly frames message-driven APIs as machine-readable contracts between senders and receivers;
- CloudEvents exists because publishers otherwise describe event data differently enough to hurt portability and tooling;
- `async-nats` already spans pub/sub plus JetStream, key-value store, object store, and service API, while the old synchronous client is deprecated;
- `rdkafka` already spans async producer/consumer roles plus exactly-once semantics through idempotent and transactional producers with read-committed consumers, but still warns that the APIs are under active development;
- `lapin` already carries runtime and TLS-backend choice in its crate surface;
- `zenoh` already blends pub/sub, query/reply, storage, and computation, while explicitly saying its config surface is unstable;
- the Rust CloudEvents SDK is real, but still explicitly WIP and unstable, with some bindings supported and others missing;
- `sea-streamer` and `testcontainers` already show that backend-agnostic and ephemeral-test workflows are part of ordinary Rust practice.

Together, those signals argue that the missing contribution is **not** another broker wrapper, local fake broker, or message-schema generator.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Event Surface Kit: declared channel/event/delivery truth
Event Surface owns the **declared interface layer**:
- supported broker or transport family;
- channel identities and roles;
- event/message identities;
- envelope families;
- delivery semantics and replay/DLQ/idempotency posture;
- checked event-interface evidence.

This layer answers questions like:
- “What channels and message identities are part of the product surface?”
- “What delivery and replay semantics are promised?”
- “Which examples or checks back those claims?”

Design rule: **event products must not invent support truth from broker code or dashboards after the fact**.

### 2) Schema Contract Kit: payload-evolution truth
Schema Contract owns the **payload and compatibility layer**:
- payload schemas or contract references;
- compatibility mode;
- evolution and migration posture;
- registry or subject attachments where relevant.

This layer answers questions like:
- “What message payload contract is actually supported?”
- “What counts as additive, breaking, or migration-gated?”
- “Which schema or registry subject is canonical?”

Design rule: **schema truth must not be silently folded into broker headers or CloudEvents metadata**.

### 3) Runtime Settings (+ optional credentials imports): activation truth
Runtime Settings owns the **activation boundary**:
- broker endpoints, topology mode, and profile selection;
- stream/consumer-group/durable names and provisioning assumptions;
- TLS/root and credential source posture;
- local vs CI vs staging vs production activation;
- environment and precedence rules;
- redaction-aware effective-setting capture.

This layer answers questions like:
- “What settings make the declared event surface real?”
- “Which topology or cluster assumptions materially change behavior?”
- “Which credential or TLS choices are part of support versus local setup?”

Design rule: **event-product claims must not silently depend on undocumented env vars, hidden broker setup, or one operator’s shell history**.

### 4) Observability: replay, lag, retry, and incident evidence
Observability owns the **runtime evidence layer**:
- message correlation and diagnostic identity;
- delivery/ack/retry/DLQ findings;
- lag and consumer health attachments;
- replay or backfill traces;
- runtime reports linking event behavior to actual operation.

This layer answers questions like:
- “Can the project prove that replay or DLQ behavior still matches the declared support contract?”
- “Which signal names and correlations exist for event operations?”
- “What runtime evidence is portable enough for support and incident work?”

Design rule: **replay and incident truth must not stay trapped in one broker dashboard or one bespoke trace view**.

### 5) Support Envelope + DocProof: supported event-product truth
Support Envelope and DocProof together own the **support/docs boundary**:
- support levels per broker/profile/lane;
- checked setup docs/examples/transcripts;
- platform/runtime caveats;
- release or deprecation posture;
- explicit non-goals and unsupported modes.

This layer answers questions like:
- “Is Kafka/NATS/RabbitMQ/Zenoh support real or merely experimental?”
- “Are replay and backfill part of the support promise or only internal ops knowledge?”
- “Which docs and examples are canonical enough for downstream users?”

Design rule: **one staging demo is not a support contract**.

### 6) Importing consumers
The stack matters when real consumers can import it honestly:
- **Service Productization** can attach event products instead of pretending every async interface is HTTP-shaped;
- **Protocol Productization** can distinguish wire protocol truth from higher-level event product truth;
- **Local-First / Media / Agent / Client / Data** stacks can import event lanes without redefining delivery or replay semantics;
- **Release / Incident / Policy / Support** consumers can reason about supported event behavior without scraping dashboards and runbooks.

Design rule: **consumers import selected event-product facts; they do not redefine them into one fake “messaging maturity” score**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust event platform.”
It is a portable boring stack with clear boundaries:

1. **channel/event/delivery truth first**
   - prove stable event-surface artifacts can name the product boundary;
2. **schema/evolution truth second**
   - prove payload compatibility and registry subjects can attach without erasing envelope or delivery truth;
3. **activation truth third**
   - prove broker endpoints, topology modes, durable names, credentials, and env precedence can be attached honestly;
4. **replay/observability truth fourth**
   - prove replay, DLQ, retry, and correlation evidence can travel as portable artifacts;
5. **support/docs and consumer imports fifth**
   - prove downstream service/release/support/incident consumers can reuse the same facts.

An eventual aggregate artifact may exist, but it should be a **thin linked pack of imported artifacts**, not a mega-schema that erases event truth, schema truth, activation truth, replay truth, and support truth.

## Proposed aggregate artifact family
A plausible aggregate lane is:
- `event-envelope/v0`
  - subject identity, selected broker/profile, imported artifact pointers, and declared event-product boundary;
- `event-activation-report/v0`
  - effective runtime-setting/topology/credential posture with redaction-aware capture;
- `event-replay-report/v0`
  - replay/backfill/DLQ/poison-message/import/export findings and their checked evidence;
- `event-product-diff/v0`
  - drift between versions or profiles;
- `event-product-pack/v0`
  - thin bundle linking:
    - `event-pack/v0`
    - schema attachments or `schema-pack` pointers
    - runtime-setting reports
    - observability/replay reports
    - support/docs attachments
    - optional service/release/incident import pointers

The point is not one new truth engine.
The point is a **reviewable event-product handoff**.

## Ranked first execution lanes
1. **single-broker event lane**
   - best first exporter because it proves the boundary without requiring universal transport fiction;
2. **delivery/replay lane**
   - proves exactly-once/effectively-once/replay/DLQ claims can be exported honestly;
3. **schema/registry lane**
   - proves payload evolution can attach without swallowing event or runtime truth;
4. **activation/credential/observability lane**
   - proves topology/settings/runtime evidence can travel without leaking secrets or flattening environments;
5. **support and consumer lane**
   - proves service/release/support/incident consumers can import the results.

## Non-goals
- a hosted broker product;
- a fake universal queue abstraction;
- replacing AsyncAPI, CloudEvents, or schema registries;
- pretending Kafka, NATS, RabbitMQ, Zenoh, Redis-stream, and webhook lanes are one runtime model;
- flattening event truth, schema truth, activation truth, replay truth, and support truth into one “messaging enabled” bit.

## Archive implications
- The archive should now treat **Event Surface + Schema Contract + Runtime Settings + Observability + Support Envelope** as a coupled **Event Productization Stack** in frontier and priority discussions, with Service / Protocol / Local-First / Media / Agent / Client / Data as importing consumers.
- Future revisions should prefer **channel/event/delivery truth, schema/evolution truth, activation truth, replay/observability truth, support/docs truth, and consumer imports** over another broker client comparison, schema-registry tangent, replay daemon, or platform-specific operator guide.
- When Service, Protocol, Local-First, Media, Agent, Client, or Data work cites event readiness, it should import **event truth**, **schema truth**, **activation truth**, **replay evidence**, and **support truth** separately.

## Read this together with
- `gaps/event-products-brokers-delivery-replay-and-support-contracts.md`
- `design/event-surface-kit.md`
- `design/schema-contract-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
- `design/service-productization-stack.md`
- `design/protocol-productization-stack.md`

## References (signals)
- AsyncAPI spec and contract docs:
  https://www.asyncapi.com/docs/reference/specification/latest
  https://www.asyncapi.com/docs/concepts/asyncapi-document
- CloudEvents:
  https://cloudevents.io/
  https://github.com/cloudevents/spec
- Rust event ingredients:
  https://docs.rs/async-nats/latest/async_nats/
  https://docs.rs/rdkafka/latest/rdkafka/
  https://docs.rs/lapin/latest/lapin/
  https://docs.rs/zenoh/latest/zenoh/
  https://docs.rs/zenoh/latest/zenoh/struct.Config.html
  https://github.com/cloudevents/sdk-rust
  https://docs.rs/sea-streamer
  https://docs.rs/testcontainers/latest/testcontainers/
  https://docs.rs/crate/testcontainers-modules/latest
