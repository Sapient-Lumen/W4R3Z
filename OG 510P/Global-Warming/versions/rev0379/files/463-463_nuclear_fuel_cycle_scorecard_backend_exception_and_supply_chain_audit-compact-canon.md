---
id: '463'
title: 463 — Nuclear fuel-cycle scorecard, backend exception, and supply-chain audit
object_type: audit
domain_tags:
- nuclear_energy
- fuel_cycle
- assurance_scorecard
- backend_exception
- supply_chain_audit
- data_quality
- maturity_caps
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_liability
- financial_assurance
- decommissioning_trust
- incident_compensation
- public_risk_transfer
service_floor:
- nuclear_fuel_cycle_public_value_scorecard
- nuclear_backend_exception_path
- nuclear_fuel_cycle_maturity_audit
- nuclear_supply_chain_red_team_review
- nuclear_backend_consent_scorecard
hazard_tags:
- fuel_cycle_blind_spot
- haleu_overclaim
- backend_greenwash
- security_transparency_conflict
- maturity_overclaim
- supply_chain_single_point_failure
clock_tags:
- revision_cycle
- fuel_cycle_review_cycle
- backend_program_review_cycle
- data_quality_review_cycle
- red_team_review_cycle
actor_tags:
- A_data_steward
- A_public_auditor
- A_red_team_reviewer
- A_fuel_cycle_supplier
- A_waste_management_authority
- A_safeguards_authority
instrument_tags:
- fuel_cycle_scorecard
- backend_exception_ledger
- haleu_readiness_audit
- source_quality_audit
- maturity_cap_execution
- publication_control
routes_to:
- '421'
- '422'
- '423'
- '425'
- '426'
- '428'
- '438'
- '443'
- '448'
- '453'
- '458'
- '459'
- '460'
- '461'
- '462'
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
- S832
- S833
- S834
- S835
- S836
- S837
- S838
- S839
- S840
- S841
- S842
- S843
- S844
- S845
- S850
- S876
- S877
- S878
- S879
- S880
- S881
- S882
- S883
- S884
- S885
- S886
- S887
- S888
upstream_dependencies:
- rev0294_integrated_energy_refactor
- nuclear_gate_engine
- fuel_cycle_service_floors
- source_edge_sync
- sqlite_export
downstream_consequences:
- fuel_cycle_and_backend_blind_spots_become_visible
- nuclear_preference_gets_backend_maturity_caps
- sensitive_publication_controls_are_encoded
equity_lenses:
- public_transparency
- host_community_consent
- transport_corridor_justice
- intergenerational_stewardship
- ratepayer_public_value
degraded_modes:
- fuel_cycle_not_mapped_to_service_floors
- backend_exception_not_logged
- source_quality_not_classified
- sensitive_fuel_cycle_information_overpublished
- sqlite_views_omit_backend_gates
evidence_grade: mixed
speculation_level: medium
revision_added: rev0295
status: canon
---

# 463 — Nuclear fuel-cycle scorecard, backend exception, and supply-chain audit

## Audit purpose

This file verifies that the cube’s pro-nuclear orientation has propagated into fuel-cycle and backend reality. Uranium, conversion, enrichment, HALEU, fabrication, fuel qualification, spent fuel, dry casks, transport, safeguards, export control, consent, and waste finance become service floors, gates, traceability rows, and backlog items.

## Maturity cap

If a nuclear pathway lacks fuel supply, qualification, safeguards, backend, consent, transport, and publication-control evidence, the relevant nuclear service floor remains capped at `R2_documented_template_only` even when the policy preference is favorable.
