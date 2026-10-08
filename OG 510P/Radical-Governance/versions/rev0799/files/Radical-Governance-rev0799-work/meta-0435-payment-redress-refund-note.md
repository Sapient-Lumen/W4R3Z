# meta-0435 — Payment redress, compensation, and refund-state note

## Summary

Rev0734 adds a payment-redress / refund layer to the archive. The new rule is: **no repair by payable label**. A public authority must separate debt recognized, claim registered, offer made, offer accepted, payment issued, money received, interim payment, final settlement, challenge, reopening, and remaining tails.

## Added archive notes

- `897` — payment-entitlement, redress, and refund dockets.
- `898` — Post Office Horizon multipath redress case packet.
- `899` — Infected Blood Compensation Authority case packet.
- `900` — IRS Employee Retention Credit refund-tail case packet.

## Added generated layer

- `metadata/payment_redress_tests.json`
- `schema/payment_redress_tests.schema.json`
- `tools/build_payment_redress_tests.py`
- `generated/PAYMENT_REDRESS_TESTS.json`
- `generated/PAYMENT_REDRESS_TESTS.md`

## Design reason

The archive already had entitlement continuity, platform migration, transition receipts, and model-decision tests. It still needed a money-state layer for situations where the public body announces, offers, pays, withholds, disallows, or delays money. Rev0734 adds that layer and tests it across scandal redress, health-harm compensation, and tax-refund administration.
