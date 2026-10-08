---
id: '333'
revision_added: rev0273
status: canon
object_type: service_continuity
domain_tags:
- critical_spares
- inventory
- stockpiles
- supply_chain
- transformers
- water_chemicals
- medical_supplies
- repair_materials
service_floor:
- critical_spares_availability
- stockpile_continuity
- substitution_standard
hazard_tags:
- supply_chain
- outage
- flood
- wildfire
- heat
- cyber
- pandemic
- geopolitical_shock
- compound_shock
clock_tags:
- stock_turnover_clock
- emergency_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- utility
- procurement_office
- warehouse_operator
- regulator
- manufacturer
- emergency_manager
- hospital
- water_utility
- grid_operator
instrument_tags:
- stockpile
- standardize
- inventory
- substitute
- prebuy
- share
- rotate
- audit
- procure
routes_to:
- '15'
- '39'
- '47'
- '48'
- '50'
- '241'
- '245'
- '265'
- '267'
- '268'
- '297'
- '316'
- '323'
- '324'
- '330'
source_ids:
- S577
- S592
- S593
upstream_dependencies:
- procurement
- warehouses
- transport
- manufacturers
- standards
- inventory_data
- maintenance_records
- mutual_aid_agreements
- insurance
downstream_consequences:
- long_outage
- unsafe_water
- repair_delay
- medical_supply_failure
- inflated_recovery_cost
- dependency_on_emergency_imports
- rationing_conflict
equity_lenses:
- small_utilities
- rural_communities
- remote_islands
- low_income_service_areas
- public_hospitals
- tribal_governments
degraded_modes:
- standard_substitute
- shared_spare_pool
- regional_stockpile
- manual_inventory
- priority_release_rule
- repairable_used_part_with_safety_certificate
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- long_lead_time
- custom_specification
- obsolete_part
- warehouse_flood_risk
- single_supplier
- expired_stock
- no_transport_for_oversize_equipment
- procurement_rule_delay
failure_modes:
- asset_restored_except_one_part
- stockpile_expired
- spares_exist_but_do_not_fit
- inventory_hidden_in_vendor_system
- warehouse_in_hazard_zone
- critical_spares_diverted_to_political_priority
- hoarding_without_sharing
proof_ledgers:
- critical_spares_inventory
- lead_time_register
- substitution_standard_catalog
- warehouse_risk_map
- stock_rotation_log
- spare_sharing_agreement
- oversize_transport_plan
- post_event_consumption_log
restoration_conflicts:
- standardization_vs_local_optimization
- stockpile_cost_vs_service_risk
- local_holdback_vs_mutual_aid
- security_confidentiality_vs_public_readiness
- scarce_spare_allocation
assurance_tests:
- inventory_spot_check
- substitute_fit_test
- warehouse_outage_drill
- oversize_transport_tabletop
- lead_time_stress_test
- mutual_spare_request_drill
inventory_posture: critical_spares_named_with_lead_time_substitute_and_release_rule
---

# 333 — Ideal Solutions: Protect critical spares, stockpiles, substitution standards, and inventory ledgers as climate-critical restoration rails

## Claim

Recovery often fails because of one missing part. **Critical spares are climate infrastructure.** Transformers, pumps, valves, relays, treatment chemicals, sensors, filters, medical gases, pharmacy stock, generator parts, culverts, radios, bridge components, meters, batteries, and lab reagents decide whether a service floor can be restored in days, months, or years.

The archive already treats supply chains, repair markets, and proof rails as important. rev0273 adds the inventory rule: if a service depends on parts, chemicals, consumables, or specialized equipment with long lead times, then the continuity packet must name the part, its lead time, its substitute, its storage risk, and its release rule.

DOE's transformer-resilience work is the canonical grid example: large power transformers raise issues of transportation, standardization, flexible design, spares, storage, maintenance, and supply chains [S592]. EPA's water and wastewater supply-chain guide shows the same pattern for treatment chemicals, equipment, and utility preparedness [S577]. World Bank maintenance work reinforces the lifecycle point: deferred maintenance and missing inventories convert routine hazards into long service interruptions [S593].

## Compact rule

**A critical-spares plan is not an inventory count; it is a restoration promise.**

For every critical item, the plan should answer:

- what service fails without it;
- normal lead time and stressed lead time;
- shelf life or maintenance requirement;
- compatible substitutes;
- storage location and hazard exposure;
- transport requirement, including oversize permits if needed;
- release priority when multiple systems need it;
- replenishment rule after use.

## Stockpile discipline

Stockpiles can also fail. They expire, flood, become obsolete, get hoarded, disappear into vendor portals, or become politically captured. The archive's rule is therefore not "stockpile everything." It is **stockpile or standardize the items whose absence causes long service failure, then rotate and audit them.**

For some items, the right answer is local inventory. For others, a regional pool. For others, standardization and mutual aid. For others, procurement framework agreements. For others, repair and refurbishment capacity. The datacube should record which posture applies.

## Failure modes

The bad patterns are predictable: a pump is repaired but a proprietary board is unavailable; a transformer exists but cannot be transported; a water plant has operators but lacks chemicals; a health facility has cold-chain refrigerators but no replacement sensor; a cleanup plan has crews but no PPE; a lab has machines but no reagents; a relief warehouse has supplies but sits in a floodplain.

## Cube routing

Route this file whenever a continuity packet depends on equipment, chemicals, consumables, spare parts, reagents, medical supplies, transformers, pumps, valves, batteries, filters, meters, radios, vehicles, or proprietary systems. Pair with `265` for supply chains, `267` and `268` for circularity / end-of-life, `323` for energy inputs, `324` for repair markets, and `330` for proof rails.

---
Citations point to `sources/register.md`.
