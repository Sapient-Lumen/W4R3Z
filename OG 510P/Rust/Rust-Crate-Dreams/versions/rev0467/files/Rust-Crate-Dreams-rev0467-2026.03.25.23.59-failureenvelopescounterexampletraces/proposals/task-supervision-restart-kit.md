---
id: P-0095
title: Task Supervision & Restart Kit — topology receipts, restart-policy receipts, health/source receipts, state-reset receipts, shutdown-escalation receipts, and failure bundles
status: idea
domains: [async, runtime, resilience, supervision, operations, debugging, testing]
last_reviewed: 2026-03-21
evidence:
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html
  - https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
  - https://docs.rs/task_scope/latest/task_scope/
  - https://docs.rs/task-supervisor/latest/task_supervisor/
  - https://docs.rs/spry/latest/spry/
  - https://docs.rs/ractor-supervisor/latest/ractor_supervisor/
  - https://docs.rs/tokio/latest/tokio/task/
  - https://www.erlang.org/doc/apps/stdlib/supervisor.html
---

# Problem

Rust has solid async building blocks, but it still lacks one **boring supervision contract** for long-lived background work.

The current substrate is useful but fragmented:

- the Rust project still calls out async complexity and runtime lock-in as live ecosystem pain;
- Tokio offers task spawning, cancellation, `JoinSet`, and graceful-shutdown substrate such as `CancellationToken` + `TaskTracker`, but that is not the same thing as a reviewable supervisor contract;
- `task_scope` and adjacent scoped-task crates improve cancellation structure, but they are not restart-policy or restart-evidence tooling;
- `task-supervisor` proves there is appetite for “keep this Tokio task alive”, including restart limits, backoff, and hung-task detection;
- `spry` proves startup/readiness and orderly restart/shutdown conventions can matter independently from raw spawning;
- `ractor-supervisor` proves OTP-style strategies, meltdown windows, and multi-level supervision trees are meaningful in Rust today.

What is still missing is one crate lane that helps another team answer, with portable artifacts:

1. **What is the restart blast radius?**
2. **Which exits or health failures actually trigger restart?**
3. **What state is reset versus retained across restart?**
4. **What happens during graceful stop, timeout, and blocking-work escape?**
5. **What failure bundle can another reviewer inspect without rerunning the system from folklore?**

The missing contribution is therefore **not** another actor framework, **not** just scoped cancellation, and **not** only a watchdog loop.
It is a **Task Supervision & Restart Kit**: one receiver-facing contract for topology, restart policy, health basis, state-reset basis, shutdown escalation, and failure bundles above Tokio tasks, actor supervision, and ad hoc keepalive loops.

# Main judgment

This lane is worthy because long-lived async work is where Rust teams still end up rebuilding the same operational semantics by hand.
A library can honestly say “uses `JoinSet`”, “supports graceful shutdown”, or “restarts failed tasks”, while downstream teams still cannot tell:

- whether one failing worker restarts itself or its siblings too,
- whether a normal exit is success or a restart trigger,
- whether a hung task is detected at all,
- whether restart reuses shared state or resets from a template,
- and whether shutdown timeout actually stops work or only stops waiting.

A worthy crate should therefore help other people review six separate truths before trusting a supervision claim:

1. **supervision topology** — static versus dynamic membership, child ordering, and restart blast radius;
2. **restart policy** — restart class, trigger classes, backoff, and meltdown windows;
3. **health / readiness basis** — how a child becomes “stable” and how a hung child is detected;
4. **state reset basis** — which in-memory mutations are reset, shared, or rehydrated across restart;
5. **shutdown escalation** — how stop signals, drain phases, timeout aftermath, and blocking-work escape are handled;
6. **failure bundle** — the portable artifact set attached to a supervision incident.

# What it provides

- `supervision-topology.receipt.json` — supervisor family, strategy, membership shape, dependency/order basis, and restart blast radius.
- `restart-policy.receipt.json` — restart class, trigger classes, backoff policy, meltdown window, and reset-after rules.
- `health-source.receipt.json` — readiness basis, health basis, probe scope, and unresponsive-task action.
- `state-reset.receipt.json` — restart state source, mutation-retention posture, and whether reset semantics are explicit or implicit.
- `shutdown-escalation.receipt.json` — stop-signal basis, graceful phase, timeout aftermath, and blocking-work posture.
- `supervision-failure-bundle.manifest.json` — attached receipts, timeline/log attachments, redaction posture, and incident classification.
- `restart.summary.md` — compact support/oncall handoff note.
- `restart.diff.json` — compares two supervision bundles and classifies topology, policy, health, state-reset, or shutdown drift.
- `cargo supervise receipt` — emits the compact receipts from a service or scenario.
- `cargo supervise doctor` — warns when restart claims overstate blast radius, state retention, or timeout behavior.
- `cargo supervise bundle` — emits one small support bundle.
- `cargo supervise inspect` — summarizes what restart/shutdown semantics another reviewer can honestly rely on.

