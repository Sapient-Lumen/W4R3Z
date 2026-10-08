# Mana Payment Producer Backlink — rev0141

Datacube: `MTGSim-rev0141-2026.07.06.12.49-paymentproducerbacklink.zip`

## Deep-read outcome

rev0140 turned each readable automatic mana-payment plan step into an execution witness by adding `produced_mana_change_record_index` on `ManaPaymentPlanStepRecord`. That made the plan able to point to the exact `Produced` `ManaChangeRecord` row that executed the chosen mana ability, but the produced row itself still did not prove that it belonged to a plan step.

rev0141 closes that one-way evidence seam. Produced `ManaChangeRecord` rows created while executing an automatic payment plan now carry two backlink fields:

- `auto_payment_producer_plan_record_index`: the one-based `ManaPaymentPlanRecord` that owns the producing step.
- `auto_payment_producer_plan_step_index`: the one-based step slot inside that plan record.

The witness is now bidirectional: `ManaPaymentPlanRecord → ManaPaymentPlanStepRecord → Produced ManaChangeRecord → ManaPaymentPlanRecord/step`.

## Code-bearing change

`pay_mana_cost_with_mana_abilities_excluding_tap_sources(...)` already records each planned mana-ability step after `activate_mana_ability(...)` produces mana. rev0141 now immediately fills the produced record's producer backlink while the step index and plan record index are still in scope. The full `ManaChangeRecord` stable hash includes both backlink fields, so StateCore snapshots and replay roots notice backlink drift.

The plan identity hash remains a pre-execution seal. The producer backlink fields are deliberately not part of `ManaAutoPaymentPlan.v2` identity because they are execution witnesses, not planner inputs.

## Validator surface

`validate_game_state(...)` now rejects:

- a plan step whose produced `ManaChangeRecord` does not point back to the same plan and one-based step;
- a produced row carrying only one side of the producer backlink;
- a backlink to a nonexistent plan record;
- a backlink to a nonexistent step slot;
- a linked plan step that points somewhere other than the produced row;
- producer backlink fields on non-`Produced` mana records.

## Regression focus

`test_auto_payment_produced_mana_records_bidirectional_plan_step_link` proves a Forest-based automatic payment has both directions wired and corrupts incomplete, out-of-range, and wrong-kind backlink cases. `test_auto_payment_plan_record_links_locked_sources_steps_and_paid_record` also asserts that the broader readable plan/payment regression carries the reverse produced-row witness.

## Audit/refactor note

This is a trust-spine refactor, not card-breadth expansion. The mission remains trusted transitions: a legal choice produces one deterministic next StateCore and typed evidence sufficient for replay, audit, branching, fuzzing, and future agents. rev0141 reduces the need for replay consumers to infer which plan step produced a mana row by making the link explicit in both directions.

## Residual seam

The mana-payment subspine now has readable plan records, plan hashes, execution witnesses, and bidirectional producer backlinks. The next semantic seam is broader cost-plan unification: tap, sacrifice, mana, alternative/additional costs, and combat declaration payments still do not share one named `CostPaymentPlanRecord` with rollback phases and receipt linkage across all paid action families.
