# Design: Event Productization pilot program

## Goal
Turn the new **Event Productization Stack** into a ranked execution plan instead of a vague “Rust messaging needs better tooling” sentiment.

This pilot program should prove that Rust can export and review **event product truth** without pretending one broker, one schema registry, one replay model, or one event spec owns the whole problem.

## Why this pilot order
The point is to begin where the ecosystem is already undeniably real:
- AsyncAPI and CloudEvents already define portable contract/envelope lanes;
- `async-nats`, `rdkafka`, `lapin`, and `zenoh` already show strong but different runtime realities;
- `sea-streamer` and `testcontainers` show that backend-agnostic and ephemeral-test workflows are already practical;
- the Rust CloudEvents SDK is still unstable, which is a warning against prematurely pretending the product boundary is already solved.

So the pilots should begin with **single-lane honesty**, then add replay, schema, activation, and consumer imports in that order.

## Candidate pilot artifacts

### 1) `event-lane-brief/v0`
A short design artifact for one selected event lane:
- subject under review
- broker/runtime family
- producer/consumer scope
- imported event/schema/settings/support artifacts
- non-goals and explicitly deferred lanes

### 2) `event-escalation-policy/v0`
Defines the handoff order:
- interface drift escalation
- replay/DLQ/backfill escalation
- runtime/topology/credential escalation
- support/docs escalation
- downstream consumer escalation

### 3) `event-correlation-budget/v0`
Defines which evidence links are required:
- channel/event ids ↔ schema ids
- channel/event ids ↔ runtime settings / topology / durable names
- channel/event ids ↔ observability or replay evidence
- product claims ↔ support/docs attachments
- downstream consumers ↔ imported event-product artifacts

### 4) `event-readiness-scorecard/v0`
Decides whether a pilot is credible:
- are lane boundaries explicit?
- are replay and recovery claims honest?
- is runtime activation visible?
- can at least one downstream consumer import the result?
- should the lane be `promote`, `pilot`, `watch`, or `defer`?

### 5) `event-product-pack/v0`
Bundle for publication and reuse:
- lane brief
- escalation policy
- correlation budget
- selected event/schema/settings/observability/support artifacts
- readiness scorecard
- consumer summary

## Ranked first pilots

### 1) Single-broker product lane
**Why first**
- It is the cheapest lane that still proves the stack is real.
- It forces the archive to say what the supported channel/event/delivery boundary actually is.
- It avoids starting from fake universality.

**Good opening candidates**
- one `async-nats` / JetStream subject family;
- or one `rdkafka` topic family with a producer + consumer role pair.

**What must be explicit**
- supported channel and event ids
- envelope family
- delivery semantics and replay posture
- checked examples
- imported support/docs stance

**Success bar**
A project can publish a reviewable event-product boundary for one concrete lane without hiding behind broker-specific code.

### 2) Replay / DLQ / backfill lane
**Why second**
- Many event products fail exactly where the happy path ends.
- Replay, retention, poison-message handling, and idempotency are support claims, not afterthoughts.

**What must be explicit**
- replay/backfill trigger posture
- dead-letter / retry / poison-message rules
- consumer-position or durable-subscription assumptions
- idempotency or de-dup expectations
- evidence proving that the documented behavior still holds

**Success bar**
A project can export replay/recovery truth that operators and support teams can reuse.

### 3) Schema / registry / compatibility lane
**Why third**
- Payload evolution is a central product concern, but it should attach **after** the event boundary is real.
- This is where the stack proves it is not just AsyncAPI prose.

**What must be explicit**
- schema ids or registry-subject references
- compatibility posture
- additive vs breaking vs migration-gated changes
- envelope/schema relationship
- drift findings and attachments

**Success bar**
A project can diff event-payload evolution without erasing delivery or runtime truth.

### 4) Runtime / credential / observability lane
**Why fourth**
- Event products often depend on endpoints, topology roles, durable names, TLS roots, and credentials that are invisible in interface docs.
- Lag, retry, and correlation evidence are where event products become operable instead of theoretical.

**What must be explicit**
- endpoint/topology/profile selection
- credential and TLS-source posture
- local vs CI vs prod activation
- message correlation, lag, retry, or DLQ evidence
- redaction posture for imported runtime reports

**Success bar**
A project can attach activation truth and runtime evidence without leaking secrets or flattening environments.

### 5) Service / support / release / incident consumer lane
**Why fifth**
- This is where the stack becomes ecosystem infrastructure rather than a local crate tool.
- Event products become more useful when higher-level products can import them instead of recreating them.

**What must be explicit**
- which consumers import which event truths
- which facts are gating versus advisory
- freshness/expiry posture
- support/release attachment rules
- public vs internal consumer boundaries

**Success bar**
A downstream consumer can import event-product evidence without flattening it into one fake green check.

## Pilots to defer
These matter later, but are weaker opening bets:
- **one universal broker abstraction** — too likely to erase the real runtime differences;
- **one generated mega-schema for every message and every runtime detail** — too broad before narrow reviewable subsets stabilize;
- **policy-first admission or maturity scoring** — too brittle before the exported truth is stable;
- **full hosted ops dashboards** — too likely to hide the portable boundary.

## Immediate archive consequences
Read this file together with:
- `design/event-productization-stack.md`
- `design/event-surface-kit.md`
- `design/schema-contract-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
- `design/service-productization-stack.md`
- `design/protocol-productization-stack.md`

The archive should now prefer:
- **single-lane honesty before universality**,
- **replay and recovery truth before platform theater**,
- **runtime activation reports instead of setup folklore**,
- **support/docs truth instead of README optimism**,
- and **consumer imports** over prose-only event-readiness claims.

## What should wait
Do **not** start with:
- a hosted Rust event platform,
- a new schema registry,
- a one-size-fits-all broker facade,
- or a fake aggregate “messaging maturity” score.

Those may become overlays or consumers later.
They are not the missing substrate.
