---
id: '452'
title: 452 — Nuclear operating experience, event reporting, root-cause, and corrective-action
  loop
object_type: corrective_action
domain_tags:
- nuclear_energy
- operating_experience
- event_reporting
- root_cause
- corrective_action
- nonrecurrence
- safety_culture
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_operating_experience_feedback
- nuclear_event_reporting_and_root_cause
- nuclear_forced_outage_recovery
- nuclear_configuration_management
- nuclear_cyber_physical_operations
hazard_tags:
- recurring_event
- near_miss_unreported
- root_cause_misclassification
- corrective_action_stale
- safety_culture_decline
- cyber_physical_event
clock_tags:
- event_notification_window
- root_cause_completion_window
- corrective_action_due_date
- operating_experience_review_cycle
- public_reporting_window
actor_tags:
- A_operating_experience_program
- A_nuclear_regulator
- A_public_auditor
- A_cybersecurity_authority
- A_nuclear_operator
instrument_tags:
- operating_experience_program
- event_report
- root_cause_analysis
- corrective_action_program
- nonrecurrence_test
- public_event_summary
routes_to:
- '110'
- '121'
- '422'
- '423'
- '424'
- '428'
- '441'
- '443'
- '449'
- '450'
- '451'
- '453'
- '459'
- '460'
- '461'
- '462'
- '463'
- '464'
- '465'
- '466'
- '467'
- '468'
- '489'
- '490'
- '491'
- '492'
- '493'
source_ids:
- S814
- S815
- S818
- S820
- S817
upstream_dependencies:
- event_capture_system
- safety_culture_reporting_channel
- independent_review_authority
- corrective_action_owner
- configuration_records
downstream_consequences:
- less_recurrence_if_operating_experience_is_closed_into_design_and_training
- false_maturity_if_events_are_counted_but_not_learned_from
- public_trust_if_event_summaries_and_challenge_routes_exist
equity_lenses:
- worker_voice
- whistleblower_protection
- host_community_right_to_know
- public_challenge
degraded_modes:
- event_reporting_without_root_cause
- corrective_action_closed_without_effectiveness_review
- near_miss_suppressed
- operating_experience_not_routed_to_training_or_design
evidence_grade: mixed
speculation_level: low
revision_added: rev0293
status: canon
---

# 452 — Nuclear operating experience, event reporting, root-cause, and corrective-action loop

## Nuclear-positive rule

The cube now favors nuclear energy not only at the build decision, but through operations. A nuclear pathway earns clean-firm priority only when the operating fleet, project, or service floor can show current evidence for safe availability, performance indicators, outage/refueling discipline, maintenance and spares, operating-experience feedback, grid-service claims, and corrective-action closure.

## What this file adds

This file turns the nuclear preference into an operations assurance requirement. It prevents a nameplate-capacity or policy-support claim from being treated as deliverable clean-firm power unless the operations evidence is current, traceable, and connected to the service-floor gate engine.

## Minimum evidence expected

- current operating-performance or availability evidence;
- regulatory oversight/performance-indicator evidence where applicable;
- outage/refueling, maintenance, spares, configuration, event-reporting, and corrective-action records;
- grid-interface or flexibility evidence before flexible-operation, blackstart, islanding, critical-load, or large-load claims are promoted;
- public summary, exception pathway, and red-team challenge route for material operating gaps.

## Maturity cap

If these records are missing, stale, synthetic, or only asserted at template level, the relevant nuclear service floor remains capped at `R2_documented_template_only` even when the policy preference favors nuclear.

## Audit note

This rev0293 file is part of the nuclear operations/refactor pass. It is pro-nuclear, but it makes the operational burden of proof explicit so the cube does not confuse nuclear preference with unverified operating maturity.
