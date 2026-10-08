# Session deep audit — rev0314

This pass continued the post-rev0301 shift from broad doctrine expansion to operational cleanup.

## Priority chosen

Wealth/property/rent and procurement/industrial-policy were selected together because both are small enough to finish in one pass but dense enough to hide important assignments: valuation, liquidity, registry privacy, site-rent netting, subsidy conditions, emergency relief recovery, stockpile allocation, publicly funded research access, and classified procurement.

## Completed

- Converted all 6 wealth/property/rent route memos and all 5 procurement/industrial-policy route memos to compact Failure-mode, Recalibration trigger, and Accountability capsule structure.
- Removed legacy wealth anti-pattern and change-trigger sections.
- Replaced wealth cube axes that still hid behind generic rent, compliance, public-loss/private-upside, price-pass-through, or deferral labels.
- Replaced procurement cube axes that still hid behind generic rent, access-exclusion, compliance-theater, price-pass-through, or clawback labels.
- Hardened `tools/audit_axis_hygiene.py` and `tools/audit_prose_bloat.py` to block regression.
- Repaired the stale `docs/README.md` opening so the documentation surface names the active revision.

## Remaining risk

The largest remaining generic-axis residue is now in older public-finance and social-floor families. The next pass should either clear public-finance residual generic channel/remedy labels or do a smaller social-floor compactness/axis cleanup where user fees, municipal bonds, tribal parity, and charitable-public-benefit transfers still carry broad public-service labels.
