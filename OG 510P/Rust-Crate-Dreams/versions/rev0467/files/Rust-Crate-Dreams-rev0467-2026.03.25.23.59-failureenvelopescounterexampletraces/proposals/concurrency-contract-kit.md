---
id: P-0538
title: Concurrency Contract Kit — reentrancy scopes, progress/fairness classes, wait-cancellation reports, and execution-context boundaries
status: idea
domains: [async, sync, concurrency, dx, correctness, docs, services, gui, libraries, embedded]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/02/11/2025-Rust-Debugging-Survey/
  - https://users.rust-lang.org/t/what-is-missing-lacking-in-the-rust-ecosystem/117157?page=3
  - https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html
  - https://docs.rs/tokio/latest/tokio/sync/struct.RwLock.html
  - https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html
  - https://docs.rs/tokio/latest/tokio/sync/struct.Notify.html
  - https://docs.rs/tokio/latest/tokio/sync/futures/struct.Notified.html
  - https://docs.rs/tokio/latest/tokio/sync/watch/struct.Receiver.html
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Receiver.html
  - https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.channel.html
  - https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html
  - https://docs.rs/tokio/latest/tokio/sync/broadcast/struct.Sender.html
  - https://docs.rs/tokio/latest/tokio/sync/watch/struct.Sender.html
  - https://docs.rs/tokio/latest/tokio/sync/oneshot/index.html
  - https://docs.rs/tokio/latest/tokio/sync/oneshot/struct.Sender.html
  - https://docs.rs/flume/latest/flume/struct.Sender.html
  - https://docs.rs/async-channel/latest/async_channel/
  - https://docs.rs/crossbeam/latest/crossbeam/channel/fn.bounded.html
  - https://docs.rs/tokio/latest/tokio/macro.select.html
  - https://docs.rs/parking_lot/latest/parking_lot/
  - https://docs.rs/parking_lot/latest/parking_lot/type.Mutex.html
  - https://doc.rust-lang.org/std/sync/struct.Mutex.html
  - https://doc.rust-lang.org/src/std/sync/poison/mutex.rs.html
  - https://doc.rust-lang.org/beta/std/sync/nonpoison/struct.Mutex.html
  - https://doc.rust-lang.org/std/sync/struct.ReentrantLock.html
  - https://docs.rs/tokio/latest/tokio/task/fn.spawn_local.html
  - https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html
  - https://docs.rs/tokio/latest/tokio/runtime/struct.Handle.html
  - https://docs.rs/tokio/latest/tokio/runtime/struct.LocalRuntime.html
  - https://docs.rs/async-executor/latest/async_executor/struct.LocalExecutor.html
  - https://docs.rs/glommio/latest/glommio/
  - https://docs.rs/glommio/latest/glommio/fn.spawn_local.html
  - https://docs.rs/async_executors/latest/async_executors/
  - https://docs.rs/executor-core/latest/executor_core/
---

# Problem

Rust does not lack concurrency primitives.
It lacks a **portable, receiver-facing way to describe what those primitives promise**.

That gap matters more than it used to.

Fresh official signals say advanced Rust users still struggle with async/concurrency complexity.
Community discussion now explicitly asks for better documentation around **forward progress guarantees** and **reentrancy**, while also naming cancellation safety and observability as missing areas.
At the same time, the current ecosystem exposes crucial semantics in fragmented, crate-specific language:

- Tokio `Mutex` documents FIFO lock distribution and queue-place loss on cancellation.
- Tokio `RwLock` documents fairness, cancellation caveats, and blocking methods that panic in async contexts.
- Tokio `Semaphore` documents fair permit distribution and queue-place loss on cancellation.
- `tokio::select!` documents cancellation safety lane by lane rather than as a single runtime-wide truth.
- `parking_lot` documents eventual fairness, reentrant mutexes, and no-poisoning semantics.
- `std::sync::Mutex` documents blocking and poisoning.
- `std::sync::ReentrantLock` exists only as a nightly experimental API.

All of that is useful.
But none of it gives another engineer one compact answer to questions like:

