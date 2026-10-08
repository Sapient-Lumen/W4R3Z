# Design: Background Work Kit (`cargo workcheck`, `work-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing a Rust program’s supported out-of-band work surface: jobs, schedules, durable workflows, triggers, backend/execution posture, retry/idempotency semantics, checked scenarios, and evidence that the declared work surface still matches the program.

This should **not** replace `apalis`, `fang`, `sqlxmq`, `tokio-cron-scheduler`, Temporal, broker products, or job dashboards.
It should make them compose better and make support claims reviewable.

## References (signals)
- `apalis` already provides tower-powered background job handling with distributed backends, concurrency controls, worker monitoring, graceful shutdown, and persisted cron jobs.
  https://docs.rs/crate/apalis/latest
- `apalis-cron` shows cron scheduling is already a normal extension lane above the same worker/middleware model.
  https://docs.rs/apalis-cron
- `apalis-workflow` already describes extensible, durable, resumable workflows with distributed execution and `apalis` integration.
  https://docs.rs/crate/apalis-workflow/latest
- `fang` already supports scheduled tasks, periodic cron tasks, unique tasks, async or threaded workers, and retries with custom backoff.
  https://docs.rs/fang/
- `sqlxmq` explicitly motivates DB-backed jobs by pointing out that application data and in-flight jobs often need one consistent transactional/backup story.
  https://docs.rs/sqlxmq
- `tokio-cron-scheduler` covers cron-like, repeated, and instant jobs and can persist task data via PostgreSQL or NATS.
  https://docs.rs/crate/tokio-cron-scheduler/latest
- Temporal docs describe workflows as resilient, event-history-backed executions that survive crashes and rely on deterministic replay.
  https://docs.temporal.io/workflows
  https://docs.temporal.io/workflow-execution/event
- Temporal’s versioning docs are direct evidence that long-lived workflows need explicit rollout/versioning metadata, not just “deploy the new worker.”
  https://docs.temporal.io/develop/go/versioning
- Temporal’s shared Rust Core SDK is evidence that Rust already sits at the heart of serious durable-execution machinery.
  https://temporal.io/blog/why-rust-powers-core-sdk
  https://github.com/temporalio/sdk-core
- `testcontainers-modules` provides practical ephemeral Postgres/Redis/NATS/Kafka/RabbitMQ-style integration environments.
  https://docs.rs/testcontainers-modules

## Core components

### 1) `work-surface/v0`
A design-time declaration of the supported out-of-band work boundary for a binary/service/workspace.

Required ideas:
- system/service identity
- work kinds in scope:
  - queued background jobs
  - scheduled one-shot jobs
  - periodic/cron jobs
  - durable workflows / orchestrations
  - activities / child tasks / sub-jobs
- support classes:
  - official
  - best-effort
  - experimental
  - deprecated
  - internal
- linked attachments:
  - runtime settings
  - event/service surfaces
  - schema attachments
  - observability/diagnostic ids
  - support-envelope assumptions

Design rule: preserve simple queued jobs and durable workflows as related but distinct lanes. Do not flatten them into one fake universal task concept.

### 2) `job-catalog/v0`
Stable identities for jobs and workflows.

Each entry should support:
- stable work id
- human-facing name + summary
- kind:
  - queue job
  - cron job
  - delayed job
  - durable workflow
  - workflow activity / child task
- ownership / upstream trigger notes
- support level
- linked input/output schema refs when relevant
- linked execution profile id
- linked retry/idempotency profile id
- linked example/check ids
- optional deprecation / replacement pointers

Design rule: keep identity stable across backend moves when possible. A job switching from Redis to Postgres or to a workflow engine should not automatically look like a brand-new feature unless the supported behavior changed.

### 3) `trigger-map/v0`
How work begins.

Each trigger entry should capture:
- stable trigger id
- trigger family:
  - manual/operator initiated
  - API/request initiated
  - event/message initiated
  - schedule/cron initiated
  - dependency completion / fan-out initiated
  - recovery/replay initiated
- source surface reference:
  - route id
  - event/channel id
  - schedule spec
  - workflow signal/query/update lane when relevant
- dedup / uniqueness / admission rules
- payload/input references
- linked work ids

Design rule: keep trigger identity separate from job identity and separate from backend execution semantics. One job may have multiple triggers; one trigger may fan out to multiple job ids.

### 4) `execution-profile/v0`
Where and how work runs.

Possible fields:
- backend/runtime family:
  - in-process scheduler
  - DB-backed queue
  - Redis-backed queue
  - AMQP / NATS / broker-backed queue
  - durable workflow engine
- worker model:
  - async tasks
  - threads
  - process pool / distributed workers
- concurrency posture:
  - singleton
  - bounded parallel
  - partitioned by key
  - workflow-engine controlled
- lease/claim semantics
- timeout families:
  - enqueue delay / schedule delay
  - start deadline
  - execution timeout
  - heartbeat timeout
  - workflow run timeout
- persistence posture:
  - memory only
  - backend persisted
  - event-history-backed durable state
- rollout/versioning notes where long-lived workflows require them
- unsupported / best-effort notes

Design rule: do not let “runs on workers” hide crucial differences between ephemeral queue jobs and replay-based durable workflows.

### 5) `retry-idempotency-profile/v0`
The correctness semantics people actually need to trust.

