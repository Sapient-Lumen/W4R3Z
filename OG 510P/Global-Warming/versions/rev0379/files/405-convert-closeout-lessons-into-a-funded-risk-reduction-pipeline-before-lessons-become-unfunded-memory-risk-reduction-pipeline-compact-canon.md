---
id: '405'
revision_added: rev0282
status: canon
object_type: router
domain_tags:
- risk_reduction_pipeline
- hazard_mitigation
- capital_planning
- lessons_applied
- project_delivery
service_floor:
- lessons_to_mitigation_pipeline
- funded_risk_reduction_queue
- post_closeout_project_route
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
- hazard_mitigation_officer
- capital_budget_officer
- public_works
- grant_manager
- community_recovery_group
- elected_body
- finance_officer
instrument_tags:
- hazard_mitigation_plan
- capital_improvement_plan
- grant_pipeline
- project_scoping
- risk_register
- budget_crosswalk
- owner_assignment
routes_to:
- '404'
- '356'
- '357'
- '371'
- '406'
- '408'
- '409'
- '412'
source_ids:
- S622
- S623
- S726
- S727
- S736
- S737
- S741
- S744
- S747
- S750
upstream_dependencies:
- functional_recovery_outcomes
- closeout_report
- hazard_mitigation_plan
- benefit_cost_support
- capital_budget_process
- community_participation
downstream_consequences:
- repeat_loss
- unfunded_exposure
- political_fatigue
- insurance_retreat
- household_balance_sheet_loss
equity_lenses:
- low_capacity_local_governments
- tribal_governments
- renters
- informal_settlements
- rural_communities
- historically_disinvested_neighborhoods
degraded_modes:
- scoped_project_waitlist
- pre_application_assistance
- pooled_grant_writer
- conditional_closeout_with_owner
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- lessons_not_budgeted
- grant_capacity_shortage
- engineering_scoping_backlog
- match_unavailable
- community_priority_not_reflected
failure_modes:
- after_action_report_shelves_the_problem
- closeout_claims_success_without_risk_reduction
- projects_chase_grants_not_risk
- mitigation_pipeline_excludes_low_capacity_places
proof_ledgers:
- lessons_to_project_crosswalk
- mitigation_pipeline
- scoping_status_log
- funding_stack_table
- unfunded_risk_register
- community_priority_record
mitigation_pipeline_state: closeout findings must route to scoped, owned, scored, financeable mitigation projects
  with unfunded-risk disclosure
---

# 405 — Convert closeout lessons into a funded risk-reduction pipeline before lessons become unfunded memory

## Core claim

Recovery closeout is not the end of climate adaptation. It is the handoff into a risk-reduction pipeline. If the same road floods, the same culvert fails, the same neighborhood loses power, the same renters are displaced, or the same facility is overwhelmed, the after-action system has not learned; it has archived its failure.

FEMA Hazard Mitigation Assistance and HMGP materials frame mitigation as long-term action to reduce future losses [S622][S623]. FEMA's benefit-cost tools and local mitigation planning materials make clear that projects need a planning, cost-effectiveness, and eligibility path, not only a moral claim [S726][S727]. OECD and infrastructure-resilience guidance add the investment point: adaptation must become a financeable project pipeline, not an unfunded aspiration [S736][S737].

## Pipeline rule

Every closeout packet should produce a mitigation-pipeline row:

- hazard and failure being prevented;
- affected service floors and households;
- owner of record;
- project scope or policy action;
- evidence freshness and design standard;
- benefit-cost / equity test;
- funding stack and match source;
- permit / land / procurement dependencies;
- maintenance owner;
- residual risk if unfunded.

## Anti-grant-chasing rule

A mature pipeline is risk-led, not NOFO-led. Grant notices may fund the work, but they should not decide which community risks count. Low-capacity communities need scoping, engineering, match, legal, and procurement support before competitive programs amplify inequality.

## Cube rule

All recovery-closeout rows should expose `mitigation_pipeline_state`. Blank means the archive should assume lessons may have been recorded without being converted into scoped, owned, fundable risk reduction.

## Rev0283 routing note — pathway and portfolio tests

Route unresolved long-lived decisions through `413`–`420`: adaptive pathways, model governance, real options, maladaptation gates, asset-portfolio stress tests, service-level contracts, unsafe-asset exits, and professional duty. The key query is no longer only whether a service floor exists; it is whether the floor can change course before physical risk outruns its design [S741][S744][S747][S750].

---
Citations point to `sources/register.md`.
