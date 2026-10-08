---
id: '491'
title: Nuclear station blackout, backup power, spent fuel, and common-cause router
object_type: integrity_gate
domain_tags:
- nuclear_energy
- station_blackout
- backup_power
- spent_fuel_cooling
- common_cause_failure
- fukushima_lessons
service_floor:
- nuclear_station_blackout_coping
- nuclear_loss_of_offsite_power_recovery
- nuclear_backup_power_fuel_security
- nuclear_fukushima_mitigation_strategies
- nuclear_spent_fuel_pool_instrumentation
- nuclear_emergency_core_cooling_extreme_event
- nuclear_multi_unit_site_common_cause_control
hazard_tags:
- station_blackout
- loss_of_offsite_power
- backup_power_failure
- spent_fuel_cooling_loss
- multi_unit_common_cause
- severe_accident_resource_contention
clock_tags:
- station_blackout_drill
- backup_power_fuel_rotation
- spent_fuel_monitoring_test
- multi_unit_resource_drill
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_emergency_manager
- A_grid_operator
- A_public_auditor
instrument_tags:
- station_blackout_coping_analysis
- backup_power_inventory
- spent_fuel_instrumentation_test
- fukushima_mitigation_strategy
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '430'
- '442'
- '449'
- '450'
- '452'
- '489'
- '490'
- '493'
source_ids:
- S903
- S905
- S907
- S908
- S909
- S911
upstream_dependencies:
- nuclear_policy_preference
- climate_hazard_assessment
- external_hazard_design_basis
- public_assurance_evidence
downstream_consequences:
- backup-power and severe-accident interface_caps_nuclear_maturity
- pro_nuclear_preference_becomes_climate_stress_tested
- public_exception_and_counterevidence_path_required
equity_lenses:
- host_communities
- disabled_people
- language_access
- older_adults
- medically_dependent_people
- future_generations
degraded_modes:
- template_only_without_local_evidence
- stale_climate_hazard_basis
- single_hazard_analysis
- unfunded_resilience_backlog
- public_counterevidence_unclosed
evidence_grade: mixed
speculation_level: medium
revision_added: rev0301
status: canon
---

# 491 — Nuclear station blackout, backup power, spent fuel, and common-cause router

## Function

This integrity gate turns extreme-event survivability into auditable records: station blackout coping, loss-of-offsite-power recovery, backup-power fuel logistics, spent-fuel pool instrumentation and cooling, Fukushima mitigation strategies, and multi-unit common-cause resource contention.

## Nuclear-positive rule

The cube favors nuclear, but only where severe-event coping strategies remain credible under climate-amplified hazards. Backup power, cooling, instrumentation, logistics, staffing, and communications must survive the same event, not merely exist on paper.

## Refactor output

Rev0301 adds station blackout and backup-power tables, spent-fuel cooling resilience records, common-cause hazard drills, and maturity caps for plants or projects that lack credible severe-event evidence.

## Evidence burden

Minimum evidence includes coping analysis, tested alternate AC or equivalent strategies, fuel/logistics records, hardened spent-fuel monitoring, severe-event procedures, drill results, and post-Fukushima mitigation status. Sources: [S903]; [S905]; [S907]; [S908]; [S909]; [S911].
