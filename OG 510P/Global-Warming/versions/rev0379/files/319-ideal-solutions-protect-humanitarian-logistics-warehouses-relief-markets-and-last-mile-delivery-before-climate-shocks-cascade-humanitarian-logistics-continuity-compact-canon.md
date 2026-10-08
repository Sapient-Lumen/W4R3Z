---
id: '319'
revision_added: rev0271
status: canon
object_type: service_continuity
domain_tags:
- humanitarian_logistics
- relief_supply
- warehousing
- last_mile
- procurement
- cash_and_vouchers
- local_markets
service_floor:
- humanitarian_logistics_continuity
- relief_supply_continuity
- last_mile_delivery
- relief_market_function
hazard_tags:
- flood
- storm
- heat
- drought
- conflict
- displacement
- port_disruption
- road_closure
- fuel_shock
- funding_shortfall
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- humanitarian_agency
- local_government
- logistics_cluster
- supplier
- transporter
- warehouse_operator
- community_organization
- donor
instrument_tags:
- preposition
- procure
- route
- convoy
- cash
- voucher
- warehouse
- coordinate
- localize
routes_to:
- '13'
- '252'
- '253'
- '275'
- '276'
- '295'
- '296'
- '299'
- '300'
- '316'
- '318'
- '320'
source_ids:
- S571
- S572
- S573
upstream_dependencies:
- transport
- ports
- warehouses
- fuel_or_charging
- telecoms
- payments
- customs
- security
- local_partners
- market_function
downstream_consequences:
- hunger
- untreated_illness
- shelter_failure
- disease_outbreak
- price_spike
- displacement_prolongation
- social_tension
- recovery_delay
equity_lenses:
- remote_communities
- informal_settlements
- displaced_people
- children
- older_adults
- disabled_people
- women_headed_households
- undocumented_people
degraded_modes:
- local_procurement
- cash_or_voucher_switch
- mobile_distribution
- community_pickup
- air_or_boat_delivery
- mutual_aid_warehouse
- paper_registration
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- port_access
- road_access
- fuel
- customs
- warehouse_space
- funding_gap
- insecurity
- last_mile_partner_capacity
- cold_chain
failure_modes:
- aid_waits_at_port
- warehouse_without_last_mile
- cash_without_markets
- duplicated_distribution
- inaccessible_queue
- local_capacity_bypass
- relief_crowds_out_recovery
proof_ledgers:
- stock_pipeline_log
- warehouse_inventory
- route_access_map
- distribution_reach_log
- market_price_log
- partner_payment_log
- cold_chain_log
restoration_conflicts:
- throughput_vs_equity
- international_speed_vs_local_capacity
- cash_vs_in_kind
- security_restriction_vs_access
- procurement_speed_vs_anti_capture
assurance_tests:
- prepositioning_drill
- last_mile_access_test
- relief_market_stress_test
- cold_chain_delivery_drill
- customs_clearance_rehearsal
---

# 319 — Ideal Solutions: Protect humanitarian logistics, warehouses, relief markets, and last-mile delivery before climate shocks cascade

## Claim

The archive treats food, water, health, transport, waste, payments, and public safety as service floors.
This file adds the emergency supply rail that often connects them: **humanitarian logistics, warehousing, procurement, transport, last-mile distribution, cash/voucher markets, local partners, and relief information are climate-critical services, not charity afterthoughts.**

Relief can fail even when supplies exist.
Goods can sit at a port, warehouse, airport, border, or depot while roads are cut, fuel is scarce, customs rules are unclear, local partners are unpaid, markets are distorted, lists are wrong, or the last mile is unsafe.
Cash can fail if markets are empty.
In-kind aid can fail if it arrives late, duplicates what people can buy, or bypasses local capacity.

WFP describes a humanitarian supply chain spanning planning, procurement, transport, storage, last-mile delivery, cash transfers, UNHAS, UNHRD, and Logistics Cluster coordination [S571].
OCHA's 2026 humanitarian overview frames humanitarian action under simultaneous pressures from wars, climate disasters, epidemics, crop failures, funding scarcity, and the need for focused, evidence-based response [S573].
The archive should therefore treat relief logistics as a service-continuity system.

## Fast rule

**Any climate packet that assumes emergency food, water, shelter, medicine, cash, debris support, school supplies, cooling supplies, cleaner-air equipment, or recovery materials must prove procurement, storage, access routes, last-mile delivery, market function, and local-partner capacity before the shock.**

## Minimum service floor

The floor includes:

1. pre-positioned and rotating essential stocks;
2. mapped warehouses, depots, cold-chain points, and staging areas;
3. route, port, bridge, airstrip, rail, river, and last-mile access information;
4. procurement rules that can move fast without becoming capture;
5. local suppliers and local partners paid on time;
6. cash / voucher switch rules when markets work;
7. in-kind switch rules when markets fail;
8. customs, border, and mutual-aid arrangements;
9. accessible distribution that does not exclude disabled people, older adults, undocumented people, no-car households, caregivers, or people in custody;
10. feedback and correction channels.

House rule: **stock in a warehouse is not assistance until it crosses the last mile.**

## Market rule

Relief markets are part of service continuity.
A serious packet asks:

- are essential goods available locally;
- are prices moving beyond reach;
- are vendors able to restock;
- are payment systems working;
- would cash support local recovery or fuel price spikes;
- would in-kind distribution undermine local markets or fill a real gap;
- which groups cannot safely use markets even if markets function.

House rule: **cash and in-kind aid are not ideologies; they are degraded-mode choices.**

## Local-capacity rule

Local organizations are not just outreach contractors.
They often know who is missing, which route is passable, which queue is unsafe, which language matters, and which households are invisible.
But they can also be overloaded, underpaid, excluded from information, or made responsible for risks they cannot finance.

The packet should therefore track local partner capacity, payments, safety, governance, and feedback.

House rule: **localization without money, authority, and protection is burden shifting.**

## Minimum proof ledger

| Question | Evidence required |
|---|---|
| What supplies were available? | stock, pipeline, expiry, and rotation logs |
| Could supplies move? | route status, fuel / charging, customs, convoy, and access logs |
| Did the last mile work? | distribution reach, missed household, queue, and complaint records |
| Did markets work? | price, stock, vendor, payment, and cash-spendability records |
| Were local partners protected? | partner contract, payment, security, and feedback logs |
| What was duplicated or missed? | interagency coordination and gap map |
| What changed after failure? | warehouse, procurement, route, partner, cash, or access correction |

## What this routes to

- use `319` when a prompt asks about humanitarian logistics, supply chains, emergency food, relief warehouses, last-mile distribution, cash/voucher response, local markets, ports, roads, or aid-delivery failure;
- pair with `275` and `276` for food and nutrition;
- pair with `295` and `296` for transport and logistics;
- pair with `316` for medical products;
- pair with `318` for payment and cash rails;
- pair with `320` for displacement and receiving-community capacity.

## Compression rule

**Relief is a climate service only when stocks, routes, markets, payments, local partners, last-mile access, and correction ledgers work before the crisis becomes a queue.**

## Preparedness cluster rule

Humanitarian logistics continuity should be prepared with national, regional, and local actors before the event: mapped routes, warehousing, customs procedures, market-switch rules, fuel or charging plans, cold-chain capacity, and last-mile partner rosters. Logistics preparedness that begins after the shock is already late. [S572]

---
Citations point to `sources/register.md`.
