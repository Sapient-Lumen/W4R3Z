---
id: '495'
title: Nuclear digital instrumentation/control modernization and software supply-chain
  router
object_type: router
domain_tags:
- nuclear_energy
- digital_instrumentation_control
- software_supply_chain
- sbom
- vulnerability_management
- configuration_baseline
service_floor:
- nuclear_digital_ic_modernization
- nuclear_software_supply_chain_sbom
- nuclear_vulnerability_patch_governance
- nuclear_secure_configuration_baseline
- nuclear_ot_backup_restore
- nuclear_plant_lifecycle_cyber_design
hazard_tags: &id001
- obsolete_analog_or_digital_components
- software_supply_chain_compromise
- unverified_patch
- configuration_drift
- backup_restore_failure
clock_tags:
- digital_ic_license_preapplication
- software_bill_of_material_refresh
- patch_risk_acceptance_cycle
- configuration_control_board
actor_tags:
- A_digital_ic_engineer
- A_nuclear_regulator
- A_supplier_quality_manager
- A_cybersecurity_officer
- A_ot_security_engineer
instrument_tags: &id002
- digital_ic_modernization_case
- software_bill_of_material
- vulnerability_patch_governance
- secure_configuration_baseline
- backup_restore_test
routes_to:
- '00'
- '01'
- '02'
- '03'
- '17'
- '226'
- '429'
- '431'
- '449'
- '450'
- '453'
- '494'
- '496'
- '497'
- '498'
source_ids:
- S915
- S918
- S919
- S920
- S921
- S923
upstream_dependencies:
- nuclear_policy_preference
- cyber_security_program
- digital_ic_assurance
- public_assurance_evidence
downstream_consequences:
- digital I&C and software supply chain_caps_nuclear_maturity
- pro_nuclear_preference_becomes_cyber_digital_assured
- security_safe_publication_path_required
equity_lenses:
- host_communities
- critical_service_users
- workers
- future_generations
- public_auditors
degraded_modes: *id001
evidence_grade: control_plane_template_with_official_guidance_sources
speculation_level: low_for_gate_design_high_for_project_specific_readiness_until_localized
revision_added: rev0302
status: canon
bottlenecks:
- cyber_workforce_depth
- legacy_digital_systems
- vendor_lockin
- classified_or_security_sensitive_evidence
- regulator_review_capacity
failure_modes: *id001
proof_ledgers: *id002
assurance_tests:
- frontmatter_index_source_route_sync
- nuclear_cyber_gate_evaluation
- security_safe_publication_review
- sqlite_query_view_execution
priority_class: nuclear_maturity_cap
security_publication_posture: public_framework_sensitive_local_details_redacted
nuclear_policy_orientation: favored_with_cyber_digital_ai_ot_security_gates
---

# 495 — Nuclear digital instrumentation/control modernization and software supply-chain router

## Function

This router connects nuclear modernization with software assurance. Digital instrumentation and control upgrades can improve reliability and address obsolescence, but only if licensing, configuration management, secure development, SBOM, vulnerability handling, patch risk acceptance, backup/restore, and supplier quality are auditable.

## Nuclear-positive rule

Favor digital modernization that preserves or improves safety and operational reliability. Do not treat digital upgrades as automatic readiness improvements if software provenance, configuration baselines, vulnerability exceptions, supplier access, or recovery tests are missing.

## Refactor output

Rev0302 adds digital I&C modernization tables, software supply-chain/SBOM ledgers, vulnerability and patch governance, configuration baselines, and lifecycle cyber-design records. These tables bind cyber maturity to actual modernization evidence rather than vendor assurances alone.

## Evidence burden

Minimum evidence includes licensing/pre-application records where needed, software provenance, SBOM or equivalent inventory, secure-development practices, vulnerability triage and patch records, configuration-control board evidence, and tested backup/restore. Sources: [S915]; [S918]; [S919]; [S920]; [S921]; [S923].
