# rev0153 — Choice Payload Anchors

rev0153 narrows the choice-lock seam introduced by rev0152. The previous receipt proved that `choose_mode` / `choose_target` rows existed between stack entry and cost payment, but consumers still had to scan the generic span to decide which row carried the mode payload and which row carried the target payload.

This revision makes the payload anchors explicit:

- `EventRecord::choice_mode_index` records the selected mode on `choose_mode` rows.
- `EventRecord::choice_target_count` records the number of targets carried by a `choose_target` row.
- `StackPlacementRecord::mode_choice_event_sequence` names the exact `choose_mode` row for modal paid actions.
- `StackPlacementRecord::target_choice_event_sequence` names the exact `choose_target` row for targeted paid actions.

Validation now rejects missing, unexpected, wrong-kind, out-of-window, wrong-object, wrong-controller, mode-index mismatched, target-count mismatched, and single-target payload mismatched choice anchors. For single-target choices, the `EventRecord::target` payload must agree with the `StackPlacementRecord::chosen_targets` payload. For multi-target choices, the event row carries the target count while the placement record remains the full ordered target list.

The mission spine remains: canonical state plus explicit legal choice yields one deterministic next state and typed evidence that replay, audit, search, fuzzing, and future agents can challenge. rev0153 strengthens the announcement evidence so a future agent does not need to infer the selected mode or target payload from prose or from an untyped event span.

Primary guarded test: `test_paid_action_choice_lock_receipts_record_mode_and_target_events`.


Validator error coverage includes `target_choice_event_target_mismatch` for single-target payload anchors that point at the wrong target.
