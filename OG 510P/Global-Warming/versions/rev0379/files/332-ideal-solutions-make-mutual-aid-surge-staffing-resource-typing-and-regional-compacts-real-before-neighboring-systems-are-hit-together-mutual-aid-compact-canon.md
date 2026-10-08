---
id: '332'
revision_added: rev0273
status: canon
object_type: service_continuity
domain_tags:
- mutual_aid
- surge_capacity
- regional_compacts
- utilities
- public_safety
- water
- power
- staffing
service_floor:
- mutual_aid_continuity
- surge_staffing
- regional_resource_sharing
hazard_tags:
- hurricane
- wildfire
- flood
- heat
- outage
- cyber
- drought
- compound_shock
- regional_disaster
clock_tags:
- emergency_clock
- recovery_clock
- seasonal_clock
- learning_clock
actor_tags:
- utility
- emergency_manager
- mutual_aid_coordinator
- regional_authority
- state_energy_office
- water_utility
- public_power_utility
- contractor
- labor_union
instrument_tags:
- mutual_aid_agreement
- resource_typing
- crew_roster
- reimbursement
- credential
- compact
- exercise
- pre_position
routes_to:
- '35'
- '39'
- '245'
- '249'
- '252'
- '253'
- '297'
- '303'
- '308'
- '315'
- '319'
- '322'
- '323'
- '324'
- '326'
source_ids:
- S589
- S590
- S591
upstream_dependencies:
- mutual_aid_agreements
- resource_typing
- credentialing
- fuel
- lodging
- communications
- labor_rules
- insurance
- reimbursement_authority
downstream_consequences:
- slow_restoration
- crew_injury
- regional_service_collapse
- reimbursement_dispute
- untrusted_priority
- operator_isolation
equity_lenses:
- small_utilities
- rural_systems
- tribal_governments
- islanded_communities
- low_income_service_areas
- frontline_workers
degraded_modes:
- shared_dispatch_cell
- regional_staging_area
- manual_resource_request
- preapproved_reimbursement
- mobile_command
- reciprocal_crew_pairing
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- same_hazard_regionwide
- crew_fatigue
- liability_uncertainty
- reimbursement_delay
- credential_mismatch
- equipment_incompatibility
- fuel_and_lodging_shortage
- no_resource_typing
failure_modes:
- mutual_aid_on_paper
- neighbors_all_hit
- wrong_equipment_arrives
- crews_blocked_at_reentry
- no_lodging_or_fuel_for_crews
- donated_resources_create_bottlenecks
- informal_aid_without_safety
proof_ledgers:
- mutual_aid_agreement_register
- resource_typing_catalog
- crew_roster
- credential_log
- deployment_time_log
- reimbursement_log
- fatigue_and_safety_log
- after_action_mutual_aid_audit
restoration_conflicts:
- send_crews_away_vs_local_risk
- rapid_deployment_vs_worker_safety
- regional_solidarity_vs_local_political_pressure
- standardization_vs_local_specificity
assurance_tests:
- cross_jurisdiction_deployment_drill
- resource_typing_tabletop
- reimbursement_claim_drill
- crew_lodging_and_fuel_test
- simultaneous_neighbor_failure_scenario
mutual_aid_status: agreement_plus_resource_typing_plus_drill_plus_reimbursement_path
---

# 332 — Ideal Solutions: Make mutual aid, surge staffing, resource typing, and regional compacts real before neighboring systems are hit together

## Claim

Mutual aid is a service floor, not a goodwill slogan. **A system is not resilient because it has neighbors; it is resilient only if help can be requested, typed, dispatched, credentialed, housed, fueled, reimbursed, protected, and learned from under stress.**

This matters more in a warming world because many climate hazards are spatially correlated. The same heat dome, wildfire-smoke event, atmospheric river, hurricane, drought, cyber disruption, or supply-chain shock can hit the usual helpers and the usual helped at the same time.

Water and wastewater WARNs show the logic clearly: utilities helping utilities can share personnel, equipment, materials, and associated services through common agreements [S590]. Public-power mutual-aid systems do the same for electric restoration [S591]. State energy-security and petroleum-response coordination adds the fuel and cross-sector layer [S589]. But the archive now needs the general rule across service floors.

## Compact rule

**No continuity packet may count mutual aid unless it has a tested resource path.**

A resource path names: what is requested; how it is typed; who approves it; how it crosses jurisdictions; how crews enter restricted zones; what fuel, food, lodging, PPE, communications, medical support, and rest they need; how costs are reimbursed; and how workers are protected from exhaustion, heat, smoke, violence, and retaliation.

## Minimum packet

The minimum mutual-aid packet has:

- signed agreements or legal authorities before the event;
- typed equipment and skill lists, not vague offers;
- crew and contractor rosters with credentialing and safety requirements;
- staging sites, lodging, fuel, charging, sanitation, and medical support;
- reimbursement, liability, workers' compensation, and insurance rules;
- multilingual public information so incoming crews are not mistaken for outsiders taking over;
- a demobilization and after-action process that records what actually helped.

## Correlated-risk test

The archive should now ask every service floor: **what if the helper is also hit?**

A county-to-county aid agreement is weak if the entire region floods. A nearby utility may be unavailable during a heat dome. A contractor mutual-aid list may fail if all contractors are repairing their own homes, schools, and depots. A hospital transfer plan may fail if all hospitals are full. A food-bank or shelter plan may fail if volunteer workers cannot travel or need care themselves.

That does not mean mutual aid is useless. It means mutual aid needs depth: local degraded modes, regional compacts, national or international surge, private-sector and nonprofit integration, and pre-negotiated priority rules.

## Failure modes

Bad mutual aid looks ready until activation. It has no standard request form. Equipment names do not match. Crews arrive without compatible radios. Procurement cannot reimburse them. Reentry controls block them. Lodging is unsafe. Heat plans protect the public but not the lineworkers, water operators, debris crews, nurses, inspectors, or volunteers doing restoration.

## Cube routing

Route this file whenever a packet says mutual aid, surge, regional support, backup crew, shared fleet, emergency assistance, contractor surge, volunteer surge, or resource sharing. Pair with `249` for workforce, `303` for public safety, `323` for fuel, `324` for repair markets, `326` for flood-control assets, and `330` for labs / inspectors.

---
Citations point to `sources/register.md`.