# What the crate should provide other people

1. **Blast-radius honesty** so `one_for_one`, `one_for_all`, and ordered suffix restarts stop being folklore.
2. **Trigger honesty** so panic, abnormal exit, normal exit, hung deadlines, and startup failure do not masquerade as one generic “failure”.
3. **State-reset honesty** so clone-from-template restarts and shared `Arc` state are not confused.
4. **Shutdown honesty** so graceful wait, abort, and “work may still continue after timeout” remain visibly different outcomes.
5. **Health-basis honesty** so panic-only monitoring and heartbeat/deadline monitoring stop being blurred together.
6. **One boring review vocabulary** that async service teams, actor users, operations reviewers, and framework authors can share.

# Personas / who it’s for

- service teams running long-lived background workers, schedulers, consumers, and sidecars;
- platform teams standardizing how services describe restart and shutdown behavior;
- framework authors who want to expose supervision semantics without forcing one actor model;
- oncall and SRE teams who need support bundles when restart storms or hung workers happen;
- library maintainers whose crates spawn internal tasks and need to state what restart/shutdown guarantees exist.

# Users & user stories

- **Service maintainer:** “If a websocket task dies, do I restart only it, or the HTTP server plus its dependent background tasks too?”
- **Reviewer:** “If restart happens, does the child start from a pristine template, retain shared counters, or rehydrate persisted state?”
- **Oncall engineer:** “Did timeout abort the tasks, or did the process merely stop waiting while blocking work kept running?”
- **Framework author:** “I have health probes and readiness gates, but I want a stable artifact vocabulary instead of prose.”
- **Safety / operations reviewer:** “Show me the restart storm window and what bundle I get when it trips.”

# Prior art (and why it’s insufficient)

- Tokio `JoinSet` is strong task-collection substrate, but it does not standardize restart topology, health policy, or failure artifacts.
- Tokio `TaskTracker` and `CancellationToken` are useful for graceful shutdown, but they are still only shutdown substrate; they do not tell another team what happens after timeout or what restart semantics exist.
- `task_scope` improves child-task cancellation discipline, but scope shutdown is not restart policy, restart blast radius, or restart evidence.
- `task-supervisor` proves demand for restarted Tokio tasks and documents clone-on-restart semantics, but that still leaves topology, cross-task blast radius, state-reset honesty, and portable incident bundles under-specified.
- `spry` proves that orderly startup and the meaning of “stable state” matter, but readiness semantics still need portable receipts.
- `ractor-supervisor` proves that OTP-style strategies, meltdown windows, and subtree-local policy are useful in Rust, but actor-supervision substrate is not yet the same thing as a runtime-agnostic support contract.

What remains missing is the **topology + restart policy + health/readiness basis + state-reset basis + shutdown-escalation + failure bundle** layer above today’s individual crates.

# Design goals

1. **Contract-first, not framework-first.** Start from what another team can review.
2. **Tokio-first, vocabulary-portable.** Import Tokio task/shutdown truths without making Tokio the only mental model.
3. **Topology honesty.** Restart blast radius and child ordering must remain explicit.
4. **State-reset honesty.** Clone-template restarts, shared `Arc` state, and persisted rehydrate paths must remain distinct.
5. **Shutdown honesty.** Graceful drain, abort, and timeout-after-work-escapes must not be flattened.
6. **Health honesty.** Panic-only monitoring and hung-task detection are different products.
7. **Import, don’t replace.** Build above Tokio, actor supervisors, and scoped-task substrate instead of demanding one new runtime.
8. **Manual-review over fake certainty.** When the tool cannot prove the claim, emit `manual_review_required`.
9. **Small bundles.** `0.1` should fit code review, CI artifacts, and support handoff.

# MVP surface

