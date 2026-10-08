# Concurrency Contract Kit scenario-lab plan — 2026-03-23

This note sharpens **P-0538 Concurrency Contract Kit** around one missing implementation question:

> if we wanted a lovable `0.1`, what should other people actually receive besides schemas and classification words?

## Main product judgment

The next missing layer is a **scenario lab**.

`0.1` should not try to auto-discover arbitrary semantics from code.
It should instead ship a small, high-trust pack of scenario bundles that make the vocabulary believable.

That means:
- few scenarios,
- strong documentation basis,
- explicit claim ceilings,
- portable example artifacts,
- and diffs that show what changed between versions or runtime families.

## Why this is worth repo space now

Three current signals make this more urgent:

1. the March 2026 Rust challenges post says async remains a consistent pain point,
2. Rust’s 2026 flagships still keep **Just Add Async** near the front of long-term language evolution,
3. the safety-critical Rust write-up explicitly says teams need concrete requirements for a safety-case-friendly async runtime.

So a crate that publishes **honest concurrency support bundles** is still addressing real ecosystem pain.

## What `0.1` should ship

### Crate split

- `concurrency-contract-core`
  - schema types
  - enums and shared vocabulary
  - diff helpers

- `concurrency-contract-import`
  - docs/annotation import helpers
  - source-basis tagging
  - runtime-family adapters where the docs are explicit enough

- `concurrency-contract-scenarios`
  - scenario manifests
  - fixture loaders
  - portable example bundles
  - doctor assertions

- `cargo-concurrency-contract`
  - CLI for inspect / check / doctor / diff / bundle / scenario workflows

## The six proving-ground scenario families

### 1. Wake-only / stored-permit scenario

Purpose:
- keep **wake semantics** separate from payload delivery.

Initial candidates:
- Tokio `Notify::notified`
- Tokio `Notify::notify_one`
- Tokio `Notify::notify_waiters`

Bundle must answer:
- whether a permit can be stored,
- whether multiple notifications coalesce,
- whether future waiters are included,
- and whether any payload or receipt evidence exists.

### 2. Latest-value state scenario

Purpose:
- keep **shared latest snapshot** separate from queues and fanout.

Initial candidate:
- Tokio `watch`

Bundle must answer:
- whether new subscribers begin with a current snapshot,
- whether intermediate states can disappear silently,
- how per-receiver seen-state behaves,
- and what close still leaves observable.

### 3. Bounded work queue scenario

Purpose:
- keep **single-consumer FIFO + backpressure** separate from latest-value or fanout stories.

Initial candidates:
- Tokio bounded `mpsc`
- `async-channel` bounded mode
- Flume bounded mode

Bundle must answer:
- what a successful send means,
- whether producers backpressure or fail,
- what close leaves in the tail,
- and whether cancellation loses queue position.

### 4. Lagging fanout scenario

Purpose:
- keep **per-receiver history and lag** separate from broadcast folklore.

Initial candidate:
- Tokio `broadcast`

Bundle must answer:
- whether each receiver gets its own cursor,
- what happens when a receiver lags,
- whether skipped items are counted,
- and whether `send` proves observation or only active audience at that moment.

### 5. Local-only execution scenario

Purpose:
- keep **local spawn legality**, **thread affinity**, and **driver-liveness** together in one believable fixture family.

Initial candidates:
- Tokio `spawn_local`
- Tokio `LocalSet`
- Tokio current-thread `Handle::block_on`
- `async_executor::LocalExecutor`
- glommio `spawn_local`

Bundle must answer:
- whether tasks are movable,
- whether a local context is mandatory,
- what actually drives progress,
- and what handles exist without full driver guarantees.

### 6. Sync recovery posture scenario

Purpose:
- show that the crate is not only about async channels.

Initial candidates:
- `std::sync::Mutex`
- `std::sync::RwLock`
- `parking_lot::Mutex`
- nightly `std::sync::nonpoison::Mutex`

Bundle must answer:
- poisoning or advisory-poisoning posture,
- recovery route,
- and what claim ceiling applies when nightly features are involved.

## Recommended scenario directory shape

Each scenario should ship:

- `README.md`
- `scenario.contract.toml`
- one or more `*.report.example.json`
- `scenario-bundle.manifest.example.json`
- `doctor-assertions.md`
- `sources.md`

That keeps every scenario both human-readable and machine-usable.

## CLI that now looks worth shipping

- `cargo concurrency-contract scenario list`
- `cargo concurrency-contract scenario check <path>`
- `cargo concurrency-contract scenario diff old/ new/`
- `cargo concurrency-contract scenario bundle <path>`
- `cargo concurrency-contract doctor --scenario <name>`

The scenario layer is important because many errors here are classification failures, not parser failures.
For example:
- stored permit presented as a queue,
- active receiver count presented as processing receipt,
- local spawn support presented as general runtime portability,
- or no-poisoning presented as fairness.

## What the crate should provide other people

After this pass, a worthy `0.1` should let another engineer receive:

1. one small bundle that explains one concurrency surface without folklore,
2. one diff between two versions / runtimes / feature sets,
3. one issue attachment maintainers can inspect without replaying the exact app,
4. one support artifact that separates delivery, cancellation, locality, liveness, and recovery,
5. one educational fixture pack that teaches honest distinctions rather than cargo-cult choices.

## Guardrails

- Do not turn this into a benchmark suite.
- Do not pretend to prove semantics from implementation internals in `0.1`.
- Do not collapse runtime-family choice into concurrency-contract scope.
- Do not collapse delivery semantics, execution locality, and shutdown behavior into one fake “async-safe” badge.
- Do not treat one runtime’s docs as a universal concurrency ontology.

## Follow-on after `0.1`

Only after the six scenario families are boring should the crate expand toward:
- more runtime adapters,
- generated support dashboards,
- version-window comparisons across crate releases,
- or imported evidence for safety-case-friendly async runtime profiles.

## Sources

- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
