---
id: '412'
revision_added: rev0282
status: canon
object_type: audit
domain_tags:
- project_performance
- maintenance
- residual_risk
- adaptive_management
- mitigation_audit
service_floor:
- post_project_performance_monitoring
- maintenance_and_residual_risk_transfer
- adaptive_management_after_completion
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
- asset_owner
- hazard_mitigation_officer
- maintenance_owner
- auditor
- community_monitor
- finance_officer
- inspector
instrument_tags:
- performance_monitoring_plan
- maintenance_escrow
- residual_risk_register
- after_action_update
- adaptive_management_trigger
- public_dashboard
- asset_condition_survey
routes_to:
- '334'
- '356'
- '365'
- '371'
- '404'
- '405'
- '407'
- '411'
source_ids:
- S627
- S728
- S734
- S735
- S738
- S739
- S741
- S744
- S747
- S750
upstream_dependencies:
- mitigation_pipeline
- finance_stack
- maintenance_plan
- telemetry
- community_reporting
- hazard_event_record
downstream_consequences:
- false_success
- repeat_damage
- downstream_harm
- funding_mistrust
- maladaptation
equity_lenses:
- downstream_communities
- low_income_service_users
- renters
- future_residents
- tribal_communities
- people_without_insurance
degraded_modes:
- conditional_project_acceptance
- annual_public_monitoring
- community_observation_channel
- maintenance_reserve_trigger
- residual_risk_notice
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- completion_counts_substitute_for_outcomes
- maintenance_owner_unfunded
- monitoring_data_not_collected
- residual_risk_not_disclosed
- project_failure_politically_embarrassing
failure_modes:
- risk_reduction_claimed_without_measurement
- asset_deteriorates_unnoticed
- project_transfers_risk_downstream
- residual_risk_surprises_households
- lessons_do_not_update_standards
proof_ledgers:
- post_project_monitoring_report
- asset_condition_log
- maintenance_budget
- residual_risk_register
- downstream_effect_log
- public_correction_record
- adaptive_management_action_log
post_project_performance_monitoring: requires measured risk reduction, maintenance budget, residual-risk disclosure,
  downstream-harm check, and adaptive-management trigger after project completion
---

# 412 — Monitor mitigation-project performance, maintenance, and residual risk before project completion is mistaken for risk reduction

## Core claim

Project completion is not risk reduction. A culvert, levee, wetland, drainage upgrade, cool corridor, code update, buyout, microgrid, or wildfire buffer has reduced risk only if it performs under the conditions it was meant to address and if its maintenance, residual risk, and downstream effects are visible.

FEMA's building-code and floodplain-management materials show why standards and administration matter beyond construction [S627][S728]. NIST and ASCE future-hazard work show that design conditions evolve as climate risk changes [S734][S735]. FEMA and World Bank nature-based-solution materials reinforce that monitoring and maintenance are lifecycle duties [S738][S739].

## Performance rule

Every completed mitigation project should carry a post-project ledger:

- design hazard and service protected;
- measured or modeled risk reduction;
- actual performance in events;
- asset condition and maintenance budget;
- residual and transferred risk;
- household and service-floor outcome check;
- public correction and adaptive-management trigger.

## Anti-ribbon-cutting rule

A public ceremony can mark construction completion. It cannot mark resilience completion. Resilience remains conditional until the protected service, excluded users, maintenance owner, and residual-risk notice survive a real or simulated loadcase.

## Cube rule

All mitigation and closeout packets should expose `post_project_performance_monitoring`. Blank means the archive should assume completion could be mistaken for reduced risk.

## Rev0283 routing note — pathway and portfolio tests

Route unresolved long-lived decisions through `413`–`420`: adaptive pathways, model governance, real options, maladaptation gates, asset-portfolio stress tests, service-level contracts, unsafe-asset exits, and professional duty. The key query is no longer only whether a service floor exists; it is whether the floor can change course before physical risk outruns its design [S741][S744][S747][S750].

---
Citations point to `sources/register.md`.
