# Choice Lock Receipts — rev0152

## Mission seam

rev0152 audits the paid-action spine immediately before cost payment. rev0149 proved that mode/target choices were locked before paid events, but consumers still had to infer the actual choice rows from surrounding log order. This revision makes the choice-lock rows a named `StackPlacementRecord` witness span.

## Code-bearing contract

`StackPlacementRecord` now carries:

- `first_choice_event_sequence`: the first `choose_mode` / `choose_target` `EventRecord` sequence in the lock window.
- `last_choice_event_sequence`: the last choice row and, for the current paid paths, the sealed `choices_locked_sequence`.
- `choice_event_count`: the number of mode/target choice rows in that explicit span.

`seal_choice_lock_witness(...)` scans only the interval after `stack_object_entered_sequence` and through `choices_locked_sequence`, then records the exact choice-event span. The helper keeps this evidence adjacent to the existing paid-action receipt sealing path, rather than spreading ad hoc scans across casts and activations.

## Refactor surface

The choice log rows now use `record_event_with_links(...)` so plain `EventRecordKind::Log` entries still carry object/controller anchors, and target choices preserve the chosen target when there is one selected target. This keeps mode and target evidence queryable without prematurely introducing a separate typed choice-record family.

## Validation

`validate_game_state(...)` now rejects:

- mode or target placements without explicit choice-lock witnesses;
- choice-event counts that disagree with the named sequence span;
- choice rows outside the stack-entry/choice-lock window;
- choice rows that name the wrong stack object or controller;
- modal placements without `choose_mode` witnesses and targeted placements without `choose_target` witnesses.

The focused regression `test_paid_action_choice_lock_receipts_record_mode_and_target_events` corrupts both missing choice evidence and a wrong choice-row object anchor. The datacube audit probe `audit_choice_lock_receipts_wiring(...)` guards source, validation, tests, docs, ledger, README, and changelog wiring.

## Remaining deeper seam

Choice-lock receipts are still event-row witnesses rather than a unified typed declaration record. The next deeper refactor should promote all announcement choices—modes, targets, divisions, optional costs, alternative/additional costs, and X values—into a single choice declaration journal that paid actions and replay can hash before any cost mutation occurs.
