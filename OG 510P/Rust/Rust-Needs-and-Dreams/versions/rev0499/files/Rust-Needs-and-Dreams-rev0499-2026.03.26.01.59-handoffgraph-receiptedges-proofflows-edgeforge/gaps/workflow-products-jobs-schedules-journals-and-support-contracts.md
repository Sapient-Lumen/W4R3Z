# Gap: workflow products still lack one portable boundary above trigger/schedule truth, retry and idempotency posture, runtime/engine identity, journal/history evidence, and shipped support claims

## What is missing
Rust now has credible ingredients for serious background jobs, scheduled tasks, resumable DAGs, and durable execution systems, but it still lacks a **boring end-to-end contract workflow** for products whose core promise is “this work will run correctly over time.”

Today teams can separately:
- declare jobs or workflows,
- choose queue / scheduler / workflow-engine backends,
- attach retries, backoff, uniqueness, checkpoints, and timers,
- expose dashboards, logs, traces, or web UIs,
- and document support claims around engines, deployment models, or upgrade posture.

What is still missing is the shared layer that answers:
- what jobs, workflow kinds, steps, signals, or schedules are actually part of the product,
- what execution guarantees are claimed versus merely inherited from an engine,
- what idempotency, deduplication, checkpoint, retry, timeout, and cancellation semantics are officially supported,
- what storage / journal / history / retention assumptions materially shape correctness,
- what worker/runtime/version lineage matters for long-lived executions,
- and what release, support, incident, or customer-facing consumers may later import without reverse-engineering worker code, queue tables, cron config, dashboards, and tribal memory.

## Why it matters
Workflow-like products fail in ways that ordinary API surfaces do not.

The hard questions are not only “did the request succeed?” but:
- whether a schedule really runs exactly once per period or only best-effort,
- whether a retry is safe because of true idempotency or merely lucky handler code,
- whether a durable workflow will resume from journaled steps or restart from the beginning,
- whether human/operator intervention is part of the supported story,
- whether queued work and persistent application data can be restored to one consistent point in time,
- and whether a new worker/runtime release is safe for long-lived executions already in flight.

Today those truths are usually scattered across queue tables, runtime config, worker logs, engine dashboards, docs pages, and release notes.

## Existing building blocks worth composing
- The 2024 State of Rust survey says Rust is especially popular for **server backends, web/networking services, and cloud technologies**, which is exactly where background work and durable execution stop being side features and become product behavior.
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- The 2025 State of Rust survey says online docs remain the canonical learning/reference surface. That raises the value of machine-readable workflow-product artifacts over README folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `apalis` already gives Rust a real background-work lane with distributed backends, concurrency controls, graceful shutdown, persisted cron jobs, and an optional Web UI.
  https://docs.rs/crate/apalis/latest
- `apalis-workflow` already treats durable/resumable workflows and DAG execution as first-class above the same worker/backend substrate.
  https://docs.rs/apalis-workflow/latest/apalis_workflow/
- `fang` already supports scheduled tasks, periodic cron tasks, unique tasks, async or threaded workers, and retries with custom backoff.
  https://docs.rs/fang/
- `sqlxmq` already makes a concrete durability argument: keeping jobs in PostgreSQL keeps jobs and application data in one transactional/backup story and supports retries, transactional completion, checkpointing, and future scheduling.
  https://docs.rs/sqlxmq/latest/sqlxmq/
- The Restate Rust SDK already gives Rust a durable-handler lane with Services, Virtual Objects, and Workflows; durable timers; durable promises/awakeables; infinite retries until terminal failure; and journal-backed service calls that eliminate manual retry logic.
  https://docs.rs/restate-sdk/latest/restate_sdk/
  https://docs.rs/restate-sdk/latest/restate_sdk/context/trait.ContextTimers.html
  https://docs.rs/restate-sdk/latest/restate_sdk/context/trait.ContextClient.html
- Restate’s architecture docs show why this category needs a product boundary at all: invocations, steps, state updates, timers, and promises all commit to a log first; retries resume from journaled state; duplicate calls with the same idempotency key resolve to the same invocation.
  https://docs.restate.dev/references/architecture
- Temporal’s published rationale for its Rust Core SDK is equally strong evidence that durable workflow machinery is a serious systems problem, not just another message queue helper. Temporal explicitly says workflow/activity workers are long-lived and must be extremely reliable, and its glossary says the Rust Core SDK centralizes complex state-machine logic for several language SDKs.
  https://temporal.io/blog/why-rust-powers-core-sdk
  https://docs.temporal.io/glossary
- External prior art is also getting clearer: DBOS now openly productizes durable execution with exactly-once event processing, scheduled jobs, durable workflows, reliable queues, and built-in observability. Even though DBOS does not currently target Rust, it sharpens the product boundary Rust still lacks.
  https://docs.dbos.dev/

## Why existing tools are not yet the whole answer
The ecosystem has **real workflow point tools**, but not the **shared product contract / diff / evidence layer**:
- `apalis` owns one queue/scheduler/worker lane.
- `apalis-workflow` owns one resumable DAG/workflow lane.
- `fang` owns one Postgres-backed scheduled/unique/retry lane.
- `sqlxmq` owns one transactional DB-backed queue lane.
- Restate owns one durable async/await runtime lane.
- Temporal shows one workflow-engine family where Rust is strategically important at the core.

Teams still have to invent their own answers for:
- stable workflow-product subject identity,
- portable workflow/job/schedule catalogs,
- explicit retry/idempotency/checkpoint/cancellation support posture,
- diffable engine/runtime/storage/retention assumptions,
- code-version / worker-version / release lineage for long-lived work,
- and downstream handoffs for support, release review, incident response, or adoption guidance.

## Target outcome
A project should be able to say:
- “this is the workflow product surface this crate/binary/service/release actually supports,”
- “these are the jobs, workflows, schedules, retries, and idempotency claims that define it,”
- “these are the runtime/engine/storage/retention assumptions that materially shape correctness,”
- “these are the journal/history/replay/lag/recovery artifacts that justify the claim,”
- and “this is the portable bundle release/support/incident tooling may consume later.”

That would be a worthy contribution because it would make Rust workflow products feel less like bespoke orchestration folklore and more like reviewable systems.
