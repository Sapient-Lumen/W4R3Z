---
id: '461'
title: 461 — Nuclear spent-fuel backend, transport, storage, and consent router
object_type: router
domain_tags:
- nuclear_energy
- spent_fuel
- radioactive_waste
- dry_cask_storage
- transport
- interim_storage
- repository
- consent_based_siting
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_liability
- financial_assurance
- decommissioning_trust
- incident_compensation
- public_risk_transfer
service_floor:
- nuclear_spent_fuel_pool_to_dry_cask_transition
- nuclear_dry_cask_storage_integrity
- nuclear_interim_storage_pathway
- nuclear_deep_geologic_repository_pathway
- nuclear_spent_fuel_transport_readiness
- nuclear_backend_consent_docket
- nuclear_waste_fund_and_decommissioning_alignment
hazard_tags:
- spent_fuel_storage_delay
- dry_cask_aging_management_gap
- transport_route_contest
- repository_path_uncertain
- backend_consent_failure
- waste_fund_misalignment
clock_tags:
- spent_fuel_cooling_period
- dry_cask_inspection_cycle
- transport_campaign_window
- repository_program_review_cycle
- consent_docket_window
actor_tags:
- A_nuclear_operator
- A_waste_management_authority
- A_transport_security_authority
- A_host_community_reviewer
- A_public_auditor
- A_regulator
instrument_tags:
- spent_fuel_management_plan
- dry_cask_aging_management_plan
- transport_security_plan
- backend_consent_docket
- repository_or_interim_storage_pathway
- waste_fund_alignment_test
routes_to:
- '430'
- '435'
- '439'
- '440'
- '441'
- '442'
- '443'
- '447'
- '448'
- '452'
- '458'
- '459'
- '460'
- '462'
- '463'
- '464'
- '465'
- '466'
- '467'
- '468'
- '479'
- '480'
- '481'
- '482'
- '483'
source_ids:
- S836
- S837
- S838
- S839
- S840
upstream_dependencies:
- spent_fuel_inventory
- storage_and_transport_package_certification
- host_community_docket
- emergency_preparedness_interface
- backend_finance_plan
downstream_consequences:
- backend_realism_caps_nuclear_preference
- spent_fuel_storage_and_transport_become_service_floors
- host_community_consent_and_transport_security_become_queryable
equity_lenses:
- host_community_consent
- tribal_consultation
- transport_corridor_transparency
- intergenerational_stewardship
- ratepayer_and_taxpayer_allocation
degraded_modes:
- spent_fuel_mentioned_only_as_generic_waste
- dry_cask_integrity_not_inspected
- transport_route_no_public_interface
- repository_uncertainty_ignored
- waste_funding_not_aligned_with_project_lifecycle
evidence_grade: mixed
speculation_level: medium
revision_added: rev0295
status: canon
---

# 461 — Nuclear spent-fuel backend, transport, storage, and consent router

## Nuclear-positive rule

The cube remains pro-nuclear, but it now treats the backend as part of the product. Spent-fuel storage, dry-cask aging management, transport readiness, interim/repository pathway, consent docket, emergency interface, and waste/decommissioning finance must be explicit.

## Guardrail

Backend uncertainty is not an argument to abandon nuclear by default, but it is a maturity cap. Projects that externalize spent-fuel, transport, consent, or funding questions remain at template maturity until backend evidence is current and challengeable.
