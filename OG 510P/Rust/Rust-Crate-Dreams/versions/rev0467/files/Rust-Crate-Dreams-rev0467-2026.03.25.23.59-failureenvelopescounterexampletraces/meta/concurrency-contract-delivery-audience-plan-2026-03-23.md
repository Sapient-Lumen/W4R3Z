# Concurrency Contract Kit delivery-audience / consumption-claim plan — 2026-03-23

This note exists to make **P-0538 Concurrency Contract Kit** more implementation-ready.

The archive already had reentrancy, fairness, cancellation, recovery, context, locality, liveness, delivery memory, and backlog pressure.
The next missing layer is now sharper: **who is actually eligible to observe a wake/value/message** and **what one observer taking it means for everyone else**.

## Main product judgment

The first lovable version of this slice should not try to prove queue internals from code.
It should normalize strong public docs and explicit maintainer annotation into two new optional reports.

## 1. `delivery-audience.report.json`

Purpose:
- answer which observers are in the audience for a single wake/value/message unit.

Minimum fields:
- `surface`
- `audience_class`
- `delivery_unit`
- `eligible_observers`
- `join_window`
- `ordering_scope`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `single_waiter_notification`
- `all_current_waiters`
- `single_consumer_delivery`
- `single_receiver_pair`
- `all_active_receivers`
- `independent_latest_state_receivers`
- `manual_review_required`

Interpretation guidance:
- `single_waiter_notification` means one waiting task may be woken or consume a stored permit.
- `all_current_waiters` means all already-registered waiters are in the audience, but future waiters are not retroactively included.
- `single_consumer_delivery` means one consumer receives each message even if multiple receiver handles exist.
- `single_receiver_pair` means the surface is explicitly one sender / one receiver for a single transfer.
- `all_active_receivers` means every currently subscribed receiver is part of the audience for each sent value.
- `independent_latest_state_receivers` means each receiver can inspect current state independently, even though intermediate send history is not retained.

## 2. `consumption-claim.report.json`

Purpose:
- answer what happens when one observer receives / marks / claims the unit.

Minimum fields:
- `surface`
- `claim_class`
- `claim_event`
- `other_observer_effect`
- `value_identity_posture`
- `redelivery_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `non_consuming_notification`
- `exclusive_message_claim`
- `clone_per_receiver_fanout`
- `independent_seen_state_marking`
- `single_use_transfer`
- `manual_review_required`

Interpretation guidance:
- `non_consuming_notification` means wake observation does not correspond to one observer taking a payload away from others.
- `exclusive_message_claim` means one receiver gets the message and others do not.
- `clone_per_receiver_fanout` means each active receiver obtains its own delivered copy / view for that send.
- `independent_seen_state_marking` means each receiver marks its own observation state without consuming shared history for other receivers.
- `single_use_transfer` means the channel exists for one transfer between one sender and one receiver.

## Why these reports belong in P-0538

These are receiver-facing concurrency truths, not just queue taxonomy.

A user choosing between `Notify`, `watch`, `broadcast`, `mpsc`, `async-channel`, Flume, or `oneshot` is often really choosing between:

- one waiter versus all current waiters,
- one receiver versus all active receivers,
- exclusive claim versus clone fanout,
- per-receiver latest-state tracking,
- or single-use transfer.

The support contract should say that explicitly.

## What the crate should give other people

A useful `0.1` should let another engineer answer:

1. If I send or notify now, who is actually in the audience?
2. Are late joiners included, excluded, or only able to observe later state?
3. If one receiver takes the value, can another receiver still see that same send?
4. Is this clone fanout, competition for one claim, or independent observation of shared latest state?
5. Is the surface a wake-only signal, a single-use transfer, or a reusable multi-observer medium?

## Suggested MVP scenario pack

- Tokio `Notify::notify_waiters` current-waiter fanout with no future inclusion
- Tokio `broadcast` all-active-receiver fanout
- Tokio `watch` per-receiver latest-state observation with independent seen state
- Tokio `mpsc` single-consumer delivery
- `async-channel` competing MPMC receivers with exclusive claim
- Flume cloned receivers still competing instead of broadcasting
- Tokio `oneshot` single-use transfer

## Guardrail

Do not let future revisions flatten these into a fake “channel delivery” summary.
The whole point is to keep **delivery audience**, **consumption claim**, **memory class**, **pressure class**, **fairness**, **cancellation**, and **context legality** separately reviewable.
