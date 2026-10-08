# Epic proposal: Event Productization Stack

## Problem
Rust projects increasingly have real event interfaces, replay stories, schema contracts, broker runtime settings, and incident dashboards, but they still lack one honest way to review event-driven behavior as a **supported product surface**.

Today, maintainers, operators, support teams, and downstream tools often reconstruct that truth from:
- broker client code;
- AsyncAPI fragments;
- CloudEvents helpers;
- registry subjects;
- consumer-group, retry, and DLQ lore;
- env-var and secret setup;
- and dashboard/runbook folklore.

That is enough to demo eventing.
It is not enough to ship or support it.

## Proposal
Build a thin composition layer above existing archive pieces:
- **Event Surface Kit**
- **Schema Contract Kit**
- **Runtime Settings Kit**
- **Observability Kit**
- **Support Envelope + DocProof**
- optional imports into **Service Productization**, **Protocol Productization**, **Release Truth**, **Incident**, and other domain stacks

The result should be an **Event Productization Stack** that can describe:
- what broker and channel/event lanes are part of the product;
- what payload and envelope contracts are promised;
- how replay, DLQ, backfill, idempotency, and retention are supported;
- what runtime/topology/credential settings activate that promise;
- what observability/replay evidence exists;
- and what support/release/incident consumers may conclude.

## Candidate artifact family
- `event-envelope/v0`
- `event-activation-report/v0`
- `event-replay-report/v0`
- `event-product-diff/v0`
- `event-product-pack/v0`

These should remain **thin linked artifacts**, not a new mega-schema.

## Reference CLI shape
- `cargo event product export`
  - emit `event-envelope/v0` for one selected subject/profile
- `cargo event product activate`
  - emit `event-activation-report/v0` from imported settings/runtime evidence
- `cargo event product replay`
  - emit `event-replay-report/v0`
- `cargo event product diff --against <ref|version|profile>`
  - emit `event-product-diff/v0`
- `cargo event product pack`
  - produce `event-product-pack/v0`
- `cargo event product verify-pack <path>`
  - verify schema versions, checksums, redaction rules, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace the lower-layer kits.

## What `event-product-pack/v0` should contain
- `manifest.json`
- `event-envelope.json`
- `event-activation-report.json`
- optional `event-replay-report.json`
- optional `event-product-diff.json`
- imported `event-pack` pointer or embedded attachment
- imported schema attachments or `schema-pack` pointers
- imported runtime-settings reports
- imported observability/replay attachments
- imported support/docs attachments
- checksums, provenance, and generator identity
- optional service/release/incident import pointers

## Design principles
- **Event-driven behavior is a product surface, not just broker plumbing.**
- **Thin imports over new truth engines.**
- **Event truth, schema truth, activation truth, replay truth, and support truth remain distinct.**
- **Single-lane honesty before universality.**
- **Replay and recovery claims need evidence, not just prose.**
- **Downstream consumers import the stack; they do not redefine it.**

## Early implementation order
1. single-broker event lane
2. replay / DLQ / backfill lane
3. schema / registry / compatibility lane
4. runtime / credential / observability lane
5. service / support / release / incident consumer imports

## Non-goals
- a hosted broker or event platform;
- a universal queue abstraction;
- replacing AsyncAPI, CloudEvents, or schema registries;
- a fake event-product health score;
- making release or policy decisions inside the pack itself.

## Success bar
This becomes worthy when a maintainer, operator, or downstream tool can answer:
- what broker/channel/event surface this subject supports;
- what payload/envelope/delivery/replay semantics are actually promised;
- what runtime/topology/credential activation belongs to that promise;
- what observability and replay evidence backs it;
- what docs/setup/support claims were checked;
- and what changed between versions or profiles as an event product,

without scraping dashboards, broker configs, and repo folklore.

## Read this with
- `gaps/event-products-brokers-delivery-replay-and-support-contracts.md`
- `design/event-productization-stack.md`
- `design/event-productization-pilot-program.md`
- `design/event-surface-kit.md`
- `design/schema-contract-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/support-envelope-kit.md`
