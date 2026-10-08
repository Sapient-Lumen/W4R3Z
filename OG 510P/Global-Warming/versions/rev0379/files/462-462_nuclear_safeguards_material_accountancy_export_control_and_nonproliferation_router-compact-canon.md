---
id: '462'
title: 462 — Nuclear safeguards, material accountancy, export-control, and nonproliferation router
object_type: integrity_gate
domain_tags:
- nuclear_energy
- safeguards
- material_accountancy
- nonproliferation
- export_control
- security
- fuel_cycle
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
service_floor:
- nuclear_fuel_cycle_safeguards
- nuclear_nonproliferation_export_control
- nuclear_material_accountancy
- nuclear_fuel_transport_security
- nuclear_sensitive_information_control
- nuclear_fuel_cycle_exception_path
hazard_tags:
- material_accountancy_gap
- export_control_breach
- safeguards_delay
- sensitive_information_leak
- fuel_transport_security_gap
- dual_use_misclassification
clock_tags:
- material_balance_period
- inspection_cycle
- export_control_review_cycle
- transport_campaign_window
- security_drill_cycle
actor_tags:
- A_regulator
- A_safeguards_authority
- A_transport_security_authority
- A_nuclear_operator
- A_public_auditor
instrument_tags:
- material_accountancy_ledger
- safeguards_interface_plan
- export_control_screen
- sensitive_information_publication_control
- transport_security_plan
- red_team_exception_review
routes_to:
- '430'
- '435'
- '439'
- '441'
- '443'
- '448'
- '459'
- '460'
- '461'
- '463'
- '464'
- '465'
- '466'
- '467'
- '468'
source_ids:
- S832
- S838
- S839
upstream_dependencies:
- nuclear_material_inventory
- safeguards_authority_interface
- export_control_jurisdiction
- transport_security_plan
- publication_control_classification
downstream_consequences:
- fuel_cycle_security_gates_cap_maturity
- public_release_controls_are_tightened_for_sensitive_rows
- export_and_material_accountancy_become_audit_dimensions
equity_lenses:
- public_transparency_without_security_leakage
- host_community_trust
- international_security
- worker_and_corridor_safety
degraded_modes:
- public_transparency_dumps_sensitive_material_routes
- export_control_unchecked
- material_balance_not_auditable
- transport_security_not_exercised
- dual_use_fuel_cycle_claim_not_classified
evidence_grade: mixed
speculation_level: medium
revision_added: rev0295
status: canon
---

# 462 — Nuclear safeguards, material accountancy, export-control, and nonproliferation router

## Nuclear-positive rule

The cube favors nuclear expansion only with safeguards, material accountancy, export-control, and security controls that can coexist with public accountability. The fuel-cycle integrity plane is now separate from ordinary procurement transparency.

## Publication rule

Fuel-cycle transparency must not disclose sensitive material quantities, exact transport routes, security details, or safeguards-sensitive information. The cube now distinguishes public auditability from security-compromising publication.
