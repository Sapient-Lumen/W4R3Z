---
status: active_program
claim_kind: routing_protocol
route_role: household_market_extraction_core
canonical_anchor: false
route_refs:
- household_market_extraction_core
- place_public_finance_core
supersedes: null
depends_on:
- household-market-extraction-gate-and-scorecard.md
- transport-access-and-household-cost-router.md
source_refresh_due: 2026-12-31
case_pressure: rev0314_household_market_extraction
---

# Auto-finance and repossession guardrails

Use this router when the household needs a vehicle to reach work, school, care, or services. Car ownership should not be counted as secure household wealth until the loan, insurance, repair, and repossession surfaces are scored.[S254][S255][S266][S267]

## Guardrail fields

- loan-to-value and negative-equity rollover;
- APR, add-ons, warranties, force-placed insurance, and fees;
- payment-to-income after insurance, fuel, repair, and parking;
- repossession notice, cure, storage, auction, deficiency-balance, and complaint rights;
- transit alternatives and job-access geography;
- subgroup incidence and dealer/lender concentration.

## Verdict effects

A case fails the vehicle foothold screen when a necessary car is financed through negative equity or high-cost terms and repossession would predictably cascade into job loss, care interruption, credit damage, or deficiency debt. The cure must combine consumer-credit rails with transportation/place repair; neither alone is enough.[S266][S267]
