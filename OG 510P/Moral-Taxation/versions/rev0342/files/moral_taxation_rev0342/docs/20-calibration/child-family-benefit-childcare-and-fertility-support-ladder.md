# Child, family-benefit, childcare, and fertility-support ladder

## Question in one sentence

How should this instrument family be calibrated so public protection, access, and floor repair do not become private gatekeeping rent or hidden burden?[S277][S625][S626][S627]

## Companion routes

Use this memo with:

- [`../10-framework/child-family-benefit-childcare-and-fertility-support-routing.md`](../10-framework/child-family-benefit-childcare-and-fertility-support-routing.md)
- [`../10-framework/incidence-and-protected-burden-routing.md`](../10-framework/incidence-and-protected-burden-routing.md)
- [`../10-framework/proceeds-routing-and-fiscal-reciprocity.md`](../10-framework/proceeds-routing-and-fiscal-reciprocity.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — nonrefundable tax credit | reduce liability only. | Weak for lowest-income families unless refundable or paired with cash support. |
| B — refundable child benefit | direct support independent of filing sophistication. | Strong for child floor and poverty reduction. |
| C — childcare subsidy / voucher | support work-related care costs. | Strong if co-pays, providers, and access are monitored. |
| D — provider-side capacity grant | build supply, quality, and wages. | Use where shortages, infant care, disability access, or rural access dominate. |
| E — pronatalist tax bonus | reward births or marriage. | Suspect unless child welfare, caregiver equality, and autonomy are protected. |

## Ten-gate ladder

1. **child-floor gate** — test the live facts before choosing the instrument.
2. **refundability gate** — test the live facts before choosing the instrument.
3. **filing-access gate** — test the live facts before choosing the instrument.
4. **work-care gate** — test the live facts before choosing the instrument.
5. **co-payment gate** — test the live facts before choosing the instrument.
6. **provider-capacity gate** — test the live facts before choosing the instrument.
7. **quality / workforce gate** — test the live facts before choosing the instrument.
8. **autonomy gate** — test the live facts before choosing the instrument.
9. **cliff gate** — test the live facts before choosing the instrument.
10. **review gate** — test the live facts before choosing the instrument.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| child poverty/floor risk | refundable or automatic child benefit | minimize filing and SSN traps. |
| work-related childcare barrier | childcare subsidy plus provider capacity | control co-pays and waitlists. |
| fertility/demography claim | child-welfare and autonomy screen | do not commodify birth or punish childlessness. |

## Failure-mode capsule

Axes: `claim_friction_child_policy`, `access_exclusion`, `trapdoor_or_cliff`. Block child-floor support captured by provider scarcity, waitlists, cliffs, or refund delay.

## Recalibration trigger capsule

Triggers: `access_or_fallback_failure`, `proceeds_or_surplus_trace_failure`, `protected_floor_or_incidence_shift`, `waitlist_growth`. Reopen on waitlist growth, copay/taper pressure, provider capture, or fallback failure.

## Accountability capsule

Authoritative assignment: route `child_family_benefit_childcare_fertility_support` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `child_benefit_childcare_subsidy_or_provider_capacity_administrator`.
- Rent/benefit trace: `childcare_provider_or_intermediary_capturing_subsidy_without_capacity_quality_or_affordability_and_employer_receiving_care_enabled_labor_supply`.
- Bottleneck/evidence: `eligibility_and_refund_delivery_portal; childcare_subsidy_waitlist_and_provider_capacity_gate +1 more`; evidence starts with `child_eligibility_income_and_dependency_records; childcare_cost_copayment_and_provider_price_records +3 more`.
- Fallback duty: `fallback_public_body_must_preserve_child_floor_auto_claim_offline_and_language_access_no_forfeiture_for_provider_waitlist_or_refund_delay`.


## Source IDs only

[S277][S625][S626][S627]

[S277]: ../../SOURCES.md#S277
[S625]: ../../SOURCES.md#S625
[S626]: ../../SOURCES.md#S626
[S627]: ../../SOURCES.md#S627
