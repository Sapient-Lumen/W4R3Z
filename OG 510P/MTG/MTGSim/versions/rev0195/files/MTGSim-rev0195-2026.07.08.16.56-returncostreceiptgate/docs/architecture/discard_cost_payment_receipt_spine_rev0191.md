# Discard Cost Payment Receipt Spine — rev0191
Audit phrase: discard-cost payment receipt.

rev0191 takes the next risky nonmana payment seam: discard-as-cost. The goal is not registry breadth; it is to make a locked cost payment independently challengeable from the paid-action transaction spine.

## What changed

- `DiscardCostDefinition` is now available on card and activated-ability definitions.
- `DiscardCostPaymentRecord` seals the ordered selected hand cards, their zone snapshots before payment, the exact `DiscardRecord` range, the exact hand-to-graveyard `ZoneChangeRecord` range, and the summary `pay_discard_cost` event sequence.
- `StackPlacementRecord` carries discard-cost required/paid flags plus discard-row, zone-change, event, and typed-payment receipt links.
- `PaidActionDeclarationRecord.v4` and `PaidActionTransactionRecord.v8` echo the same discard payment range/hash.
- `PaidActionTransactionJournal.v6` exports top-level and committed-snapshot `discard_payment_*` fields while the parser still accepts legacy v4.

## Validator posture

The validator rejects drift between the cost-payment row and its witnesses: wrong selected card, wrong payer/source, non-cost discard rows, hand-to-non-graveyard movement, missing `pay_discard_cost` event witness, missing typed payment row, missing hash, declaration mismatch, transaction mismatch, and rollback rows that carry committed discard-payment links.

## Why this was prioritized

Discard is a hidden-zone action that becomes public only when payment moves the selected card. That makes it riskier than another passive metadata pass: a simulator can appear to move the right object while losing the reason it moved. The receipt spine preserves both semantic intent and physical movement so later replay/search/agent consumers do not have to infer cost payment from prose logs.

## Still missing

- Mixed nonmana cost-plan ordering across sacrifice, discard, tap, counters, life, and future costs.
- Random/opponent-selected discard payment variants.
- Characteristic-conditional discard costs under hidden-zone replacement rollback.
- Importer status gates that distinguish text parsed, semantic payment implemented, regression tested, and fuzz covered.
