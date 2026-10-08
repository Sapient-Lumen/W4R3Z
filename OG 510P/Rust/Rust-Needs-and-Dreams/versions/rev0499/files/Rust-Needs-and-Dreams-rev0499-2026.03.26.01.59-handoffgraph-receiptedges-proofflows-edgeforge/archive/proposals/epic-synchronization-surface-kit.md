# Epic proposal: Synchronization Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for synchronization surfaces**.

Rust has plenty of strong primitives already. What it lacks is a reviewable way to state what those primitives mean in practice: blocking versus async posture, fairness, poisoning, backpressure, retention, lag/drop behavior, close/drain semantics, cancellation behavior, and what evidence actually backs those claims.

In other words: Rust needs a boring, explicit `sync-pack/v0` more than it needs one more crate claiming to be a faster queue or nicer mutex.

## Why now
The timing is unusually good:
- Rust’s 2026 flagships say patterns that work in sync Rust should work in async Rust, which makes the seam between blocking and async coordination a first-class design problem;
- the 2025 async goals framed parity work as necessary for real async-library evolution;
- Tokio’s docs now actively teach people when std locks are often preferable in async code, which is direct evidence that “async primitive” versus “blocking primitive” is not a trivial naming question;
- Tokio’s own sync module centers message passing, while its primitives expose explicit fairness and shutdown semantics;
- the safety-critical vision work says async choices pull in runtime and scheduling assumptions that must be explainable and evidenced;
- and the ecosystem already has strong point tools (`parking_lot`, `crossbeam-channel`, `flume`, `loom`, `shuttle`) but no shared artifact family above them.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- https://docs.rs/tokio/latest/tokio/sync/index.html
- https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://docs.rs/parking_lot
- https://docs.rs/crossbeam-channel
- https://docs.rs/flume
- https://docs.rs/loom
- https://docs.rs/shuttle

## What should be built
A first credible version should ship:
1. `sync-surface/v0`, `lock-profile/v0`, `channel-profile/v0`, `signal-permit-profile/v0`, `shutdown-cancel-profile/v0`, `sync-adapter-profile/v0`, `sync-vector-set/v0`, `sync-check-report/v0`, and `sync-pack/v0`
2. one blocking-lock pilot comparing std and `parking_lot`
3. one async-lock pilot comparing Tokio lock semantics and the “use std mutex unless you need `.await` across the guard” story
4. one channel pilot spanning bounded/unbounded/std/Tokio/latest-value/broadcast distinctions
5. one signal/permit pilot for `Notify`, `Semaphore`, and oneshot semantics
6. one verification pilot attaching `loom` and `shuttle` evidence to a documented surface
7. docs and CI that make fairness, backpressure, shutdown, and runtime assumptions explicit

The winning version is small, semantic, and evidence-friendly.
It should make synchronization truth legible together rather than canonizing one runtime or one primitive family.

## Initial pilots
- **Lock lane** — std, `parking_lot`, and Tokio lock surfaces compared honestly
- **Queue lane** — std `mpsc`, Tokio `mpsc`, `watch`, `broadcast`, and ecosystem alternatives with explicit topology/backpressure semantics
- **Signal lane** — semaphore, notify, and oneshot surfaces treated as their own family rather than fake queues
- **Verification lane** — interleaving/shutdown/cancellation vectors backed by loom/shuttle where appropriate
- **Mixed-mode lane** — explicit adapter truth for sync↔async producers/consumers and bridge wrappers

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document synchronization vocabulary for locks, channels, signals, shutdown, and verification
2. **v0.2 lock and channel pilots**
   - ship fairness/backpressure/shutdown vectors for at least one blocking and one async family
3. **v0.3 signal + mixed-mode adapters**
   - add semaphore/notify/oneshot profiles and sync↔async adapter truth
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical implementation strategy

## Success metrics
- Users can compare coordination primitives by semantics, not crate popularity alone.
- “Drop-in replacement” claims become reviewable because fairness, poisoning, lag, and closure behavior are explicit.
- Shutdown and backpressure bugs become easier to catch before production because they have named vectors and attached evidence.
- Safety-/ops-facing teams can explain runtime and synchronization assumptions without reconstructing them from source code.
- Rust gets closer to real sync/async parity because the semantic differences stop hiding in doc prose.

## Archive fit
This proposal fills a real missing seam in the archive.

The repo already covers task lifecycle, replay, traits, pointers, validity, and interop, but it does not yet have a first-class contract for **the semantics of the coordination primitives themselves**.

Synchronization Surface Kit is the missing substrate for a part of Rust that is both widely used and still unusually easy to misunderstand.
