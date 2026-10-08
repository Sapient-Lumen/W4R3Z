# rev0190 — Nonmana Cost Receipt Transaction Spine

## Mission focus

The highest-risk unfinished seam is still the paid-action body. This is not card-count breadth work: broad card coverage is less strategically valuable than making each legal transition produce typed, durable evidence that survives replay, audit, branching, fuzzing, search, and explanation. rev0190 therefore avoids another registry pass and moves one concrete nonmana-cost witness from placement-local evidence into the paid-action transaction spine.

## Online grounding used this turn

- Official Magic Comprehensive Rules remain the public corner-case reference at `https://magic.wizards.com/en/rules`; this datacube continues not to bundle official rules text.
- The public rules source observed for this session remains the 2026-06-19 rules document path recorded in `data/rules/official/manifest.json` and the ledger source date.
- Broad open-source engines such as XMage already compete on card breadth; MTGSim's stronger lane is auditable deterministic evidence, not raw implemented-card count.
- Research/game interfaces such as OpenSpiel make stable observation/action/result evidence useful for future search and agent integration.

## What changed

`PaidActionDeclarationRecord.v2` now carries `first_sacrifice_cost_payment_record_index`, `sacrifice_cost_payment_record_count`, and `sacrifice_cost_payment_hash`. The declaration sealed at stack placement therefore exposes the exact typed sacrifice-cost payment receipt rather than forcing consumers to infer it from the placement row.

`PaidActionTransactionRecord.v6` carries the same exact receipt range and hash on committed transaction rows. `record_paid_action_transaction_commit(...)` copies the sealed placement receipt into the terminal transaction, and the record hash includes those fields.

`PaidActionTransactionJournal.v4` serializes both top-level transaction fields and the committed declaration snapshot fields: `sacrifice_payment_first`, `sacrifice_payment_count`, and `sacrifice_payment_hash`.

Validation now checks declaration, placement, transaction, and `SacrificeCostPaymentRecord` coherence: receipt range validity, payer/source identity, payment sequence ordering inside the paid-action span, one-row hash agreement, and rollback rows that must not carry committed receipt links.

## Audit/refactor outcome

The datacube audit has a new `nonmana_cost_receipt_transaction_spine` probe covering source, tests, docs, ledger, README, changelog, and artifact report. That is deliberately narrow: it protects the new semantic seam without adding broad doctrine or registry work.

## Still missing

The next risky step is not a card-importer sprint. It is a reusable nonmana cost-plan transaction kernel that can unify sacrifice, discard, tap, counter removal, life payment, mode/target/X choices, additional/alternative costs, and replacement/prevention interposition under one ordered declaration/payment/rollback proof. rev0190 only seals the sacrifice-cost payment receipt as the first vertical slice of that larger cost-plan spine.

## Validation

The release CMake/CTest path passed from the revised tree. Full harness, rule, catalog, audit, and package reports are refreshed under the rev0190 report names before packaging.
