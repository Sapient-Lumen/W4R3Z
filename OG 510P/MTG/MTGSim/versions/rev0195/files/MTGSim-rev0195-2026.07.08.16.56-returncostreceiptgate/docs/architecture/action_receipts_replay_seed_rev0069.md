# rev0069 action receipts and replay-seed boundary

rev0069 moves the next riskiest seam from doctrine into executable code: legal actions are no longer only a generated list plus display labels. `apply_action(...)` now appends an `ActionReceiptRecord` after every attempted action.

The receipt is deliberately coarse. It is not another one-to-one `EventRecord` payload, because one chosen action can produce many rule events: payment, stack placement, priority handoff, trigger movement, resolution, and state-based actions. Instead it records the transition boundary around that work.

## What the receipt stores

Each receipt stores:

- a contiguous receipt index;
- canonical action fields: kind, player, object, target vector, mode index, ability index, and mana ability index;
- a canonical action hash that ignores display labels;
- the pre-action and post-action `canonical_state_hash(...)` values;
- the pre-action and post-action journal hashes sampled before the receipt row itself is appended;
- journal entry counts sampled before and after the action work, also before appending the receipt;
- the event-sequence allocator before and after the action;
- whether the action was legal at the boundary and whether it actually applied.

The hash/string helpers intentionally treat `LegalAction::label` as UI-only. This closes a replay hazard: labels can be localized or reformatted without changing the chosen action.

## Why this is a replay seed, not full replay

A full replay system still needs canonical checkpoint serialization, versioned input serialization, chance/observation handling, and a reconstruction test. The action receipt is the minimum durable transition seed: it tells a future replayer which canonical action was attempted and what hashes/counts must bracket the transition.

## Trimmed branches

Trimmed branches start with an empty journal. After rev0069, their first `apply_action(...)` receipt proves that no old journal rows were inherited by recording `journal_entries_before == 0` while still preserving the inherited `StateCore` hash before the action.

## Validation and tests

Validation now checks that action receipts are contiguous, have valid player/object/target references, do not claim an illegal action was applied, have monotone journal/event counters, and that the stored action hash matches the canonical action fields.

New regression coverage:

- `test_canonical_action_hash_ignores_display_label`;
- `test_apply_action_records_transition_receipt_hashes`;
- `test_trimmed_branch_records_new_action_receipt_only`.
