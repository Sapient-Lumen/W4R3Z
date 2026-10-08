# rev0143 — Mana Payment Pool Span

## Mission slice

rev0142 made automatic mana-payment plan steps readable as execution witnesses: each planned step can name its tap event and produced `ManaChangeRecord`, and the final paid row points back to the typed plan. One important context fact was still implicit: the plan did not preserve the player's mana pool at the moment planning began, nor the exact pool handed into the final paid `ManaChangeRecord` after automatic mana abilities ran.

rev0143 adds that pool-span witness to `ManaPaymentPlanRecord`:

- `pool_before_plan` snapshots the player's floating mana before automatic payment planning records the selected plan.
- `pool_before_payment` snapshots the pool after executing the selected mana-ability steps and immediately before the final paid `ManaChangeRecord` spends the cost.
- `ManaAutoPaymentPlan.v3` includes `pool_before_plan` in the plan identity hash, so the same locked-source/step list no longer claims to be the same plan when it was selected from a different starting pool.

## Why this matters

The hash and step witnesses proved which sources were selected and which production rows executed them. Without a starting-pool witness, an auditor still had to infer whether a plan used pre-existing floating mana, overproduced mana, or selected fewer steps because the pool already covered part of the cost. Without a before-payment pool witness, the plan did not directly name the exact pool state the final payment consumed.

The new span makes automatic payment evidence answer three questions without replaying prose logs:

1. What pool existed before the plan was selected?
2. Which planned steps changed that pool before payment?
3. Did the final paid row consume the same pool the plan says it handed off?

## Invariants

- `pool_before_plan` is part of the `ManaAutoPaymentPlan.v3` identity hash.
- `pool_before_plan + sum(step.produces)` must equal `pool_before_payment`.
- `pool_before_payment` must match the linked automatic paid `ManaChangeRecord::pool_before`.
- The paid `ManaChangeRecord` must still link back to the same plan record and hash.

## Boundaries

This slice does not introduce spending restrictions, mana-purpose tags, floating-mana expiration provenance, or cost-modifier records. It is a narrow evidence refactor that makes the current automatic payment plan self-contained enough for replay/audit consumers to distinguish starting-pool context from planned production.
