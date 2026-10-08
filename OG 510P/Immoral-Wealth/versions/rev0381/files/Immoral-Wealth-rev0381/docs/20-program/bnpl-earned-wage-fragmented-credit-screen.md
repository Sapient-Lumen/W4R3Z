---
status: active_program
claim_kind: screening_protocol
route_role: household_market_extraction_core
canonical_anchor: false
route_refs:
- household_market_extraction_core
- measurement_uncertainty_core
supersedes: null
depends_on:
- household-market-extraction-gate-and-scorecard.md
- top-tail-audit-and-uncertainty-bounds.md
source_refresh_due: 2026-12-31
case_pressure: rev0314_household_market_extraction
---

# BNPL and earned-wage fragmented-credit screen

Use this screen when small app-based or payroll-linked obligations are common. The key question is not whether any single transaction is large; it is whether product fragmentation hides cumulative payment load and weakens the household's capacity to build a first buffer.[S264][S265][S272]

## Required checks

| Check | Why it matters |
|---|---|
| total active obligations across providers | prevents product-by-product false pass |
| repeat use and loan count | distinguishes convenience from chronic liquidity gap |
| late fees, charge-offs, dispute/refund rights | reveals downside costs |
| fee/tip/expedite pressure | makes wage access cost visible |
| payroll priority and recourse | tests whether wages are pre-committed |
| credit reporting and correction | tests credit-file damage or invisibility |
| regulator data access | tests measurement and enforcement capacity |

## Routing

- **Convenience use with clear total cost and low repeat distress:** watch.
- **Necessity use with repeat borrowing:** Gate 16 warning/fail.
- **Poor visibility to household or regulator:** Gate 10 evidence debt.
- **Payroll deductions or employer partnership with weak safeguards:** Gate 14 workplace-power watch.
