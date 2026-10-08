---
id: '375'
revision_added: rev0278
status: canon
object_type: service_continuity
domain_tags:
- heat_health
- thermal_survivability
- worker_safety
- schools
- housing
- transit
- public_health
service_floor:
- executable_heat_action_thresholds
- preimpact_heat_protection
hazard_tags:
- heat
- humidity
- nighttime_heat
- outage
- smoke
- drought
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- public_health_agency
- weather_service
- employer
- school_district
- utility
- housing_inspector
- transit_operator
- care_facility
instrument_tags:
- warn
- open_cooling
- modify_work
- check_facilities
- transport
- enforce
- dashboard
- review
routes_to:
- '279'
- '280'
- '306'
- '311'
- '339'
- '353'
- '363'
- '365'
- '372'
- '378'
source_ids:
- S678
- S679
upstream_dependencies:
- heat_forecast
- vulnerability_map
- cooling_sites
- transport
- staffing
- power
- outreach_roster
downstream_consequences:
- heat_illness
- worker_death
- school_exposure
- care_facility_harm
- unreachable_cooling
equity_lenses:
- outdoor_worker
- elder
- child
- disabled_person
- renter
- homeless_person
- incarcerated_person
- transit_dependent
degraded_modes:
- mobile_cooling
- door_knock_check
- phone_tree
- water_distribution
- work_stoppage
- facility_shelter_in_place
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- alert_without_cooling
- threshold_not_tied_to_work_rules
- cooling_center_unreachable
- facility_no_ac
failure_modes:
- heat_warning_theatre
- emergency_department_surge
- employer_noncompliance
- cooling_access_failure
proof_ledgers:
- heat_action_threshold_table
- cooling_site_log
- work_rest_enforcement_log
- facility_check_log
- heat_mortality_review
restoration_conflicts:
- economic_activity_vs_worker_safety
- school_continuity_vs_child_heat_risk
- privacy_vs_targeted_outreach
- grid_stress_vs_cooling_need
assurance_tests:
- heat_threshold_activation_drill
- cooling_transport_test
- outdoor_worker_mystery_shop
- care_facility_heat_audit
forecast_trigger_rule: HeatRisk_or_local_health_trigger
heat_action_threshold: published_multiagency_threshold_table
---
# 375 — Ideal Solutions: Make heat-action thresholds executable across health, labor, schools, transit, housing, and events before HeatRisk remains informational

## Core claim

Heat is the clearest example of a forecast that must become an operating order. A heat map or advisory does not cool an apartment, stop unsafe outdoor work, check an elder, reduce school exposure, keep transit running, or staff a cooling center.

NWS HeatRisk provides a color-numeric indication of expected heat-related impacts, including categories that affect sensitive groups, health systems, industries, and eventually anyone without effective cooling or hydration [S678]. The CDC/NWS collaboration notes that early warning systems and action plans can reduce heat-exposure risk, and that alerts and advisories before or during heat periods can save lives [S679].

## Heat-action thresholds

A heat-action packet should pre-commit thresholds for:

- public-health outreach and clinical surge;
- cooling-center opening and transport;
- utility shutoff moratoria and reconnection;
- school recess, sports, dismissal, and building checks;
- outdoor work-rest-water-shade rules;
- transit slowdown, station cooling, and paratransit priority;
- prison, jail, shelter, eldercare, and care-home checks;
- indoor rental-housing temperature complaints;
- event cancellation or modification;
- public dashboard status and next update.

The threshold should not be only meteorological. It should include vulnerability: nighttime heat, humidity, lack of air conditioning, power reliability, urban heat island, smoke co-exposure, medications, age, disability, homelessness, institutional settings, and outdoor labor.

## Why this is separate from cooling

The archive already has cooling and thermal survivability files. This file adds the operating rule: **when heat is forecast, who changes what before bodies start showing up in emergency departments?** The answer must span health, labor, housing, schools, utilities, transit, shelters, and care institutions.

## The degraded-mode rule

A heat-action plan fails if it depends on perfect grid service, smartphones, English-language alerts, cars, voluntary employer compliance, or people choosing to leave unsafe housing. Degraded mode means door-to-door or phone outreach, mobile cooling, shaded water points, transport, legal enforcement, offline call lists, facility checks, and medically targeted assistance.

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
