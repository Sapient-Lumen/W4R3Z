---
id: '413'
revision_added: rev0283
status: canon
object_type: router
domain_tags:
- adaptive_pathways
- sequencing
- deep_uncertainty
- decision_triggers
- portfolio_governance
service_floor:
- adaptive_pathway_state
- sequenced_adaptation_options
- switching_rule_before_lock_in
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
- capital_clock
- standards_clock
- land_use_clock
- learning_clock
- recovery_clock
actor_tags:
- planning_department
- hazard_mitigation_officer
- capital_budget_officer
- community_recovery_group
- utility
- elected_body
instrument_tags:
- adaptation_pathway_map
- signpost
- trigger_threshold
- option_sequence
- path_dependency_review
- public_switching_rule
routes_to:
- '356'
- '357'
- '364'
- '371'
- '405'
- '407'
- '410'
- '414'
- '415'
- '416'
source_ids:
- S110
- S741
- S742
upstream_dependencies:
- hazard_maps
- future_condition_design_values
- readiness_scoring
- finance_stack
- public_ledger_contestability
- community_priorities
downstream_consequences:
- late_switch
- stranded_assets
- maladaptation
- unfunded_retreat
- avoidable_loss
- contested_legitimacy
equity_lenses:
- low_capacity_local_governments
- tribal_governments
- renters
- informal_settlements
- rural_places
- future_residents
degraded_modes:
- low_regret_action_now
- temporary_protection_with_exit_trigger
- monitoring_only_with_escalation_date
- modular_project_stage
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- single_project_plan_substitutes_for_pathway
- trigger_not_owned
- signpost_data_missing
- community_not_informed_about_switch_points
- political_inertia_after_threshold_crossed
failure_modes:
- plan_locks_in_wrong_future
- investment_arrives_too_late
- early_low_regret_action_becomes_excuse_for_delay
- public_trust_fails_when_route_changes
proof_ledgers:
- pathway_map
- signpost_register
- trigger_decision_log
- option_sequence_table
- community_notice_record
- switching_decision_record
adaptive_pathway_state: pathway has signposts, thresholds, switching owners, public decision logs, and no-regret
  first moves
---

# 413 — Govern adaptation as pathways with signposts and switching rules before plans become one-way bets

## Core claim

An adaptation plan is not mature because it names a preferred project. It is mature when it identifies plausible futures, sequences options, names the signals that would make the current option insufficient, assigns authority to switch, and preserves enough choice that later actors are not trapped by today's false certainty.

The archive already uses clocks, triggers, and dashboards. Rev0283 adds the missing pathway discipline: the ability to say, before the shock or trend fully arrives, which actions are low-regret now, which actions are held open, which thresholds force escalation, and which choices would close off safer futures. IPCC's adaptation-limits and maladaptation findings make the rule basic: delay and lock-in can make later adaptation impossible or much more expensive [S110]. Dynamic Adaptive Policy Pathways treat adaptation as a sequence of measures under uncertainty, with signposts and path dependencies made explicit [S741]. Adaptation-pathways guidance similarly emphasizes staged investment, flexibility, and communication of adaptation choices [S742].

## Pathway packet

Every major adaptation or service-floor strategy should carry a pathway packet:

- objective and protected service floor;
- present action, near-term action, deferred option, and exit option;
- signposts monitored;
- trigger thresholds;
- owner of the threshold decision;
- budget or procurement lead time needed before the trigger;
- equity test at every switch point;
- public explanation of what choice is being preserved or foreclosed.

## Anti-one-way rule

The archive should distrust irreversible capital decisions that are justified by a single climate future, a single design event, a single grant window, or a single political cycle. A pathway can still choose a large project, but it must show why cheaper monitoring, modular staging, demand management, relocation, nature-based buffers, or reversible design are not being prematurely discarded.

## Cube rule

The field `adaptive_pathway_state` should be blank only for objects that truly do not require sequencing. For capital, land-use, service-floor, retreat, utility, and protection decisions, blank means the plan may be a one-way bet.

---
Citations point to `sources/register.md`.
