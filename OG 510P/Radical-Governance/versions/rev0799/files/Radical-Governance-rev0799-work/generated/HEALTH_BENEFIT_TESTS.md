# Health-benefit and prescription-drug transition tests matrix

Generated for `rev0799` from `metadata/health_benefit_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `HB-01` Coverage, payer, and plan-state ladder | Can the packet separate eligibility, enrollment, payer, plan, product, premium, effective-date, first-use, and retroactive reinstatement states before calling coverage continuous? | `894`, `895`, `923`, `924` | Do not treat enrollment, renewal, or SEP status as continuity until payer and plan-state receipts are joined. |
| `HB-02` Treatment and medication baseline | Does the transition packet identify active medications, therapies, providers, pharmacies, equipment, care plans, and high-risk clinical clocks at the handoff date? | `894`, `897`, `923`, `924` | Add a treatment baseline before scoring a coverage transition as safe. |
| `HB-03` Marketplace SEP and effectuation receipt | Where Medicaid / CHIP coverage is lost, will be lost, or denied, can the packet prove SEP eligibility, document state, plan selection, premium payment, effective date, and first usable coverage? | `894`, `895`, `901`, `923`, `924` | Treat the Marketplace path as incomplete until the person can use coverage, not merely apply. |
| `HB-04` Formulary and utilization-management map | Can each at-risk drug be mapped across formulary status, tier, prior authorization, step therapy, quantity limit, network, specialty pharmacy, and refill rules before and after transition? | `874`, `894`, `923`, `924` | Do not rely on plan-level coverage where drug-level restrictions are unresolved. |
| `HB-05` Transition-fill and emergency bridge clock | Is a temporary, emergency, or bridge supply available, noticed as temporary, and long enough for the exception / appeal / prescriber route to complete before harm? | `894`, `897`, `923`, `924` | Do not count a transition fill as repair unless it reaches a permanent cure route or safe alternative therapy. |
| `HB-06` Exception, appeal, and prescriber evidence route | Are coverage determination, exception, expedited review, appeal, prescriber statement, representative authority, and late-filing good-cause routes usable before treatment interruption? | `404`, `425`, `905`, `923`, `924` | Add a clinically timed exception / appeal route before accepting a denial or substitution. |
| `HB-07` Affordability and cost-sharing state | Can the packet prove premium, grace-period, deductible, copay / coinsurance, out-of-pocket cap, Extra Help / LIS, dual status, payment-plan election, monthly bill, and point-of-sale cost state? | `897`, `901`, `923`, `924` | Do not treat a drug as accessible when coverage exists but cost state is unaffordable or unresolved. |
| `HB-08` Notice, language, representative, and assistance route | Does notice reach the person, representative, prescriber, pharmacy, navigator, SHIP counselor, or assister with enough time and accessible channels to complete the cure route? | `424`, `425`, `426`, `905`, `921`, `923`, `924` | Do not close or deny without treatment-aware notice and assistance evidence. |
| `HB-09` Retroactive correction, reimbursement, and claim repair | If the handoff fails, can retroactive coverage, reinstatement, reimbursement, claim reversal, cost-sharing correction, or replacement supply repair the gap? | `894`, `897`, `923`, `924` | Add a repair tail before calling the transition complete after error. |
| `HB-10` Treatment-gap and medication-access metrics | Do public or internal metrics count medication gaps, transition fills, exceptions, denials, appeal reversals, point-of-sale rejections, abandonment, treatment episodes, and high-risk subgroup variation—not just enrollment? | `419`, `894`, `917`, `923`, `924` | Do not use enrollment dashboards as treatment-continuity evidence without treatment-gap metrics. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `924` | `HB-01`, `HB-02`, `HB-03`, `HB-04`, `HB-05`, `HB-06`, `HB-07`, `HB-08`, `HB-09`, `HB-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 1 |
| `419` | 1 |
| `424` | 1 |
| `425` | 2 |
| `426` | 1 |
| `874` | 1 |
| `894` | 7 |
| `895` | 2 |
| `897` | 4 |
| `901` | 2 |
| `905` | 2 |
| `917` | 1 |
| `921` | 1 |
| `923` | 10 |
| `924` | 10 |

## Use rule

Run health-benefit tests whenever Medicaid, CHIP, Marketplace, Medicare, Part D, managed-care, pharmacy-benefit, formulary, prior-authorization, transition-fill, exception, appeal, Extra Help / LIS, payment-plan, premium, document-verification, or pharmacy point-of-sale state can interrupt treatment. Separate eligibility, enrollment, payer, plan, formulary, utilization-management, cost, notice, representative, treatment, and repair states before treating coverage or medication as continuous.
