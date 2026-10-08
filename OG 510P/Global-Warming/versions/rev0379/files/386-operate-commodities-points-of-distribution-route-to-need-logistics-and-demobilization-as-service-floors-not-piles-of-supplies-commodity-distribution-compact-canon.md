---
id: '386'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- commodity_distribution
- points_of_distribution
- logistics
- supply_chain
- mass_care
- food_water_shelter
- last_mile
service_floor:
- life_sustaining_commodity_access
- POD_or_delivery_route
- inventory_to_need_visibility
hazard_tags:
- flood
- storm
- wildfire
- heat
- smoke
- outage
- earthquake
- displacement
- supply_chain_disruption
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- logistics_section
- emergency_manager
- mass_care_operator
- transport_agency
- warehouse_operator
- voluntary_organization
- community_liaison
instrument_tags:
- stage
- distribute
- deliver
- inventory
- prioritize
- demobilize
- monitor
routes_to:
- '275'
- '276'
- '295'
- '319'
- '323'
- '328'
- '339'
- '361'
- '379'
- '381'
- '383'
- '387'
source_ids:
- S691
upstream_dependencies:
- warehouses
- transport
- fuel
- route_status
- staff
- security
- public_information
- volunteers
- cooling_and_shade
downstream_consequences:
- dehydration
- food_insecurity
- shelter_overload
- medical_nonadherence
- public_disorder
- donation_waste
equity_lenses:
- no_car_households
- disabled_people
- older_adults
- remote_communities
- informal_settlements
- language_access
- families_with_infants
degraded_modes:
- walk_up_POD
- mobile_delivery
- door_to_door_delivery
- community_pickup_point
- voucher_substitution
- paper_inventory
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- wrong_commodity
- POD_site_inaccessible
- transport_gap
- inventory_not_visible
- security_overcorrection
- demobilization_too_early
- unsolicited_goods_clog_logistics
failure_modes:
- supplies_exist_but_not_at_point_of_need
- POD_requires_car
- queue_heat_exposure
- disabled_users_cannot_carry_supplies
- inventory_expires_or_disappears
- public_message_wrong_location
proof_ledgers:
- commodity_inventory_log
- POD_status_board
- route_to_need_map
- delivery_exception_log
- queue_safety_log
- demobilization_log
commodity_distribution_state: inventory, route, POD, accessible delivery, queue safety, exception, and demobilization
  posture
---

# 386 — Ideal Solutions: Operate commodities, points of distribution, route-to-need logistics, and demobilization as service floors, not piles of supplies

## Core claim

Supplies are not a service floor until they are visible, staged, routed, accessible, distributed, monitored, and demobilized. A warehouse full of water, meals, tarps, filters, diapers, medications, masks, or generators can still fail the public if the point of distribution is unreachable, car-dependent, overheated, unsafe, unstaffed, wrongly advertised, or not linked to households that cannot queue.

FEMA's distribution-management guidance explicitly covers movement from resources to points of need, commodity PODs, inventory management, sourcing, and demobilization [S691]. The climate cube converts those logistics functions into readiness fields.

## Commodity service floor

The minimum floor should answer:

- what life-sustaining commodities are required;
- who owns sourcing and inventory;
- where commodities are staged;
- what route and vehicle move them;
- which POD or delivery model serves whom;
- how no-car, disabled, medically dependent, rural, isolated, and heat-exposed users are served;
- how public information stays synchronized with site status;
- when distribution demobilizes and what replaces it.

## PODs are user interfaces

A POD is not only a logistics site. It is a public interface under stress. It needs shade, water, toilets, queue control, language access, accessibility, traffic management, security that does not deter vulnerable users, worker protection, and a way to record unmet demand. A drive-through POD alone is not an adequate floor where many households lack cars or fuel.

## Anti-pile rule

Unsolicited goods, politically staged donations, excess bottled water, or mismatched supplies can clog warehouses and routes. Commodity readiness should privilege requested, typed, tracked, needed, and time-sensitive goods over symbolic abundance.

## Cube rule

Any mass-care, shelter, water, food, health, smoke, heat, or recovery packet that depends on supplies should expose `commodity_distribution_state`. Blank means the archive should treat the commodity promise as an input assumption, not a service floor.

---
Citations point to `sources/register.md`.
