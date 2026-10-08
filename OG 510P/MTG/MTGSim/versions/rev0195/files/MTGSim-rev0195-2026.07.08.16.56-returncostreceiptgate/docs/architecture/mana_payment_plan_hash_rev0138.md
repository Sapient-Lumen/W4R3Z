# Mana Payment Plan Hash — rev0138

## Mission fit

MTGSim's center remains the trusted transition kernel: an authoritative `StateCore`, an explicit rules-valid choice, one deterministic next `StateCore`, and typed evidence for replay, audit, branching, fuzzing, search, and future agents.

rev0137 made automatic mana-payment plan counts visible on the durable `ManaChangeRecord`. rev0138 makes the next evidence step: the record now carries a stable identity hash for the auto-payment plan itself. Counts are useful, but they cannot distinguish which locked sources and which mana-ability steps were planned. The hash gives future receipt-level cost phases a compact, replay-stable anchor without forcing a full cost-plan object into the public surface yet.

## The gap

Before rev0138, a paid automatic `ManaChangeRecord` could say:

- one mana-ability step was reserved;
- one tap source was locked before planning;
- the payment was automatic.

It still could not say which source was locked, which mana ability was selected, or whether an empty auto-payment plan was intentionally routed through the planner instead of being a manual payment. The final state often revealed the tapped source, but durable payment evidence was still a count-only proof.

## Change

`ManaChangeRecord` now includes:

- `auto_payment_plan_hash`

The new `mana_payment_plan_hash(...)` helper hashes the `MTGSim.ManaAutoPaymentPlan.v1` version string, the locked-source set with source zone-change identities, and the selected mana-ability steps with source identity, ability index, produced mana, and tap-cost status. The payment executor computes that hash before activating the reserved mana abilities, then stores it on the final paid record through `pay_mana_cost_recorded(...)`.

The canonical StateCore hash now includes `auto_payment_plan_hash`, so plan identity evidence participates in replay/audit digests.

## Validation contract

`validate_game_state(...)` now rejects malformed plan hashes with three diagnostics:

- `mana_change_record.plan_hash_on_nonpayment`
- `mana_change_record.plan_hash_without_auto_payment`
- `mana_change_record.auto_payment_plan_hash_missing`

An automatic paid record must carry a nonzero plan hash, even when the plan has zero mana-ability steps and zero locked tap sources because the payment spent pre-existing floating mana through the automatic-payment path. Manual payment, production, and pool-clearing records must keep the hash clear.

## Focused regressions

`test_auto_payment_plan_hash_records_empty_plan_evidence` proves that an automatic payment with no reserved mana-ability steps and no locked tap sources still records a nonzero plan hash and that the validator rejects stripping the hash afterward.

The existing activation and attack tap-cost regressions now also assert `auto_payment_plan_hash != 0`, covering non-empty locked-source plans.

## Refactor value

This is an evidence/refactor slice, not a card-breadth slice. It intentionally stops short of adding a full `CostPaymentPlanRecord`. The value is that every automatic paid `ManaChangeRecord` now has a stable anchor for its plan identity. Future work can lift this hash into a named cost-plan phase carrying the full selected source list, excluded source list, payment order, rollback proof, and causal receipt linkage across casts, activations, and combat declarations.
