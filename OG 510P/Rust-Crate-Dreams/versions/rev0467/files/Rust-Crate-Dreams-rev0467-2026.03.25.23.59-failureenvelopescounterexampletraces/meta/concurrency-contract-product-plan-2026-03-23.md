# Concurrency Contract Kit product plan — 2026-03-23

This note exists to make **P-0538 Concurrency Contract Kit** more implementation-ready.

The archive already decided that the missing value is a **receiver-facing support-contract layer** for concurrency semantics scattered across docs and folklore.
This pass sharpens what a plausible `0.1` should actually ship.

## Main product judgment

The first lovable version should **not** try to infer arbitrary concurrency semantics from code.

It should do four simpler things well:

1. import or record claims from strong public docs and explicit maintainer annotations;
2. normalize them into a compact shared vocabulary;
3. emit small diffable artifacts;
4. package those artifacts into one portable review bundle.

## Core reports that now look worth shipping

### 1. `reentrancy-scope.report.json`
Purpose:
- answer whether the same thread, task, callback chain, or actor may re-enter the surface without blocking or deadlocking.

Minimum fields:
- `surface`
- `reentrancy_class`
- `scope_basis` (`same_thread`, `same_task`, `callback_path`, `manual_review_required`)
- `nightly_or_experimental`
- `claim_basis`
- `claim_ceiling`

### 2. `progress-fairness.report.json`
Purpose:
- answer what kind of ordering or starvation promise exists.

Minimum fields:
- `surface`
- `fairness_class` (`fifo`, `eventual_fairness`, `writer_priority`, `unspecified`, `manual_review_required`)
- `starvation_posture`
- `scope_notes`
- `claim_basis`
- `claim_ceiling`

### 3. `wait-cancellation.report.json`
Purpose:
- answer what exactly is preserved or forfeited if a wait is cancelled, dropped, or loses a `select!` race.

Minimum fields:
- `surface`
- `cancellation_class`
- `queue_membership_effect`
- `value_or_message_effect`
- `wake_or_permit_effect`
- `partial_effect_risk`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `cancel_safe_no_state_consumed`
- `queue_withdrawal_loses_place`
- `wake_registration_requires_manual_review`
- `not_cancel_safe`
- `manual_review_required`

### 4. `execution-context-boundary.report.json`
Purpose:
- answer which execution contexts are legal, discouraged, panic-prone, or deadlock-prone.

Minimum fields:
- `surface`
- `allowed_contexts`
- `forbidden_contexts`
- `panic_behavior`
- `blocking_behavior`
- `workaround_routes`
- `claim_basis`
- `claim_ceiling`

### 5. `mobility-affinity.report.json`
Purpose:
- answer whether a surface or spawned task is movable across threads, fixed to the current thread, or requires a specific local execution context.

