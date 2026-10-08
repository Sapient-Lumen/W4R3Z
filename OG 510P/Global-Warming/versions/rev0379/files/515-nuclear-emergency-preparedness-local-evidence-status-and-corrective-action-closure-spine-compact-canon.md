---
id: '515'
title: Nuclear emergency preparedness local evidence status and corrective action closure spine
object_type: integrity_gate
domain_tags:
- nuclear_energy
- nuclear_emergency_preparedness
- local_evidence_status
- corrective_action_closure
- exercise_evidence
- public_safety
service_floor:
- nuclear_emergency_preparedness_program
- nuclear_after_action_corrective_action_closure
- nuclear_population_monitoring_decontamination
- nuclear_reentry_relocation_recovery_decision
- nuclear_epz_plume_pathway_planning
- nuclear_epz_ingestion_pathway_planning
hazard_tags:
- paper_readiness
- stale_local_evidence
- exercise_nonclosure
- false_green_scorecard
- public_trust_collapse
clock_tags:
- emergency_plan_review_cycle
- corrective_action_closure_cycle
- source_freshness_cycle
- exercise_evidence_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_fema
- A_state_emergency_management
- A_local_emergency_management
- A_public_health_authority
- A_public_information_officer
instrument_tags:
- local_evidence_status_table
- corrective_action_closure_pattern
- exercise_inject_runbook
- decision_log_minimum_fields
routes_to:
- 509
- 510
- 511
- 512
- 513
- 514
- 516
source_ids:
- S954
- S956
- S958
- S960
- S962
- S963
- S967
- S968
- S969
- S970
- S971
- S972
- S973
- S974
- S975
- S976
- S977
- S978
upstream_dependencies:
- nuclear_emergency_service_floor_gate_evaluation_sparse_rev0308
- nuclear_local_evidence_status_rev0308
- nuclear_emergency_corrective_action_closure_rev0308
downstream_consequences:
- emergency_preparedness_maturity_cap
- site_localization_import
- public_safe_counterevidence_scorecard
equity_lenses:
- disability_access
- language_access
- no_car_households
- schools_childcare
- hospitals_long_term_care
- worker_and_first_responder_safety
degraded_modes:
- compound_disaster_during_radiological_event
- alert_channel_partial_failure
- crc_throughput_shortfall
- ingestion_pathway_delay
- recovery_claims_backlog
evidence_grade: authority_plus_site_specific_evidence_required
speculation_level: low_for_template_structure_high_for_site_readiness_until_artifacts_loaded
revision_added: rev0308
status: canon
---

# Nuclear emergency preparedness local evidence status and corrective action closure spine

Rev0308 is a turn away from doctrine and toward executable readiness. Rev0307 made emergency-preparedness applicability sparse; rev0308 makes each sparse binding prove itself locally.

## Operating rule

No emergency-preparedness gate may upgrade above **R2_documented_template_only** merely because the sparse template says the gate applies. A site, project, or jurisdiction must load a local evidence row with an artifact reference, owner, independent verifier, freshness date, exercise or tabletop evidence where operational, open-deficiency status, and public-safe counterevidence path.

## What changed

- `cube/nuclear-local-evidence-status-rev0308.csv` creates 264 local proof slots, one for every row in the sparse emergency service-floor/gate view.
- `cube/nuclear-emergency-service-floor-gate-evaluation-sparse-rev0308.csv` carries the sparse view forward and adds an explicit maturity-upgrade blocker if local evidence is missing.
- `cube/nuclear-emergency-corrective-action-closure-rev0308.csv` adds closeout patterns for the failures most likely to be waved away after an exercise: stale EPZ data, alert failure, evacuation bottlenecks, KI false reassurance, CRC throughput, ingestion-pathway delay, emergency-worker exposure control, recovery/claims gaps, and compound-disaster degraded access.
- `cube/nuclear-emergency-exercise-inject-runbook-rev0308.csv` turns the compound-disaster loadcases into timed injects that force decisions, evidence capture, and corrective-action closure.
- `cube/nuclear-emergency-decision-log-minimum-fields-rev0308.csv` defines the minimum decision record needed to audit protective-action, ingestion, KI, monitoring, reentry, recovery, and exercise decisions.

## Non-negotiable readiness cap

A local evidence row is not satisfied by a plan excerpt alone. It needs dated, accountable, testable evidence. A row remains capped when any of the following is missing:

1. the local artifact or artifact reference;
2. the accountable owner and independent verifier;
3. a freshness date inside the row's SLA or a documented material-change review;
4. exercise, drill, tabletop, or decision-log evidence for operational claims;
5. a corrective-action record for observed failure modes;
6. a public-safe disclosure and counterevidence path.

## The practical failure this is meant to prevent

The most dangerous state is not an obviously missing plan. It is a green-looking emergency-preparedness scorecard built from real guidance, real crosswalks, and no local evidence. Rev0308 makes that state visible: the package now contains the slots where local proof must go, and it initializes them as missing rather than pretending generic doctrine is evidence.

## Next hard move

The next high-value artifact is a direct emergency-plan-change/effectiveness table for 10 CFR 50.54(q)-style reviews and a parallel 10 CFR 50.160 performance-objective metrics table for SMR/non-LWR/NPUF branches.
