# Session deep audit — rev0313

This pass continued the post-rev0301 shift from doctrine expansion to operational cleanup.

## Priority chosen

Financial-system-risk was selected because it is operationally dense and failure-prone: public guarantees, stablecoin reserves, custody freezes, de-risking false positives, fiscal opacity, reinsurance backstops, event-contract addiction, creditor priority, and policyholder surplus can all look like ordinary market pricing unless the cube names the rail and evidence.

## Completed

- Converted all 8 financial-system route memos to compact Failure-mode, Recalibration trigger, and Accountability capsule structure.
- Removed legacy financial anti-pattern taxonomies from the route memos.
- Replaced financial cube axes that still hid behind `rent_extraction`, `public_loss_private_upside`, `compliance_theater`, `platform_account`, `legal_risk_transfer`, `fee_surcharge`, `clawback`, or `disclosure`.
- Hardened `tools/audit_prose_bloat.py` and `tools/audit_axis_hygiene.py` to block regression.

## Remaining risk

The next compactness/specificity targets are wealth/property/rent and public-procurement/industrial-policy. Wealth/property is dense around valuation, liquidity, hardship, register privacy, and site-rent netting. Procurement is dense around emergency relief, stockpiles, public-funded research, classified contracting, and public-upside clawback.
