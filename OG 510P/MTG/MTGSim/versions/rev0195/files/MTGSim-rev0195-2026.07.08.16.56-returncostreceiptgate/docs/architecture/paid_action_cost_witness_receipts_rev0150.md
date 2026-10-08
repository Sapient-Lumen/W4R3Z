# rev0150 — Paid Action Cost Witness Receipts

## Why this slice exists

rev0149 made the paid-action phase visible on `StackPlacementRecord`, but the next audit found two cost-witness seams that were still weaker than the mission requires:

1. loyalty costs were represented by `loyalty_cost_paid` and an ordered event span, but the stack-placement receipt did not name the `CounterChangeRecord` range that actually paid the loyalty cost;
2. tap costs were proven by searching for a matching `tap` row in the paid-action window, but the receipt did not name the exact tap witness or require its source zone-change snapshot to match the paid source incarnation.

MTGSim's heart is a trusted transition kernel: canonical state plus explicit legal choice yields one deterministic next state and typed evidence that replay, audit, search, fuzzing, and future agents can challenge. Cost payment cannot remain partly inferential at the point where the stack-placement receipt claims the action succeeded.

## What changed

`StackPlacementRecord` now carries two additional cost-witness surfaces:

- `tap_cost_event_sequence`: the exact `EventRecord` sequence of the tap row that paid an activation tap cost. Validation requires it to be a `tap` log row, inside the paid-action window, with matching source object, controller, and `source_zone_change_index_before`.
- `first_paid_action_counter_change_record_index` and `paid_action_counter_change_record_count`: a one-based range into `GameState::counter_change_records` covering counter mutations that occur after choice lock and before final stack-placement receipt. Loyalty activations with nonzero `loyalty_cost_delta` must expose this loyalty counter-change range, and validation checks the linked rows are loyalty counter changes for the source object.

The sealing helper remains centralized in `seal_paid_action_phase(...)`. It now snapshots `counter_change_records.size()` when choices are locked, emits counter-change ranges after costs are paid, and resolves the exact tap-cost witness while the paid-action window is still local.

## Validator guarantees

New or strengthened diagnostics include:

- `stack_placement_record.invalid_paid_phase_counter_change_range`
- `stack_placement_record.paid_phase_counter_change_sequence_outside_span`
- `stack_placement_record.paid_phase_missing_loyalty_counter_change`
- `stack_placement_record.paid_phase_loyalty_counter_source_mismatch`
- `stack_placement_record.paid_phase_loyalty_counter_kind_mismatch`
- `stack_placement_record.paid_phase_tap_witness_missing`
- `stack_placement_record.paid_phase_tap_witness_not_tap`
- `stack_placement_record.paid_phase_tap_witness_sequence_outside_span`
- `stack_placement_record.paid_phase_tap_witness_source_mismatch`
- `stack_placement_record.paid_phase_tap_witness_player_mismatch`
- `stack_placement_record.paid_phase_tap_witness_zone_index_mismatch`

## Refactor boundary

This revision does not attempt a complete general cost-plan record. It deliberately tightens two adjacent witnesses already produced by the engine: tap Event rows and loyalty CounterChangeRecord rows. The broader future target remains a unified paid-action cost plan that can represent variable costs, alternative costs, cost increases/reductions, ward, sacrifice choices, counter changes, taps, discards, and mana payment as one ordered payment object.

## Evidence

Focused C++ regressions extend the existing paid-action phase tests:

- activated abilities now assert that `tap_cost_event_sequence` resolves to the exact tap row and reject a witness with the wrong source zone-change snapshot;
- loyalty activations now assert that the paid-action counter-change range points at the loyalty counter mutation and reject missing or non-loyalty counter ranges.

The datacube audit adds `audit_paid_action_cost_witness_receipts_wiring(...)` so this field-level seam remains connected across source, validation, tests, documentation, rules ledger, README, and changelog.
