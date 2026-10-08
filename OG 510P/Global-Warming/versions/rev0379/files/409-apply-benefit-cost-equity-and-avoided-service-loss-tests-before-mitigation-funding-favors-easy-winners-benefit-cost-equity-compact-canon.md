---
id: '409'
revision_added: rev0282
status: canon
object_type: integrity_gate
domain_tags:
- benefit_cost_analysis
- equity
- avoided_loss
- service_outage
- project_selection
service_floor:
- benefit_cost_equity_test
- avoided_service_loss_valuation
- distributional_project_selection
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- storm
- drought
- sea_level
- smoke
clock_tags:
- recovery_clock
- capital_clock
- standards_clock
- land_use_clock
- learning_clock
actor_tags:
- grant_manager
- hazard_mitigation_officer
- economist
- community_recovery_group
- finance_officer
- civil_rights_officer
instrument_tags:
- benefit_cost_analysis
- distributional_weight
- avoided_outage_metric
- equity_screen
- low_capacity_assistance
- public_selection_record
routes_to:
- '108'
- '356'
- '371'
- '405'
- '408'
- '410'
- '411'
- '412'
source_ids:
- S490
- S726
- S727
- S736
- S737
upstream_dependencies:
- risk_register
- hazard_map
- community_priorities
- service_floor_outage_data
- finance_stack
downstream_consequences:
- maldistribution
- underinvestment_in_poorer_places
- false_cost_effectiveness
- loss_of_trust
equity_lenses:
- low_property_value_places
- renters
- uninsured_households
- rural_places
- tribal_governments
- disabled_people
- language_minorities
degraded_modes:
- BCA_technical_assistance
- small_project_simplified_test
- equity_override_with_public_record
- unquantified_benefits_appendix
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- benefits_hard_to_quantify
- data_gaps_for_uninsured_loss
- small_projects_fail_formal_BCA
- political_pressure_for_visible_assets
- service_outage_costs_missing
failure_modes:
- funds_go_to_high_property_value_areas
- benefits_ignore_renters_and_service_users
- avoided_deaths_or_outages_undercounted
- projects_selected_for_ease_not_need
proof_ledgers:
- BCA_file
- equity_screen
- avoided_service_loss_table
- unquantified_benefits_note
- selection_decision_log
- appeal_or_reconsideration_record
benefit_cost_equity_test: requires quantified and unquantified benefits, service-outage avoided loss, distributional
  screen, low-capacity assistance, and public selection rationale
---

# 409 — Apply benefit-cost, equity, and avoided-service-loss tests before mitigation funding favors easy winners

## Core claim

Benefit-cost analysis is necessary but dangerous when it becomes a narrow property-value machine. Climate mitigation projects should show cost-effectiveness, but the archive should not let formal arithmetic erase avoided deaths, avoided displacement, continuity of care, school stability, utility service, unpaid care, renter losses, cultural loss, or the value of protecting low-wealth places.

FEMA's BCA materials define benefit-cost analysis as comparing future risk-reduction benefits with project cost [S726]. FEMA mitigation planning materials show that mitigation projects need planning and eligibility discipline [S727]. Infrastructure-resilience guidance emphasizes avoided service disruption and resilience benefits across users, not just asset replacement [S490][S736]. OECD adaptation-investment work frames policy and investment conditions as central to mobilizing adaptation finance [S737].

## Selection rule

A mature project-selection packet should include:

- standard BCA where required;
- avoided service outage and household-function loss;
- mortality, morbidity, displacement, education, care, and livelihood effects;
- distributional screen by income, race, disability, tenure, language, rurality, and tribal status;
- unquantified benefits note;
- technical assistance for low-capacity applicants;
- public explanation when a high-need project fails the formal score.

## Anti-easy-winner rule

Funding programs should not confuse easy documentation with high social value. If the most at-risk community cannot afford engineering, match, or grant writing, that is a program-design defect, not proof that the project lacks value.

## Cube rule

All mitigation finance and project rows should expose `benefit_cost_equity_test`. Blank means the archive should assume project selection may favor administratively strong places over high-need places.

---
Citations point to `sources/register.md`.
