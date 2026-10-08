# Gap: background jobs, schedules, and durable-work contracts

## What is missing
Rust now has credible building blocks for queued jobs, cron-like scheduling, database-backed background work, and even durable workflow execution, but it still lacks a **boring, end-to-end contract workflow** for out-of-band work.

Today teams can separately:
- enqueue work into Redis/Postgres/AMQP-style backends,
- schedule one-shot or cron-like jobs,
- run workers with retries and middleware,
- model uniqueness/idempotency in backend-specific ways,
- and, at the far end, use durable workflow systems that replay state from event history.

What is still missing is the shared layer that answers:
- what jobs/workflows a program officially exposes,
- how each one is triggered,
- what execution backend and concurrency model it assumes,
- what retries, uniqueness, timeouts, and idempotency guarantees are actually promised,
- and what evidence exists that those claims still hold.

## Why it matters
This is not just a “background queue crate” problem.

Out-of-band work is increasingly a **public support surface**:
- API servers hand real work to queues and schedulers,
- SaaS products depend on recurring and delayed jobs,
- multi-step business processes need durable orchestration,
- and operators need to know which jobs are safe to retry, replay, or compensate.

Without a shared artifact layer, those truths get scattered across:
- worker registration code,
- cron expressions,
- queue schema tables,
- workflow-engine-specific metadata,
- dashboard screenshots,
- and oral tradition about which jobs are “safe” to rerun.

That is exactly the kind of ecosystem seam this archive should care about: strong point tools, weak shared artifacts.

## Existing building blocks worth composing
- `apalis` is already a serious Rust background-job library with tower middleware, distributed backends, concurrency controls, worker monitoring, graceful shutdown, and persisted cron jobs.
  https://docs.rs/crate/apalis/latest
- `apalis-cron` shows cron scheduling is already an adapter lane inside that ecosystem rather than a toy side feature.
  https://docs.rs/apalis-cron
- `apalis-workflow` already experiments with extensible, durable, resumable workflows integrated with `apalis` workers/backends, which is strong evidence that “jobs vs workflows” is already a live Rust design seam.
  https://docs.rs/crate/apalis-workflow/latest
- `fang` already exposes async/threaded workers, scheduled tasks, periodic cron tasks, unique tasks, and retries with custom backoff.
  https://docs.rs/fang/
- `sqlxmq` explicitly argues that database-backed jobs matter because in-flight job state should stay consistent with normal application data and backups.
  https://docs.rs/sqlxmq
- `tokio-cron-scheduler` covers cron-like, one-shot, and repeated jobs and can persist task data using PostgreSQL or NATS.
  https://docs.rs/crate/tokio-cron-scheduler/latest
- Temporal’s workflow docs explicitly frame workflows as resilient, event-history-backed executions that can continue after crashes, while also requiring deterministic replay.
  https://docs.temporal.io/workflows
  https://docs.temporal.io/workflow-execution/event
- Temporal’s versioning docs are a useful adjacent signal: long-lived workflows need explicit rollout/versioning discipline because replay safety matters.
  https://docs.temporal.io/develop/go/versioning
- Temporal’s Rust Core SDK history is also a signal that Rust is already trusted for the hard concurrency/state-machine core of durable workflow systems.
  https://temporal.io/blog/why-rust-powers-core-sdk
  https://github.com/temporalio/sdk-core
- `testcontainers-modules` already makes Kafka/NATS/Postgres/Redis/RabbitMQ-style ephemeral integration environments practical in Rust tests, which means checked background-work evidence is increasingly feasible.
  https://docs.rs/testcontainers-modules

## Why existing tools are not yet the whole answer
The ecosystem has **queue-specific, scheduler-specific, and engine-specific tools**, but not the **shared contract / capability / evidence layer**:
- `apalis` and `fang` help run jobs,
- `sqlxmq` and database-backed queues help keep job state near data,
- schedulers help with time-based triggers,
- durable workflow systems help with long-lived orchestration,
- and test infrastructure helps validate some paths.

But teams still have to invent their own answers for:
- stable job/workflow identities,
- normalized trigger declarations,
- retry/lease/timeout/idempotency truth,
- explicit distinctions between illustrative and checked runs,
- and diffable review artifacts when a job is renamed, made unique, gains retries, changes cadence, or switches backend assumptions.

This is the same pattern seen elsewhere in the archive: strong execution engines, weak portable artifacts.

## Target outcome
A project should be able to say:
- “these are the background jobs and durable workflows we officially support,”
- “these are their triggers and execution backends,”
- “these are the retry, timeout, uniqueness, heartbeat, and idempotency rules that define them,”
- “these are the schedules and rollout/versioning assumptions that matter,”
- and “this is the portable bundle CI, release review, operators, and later archaeology can consume.”

That is bigger than a queue helper crate and smaller than a hosted orchestration platform.
