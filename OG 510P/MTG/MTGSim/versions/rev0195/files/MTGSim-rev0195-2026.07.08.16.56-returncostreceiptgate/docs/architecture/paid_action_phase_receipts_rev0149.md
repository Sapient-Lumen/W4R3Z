# rev0149 — Paid Action Phase Receipts

## Mission fit

Paid Action Phase Receipts make the inner transition mission visible at the phase where most mistakes hide: after a spell or ability is announced, modes and targets are locked, costs are paid, and the stack object is finally considered placed. The cube already had strong mana-payment evidence, but the broader paid action phase could still be reconstructed only by following adjacent event order.

rev0149 promotes that seam into typed `StackPlacementRecord` evidence. A paid cast, activated ability, or loyalty ability now records whether the stack object existed before costs, when choices were locked, which event span belonged to payment, which `ManaPaymentPlanRecord` and `ManaChangeRecord` rows were used, and which sacrifice zone changes were part of the paid body.

## New record surface

`StackPlacementRecord` now carries:

- `paid_action_phase_recorded`
- `stack_object_on_stack_before_costs`
- `choices_locked_before_costs`
- `paid_action_events_before_stack_placement`
- `stack_object_entered_sequence`
- `choices_locked_sequence`
- `first_paid_action_event_sequence` / `last_paid_action_event_sequence`
- `first_mana_payment_plan_record_index` / `mana_payment_plan_record_count`
- `first_mana_change_record_index` / `mana_change_record_count`
- `first_paid_action_zone_change_record_index` / `paid_action_zone_change_record_count`

These fields do not replace the existing receipt spine. They make the paid-action portion auditable before the outer `ActionReceiptRecord` claims the transition committed.

## Engine refactor

The engine now captures paid-action snapshots with `PaidActionPhaseSnapshot`, `capture_paid_action_phase_snapshot`, and seals them through `seal_paid_action_phase`. Spell casts with mana, modes, targets, and sacrifice costs use the same sealing path as activated abilities. Loyalty activations now create their synthetic loyalty stack object and lock target evidence before the loyalty counter payment, so the loyalty stack object is present before costs are paid.

## Validator and audit

`validate_game_state` now rejects records that have a paid/choice shape but lack paid-action phase evidence. It also checks ordering and range integrity for choice locks, stack-entry evidence, mana plans, mana changes, tap witnesses, and sacrifice zone-change spans. The dedicated audit probe `audit_paid_action_phase_receipts_wiring` keeps the new surface wired through source, validation, tests, architecture notes, audit notes, the rules ledger, README, and changelog.

## Focused regression coverage

- `test_paid_action_phase_records_sacrifice_spell_cost_span`
- `test_paid_action_phase_records_mana_and_tap_receipts_for_activated_ability`
- `test_paid_action_phase_records_loyalty_stack_before_counter_payment`

These tests corrupt the new evidence directly and expect specific diagnostics rather than relying on event prose or final state alone.

## Remaining gap

This is still a receipt slice, not the complete cost-plan kernel. The next deeper refactor should name a broader cost/payment plan that includes all nonmana costs, rollback reason, total-cost lock, and receipt emission as one reusable operation for spells, activated abilities, loyalty abilities, and future special actions.
