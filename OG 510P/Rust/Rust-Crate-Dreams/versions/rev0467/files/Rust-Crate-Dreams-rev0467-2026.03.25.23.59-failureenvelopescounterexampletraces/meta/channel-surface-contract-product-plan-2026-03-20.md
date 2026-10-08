# Channel Surface Contract Kit — product plan (2026-03-20)

This note sharpens **P-0529 Channel Surface Contract Kit** into an implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0529** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace channel crates, prove queue correctness, or standardize every possible stream primitive.
It should provide one boring, reviewable contract layer above today’s channel families.

`0.1` should make four things first-class:

1. **capacity posture** — bounded, unbounded, zero-capacity, latest-only, overwrite ring, or priority queue;
2. **overflow policy** — wait, reject, drop, lag, or retain-latest behavior;
3. **delivery obligation** — what a successful send actually means and who can observe it;
4. **shutdown / drain truth** — what close/drop does to buffered work and what clean shutdown recipe is supported.

## What `0.1` should provide other people

- one compact `capacity-posture.receipt.json`
- one compact `overflow-policy.receipt.json`
- one compact `delivery-obligation.report.json`
- one compact `shutdown-drain.receipt.json`
- one rendered `channel-surface.summary.md`
- a diff command for release reviewers

## Commands worth shipping first

- `cargo channel-surface init`
- `cargo channel-surface observe`
- `cargo channel-surface check`
- `cargo channel-surface doctor`
- `cargo channel-surface summary`
- `cargo channel-surface diff <old> <new>`
- `cargo channel-surface pack`

## What to import, not reinvent

- Tokio channel semantics
- `futures::channel::mpsc`
- `async-channel`
- `crossbeam-channel`
- `flume`
- `embassy-sync`
- existing domain wrappers that already make additional policy choices

## Suggested `0.1` doctor warnings

- `bounded_without_full_policy`
- `send_success_meaning_missing`
- `latest_only_presented_as_event_history`
- `broadcast_lag_signal_missing`
- `shutdown_recipe_missing`
- `priority_or_non_fifo_behavior_missing`
- `close_signal_or_interest_signal_missing`

## First proving-ground scenarios

1. **Tokio bounded mpsc backpressure + close-then-drain**
2. **Tokio broadcast lagging receivers**
3. **Tokio watch latest-state semantics**
4. **Crossbeam zero-capacity rendezvous**
5. **Embassy priority reordering**
6. **Drop-oldest ring channel without backpressure**

## What to leave for later

- formal proofs of fairness or starvation bounds
- end-to-end telemetry / queue dashboards
- actor-model policy layers
- auto-benchmarking or auto-tuning
- aggressive semantic unification that hides ambiguity
- a full cancellation-safety and permit-queue lane (valuable, but still optional for `0.1`)