- Minimal types:
  - `SupervisionTopologyReceipt`
  - `RestartPolicyReceipt`
  - `HealthSourceReceipt`
  - `StateResetReceipt`
  - `ShutdownEscalationReceipt`
  - `SupervisionFailureBundleManifest`
  - `RestartDiff`
- Import adapters:
  - Tokio task groups / `JoinSet`
  - `CancellationToken` + `TaskTracker` shutdown paths
  - `task-supervisor` task definitions
  - `ractor-supervisor` child specs and meltdown config
  - manual JSON/TOML descriptors for other runtimes/frameworks
- Outputs:
  - receipts/reports as JSON
  - a tiny `restart.summary.md`
  - one zip/tar support bundle format reusing the archive’s evidence-bundle vocabulary when useful

# Proposed fixture / artifact vocabulary

- `supervision-topology.receipt.json`
- `restart-policy.receipt.json`
- `health-source.receipt.json`
- `state-reset.receipt.json`
- `shutdown-escalation.receipt.json`
- `supervision-failure-bundle.manifest.json`
- `restart.summary.md`
- `restart.diff.json`

# Suggested commands

- `cargo supervise receipt`
- `cargo supervise doctor`
- `cargo supervise bundle`
- `cargo supervise inspect`
- `cargo supervise diff`

# Adoption plan

## Who adopts it first

- Tokio services that already have background workers and ad hoc restart loops.
- Actor-based systems that want exportable receipts without forcing every consumer into actor terminology.
- Internal platform teams standardizing runbooks and support-bundle expectations.

## Why they adopt

- It shortens support and design review: restart semantics stop living in tribal knowledge.
- It gives teams one portable way to say whether restart is safe, what resets, and what shutdown actually means.
- It lets current frameworks stay in place while exporting shared receipts.

## Path to ecosystem pull

- Start with Tokio and one actor-supervision adapter.
- Ship doctor warnings that catch over-claims around clone reset, hung detection, and timeout aftermath.
- Publish tiny scenario bundles that maintainers can copy into docs and CI.
- Keep artifact vocabulary runtime-agnostic enough that other runtimes can import without pretending feature parity.

# Maintenance plan

- Keep the core schema set tiny and versioned.
- Prefer adapters and vocabulary extensions over deep runtime coupling.
- Treat doctor warnings as semver-sensitive public surface.
- Maintain explicit redaction guidance for failure bundles.

# Risks / sharp edges

- A supervision contract can easily over-claim if it hides runtime-specific shutdown behavior.
- Restart semantics vary widely between task loops, actor systems, and process-level supervisors.
- Clone-based restart can look safe while silently dropping meaningful in-memory state.
- Blocking work and external side effects complicate “restart succeeded” claims.
- Too much framework ambition would turn this into another actor/runtime ecosystem instead of a contract lane.

# Non-goals

- a universal actor framework;
- a new async runtime;
- full distributed process supervision across hosts;
- exactly-once semantics for restarted side effects;
- a hosted orchestration control plane;
- replacing existing task or actor libraries.

# Relationship to other proposals

- Distinct from **P-0520 Crate Lifecycle Surface Pack Kit**: lifecycle support is the broader receiver-facing shutdown truth lane; **P-0095** is the restart/topology/health/state-reset lane for supervised work.
- Distinct from **P-0529 Channel Surface Contract Kit**: channels define delivery/backpressure truth, not supervision topology.
- Distinct from **P-0073 Async Replay Debugger Kit**: replay/debugging describes what an async incident bundle can replay; **P-0095** describes restart policy and shutdown semantics before or alongside replay.
- Distinct from **P-0532 Async Runtime Assurance Profile Kit**: runtime assurance is about choosing and qualifying a runtime family; **P-0095** is about application/task supervision above that runtime.
- Distinct from actor frameworks and worker libraries: those are substrate; **P-0095** is the portable review contract above them.

# What to leave for later

- multi-process and distributed supervision graphs;
- universal adapters for every async runtime;
- deep IDE visualization;
- hosted dashboards and orchestration UIs;
- automatic derivation of side-effect idempotence;
- full synthesis from arbitrary tracing streams without declared config.

# Open questions

- Should `0.1` include a separate `effect-idempotence.receipt` or leave that to notes plus manual review?
- How much of meltdown policy belongs in the core receipt versus optional framework adapters?
- Should readiness and liveness remain one receipt or split once enough frameworks expose distinct hooks?
- How much bundle redaction guidance belongs in this crate versus the shared evidence-bundle substrate?

# Sources

See front matter links.
