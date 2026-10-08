# Design note: Workflow Productization Stack (Background Work + Runtime Settings + Observability + Release Truth + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust jobs/workflows/schedules, runtime activation, history/retry/recovery evidence, long-lived release lineage, and support claims so the ecosystem can make **workflow products** reviewable without anointing one queue, one durable-execution engine, one scheduler, or one hosted control plane as the answer.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose:
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/service-surface-kit.md`](./service-surface-kit.md)
- [`design/event-surface-kit.md`](./event-surface-kit.md)
- [`design/identity-surface-kit.md`](./identity-surface-kit.md)
- [`design/agent-productization-stack.md`](./agent-productization-stack.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “background jobs are possible.” They are saying the ecosystem already spans several real workflow lanes, but still lacks a **portable productization layer** above them:
- Rust is increasingly used for server backends, web/networking services, and cloud technologies, so queues and workflows increasingly define product behavior rather than merely implementation details.
- The 2025 State of Rust survey still says online docs are the canonical reference surface, which means supportable workflow truth cannot live only in dashboards, worker code, and ops memory.
- `apalis` already spans distributed backends, persisted cron jobs, graceful shutdown, and optional workflow-management UI.
- `apalis-workflow` already promotes durable/resumable sequential and DAG workflows above the same substrate.
- `fang` and `sqlxmq` both make durability, scheduling, retries, uniqueness, checkpointing, and storage choices explicit enough that users can feel the difference between “task queue” lanes.
- The Restate Rust SDK already exposes durable handlers, workflows, timers, durable promises, and journal-backed retries.
- Temporal’s Rust Core SDK is strong outside-in evidence that workflow machinery has enough state-machine complexity that product boundaries matter.
- DBOS strengthens the same point from outside Rust by explicitly productizing exactly-once event processing, scheduled jobs, and durable workflows.

Together these signals justify treating workflow productization as a **frontier-worthy ecosystem seam** rather than leaving Rust durable work split across queue crates, scheduler config, workflow runtimes, dashboards, and release notes.

## Stack layers

### 1) Background Work: declared job/workflow/schedule truth
Background Work owns the **declared work surface**:
- job/workflow identities
- trigger maps
- schedule and delayed-execution posture
- retry/idempotency/checkpoint/cancellation semantics
- queue versus durable-workflow versus DAG distinctions
- checked execution examples and reports

Background Work answers questions like:
- “What jobs or workflows are actually part of the product?”
- “Which triggers, schedules, retries, or uniqueness rules are promised?”
- “Is this a queue lane, a DAG lane, or a durable journal/replay lane?”

Design rule: **workflow products must not derive their public contract from worker code, queue tables, or one engine dashboard after the fact.**

### 2) Runtime Settings: engine/store/retention activation truth
Runtime Settings owns the **activation boundary**:
- selected queue/DB/workflow-engine runtime family
- broker/database/storage endpoints
- retention windows, schedule stores, journal/history backends
- environment/profile/credential activation
- effective-setting capture and precedence
- degraded/offline/local profiles when relevant

Runtime Settings answers questions like:
- “What runtime/backend choices make the declared workflow surface real?”
- “Which retention or storage settings materially affect recovery or replay?”
- “Which env vars, secrets, or profile switches change semantics?”

Design rule: **workflow-product claims must not silently depend on undocumented engine configuration, retention defaults, or one operator shell session.**

### 3) Observability: journal/history/retry/recovery evidence
Observability owns the **runtime evidence layer**:
- execution/journal/history identifiers
- schedule / lag / retry / timeout / dead-letter findings
- replay / recovery / resume artifacts
- correlation between workflow subject and runtime events
- runtime reports portable enough for incident/support review

Observability answers questions like:
- “Can the project prove a workflow resumed from durable state rather than just happened to succeed again?”
- “Which workflow IDs, run IDs, journal IDs, or attempt IDs exist for support?”
- “What runtime evidence is portable enough to outlive one dashboard?”

Design rule: **workflow history and recovery truth must not stay trapped in one vendor UI or ephemeral logs.**

### 4) Release Truth: long-lived execution lineage
Release Truth owns the **version and provenance boundary** for long-lived work:
- which binary/image/source package and code revision ran a workflow subject
- worker/runtime/build lineage across upgrades
- rollout/versioning notes for long-lived workflows
- release/import evidence that matters for in-flight executions
- diffable lineage reports between releases

Release Truth answers questions like:
- “What exactly changed between the worker/runtime that started this workflow and the one now resuming it?”
- “Is a new release safe for in-flight schedules or durable executions?”
- “Which provenance facts can support/debug/incident consumers import later?”

Design rule: **workflow products must not treat long-lived execution upgrades as ordinary stateless deploy folklore.**

### 5) Support Envelope + DocProof: supported workflow-product truth
Support Envelope and DocProof together own the **support/docs boundary**:
- support levels per backend/runtime/deployment lane
- checked setup docs, examples, and runbooks
- supported upgrade/migration and operator-intervention posture
- platform/runtime caveats
- explicit unsupported or best-effort lanes

This layer answers questions like:
- “Is this queue/workflow engine support real, experimental, or local-only?”
- “Are replay/recovery/manual intervention part of the promise or just operator folklore?”
- “Which docs and examples are canonical enough for downstream users?”

Design rule: **a working demo or dashboard is not a support contract.**

### 6) Importing consumers
The stack matters when other systems can import it honestly:
- **Service Productization** can attach workflow products instead of flattening all background work into route handlers.
- **Agent Productization** can attach durable task/workflow runtime truth without redefining it as prompt or tool behavior.
- **Event Productization** can distinguish durable workflow semantics from message delivery semantics.
- **Identity Productization** can import subject/auth/operator-intervention truth without owning workflow execution semantics.
- **Release / Incident / Support / Atlas** consumers can reason about durable work without scraping queue tables and dashboards.

Design rule: **consumers import selected workflow-product facts; they do not redefine them into one fake “automation maturity” score.**

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust workflow engine.”
It is a portable boring stack with clear boundaries:

1. **job/workflow/schedule truth first**
   - prove stable work-surface artifacts can name the product boundary;
2. **engine/store/retention activation truth second**
   - prove backend/runtime choices can attach honestly without hiding semantics in env vars;
3. **journal/history/retry/recovery truth third**
   - prove runtime evidence can travel outside one dashboard;
4. **release lineage truth fourth**
   - prove in-flight workflows can be related to concrete worker/runtime/source revisions;
5. **support/docs and consumer imports fifth**
   - prove service/agent/release/support consumers can reuse the same facts.

An eventual aggregate artifact may exist, but it should be a **thin linked pack of imported artifacts**, not a mega-schema that erases declared work truth, activation truth, runtime evidence, release lineage, and support truth.

## Proposed aggregate artifact family
A plausible aggregate lane is:
- `workflow-product-brief/v0`
  - workflow subject identity, supported work kinds, selected backend/runtime family, imported artifact pointers, and review status;
- `workflow-runtime-report/v0`
  - effective engine/storage/retention/activation posture with redaction-aware capture;
- `workflow-history-report/v0`
  - replay/retry/recovery/schedule/lag/manual-intervention findings and their checked evidence;
- `workflow-product-diff/v0`
  - drift between two versions or profiles;
- `workflow-product-pack/v0`
  - thin bundle linking:
    - `work-pack/v0`
    - runtime-setting reports
    - observability/history reports
    - release-truth attachments
    - support/docs attachments
    - optional service/agent/event/identity import pointers

The point is not one new truth engine.
The point is a **reviewable workflow-product handoff**.

## Ranked first execution lanes
1. **single-backend queue lane**
   - best first exporter because it proves stable job/schedule/retry truth without requiring a universal durable-engine model;
2. **transactional DB-backed lane**
   - proves storage/backup/idempotency/checkpoint truth can be attached honestly;
3. **DAG/resumable workflow lane**
   - proves workflow shape and step-level evidence can travel portably;
4. **durable-engine lane**
   - proves journal/history/timer/promise/replay semantics can be exported without collapsing engine specifics;
5. **release/support/incident lane**
   - proves the stack matters outside demos by attaching long-lived execution truth to support, release, and incident consumers.

## Non-goals
- one universal workflow runtime;
- a hosted orchestration control plane;
- flattening queues, cron schedulers, DAG engines, and durable journal/replay systems into one runtime model;
- another queue client wrapper or cron parser;
- another “workflow UI” without portable artifacts;
- flattening declared work truth, runtime activation, history evidence, release lineage, and support truth into one fake badge.

## Archive implications
- The archive should now treat **Background Work + Runtime Settings + Observability + Release Truth + Support Envelope** as a coupled **Workflow Productization Stack** in frontier and priority discussions, with Service / Agent / Event / Identity as importing consumers.
- Future revisions should prefer **declared workflow truth, activation truth, history/retry/recovery truth, release lineage truth, support/docs truth, and consumer imports** over another queue bake-off, cron helper, workflow dashboard, or “workflow framework” winner pitch.
- When Service, Agent, Event, Identity, Release, Support, or Atlas work cites durable execution readiness, they should import **workflow-product truth**, **activation truth**, **history truth**, **release lineage truth**, and **support truth** separately.

## References (signals)
- Rust surveys:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust workflow/background-work lanes:
  https://docs.rs/crate/apalis/latest
  https://docs.rs/apalis-workflow/latest/apalis_workflow/
  https://docs.rs/fang/
  https://docs.rs/sqlxmq/latest/sqlxmq/
- Restate Rust and architecture:
  https://docs.rs/restate-sdk/latest/restate_sdk/
  https://docs.rs/restate-sdk/latest/restate_sdk/context/trait.ContextTimers.html
  https://docs.rs/restate-sdk/latest/restate_sdk/context/trait.ContextClient.html
  https://docs.restate.dev/references/architecture
- Temporal Rust Core:
  https://temporal.io/blog/why-rust-powers-core-sdk
  https://docs.temporal.io/glossary
- External prior art:
  https://docs.dbos.dev/
