# Design: Synchronization Surface Kit (`cargo syncsurf`, `sync-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **synchronization surfaces** in Rust: blocking locks, async locks, condition variables, semaphores, notifications, oneshot signals, bounded/unbounded channels, latest-value channels, broadcast channels, and mixed-mode adapters.

This should help answer questions like:
- is this primitive intended for blocking threads, async tasks, or both,
- can a guard/permit be held across `.await`,
- what fairness or starvation posture is promised,
- what happens on close, cancellation, lag, or dropped receivers,
- is backpressure part of the public contract,
- can producers and consumers live in different runtimes or in sync + async code simultaneously,
- and what evidence demonstrates these claims.

It should **not** replace the primitives themselves, settle runtime design, or redefine Rust’s memory model.
It should make coordination semantics reviewable.

## References (signals)
- Rust’s 2026 flagships say “patterns that work in sync Rust should work in async Rust”, with milestones like RTN, async fn in dyn trait, immobile types/guaranteed destructors, and ergonomic ref-counting. That is strong evidence that the sync/async boundary remains active ecosystem terrain.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H1 goals explicitly framed async parity as part of making Rust easier to use for network systems, while improving `Pin` ergonomics and preparing async/sync generators.
  https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- The safety-critical vision work says async is not “just a language feature”; it pulls in runtime choices, scheduling assumptions, and quality/process artifacts, and explicitly recommends defining requirements for safety-case-friendly async runtimes.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Tokio’s `sync` docs say message passing is the most common form of synchronization in Tokio programs, while Tokio’s mutex docs explicitly warn that std mutexes are often preferred in async code unless you need to hold the guard across `.await`.
  https://docs.rs/tokio/latest/tokio/sync/index.html
  https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
- Std and Tokio channels already encode materially different semantics: infinite buffering vs bounded backpressure, single-consumer vs multi-consumer flavors, last-value retention, and clean shutdown guidance.
  https://doc.rust-lang.org/std/sync/mpsc/
  https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
  https://docs.rs/tokio/latest/tokio/sync/watch/index.html
  https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html
- `parking_lot`, `crossbeam-channel`, `flume`, `loom`, and `shuttle` are concrete evidence that the ecosystem already has strong point solutions but not a shared review/evidence layer above them.
  https://docs.rs/parking_lot
  https://docs.rs/crossbeam-channel
  https://docs.rs/flume
  https://docs.rs/loom
  https://docs.rs/shuttle

## Core idea
Treat synchronization semantics as a first-class surface, not just an implementation detail buried in docs.

The kit should separate:
1. **coordination role** — lock, queue, semaphore, signal, or hybrid;
2. **runtime posture** — blocking-only, async-only, mixed-mode, or runtime-agnostic;
3. **wait semantics** — FIFO, write-preferring, best-effort, unspecified, single-permit, broadcast, latest-value, rendezvous, etc.;
4. **backpressure/retention semantics** — bounded, unbounded, overwrite-latest, broadcast lag, queue drain, permit exhaustion;
5. **closure/shutdown/cancellation semantics** — what counts as closed, when sends/receives fail, whether queued items drain, and what is dropped;
6. **verification posture** — normal tests, schedule exploration, fairness vectors, shutdown vectors, and unsupported claims.

## Proposed artifact family

### 1) `sync-surface/v0`
Top-level description of a synchronization primitive or a family.

Fields should include:
- artifact id
- crate/module/item identity
- primitive class (`mutex`, `rwlock`, `condvar`, `channel`, `watch`, `broadcast`, `oneshot`, `notify`, `semaphore`, `hybrid`)
- intended execution domain (`blocking`, `async`, `mixed`, `runtime-agnostic`)
- data-bearing vs signal-only status
- attached profile references
- supported targets / `std` / `alloc` / `no_std` posture

### 2) `lock-profile/v0`
For mutex/rwlock/condvar-style primitives.

Fields should include:
- ownership / guarded-data model
- poisoning posture
- fairness / starvation posture
- reader/writer priority policy
- whether guards may cross `.await`
- reentrancy posture if relevant
- wakeup/spurious-wakeup notes for condvar-like surfaces
- blocking behavior and runtime assumptions

### 3) `channel-profile/v0`
For queues and data-bearing channels.

Fields should include:
- producer/consumer topology (`mpsc`, `mpmc`, `broadcast`, `watch`, `oneshot`, etc.)
- bounded / unbounded / rendezvous / overwrite-latest capacity mode
- ordering guarantees
- backpressure semantics
- lag / overwrite / drop semantics
- closure rules for senders and receivers
- clean-shutdown posture
- sync↔async crossing support

### 4) `signal-permit-profile/v0`
For `Semaphore`, `Notify`, oneshot notifications, and similar surfaces.

