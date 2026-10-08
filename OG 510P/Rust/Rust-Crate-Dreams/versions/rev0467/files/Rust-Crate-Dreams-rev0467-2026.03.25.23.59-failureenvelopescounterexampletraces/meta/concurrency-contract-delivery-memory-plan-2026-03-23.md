# Concurrency Contract Kit delivery-memory / backlog-pressure plan — 2026-03-23

This note exists to make **P-0538 Concurrency Contract Kit** more implementation-ready.

The archive already had reentrancy, fairness, cancellation, recovery, context, locality, and liveness.
The next missing layer is now sharper: **what the surface remembers when nobody is ready** and **what happens under pressure**.

## Main product judgment

The first lovable version of this slice should not try to prove queue internals from code.
It should normalize strong public docs and explicit maintainer annotation into two new optional reports.

## 1. `delivery-memory.report.json`

Purpose:
- answer what kind of state survives between send/notify and later observation.

Minimum fields:
- `surface`
- `memory_class`
- `delivery_unit`
- `receiver_fanout`
- `accumulation_limit`
- `late_receiver_posture`
- `close_or_disconnect_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `no_memory_rendezvous`
- `single_coalesced_permit`
- `latest_value_only`
- `bounded_fifo_queue`
- `unbounded_fifo_queue`
- `per_receiver_bounded_broadcast_history`
- `manual_review_required`

Interpretation guidance:
- `single_coalesced_permit` means repeated wake-like signals collapse to at most one remembered permit.
- `latest_value_only` means receivers may observe only the newest value and intermediate history is not retained for later inspection.
- `per_receiver_bounded_broadcast_history` means each receiver has a cursor over bounded retained history and may lag out.
- `no_memory_rendezvous` means no buffered state exists at all; send/recv must pair.

## 2. `backlog-pressure.report.json`

Purpose:
- answer what happens when producers outrun consumers or available memory/history runs out.

Minimum fields:
- `surface`
- `pressure_class`
- `full_or_lag_trigger`
- `producer_effect`
- `consumer_effect`
- `loss_or_skip_posture`
- `growth_risk`
- `signal_visibility`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `backpressure_wait`
- `overwrite_oldest_with_lag_signal`
- `drop_intermediate_history`
- `unbounded_growth_risk`
- `rendezvous_pairing_required`
- `manual_review_required`

Interpretation guidance:
- `backpressure_wait` means producers wait or reserve capacity rather than overwrite retained history.
- `overwrite_oldest_with_lag_signal` means retained history is bounded and lagging consumers may lose older items with an explicit signal.
- `drop_intermediate_history` fits latest-value watch semantics where the newest state wins and earlier values are not guaranteed observable.
- `unbounded_growth_risk` is not a claim of safety; it is a claim that pressure moves to memory growth instead of bounded overwrite/block behavior.

## Why these reports belong in P-0538

These are receiver-facing concurrency truths, not merely channel implementation trivia.
A user choosing between `Notify`, `watch`, `broadcast`, bounded `mpsc`, `async-channel`, or rendezvous channels is often really choosing between:

- coalesced wake memory,
- state snapshot memory,
- queued work memory,
- bounded fanout history,
- or no memory at all.

The support contract should say that explicitly.

## What the crate should give other people

A useful `0.1` should let another engineer answer:

1. If I send now and no one is ready, what is remembered?
2. Can repeated sends/wakes accumulate, coalesce, overwrite, or pair only by rendezvous?
3. If the consumer falls behind, do we block, drop, overwrite, or grow?
4. Does the consumer learn that loss happened, or is history simply absent?
5. Is this single-delivery, latest-state, or fanout history?

## Suggested MVP scenario pack

- Tokio `Notify` single stored permit / `notify_waiters` no-future-memory split
- Tokio `watch` latest-value-only with seen/unseen tracking
- Tokio `broadcast` bounded history with lag detection
- Tokio bounded `mpsc` FIFO backpressure without overwrite semantics
- `async-channel` bounded vs unbounded single-delivery MPMC posture
- `crossbeam-channel` zero-capacity rendezvous posture

## Guardrail

Do not let future revisions flatten these into a fake “channel semantics” summary.
The whole point is to keep **memory class**, **pressure class**, **fairness**, **cancellation**, and **context legality** separately reviewable.
