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
- gate-20-public-balance-sheet-register-and-subgates.md
source_refresh_due: 2027-03-31
---

# Public-balance-sheet seniority waterfall

The seniority waterfall is the rev0319 answer to the question: **whose claim is treated as money-good under public stress?**

## Required waterfall levels

Every Gate 20 scoreboard should list the following claimant ranks, even if the answer is unknown:

1. **Automatically protected claimants** — paid or stabilized without discretionary repair.
2. **Liquidity-protected private claimants** — protected to preserve payment, credit, housing, market, or macro stability.
3. **Appropriation-contingent public claimants** — dependent on future budget or legislative action.
4. **Haircut-exposed claimants** — exposed to benefit cuts, service cuts, deductibles, rate shock, nonrenewal, discharge denial, or reduced claim value.
5. **Residual payers** — pay through taxes, fees, assessments, inflation, lower services, lower public investment, or future debt.
6. **Public-upside receivers** — receive recoveries, warrants, equity, fees, clawbacks, senior claims, or none.

## Scoreboard object

The machine object is `seniority_waterfall`, an array of entries:

```json
{
  "rank": 1,
  "claimant_class": "...",
  "claim_status": "automatic|liquidity_protected|appropriation_contingent|haircut_exposed|residual_payer|public_upside_receiver|unknown",
  "stress_treatment": "...",
  "evidence_quality": "direct|proxy|inference|missing",
  "source_ids": ["S..."]
}
```

## Comfort rule

A case cannot count a public balance sheet as an ordinary-claimant counterweight when liquidity-protected private claims are senior to social-insurance, care, disability, housing, worker, renter, municipal, or future-cohort claims unless the package also includes public-upside recovery and enforceable ordinary-claimant protection.

## Diagnostic questions

- Are creditors, asset holders, or intermediaries made whole faster than households?
- Are fees, assessments, premiums, user charges, or tax expenditures doing hidden fiscal work?
- Are public services cut while protected private claims remain money-good?
- Are social-insurance promises treated as obligations or as politically contingent ambitions?
- Do future cohorts inherit debt service without receiving asset claims?
- Does the public receive upside after rescuing private downside?

This waterfall should be read with the fiscal-risk register and the Gate 20 subgate screen.[S345][S346][S351][S357][S363][S373][S375][S376][S378][S381][S382]

Rev0355 adds a rule of reading for large-load projects: private creditor protection and gross local revenue are separate from public hold-harmless; signed public instruments must show who is senior under cancellation, delay, underload, tax-rebate, water, and ratebase stress.
