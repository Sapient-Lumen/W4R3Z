---
id: '514'
title: Nuclear emergency preparedness operational proof spine
object_type: integrity_gate
domain_tags:
- nuclear_energy
- nuclear_emergency_preparedness
- radiological_emergency_response
- epz_planning
- public_safety
- civil_protection
- nuclear_public_trust
service_floor:
- nuclear_emergency_preparedness_program
- nuclear_epz_plume_pathway_planning
- nuclear_epz_ingestion_pathway_planning
- nuclear_ki_distribution_decision_pathway
- nuclear_population_monitoring_decontamination
- nuclear_reentry_relocation_recovery_decision
hazard_tags:
- emergency_plan_theater
- epz_demographic_drift
- ki_false_reassurance
- evacuation_route_failure
- recovery_abandonment
- exercise_nonclosure
clock_tags:
- emergency_plan_review_cycle
- evacuation_time_estimate_update_cycle
- biennial_exercise_cycle
- corrective_action_closure_cycle
- recovery_closeout_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_fema
- A_state_emergency_management
- A_local_emergency_management
- A_public_health_authority
- A_public_information_officer
instrument_tags:
- emergency_plan_crosswalk
- epz_operational_assumption_ledger
- sparse_applicability_overlay
- ki_decision_limits_proof
- reentry_relocation_recovery_ladder
routes_to:
- 509
- 510
- 511
- 512
- 513
- 515
- 516
source_ids:
- S953
- S954
- S955
- S956
- S957
- S958
- S959
- S960
- S961
- S962
- S963
- S964
- S965
- S966
- S967
- S968
- S969
- S970
- S971
upstream_dependencies:
- nuclear_assurance_gate
- nuclear_service_floor_map
- nuclear_emergency_preparedness_program
downstream_consequences:
- sparse_emergency_gate_evaluation
- emergency_preparedness_maturity_cap
- public_scorecard_counterevidence
equity_lenses:
- disability_access
- language_access
- no_car_households
- schools_childcare
- hospitals_long_term_care
- tribal_and_cross_jurisdictional_coordination
degraded_modes:
- smoke_heat_flood_or_outage_during_evacuation
- alert_system_partial_failure
- hospital_surge_shortage
- contaminated_food_water_pathway
- recovery_claims_backlog
evidence_grade: authority_plus_local_evidence_required
speculation_level: low_for_authority_high_for_local_readiness_until_evidenced
revision_added: rev0307
status: canon
---

# Nuclear emergency preparedness operational proof spine

Rev0307 changes the emergency-preparedness part of the cube from a broad all-gates-everywhere template into an operational proof spine. The prior matrix remains available as a legacy QA surface, but the emergency-preparedness service floors now have sparse binding gates and a separate change log.

## Minimum proof spine

1. **Reasonable assurance is the top-level test.** The emergency plan is not mature because a binder exists. It is mature only when onsite and offsite plans can show that protective measures can and will be taken, with FEMA/offsite and NRC/onsite interfaces traceable.
2. **The 16 planning standards are first-class controls.** Every emergency-preparedness maturity claim must map to the 10 CFR 50.47(b) planning standards: responsibility assignment, on-shift staffing, assistance resources, classification/action levels, notification, communications, public information, facilities/equipment, dose assessment, protective actions, worker exposure control, medical services, recovery/reentry, exercises, training, and plan maintenance.
3. **EPZ evidence must be local and fresh.** The classic about-10-mile plume pathway and about-50-mile ingestion pathway are planning starts, not proof. The proof is current demographics, access routes, schools, hospitals, long-term-care facilities, carless households, alert reach, evacuation-time estimates, ingestion-pathway controls, and compound-shock assumptions.
4. **KI is not a public-protection substitute.** KI can support thyroid protection against radioactive iodine when directed by officials, but it cannot satisfy evacuation, sheltering, decontamination, population monitoring, food/water controls, medical surge, or recovery gates.
5. **Recovery is not an appendix.** Reentry, relocation, drinking-water decisions, food/agriculture restrictions, cleanup, waste handling, claims, mental-health support, population monitoring, registry readiness, benefits continuity, and counterevidence closure must be pre-authorized enough to operate while trust is damaged.
6. **Exercises must close the loop.** A drill or evaluated exercise does not upgrade maturity until findings are assigned, corrected, retested when material, and visible in a public-safe scorecard.
7. **New reactor emergency planning is a branch, not a waiver.** Small modular, non-light-water, and non-power production or utilization facilities may use a performance-based framework where applicable, but they still need demonstrated emergency response functions, public-information capability, communications, reentry plans, ingestion-response planning, corrective actions, and EPZ basis where an EPZ extends beyond the site boundary.

## Maturity cap

No emergency-preparedness floor should rise above **R2_documented_template_only** unless the site-specific evidence passes the sparse gate set created in rev0307 and the sixteen-planning-standard crosswalk has no open P0 gaps. No KI, public-alert, evacuation, population-monitoring, or recovery claim can substitute for another domain's proof.

## Tables added or made authoritative for this spine

- `cube/nuclear-ep-16-planning-standard-crosswalk.csv`
- `cube/nuclear-epz-operational-assumption-ledger.csv`
- `cube/nuclear-ki-decision-limits-proof.csv`
- `cube/nuclear-reentry-relocation-recovery-ladder.csv`
- `cube/nuclear-emergency-preparedness-sparse-applicability-rule-rev0307.csv`
- `cube/nuclear-emergency-service-floor-gate-evaluation-sparse-rev0307.csv`
- `cube/nuclear-service-floor-map-rev0307-applicability-change-log.csv`


## Rev0308 local-evidence closure overlay

Rev0308 adds the missing local proof layer. The sparse emergency view now routes to `cube/nuclear-local-evidence-status-rev0308.csv`, one row per sparse emergency service-floor/gate binding, and to `cube/nuclear-emergency-corrective-action-closure-rev0308.csv` for closeout rules. This prevents a sparse template from becoming a new paper-readiness surface.
