# Concurrency Contract Kit delivery acceptance / observation plan — 2026-03-23

This note exists to make **P-0538 Concurrency Contract Kit** more implementation-ready.

The archive already decided that the missing value is a **receiver-facing support-contract layer** for concurrency semantics scattered across docs and folklore.
This pass sharpens what a plausible next slice should actually ship above the existing memory / pressure / audience / claim work.

## Main product judgment

The next lovable slice should **not** try to infer end-to-end receipt or processing from arbitrary code.

It should do two smaller things well:

1. say what producer-visible success means for a send / notify / publish surface;
2. say what evidence of downstream observation exists later, if any.

## New reports that now look worth shipping

### 1. `delivery-acceptance.report.json`
Purpose:
- answer what a successful producer-side operation actually certifies.

Minimum fields:
- `surface`
- `acceptance_class`
- `accepted_unit`
- `success_meaning`
- `receiver_liveness_requirement`
- `storage_or_visibility_effect`
- `future_joiner_posture`
- `observation_guarantee`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `wake_or_permit_recorded`
- `receiver_open_then_queue_admission`
- `latest_state_update_and_current_receiver_notification`
- `active_receiver_presence_required`
- `live_receiver_required_then_queue_or_handoff`
- `manual_review_required`

### 2. `observation-evidence.report.json`
Purpose:
- answer what evidence exists after acceptance that anybody actually observed or processed the unit.

Minimum fields:
- `surface`
- `evidence_class`
- `positive_evidence`
- `negative_evidence`
- `producer_visible_signals`
- `externalization_route`
- `separate_ack_required`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `none`
- `closure_only_negative_signal`
- `active_receiver_count_hint_only`
- `receiver_local_state_only`
- `application_ack_required`
- `manual_review_required`

## Why these reports now belong here

Current docs now make these distinctions concrete enough to standardize:

- Tokio `mpsc::Sender::send` explicitly says `Ok` does not mean the data will be received.
- Tokio `broadcast::Sender::send` says success requires at least one active receiver, while `receiver_count()` explicitly warns that the count is not a guarantee that a sent value will reach that many receivers.
- Tokio `watch::Sender::send` says success updates the latest value and notifies receivers, while failure returns the value and does not seed future receivers.
- Tokio `oneshot` says a sent message can remain in the channel until the receiver is dropped, and `poll_closed` / `is_closed` give closure signals rather than receipt proof.
- Tokio `Notify` says the surface carries no data and only wakes or records a permit.
- Flume says `send` / `send_async` fail if all receivers have been dropped, but success is still queue or rendezvous admission rather than processing receipt.

That is a real receiver-facing distinction.
It belongs in the bundle when relevant.

## Suggested first fixture set for this slice

1. Tokio `mpsc::Sender::send`
2. Tokio `broadcast::Sender::send` plus `receiver_count`
3. Tokio `watch::Sender::send`
4. Tokio `oneshot::Sender::{send,poll_closed,is_closed}`
5. Tokio `Notify::{notify_one,notify_waiters}`
6. Flume `Sender::{send,send_async}`

## What the crate should provide other people

Other engineers should get:

1. one honest answer to **what `Ok` from this surface means**;
2. one honest answer to **what `Ok` definitely does not prove**;
3. one explicit distinction between endpoint liveness, queue admission, state replacement, and true downstream observation;
4. one explicit distinction between count hints, close signals, receiver-local seen state, and real receipt evidence;
5. one cheap path to say **application-level acknowledgment required** instead of pretending the primitive already proves it.

## Guardrails

- Do not auto-prove message processing from send success in `0.1`.
- Do not flatten audience / claim semantics into acceptance semantics.
- Do not flatten memory / pressure semantics into observation evidence.
- Do not treat close notifications as positive receipt proof.
- Do not treat returned receiver counts as delivery receipts.
