# Transport congestion, road pricing, mobility, and transit-repair ladder

## Question in one sentence

How should congestion charges, tolls, fuel taxes, and mobility fees be set so users face real scarcity and harm while protected travelers keep access?[S586][S587]

## Companion routes

Use this memo with:

- [`../10-framework/transport-congestion-road-pricing-and-mobility-access-routing.md`](../10-framework/transport-congestion-road-pricing-and-mobility-access-routing.md)
- [`../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md`](../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md)
- [`../10-framework/proceeds-routing-and-fiscal-reciprocity.md`](../10-framework/proceeds-routing-and-fiscal-reciprocity.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — fuel tax | broad road/emissions proxy. | Simple; weak for congestion and EV transition. |
| B — cordon/congestion charge | zone/time toll. | Strong if alternatives and exemptions are real. |
| C — vehicle-miles fee | distance-based road charge. | Use with privacy and rural safeguards. |
| D — curb/freight charge | scarce curb, delivery, or heavy-use fee. | Good when targeted to scarce public space. |
| E — mobility credit | rebate, discount, or transit credit. | Needed where protected access is at risk. |

## Ten-gate ladder

1. **purpose gate** — identify congestion, emissions, pavement wear, curb scarcity, safety, or transit repair.
2. **baseline gate** — publish traffic, speed, emissions, transit, and equity baseline.
3. **alternative gate** — verify usable transit, paratransit, carpool, freight, or time-shift alternatives.
4. **exemption gate** — design disability, emergency, low-income, medical, and shift-work relief by need, not formal title.
5. **proceeds gate** — require maintenance-of-effort and visible mobility repair.
6. **privacy gate** — minimize plate, trip, and account data; preserve correction.
7. **rate gate** — set price by time, place, vehicle class, and avoidable burden.
8. **collection gate** — cap fines, late fees, holds, and registration sanctions.
9. **evaluation gate** — compare actual congestion, emissions, transit reliability, and burden.
10. **review gate** — trigger changes when alternatives fail or burdens concentrate.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| dense congestion | cordon/time charge | transit repair and exemptions. |
| road wear | weight/distance fee | privacy and rural safeguards. |
| emissions | fuel/carbon rate | floor repair for necessary travel. |
| curb scarcity | curb/freight charge | small-business and disability loading zones. |

## Failure-mode capsule

Axes: `mobility_ransom`, `exemption_formalism`, `public_loss_private_upside`, `data_or_confidentiality_overreach`. Mobility ransom: tolls, fines, account locks, or trip data burden necessary travel before transit/privacy/offline safeguards work.


## Recalibration trigger capsule

Triggers: `congestion_target_miss`, `protected_floor_or_incidence_shift`, `transit_repair_failure`. Reopen on target miss, transit-repair failure, sanction cascade, data expansion, or protected-traveler access loss.


## Accountability capsule

Authoritative assignment: route `transport_congestion_road_pricing_mobility_access` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `road_operator_transport_authority_or_toll_platform_with_pricing_exemption_location_data_and_transit_repair_control`.
- Rent/benefit trace: `unpriced_peak_road_user_developer_freight_operator_or_toll_vendor_capturing_congestion_space_fee_markup_or_location_data_value`.
- Bottleneck/evidence: `tolling_platform; exemption_registry +3 more`; evidence starts with `speed_delay_emissions_zone_and_road_use_record; toll_rate_exemption_income_rebate_and_disability_access_file +3 more`.
- Fallback duty: `transport_authority_must_preserve_fallback_mobility_access_offline_or_assisted_exemption_and_transit_repair_when_toll_platforms_or_private_mobility_channels_fail`.


## Source IDs only

[S586][S587]

[S586]: ../../SOURCES.md#S586
[S587]: ../../SOURCES.md#S587
