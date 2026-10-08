# rev0146 — Mana Payment Locked Step Guard

## Mission spine

The automatic payment spine now carries a readable `ManaPaymentPlanRecord`, payer-scoped plan hash, produced-mana witnesses, tap-event witnesses, pool-span snapshots, and paid-record backlinks. The next trust gap was not another field: it was consistency between two fields already present in the same plan.

A payment plan can preserve `locked_tap_sources`, the set of tap sources locked out before auto-mana planning, and each planned mana-ability step can say whether it paid a tap cost. Before rev0146, validation proved both halves separately but did not reject a contradictory durable row that locked a source and then reused the same source snapshot as a tap-cost mana step. Live planning avoids that contradiction, but replay/audit consumers should not have to trust live planning when validating a serialized or corrupted cube.

## Code-bearing change

`validate_game_state(...)` now emits `mana_payment_plan_record.locked_source_used_as_tap_step` when a tap-cost `ManaPaymentPlanStepRecord` uses the same object and zone-change snapshot as a `ManaPaymentPlanLockedSourceRecord` in the owning plan. This makes the lock semantics local to the typed plan row: “locked out” cannot coexist with “activated as a tap-cost payment source” for the same payment plan.

## Focused regression

`test_validator_rejects_payment_plan_locked_tap_source_reused_as_step` builds the ordinary safe case first: a tap-cost activated ability source is locked out, and an external battery taps for the mana cost. The valid plan has one locked source and one external tap-cost step. The regression then corrupts only the locked-source entry to point at the step source, repairs the plan hash, repairs the paid-record mirror, and expects the new validator diagnostic. That prevents the test from passing merely because the hash changed.

## Audit stance

This is a validator/refactor slice, not a live-planning behavior change. Its purpose is to keep the durable evidence object honest even if a future serializer, branch merge, or tool edits the plan record. The broader future seam remains a fully typed tap/untap record family, but this guard closes the contradiction currently expressible inside `ManaPaymentPlanRecord` itself.
