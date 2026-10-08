# rev0147 — Tap Event Zone Snapshot

## Mission spine

rev0144 gave plain `tap` log rows structured object/player anchors so automatic payment tap witnesses could identify which source tapped for which payer. rev0146 then made locked-source/step contradictions rejectable inside the typed payment plan. The remaining adjacent trust gap was zone identity: a tap witness could name the same object id and player while failing to prove the exact zone-change incarnation of that permanent.

That matters because MTGSim treats object id plus zone-change index as the durable identity spine for stale-target checks, stack objects, zone-change records, and payment-plan steps. A payment-plan tap witness should therefore bind the `tap` row to the same zone-change snapshot as the planned `ManaPaymentPlanStepRecord`, not merely the same object id.

## Code-bearing change

`EventRecord` now carries `object_zone_change_index` for object-anchored rows. `tap_object(...)` fills that field with the tapped permanent's current `zone_change_index` when it emits the plain `tap` log row through `record_event_with_links(...)`. The field participates in EventRecord hashing, so the journal/state hash now sees tap witness zone identity rather than treating it as prose.

Validation now rejects plain `tap` log rows missing that snapshot with `event_record.tap_log_missing_object_zone_index`. Automatic payment-plan validation also checks that `ManaPaymentPlanStepRecord::tap_event_sequence` points to a tap row whose `object_zone_change_index` matches the step's `source_zone_change_index`, reporting `mana_payment_plan_record.tap_event_witness_zone_index_mismatch` on drift.

## Focused regression

`test_tap_log_event_records_object_and_player_context` now asserts that ordinary tap rows carry the tapped object's zone-change snapshot and that stripping it is invalid. `test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record` corrupts only the witnessed tap event's zone-change snapshot while leaving object, player, step identity, production witness, and paid-record links intact; validation must reject the mismatch specifically.

## Audit stance

This remains a bridge refactor rather than the full typed tap/untap record family. The cube still stores taps as plain log rows, but those rows now carry enough typed identity for automatic payment witnesses to prove object, controller, order, and zone-change snapshot. The future stronger slice should still promote tap/untap into first-class records; rev0147 prevents the current bridge from being identity-weaker than the payment-plan step it certifies.

Audit phrase: tap event zone snapshot.
Audit phrase: tap_event_witness_zone_index_mismatch.
Audit phrase: event_record.tap_log_missing_object_zone_index.
