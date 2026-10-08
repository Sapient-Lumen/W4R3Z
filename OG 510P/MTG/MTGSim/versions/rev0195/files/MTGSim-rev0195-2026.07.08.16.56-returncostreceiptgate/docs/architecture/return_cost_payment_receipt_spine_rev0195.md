# rev0195 — Return Cost Payment Receipt Spine

## Mission seam

The riskiest unfinished part of the cube is still not card breadth; it is proving that a legal paid action paid exactly the locked costs and nothing else. Return-to-hand costs are especially easy to mis-audit because they look like ordinary battlefield-to-hand movement unless the payment spine binds selection, movement, and event witness together.

rev0195 narrows that seam. Return costs now produce a first-class `ReturnCostPaymentRecord` that seals the payer, source object, locked `ReturnCostDefinition`, selected returned objects, selected pre-payment zone snapshots, battlefield-to-hand zone-change witness range, ordered `pay_return_cost` event sequence, and stable payment hash.

## What changed

- Bumped paid-action schemas to `PaidActionDeclarationRecord.v7`, `PaidActionTransactionRecord.v11`, and `PaidActionTransactionJournal.v9`.
- Added return-cost fields to stack placements, declarations, transactions, committed declaration snapshots, journal export, journal parse, and journal verification.
- Added validator diagnostics for `return_cost_payment_record.hash_mismatch`, `return_cost_payment_record.zone_change_shape_mismatch`, `stack_placement_record.missing_return_cost_payment_hash`, `stack_placement_record.missing_return_cost_event_witness`, and `paid_action_transaction_record.return_payment_hash_mismatch`.
- Added focused C++ coverage in `test_paid_action_phase_records_return_cost_for_activated_ability` so the receipt path is exercised by executable semantics rather than only schema probes.

## Why it matters

This keeps return-to-hand costs on the same evidence rail as sacrifice, discard, tap, life, and loyalty costs. The transaction can now be challenged at the receipt level: was the selected object legal, did it start in the sealed zone snapshot, did it move battlefield→hand, did the event witness match the payment, and did every placement/declaration/transaction hash agree?

## Still intentionally deferred

The generic return-cost definition is deliberately narrow: count, type mask, and optional tapped requirement. Richer costs such as “return a permanent you control of a subtype,” “return this object,” choice prompts, alternate costs, and replacement/prevention interactions should be added only after the same receipt spine can carry those predicates explicitly.

Audit vocabulary: this revision is the return-to-hand cost receipt gate; it prevents return costs from hiding as generic battlefield-to-hand movement inside a paid-action window.
