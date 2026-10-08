# Mana Payment Step Witness — rev0140

## Mission fit

The paid-action thread is moving from “the action did not leak” toward “the action body can explain exactly how it paid.” rev0139 introduced readable `ManaPaymentPlanRecord` evidence for automatic non-free mana payments. rev0140 adds the missing execution witness: every selected mana-ability step now points to the produced `ManaChangeRecord` that executed it.

This keeps MTGSim aligned with the trusted-transition mission: an authoritative `StateCore` plus a legal choice yields one next `StateCore` and typed evidence a replay/search/agent consumer can inspect without scraping prose.

## New field

`ManaPaymentPlanStepRecord` now includes:

- `produced_mana_change_record_index`: one-based index of the `Produced` `ManaChangeRecord` created by the selected mana ability.

The automatic payment executor records the plan first, activates each selected mana ability, then fills the corresponding step witness link immediately after the produced mana row appears. The final paid `ManaChangeRecord` still links back to the plan via `auto_payment_plan_record_index`, and the plan still links forward through `paid_mana_change_record_index`.

The intended walk is now:

`ManaPaymentPlanRecord → ManaPaymentPlanStepRecord → Produced ManaChangeRecord → Paid ManaChangeRecord`

## Hash boundary

`ManaAutoPaymentPlan.v2` remains a pre-execution plan identity seal. It hashes:

- cost,
- locked tap-source identities and zone-change snapshots,
- selected mana-ability source identity,
- selected source zone-change snapshot,
- selected mana ability index,
- selected produced-mana payload,
- tap-cost flag.

It intentionally does **not** hash `produced_mana_change_record_index`, because that index is an execution witness filled after the plan is recorded. The full `ManaPaymentPlanStepRecord`, including the witness index, remains part of the canonical `StateCore` hash through the ordinary journal hash path.

`mana_payment_plan_record_identity_hash(...)` exposes the pre-execution identity hash for validation and audit consumers.

## Validator surface

`validate_game_state(...)` now rejects:

- `mana_payment_plan_record.identity_hash_mismatch`,
- `mana_payment_plan_record.step_missing_produced_link`,
- `mana_payment_plan_record.step_link_not_production`,
- player/source/zone/ability/pool mismatches between plan step and produced record,
- production before the plan or after the paid record,
- out-of-order production witnesses,
- duplicate witness rows shared by multiple steps.

## Residual seam

The plan now proves selected mana-ability execution, but the broader paid action still has separate bodies for mana, tap, sacrifice, stack placement, and combat declaration payments. The next semantic target is a higher-level cost-payment phase record that groups all cost components under a single rollback/receipt spine.
