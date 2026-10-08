---
id: '503'
title: Nuclear physical security scorecard, sensitive-publication, and maturity-cap audit
object_type: integrity_gate
domain_tags:
- nuclear_energy
- physical_security
- nuclear_security
- design_basis_threat
- insider_threat
- transport_security
- drone_security
- security_safe_publication
service_floor:
- nuclear_security_sensitive_information_control
- nuclear_physical_security_public_scorecard
- nuclear_security_red_team_counterevidence
- nuclear_security_drill_and_exercise
- nuclear_security_event_reporting
- nuclear_security_contingency_plan
hazard_tags: &id001
- security_overclaim
- sensitive_information_disclosure
- red_team_counterevidence_unclosed
- security_drill_gap
- security_event_underreporting
- public_trust_failure
clock_tags:
- public_security_scorecard_cycle
- security_publication_review_cycle
- red_team_review_cycle
- security_event_after_action_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_security_authority
- A_public_auditor
- A_law_enforcement_partner
instrument_tags: &id002
- nuclear_physical_security_scorecard
- security_sensitive_publication_control
- red_team_counterevidence_ledger
- security_event_after_action_report
- maturity_cap_execution
routes_to:
- '00'
- '01'
- '02'
- '03'
- '05'
- '421'
- '422'
- '423'
- '428'
- '429'
- '430'
- '441'
- '493'
- '498'
- '499'
- '500'
- '501'
- '502'
source_ids:
- S925
- S926
- S927
- S928
- S929
- S930
- S931
- S932
- S933
- S934
- S935
- S936
- S937
- S938
upstream_dependencies:
- nuclear_policy_preference
- physical_security_program
- public_assurance_evidence
- security_safe_publication_boundary
downstream_consequences:
- physical_security_caps_nuclear_maturity
- pro_nuclear_preference_becomes_security_assured
- sensitive_information_is_controlled_not_published
equity_lenses:
- host_communities
- workers
- critical_service_users
- future_generations
- public_auditors
degraded_modes: *id001
evidence_grade: control_plane_template_with_official_guidance_sources
speculation_level: low_for_gate_design_high_for_project_specific_readiness_until_localized
revision_added: rev0303
status: canon
bottlenecks:
- classified_or_security_sensitive_evidence
- security_workforce_depth
- regulator_review_capacity
- law_enforcement_coordination
- public_redaction_boundary
failure_modes: *id001
proof_ledgers: *id002
assurance_tests:
- frontmatter_index_source_route_sync
- nuclear_physical_security_gate_evaluation
- security_sensitive_publication_review
- sqlite_query_view_execution
priority_class: nuclear_maturity_cap
security_publication_posture: public_framework_sensitive_local_details_redacted
nuclear_policy_orientation: favored_with_physical_security_insider_drone_transport_gates
---

# 503 — Nuclear physical security scorecard, sensitive-publication, and maturity-cap audit

## Function

This audit file makes the rev0303 physical-security layer queryable. It records what counts as public assurance, what remains controlled safeguards information, and which gates cap maturity if unclosed.

## Nuclear-positive rule

Prefer nuclear only when physical-security evidence is strong enough to be externally challengeable at a safe level of abstraction. Security claims that cannot be independently reviewed, safely summarized, or corrected must cap maturity.

## Control-plane effect

Rev0303 adds the physical-security scorecard, source-authority audit, gap backlog, traceability matrix, maturity-cap execution, and publication-control artifacts.

## Evidence burden

Minimum evidence includes redacted public scorecards, source-authority classification, sensitive-publication review, counterargument closure, security event/corrective-action tracking, and controlled channels for non-public review. Sources: [S925]; [S926]; [S927]; [S928]; [S929]; [S930]; [S931]; [S932]; [S933]; [S934]; [S935]; [S936]; [S937]; [S938].
