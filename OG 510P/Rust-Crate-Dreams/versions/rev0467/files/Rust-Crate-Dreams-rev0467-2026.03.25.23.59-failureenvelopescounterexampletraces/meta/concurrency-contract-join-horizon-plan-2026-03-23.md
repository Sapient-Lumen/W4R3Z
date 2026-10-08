# Concurrency Contract Kit join-horizon plan — 2026-03-23

This note sharpens **P-0538 Concurrency Contract Kit** around a new missing lane:
**late-joiner admission** and **join-start baseline**.

## Main product judgment

A first useful implementation should not try to infer join semantics from arbitrary code.
It should normalize strong documented cases where a new observer may or may not join after surface creation and what that observer starts with.

The point is to answer questions like:

- Can a new receiver or waiter join after the surface already exists?
- If yes, does it start with future sends only, the current snapshot, the current tail, one stored permit, or nothing?
- Is a “join” route explicit (`subscribe`, `resubscribe`, clone, future creation) or simply absent?
- Are current waiters and future joiners treated differently?

## New reports that now look worth shipping

### 1. `late-joiner-admission.report.json`
Purpose:
- answer whether a surface admits new observers after creation and by what route.

Minimum fields:
- `surface`
- `admission_class`
- `join_mechanism`
- `observer_role`
- `admission_preconditions`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `fixed_cohort_only`
- `subscribe_route_available`
- `resubscribe_route_available`
- `future_waiter_creation_available`
- `current_waiters_only_no_future_join_memory`
- `manual_review_required`

### 2. `join-start.report.json`
Purpose:
- answer what a newly admitted observer immediately starts with.

Minimum fields:
- `surface`
- `start_class`
- `historic_visibility`
- `immediate_observable_state`
- `seen_state_posture`
- `future_visibility`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `future_only`
- `current_snapshot_seen`
- `current_tail_only`
- `stored_single_permit`
- `none_not_applicable`
- `manual_review_required`

## Why this belongs in P-0538 instead of a new subscription helper lane

The same ecosystems already used for memory / audience / closure semantics expose the gap directly:

- Tokio `broadcast::subscribe` gives a new receiver only values sent after the call.
- Tokio `broadcast::Receiver::resubscribe` starts from the current tail, not the current receiver’s backlog.
- Tokio `watch::Sender::subscribe` creates a new receiver whose current value is already considered seen.
- Tokio `Notify::notify_one` can seed one future waiter by storing a permit.
- Tokio `Notify::notify_waiters` intentionally does not seed future waiters.
- Tokio `mpsc` and `oneshot` make late-joiner routes inapplicable because their receiver cohort is fixed by channel creation.

That is exactly the kind of receiver-facing truth the crate should export.

## MVP scenario pack

Prefer small proving grounds:

1. `broadcast_subscribe_future_only`
2. `broadcast_resubscribe_current_tail`
3. `watch_subscribe_current_snapshot_seen`
4. `notify_one_stored_single_permit_for_future_waiter`
5. `notify_waiters_current_waiters_only`
6. `mpsc_fixed_receiver_cohort`
7. `oneshot_fixed_pair`
8. `portable_bundle_keeps_join_admission_and_join_start_separate`

## Doctor checks to add

- reject “subscribe implies current snapshot” when docs say future-only;
- reject “all notified waiters implies future joiners inherit a wake” when no permit is stored;
- reject “cloneable / resubscribable” equivalence without checking start baseline;
- reject “single-consumer” surfaces being treated as late-join-capable subscriptions.
