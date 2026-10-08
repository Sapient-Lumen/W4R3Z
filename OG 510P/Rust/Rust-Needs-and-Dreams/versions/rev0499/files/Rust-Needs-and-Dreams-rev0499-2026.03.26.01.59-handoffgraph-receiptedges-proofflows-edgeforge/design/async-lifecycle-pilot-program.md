# Design: Async Lifecycle pilot program (`cargo asyncdoctor pilot`, `async-pilot-pack/v0`)

## Why this needs a pilot program
The archive already has a credible **Async Lifecycle Kit**, but the missing question is now more practical: **how does this become a real contribution instead of one more async helper crate?**

Current Rust signals argue for staged rollout:
- async remains a multi-year flagship effort, and the project still explicitly calls out runtime choice, runtime interoperability, cancellation sharp edges, and reliability as problems worth solving;
- the Async Book is now teaching structured concurrency and pinning as first-class topics;
- the 2026 flagship themes keep **Just Add Async** alive, which means ecosystem-facing lifecycle conventions are more valuable now, not less;
- Tokio already proves the pieces exist for graceful shutdown, but they are still runtime-shaped patterns rather than a portable review boundary.

That combination points to a ranked pilot program: prove lifecycle evidence in a few high-pressure lanes before widening adapters or schemas.

## References (signals)
- Async parity flagship, including runtime-choice and reliability pain:
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- Async Book progress on concurrency primitives, structured concurrency, and pinning:
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- 2026 flagship themes (`Just Add Async`):
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Pin ergonomics:
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- Ergonomic ref-counting for async task-shared state:
  https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Tokio graceful shutdown building blocks:
  https://tokio.rs/tokio/topics/shutdown

## Design principles
1. **Start from ownership and shutdown, not abstract purity.** Detached tasks, cancellation propagation, and drain policy are the first truths to standardize.
2. **Adapters before universality.** Tokio-first is acceptable; fake cross-runtime equivalence is not.
3. **Budgets must be artifacts.** Timeouts, drop policy, and detached-task waivers should not hide in prose.
4. **Service and library lanes are different.** A service can own process shutdown; a library usually cannot.
5. **Evidence should feed nearby tools.** Replay and debugger consumers are part of the value proposition.
6. **Do not wait for the perfect language future.** RTN, async dyn traits, ergonomic ref-counting, and guaranteed destructors will help, but they do not eliminate the current lifecycle gap.

## Artifact additions for pilot work
### `async-pilot-brief/v0`
Why this lane is being piloted now.

Should record:
- pilot id and summary
- lane family (`service-shutdown`, `library-portability`, `background-workers`, `repro`, `constrained-async`)
- why the lane matters
- intended consumers and success bar

### `runtime-capability-profile/v0`
Used to declare what the selected runtime adapter can and cannot promise.

### `shutdown-policy/v0`
Used to make drain budgets, drop policy, and detached-task waivers explicit.

### `async-lifecycle-report/v0`
Used to export task topology, cancellation propagation, and shutdown outcomes.

### `async-pilot-scorecard/v0`
Should ask:
- did the pilot preserve runtime-specific truth honestly?
- did it avoid becoming a runtime wrapper?
- did a real consumer use the exported artifact?
- did it make shutdown/cancellation review easier than bespoke logs?
- is widening to more adapters or lanes justified?

## Ranked pilots

### 1) Tokio service graceful-shutdown lane
**Why first**
- Tokio already documents the core pieces (`CancellationToken`, task tracking, join/drain patterns), so this lane has the best ratio of pain to tractability.
- It exercises the most important operational truths: trigger, propagation, drain, timeout, detached tasks, and final state.

**Core artifacts**
- `runtime-capability-profile/v0`
- `shutdown-policy/v0`
- `async-lifecycle-report/v0`
- `async-pack/v0`

**Acceptance bar**
- A service can attach one pack to CI or a release review and answer: what tasks were owned, how shutdown propagated, whether drain completed within policy, and where explicit waivers existed.

### 2) Runtime-portable library lane
**Why second**
- The async flagship is explicit that runtime choice is hard to reverse and cross-runtime library interoperability is awkward.
- This lane tests whether the kit can shrink feature-matrix pain without pretending runtimes are identical.

**Core artifacts**
- adapter-specific `runtime-capability-profile/v0`
- library-scoped `shutdown-policy/v0` or lifecycle contract notes
- `async-lifecycle-report/v0` from adapter test runs
- unsupported/approximation markers

**Acceptance bar**
- A library can publish which lifecycle assumptions it makes and prove a limited, honest portability story across selected runtime adapters.

### 3) Background-worker / supervised-task lane
**Why third**
- Many services fail not on request handling but on worker drains, retries, and shutdown coordination.
- This lane creates a clean handoff between Async Lifecycle Kit and Background Work Kit.

**Core artifacts**
- task-group topology export
- worker shutdown policy
- cancellation-path evidence
- integration notes for durable work systems

**Acceptance bar**
- Worker families can be reviewed as owned/supervised task groups rather than hidden detached tasks.

### 4) Issue / repro / debugger-consumer lane
**Why fourth**
- By this point, lifecycle reports should be useful not only in CI but also for triage.
- This lane proves the kit composes with Replay Kit and Debugger Experience Kit instead of living in isolation.

**Core artifacts**
- `async-repro/v0`
- selected `async-lifecycle-report/v0`
- debugger-facing task topology attachment

**Acceptance bar**
- An async hang, shutdown failure, or cancellation bug can be reported with one portable bundle that helps both replay and debugging consumers.

### 5) Constrained / embedded async lane
**Why fifth**
- The async flagship explicitly spans from embedded to cloud, but this lane should come later because runtime assumptions differ more sharply.
- The point is to test whether lifecycle artifacts can degrade honestly in constrained environments.

**Core artifacts**
- constrained runtime-capability profile
- reduced shutdown policy
- lightweight lifecycle report

**Acceptance bar**
- The kit can express reduced capabilities and still provide useful lifecycle truth without pretending full-service semantics exist.

## What should wait
- Do **not** begin with a universal runtime facade.
- Do **not** begin with a cross-runtime compatibility badge.
- Do **not** begin with distributed tracing ingestion or a “full async observability platform”.

Those are downstream possibilities. First prove that lifecycle ownership and shutdown truth can be exported honestly in a few real lanes.

## Immediate archive decision
Treat [`design/async-lifecycle-kit.md`](./async-lifecycle-kit.md) and [`proposals/epic-async-lifecycle-kit.md`](../proposals/epic-async-lifecycle-kit.md) as the schema/epic anchors, and treat this file as the **execution order**. The next credible move is a Tokio-first lifecycle pack that survives Pilot 1 and Pilot 2 honestly, not another crate that hides task ownership behind convenience APIs.
