# Life Cost Payment Receipt Spine — rev0193

rev0193 advances the paid-action risk seam from visible nonmana object payments into life payments. Paying life is not damage and should not be inferred from an ordinary life-loss row: it is a cost payment that must be locked, paid, journaled, and rejectable when the payer lacks the resource.

## What changed

- Added `LifeCostDefinition` and `LifeCostPaymentRecord` for spell and activated-ability life costs.
- Bumped the paid-action audit schemas to `PaidActionDeclarationRecord.v5`, `PaidActionTransactionRecord.v9`, and `PaidActionTransactionJournal.v7`.
- Added `life_payment_*` and `life_amount` fields to committed declaration snapshots and terminal paid-action transaction rows.
- Routed payment through `pay_life_cost`, which writes a pure `LifeChangeRecord` loss, then a `pay_life_cost` event witness, then a typed payment receipt.
- Extended validation so the receipt must match payer, source object, amount, before/after life totals, linked life-change row, event witness, declaration echo, stack-placement echo, transaction echo, and rollback exclusion.
- Refactored the scenario front door so `life_cost=N` on cards and `:life=N` / `:life_cost=N` on activated abilities are first-class scenario DSL inputs.

## Why this matters

This keeps the project on executable semantic progress instead of registry breadth. The risky bug class is subtle: a log can show a player lost life, but an auditor also needs to know whether that loss was caused by damage, effect text, lifelink-adjacent resolution, or paying a locked cost. The life-cost payment receipt makes that distinction durable and hash-sealed.

## Remaining risk

The next consolidation target is a reusable mixed-cost payment kernel. Sacrifice, discard, tap, and life now have typed receipts, but their orchestration still has bespoke branches. A future refactor should pay a locked cost vector in one transaction, with rollback boundaries and receipt ranges produced by a shared planner rather than one-off call sites.
