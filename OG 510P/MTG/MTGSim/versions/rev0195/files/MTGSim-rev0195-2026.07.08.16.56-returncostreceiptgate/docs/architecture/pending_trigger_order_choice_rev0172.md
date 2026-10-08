# rev0172 — pending trigger order choice

## Risk cut

The risky seam was trigger placement after simultaneous events: pending triggers were visible as a priority gate, but ordering still collapsed into a deterministic engine policy. That made same-controller ordering and APNAP-block evidence hard to replay or challenge.

## What changed

- `PutPendingTriggersOnStack` actions now carry `trigger_order`, a one-based ordered list of `TriggerRecord` indices.
- Legal-action generation emits explicit order choices for pending triggers, grouping by APNAP player block and allowing each player-controlled block to be ordered independently.
- `put_pending_triggers_on_stack(GameState&, trigger_order)` validates that the order names exactly the current pending triggers, forbids duplicates, and rejects cross-APNAP reordering.
- `ActionReceiptRecord`, canonical action hash/string, and `ActionTrace.v17` preserve the chosen order so replay is not forced to rediscover a hidden default.
- Validation rejects trigger-order receipt drift, wrong-kind trigger-order payloads, duplicate/invalid trigger references, and stack-order mismatches.

## Audit/refactor

The refactor extracted pending-trigger default ordering, APNAP-block validation, trigger-order labels, and order-action generation out of the placement path. The old no-argument API remains as a deterministic fallback for legacy callers, but new replayable transitions should use the explicit order-bearing action.

## Grounding

The local model is grounded in the current online rules shape: pending triggers are put on the stack before priority, and when multiple triggered abilities are pending they are ordered in APNAP blocks with each player choosing the order for triggers they control. Official rules text is not bundled in this datacube.

## Evidence

- `test_pending_trigger_order_choice_preserves_player_selected_sequence`
- `test_pending_trigger_order_rejects_cross_apnap_reordering`
- `ActionTrace.v17` text roundtrip with `trigger_order=` preservation
- release build, 342 C++ tests, 93 scenarios, 12 broad fuzz seeds, rule coverage, and datacube audit
