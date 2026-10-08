# Design: Async Lifecycle Kit (`async-core`, `async-scope`, `cargo asyncdoctor`)

## Goal
Create a thin ecosystem layer that makes async Rust services and libraries easier to build, review, and shut down correctly by standardizing:
- a **lane-aware lifecycle facade**,
- **structured task-ownership primitives**,
- and **portable lifecycle evidence artifacts**.

This is not a new runtime. It is a convergence layer over the lifecycle concerns that Rust users still solve ad hoc and runtime-by-runtime, and it should import lower-level spawn / local / time / environment truth from Async Commons rather than pretending all async portability questions are lifecycle questions.

## References (signals)
- 2025H1 async flagship: async remains a multi-year parity effort, and the status quo still calls out runtime choice, runtime interoperability, cancellation sharp edges, and reliability as core pain points.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- May 2025 goals update: the official Async Book gained new chapters on concurrency primitives, structured concurrency, and pinning, which is a strong sign that lifecycle guidance is becoming first-class rather than folklore.
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- 2026 flagship themes: **Just Add Async** remains an active direction with milestones around RTN, `async fn` in `dyn Trait`, immobile types / guaranteed destructors, and ergonomic ref-counting.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- 2025H2 pin ergonomics goal: pinning still has poor ergonomics and directly affects async and generator usability.
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- 2025H2 ergonomic ref-counting goal: async Rust programs frequently share task context via ref-counted state, which means lifecycle friction is not just about futures syntax.
  https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Tokio graceful shutdown guidance and primitives (`CancellationToken`, `TaskTracker`, `JoinSet`) demonstrate both maturity of the pieces and the lack of a cross-runtime lifecycle contract.
  https://tokio.rs/tokio/topics/shutdown
  https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
  https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html

## Core components

### 1) `async-core`
A minimal facade crate for lifecycle-relevant async operations:
- `Spawner`
- `ScopedSpawner`
- `Cancellation`
- timer / shutdown-budget abstraction
- task-handle classification (`tracked`, `detached`, `blocking`, `local`)
- runtime capability query hooks

Design rule: **only include what is necessary for portability of lifecycle semantics**. Do not try to standardize whole runtime APIs.

### 2) `async-scope`
A structured-concurrency crate with explicit policies:
- scoped task groups / nurseries
- configurable drop policy:
  - `join`
  - `cancel_then_join`
  - `abort`
  - `detach_with_waiver`
- bounded shutdown budgets and reason codes
- error aggregation semantics suitable for services and libraries

The core value is not novelty; it is making task ownership visible and defaulting toward “no forgotten tasks”.

### 3) `runtime-capability-profile/v0`
Machine-readable runtime adapter declaration.

Should record:
- runtime family and adapter version
- imported `async-lane-profile/v0` / `async-capability-profile/v0` refs where available
- spawn/task-local/blocking support
- cancellation primitive used
- timer/sleep behavior relied on
- task-tracking support level
- unsupported semantics or approximation notes

### 4) `shutdown-policy/v0`
Explicit lifecycle contract for a scope or service.

Should record:
- trigger sources
- cancellation propagation rules
- drain budget / timeout posture
- drop policy
- detached-task waivers
- expected terminal states

### 5) `async-lifecycle-report/v0`
Machine-readable lifecycle evidence.

Should record:
- selected runtime capability profile
- shutdown policy digest
- scope topology / task tree metadata
- tracked vs detached tasks
- shutdown trigger and propagation path
- drain timing / timeout / outcome
- reason codes such as:
  - `TASK:DETACHED`
  - `TASK:SCOPE-LEAK`
  - `CANCEL:UNOBSERVED`
  - `SHUTDOWN:TIMEOUT`
  - `DROP:ABORT-POLICY`

### 6) `async-repro/v0`
Minimized issue bundle for hangs, shutdown failures, and cancellation hazards:
- seed / timing hints when present
- minimal fixture
- selected runtime adapter
- log or tracing excerpts
- preservation claim (`hang`, `leak`, `cancel-loss`, `late-shutdown`)

### 7) `async-pack/v0`
Bundle for review and reuse:
- runtime capability profile
- shutdown policy
- one or more lifecycle reports
- optional repro bundle
- references/rendered summaries

### 8) `cargo asyncdoctor`
Reference cargo UX:
- `cargo asyncdoctor lint`
  - detect lifecycle smells in declared scopes and optional annotations
- `cargo asyncdoctor test --shutdown`
  - run graceful-shutdown and cancellation-path tests
- `cargo asyncdoctor report`
  - emit `async-lifecycle-report/v0`
- `cargo asyncdoctor minimize`
  - export `async-repro/v0`

## What the kit should provide to others
- **Library authors:** a narrow portability facade and lifecycle conventions that reduce runtime-feature-matrix pain.
- **Application teams:** structured task ownership and predictable shutdown defaults.
- **Tooling authors:** stable report schemas instead of scraping runtime-specific logs.
- **Reviewers / CI:** objective artifacts proving that shutdown paths and task tracking were exercised.

## Integration points
- **Replay Kit:** consume `async-repro/v0` and enrich it with deterministic replay when available.
- **Debugger Experience Kit:** import task-topology and cancellation-path evidence to improve async-debug support claims.
- **Background Work Kit:** use async lifecycle artifacts as the substrate for durable worker supervision rather than re-specifying task shutdown.
- **Cargo Report Kit:** converge on report ergonomics and packaging conventions.

## Hard problems (explicitly scoped)
1. **Runtime mismatch**
   - v0 should support Tokio first and treat other runtimes as adapters rather than pretending perfect interchangeability.
2. **Static checking limits**
   - many cancellation bugs are semantic, not syntactic. Prefer evidence and conventions over fake guarantees.
3. **Pin and language evolution**
   - the kit must complement, not ossify around, current pin ergonomics limitations.
4. **Observability overhead**
   - task-tree capture and tracing hooks should be optional, with cheap defaults.
5. **Overreach risk**
   - if the crate starts replacing runtimes or pretending spawn/time/I/O/local/environment lanes are already one universal async surface, the design has failed.

## Stack position
Treat Async Lifecycle as the **declaration and lifecycle-evidence anchor** inside the broader [`design/async-reliability-stack.md`](./async-reliability-stack.md). Read [`design/async-commons-lane-map.md`](./async-commons-lane-map.md) as the lower-level rule for what spawn / local / time / environment truths should stay separate and imported here. Replay and DST should import lifecycle truth rather than redefine task ownership or shutdown policy.

## Execution order
Treat [`design/async-lifecycle-pilot-program.md`](./async-lifecycle-pilot-program.md) as the ranked rollout plan. The next credible move is not another async helper crate; it is proving that a Tokio-first lifecycle pack can survive service, library, and repro lanes honestly.
