# rev0194 — Loyalty Cost Payment Receipt Spine

Audit phrase: loyalty-cost payment receipt.

## Risk addressed

The previous loyalty ability path already used a typed `CounterChangeRecord` for adding or removing loyalty counters, but the paid-action transaction spine still had to infer that the counter mutation was *the cost payment* from a broader paid-action counter-change range plus `loyalty_cost_paid` flags. That inference is fragile: a future loyalty ability implementation could add counters as an effect, replacement, damage result, or cleanup row inside the same action window and accidentally satisfy a generic span check.

rev0194 narrows that seam. Loyalty costs now produce a first-class `LoyaltyCostPaymentRecord` that seals the payer, planeswalker source, source zone-change snapshot, signed loyalty cost delta, before/after loyalty totals, exact `CounterChangeRecord` index, ordered event sequence, and stable payment hash.

## Code-bearing changes

- Bumped paid-action schemas to `PaidActionDeclarationRecord.v6`, `PaidActionTransactionRecord.v10`, and `PaidActionTransactionJournal.v8`.
- Added `GameState::loyalty_cost_payment_records`, public count/latest/hash accessors, and `MTGSim.LoyaltyCostPaymentRecord.v1` hashing.
- Wired loyalty payments through declaration, stack placement, terminal transaction, committed declaration snapshot, journal serialization, journal parsing, and fail-closed journal verification.
- Hardened validation so the receipt must match the loyalty counter-change row: kind, counter type, amount, before/after totals, payer, source object, source incarnation, `cost_payment=true`, no damage/cleanup metadata, and `loyalty_cost_paid` `EventRecord` witness.
- Extended the focused loyalty paid-action regression with hash, counter-link, stack-hash, and event-witness tamper cases.

## Why this is forward momentum rather than registry work

This pass does not add card breadth. It converts an already-modeled, high-risk rules action into replayable payment evidence and removes dependence on a generic counter-change span for proving loyalty-cost payment. The datacube can now distinguish a loyalty counter movement that paid CR 606 loyalty cost from a loyalty counter movement that merely occurred during the same activated-ability transaction.

## Remaining risk

The model still supports one scaffolded loyalty ability per definition and does not yet represent multiple printed loyalty abilities, static timing exceptions, copy/control-change wrinkles, or every counter replacement effect. Those are future semantic breadth. The core cost-payment witness is now ready for that breadth instead of being another generic counter span.
