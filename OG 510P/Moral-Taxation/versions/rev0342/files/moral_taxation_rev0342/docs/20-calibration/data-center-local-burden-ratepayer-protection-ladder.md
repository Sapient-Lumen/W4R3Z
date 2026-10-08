# Data-center local-burden and ratepayer-protection ladder

## Question in one sentence

What is the smallest workable ladder for deciding when a data center, cloud facility, or AI compute cluster should pay local-burden charges, ratepayer credits, water charges, bonding, abatement clawbacks, or proceeds-repair shares?[S15][S445][S10]

## Companion routes

Use this memo with:

- [`../10-framework/data-center-grid-water-and-ratepayer-burden-routing.md`](../10-framework/data-center-grid-water-and-ratepayer-burden-routing.md)
- [`../10-framework/net-fiscal-stack-and-hidden-negative-tax-routing.md`](../10-framework/net-fiscal-stack-and-hidden-negative-tax-routing.md)
- [`../10-framework/jurisdiction-and-scale-routing.md`](../10-framework/jurisdiction-and-scale-routing.md)
- [`../10-framework/ai-exceptional-levy-trigger-routing.md`](../10-framework/ai-exceptional-levy-trigger-routing.md)
- [`beneficiary-home-market-and-local-burden-claim-split-ladder.md`](beneficiary-home-market-and-local-burden-claim-split-ladder.md)
- [`proceeds-visibility-local-share-and-earmarking-ladder.md`](proceeds-visibility-local-share-and-earmarking-ladder.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — no special local rule | treat the facility like any large customer. | Correct only when full marginal local burden is already priced. |
| B — generic AI compute tax | tax tokens, models, or server count. | Reject: rough theater unless it tracks a real burden, rent, or bottleneck. |
| C — local-burden ledger plus repair | charge shifted grid, water, land, and infrastructure burdens; route proceeds visibly. | Adopt. |
| D — abatement-first growth strategy | subsidize facility siting and hope indirect gains offset costs. | Reject unless net-of-stack proof and clawback are explicit. |

## Ten-gate ladder

1. **facility-definition gate** — identify facility, operator, cloud tenant, model lab, power purchaser, landlord, utility, and local government.
2. **load gate** — measure contracted load, peak load, ramp speed, dispatchability, curtailment rights, and reliability implications.[S445]
3. **cost-causation gate** — assign generation, transmission, distribution, substation, interconnection, queue, reliability, and study costs to the causative beneficiary where possible.
4. **ratepayer-incidence gate** — identify whether ordinary residential, small-business, municipal, or industrial customers absorb costs through ratebase, riders, tariff design, or public debt.
5. **water-and-local-harm gate** — price or restrict water withdrawal, consumption, discharge, cooling burden, local emissions, noise, and land-use harms.
6. **net-fiscal-stack gate** — offset taxes paid against abatements, grants, cheap land, public infrastructure, special tariffs, accelerated depreciation, and guarantees.
7. **bottleneck-rent gate** — test whether scarcity in AI infrastructure, power, chips, cloud access, or land produces rents beyond ordinary cost recovery.[S10]
8. **local-benefit gate** — verify jobs, wages, tax base, supplier commitments, grid upgrades usable by others, and community benefits; discount claims that are not enforceable.
9. **instrument-selection gate** — choose interconnection charge, demand charge, water charge, local-burden fee, property-tax clawback, bond, reserve, ratepayer credit, or ordinary tax.
10. **proceeds-and-review gate** — route proceeds first to ratepayer credits, grid/water repair, local public capacity, or burdened locality before general revenue; schedule review when load, tariff, water, or subsidy facts change.

## Default settings

| Burden posture | Instrument | Proceeds rule |
|---|---|---|
| full marginal grid cost already paid | ordinary tax stack | no special local burden charge. |
| upgrade costs socialized | facility-side charge or ratepayer credit | credit burdened rate classes first. |
| water scarcity live | volumetric/scarcity charge, cap, recycling duty, or denial | watershed repair and drought resilience first. |
| tax abatement plus rate impact | abatement clawback or local-burden offset | no subsidy unless net public benefit remains. |
| bottleneck rent without local burden | rent or excess-return route | national/club/public-capacity route may dominate. |
| local burden plus global beneficiary | split claim | local repair first, then broader coordination. |

## Failure-mode capsule

Axes: `abatement_without_netting`, `ratepayer_cross_subsidy`, `opacity_or_erasure`. Local-load laundering: facility capacity, abatement, water, or interconnection records shift costs to ratepayers/local hosts.


## Recalibration trigger capsule

Triggers: `capacity_or_control_shift`, `protected_floor_or_incidence_shift`. Reopen on load, water, rate-case, interconnection, or abatement net-benefit drift.


## Accountability capsule

Authoritative assignment: route `data_center_local_burden` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `data_center_operator_cloud_controller_or_utility_with_load_water_and_incentive_control`.
- Rent/benefit trace: `data_center_operator_cloud_customer_landlord_or_local_developer_receiving_below_cost_grid_water_land_or_tax_abatement_value`.
- Bottleneck/evidence: `interconnection_queue_operator; utility_rate_case_record_holder +3 more`; evidence starts with `contracted_peak_load_interconnection_and_curtailment_record; marginal_grid_upgrade_cost_rate_case_and_ratepayer_incidence_file +4 more`.
- Fallback duty: `public_utility_and_local_government_must_preserve_fallback_essential_service_affordability_reliability_and_local_repair_when_private_compute_load_uses_mandatory_public_infrastructure`.


## Source IDs only

[S10][S15][S445]

[S10]: ../../SOURCES.md#S10
[S15]: ../../SOURCES.md#S15
[S445]: ../../SOURCES.md#S445

