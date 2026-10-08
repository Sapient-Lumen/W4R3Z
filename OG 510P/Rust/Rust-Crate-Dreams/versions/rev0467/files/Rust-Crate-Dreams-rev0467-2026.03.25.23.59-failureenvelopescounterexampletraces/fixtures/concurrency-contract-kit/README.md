# Concurrency Contract Kit fixtures

This fixture family exists to keep **P-0538 Concurrency Contract Kit** concrete.

The core claim is that concurrency semantics should become a **reviewable support contract**, not just prose spread across API pages.

## Core review objects

- `reentrancy-scope.report.json`
- `progress-fairness.report.json`
- `wait-cancellation.report.json`
- `execution-context-boundary.report.json`
- optional `mobility-affinity.report.json`
- optional `driver-liveness.report.json`
- optional `failure-recovery.report.json`
- optional `delivery-memory.report.json`
- optional `backlog-pressure.report.json`
- optional `delivery-audience.report.json`
- optional `consumption-claim.report.json`
- optional `delivery-acceptance.report.json`
- optional `observation-evidence.report.json`
- optional `late-joiner-admission.report.json`
- optional `join-start.report.json`
- optional `delivery-order.report.json`
- optional `gap-visibility.report.json`
- optional `closure-finality.report.json`
- optional `post-close-availability.report.json`
- `concurrency-support-bundle.manifest.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- a surface can be acquired,
- it is therefore re-entrant,
- it is therefore fair,
- cancellation is therefore harmless,
- and it is therefore safe in any execution context.

Those are not the same claim.
A surface may also be legal in a context and still remain thread-affine or require an explicit drive loop for progress.

## Scenario families

### `tokio_mutex_fifo_is_not_reentrant/`
Tokio `Mutex` can fairly distribute locks while still not making a same-task reentrancy promise.
The fixture keeps ordering separate from re-entry semantics and context legality.

### `tokio_select_and_semaphore_cancel_safety_is_lane_specific/`
Cancellation can be documented at the method or combinator level and still cause queue-place loss.
The fixture keeps “cancel-safe enough for use” separate from “no effect when cancelled.”

### `tokio_notify_queue_loss_is_not_channel_message_loss/`
Queue withdrawal for `Notify` is real, but it is not the same thing as losing a buffered message.
The fixture keeps queue place, stored-permit behavior, and message delivery separate.

### `tokio_watch_changed_true_cancel_safety_keeps_seen_state/`
`watch::Receiver::changed` documents stronger cancellation guarantees than queue withdrawal.
The fixture keeps seen-state preservation separate from fairness or reentrancy claims.

### `tokio_mpsc_recv_true_cancel_safety_keeps_message_availability/`
`mpsc::Receiver::recv` documents that cancellation does not consume a message.
The fixture keeps true cancel safety separate from queue-place loss.

### `parking_lot_eventual_fairness_is_not_tokio_fifo/`
`parking_lot` fairness vocabulary is real, but it is not identical to Tokio FIFO queueing.
The fixture keeps fairness classes explicit instead of pretending all fair-ish claims are the same.

### `std_mutex_blocking_and_nightly_reentrant_lock_do_not_imply_async_safety/`
Blocking behavior, poisoning, and experimental reentrant locking are not blanket async-context endorsements.
The fixture keeps reentrancy and execution-context truth separate.

### `std_poisoning_and_nonpoison_are_recovery_contracts_not_fairness_claims/`
Poisoning, advisory recovery, and explicit non-poisoning are receiver-facing recovery postures.
The fixture keeps recovery posture separate from fairness and context legality.

### `portable_bundle_keeps_reentrancy_progress_cancellation_and_context_separate/`
A portable bundle should join the core reports without flattening them into one “concurrency safe” bit.


### `tokio_spawn_local_requires_local_context_and_same_thread_execution/`
Local spawn support is real, but it is not the same thing as movable work or “works anywhere Tokio works.”
The fixture keeps same-thread affinity and required local context explicit.

### `tokio_current_thread_handle_block_on_is_not_driver_complete/`
A handle may still be insufficient to drive I/O and timers.
The fixture keeps handle availability separate from driver-liveness.

### `tokio_localruntime_is_thread_bound_and_not_a_localset/`
A local runtime may support local tasks without being equivalent to a `LocalSet`.
The fixture keeps thread-bound runtime posture separate from local-set semantics.

### `async_executor_local_executor_is_creator_thread_bound_and_explicitly_driven/`
Thread-local executors are portable substrate for this lane.
The fixture keeps creator-thread affinity and explicit drive requirements visible.

### `glommio_spawn_local_requires_current_single_thread_executor/`
Thread-per-core / local-executor systems add placement and current-executor assumptions.
The fixture keeps those separate from generic async-context legality.

### `portable_bundle_keeps_context_mobility_and_driver_liveness_separate/`
A portable bundle should join context legality, locality, and liveness without flattening them into one “works in async” bit.

### `tokio_notify_single_permit_memory_is_not_a_queue/`
Tokio `Notify` can remember one coalesced permit without becoming a message queue.
The fixture keeps wake memory separate from backlog semantics.

### `tokio_watch_latest_value_only_drops_intermediate_history/`
Tokio `watch` retains only the latest value.
The fixture keeps latest-state visibility separate from per-send retention.

### `tokio_broadcast_bounded_history_reports_lagged_loss/`
Tokio `broadcast` exposes bounded history plus lag signaling.
The fixture keeps bounded fanout history separate from no-loss delivery claims.

### `tokio_mpsc_bounded_fifo_backpressures_senders_without_overwrite/`
Tokio bounded `mpsc` backpressures senders instead of overwriting older queued messages.
The fixture keeps queue backpressure separate from lag-loss semantics.

### `async_channel_unbounded_removes_capacity_pressure_but_not_single_delivery/`
`async-channel` unbounded mode moves pressure toward growth risk, not broadcast fanout.
The fixture keeps unbounded accumulation separate from delivery multiplicity.

### `crossbeam_zero_capacity_is_rendezvous_not_buffered_memory/`
Zero-capacity channels are explicit rendezvous surfaces.
The fixture keeps no-memory pairing separate from buffered channel semantics.

### `portable_bundle_keeps_delivery_memory_and_pressure_separate/`
A portable bundle should join delivery memory and pressure without flattening them into “channel behavior”.

### `tokio_notify_waiters_reaches_all_current_waiters_without_future_subscription/`
`notify_waiters` reaches all already waiting tasks without turning into future-subscriber memory.
The fixture keeps current audience separate from stored permits and future joiners.

### `tokio_broadcast_fans_out_each_send_to_all_active_receivers/`
`broadcast` gives every active receiver a delivered view of each send.
The fixture keeps fanout separate from single-consumer competition.

### `tokio_watch_receivers_track_seen_state_independently/`
`watch` receivers each track seen state over shared latest state.
The fixture keeps independent observation separate from queue delivery and per-send broadcast history.

### `tokio_mpsc_delivers_each_message_to_single_consumer/`
Tokio `mpsc` is a single-consumer queue.
The fixture keeps single-consumer delivery separate from MPMC competition and broadcast.

### `async_channel_competing_receivers_claim_each_message_once/`
`async-channel` allows many consumers while each message is still claimed only once.
The fixture keeps MPMC competition separate from fanout.

### `flume_cloned_receivers_still_compete_for_single_delivery/`
Cloning a Flume receiver does not create broadcast semantics.
The fixture keeps cloneable handles separate from fanout delivery.

### `tokio_oneshot_is_single_use_transfer_not_subscription/`
One-shot transfer is its own claim class.
The fixture keeps single-use transfer separate from reusable channel or latest-state stories.

### `portable_bundle_keeps_delivery_audience_and_claim_separate/`
A portable bundle should join audience and claim artifacts without flattening them into generic channel behavior.


### `tokio_mpsc_send_ok_means_receiver_open_not_eventual_receipt/`
Tokio `mpsc::Sender::send` explicitly says `Ok` does not prove eventual receipt.
The fixture keeps queue admission separate from observation proof.

### `tokio_broadcast_send_count_is_hint_not_observation_receipt/`
Tokio `broadcast` can expose active-receiver hints without proving actual observation.
The fixture keeps audience hints separate from delivery receipts.

### `tokio_watch_send_updates_latest_state_but_failed_send_seeds_no_future_receivers/`
Tokio `watch` success changes shared latest state, while failed send seeds nothing for future receivers.
The fixture keeps acceptance meaning separate from future-observation folklore.

### `tokio_oneshot_send_stores_value_but_sender_only_gets_close_signal/`
Tokio `oneshot` lets the sender observe closure without proving that the receiver awaited and used the value.
The fixture keeps close signals separate from receipt proof.

### `tokio_notify_records_permit_or_wakes_without_payload_receipt/`
Tokio `Notify` changes wake eligibility rather than exporting payload receipt.
The fixture keeps wake acceptance separate from message observation.

### `flume_send_ok_requires_live_receiver_but_not_processing_receipt/`
Flume shares the same support gap: live-receiver success is still not processing proof.
The fixture keeps portable liveness-gated success separate from acknowledgment.

### `portable_bundle_keeps_delivery_acceptance_and_observation_evidence_separate/`
A portable bundle should join acceptance and evidence artifacts without flattening them into a generic send-success bit.


### `tokio_mpsc_fifo_order_has_no_gap_counter/`
Tokio bounded `mpsc` exports FIFO single-consumer ordering.
The fixture keeps queue order separate from counted gap visibility.

### `tokio_broadcast_per_receiver_fifo_exposes_lag_counts/`
Tokio `broadcast` exports per-receiver FIFO plus lag/skipped-message counts.
The fixture keeps counted gaps separate from generic “messages may be lost” folklore.

### `tokio_watch_latest_snapshot_silently_discards_intermediate_sequence/`
Tokio `watch` exports latest-state visibility, not full ordered history.
The fixture keeps latest snapshot semantics separate from FIFO message order.

### `tokio_notify_coalesces_repeated_notify_one_without_skip_count/`
Tokio `Notify` coalesces repeated wake signals into one stored permit.
The fixture keeps coalesced wake semantics separate from counted sequence delivery.

### `crossbeam_select_ready_choice_is_random_without_biased_mode/`
Crossbeam `Select` can choose randomly among multiple simultaneously ready operations.
The fixture keeps cross-surface ready-operation choice separate from per-channel message order.

### `portable_bundle_keeps_delivery_order_and_gap_visibility_separate/`
A portable bundle should join order and gap reports without flattening them into generic channel behavior.


### `tokio_mpsc_close_is_drain_then_terminal_not_immediate_empty/`
Tokio `mpsc` close shuts future admission while still requiring the receiver to drain buffered items and permit-backed sends.
The fixture keeps close-state separate from immediate emptiness.

### `tokio_broadcast_closed_still_delivers_retained_values_until_exhausted/`
Tokio `broadcast` can be closed while each receiver still has retained history to drain.
The fixture keeps closed-state separate from receiver-tail exhaustion.

### `tokio_watch_closed_keeps_last_value_and_can_reopen_via_subscribe/`
Tokio `watch` can enter a closed interval and later be reopened by `subscribe`.
The fixture keeps closure finality separate from latest-value visibility and reopenability.

### `tokio_oneshot_close_blocks_future_send_but_in_flight_value_may_remain/`
Tokio `oneshot` close blocks future sends without proving the slot is empty.
The fixture keeps close success separate from in-flight value recovery.

### `async_channel_closed_still_allows_remaining_messages/`
`async-channel` documents that remaining messages can still be received after close.
The fixture keeps closed-state separate from drained-state.

### `std_mpsc_disconnect_is_drain_then_terminal_with_buffered_tail/`
`std::sync::mpsc` disconnect still allows buffered tail to drain before terminal error.
The fixture keeps disconnect separate from immediate terminal emptiness.

### `portable_bundle_keeps_closure_finality_and_post_close_availability_separate/`
A portable bundle should join closure-finality and post-close-availability artifacts without flattening them into one “closed” bit.

### `tokio_broadcast_subscribe_starts_with_future_sends_only/`
`broadcast::subscribe` admits late receivers, but only for values sent after the subscription call.
The fixture keeps future-only subscribe separate from current-snapshot or replay semantics.

### `tokio_broadcast_resubscribe_starts_from_current_tail_not_old_queue/`
`broadcast::Receiver::resubscribe` starts from the current tail rather than inheriting the current receiver's queued values.
The fixture keeps current-tail semantics separate from replay or queue inheritance.

### `tokio_watch_subscribe_starts_with_current_value_marked_seen/`
`watch::Sender::subscribe` creates a receiver whose current value is already considered seen.
The fixture keeps current-snapshot subscribe separate from future-only subscribe.

### `tokio_notify_notify_one_can_seed_one_future_waiter/`
`Notify::notify_one` can seed one future waiter when no task is currently waiting.
The fixture keeps stored-permit late waits separate from current-waiters-only notification.

### `tokio_notify_waiters_has_no_future_joiner_memory/`
`Notify::notify_waiters` reaches current waiters without storing a future permit.
The fixture keeps current-waiter reach separate from late-join memory.

### `tokio_mpsc_fixed_receiver_cohort_has_no_late_joiner_route/`
Tokio `mpsc` fixes its receiver cohort at channel creation.
The fixture keeps fixed-cohort surfaces separate from subscription-capable ones.

### `tokio_oneshot_fixed_pair_has_no_late_joiner_route/`
Tokio `oneshot` fixes its sender/receiver pair at channel creation.
The fixture keeps fixed-pair transfer separate from reusable subscription stories.

### `portable_bundle_keeps_join_admission_and_join_start_separate/`
A portable bundle should join late-joiner admission and join-start artifacts without flattening them into one generic “subscribe” bit.


### `tokio_watch_receivers_have_independent_seen_cursors/`
Tokio `watch` gives each receiver its own seen-state cursor over shared latest state.
The fixture keeps independent local progress separate from fanout and latest-value memory.

### `tokio_broadcast_receivers_have_per_receiver_cursors_and_self_lag_rebase/`
Tokio `broadcast` gives each receiver retained-history progress and a self-local lag-rebase path.
The fixture keeps per-receiver cursor recovery separate from full replay and separate from shared work-pool competition.

### `async_channel_consumers_share_competitive_claim_pool_not_independent_cursors/`
`async-channel` many-consumer delivery is still one-of-many claim, not independent observer-local cursors.
The fixture keeps shared work-pool competition separate from fanout or replay surfaces.

### `flume_cloned_receivers_compete_for_shared_work_pool/`
Flume cloned receivers still compete for single delivery.
The fixture keeps work-stealing / shared-pool semantics separate from broadcast and separate from per-observer retained-history progress.

### `tokio_mpsc_single_receiver_has_fixed_cursor_not_multiobserver_coupling/`
Tokio `mpsc` is single-consumer, so multi-observer cursor language is inapplicable.
The fixture keeps fixed single-consumer posture separate from many-receiver channels.

### `tokio_notify_is_wake_only_and_has_no_data_cursor/`
Tokio `Notify` is wake-only and carries no data.
The fixture keeps wake eligibility separate from any fake message cursor language.

### `portable_bundle_keeps_observer_cursor_and_progress_isolation_separate/`
A portable bundle should join cursor ownership and observer progress-isolation without flattening them into generic “channel behavior”.
