---
id: '499'
title: Nuclear physical protection, design-basis threat, and force-on-force router
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
- nuclear_physical_protection_program
- nuclear_design_basis_threat_alignment
- nuclear_armed_response_readiness
- nuclear_force_on_force_testing
- nuclear_security_performance_evaluation
- nuclear_security_contingency_plan
hazard_tags: &id001
- radiological_sabotage
- theft_or_diversion
- external_assault
- insider_threat
- security_drill_failure
- sensitive_information_disclosure
clock_tags:
- physical_security_plan_review_cycle
- design_basis_threat_review_cycle
- force_on_force_cycle
- security_corrective_action_cycle
actor_tags:
- A_nuclear_operator
- A_nuclear_regulator
- A_physical_security_manager
- A_security_force
- A_law_enforcement_partner
instrument_tags: &id002
- physical_security_plan
- design_basis_threat_crosswalk
- force_on_force_exercise_record
- armed_response_performance_evaluation
- security_corrective_action_program
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
- '500'
- '501'
- '502'
- '503'
source_ids:
- S925
- S926
- S927
- S928
- S929
- S930
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

# 499 — Nuclear physical protection, design-basis threat, and force-on-force router

## Function

This router makes the cube's pro-nuclear preference conditional on a physical protection programme that is visibly tied to the design-basis threat, armed response readiness, contingency planning, and independent or regulator-observed performance testing.

## Nuclear-positive rule

Prefer nuclear where physical security can credibly protect core, spent-fuel, vital-area, material-access and response functions without hiding the public assurance basis. Do not credit nuclear maturity where security posture is asserted but not exercised, independently reviewed, or bounded by a redacted public scorecard.

## Control-plane effect

Rev0303 turns physical security into a binding maturity cap. It separates public challengeable evidence from protected safeguards information: the public can see that gates exist and whether they are closed, but not site layouts, tactics, response timings, weapons posture, adversary assumptions, or vulnerabilities.

## Evidence burden

Minimum evidence includes a current physical security plan, design-basis-threat crosswalk, protected/vital-area controls, security organization depth, force-on-force or equivalent performance evaluations, contingency drills, corrective-action closure, and security-safe publication review. Sources: [S925]; [S926]; [S927]; [S928]; [S929]; [S930]; [S938].
