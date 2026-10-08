# Design: Async Reliability pilot program (`cargo asyncdoctor pilot`, `async-reliability-pack/v0`)

## Why this needs a pilot program
The archive already has three strong ingredients:
- [`design/async-lifecycle-kit.md`](./async-lifecycle-kit.md)
- [`design/replay-kit.md`](./replay-kit.md)
- [`design/dst-kit.md`](./dst-kit.md)

What it still lacked was the ranked execution layer that says **how these become one credible ecosystem contribution instead of three thoughtful adjacent notes**.

Current Rust signals make that timing unusually good:
- the async flagship says cancellation sharp edges, runtime choice, interoperability, and reliability are still central problems;
- the 2026 flagship themes keep **Just Add Async** active, which means the language is still unblocking the next generation of async libraries rather than declaring the async story “done”;
- the Async Book is being actively rewritten and now teaches concurrency primitives, structured concurrency, and pinning;
- Tokio already teaches a recognizable graceful-shutdown pattern with `CancellationToken` and `TaskTracker`, and the current docs now make one-way child cancellation and tracker drain semantics explicit enough to anchor a first portable lifecycle lane.

That combination suggests a practical rollout: start from service shutdown truth, then make failure capture portable, then connect deterministic exploration, and only after that widen toward multi-runtime/library/consumer stories.

## References (signals)
- 2025H1 async flagship:
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- 2026 flagship themes (`Just Add Async`):
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- May 2025 goals update / Async Book progress:
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- Async Book:
  https://rust-lang.github.io/async-book/
  https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html
- Tokio graceful shutdown:
  https://tokio.rs/tokio/topics/shutdown
- Tokio cancellation hierarchy primitive:
  https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- Tokio task tracker:
  https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- Loom:
  https://docs.rs/loom/latest/loom/
- Shuttle:
  https://docs.rs/shuttle/latest/shuttle/
- Turmoil:
  https://docs.rs/turmoil/latest/turmoil/
- MadSim:
  https://docs.rs/madsim/latest/madsim/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Design principles
1. **Start from shutdown and ownership.** That is the most common async failure surface and the best immediate source of reviewable value.
2. **Treat replay as a downstream handoff, not the starting substrate.** Many failures can be summarized before they can be replayed exactly.
3. **Treat deterministic simulation as exploration, not universal truth.** A DST backend should describe what it explored and what semantics it approximated.
4. **Preserve runtime identity.** Tokio-first pilots are acceptable; fake cross-runtime claims are not.
5. **Make consumer imports late and explicit.** Debugger, CI, incident, and support consumers should widen after the core pack boundary is solid.

## Shared pilot artifacts
### `async-reliability-brief/v0`
A short declaration of why a lane is being piloted.

Should record:
- pilot id
- lane family (`service-shutdown`, `failure-replay`, `deterministic-simulation`, `library-portability`, `consumer-import`)
- why this lane matters
- selected runtime / backend family
- intended consumers and success bar

### Core imports from existing kits
- `runtime-capability-profile/v0`
- `shutdown-policy/v0`
- `async-lifecycle-report/v0`
- `async-repro/v0`
- `replay-pack/v0`
- `replay-report/v0`
- `dst-config/v0`
- `dst-seed/v0`
- `dst-report/v0`
- optional `dst-history/v0`
- optional `test-pack/v0` attachment refs

### `async-reliability-pack/v0`
Portable bundle for a specific pilot lane.

Should contain:
- the pilot brief
- one lifecycle subject
- zero or more replay artifacts
- zero or more simulation artifacts
- exact/best-effort caveat markers
- links to attached test/time/tracing/debugger evidence
- review summary and unresolved gaps

Design rule: **this pack is a composition envelope, not a mega-schema that absorbs the underlying kits.**

## Ranked rollout

### Pilot 1 — Tokio service shutdown truth
Start with the highest-confidence, most teachable lane.

Artifacts:
- `runtime-capability-profile/v0`
- `shutdown-policy/v0`
- `async-lifecycle-report/v0`
- `async-reliability-brief/v0`

Success bar:
- a service can export task ownership, cancellation-tree posture, and shutdown posture without scraping logs;
- detached-task waivers, drain budgets, and tracker-close semantics are explicit;
- CI or code review can inspect the result.

### Pilot 2 — Failure handoff to replay
Once lifecycle truth exists, make observed failures portable.

Artifacts:
- lifecycle report
- `async-repro/v0`
- optional `replay-pack/v0` / `replay-report/v0`
- optional `test-pack/v0` attachment

Success bar:
- a shutdown hang, cancellation loss, or leaked-task bug can move from “we saw it once” to “here is the portable issue bundle”;
- exact vs best-effort replay is explicit.

### Pilot 3 — Deterministic simulation attachment
Connect lifecycle invariants to exploration tooling.

Artifacts:
- lifecycle policy/report
- `dst-config/v0`
- `dst-seed/v0`
- `dst-report/v0`
- optional `dst-history/v0`

Suggested backends/lanes:
- Loom for exhaustive permutation of valid concurrent executions
- Shuttle for randomized exploration at larger scales
- Tokio paused-time tests for time control
- Turmoil / MadSim / Moonpool-style lanes for multi-host or fault-rich exploration

Success bar:
- schedule/time/fault exploration can attach to the same async subject without pretending every backend has identical semantics.

### Pilot 4 — Runtime-portable library posture
Only after the service lane is solid, test the portability story.

Artifacts:
- runtime capability profiles for more than one adapter
- portability notes and unsupported semantics
- lifecycle report with approximation markers

Success bar:
- a library can explain what lifecycle guarantees it expects from a runtime and what parts are adapter-specific;
- the archive avoids pretending portability is free.

### Pilot 5 — Consumer import lane
Widen only after the core async reliability boundary is usable.

Consumers:
- Debugger Experience Kit
- Incident Kit
- Test Run Evidence Kit
- Support Envelope Kit
- Atlas / Semantic Context slices where justified

Success bar:
- consumers import the artifacts without silently redefining the async truth.

## What should count as success overall
The stack is working when:
- shutdown and cancellation policy are reviewable,
- async failures can be handed off into portable replay bundles when possible,
- deterministic exploration can attach without semantic dishonesty,
- runtime identity is preserved,
- and async debugging / incident / CI workflows become easier without any one tool becoming the de facto source of truth.

## Failure modes to avoid
- Starting with a fake universal runtime facade.
- Claiming deterministic replay where only “best effort” exists.
- Making observability logs the only durable artifact.
- Forcing DST backends into one semantic model.
- Jumping straight to debugger or assistant integration before the core lifecycle boundary is stable.

## Immediate archive instruction
Treat this file plus [`design/async-reliability-stack.md`](./async-reliability-stack.md) as the shared execution layer above Async Lifecycle, Replay, and DST.

The next credible async move is now a ranked stack program:
1. Tokio shutdown truth,
2. replay handoff,
3. deterministic simulation attachment,
4. library-portability lane,
5. consumer imports.
