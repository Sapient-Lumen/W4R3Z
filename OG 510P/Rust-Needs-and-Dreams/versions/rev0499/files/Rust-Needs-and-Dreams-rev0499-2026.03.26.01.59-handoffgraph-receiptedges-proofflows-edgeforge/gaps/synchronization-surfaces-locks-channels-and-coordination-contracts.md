# Gap: synchronization surfaces, coordination semantics, and reviewable shared-state contracts

## What is missing
Rust has many synchronization primitives, but the ecosystem still lacks a **portable way to describe what a synchronization surface actually promises**.

Today there is no standard way to say:
- whether a primitive is for blocking threads, async tasks, or both,
- whether waiting is FIFO, writer-preferring, best-effort, or intentionally unspecified,
- whether lock poisoning exists, is recoverable, or is intentionally absent,
- whether a channel is bounded, unbounded, rendezvous, last-value-only, broadcast-to-all, or work-stealing / at-most-one-consumer,
- whether backpressure is part of the contract or merely an implementation accident,
- whether a permit/guard may be held across `.await`,
- what “shutdown” means for queued values, reserved capacity, sender/receiver closure, lagged subscribers, or dropped waiters,
- which cancellation and clean-termination behaviors are guaranteed,
- which primitives assume a runtime, executor, or OS thread pool,
- and which claims were actually checked with interleaving tests, model checks, fairness vectors, or shutdown/cancellation vectors.

That gap matters because Rust’s roadmap is explicitly trying to make patterns that work in sync Rust also work in async Rust. At the same time, current practice still asks users to navigate a fragmented coordination toolbox: `std::sync::{Mutex,RwLock,Condvar,mpsc}`, `tokio::sync::{Mutex,RwLock,mpsc,watch,broadcast,oneshot,Notify,Semaphore}`, `parking_lot`, `crossbeam-channel`, `flume`, and concurrency-testing tools like `loom` and `shuttle`.

So the missing contribution is not one new mutex or one new channel crate.
It is a **reviewable synchronization-surface layer** for publishing coordination semantics honestly across blocking, async, and mixed-mode Rust.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://doc.rust-lang.org/std/sync/mpsc/
- https://docs.rs/tokio/latest/tokio/sync/index.html
- https://docs.rs/parking_lot
- https://docs.rs/crossbeam-channel
- https://docs.rs/flume
- https://docs.rs/loom
- https://docs.rs/shuttle

## The current seam is awkward
Rust already has real and meaningful semantic diversity here, but it is published mostly as crate docs, examples, or folklore:
- `std::sync::Mutex` has poisoning semantics;
- `parking_lot::Mutex` explicitly advertises itself as smaller, faster, and more flexible than std and exposes fairness-related unlock choices;
- Tokio’s async `Mutex` is explicitly FIFO/fair, but Tokio also says that in async code it is often preferred to use the ordinary std `Mutex` when you do not need to hold the guard across `.await`;
- Tokio’s `RwLock` is fair / write-preferring to avoid writer starvation;
- `std::sync::mpsc::channel` is infinitely buffered while `sync_channel` is bounded and can even be rendezvous-style at capacity 0;
- Tokio’s bounded `mpsc` makes backpressure explicit, while `UnboundedSender` is intentionally usable from both sync and async code;
- Tokio’s `watch` channel only retains the latest value, while `broadcast` delivers each value to all receivers and exposes lag-sensitive behavior;
- `Notify` carries no data and acts like a basic wakeup mechanism rather than a queue;
- semaphores coordinate permits rather than ownership of one protected value;
- and real verification already spans exhaustive-style schedule exploration (`loom`) and randomized schedule exploration (`shuttle`).

Those are not minor implementation details. They are precisely the facts that determine whether a primitive composes safely with a runtime, preserves latency budgets, leaks messages at shutdown, or matches a system’s backpressure story.

Sources:
- https://doc.rust-lang.org/std/sync/poison/struct.Mutex.html
- https://docs.rs/parking_lot/latest/parking_lot/type.Mutex.html
- https://docs.rs/parking_lot/latest/parking_lot/type.FairMutex.html
- https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
- https://docs.rs/tokio/latest/tokio/sync/struct.RwLock.html
- https://doc.rust-lang.org/std/sync/mpsc/
- https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
- https://docs.rs/tokio/latest/tokio/sync/watch/index.html
- https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html
- https://docs.rs/tokio/latest/tokio/sync/struct.Notify.html
- https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html
- https://docs.rs/loom/latest/loom/
- https://docs.rs/shuttle/latest/shuttle/

## Why this matters
This gap matters because synchronization choices cut across almost every serious Rust domain:
1. **Async/sync interop** — Rust is explicitly trying to bring async closer to parity with sync Rust, but users still need to know when a blocking primitive is fine in async code and when a runtime-aware primitive is required.
2. **Backpressure and shutdown** — queues and channels are where systems silently smuggle policy. “bounded”, “unbounded”, “latest only”, “broadcast”, and “close then drain” are public semantics, not just transport trivia.
3. **Fairness and starvation** — read/write priority, FIFO acquisition, and fair unlock behavior determine latency tails and liveness in production, but these guarantees are hard to compare across crates.
4. **Safety-critical and long-lived systems** — the 2026 safety-critical work explicitly says async is not just a language feature; it pulls in runtime choices, scheduling assumptions, and quality/process artifacts. Synchronization semantics therefore need to be explainable, not guessed.
5. **Verification and maintenance** — interleaving tests often live far away from the docs that describe the primitive surface. That makes it too easy to change shutdown, lag, or fairness behavior without leaving reviewable evidence.

A worthy contribution here is therefore not another synchronization toolbox.
It is a way to treat synchronization surfaces as **reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
- https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
- https://docs.rs/loom/latest/loom/
- https://docs.rs/shuttle/latest/shuttle/

## What “good” looks like
A worthy contribution here is **not** one universal queue/lock API that erases meaningful differences.

It is a shared synchronization-surface boundary:
- one `sync-surface/v0` describing the coordination role and runtime/blocking posture,
- one `lock-profile/v0` for mutex/rwlock/condvar-like semantics such as poisoning, fairness, guard lifetime, and starvation posture,
- one `channel-profile/v0` for queue topology, fan-in/fan-out shape, backpressure, retention, lag/drop posture, and closure semantics,
- one `signal-permit-profile/v0` for semaphore/notify/oneshot-style coordination without pretending they are queues,
- one `shutdown-cancel-profile/v0` for close/drain/drop/lag/cancel behavior,
- one `sync-adapter-profile/v0` for wrappers and migrations between blocking and async surfaces,
- one `sync-vector-set/v0` for fairness, cancellation, shutdown, lag, backpressure, and interleaving vectors,
- one `sync-check-report/v0` recording what actually ran under normal tests, loom-like checks, or shuttle-like schedule exploration,
- and one `sync-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams review coordination semantics using explicit artifacts instead of inferring them from crate names, blog posts, snippets, or “works for me” examples.

## Non-goals
This gap should not be used to:
- define all of Rust concurrency or replace the memory model,
- flatten locks, channels, semaphores, `Notify`, oneshot signals, and structured concurrency into one fake primitive,
- bless one runtime or one synchronization crate as the official answer,
- or hide missing shutdown / fairness / cancellation semantics behind a generic “thread-safe” badge.

The job is smaller and sharper:
**make synchronization surfaces legible, honest, and checkable across blocking, async, and mixed-mode Rust.**
