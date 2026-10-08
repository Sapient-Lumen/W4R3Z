# Mana Payment Plan Evidence — rev0137

## Mission fit

MTGSim's center remains the trusted transition kernel: an authoritative `StateCore`, an explicit rules-valid choice, one deterministic next `StateCore`, and typed evidence for replay, audit, branching, fuzzing, search, and future agents.

rev0134 made paid cast and activation bodies transactional. rev0135 corrected an inner sacrifice-payment order. rev0136 locked nonvigilance attackers out of self-funding their own attack costs. rev0137 follows the same line by making the auto-payment plan itself inspectable in the typed mana-payment record, not only implied by helper names or `mana_auto_plan` event prose.

## The gap

Before rev0137, the engine could prove a paid activation or attack succeeded and the tests could inspect the final tapped source, but the `ManaChangeRecord` for the actual payment did not carry the cost-plan evidence that mattered:

- how many mana-ability steps were reserved by the auto-payment planner;
- how many tap sources were locked out before that planner ran;
- whether any plan metadata was accidentally attached to a manual payment, production record, or pool-clearing record.

That left the transaction body with a small audit asymmetry: the event stream could say a planner ran, but the durable typed `ManaChangeRecord` did not itself explain the payment plan that produced the spent mana.

## Change

`ManaChangeRecord` now carries two auto-payment plan fields on paid records:

- `auto_payment_mana_ability_count`
- `auto_payment_locked_tap_source_count`

`pay_mana_cost_with_mana_abilities_excluding_tap_sources(...)` passes `plan.size()` and `locked_tap_sources.size()` into `pay_mana_cost_recorded(...)`, and `pay_mana_cost_recorded(...)` stores those counts only when the resulting `ManaChangeRecord` is an automatic payment.

The stable hash includes both new fields, so payment-plan evidence is part of the canonical StateCore identity and replay/audit digest surface.

## Validation contract

`validate_game_state(...)` now rejects three malformed states:

- `mana_change_record.auto_payment_on_nonpayment`: `auto_payment=true` outside a paid record;
- `mana_change_record.plan_metadata_on_nonpayment`: nonzero plan metadata outside a paid record;
- `mana_change_record.plan_metadata_without_auto_payment`: nonzero plan metadata without `auto_payment=true`.

The existing mana record regression now checks that manual production/payment records carry no auto-plan metadata and injects a malformed paid record to prove the validator catches plan metadata without auto-payment.

## Focused regressions

The two previous tap-lock regressions now also assert typed plan evidence:

- `test_activated_ability_tap_cost_locks_source_before_auto_mana_payment` confirms the activation payment records one external mana-ability step and one locked tap source.
- `test_attack_cost_locks_nonvigilance_attackers_out_of_auto_mana_payment` confirms the attack-cost payment records one external mana-ability step and one locked nonvigilance attacker tap source.

## Refactor value

This is intentionally a small evidence/refactor slice, not a larger card-breadth change. It turns the rev0134/rev0136 helper-level lock into data that future cost-plan phases can promote without changing the public test seam again.

The next semantic move should still be a named cost-plan object or receipt phase carrying selected sources, excluded sources, payment order, rollback proof, and causal receipt linkage for casts, activations, and combat declarations. rev0137 simply gives that future object a typed anchor already present in every auto-paid `ManaChangeRecord`.