- “Can I re-enter this surface from the same callback path?”
- “Is starvation possible here, or is ordering actually FIFO?”
- “If this waiter is cancelled, what state does it lose?”
- “If no receiver is ready now, does this remember one wake, the latest value, a bounded backlog, or nothing at all?”
- “When producers outrun consumers, does it block, overwrite, drop intermediate history, or require rendezvous?”
- “Will this block, panic, or deadlock in an async execution context?”
- “How much of that is a strong documented promise versus a manual-review ceiling?”

The missing crate is **not** another mutex or semaphore.
It is a **Concurrency Contract Kit** that helps other crates publish reviewable receipts and reports about those semantics.

# What it provides

Core artifacts:

- `concurrency-contract.toml` — declared surfaces, imported authority, support scope, and scenario tags.
- `reentrancy-scope.report.json` — whether a surface is non-reentrant, same-thread reentrant, same-task reentrant, callback-reentrant, or manual-review-only.
- `progress-fairness.report.json` — ordering / fairness / starvation / preference class, such as `fifo`, `eventual_fairness`, `writer_priority`, `unspecified`, or `manual_review_required`.
- `wait-cancellation.report.json` — what happens when a queued waiter is cancelled, dropped, or timed out; whether queue membership is lost; whether any message/value/seen state was consumed; whether stored permits or wake registrations matter; and whether partial state changes are possible.
- `execution-context-boundary.report.json` — which contexts are allowed or forbidden, such as `async_task`, `blocking_thread`, `runtime_entered`, `signal_handler`, `callback_reentry`, or `manual_review_required`, plus block/panic/deadlock caveats.
- optional `mobility-affinity.report.json` — whether work is movable across threads, same-thread local only, local-context required, runtime-thread-bound, CPU-pinned local, or manual-review-only.
- optional `driver-liveness.report.json` — what must actively keep running for progress to happen, such as background runtime workers, explicit `run` / `tick` / `run_until`, `Runtime::block_on`, `LocalSet` driving, or manual-review-only posture.
- optional `failure-recovery.report.json` — poisoning, advisory poisoning, no-poisoning, experimental non-poisoning, wake-after-close, recovery hooks, or out-of-scope posture.
- optional `delivery-memory.report.json` — what a surface remembers when nobody is ready: none, one coalesced wake, latest value only, bounded FIFO queue, unbounded FIFO queue, or bounded per-receiver broadcast history.
- optional `backlog-pressure.report.json` — what happens under pressure: wait for capacity, overwrite oldest with lag signal, drop intermediate history, risk unbounded growth, or require rendezvous.
- optional `delivery-acceptance.report.json` — what producer-visible success means: wake/permit recorded, endpoint open, queue admission, latest-state replacement, active receivers existed, or manual-review-only.
- optional `observation-evidence.report.json` — what evidence exists later: none, closure-only signal, receiver-count hint, receiver-local state only, explicit application-level ack required, or manual-review-only.
- optional `late-joiner-admission.report.json` — whether new observers may join after creation via subscribe, resubscribe, future creation, or not at all, and what preconditions apply.
- optional `join-start.report.json` — what a newly admitted observer starts with: future-only visibility, current snapshot already seen, current tail baseline, one stored permit, or not-applicable fixed-cohort posture.
- optional `observer-cursor.report.json` — whether observers each maintain local seen-state, keep per-receiver retained-history cursors, compete for a shared claim pool, rely on one fixed single-receiver cursor, or have no data cursor at all.
- optional `observer-progress-isolation.report.json` — whether a slow observer only hurts itself, self-lags with cursor rebase, competes for shared work, or makes multi-observer progress language inapplicable.
- `concurrency-support-bundle.manifest.json` — portable bundle joining the above artifacts for code review, issue triage, docs exports, and release diffs.
- optional `notes.md` — concise human-readable support note for docs, PRs, or incident playbooks.

CLI surface:

- `cargo concurrency-contract init`
- `cargo concurrency-contract inspect`
- `cargo concurrency-contract check`
- `cargo concurrency-contract bundle`
- `cargo concurrency-contract diff <old> <new>`

# What the crate should provide other people

