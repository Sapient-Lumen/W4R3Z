# User-fee, service-charge, affordability, and essential-access ladder

## Question in one sentence

How should the archive distinguish legitimate cost recovery from hidden taxation, regressive access tolls, and essential-service ransom?[S573][S574][S575]

## Companion routes

Use this memo with:

- [`../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md`](../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md)
- [`../10-framework/decision-procedure.md`](../10-framework/decision-procedure.md)
- [`../10-framework/proposal-scorecard.md`](../10-framework/proposal-scorecard.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — cost-causer fee | avoidable special cost. | Usually allowed with review. |
| B — special-benefit fee | discrete optional public service. | Allowed if proportional. |
| C — public-capacity charge | broad public cost. | Treat as tax-like. |
| D — required-access fee | compliance, appeal, status, utilities, basic transit. | Waive or rebate at floor risk. |
| E — essential-service shutoff | nonpayment cuts off health/safety service. | Restrict heavily and require assistance. |

## Ten-gate ladder

1. **benefit gate** — identify the special benefit or cost-causing conduct.
2. **authorization gate** — if the fee funds general public goods, route it like a tax.
3. **cost gate** — show cost basis, update cadence, and independent review.
4. **equity gate** — test low-income, disability, age, rural, and household-size effects.
5. **essential-service gate** — flag water, electricity, heat, basic transit, filing, appeal, status, or safety access.
6. **affordability gate** — cap burden, offer discounts, arrears plans, and assistance.
7. **disconnection gate** — require notice, cure, health/seasonal protections, and no-rent reconnection.
8. **self-funding gate** — test whether the collecting entity has a revenue conflict.
9. **industrial-cost gate** — assign large-user infrastructure costs to the user before residential pass-through.
10. **sunset gate** — review fee level, proceeds use, and access outcomes.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| optional premium service | special-benefit fee | cost proportionality. |
| required public form or appeal | waiver/rebate | no access toll. |
| water or power arrears | affordability plan | no shutoff without cure and safeguards. |
| industrial load upgrade | cost-causation charge | no household cross-subsidy. |
| agency self-funding | independent review | cap and audit. |

## Accountability capsule

Authoritative assignment: route `user_fee_service_charge_utility_public_access_toll` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `utility_or_public_service_charge_authority_with_cost_affordability_disconnection_and_reconnection_control`.
- Rent/benefit trace: `utility_public_agency_vendor_or_general_fund_capturing_essential_service_fee_revenue_excess_cost_recovery_or_reconnection_rent`.
- Bottleneck/evidence: `tariff_and_cost_of_service_record; bill_line_item_and_collection_channel +3 more`; evidence starts with `fee_schedule_tariff_cost_of_service_and_special_benefit_record; household_income_affordability_arrearage_deposit_and_shutoff_file +3 more`.
- Fallback duty: `public_body_and_utility_regulator_must_preserve_fallback_lifeline_service_offline_access_disconnection_moratorium_reconnection_cure_and_nonforfeiture_for_essential_services`.


## Source IDs only

[S573][S574][S575]

[S573]: ../../SOURCES.md#S573
[S574]: ../../SOURCES.md#S574
[S575]: ../../SOURCES.md#S575
