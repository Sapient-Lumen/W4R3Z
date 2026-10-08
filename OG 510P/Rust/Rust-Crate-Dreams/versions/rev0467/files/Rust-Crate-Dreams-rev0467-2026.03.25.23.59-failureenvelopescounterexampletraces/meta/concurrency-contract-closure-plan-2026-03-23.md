# Concurrency Contract Kit closure finality / post-close availability plan — 2026-03-23

This note exists to make **P-0538 Concurrency Contract Kit** more implementation-ready.

The archive already decided that the missing value is a **receiver-facing support-contract layer** for concurrency semantics scattered across docs and folklore.
This pass sharpens what a plausible next slice should actually ship above the existing memory / pressure / audience / claim / acceptance / evidence / order / gap work.

## Main product judgment

The next lovable slice should **not** try to prove whole-program shutdown correctness.

It should do two smaller things well:

1. say what “closed” or “disconnected” actually finalizes for a surface;
2. say what values, snapshots, or retained tail remain observable after closure.

## New reports that now look worth shipping

### 1. `closure-finality.report.json`
Purpose:
- answer whether closure is immediate terminal, drain-then-terminal, reopenable, or subject to a close/send race.

Minimum fields:
- `surface`
- `closure_class`
- `close_trigger`
- `terminal_condition`
- `reopen_posture`
- `residual_delivery_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `immediate_terminal`
- `drain_then_terminal`
- `reopenable_closed_state`
- `close_race_with_in_flight_value`
- `manual_review_required`

### 2. `post-close-availability.report.json`
Purpose:
- answer what remains observable after closure and how it is accessed.

Minimum fields:
- `surface`
- `availability_class`
- `retained_unit`
- `access_route_after_close`
- `consumer_obligation`
- `terminal_signal_after_tail`
- `visibility_scope`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `none`
- `buffered_tail_drains`
- `retained_history_drains`
- `latest_snapshot_still_readable`
- `in_flight_value_may_still_be_recoverable`
- `manual_review_required`

## Why these reports now belong here

Current docs now make these distinctions concrete enough to standardize:

- Tokio `mpsc` clean-shutdown docs say the receiver should close and then consume the channel to completion, and the receiver docs say buffered messages and outstanding permits can still produce values after `close`.
- Tokio `broadcast` says closure begins when all senders are dropped, but receivers still get retained values until those values are exhausted.
- Tokio `watch` says `changed` only errors when the channel is closed and the current value is already seen, while `Sender::closed` says a closed channel can be reopened by `subscribe`.
- Tokio `oneshot` says `Receiver::close` blocks future sends but `try_recv` should still be used to recover a value sent before close completed, and the module docs say an already-sent value can remain until the receiver is dropped.
- `async-channel` says that when a channel is closed, no more messages can be sent but remaining messages can still be received.
- `std::sync::mpsc::Receiver` says that after sender disconnect buffered messages sent before disconnect can still be properly received.

That is a real receiver-facing distinction.
It belongs in the bundle when relevant.

## Suggested first fixture set for this slice

1. Tokio `mpsc::Receiver::close` plus `recv`
2. Tokio `broadcast::Receiver::recv`
3. Tokio `watch::{Sender::closed, Sender::subscribe, Receiver::changed, Receiver::borrow}`
4. Tokio `oneshot::{Receiver::close, Receiver::try_recv}`
5. `async-channel::{Sender::close, Receiver::close, recv}`
6. `std::sync::mpsc::Receiver::recv`

## What the crate should provide other people

Other engineers should get:

1. one honest answer to **what closure finalizes right now**;
2. one honest answer to **what can still be observed after closure**;
3. one explicit distinction between “no new sends can enter” and “the observation surface is empty”;
4. one explicit distinction between a permanently terminal state and a closed state that can later be reopened or resumed;
5. one cheap path to say **manual review required** instead of pretending the docs prove whole-system shutdown correctness.

## Guardrails

- Do not auto-prove global shutdown or drain completion in `0.1`.
- Do not flatten closure finality into send-success semantics.
- Do not flatten post-close availability into delivery-memory class.
- Do not treat “closed” as proof that the surface is empty.
- Do not treat last-value visibility or in-flight recovery as proof that the surface is reopenable.
