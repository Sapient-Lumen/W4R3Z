# Tap Cost Payment Receipt Spine — rev0192

rev0192 advances the same high-risk paid-action seam without adding registry breadth: tap-as-cost is now a typed payment receipt instead of only a plain `tap` log witness on `StackPlacementRecord`.

## What changed

- Added `TapCostPaymentRecord`, sealing payer, source object, source zone-change snapshot, before/after tapped flags, the exact tap `EventRecord` sequence, and a stable payment hash.
- Added tap payment range/hash fields to `StackPlacementRecord`, `PaidActionDeclarationRecord.v4`, and `PaidActionTransactionRecord.v8`.
- Bumped new paid-action journal exports to `PaidActionTransactionJournal.v6` and serialized `tap_payment_*` fields on both top-level transaction rows and committed declaration snapshots.
- Replaced direct activated-ability tap-cost mutation with `pay_tap_cost`, so the engine writes the typed receipt at the same moment the tap EventRecord is emitted.
- Refactored the stack-placement identity hash to include the previously under-covered discard payment fields alongside the new tap payment fields.

## Why this is the risk seam

Rule payment order is the dangerous part of this cube: the source is already on the stack for spells, choices are locked, mana abilities may be activated, and then nonmana costs happen before the final placement/transaction receipt. A tap cost is especially easy to under-audit because a tap log row looks sufficient until an activated ability, auto-mana planning, or tamper case needs to prove that the tap was *the cost payment* and not merely a nearby state change.

The revision keeps the low-level tap row but makes it subordinate to a typed payment receipt. Auditors can now challenge the tap cost through the declaration, placement, terminal transaction, journal export, and validator rather than inferring intent from event text.

## Validation shape

The validator now rejects:

- tap payment record hash drift;
- missing typed tap payment receipts on paid tap costs;
- tap receipts outside the locked-cost/payment/placement window;
- payer/source/source-zone mismatches between payment receipt, tap EventRecord, declaration, placement, and transaction;
- rollback rows that carry committed tap payment receipt links.

The focused C++ coverage in `test_paid_action_phase_records_mana_and_tap_receipts_for_activated_ability` now asserts the full receipt spine and corrupts both the old plain tap witness and the new typed payment row.

## Deliberate non-goals

This is not registry breadth and not a claim of broad activated-ability completeness. The goal is to make one risky cost-payment seam durable and challengeable before widening the card surface. Future work should continue extracting a reusable nonmana cost-plan kernel so tap, sacrifice, discard, counter, life, and mixed additional costs share the same ordering and rollback skeleton.

Exact audit phrase: tap-cost payment receipt.
