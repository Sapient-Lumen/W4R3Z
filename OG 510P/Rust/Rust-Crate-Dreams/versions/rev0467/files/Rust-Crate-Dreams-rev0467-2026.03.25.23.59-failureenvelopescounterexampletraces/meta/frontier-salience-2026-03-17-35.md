# Frontier salience scan — 2026-03-17 (crate lifecycle surfaces promoted as the background-work / shutdown-truth lane)

This pass added a new top-level proposal: **P-0520 Crate Lifecycle Surface Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a twelfth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), **P-0516** (configuration/setup scenarios), **P-0517** (performance envelopes), **P-0518** (observability surfaces), and **P-0519** (authority surfaces).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another graceful-shutdown framework,
- another structured-concurrency experiment,
- another Tokio helper,
- another generic supervisor/runtime,
- or another docs-only async best-practices guide.

It is the boring crate that can hand other people:

- one **lifecycle pack**,
- one **background-work receipt**,
- one **cancellation-surface report**,
- one **shutdown-obligation report**,
- one **drain-recipe manifest**,
- one **race/retry-safety report**,
- one **lifecycle-check report**,
- and one **lifecycle diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0520 Crate Lifecycle Surface Pack Kit**
9. **P-0518 Crate Observability Surface Pack Kit**
10. **P-0519 Crate Authority Surface Pack Kit**
11. **P-0512 Crate Guidance Pack Kit**
12. **P-0513 Crate Runtime Handoff Pack Kit**
13. **P-0515 Crate Off-Ramp Pack Kit**
14. **P-0510 Crate Capability Contract & Interop Profile Kit**
15. **P-0511 Crate Interop Profile Pack Kit**
16. **P-0429 rustc_public Analysis Workbench Kit**

## Why P-0520 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, which makes lifecycle truth a plausible crate support surface rather than executor trivia.
- The 2025 survey says **docs and code** remain the main learning surfaces; lifecycle behavior hidden in examples or issue comments is therefore still too implicit.
- Tokio’s shutdown guide still frames graceful shutdown as a three-part discipline: decide when to stop, tell work to stop, and wait for it to stop.
- Tokio / tokio-util already expose enough lifecycle substrate (`CancellationToken`, `TaskTracker`, `JoinHandle`, `AbortHandle`, `AbortOnDropHandle`) that the missing value is now the support artifact rather than the primitive.
- Tokio’s docs explicitly distinguish cancellation-safe operations from partially-progressing or non-cancel-safe ones, which means lifecycle truth is already real but scattered.
- Existing crates like `async_shutdown`, `tokio-graceful-shutdown`, `task_scope`, and `moro` show demand for lifecycle help, but they still do not publish a stable downstream contract for one crate’s background work and shutdown obligations.

That means the lane is both:

- **timely** — because the runtime substrate is real enough to support a contract layer now,
- and **distinct** — because the missing value is a crate-authored lifecycle surface above primitives and below frameworks/platforms.

## What changed in the archive

Added:
- `proposals/crate-lifecycle-surface-pack-kit.md`
- `meta/crate-lifecycle-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-35.md`
- `fixtures/crate-lifecycle-surface-pack-kit/`
- `entries/2026-03-17-206.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- runtime failure handoff,
- observability,
- authority / ambient powers,
- setup scenarios,
- generic structured-concurrency substrate,
- graceful-shutdown orchestration,
- and receiver-facing lifecycle contracts

into one fake “async shutdown solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://tokio.rs/tokio/topics/shutdown
- https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
- https://docs.rs/tokio/latest/tokio/task/struct.AbortHandle.html
- https://docs.rs/tokio/latest/tokio/macro.select.html
- https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
- https://docs.rs/tokio-util/latest/tokio_util/task/index.html
- https://docs.rs/async-shutdown/latest/async_shutdown/
- https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
- https://docs.rs/task_scope/latest/task_scope/
- https://docs.rs/crate/moro/0.4.0
