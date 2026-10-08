---
id: '370'
revision_added: rev0277
status: canon
object_type: service_continuity
domain_tags:
- infectious_disease
- vector_control
- wastewater_surveillance
- environmental_health
- climate_health
- laboratories
service_floor:
- climate_sensitive_disease_surveillance
- outbreak_early_warning_and_response
hazard_tags:
- heat
- flood
- drought
- storm
- displacement
- water_contamination
- vector_shift
- disease_outbreak
clock_tags:
- seasonal_clock
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- public_health_agency
- laboratory
- wastewater_utility
- vector_control_team
- clinician
- school
- shelter_operator
- community_health_worker
instrument_tags:
- surveil
- sample
- test
- warn
- treat
- vector_control
- vaccinate
- coordinate
routes_to:
- '24'
- '277'
- '278'
- '279'
- '280'
- '311'
- '316'
- '330'
source_ids:
- S387
- S663
- S664
- S665
upstream_dependencies:
- labs
- wastewater_utility
- clinics
- vector_control
- climate_services
- WASH
- shelters
- public_communications
downstream_consequences:
- preventable_outbreak
- hospital_surge
- school_closure
- worker_absence
- shelter_harm
- water_and_food_insecurity
equity_lenses:
- children
- older_adults
- immunocompromised_people
- displaced_people
- informal_settlement_residents
- rural_communities
- people_without_healthcare_access
degraded_modes:
- sentinel_clinic_reporting
- mobile_testing
- wastewater_priority_sites
- community_health_worker_reports
- syndromic_hotline
- conservative_WASH_notice
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- lab_capacity
- delayed_case_reporting
- wastewater_site_gap
- vector_control_staff_shortage
- weak_climate_health_integration
- shelter_health_surveillance_gap
failure_modes:
- outbreak_detected_after_health_system_surge
- vector_shift_not_tracked
- wastewater_signal_not_connected_to_action
- shelter_cluster_missed
- flood_WASH_failure_becomes_disease_event
proof_ledgers:
- syndromic_surveillance_log
- wastewater_trend_dashboard
- vector_trap_and_control_log
- lab_turnaround_log
- shelter_health_cluster_log
- climate_health_alert_log
restoration_conflicts:
- privacy_vs_granularity
- false_alarm_vs_delayed_action
- vector_control_vs_ecology
- limited_lab_capacity_vs_multi_pathogen_testing
assurance_tests:
- wastewater_signal_action_drill
- vector_outbreak_tabletop
- shelter_cluster_detection_test
- lab_surge_turnaround_test
- climate_health_alert_relay_test
infectious_disease_surveillance: climate_health_readiness_requires_climate_services_wastewater_vector_clinical_lab_and_shelter_surveillance_linked_to_action
---

# 370 — Ideal Solutions: Protect infectious disease, vector, wastewater, and environmental surveillance as climate health rails

## Claim

Heat, flood, drought, displacement, poor air, damaged WASH systems, food insecurity, animal stress, and ecological change can shift infectious-disease risk. Climate-health readiness therefore needs surveillance rails before the outbreak is obvious to hospitals.

CDC describes wastewater monitoring as public-health infrastructure for monitoring infectious diseases through wastewater; it can help local agencies identify outbreak trends early, direct prevention, and complement other surveillance data [S663]. WMO's health-focused climate-services report says the health sector needs tailored climate information for extreme weather, poor air quality, shifting infectious-disease patterns, and food and water insecurity [S664]. WHO says dengue cases have grown dramatically in recent decades and links spread risk to changing vector distribution, climate conditions, surveillance limitations, overburdened health systems, and population movements [S387]. WHO's dengue and Aedes plan emphasizes collaborative surveillance, laboratory diagnostics, vector control, community protection, clinical management, and access to countermeasures [S665].

House rule: **climate-health surveillance is a service floor when signals are tied to thresholds, owners, public action, and clinical capacity.**

## Fast rule

For every climate-sensitive disease threat, specify the signal, threshold, owner, lab capacity, clinical route, community action, vector or WASH control, and public communication path.

## The compact canon

### 1. Surveillance must be collaborative

Clinical reporting, syndromic surveillance, wastewater, vector traps, school absences, shelter health logs, veterinary data, WASH indicators, weather forecasts, and community reports should be connected through a public-health operating loop.

### 2. Wastewater is early warning, not diagnosis

Wastewater trends can help detect signals before individual testing is widespread, especially when clinical testing is scarce. But signals need interpretation, representative site coverage, privacy safeguards, and action thresholds.

### 3. Vector control is service continuity

Dengue, chikungunya, Zika, malaria, West Nile, tick-borne diseases, and other vector risks are not only health-department topics. They involve drainage, water storage, waste, housing screens, schools, camps, shelters, worker protection, and community engagement.

### 4. Shelters and displacement sites need health surveillance

Congregate shelters, camps, schools, prisons, dormitories, and temporary housing can become outbreak amplifiers. Health logs, isolation options, WASH, ventilation, vaccination, medication access, and referral pathways should be ready before occupancy.

### 5. Climate services should trigger health operations

Heat, rainfall, humidity, drought, flood, smoke, and ecological indicators should not remain in meteorological dashboards. They should trigger vector control, WASH notice, staffing, medicine stock, outreach, and clinical readiness.

## Minimum packet

A climate-health surveillance packet includes: disease list; climate trigger; wastewater and sentinel site map; lab throughput; vector-control plan; shelter health log; WASH thresholds; clinical guidance; public notice; privacy rule; and after-action correction ledger.

## Bottom line

The archive should not wait for climate-sensitive disease to show up as hospital surge. The floor is early signal, fast action, and equitable access to prevention and care.

---
Citations point to `sources/register.md`.