Minimum fields:
- `surface`
- `mobility_class`
- `locality_scope`
- `spawn_context_requirements`
- `cross_thread_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `send_movable`
- `same_thread_local_only`
- `local_context_required`
- `runtime_thread_bound`
- `cpu_pinned_local`
- `manual_review_required`

### 6. `driver-liveness.report.json`
Purpose:
- answer what must keep running for the surface to make progress.

Minimum fields:
- `surface`
- `liveness_class`
- `drive_requirements`
- `non_driving_handles`
- `background_progress_posture`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `background_runtime_driven`
- `explicit_drive_required`
- `localset_drive_required`
- `handle_can_block_without_driving`
- `blocking_bridge_not_cancellable`
- `manual_review_required`

### 7. `failure-recovery.report.json` (optional but now worth standardizing)
Purpose:
- answer what happens after panic or failed initialization and what recovery route is promised.

Minimum fields:
- `surface`
- `recovery_class`
- `panic_while_holding_effect`
- `poisoning_mode`
- `recovery_route`
- `stability_class`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `advisory_poisoning_with_escape_hatch`
- `poisoning`
- `no_poisoning`
- `nonpoison_experimental`
- `manual_review_required`

## Why the fifth report now belongs here

The archive originally treated recovery posture as optional.
The same is true of locality / liveness, and now delivery memory / pressure, but current docs now make those distinctions concrete enough to standardize as optional first-class artifacts too: local spawn APIs can be thread-bound, a handle may exist without actually driving timers or I/O, and wake/value memory can be coalesced, bounded, overwritten, or absent altogether.

Current docs make it concrete enough that it should become a standard optional artifact:

- `std::sync::Mutex` makes poisoning **advisory** and documents an escape hatch through `PoisonError::into_inner`;
- `std::sync::RwLock` documents writer-only poisoning behavior;
- `parking_lot::Mutex` explicitly says there is **no poisoning** and the lock is released normally on panic;
- nightly `std::sync::nonpoison::Mutex` makes non-poisoning an explicit experimental posture.

That is a real receiver-facing distinction.
It belongs in the bundle when relevant.

### 8. `delivery-memory.report.json` (optional but now worth standardizing)
Purpose:
- answer what kind of state survives when notifications or messages arrive before the observer is ready.

Minimum fields:
- `surface`
- `memory_class`
- `delivery_unit`
- `receiver_fanout`
- `accumulation_limit`
- `late_receiver_posture`
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

### 9. `backlog-pressure.report.json` (optional but now worth standardizing)
Purpose:
- answer what happens when producers outrun consumers or bounded history is exceeded.

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

Current docs make this standardization worth doing because the ecosystem now clearly exposes materially different memory/pressure classes: Tokio `Notify` coalesces to at most one stored permit, Tokio `watch` stores only the latest value, Tokio `broadcast` reports lag against bounded retained history, bounded `mpsc` backpressures senders, and some channels are explicitly unbounded or zero-capacity rendezvous surfaces.


### 10. `late-joiner-admission.report.json` (optional but now worth standardizing)
Purpose:
- answer whether new observers may enter after creation and by what route.

Minimum fields:
- `surface`
- `admission_class`
- `join_mechanism`
- `observer_role`
- `admission_preconditions`
- `history_window`
- `claim_basis`
- `claim_ceiling`

Recommended classes:
- `fixed_cohort_only`
- `subscribe_route_available`
- `resubscribe_route_available`
- `future_waiter_creation_available`
- `current_waiters_only_no_future_join_memory`
- `manual_review_required`

### 11. `join-start.report.json` (optional but now worth standardizing)
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

Current docs make this standardization worth doing because the ecosystem now clearly exposes materially different observer-start classes: Tokio `broadcast::subscribe` is future-only, `broadcast::Receiver::resubscribe` starts from the current tail rather than the old receiver queue, Tokio `watch::Sender::subscribe` begins with the current value already seen, `Notify::notify_one` can seed one future waiter via a stored permit, and `Notify::notify_waiters` intentionally does not seed future waiters at all.

## Suggested crate split

- `concurrency-contract-core`
  - vocabulary enums
  - artifact structs
  - serde schemas
  - diff support

- `concurrency-contract-import`
  - docs/annotation import helpers
  - source-basis tagging
  - optional adapters for Tokio / `std` / `parking_lot`

- `concurrency-contract-fixtures`
  - fixture loaders
  - scenario validation helpers
  - schema tests

- `cargo-concurrency-contract`
  - init / inspect / check / bundle / diff / doctor workflows

## Suggested CLI

- `cargo concurrency-contract init`
- `cargo concurrency-contract inspect`
- `cargo concurrency-contract check`
- `cargo concurrency-contract doctor`
- `cargo concurrency-contract diff old/ new/`
- `cargo concurrency-contract bundle`

`doctor` is worth adding now because many failures here are classification failures:
- queue withdrawal incorrectly presented as “fully cancel safe”;
- no-poisoning presented as fairness;
- reentrancy presented as async-context legality;
- nightly posture presented as stable support.

## Best first fixtures

1. Tokio `Notify::notified`
2. Tokio `watch::Receiver::changed`
3. Tokio `mpsc::Receiver::recv`
4. Tokio `spawn_local` / `LocalSet` / `Handle::block_on` on `current_thread`
5. Tokio `LocalRuntime`
6. `async_executor::LocalExecutor`
7. glommio `spawn_local`
8. `std::sync::Mutex`
9. `parking_lot::Mutex`
10. nightly `std::sync::nonpoison::Mutex`
11. nightly `std::sync::ReentrantLock`

## What the crate should provide other people

Other engineers should get:

1. one vocabulary that travels across docs, reviews, support tickets, and release diffs;
2. one artifact bundle they can inspect without replaying the exact workload;
3. one honest distinction between queue loss, value loss, wake loss, and context misuse;
4. one honest distinction between local spawn support, thread-affinity, and movable work;
5. one honest distinction between driver-complete contexts and non-driving handles;
6. one honest distinction between poisoning, advisory recovery, and no-poisoning posture;
7. one honest distinction between producer-visible success and actual downstream observation;
8. one honest distinction between close signals, audience hints, and real receipt evidence;
9. one honest distinction between closed, drained, terminal, and reopenable states;
10. one honest distinction between no-future-sends and no-post-close-observable-tail;
11. one claim ceiling for nightly or otherwise partial support.

## Guardrails

- Do not auto-prove semantics from source code in `0.1`.
- Do not collapse channel delivery semantics into this lane; import **P-0529** when the sharp question is delivery/closure/backpressure.
- Do not collapse runtime-family choice into this lane; import **P-0532** when the sharp question is runtime topology/capabilities.
- Do not collapse deadlock detection or formal race proofs into this lane.


### 10. `delivery-audience.report.json` (optional but now worth standardizing)
Purpose:
- answer who is actually eligible to observe a wake/value/message unit.

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

### 11. `consumption-claim.report.json` (optional but now worth standardizing)
Purpose:
- answer what one observer taking / marking / receiving the unit does to others.

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

Current docs make this standardization worth doing because the ecosystem now clearly exposes materially different audience/claim classes: Tokio `broadcast` fans out to all active receivers, Tokio `watch` keeps per-receiver seen state over shared latest state, `Notify::notify_waiters` reaches all current waiters without future inclusion, Tokio `mpsc` is single-consumer, `async-channel` allows many consumers while still giving each message to only one, Flume cloned receivers still compete for single delivery, and Tokio `oneshot` is a single-use transfer.


### 12. `delivery-acceptance.report.json` (optional but now worth standardizing)
Purpose:
- answer what a successful send / notify / publish operation actually certifies.

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

### 13. `observation-evidence.report.json` (optional but now worth standardizing)
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

Current docs make this standardization worth doing because the ecosystem now clearly exposes materially different producer-facing ceilings: Tokio `mpsc::Sender::send` says `Ok` does not guarantee receipt, Tokio `broadcast` exposes active-receiver hints without proof of observation, Tokio `watch::Sender::send` distinguishes successful latest-state replacement from failed no-seeding, Tokio `oneshot::Sender` exposes close-notification rather than processing proof, Tokio `Notify` carries no payload receipt, and Flume shows the same live-receiver success pattern outside Tokio.

## 2026-03-23 addendum — delivery order and gap visibility now belong in the product shape

The concurrency-support lane now also needs to export:

- whether a surface promises single-consumer FIFO, per-receiver FIFO, latest-snapshot-only visibility, coalesced wake semantics, or selection-level random/biased choice;
- whether missed or collapsed units are impossible under the documented route, counted, cursor-rebased, silently dropped, or only manually reviewable;
- and doctor rules that reject fake equivalence between queue order, snapshot visibility, lag counting, and wake coalescing.

This is not just memory, pressure, audience, or claim posture.
It is the missing support-contract layer for **what sequence exists** and **what the receiver can know about gaps in it**.


## 2026-03-23 addendum — closure finality and post-close availability now belong in the product shape

The concurrency-support lane now also needs to export:

- whether closure is immediate terminal, drain-then-terminal, reopenable, or subject to a documented close/send race;
- whether a buffered tail, retained history, latest snapshot, or in-flight one-shot value remains observable after closure;
- and doctor rules that reject fake equivalence between “no new sends may enter” and “nothing remains to be read”.

This is not just memory, acceptance, evidence, or order posture.
It is the missing support-contract layer for **what closure finalizes** and **what remains visible afterward**.


## 2026-03-23 observer-cursor / progress-isolation refinement

Add two more portable artifacts before opening another neighboring runtime/channel lane:

- `observer-cursor.report.json`
- `observer-progress-isolation.report.json`

This refinement exists because current docs now make three different observer-topology families concrete:

1. **independent local cursors** (`watch`),
2. **per-receiver retained-history cursors with self-local lag recovery** (`broadcast`),
3. **shared competitive claim pools** (`async-channel`, Flume),
4. **fixed single-consumer posture** (`mpsc`),
5. **wake-only no-cursor posture** (`Notify`).

A first implementation should prefer strong documented cases and refuse to infer deeper causal scheduling behavior than the docs justify.
