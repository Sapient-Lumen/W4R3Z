---
status: program_tool
claim_kind: scoring_protocol
route_role: public_balance_sheet_core
canonical_anchor: false
route_refs:
- public_balance_sheet_core
- certification_core
supersedes: null
depends_on:
- scoreboard-schema.json
- public-balance-sheet-seniority-waterfall.md
source_refresh_due: 2027-03-31
---

# Gate 20 public-balance-sheet register and subgates

Gate 20 asks whether public assets, fiscal capacity, guarantees, social-insurance promises, public credit, central-bank capacity, crisis tools, and tax expenditures operate as real ordinary-claimant counterweights or as hidden support for private asset and creditor claims.

## Gate 20 certification rule

Do not certify a public-counterweight pass unless the case has a public-balance-sheet register, subgate findings, and a seniority waterfall. The case must show who benefits, who pays, who is cut, whether the public receives upside, and whether ordinary claimants can enforce protection under stress.

## Subgates

| Subgate | Name | Blocking question |
|---|---|---|
| 20A | Public debt and interest capacity | Do debt service and interest-rate risks crowd out floors, services, enforcement, public investment, or countercyclical repair? |
| 20B | Claim security | Are social-insurance, pension, health, disability, care, or public-benefit promises financed and legally durable enough to count as wealth substitutes? |
| 20C | Contingent liabilities and guarantees | Are guarantees, insurance funds, credit programs, SOEs, PPPs, disaster obligations, and legal claims disclosed and stress-tested? |
| 20D | Crisis backstop governance | Who is rescued under stress, under what terms, with what haircut, condition, sunset, and report? |
| 20E | Public-upside recovery | Does the public receive warrants, equity, fees, clawbacks, senior claims, recoveries, or other upside when it absorbs downside? |
| 20F | Central-bank quasi-fiscal visibility | Are remittance losses, deferred assets, interest-on-reserves distribution, facilities, and asset-price stabilization effects visible? |
| 20G | Public asset and sovereign wealth governance | Are public assets rule-bound, professionally managed, protected from raiding, and linked to ordinary claimants? |
| 20H | Generational and intergovernmental incidence | Does repair fall on younger cohorts, renters, disabled claimants, caregivers, migrants, municipalities, or future taxpayers? |

## Required register object

Each relevant scoreboard must include `public_balance_sheet_register` entries with:

```json
{
  "exposure_name": "...",
  "legal_authority": "...",
  "claimant_perimeter": "...",
  "beneficiaries": {"direct": ["..."], "indirect": ["..."]},
  "maximum_exposure": "...",
  "expected_loss": "...",
  "stress_scenario": "...",
  "correlation_with_household_need": "low|medium|high|unknown",
  "funding_source": "fees|assessments|appropriation|central_bank|future_debt|mixed|unknown",
  "loss_sharing": "...",
  "public_upside_recovery": "fees|warrants|equity|clawbacks|none|unknown|mixed",
  "ordinary_claimant_protection": "...",
  "sunset_or_review": "...",
  "evidence_quality": "direct|proxy|inference|missing",
  "source_ids": ["S..."]
}
```

## Evidence minimum

A Gate 20 case requires direct or proxy evidence for exposure scale, legal authority, stress scenario, funding source, and at least one incidence channel. If ordinary-claimant protection, public-upside recovery, or residual-payer identity is missing, the case cannot receive a comfort verdict.[S345][S346][S350][S351][S357][S360][S363][S373][S375][S376][S378][S381][S382]

## Case routing

Use this tool for federal debt/interest cases, social-insurance and pension cases, deposit insurance and bank backstops, housing-finance guarantees, central-bank quasi-fiscal surfaces, sovereign wealth funds, climate residual insurance, stablecoins and cash-like private claims, private credit and nonbank finance, student loans, PPPs, SOEs, legal judgments, disaster funds, and tax expenditures.

Rev0355 adds River Bend as a public-instrument ladder case: utility announcement, IDB/PILOT revenue architecture, distribution schedule, rebate sequencing, and official public-record route are evidence leads, not closure.
