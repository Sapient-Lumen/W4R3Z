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


# Public pension, social-insurance, and claim-security router

Use this router when public or pension promises are being counted as wealth substitutes.

## Decision path

1. Identify the claim: old-age, disability, survivor, health, private-pension guarantee, public-worker pension, or tax-favored retirement account.
2. Score legal durability and automatic benefit formula.
3. Score actuarial balance, trust-fund depletion, funded ratio, and assumption stress.
4. Identify the adjustment mechanism: revenue, benefit formula, retirement age, COLA, eligibility, contributions, general revenue, or service cuts.
5. Score incidence by cohort, gender, caregiver status, disability, migrant status, income, and public/private employment.
6. Decide whether the claim counts as a real floor, a vulnerable promise, or proof debt.[S351][S352][S353][S355][S356]

No pension promise should count as lower-half wealth unless the claimant can reasonably rely on it when crossing retirement, disability, survivor, and care-need moments.
