---
status: active_bridge
claim_kind: program_router
route_role: public_balance_sheet_core
canonical_anchor: false
route_refs:
- public_balance_sheet_core
- case_calibration_core
supersedes: null
depends_on:
- public-balance-sheet-gate-and-sovereign-backstop-scorecard.md
source_refresh_due: 2027-03-31
case_pressure: rev0318_public_balance_sheet
---


# Fiscal-risk register and contingent-liability router

Use this router when a case contains guarantees, insurance funds, disaster aid, PPPs, SOEs, GSEs, student loans, deposit insurance, public pensions, emergency lending, or legal judgments.

## Minimum register fields

1. legal authority and claimant perimeter;
2. maximum exposure and expected exposure;
3. stress scenario and correlation with recession/disaster/financial crisis;
4. fee, premium, assessment, or appropriation source;
5. beneficiaries by income/wealth/group/place;
6. loss-sharing rules for private owners, creditors, managers, and intermediaries;
7. public-upside instruments: warrants, equity, recoveries, fees, or clawbacks;
8. reporting cadence and independent audit;
9. sunset, renewal, and emergency extension rules.[S350][S361][S362][S363][S364]

Route to Gate 20 when any major guarantee is implicit, unpriced, or likely to favor asset holders over ordinary claimants.


## rev0319 operationalization addendum

rev0319 addendum: every fiscal-risk register entry should now be mirrored in `public_balance_sheet_register` with claimant perimeter, residual payer, public-upside recovery, and seniority-waterfall treatment.
