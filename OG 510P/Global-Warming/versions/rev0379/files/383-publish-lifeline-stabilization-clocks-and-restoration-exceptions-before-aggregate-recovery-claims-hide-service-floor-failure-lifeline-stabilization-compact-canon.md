---
id: '383'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- community_lifelines
- restoration_clock
- service_floor_dashboard
- critical_services
- public_information
service_floor:
- lifeline_stabilization_clock
- public_restoration_exception_path
- time_to_service_floor
hazard_tags:
- compound_hazard
- flood
- storm
- wildfire
- heat
- smoke
- outage
- cyber_disruption
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- utility
- transport_agency
- health_agency
- shelter_operator
- public_information_officer
- community_liaison
instrument_tags:
- publish
- prioritize
- stabilize
- restore
- exception_route
- appeal
- update
routes_to:
- '252'
- '308'
- '331'
- '365'
- '371'
- '381'
- '382'
- '385'
source_ids:
- S536
upstream_dependencies:
- EOC
- telemetry
- utility_status
- transport_access
- public_information
- community_reports
downstream_consequences:
- health_deterioration
- unsafe_return
- shelter_overload
- business_closure
- trust_collapse
equity_lenses:
- medically_dependent_households
- rural_last_mile
- multifamily_residents
- small_businesses
- care_facilities
- no_car_households
degraded_modes:
- manual_status_board
- radio_sitrep
- door_hanger_notice
- community_liaison_update
- public_hotline
evidence_grade: design_judgment
speculation_level: low
bottlenecks:
- restoration_metric_aggregate
- critical_customer_registry_stale
- unserved_pocket_hidden
- private_operator_data_gap
- status_lag
failure_modes:
- percent_restored_masks_critical_need
- dashboard_greenwashing
- restoration_clock_not_public
- exception_request_has_no_owner
- dependency_restored_out_of_sequence
proof_ledgers:
- lifeline_status_board
- time_to_restoration_clock
- critical_customer_exception_log
- unserved_pocket_map
- public_update_archive
lifeline_stabilization_clock: public time-to-service-floor clock by lifeline and exception path
---

# 383 — Ideal Solutions: Publish lifeline stabilization clocks and restoration exceptions before aggregate recovery claims hide service-floor failure

## Core claim

Restoration statistics are not the same as service floors. A utility, road system, water network, payment rail, shelter system, or telecom network can report high aggregate restoration while the users most dependent on that service remain stranded. The cube therefore needs **lifeline stabilization clocks**: public, service-specific clocks that show when the minimum floor is restored, where it is still degraded, and what exception route exists.

FEMA's Community Lifelines doctrine is the right starting point because it frames essential services as incident-stabilization objects rather than sector silos [S536]. The climate cube adds a harder rule: stabilization must be visible at the user path, not only at the infrastructure operator's average status.

## What should be timed

At minimum, the clock should track time to safe water, time to indoor thermal survivability, time to reliable communications, time to basic mobility access, time to medicine / oxygen / dialysis access, time to safe refuge, time to household cash or benefits, time to waste / debris clearance, time to building-safety decision, and time to documented denial / appeal.

The unit of analysis should not only be jurisdiction-wide percent restoration. It should include service pockets: care homes, prisons, mobile-home parks, apartment towers, rural roads, island communities, informal settlements, small business districts, schools, clinics, and critical-customer clusters.

## Exception route

Every public restoration claim should include an exception path: "If your service floor is still down, here is how to report it, what proof is not required, what deadline applies to the agency, and what manual alternative exists." Without that, dashboards can become political cover for hidden non-restoration.

## Operating test

A lifeline is stabilized only when the public clock, owner, degraded mode, critical exceptions, dependency constraints, and next update time are visible. If the dashboard says "power 90% restored" but cannot identify medically dependent customers, oxygen users, cooling sites, elevators, pharmacies, and communications nodes still without service, the cube should not mark the power floor green.

## Cube rule

Service-floor rows should expose `lifeline_stabilization_clock` when post-impact operations are relevant. Blank means the readiness grade is capped: the archive may know the service exists, but it cannot prove restoration timing or exception handling.

---
Citations point to `sources/register.md`.
