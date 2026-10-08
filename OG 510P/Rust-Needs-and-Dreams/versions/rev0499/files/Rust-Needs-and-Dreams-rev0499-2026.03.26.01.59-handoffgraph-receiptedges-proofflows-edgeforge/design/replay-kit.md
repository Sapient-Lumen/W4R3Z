# Design: Replay Kit (`cargo replay`, replay-pack/v0)

## Goal
Provide a practical record/replay + minimization workflow for async/concurrency bugs by defining:
- a reference CLI (`cargo replay`),
- a portable artifact format (`replay-pack/v0`) for “bug cassettes”,
- runtime-agnostic instrumentation adapters (via `tracing`),
- integration points with Loom/Shuttle/Tokio Console and (optionally) rr.

## References (signals)
- Loom: https://crates.io/crates/loom
- Shuttle: https://docs.rs/shuttle/latest/shuttle/
- Tokio Console: https://crates.io/crates/tokio-console ; https://github.com/tokio-rs/console
- rr: https://rr-project.org/ ; https://github.com/rr-debugger/rr
- lildb async debugger writeup: https://cliffle.com/blog/lildb/

## Core UX: `cargo replay`
- `cargo replay record --test <name>`
  - run test/integration test with instrumentation
  - save a `replay-pack/v0` on failure (or always, via flag)
- `cargo replay replay <pack>`
  - deterministically replay the schedule/events
  - support “single-step” and “reverse” navigation where possible
- `cargo replay minimize <pack>`
  - shrink failing schedule:
    - remove events not needed
    - shrink interleavings
    - reduce timing nondeterminism
  - output a smaller pack
- `cargo replay diff <A> <B>`
  - compare two packs (useful for “did we fix it?”)
- `cargo replay report`
  - emit `replay-report/v0` summary suitable for CI

## Instrumentation model
### Layer 1: logical events (preferred, portable)
- task lifecycle:
  - spawn, poll, wake, block, drop
- synchronization:
  - mutex lock/unlock, channel send/recv, notify/wait
- time:
  - sleep, deadline timers, clock reads (virtualized)

Implementation approach:
- `tracing` spans/events for runtime hooks (Tokio Console already uses tracing layers).
  - A `ReplayLayer` captures events and scheduler decisions.

### Layer 2: scheduler control (for deterministic replay)
- Provide a “virtual executor” mode for tests that routes scheduling decisions through Replay Kit.
- For non-instrumented code, support “best-effort” replay of captured decisions.

### Layer 3: OS-level record/replay (optional)
- For Linux-only or last-resort debugging, allow attaching an rr trace pointer *inside* the replay pack.
- Use rr for reverse execution at the syscall level, while Replay Kit provides task-level semantics.

## Artifacts
### `replay-pack/v0`
- subject metadata:
  - crate, git sha (optional), toolchain
  - test command and env allowlist hash
- event log:
  - logical events (content-addressed chunks)
  - scheduler decisions
  - time virtualization data
- privacy controls:
  - redaction rules for fields
  - optional “payload elision” (hash-only payloads)
- attachments:
  - `tokio-console` capture pointer (optional)
  - `rr` trace pointer (optional)

### `replay-report/v0`
- pass/fail on replay
- minimization stats (events reduced, time reduced)
- reason codes:
  - `NONDETERMINISTIC_SOURCE_UNCAPTURED`
  - `UNSUPPORTED_RUNTIME_HOOK`
  - `PRIVACY_REDACTION_BLOCKED`
  - `REPLAY_DIVERGENCE`
- hints:
  - add instrumentation, pin timers, avoid wall-clock reads

## Integration points
- Loom/Shuttle:
  - convert failing loom/shuttle schedules into replay packs for sharing
- Tokio Console:
  - attach console captures to replay packs for rich inspection
- Policy/Trust:
  - treat replay packs as incident evidence (ties into Incident Kit)

## Stack position
Treat Replay as the **observed-failure capture lane** inside the broader [`design/async-reliability-stack.md`](./async-reliability-stack.md). Replay should import lifecycle and test-run subject identity where available, and it should stay distinct from deterministic simulation.

## Evaluation plan
- Pilot targets:
  - async channel-heavy services
  - mutex contention workloads
- Benchmarks:
  - overhead of recording (goal: low single-digit % in tests)
  - minimization effectiveness
- UX bar:
  - “paste one file in an issue and another dev can replay it”
