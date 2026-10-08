# Sacrifice Cost Payment Receipt — rev0171

rev0171 closes a risky nonmana-cost evidence gap rather than adding another doctrine surface. Paid spell and activated-ability paths already exposed broad paid-action spans and exact sacrifice zone-change witnesses, but the ordered cost payment selection was still reconstructed indirectly from logs and zone ranges.

## Change

`SacrificeCostPaymentRecord` is now a typed receipt for sacrifice costs. It records payer, source object, locked `SacrificeCostDefinition`, ordered selected objects, each selected object's pre-payment zone-change index, the exact zone-change record range created by the payment, the summary `pay_sacrifice_cost` event sequence, and a stable `payment_hash`.

`StackPlacementRecord` now links the sacrifice payment receipt range and stores the linked payment hash for the common one-receipt case. `journal_hash`, `journal_entry_count`, and reserved-capacity accounting include the new receipt vector. During the audit/refactor pass, `journal_reserved_capacity_bytes` was also corrected to include `paid_action_transaction_records`, which had been omitted from the capacity estimate.

## Validator guarantees

The validator now rejects missing sacrifice payment receipt links, tampered receipt hashes, zone/object mismatch between the ordered selected objects and zone-change witness range, payment events outside the paid-action window, wrong payer/source links, and stale pre-payment zone snapshots.

## Grounding

The online rules surface remains a moving reference source rather than an executable spec. The relevant cost-payment seam is the CR 601/602 sequence: determine and lock costs, allow mana abilities where applicable, then pay total costs. This revision does not copy official rules text; it makes MTGSim's local transition evidence more challengeable at that seam.

## Evidence

Release build passed. `340/340` C++ cases passed. `93/93` scenarios passed. `12/12` broad fuzz seeds passed. Datacube audit passed with `0` errors and `0` warnings.
