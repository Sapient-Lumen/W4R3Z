# Epic Proposal: Async Lifecycle Kit (`async-core`, `async-scope`, `cargo asyncdoctor`)

## One-sentence pitch
Make async Rust feel less like “hard mode” by standardizing task ownership, cancellation propagation, graceful shutdown, and runtime-portable lifecycle evidence.

## Deliverables
- `async-core` portability facade
- `async-scope` structured concurrency / nursery crate
- `cargo asyncdoctor` reference tool
- Schemas:
  - `runtime-capability-profile/v0`
  - `shutdown-policy/v0`
  - `async-lifecycle-report/v0`
  - `async-repro/v0`
  - `async-pack/v0`
- Tokio-first adapter, with later adapters only where justified
- Docs:
  - shutdown playbook
  - library-author portability guidance
  - CI recipe for lifecycle checks
  - ranked pilot-program guidance

## Why now (signals)
- The 2025H1 async flagship frames async as a multi-year parity effort and explicitly says the project should support reliable, standardized abstractions for async control flow while making room for a thriving async ecosystem.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The May 2025 goals update says the next generation of async libraries is being unblocked by language work, and the Async Book now teaches concurrency primitives, structured concurrency, and pinning as core topics.
  https://blog.rust-lang.org/2025/06/20/may-project-goals-update/
- The 2026 flagship themes keep **Just Add Async** active, with milestones around RTN, `async fn in dyn Trait`, immobile types / guaranteed destructors, and ergonomic ref-counting.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Pin ergonomics remains active because `Pin` continues to block async/generator ergonomics.
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
- Ergonomic ref-counting highlights how often async systems share task context through `Arc`-like patterns, reinforcing that lifecycle structure and ownership are central ergonomic pain points.
  https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Tokio’s guidance already points developers toward cancellation tokens, task tracking, and explicit drain phases for graceful shutdown, demonstrating demand for the pattern while also highlighting today’s runtime specificity.
  https://tokio.rs/tokio/topics/shutdown

## Non-goals
- Replacing Tokio, async-std, or Smol
- Defining all async APIs behind one facade
- Pretending different runtimes have identical semantics
- Proving cancellation correctness statically in the general case
- Waiting for every upstream async language piece to land before helping users

## Strategic value
This is a worthy contribution because it attacks a gap that is both **common** and **under-standardized**:
- it helps library authors converge on a smaller portability surface,
- it makes shutdown correctness reviewable and teachable,
- it gives CI something better than “hope our teardown logic works”,
- it creates portable attachments for triage/debugging consumers,
- and it complements official async language work instead of competing with it.

## Milestones
1. **Pilot 1: Tokio service shutdown lane**
   - Tokio adapter
   - explicit shutdown policy
   - lifecycle report export
2. **Pilot 2: runtime-portable library lane**
   - adapter capability profiles
   - limited portability reports
   - unsupported/approximation markers
3. **Pilot 3: supervised worker lane**
   - integration with Background Work Kit
   - topology and cancellation-path evidence
4. **Pilot 4: repro / debugger-consumer lane**
   - `async-repro/v0`
   - Replay / Debugger integration
5. **Later widening**
   - additional runtimes where justified
   - constrained/embedded async lane
   - deeper tracing hooks where they pay for themselves

## Stack position
Treat Async Lifecycle as one part of the broader [`design/async-reliability-stack.md`](../design/async-reliability-stack.md): it owns lifecycle truth, while Replay and DST own downstream failure-capture and exploration lanes.

## Immediate archive instruction
Treat [`design/async-lifecycle-pilot-program.md`](../design/async-lifecycle-pilot-program.md) as the ranked rollout plan. The next credible async-lifecycle move is not another convenience crate; it is a Tokio-first evidence lane that can later survive library portability and repro/debug consumers without hiding runtime truth.