Possible fields:
- retry policy:
  - none
  - bounded attempts
  - unbounded until success
  - cron reschedule semantics
- backoff policy reference
- uniqueness posture:
  - none
  - dedup by job key
  - queue-native unique constraint
  - workflow-instance identity
- idempotency expectation:
  - not safe to retry
  - safe with idempotency key
  - safe by transactional design
  - workflow-engine replay-safe only
- compensation / saga notes
- poison-job / DLQ / terminal-failure handling
- cancellation semantics
- manual operator intervention expectations

Design rule: keep retry policy, uniqueness, and idempotency as first-class support truth. They are not mere implementation details.

### 6) `work-example-catalog/v0`
Small canonical examples and checked scenarios.

Possible contents:
- example enqueue payloads
- example trigger events or API requests
- example cron/schedule specs
- example workflow histories or summaries
- example idempotency-key / uniqueness cases
- example cancellation / timeout cases
- provenance labels:
  - illustrative only
  - generated
  - checked in CI
  - captured from fixture replay

Design rule: keep examples bounded and scrubbed. Do not dump production queue state or giant workflow histories.

### 7) `work-check-plan/v0`
A concrete plan for what is checked.

Required ideas:
- work ids selected
- trigger families exercised
- execution backends exercised
- retry/timeout/heartbeat/cancellation checks performed
- uniqueness/idempotency checks performed
- schedule/cron validation steps
- durable replay/versioning checks when relevant
- local/ephemeral infrastructure used
- unsupported or intentionally omitted lanes

This is where the kit stops pretending “we have a queue and a worker” means “the background-work surface is reviewed.”

### 8) `work-check-report/v0`
Evidence from tests, comparisons, and runtime checks.

Possible contents:
- coverage summary by job/workflow id
- trigger wiring mismatches
- schedule parse/drift findings
- retry/backoff/idempotency findings
- timeout/heartbeat/cancellation findings
- replay/versioning findings for durable workflows
- backend/worker environment notes
- raw attachments:
  - queue table snapshots
  - scheduler exports
  - workflow histories
  - test transcripts
  - fixture logs
  - captured metrics/traces

### 9) `work-diff-report/v0` (optional)
For compatibility-sensitive changes:
- work id added/removed/renamed
- trigger changed
- schedule/cadence changed
- backend/runtime family changed
- retry/timeout/heartbeat policy changed
- uniqueness/idempotency posture changed
- support level changed
- required operator action or migration notes

Should distinguish:
- additive changes
- behavior-breaking changes
- backend-only implementation changes
- documentation-only drift
- manual rollout/versioning coordination required

### 10) `work-pack/v0`
Bundle format containing:
- `work-surface/v0`
- `job-catalog/v0`
- `trigger-map/v0`
- one or more `execution-profile/v0`
- one or more `retry-idempotency-profile/v0`
- optional `work-example-catalog/v0`
- one or more `work-check-report/v0`
- optional `work-diff-report/v0`
- optional raw attachments: schedule specs, queue/backend metadata, workflow histories, check transcripts, and fixture configuration

This is the unit that should travel through CI, release review, ops handoff, and later archaeology.

### 11) `cargo workcheck`
Reference UX:
- `cargo workcheck init`
- `cargo workcheck jobs`
- `cargo workcheck triggers`
- `cargo workcheck schedules`
- `cargo workcheck retries`
- `cargo workcheck diff`
- `cargo workcheck pack`

`cargo workcheck` should begin as an explainer / adapter / packer.
It should not pretend to be the one true queue, scheduler, or workflow engine.

## Default policy
- **Separate work identity, trigger identity, execution semantics, and retry/idempotency semantics.**
- **Preserve queued jobs, scheduled jobs, and durable workflows as related but distinct lanes.**
- **Treat retries, uniqueness, idempotency, timeouts, heartbeats, and cancellation semantics as support surfaces.**
- **Keep checked scenarios distinct from illustrative examples.**
- **Prefer adapters over replacement runtimes** in v0.

## What the kit should provide to others
- **Service Surface Kit:** link API routes or webhook handlers to job triggers without absorbing route behavior itself.
- **Event Surface Kit:** link event-driven triggers and downstream jobs without flattening asynchronous messaging into background-work semantics.
- **Runtime Settings Kit:** reference queue URLs, cron settings, feature flags, and worker concurrency knobs without owning config itself.
- **Observability Kit:** attach metrics/traces/log ids for queue depth, retries, heartbeats, and workflow progress without making telemetry the primary contract.
- **Diagnostic Surface Kit:** attach stable failure/timeout/cancellation codes without making failure rendering the whole job contract.
- **Migration Kit:** describe rollout/versioning requirements for long-lived workflows and backend moves.
- **Support Envelope Kit:** record backend/runtime/platform assumptions that matter for workers and schedulers.

## Overlap boundaries
- **Not Event Surface Kit:** that kit is about channels, message identities, and delivery semantics. This kit begins where an event has already become a declared unit of work.
- **Not Service Surface Kit:** that kit is about request/response service boundaries. This kit is about work that continues beyond the initiating request.
- **Not Migration Kit:** migration tracks source→destination change programs broadly; this kit records the supported work surface that migrations may change.
- **Not Replay Kit / DST Kit:** those are failure-finding and reproduction kits. This kit is about the declared supported work boundary itself.
- **Not a hosted orchestrator:** the value is the portable artifact and review workflow, not another control plane.