Fields should include:
- stored data vs no-data signaling
- permit accounting model
- close semantics
- fairness / queueing posture
- lost-wakeup / stored-permit semantics
- cancellation of waiters
- runtime assumptions

### 5) `shutdown-cancel-profile/v0`
Captures termination and cancellation semantics across primitive families.

Fields should include:
- close entry points
- whether producers can reserve capacity after close
- drain-on-close vs drop-on-close semantics
- lag reporting / dropped-update semantics
- receiver-drop consequences
- waiter cancellation behavior
- graceful-shutdown recipe references

### 6) `sync-adapter-profile/v0`
Describes wrappers, migrations, or bridges.

Fields should include:
- source/target primitive ids
- lossless / lossy / partial status
- changes in blocking posture
- changes in fairness/backpressure/shutdown semantics
- runtime / allocation / latency costs
- unsupported or caveated behaviors

### 7) `sync-vector-set/v0`
Golden vectors for synchronization behavior.

Fields should include:
- vector id
- fixture/setup description
- interleaving scenario class
- fairness expectation
- shutdown/close expectation
- lag/backpressure expectation
- cancellation expectation
- normal-test / loom / shuttle / model-check lane
- unsupported-case markers

### 8) `sync-check-report/v0`
Records what was actually exercised.

Fields should include:
- primitives / adapters checked
- vectors run / skipped
- pass/fail/partial status
- observed mismatches
- runtime / toolchain / OS details when relevant
- attached traces, minimized repros, loom runs, shuttle seeds, or benchmark notes

### 9) `sync-pack/v0`
Bundle of the above plus docs, migration notes, examples, and CI pointers.

## CLI shape
`cargo syncsurf` should be a thin orchestrator, not a new runtime.

Potential commands:
- `cargo syncsurf init` — scaffold synchronization-surface metadata
- `cargo syncsurf export` — emit profiles for selected primitives
- `cargo syncsurf check` — run vectors over chosen primitives/adapters
- `cargo syncsurf diff` — compare semantic changes across versions
- `cargo syncsurf pack` — bundle a `sync-pack/v0`

The tool should prefer references to source docs, tests, and existing concurrency-checking harnesses rather than giant generated snapshots.

## Initial targets
A first credible version should start where the seam is already undeniable:
1. **Blocking lock pilot**
   - `std::sync::Mutex` / `RwLock`
   - `parking_lot::Mutex` / `RwLock`
2. **Async lock pilot**
   - `tokio::sync::Mutex` / `RwLock`
   - explicit guard-across-`.await` posture
3. **Channel pilot**
   - `std::sync::mpsc::channel` and `sync_channel`
   - `tokio::sync::mpsc`, `watch`, and `broadcast`
   - `crossbeam-channel` and `flume` as ecosystem comparison lanes
4. **Signal/permit pilot**
   - `tokio::sync::Semaphore`, `Notify`, and `oneshot`
5. **Verification pilot**
   - one `loom` lane and one `shuttle` lane exercising a documented synchronization surface

The kit should support both **promotion** (this primitive family is suitable as shared infrastructure) and **honest restriction** (fairness unspecified; shutdown lossy; async-runtime-specific; verification limited).

## What good adoption looks like
A good v1 does not need to unify all concurrency in Rust.
It needs to prove that the ecosystem can publish honest synchronization truth.

Success would look like:
- one report that makes fairness, backpressure, and shutdown posture obvious;
- adapters revealing when a “drop-in replacement” changes poisoning, lag, or clean-shutdown semantics;
- verification vectors attached directly to primitive surfaces instead of living as hidden test lore;
- Atlas/domain guides that can recommend a queue/lock stack with real attached evidence;
- and fewer accidental design mistakes caused by choosing primitives from name similarity alone.

## Boundaries with other archive proposals
- **Async Lifecycle Kit** is about task structure, scopes, and cancellation choreography; Synchronization Surface Kit is about the semantics of the coordination primitives themselves.
- **Runtime Capability Kit** governs authority and least privilege, not fairness/backpressure/closure behavior.
- **Trait Surface Kit** and **Interop Commons Kit** may describe shared traits/adapters for sync primitives, but do not define the synchronization semantics themselves.
- **Validity Surface Kit** covers invalid values and boundary assumptions, not liveness/fairness/shutdown semantics.
- **Replay Kit** and **Formal Verification Kit** can attach stronger evidence, but Synchronization Surface Kit defines the contract they should be checking.

## Failure modes to avoid
- inventing one universal “channel metadata” format that erases broadcast, watch, semaphore, notify, and lock distinctions;
- pretending runtime-specific primitives are runtime-agnostic because wrappers exist;
- flattening fairness, throughput, and latency into one fake score;
- hiding shutdown and lag semantics behind casual language like “graceful” or “reliable”;
- or claiming verification coverage from one loom/shuttle example when large portions of the surface remain unexercised.
