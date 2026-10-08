# Pilot program: Workflow Productization Stack

## Purpose
Run a **ranked, bounded pilot program** for workflow products so the archive can test whether a thin `workflow-product-pack/v0` layer is genuinely useful above Rust job queues, schedulers, DAG/workflow engines, durable runtimes, release lineage, and support/docs truth.

This pilot should prove that the stack can export reviewable artifacts without flattening:
- queued jobs into durable workflows,
- schedule semantics into retry semantics,
- runtime activation into release lineage,
- or runtime dashboard evidence into supported product truth.

## The stack under test
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/workflow-productization-stack.md`](./workflow-productization-stack.md)

## Ranked rollout

### 1) Single-backend queue lane
Use one narrow lane where the workflow product story is mostly jobs + retries + schedules:
- likely subjects: `apalis`, `fang`, or a similar concrete queue/scheduler product
- export:
  - `work-pack/v0`
  - runtime-setting report for backend/storage activation
  - support/docs notes for supported worker/runtime modes
- prove:
  - stable job ids
  - schedule truth
  - retry/idempotency truth
  - bounded support claims

Success bar: reviewers can tell **what work exists**, **how it is triggered/scheduled**, and **what retry/uniqueness semantics are claimed** without reading worker code.

### 2) Transactional DB-backed lane
Use a queue lane where persistence and correctness are part of the main value proposition:
- likely subject: `sqlxmq`
- export:
  - work-surface/job catalog
  - runtime-setting report for DB/retention/connection assumptions
  - history/evidence report for retries/checkpoints/completions
  - release/support notes for deployment and upgrade posture
- prove:
  - DB-backed queue truth is not just backend choice; it changes backup/restore and exactly-once posture
  - checkpoint/retry semantics can be separated from ordinary queue success/failure logs

Success bar: reviewers can tell **why this lane is different from a generic queue**, and what is truly promised versus merely convenient.

### 3) Resumable DAG/workflow lane
Use a lane where workflow shape matters beyond “job plus retry”:
- likely subject: `apalis-workflow`
- export:
  - work catalog with sequential/DAG workflow identities
  - runtime-setting report for backend choice
  - history/evidence report for resumability and step execution
  - bounded consumer handoff for support/docs
- prove:
  - workflow graph/step truth can be published without pretending every engine has the same semantics
  - distributed or resumable execution claims can be attached to real evidence

Success bar: reviewers can tell **workflow shape**, **resume posture**, and **backend dependence** apart.

### 4) Durable engine lane
Use a lane where journal/history/timers/promise semantics are first-class:
- likely subject: Restate Rust SDK
- comparative import: Temporal Rust Core / DBOS as outside-in evidence only
- export:
  - workflow subject + runtime-setting report
  - history/retry/recovery report
  - release-truth attachment for long-lived execution lineage
  - support/docs note for durable-engine-specific caveats
- prove:
  - durable timers, promises, journal replay, and idempotency are not hidden implementation details
  - long-lived workflow upgrades need release lineage, not just runtime logs

Success bar: reviewers can tell **declared workflow surface**, **engine activation**, **history/recovery evidence**, and **code/runtime lineage** apart.

### 5) Release/support/incident consumer lane
Use one downstream consumer-focused lane:
- support review,
- incident/runbook intake,
- release/upgrade review,
- or atlas/adoption guidance.

Export:
- `workflow-product-pack/v0`
- one lossy consumer summary with explicit lossiness notes

Success bar: a downstream consumer can answer:
- what work is supported,
- what runtime/backing assumptions materially affect correctness,
- what evidence justifies durability/retry claims,
- what release lineage matters for in-flight work,
- and what remains partial/experimental/unsupported.

## What to measure
Across the rollout, track whether the stack can keep distinct:
- work identity vs trigger identity,
- queue/schedule truth vs durable-workflow truth,
- activation truth vs release lineage,
- runtime evidence vs support claims,
- and imported consumer summaries vs canonical workflow-product artifacts.

## Failure conditions
The pilot is failing if it turns into any of the following:
- another queue/worflow-engine framework comparison table,
- a dashboard export without declared workflow truth,
- a release artifact that ignores in-flight workflow/version lineage,
- a support matrix that hides retry/idempotency/storage assumptions,
- or a mega-schema that erases real differences between queue, DAG, and durable-engine lanes.

## Expected deliverables
If the pilot works, the archive should leave behind:
- one explicit `workflow-product-pack/v0` candidate shape,
- one bounded `workflow-product-diff/v0` story,
- one consumer handoff profile,
- and stronger ranking evidence for when workflow productization deserves promotion over adjacent service/event/agent lanes.
