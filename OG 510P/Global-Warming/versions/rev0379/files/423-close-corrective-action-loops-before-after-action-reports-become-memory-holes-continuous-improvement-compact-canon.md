---
id: '423'
revision_added: rev0284
status: canon
object_type: delivery_packet
domain_tags:
- continuous_improvement
- after_action
- corrective_action
- exercise_to_fix
- learning_system
- nuclear_cyber_digital_assurance
service_floor:
- corrective_action_state
- closed_loop_learning
- retest_before_readiness_claim
hazard_tags:
- compound_hazard
clock_tags:
- learning_clock
- emergency_clock
- seasonal_clock
actor_tags:
- emergency_manager
- service_owner
- exercise_planner
- auditor
- community_reviewer
instrument_tags:
- after_action_report
- improvement_plan
- corrective_action_tracker
- root_cause_review
- retest
routes_to:
- '322'
- '338'
- '364'
- '378'
- '404'
- '422'
- '428'
- '498'
source_ids:
- S602
- S763
- S764
upstream_dependencies:
- incident_records
- exercise_load_case
- assessment_stabilization_ledger
- owner_accountability
downstream_consequences:
- better_next_event
- reduced_repeat_failure
- evidence_based_budget
- updated_training
equity_lenses:
- people_harmed_by_prior_failure
- community_organizations
- frontline_workers
- language_access_users
degraded_modes:
- paper_tracker_with_owner_due_date
- sampled_retest
- public_exception_note
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- aar_written_but_not_owned
- due_dates_missing
- corrections_unfunded
- same_failure_repeats
failure_modes:
- lessons_become_archive
- exercise_theatre
- unclosed_findings
- readiness_claim_ignores_real_incident
proof_ledgers:
- aar_ip
- corrective_action_register
- root_cause_log
- closure_evidence
- retest_record
- public_lessons_dashboard
corrective_action_state: finding has owner, due date, funding or constraint note,
  closure evidence, retest, and public status
---

# 423 — Close corrective-action loops before after-action reports become memory holes

## Core claim

A lesson is not learned when it is written. It is learned when the underlying condition changes and the next drill, season, or event proves the change.

FEMA's National Continuous Improvement Guidance explicitly supports programs beyond After-Action Reports, including incident operations, process improvement, and issue resolution [S763]. FEMA's HSEEP improvement-planning materials say an effective corrective-action program develops dynamic improvement plans with corrective actions continually monitored and implemented [S764]. The archive already uses exercise loadcases; rev0284 requires those loadcases to generate closure evidence rather than reports alone [S602].

## Corrective-action packet

Every material exercise, incident, audit, complaint, miss, false alarm, denied claim, or service-floor failure should produce a corrective-action row with:

- finding and root cause;
- affected service floor and population;
- owner and backup;
- due date and funding path;
- interim risk acceptance or temporary control;
- closure evidence;
- retest date and loadcase;
- public status where safe.

## Anti-memory-hole rule

A repeat finding is not a new finding. It is evidence that prior governance failed. Repeated corrective-action closure without retest should reduce readiness maturity.

## Cube rule

The field `corrective_action_state` distinguishes paper learning from operational learning. Blank means the archive cannot tell whether mistakes are being repaired or merely remembered.

---
Citations point to `sources/register.md`.
