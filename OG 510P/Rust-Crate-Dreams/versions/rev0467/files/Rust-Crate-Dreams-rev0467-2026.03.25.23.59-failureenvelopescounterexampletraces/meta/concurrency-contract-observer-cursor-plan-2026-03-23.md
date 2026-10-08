# Concurrency Contract Kit observer-cursor plan — 2026-03-23

This note sharpens **P-0538 Concurrency Contract Kit** around a new missing lane:
**observer cursor posture** and **observer progress isolation**.

## Main product judgment

A first useful implementation should not try to infer cursor topology from arbitrary code.
It should normalize strong documented cases where observers either keep independent progress state, share one competitive claim frontier, or make multi-observer cursor language inapplicable.

The point is to answer questions like:

- Does each observer advance its own cursor, or do all observers compete over one shared pool?
- If one observer falls behind, does it only hurt itself, or does it change what other observers/senders can do?
- Is the surface fundamentally single-consumer or wake-only, making cross-observer cursor language inapplicable?
- Is a lagging observer rebased locally, does it silently lose claim opportunities, or is that not the right model for the surface?

## New reports that now look worth shipping

### 1. `observer-cursor.report.json`
Purpose:
- answer what kind of cursor or progress frontier observers have.

Minimum fields:
- `surface`
- `cursor_class`
- `observer_cardinality`
- `cursor_owner`
- `progress_frontier`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `per_observer_seen_cursor`
- `per_observer_retained_history_cursor`
- `shared_competitive_claim_pool`
- `fixed_single_receiver_cursor`
- `wake_only_no_cursor`
- `manual_review_required`

### 2. `observer-progress-isolation.report.json`
Purpose:
- answer what one observer’s slowness or progress state does to others.

Minimum fields:
- `surface`
- `slow_observer_effect_class`
- `affects_other_observers`
- `affects_sender_progress`
- `local_recovery_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `observer_local_only`
- `self_lag_with_cursor_rebase`
- `shared_work_pool_competition`
- `single_receiver_only_not_multiobserver`
- `wake_only_not_data_progress`
- `manual_review_required`

## Why this belongs in P-0538 instead of a new queue or actor lane

The same ecosystems already used for audience / claim / order / join semantics expose the gap directly:

- Tokio `watch` gives each receiver independent seen-state tracking.
- Tokio `broadcast` gives each receiver its own retained-history cursor and a lag-rebase path when that receiver falls behind.
- Flume explicitly says cloned receivers are not broadcast; they compete for one shared work pool.
- `async-channel` documents the same one-of-many-consumers claim pool.
- Tokio `mpsc` makes multi-observer cursor language inapplicable because only one receiver exists.
- Tokio `Notify` is wake-only and carries no data, so cursor/posture language should not be overclaimed.

That is exactly the kind of receiver-facing truth the crate should export.

## MVP scenario pack

Prefer small proving grounds:

1. `watch_independent_seen_cursors`
2. `broadcast_per_receiver_cursor_and_self_lag_rebase`
3. `async_channel_shared_competitive_claim_pool`
4. `flume_cloned_receivers_shared_work_pool`
5. `mpsc_fixed_single_receiver_cursor`
6. `notify_wake_only_no_data_cursor`
7. `portable_bundle_keeps_cursor_and_progress_isolation_separate`

## Doctor checks to add

- reject “many receivers” as evidence of independent cursors when docs actually describe a shared claim pool;
- reject “single-delivery” as evidence that all observers share one lag/recovery fate;
- reject wake-only notification surfaces being treated like data cursors;
- reject single-consumer surfaces being forced into multi-observer isolation language.
