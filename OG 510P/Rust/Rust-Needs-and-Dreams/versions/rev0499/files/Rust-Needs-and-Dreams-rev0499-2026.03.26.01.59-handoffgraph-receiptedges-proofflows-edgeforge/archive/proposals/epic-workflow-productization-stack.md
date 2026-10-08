# Epic proposal: Workflow Productization Stack (`cargo workflow-product`, `workflow-product-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **workflow products** that links **declared jobs/workflows/schedules**, **runtime/engine/storage activation**, **journal/history/retry/recovery evidence**, **long-lived release lineage**, and **support/docs truth** into one portable review boundary without pretending queues, schedulers, resumable DAGs, durable async/await runtimes, and workflow engines have already converged into one framework or one source of truth.

## Why this is now worth doing
Rust workflow reality is no longer just “some people have background jobs.”
It now spans multiple real product lanes:
- simple job workers,
- scheduled and cron-driven work,
- transactional DB-backed queues,
- resumable or DAG workflows,
- durable async/await runtimes,
- and engine-backed long-lived executions with timers, journals, retries, and replay.

That maturity changes the missing contribution.
The missing thing is **not** another queue crate, scheduler helper, workflow UI, or engine wrapper.
It is the attachable product boundary above them.

## The ecosystem evidence
The current ecosystem already shows the exact fragmentation pattern that calls for a shared product layer:
- `apalis` spans distributed backends, persisted cron jobs, graceful shutdown, and optional workflow-management UI.
- `apalis-workflow` already makes durable/resumable sequential and DAG workflows first-class.
- `fang` already makes scheduled tasks, periodic tasks, unique tasks, and custom retry/backoff policy part of the product surface.
- `sqlxmq` already treats transactional send/completion/checkpointing and DB-consistent backup/restore as the reason to use the lane.
- Restate Rust already treats durable handlers, workflows, durable timers, promises, and journal-backed service calls as normal application building blocks.
- Temporal makes the opposite kind of evidence visible: Rust is strategically important precisely because workflow runtimes require reliable, long-lived, state-machine-heavy core logic.
- DBOS shows that workflow products are becoming their own category, with exactly-once events, scheduled jobs, durable workflows, and built-in observability as product features.

That is exactly when Rust should add a **thin pack/report/import layer** instead of another winner-take-all pitch.

## What this epic should provide
A thin, portable workflow-product contract layer with:
- subject identity for the exact app/service/binary/release/deployment being reviewed,
- imported work-surface artifacts,
- imported runtime activation and retention/storage posture,
- selected journal/history/retry/recovery evidence,
- imported release-truth attachments for long-lived execution lineage,
- bounded support/docs/release/incident/agent/service handoffs,
- explicit diff and lossiness reporting between revisions or consumers,
- and no pretense that one engine schema or one queue runtime owns the whole category.

## This epic should not own
- a universal workflow DSL,
- a hosted workflow control plane,
- a universal scheduler or queue runtime,
- a fake one-number “automation reliability” badge,
- or a reimplementation of existing engines and runtimes.

## Candidate artifact family

### `workflow-product-brief/v0`
Why the product exists, intended consumer set, work kinds in scope, support levels, and review status.

### `workflow-product-subject/v0`
The exact service/app/workspace/release/deployment subject, imported work/runtime/release/support surfaces, comparison base, and environment/support scope.

### `workflow-product-pack/v0`
The portable review bundle linking:
- imported `work-pack/v0` attachments,
- imported runtime-setting reports,
- imported history/retry/recovery evidence,
- imported release-truth attachments,
- imported support/docs handoffs,
- local notes, waivers, caveats, and integrity metadata.

### `workflow-product-diff/v0`
What changed between two review points, with separate sections for:
- jobs/workflows/schedules/triggers,
- retry/idempotency/checkpoint/cancellation semantics,
- backend/runtime/storage/retention posture,
- history/journal/replay behavior,
- worker/runtime/source lineage,
- docs/support/release claims.

### `workflow-product-handoff/v0`
Bounded consumer summaries for:
- service owners,
- support / incident review,
- release review,
- atlas / adoption review,
- agent consumers,
- assistant/editor rendering.

## Recommended rollout
1. queue/schedule product lane
2. transactional DB-backed lane
3. resumable DAG/workflow lane
4. durable-engine lane
5. release/support/incident handoff lane

This should be driven by [`design/workflow-productization-pilot-program.md`](../design/workflow-productization-pilot-program.md).

## What makes this epic “epic” rather than incremental
A merely incremental tool would improve one lane:
- a nicer `apalis` wrapper,
- a nicer cron/scheduler helper,
- a nicer `sqlxmq` dashboard,
- a nicer Restate/Temporal/DBOS adapter,
- or a nicer workflow UI.

An epic contribution here instead gives Rust one **portable workflow-product contract** above those lanes.
That is strategically different because it can:
- make service/support/release/incident/agent reviews share the same workflow subject and evidence boundary;
- let queue, schedule, DAG, and durable-engine workflows stay specialized without pretending any one defines the whole product;
- keep declared work truth, activation truth, history truth, release lineage, and support claims distinct but linked;
- and give downstream tooling a bounded artifact to import instead of re-scraping queue tables, dashboards, runtime config, and README prose.

## Design principles
- **Declared work truth is not runtime activation truth.**
- **Runtime activation truth is not history/recovery evidence.**
- **History/recovery evidence is not release lineage truth.**
- **Release lineage is not support/docs truth.**
- **Consumer summaries are intentionally lossy and say so.**
- **The stack stays thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact workflow product subject,”
- “these are the jobs, workflows, schedules, and semantics we actually support,”
- “these are the runtime/storage/retention assumptions behind that support,”
- “these are the evidence artifacts we have for retries, journaling, recovery, and replay,”
- “this is the worker/runtime/source lineage that matters for long-lived executions,”
- “this is what changed from the prior review,”
- and “this is what service/support/release/incident/agent consumers may safely conclude,”

without inventing a bespoke workflow-readiness schema for every repository.

## Read this with
- `gaps/workflow-products-jobs-schedules-journals-and-support-contracts.md`
- `design/workflow-productization-stack.md`
- `design/workflow-productization-pilot-program.md`
- `design/background-work-kit.md`
- `design/runtime-settings-kit.md`
- `design/observability-kit.md`
- `design/release-truth-stack.md`
- `design/support-envelope-kit.md`
