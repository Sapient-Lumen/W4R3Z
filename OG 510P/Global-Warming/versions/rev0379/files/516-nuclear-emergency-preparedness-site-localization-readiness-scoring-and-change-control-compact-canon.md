---
id: '516'
title: Nuclear emergency preparedness site localization, readiness scoring, and change control
object_type: integrity_gate
domain_tags:
- nuclear_energy
- nuclear_emergency_preparedness
- site_localization
- readiness_scoring
- emergency_plan_change_control
- smr_performance_objectives
- public_safety
service_floor:
- nuclear_emergency_preparedness_program
- nuclear_epz_plume_pathway_planning
- nuclear_epz_ingestion_pathway_planning
- nuclear_population_monitoring_decontamination
- nuclear_reentry_relocation_recovery_decision
- nuclear_after_action_corrective_action_closure
hazard_tags:
- synthetic_fixture_misuse
- false_green_scorecard
- emergency_plan_change_reduction_in_effectiveness
- smr_performance_objective_gap
- compound_disaster_during_radiological_event
- site_local_evidence_gap
clock_tags:
- emergency_plan_change_review_cycle
- exercise_evidence_cycle
- corrective_action_closure_cycle
- source_freshness_cycle
- sqlite_mirror_refresh_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_fema
- A_state_emergency_management
- A_local_emergency_management
- A_public_health_authority
- A_public_information_officer
- A_independent_reviewer
instrument_tags:
- synthetic_site_fixture
- local_evidence_sample_import
- readiness_scorecard
- gap_burndown
- 50_54q_change_effectiveness_review
- 50_160_performance_objective_metrics
- emergency_sqlite_mirror
routes_to:
- 509
- 510
- 511
- 512
- 513
- 514
- 515
source_ids:
- S954
- S956
- S958
- S960
- S962
- S963
- S967
- S968
- S972
- S973
- S974
- S975
- S976
- S977
- S978
- S979
- S980
- S981
- S982
- S983
- S984
upstream_dependencies:
- nuclear_local_evidence_status_rev0308
- nuclear_emergency_service_floor_gate_evaluation_sparse_rev0308
- nuclear_emergency_exercise_inject_runbook_rev0308
- nuclear_emergency_corrective_action_closure_rev0308
downstream_consequences:
- site_local_readiness_scoring
- gap_burndown_queue
- emergency_plan_change_screening
- smr_performance_objective_branch
- public_safe_counterevidence_scorecard
equity_lenses:
- disability_access
- language_access
- no_car_households
- schools_childcare
- hospitals_long_term_care
- worker_and_first_responder_safety
- tribal_and_cross_jurisdictional_coordination
degraded_modes:
- synthetic_fixture_not_real_evidence
- performance_branch_unproven
- failed_exercise_open_corrective_action
- stale_epz_data
- crc_throughput_shortfall
- alert_channel_partial_failure
- ingestion_pathway_delay
evidence_grade: synthetic_fixture_plus_authority_control_structure
speculation_level: medium_for_fixture_scenarios_low_for_control_requirements
revision_added: rev0309
status: canon
---

# Nuclear emergency preparedness site localization, readiness scoring, and change control

Rev0309 is the first emergency-preparedness revision that deliberately stops at the edge of real-world evidence and makes that boundary executable. Rev0308 created the local proof slots; this revision adds synthetic site/jurisdiction fixtures, sample local evidence rows, floor-level readiness scores, exercise outcomes, a gap burn-down queue, a 10 CFR 50.54(q)-style change-effectiveness review table, a 10 CFR 50.160 performance-objective branch table, and a small emergency SQLite mirror.

## Non-negotiable interpretation

The site fixtures are **not** real plant records and must not be used as evidence that any real site is ready. Their value is narrower and more useful: they prove that the cube can ingest site-local evidence, cap maturity when evidence is stale or missing, surface P0 failures, and separate large-LWR emergency-planning assumptions from performance-based SMR/non-LWR/NPUF branches.

## Why this was the riskiest unfinished work

A sparse gate model can still become paper readiness if every sparse row stays at `SITE_TBD`. Rev0309 converts the template into a worked model:

1. `cube/nuclear-emergency-site-localization-fixture-rev0309.csv` defines four synthetic site archetypes with different hazard, population, EPZ, CRC, transportation, public-alert, and recovery burdens.
2. `cube/nuclear-emergency-jurisdiction-localization-fixture-rev0309.csv` creates the offsite jurisdictions that must own school, health, public-alert, transportation, shelter, ingestion-pathway, and recovery work.
3. `cube/nuclear-local-evidence-status-site-sample-rev0309.csv` expands the 264 rev0308 proof slots across the four fixtures and assigns current, stale, failed, missing, or performance-branch-unproven status.
4. `cube/nuclear-emergency-readiness-scorecard-site-sample-rev0309.csv` computes floor and site maturity caps from those rows instead of from doctrine.
5. `cube/nuclear-emergency-gap-burndown-rev0309.csv` lists concrete closure work for open fixture gaps, including owner, first closure step, retest need, and readiness cap.

## What counts as progress now

A row improves only by loading a dated artifact, proving the artifact is inside its freshness SLA, showing exercise or decision-log evidence where operational, closing or compensating deficiencies, and preserving a public-safe counterevidence path. A plan excerpt, a stockpile, a memorandum, or a general crosswalk is not enough.

## Change-control branch

The new `cube/nuclear-emergency-50-54q-effectiveness-review-rev0309.csv` table turns emergency-plan changes into screened decisions. Any proposed change that could reduce emergency-plan effectiveness is routed to prior-approval / non-implementation until independently screened and supported.

## New-reactor branch

The new `cube/nuclear-emergency-50-160-performance-objective-metrics-rev0309.csv` table prevents a different failure: treating performance-based emergency preparedness as a waiver. For advanced reactor fixtures, the cube demands demonstrable emergency response capabilities, protective-action communication, dose assessment, reentry/recovery, public information, and corrective-action closure before maturity can rise.

## Refactor boundary

Rev0309 still retains the legacy universal nuclear crossproduct tables for compatibility. It does not let them be canonical for emergency-preparedness applicability or site readiness. The canonical operational chain for this area is now:

` sparse gate applicability -> local evidence slot -> site evidence status -> exercise result -> corrective action -> readiness score -> gap burn-down `
