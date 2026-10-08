---
id: '489'
title: Nuclear climate hazard site screen and external-event reanalysis router
object_type: router
domain_tags:
- nuclear_energy
- climate_resilience
- external_hazards
- site_reanalysis
- compound_hazard
- climate_stress_test
service_floor:
- nuclear_climate_hazard_site_screen
- nuclear_site_hazard_reanalysis_cycle
- nuclear_climate_loadcase_stress_test
- nuclear_compound_hazard_pra
- nuclear_climate_periodic_safety_review
hazard_tags:
- flood
- storm_surge
- extreme_heat
- drought
- wildfire_smoke
- compound_hazard
- climate_model_uncertainty
clock_tags:
- pre_fid_site_screen
- ten_year_periodic_safety_review
- annual_climate_hazard_refresh
- post_event_reanalysis
actor_tags:
- A_nuclear_regulator
- A_nuclear_operator
- A_climate_risk_modeler
- A_public_auditor
- A_host_community_reviewer
instrument_tags:
- climate_hazard_site_screen
- external_event_reanalysis
- compound_hazard_pra
- site_characteristics_review
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '421'
- '422'
- '428'
- '429'
- '430'
- '436'
- '488'
- '490'
- '493'
source_ids:
- S901
- S902
- S903
- S904
- S910
- S911
- S912
upstream_dependencies:
- nuclear_policy_preference
- climate_hazard_assessment
- external_hazard_design_basis
- public_assurance_evidence
downstream_consequences:
- site/external-hazard screening_caps_nuclear_maturity
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

# 489 — Nuclear climate hazard site screen and external-event reanalysis router

## Function

This router makes the cube's pro-nuclear preference conditional on climate-aware siting and periodic external-hazard reanalysis. Nuclear is favored as clean firm capacity, but not if the site hazard basis is stale, single-hazard, or blind to changing meteorological and hydrological conditions.

## Nuclear-positive rule

Prefer nuclear where it can supply clean firm power and public-service continuity under stress. Require site and design-basis evidence that covers flood, storm surge, heat, drought, wildfire smoke, seismic/external interactions, and compound hazards before maturity rises above template level.

## Control-plane effect

Rev0301 adds nuclear climate hazard screens, external-event reassessment, compound-hazard PRA, climate-loadcase stress tests, independent review hooks, and public exception ledgers. The site screen becomes a gate, not a note.

## Evidence burden

Minimum evidence includes site characteristics review, climate trend assumptions, hazard-margin treatment, design-basis and beyond-design-basis analysis, peer/regulator review, and a dated reanalysis cycle. Sources: [S901]; [S902]; [S903]; [S904]; [S910]; [S911]; [S912].
