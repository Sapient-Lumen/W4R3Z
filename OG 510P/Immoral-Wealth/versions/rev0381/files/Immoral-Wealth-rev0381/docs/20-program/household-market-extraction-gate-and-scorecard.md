---
status: active_program
claim_kind: certification_gate
route_role: household_market_extraction_core
canonical_anchor: true
route_refs:
- household_market_extraction_core
- certification_core
supersedes: null
depends_on:
- ../10-framework/household-market-extraction-and-cost-of-life-tollgates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0314_household_market_extraction
---

# Household-market-extraction gate and scorecard

Gate 16 asks whether lower-half and middle households can convert income, benefits, and modest assets into durable net wealth after ordinary private-market tollgates are paid. The gate blocks comfort certification when everyday markets repeatedly drain liquidity, hide total cost, interrupt care/work, or turn small shortfalls into escalating fees and losses.[S260][S262][S263][S269]

## Gate 16 question

Can an ordinary household meet recurring cost-of-life obligations without losing the first buffer to high-cost credit, opaque fees, auto-finance traps, fragmented app/payroll credit, child/elder-care costs, or cancellation/remedy friction?

## Scorecard fields

| Field | Pass | Warning | Fail / veto pressure |
|---|---|---|---|
| `household_market_extraction_gate` | low tolls, strong remedies | sectoral warnings | routine private tolls absorb buffer |
| `consumer_credit_fee_drag` | fees low and avoidable | elevated by subgroup | recurring fees function as volatility tax |
| `overdraft_nsf_fee_drag` | low revenue and safe alternatives | residual bank-fee exposure | repeated fees hit liquidity-stressed households |
| `credit_card_late_fee_exposure` | low/reasonable cost and hardship rails | repeat late fees concentrated | late fees are profit center for vulnerable users |
| `high_cost_small_dollar_credit` | capped, affordable, low repeat use | state-by-state weakness | payday/title/pawn/installment traps fund necessities |
| `unbanked_underbanked_cost_burden` | low-cost account rails universal | subgroup gaps | nonbank products replace safe account access |
| `auto_finance_negative_equity` | low LTV, clean title path | rollover watch | vehicle is underwater and necessary for work |
| `auto_repossession_mobility_loss` | rare and remedy-protected | subgroup concentration | repossession causes work/care/credit cascade |
| `bnpl_fragmented_credit_visibility` | total obligations visible | partial data | product stacking hides overcommitment |
| `earned_wage_access_fee_visibility` | clear, no pressure, no recourse | fee/tip watch | wage timing becomes high-cost liquidity market |
| `junk_fee_or_drip_pricing` | all-in price upfront | sectoral rules | total price hidden until lock-in |
| `negative_option_subscription_trap` | cancellation as easy as sign-up | rule uncertainty | recurring charges continue through friction |
| `childcare_cost_time_wealth_drag` | affordable, available, hours-fit | cost/availability stress | care costs or gaps block work/saving |
| `childcare_labor_force_interruption` | minimal forced exit | subgroup warning | parents reduce work/training involuntarily |
| `long_term_care_asset_spenddown` | support before poverty | asset-test warning | care need exhausts assets before public support |
| `household_market_remedy_access` | easy complaint, refund, correction | weak enforcement | remedy arrives after irreversible loss |

## Verdict effects

- **Pass** strengthens the lower-half floor and earnings-led wealth-formation claims.
- **Warning** blocks `near_ideal` unless the case shows low incidence, subgroup checks, and strong remedies.
- **Fail** usually routes to `correction_required`; it can route to `emergency_repair` when tollgates interrupt work, care, utilities, food, medicine, transport, or housing.
- **Veto pressure** applies when tollgates are concentrated by race, caste, gender, disability, immigration status, age, military status, geography, or family structure.[S263][S268][S274][S277]

## Evidence pack

Use household debt/delinquency, fee revenue, product-level market monitoring, account-access data, complaint records, contract terms, auto repossession/negative-equity data, childcare prices and availability, labor-force interruption evidence, long-term-care out-of-pocket cost and eligibility data, subgroup incidence, and legal/enforcement status.
