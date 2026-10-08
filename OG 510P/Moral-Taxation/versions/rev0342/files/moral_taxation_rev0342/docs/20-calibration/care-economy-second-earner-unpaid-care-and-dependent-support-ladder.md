# Care economy, second-earner, unpaid-care, and dependent-support ladder

## Question in one sentence

What ladder should decide whether a tax or benefit rule recognizes care and dependents fairly, or instead hides unpaid care, penalizes marriage, and traps second earners?[S500][S501][S502]

## Companion routes

Use this memo with:

- [`../10-framework/care-economy-second-earner-and-household-floor-routing.md`](../10-framework/care-economy-second-earner-and-household-floor-routing.md)
- [`../10-framework/assessment-units-care-and-dependency-routing.md`](../10-framework/assessment-units-care-and-dependency-routing.md)
- [`../10-framework/labor-tax-wedge-platform-work-and-social-insurance-routing.md`](../10-framework/labor-tax-wedge-platform-work-and-social-insurance-routing.md)
- [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — individual filing | each person taxed separately. | Default for personhood and second-earner protection. |
| B — household means test | use household resources for benefit targeting. | Accept only with cliff smoothing and caregiver review. |
| C — caregiver credit/allowance | pay or credit unpaid care. | Strong where care substitutes for paid work. |
| D — childcare/eldercare subsidy | reduce care cost to enable work and quality care. | Default for second-earner and dependent-access cases. |
| E — social-insurance care credit | protect pension/benefit records. | Required where care interrupts earnings. |

## Ten-gate ladder

1. **personhood gate** — start with each adult as a separate person for liability, standing, notice, and benefit access.
2. **dependency gate** — identify children, elders, disabled persons, illness, disaster care, and temporary or long-term care needs.
3. **participation gate** — calculate effective marginal rates for second earners after tax, benefit withdrawal, childcare, commuting, and care costs.[S500]
4. **unpaid-care gate** — estimate hours, opportunity cost, pension loss, career interruption, respite need, and social value.
5. **paid-care gate** — test wages, benefits, training, quality, migration status, public financing, and care-worker voice.[S501]
6. **support gate** — choose care credit, allowance, refundable dependent credit, childcare subsidy, eldercare support, disability support, or public provision.
7. **record gate** — protect social-insurance credits, wage records, caregiver identities, and dependent eligibility without invasive surveillance.
8. **automation gate** — prefill recurring facts and reduce renewal burdens where the state already knows dependency or disability facts.
9. **cliff gate** — smooth marriage, cohabitation, household-income, childcare, and benefit cliffs.
10. **review gate** — revisit when second-earner participation falls, care gaps rise, unpaid-care hours increase, or claim take-up is low.[S502]

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| unpaid family care | caregiver credit/allowance | recognize time and pension loss. |
| second-earner barrier | childcare/care subsidy | smooth effective marginal rate. |
| care-worker low wages | public funding/wage floor | decent work and quality. |
| household means test | taper and individual access | no marriage penalty by default. |
| recurring dependency | automatic renewal | low-friction verification. |

## Failure-mode capsule

Axes: `care_gap_denial`, `marriage_penalty`, `trapdoor_or_cliff`. Block household rules that hide unpaid care or make the second earner absorb the fiscal shock.

## Recalibration trigger capsule

Triggers: `protected_floor_or_incidence_shift`, `second_earner_effective_rate_spike`, `record_or_measurement_staleness`. Reopen on rate spikes, better care records, or shared-resource tests excluding unsafe households.

## Accountability capsule

Authoritative assignment: route `care_economy_second_earner_household_floor` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `tax_benefit_and_care_support_rule_designer`.
- Rent/benefit trace: `employer_or_public_budget_receiving_unpriced_care_subsidy_and_household_unit_beneficiary_of_second_earner_penalty`.
- Bottleneck/evidence: `filing_status_and_household_means_test_gate; childcare_or_care_subsidy_enrollment_channel +1 more`; evidence starts with `effective_marginal_rate_and_second_earner_cost_stack; care_hours_dependency_and_respite_need_records +3 more`.
- Fallback duty: `fallback_public_body_must_preserve_individual_notice_direct_care_side_support_low_friction_renewal_and_no_captive_household_forfeiture`.


## Source IDs only

[S500][S501][S502]

[S500]: ../../SOURCES.md#S500
[S501]: ../../SOURCES.md#S501
[S502]: ../../SOURCES.md#S502