1. **One reentrancy answer** instead of folklore.
2. **One progress/fairness answer** instead of vague “should be fine under load.”
3. **One wait-cancellation answer** instead of silent queue-position loss or state-consumption surprises.
4. **One recovery answer** instead of leaving poisoning or no-poisoning buried in prose.
5. **One execution-context answer** instead of hidden block/panic/deadlock traps.
6. **One locality / mobility answer** instead of folklore about `!Send`, thread-affinity, or local-only spawn.
7. **One driver-liveness answer** instead of assuming a spawn handle or runtime handle is enough to make timers, I/O, or local tasks progress.
8. **One delivery-memory answer** instead of flattening coalesced wakes, latest-value watches, queues, broadcast history, and rendezvous channels into one fake “channel” story.
9. **One backlog-pressure answer** instead of silent overwrite, hidden unbounded growth, or accidental lag-loss surprises.
10. **One delivery-audience answer** instead of guessing whether one waiter, one receiver, all active receivers, or each receiver’s latest-state cursor is actually in scope for the same event/value.
11. **One consumption-claim answer** instead of silently blurring exclusive claim, clone fanout, independent seen-state tracking, and single-use transfer.
12. **One delivery-acceptance answer** instead of guessing what `Ok` from `send` or `notify` actually certified.
13. **One observation-evidence answer** instead of confusing close signals, receiver counts, or local seen-state with true receipt proof.
14. **One late-joiner-admission answer** instead of guessing whether new observers may still enter after the surface already exists.
15. **One join-start answer** instead of flattening future-only subscribe, current-snapshot subscribe, current-tail resubscribe, stored-permit wake start, and fixed-cohort no-join posture into one fake “subscribe” story.
16. **One observer-cursor answer** instead of guessing whether observers keep their own progress state or compete over one shared frontier.
17. **One observer-progress-isolation answer** instead of flattening self-local lag, shared work-pool competition, fixed single-consumer posture, and wake-only notification into one fake “multi-observer progress” story.
18. **One delivery-order answer** instead of flattening FIFO queues, per-receiver broadcast order, latest-state watches, coalesced wakes, and selection-level random choice into one fake “ordered channel” story.
19. **One gap-visibility answer** instead of guessing whether missed or collapsed units are counted, cursor-rebased, or silently lost.
20. **One closure-finality answer** instead of flattening immediate terminal shutdown, drain-then-terminal closure, reopenable closed intervals, and close/send races into one fake “closed” story.
21. **One post-close-availability answer** instead of guessing whether buffered tail, retained history, latest snapshot, or an in-flight one-shot value remains observable.
22. **One claim ceiling** that says when docs are strong enough and when manual review is still required.
23. **One portable artifact bundle** another engineer can inspect without reproducing the exact runtime or test setup.
24. **One shared vocabulary** importable by channel, runtime, resource, docs, and debugging support crates.

# Persona / who it’s for

- maintainers of async or sync primitives
- library authors exposing locks, semaphores, worker gates, callback registries, or waitable handles
- service teams reviewing cancellation safety and starvation risk
- GUI or game-loop teams mixing async and blocking code paths
- embedded / systems teams that need execution-context honesty
- docs/support/tool authors who want stable, machine-readable semantics instead of scraping prose

# Users & user stories

- **Runtime adapter maintainer**: “Export whether this surface is FIFO, writer-preferred, or unspecified without pretending I own the underlying runtime.”
- **Service engineer**: “Attach one bundle proving which waiters lose queue position when cancelled and which calls are safe inside `select!` races.”
- **Library adopter**: “See whether recursive callback entry is supported, forbidden, or only safe with manual review.”
- **Support engineer**: “Answer whether an async deadlock report is really a context-boundary violation, a non-reentrancy issue, or a fairness/starvation misunderstanding.”
- **Docs author**: “Render a compact matrix of reentrancy, cancellation, and execution-context guarantees for several primitives without inventing new wording each time.”

# Prior art (and why it’s insufficient)

- **Tokio docs** provide critical facts, but they do so primitive by primitive and method by method.
- **`parking_lot` docs** expose meaningful semantics, but not in a vocabulary directly comparable to Tokio or `std`.
- **`std` docs** document blocking, poisoning, and experimental reentrant locking, but not a portable support-bundle layer.
- **Deadlock detectors** and **model checkers** help find bugs, but they do not export the receiver-facing contract vocabulary a maintainer should publish.
- **General async tutorials** help explain patterns, but they are not machine-readable support artifacts.
- **Executor abstraction crates** make it easier to write runtime-agnostic code, but they do not publish receiver-facing receipts about locality, affinity, or driver-liveness.

