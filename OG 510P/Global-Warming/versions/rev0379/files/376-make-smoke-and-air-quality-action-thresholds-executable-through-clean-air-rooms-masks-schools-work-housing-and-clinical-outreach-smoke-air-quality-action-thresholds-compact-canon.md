---
id: '376'
revision_added: rev0278
status: canon
object_type: service_continuity
domain_tags:
- wildfire_smoke
- air_quality
- clean_air
- schools
- worker_safety
- housing
- clinical_outreach
service_floor:
- executable_smoke_action_thresholds
- clean_air_access_under_smoke
hazard_tags:
- wildfire_smoke
- pm25
- ozone
- heat
- outage
- wildfire
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- public_health_agency
- air_quality_agency
- school_district
- employer
- housing_inspector
- shelter_operator
- clinician
instrument_tags:
- monitor
- warn
- activate_clean_air
- distribute_masks
- modify_work
- filter
- inspect
- review
routes_to:
- '306'
- '311'
- '339'
- '341'
- '353'
- '363'
- '365'
- '366'
- '372'
- '375'
source_ids:
- S680
- S681
upstream_dependencies:
- AQI_forecast
- indoor_air_monitoring
- filters
- masks
- clean_air_sites
- clinical_rosters
- school_rules
downstream_consequences:
- respiratory_surge
- unsafe_school_activity
- worker_exposure
- shelter_harm
- indoor_exposure_invisible
equity_lenses:
- asthma_patient
- pregnant_person
- child
- elder
- outdoor_worker
- renter
- incarcerated_person
- homeless_person
degraded_modes:
- clean_air_room
- portable_filter_distribution
- respirator_distribution
- work_modification
- mobile_clinic_outreach
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- outdoor_AQI_without_indoor_action
- clean_air_room_unpowered
- masks_not_stocked
- work_rule_unenforced
failure_modes:
- smoke_advice_without_access
- indoor_false_safety
- heat_smoke_conflict
- clinical_outreach_gap
proof_ledgers:
- AQI_action_table
- filter_inventory
- mask_distribution_log
- indoor_pm25_sample_log
- school_activity_log
restoration_conflicts:
- ventilation_vs_smoke_intrusion
- work_continuity_vs_exposure
- privacy_vs_clinical_outreach
- heat_cooling_vs_clean_air
assurance_tests:
- smoke_threshold_activation_drill
- clean_air_room_power_test
- mask_distribution_drill
- school_smoke_decision_review
forecast_trigger_rule: AQI_or_smoke_forecast_trigger
smoke_air_quality_action_threshold: AQI_PM25_to_clean_air_action_table
---
# 376 — Ideal Solutions: Make smoke and air-quality action thresholds executable through clean-air rooms, masks, schools, work, housing, and clinical outreach

## Core claim

Smoke is both an outdoor hazard and an indoor service-floor test. A city can publish air-quality data and still fail if schools, shelters, workplaces, prisons, clinics, transit stations, and rental housing do not have executable clean-air actions.

AirNow provides current and forecast AQI information and a Fire and Smoke Map; the AQI is designed to communicate how clean or polluted outdoor air is and associated health effects [S680]. EPA's wildfire-smoke health course emphasizes that clinicians and public-health actors should use the AQI to advise patients, prepare before smoke is in the air, reduce co-exposure to smoke and heat, and deploy indoor and outdoor exposure-reduction strategies [S681].

## Smoke-action thresholds

A smoke-action packet should define:

- AQI / PM2.5 thresholds and local forecast rules;
- school outdoor-activity and closure/modification rules;
- clean-air shelter and clean-air room activation;
- filtration, HVAC, portable HEPA, and mask inventory;
- worker protection and outdoor-work limits;
- clinical outreach to asthma, COPD, pregnancy, cardiovascular, elder, child, and immunocompromised groups;
- housing inspection or complaint routes for smoke intrusion;
- transit and public-space protection;
- combined heat-smoke rules;
- public dashboard and rumor-control messaging.

## The indoor truth problem

Smoke plans often over-rely on outdoor monitors. The service-floor question is: **what is the indoor exposure of people who cannot leave, cannot seal their housing, cannot afford filtration, or are confined in institutions?** The cube should require at least a sampleable indoor-air pathway for schools, shelters, care homes, custody, and clean-air rooms.

## Masks and filtration are logistics, not advice

Advice to “stay indoors” or “use a respirator” is not a service floor when buildings are leaky, workers must work, masks are unavailable or poorly fitted, and households cannot buy filters. Smoke readiness therefore depends on procurement, inventory, distribution, fit guidance, multilingual communication, and enforcement against unsafe work.

## Operating test

The file is operational only if a named owner can answer five questions before the event, not while the event is already unfolding:

1. What signal activates the action?
2. Who is authorized to act without waiting for a new meeting?
3. What money, staff, contracts, routes, and public messages are already pre-cleared?
4. Which households, workers, institutions, or places are likely to be missed by the nominal channel?
5. How will the decision be reviewed if the forecast misses, the hazard shifts, or the action causes harm?

A forecast, warning, model, dashboard, or alert is not a service floor by itself. It becomes a service floor only when it releases an owned action bundle with funding, authority, equity checks, degraded modes, public explanation, and after-action learning.

## Cube rule

Every trigger-facing packet should expose `forecast_trigger_rule`, `impact_based_decision_support`, `anticipatory_finance_rule`, `protective_action_authority`, `alert_interoperability_state`, `false_alarm_learning`, and `prepositioning_state` where relevant. Blank fields mean the cube should demote the readiness score, not assume the prose is sufficient.

---
Citations point to `sources/register.md`.
