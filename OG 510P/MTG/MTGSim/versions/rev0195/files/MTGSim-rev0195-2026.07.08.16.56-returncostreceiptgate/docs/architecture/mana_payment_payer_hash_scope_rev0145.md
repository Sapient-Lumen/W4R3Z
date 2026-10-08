# rev0145 — Mana Payment Payer Hash Scope

## Mission spine

The automatic mana-payment evidence spine now has readable plan rows, pool-span witnesses, produced-mana backlinks, and tap-event identity anchors. The remaining adjacent hash-domain weakness was payer scope: two different players could execute identical empty auto-payment plans with the same cost and starting pool and receive the same `plan_hash` payload even though the typed `ManaPaymentPlanRecord` rows identified different payers.

rev0145 advances the plan identity namespace to `MTGSim.ManaAutoPaymentPlan.v4` and hashes `PlayerId` before the cost, pool, locked tap-source set, and selected mana-ability step identity. The paid `ManaChangeRecord` still mirrors the plan hash, and `mana_payment_plan_record_identity_hash(...)` now recomputes the same payer-scoped identity payload from the typed plan record.

## Why this matters

The cube is increasingly useful for replay, branch/search, and future multi-agent audit consumers. Those consumers should not need to combine an external payer field with a plan hash to avoid ambiguity. The hash itself should describe the identity domain it seals. A payer-scoped plan hash means identical empty plans are intentionally different when different players pay them.

## Code-bearing changes

- Changed `mana_payment_plan_hash_from_records(...)` to accept `PlayerId` and include it in the stable hash stream.
- Advanced the plan namespace from `MTGSim.ManaAutoPaymentPlan.v3` to `MTGSim.ManaAutoPaymentPlan.v4`.
- Routed both live auto-payment planning and `mana_payment_plan_record_identity_hash(...)` through the payer-scoped hash helper.
- Documented the payer-scoped hash expectation directly in `ManaPaymentPlanRecord`.

## Focused regression

`test_auto_payment_plan_hash_is_payer_scoped_for_empty_plans` constructs two automatic payments with the same empty plan shape: one green floating mana, one green cost, no locked tap sources, and no selected mana-ability steps. Player 1 and player 2 now receive distinct plan hashes, and the validator rejects a changed `ManaPaymentPlanRecord::player` because its existing hash no longer matches the typed identity payload.

## Audit stance

This slice intentionally does not add a new typed record family. It tightens the existing seal domain and keeps the automatic payment plan as the durable, readable evidence object. The future work remains a typed tap/untap record family, but payer scoping is the smaller trust fix directly adjacent to the current hash spine.