What remains missing is a crate that lets maintainers:

- declare concurrency support surfaces,
- verify them against fixtures,
- export receipts and reports,
- and diff those claims over time.

# Design goals

1. **Receiver-facing truth first** — optimize for adopters and reviewers, not only implementors.
2. **Keep the semantic axes separate** — reentrancy, fairness/progress, wait-cancellation, recovery posture, and execution-context boundaries are not interchangeable.
3. **Runtime- and primitive-neutral vocabulary** — support `std`, Tokio, `parking_lot`, and future ecosystems without flattening them.
4. **Keep legality, locality, and liveness separate** — being callable, being thread-affine, and being actively driven are different claims.
5. **Memory-honest** — coalesced wakes, latest-state channels, queued work, bounded broadcast history, and rendezvous delivery are different claims.
6. **Audience-honest** — one waiter, one receiver, all active receivers, and per-receiver latest-state observers are different claims.
7. **Claim-honest** — exclusive message claim, clone-per-receiver fanout, non-consuming wake, and independent seen-state tracking are different claims.
8. **Acceptance-honest** — producer-visible success is not the same thing as downstream observation or processing.
9. **Evidence-honest** — close signals, receiver counts, and receiver-local seen bits are weaker than true receipt proofs.
10. **Closure-honest** — closed, drained, terminal, reopenable, and empty are different claims.
11. **Join-horizon-honest** — future-only subscribe, current-snapshot subscribe, current-tail resubscribe, stored-permit late waits, and fixed-cohort no-join posture are different claims.
12. **Artifact-first** — small receipts and reports before dashboards.
13. **Conservative by default** — use `manual_review_required` when claims are partial.
14. **Import-friendly** — reuse existing docs/tests/fixtures where possible rather than forcing maintainers to restate everything by hand.
15. **Diffable over time** — release reviewers should be able to spot changed guarantees.

# MVP surface

Minimal types:
- `ConcurrencyContract`
- `ReentrancyScopeReport`
- `ProgressFairnessReport`
- `WaitCancellationReport`
- `ExecutionContextBoundaryReport`
- optional `MobilityAffinityReport`
- optional `DriverLivenessReport`
- optional `FailureRecoveryReport`
- optional `DeliveryMemoryReport`
- optional `BacklogPressureReport`
- optional `DeliveryAudienceReport`
- optional `ConsumptionClaimReport`
- optional `DeliveryAcceptanceReport`
- optional `ObservationEvidenceReport`
- optional `LateJoinerAdmissionReport`
- optional `JoinStartReport`
- optional `DeliveryOrderReport`
- optional `GapVisibilityReport`
- optional `ClosureFinalityReport`
- optional `PostCloseAvailabilityReport`
- `ConcurrencySupportBundleManifest`

Minimal functions:
- `inspect_reentrancy_scope()`
- `inspect_progress_fairness()`
- `inspect_wait_cancellation()`
- `inspect_execution_context_boundaries()`
- `inspect_mobility_affinity()`
- `inspect_driver_liveness()`
- `inspect_failure_recovery()`
- `inspect_delivery_memory()`
- `inspect_backlog_pressure()`
- `inspect_delivery_audience()`
- `inspect_consumption_claim()`
- `inspect_delivery_acceptance()`
- `inspect_observation_evidence()`
- `inspect_late_joiner_admission()`
- `inspect_join_start()`
- `inspect_delivery_order()`
- `inspect_gap_visibility()`
- `inspect_closure_finality()`
- `inspect_post_close_availability()`
- `write_bundle()`
- `diff_bundle()`

Feature flags:
- `tokio-import`
- `parking-lot-import`
- `std-import`
- `async-executor-import`
- `glommio-import`
- `serde`
- `bundle`
- `loom-fixtures`

# Compatibility story

- Starts as a metadata / receipt layer above existing crates rather than replacing them.
- Can import facts from docs, fixtures, and maintained annotations.
- Can support sync and async crates at the same time.
- Leaves room for no-std or embedded-specific adapters later, even if the first substrate is `std` / Tokio / `parking_lot` heavy.
- Treats undocumented or conditional behavior as partial support, not silent success.

