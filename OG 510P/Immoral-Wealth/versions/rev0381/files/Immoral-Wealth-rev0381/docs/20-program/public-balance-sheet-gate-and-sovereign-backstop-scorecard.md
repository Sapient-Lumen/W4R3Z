---
status: active_bridge
claim_kind: program_protocol
route_role: public_balance_sheet_core
canonical_anchor: false
route_refs:
- public_balance_sheet_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2027-03-31
case_pressure: rev0318_public_balance_sheet
---


# Public balance-sheet gate and sovereign-backstop scorecard

## Gate 20 — public balance sheet, sovereign backstop, and fiscal-risk incidence

A case cannot pass when the public balance sheet quietly protects asset holders, creditors, intermediaries, or older/insider cohorts while ordinary claimants face weaker floors, thinner public services, higher fees, or future claim haircuts.

Gate 20 asks: **Who owns the upside, who receives the backstop, who pays the interest or assessment, and whose claims are cut when the public balance sheet is stressed?**

## Scorecard fields

| Field | Pass | Warning | Fail |
|---|---|---|---|
| public balance-sheet gate | public assets/liabilities transparent and incidence-scored | partial disclosure | hidden public risk drives comfort verdict |
| debt/interest crowdout | debt supports capacity and interest is manageable | rising pressure | interest/services tradeoff already visible |
| fiscal risk register | comprehensive, published, stress-tested | partial | guarantees/backstops absent from budget view |
| contingent liabilities | quantified, priced, monitored | partial | implicit guarantees dominate |
| social-insurance claim security | financed and politically durable | projected depletion/repair needed | likely sudden benefit or eligibility haircut |
| pension funding risk | assumptions conservative, funding path credible | material underfunding | adjustment likely falls on services/workers/retirees |
| deposit insurance | prefunded, assessed, transparent, loss-sharing rules | prefunded but systemic exceptions likely | implicit blanket backing without fee/upside recovery |
| crisis backstop | conditions, haircuts, warrants/equity, sunset, reports | partial | rescue priority without public upside |
| public credit/guarantees | subsidy and fair-value risk visible | partial | credit support treated as free |
| housing-finance guarantees | affordability and taxpayer risk jointly scored | strong but opaque exposure | guarantee benefits owners/intermediaries without loss discipline |
| sovereign wealth/public assets | rule-bound, transparent, claimant-linked | strong asset but claimant link weak | patronage, raiding, or elite project capture |
| central-bank quasi-fiscal | losses/remittance effects disclosed | disclosed but not incidence-scored | ignored because off-budget |
| generational incidence | adjustment burden explicit and progressive | unclear | younger/lower-wealth cohorts absorb repair |

## Certification effects

- Gate 20 hardens Gate 7 because public/common wealth counts only when balance-sheet claims are real and governed.
- Gate 20 hardens Gate 15 because fiscal stress often arrives locally as service cuts, user fees, infrastructure delay, and property-tax pressure.
- Gate 20 hardens Gate 11 because rescue, guarantee, and fiscal-risk programs require enforcement, audits, and legal durability.
- Gate 20 hardens Gate 16 because public-cost shifts become private tollgates.
- Gate 20 hardens Gate 18 because post-shock recovery fails when public capacity is already claimed by creditors or backstopped insiders.

## Opening package

Build a public fiscal-risk register; publish contingent-liability and guarantee exposure; stress test social-insurance and public-pension claims; pre-fund insurance backstops with risk-sensitive assessments; attach warrants/equity/clawbacks to crisis rescues; score distributional incidence of interest and debt-service pressure; govern public assets through fiscal rules, independent reporting, and claimant-linked benefits; and require sunset/review of emergency facilities.[S345][S346][S350][S357][S360][S369]


## rev0319 operationalization addendum

rev0319 addendum: use `gate-20-public-balance-sheet-register-and-subgates.md` and `public-balance-sheet-seniority-waterfall.md` before any Gate 20 comfort verdict. The older scorecard remains the narrative screen; the new files are the machine-operational layer.
