# Epic proposal: Background Work Kit

## Thesis
Rust’s out-of-band execution ecosystem is mature enough that the missing contribution is no longer “yet another queue” or “yet another cron crate.”
The higher-leverage missing piece is a **portable background-work contract** that lets teams declare, diff, validate, and ship what their systems actually promise: job/workflow identities, trigger sources, schedules, execution backends, retry and idempotency posture, timeout/heartbeat rules, and checked execution evidence.

In other words: Rust needs a boring, attachable `work-pack/v0` more than it needs one more backend-specific worker abstraction.

## Why now
The ecosystem signals line up:
- `apalis` already spans distributed backends, worker middleware, graceful shutdown, and persisted cron jobs.
- `fang` already treats uniqueness, scheduling, cron, and retries as first-class concerns.
- `sqlxmq` shows DB-backed job state and application-data consistency are real design advantages, not edge cases.
- `tokio-cron-scheduler` shows scheduling and persistence are normal runtime requirements.
- `apalis-workflow` and Temporal show durable workflow/orchestration semantics are already adjacent to ordinary queue work.
- Temporal’s docs make deterministic replay and workflow versioning explicit, which is a strong signal that long-lived work surfaces need reviewable metadata, not just runtime code.
- ephemeral infrastructure for queues/brokers/datastores is increasingly practical through `testcontainers-modules`.

That means the missing substrate is not raw execution capability.
It is the **reviewable boundary above today’s pieces**.

Sources:
- https://docs.rs/crate/apalis/latest
- https://docs.rs/apalis-cron
- https://docs.rs/crate/apalis-workflow/latest
- https://docs.rs/fang/
- https://docs.rs/sqlxmq
- https://docs.rs/crate/tokio-cron-scheduler/latest
- https://docs.temporal.io/workflows
- https://docs.temporal.io/workflow-execution/event
- https://docs.temporal.io/develop/go/versioning
- https://temporal.io/blog/why-rust-powers-core-sdk
- https://github.com/temporalio/sdk-core
- https://docs.rs/testcontainers-modules

## What should be built
A first credible version should ship:
1. `work-surface/v0`, `job-catalog/v0`, `trigger-map/v0`, `execution-profile/v0`, `retry-idempotency-profile/v0`, optional `work-example-catalog/v0`, `work-check-plan/v0`, `work-check-report/v0`, optional `work-diff-report/v0`, and `work-pack/v0`
2. adapters for common Rust work-runtime lanes (`apalis`, `fang`, `sqlxmq`, cron schedulers, and durable workflow engines where possible)
3. docs/reference generation for supported jobs, triggers, schedules, backends, retry/idempotency semantics, and operator-visible lifecycle rules
4. validation/reporting support for schedule drift, uniqueness/idempotency regressions, timeout/heartbeat policy changes, and durable workflow rollout/versioning mismatches
5. release/CI examples showing work packs attached to web backends, workers, schedulers, and operator handoff

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one `apalis` service mixing queued jobs and persisted cron jobs with middleware + graceful-shutdown assumptions captured explicitly
- one `fang`-style Postgres worker with unique tasks and retry/backoff behavior modeled as support data rather than code comments
- one `sqlxmq` app where job/database transactional consistency is part of the declared work contract
- one `tokio-cron-scheduler` pilot proving schedule-only lanes can attach cleanly to the same artifact family
- one durable-workflow pilot proving replay/versioning expectations can live beside ordinary job semantics without flattening them

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve work ids, trigger ids, execution posture, and retry/idempotency truth
2. **v0.2 adapters**
   - support `apalis`, `fang`, `sqlxmq`, and one scheduler lane
   - support raw workflow-history/versioning attachments for durable-execution pilots
3. **v0.3 cross-kit integration**
   - integrate with Service Surface, Event Surface, Runtime Settings, Observability, Diagnostics, Migration, and Support Envelope workflows
   - support diff/baseline workflows across backend changes and rollout modes
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the schemas without sharing one runtime/backend stack

## Success metrics
- Teams can review background-work changes as explicit artifacts instead of reading worker registration code, cron strings, queue tables, and runbook prose.
- Supported jobs/workflows, triggers, and retry/idempotency assumptions remain documented from one declared source.
- Queue/scheduler/backend migrations become easier because support claims survive beyond one implementation.
- Long-lived workflow rollouts become easier to reason about because replay/versioning expectations are attached explicitly.
- Rust services become easier to hand off to operators, SREs, support teams, and future maintainers without bespoke archaeology.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Service Surface Kit covers request/response boundaries,
- Event Surface Kit covers messaging boundaries,
- Runtime Settings Kit covers config,
- Observability Kit covers telemetry,
- Diagnostic Surface Kit covers failure surfaces,
- and Replay/DST/Migration kits cover execution evidence and change programs.

But none of those is the portable contract for the **composed background-work boundary itself**.
Background Work Kit is the missing substrate that keeps jobs, triggers, schedules, execution posture, and retry/idempotency truth attached to one reviewable interface without absorbing them into one mega-runtime.