# Conformance & fixtures

The fixture pack should freeze at least these scenarios:

- FIFO async mutex semantics that are **not** reentrancy claims.
- Eventual fairness that is **not** the same thing as Tokio FIFO ordering.
- Queue withdrawal under cancellation that is **not** the same thing as message loss.
- Truly cancel-safe receive paths that preserve seen-state or message availability.
- Blocking methods that are legal on a blocking thread but panic or deadlock in an async context.
- Local spawn surfaces that are **not** the same thing as movable work or background-driven progress.
- Handles that can block or spawn but do **not** drive local tasks, timers, or I/O.
- Poisoning, advisory recovery, and explicit no-poisoning posture.
- Coalesced wake memory that is **not** a queue.
- Latest-value-only state that is **not** per-send history.
- Bounded broadcast history with lag signaling that is **not** no-loss fanout.
- One-waiter notification, all-current-waiter notification, all-active-receiver fanout, exclusive single-receiver claim, and independent seen-state observation as distinct audience/claim classes.
- Send `Ok` that only proves the endpoint was still open, not eventual receipt.
- Returned receiver counts that are hints about active audience, not observation receipts.
- Successful watch send that updates latest shared state while failed send seeds no future receivers.
- One-shot send that stores a value while exporting only close notifications to the sender.
- Future-only broadcast subscribe that is not current-snapshot subscribe.
- Resubscribe-from-tail that is not replay-from-origin or inherited receiver backlog.
- Current-snapshot watch subscribe that is not future-only subscription.
- Stored-permit `Notify` wake memory that is not current-waiters-only `notify_waiters` behavior.
- Fixed-cohort `mpsc` / `oneshot` surfaces that are not late-join-capable subscriptions.
- Wake/permit acceptance that is not payload receipt.
- FIFO single-consumer queue order that is **not** per-receiver broadcast order.
- Per-receiver broadcast FIFO plus counted skipped-message signals.
- Latest-snapshot visibility that is **not** per-send history.
- Coalesced wake semantics that are **not** counted sequence delivery.
- Ready-operation random choice that is **not** underlying channel FIFO.
- Cloned receivers that still compete for single delivery.
- Receiver-side close that is **not** the same thing as immediate emptiness.
- Sender-disconnect closure that still leaves buffered tail to drain.
- Closed watch state that is **not** the same thing as permanently terminal.
- One-shot close that blocks future sends without proving the slot is empty.
- Zero-capacity rendezvous channels that are **not** buffered queues.
- Portable bundles that keep reentrancy, progress, cancellation, recovery, context, locality, liveness, delivery memory, pressure, audience, claim, acceptance, observation-evidence, delivery-order, and gap-visibility semantics separate.

# Path to boring stability

- Stabilize the four core reports plus optional recovery, delivery-memory, backlog-pressure, delivery-audience, consumption-claim, delivery-acceptance, observation-evidence, late-joiner-admission, join-start, and bundle-manifest reports before adding many import adapters.
- Start with well-documented substrate (`std`, Tokio, `parking_lot`) before chasing broad ecosystem coverage.
- Keep failure/recovery and poison/no-poison imports optional at first.
- Favor explicit scenario fixtures over inferred “smart” verdicts.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A cargo subcommand and library that produce one `reentrancy-scope`, one `progress-fairness`, one `wait-cancellation`, one `execution-context-boundary`, and, when relevant, one `mobility-affinity`, one `driver-liveness`, one `failure-recovery`, one `delivery-memory`, one `backlog-pressure`, one `delivery-audience`, one `consumption-claim`, one `delivery-acceptance`, one `observation-evidence`, one `late-joiner-admission`, and one `join-start` report for a small set of well-documented primitives, then package them into one portable bundle.

# De-risk plan

1. Start with exportable reports, not automatic semantic inference.
2. Import only claims with strong public documentation or explicit maintainer annotation.
3. Keep “manual review required” cheap and visible.
4. Add ecosystem adapters only after the core reports and recovery vocabulary feel stable.

# Non-goals

- Not a replacement for mutex / channel / semaphore implementations.
- Not a universal async runtime abstraction.
- Not a deadlock prover or model checker.
- Not a full observability stack.
- Not a generic docs renderer without artifact output.
