---
id: '416'
revision_added: rev0283
status: canon
object_type: integrity_gate
domain_tags:
- maladaptation
- lock_in
- equity
- project_selection
- risk_transfer
service_floor:
- maladaptation_lockin_gate
- risk_transfer_red_team
- no_false_resilience_claim
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
- hazard_mitigation_officer
- civil_rights_officer
- community_recovery_group
- engineer
- planner
- grant_manager
- auditor
instrument_tags:
- maladaptation_screen
- lock_in_review
- risk_transfer_note
- distributional_harm_test
- public_exception_record
- red_team
routes_to:
- '108'
- '110'
- '371'
- '407'
- '409'
- '410'
- '411'
- '413'
- '414'
- '415'
source_ids:
- S110
- S737
- S738
- S741
- S745
upstream_dependencies:
- model_governance
- adaptive_pathway
- future_hazard_mapping
- community_participation
- benefit_cost_equity_test
- no_new_risk_land_use
downstream_consequences:
- amplified_vulnerability
- blocked_exit
- repeat_loss
- community_opposition
- litigation
- funding_mistrust
equity_lenses:
- downstream_communities
- renters
- uninsured_households
- tribal_governments
- low_income_neighborhoods
- future_residents
degraded_modes:
- conditional_approval_with_trigger
- smaller_reversible_stage
- risk_transfer_compensation
- retreat_option_preserved
- project_redesign
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- project_success_metric_too_narrow
- risk_shifted_downstream
- protection_induces_new_exposure
- green_project_displaces_residents
- hardening_delays_needed_retreat
failure_modes:
- future_exposure
- inequitable_protection
- downstream_damage
- unfunded_maintenance
- false_security
- legal_contestation
proof_ledgers:
- maladaptation_screen
- lock_in_log
- risk_transfer_map
- equity_harm_note
- public_red_team_response
- exception_register
maladaptation_lockin_gate: project has red-team test for risk transfer, induced exposure, inequity, maintenance
  failure, and foreclosed retreat
---

# 416 — Red-team maladaptation and lock-in before resilience projects increase future risk

## Core claim

Some resilience projects reduce one visible risk while increasing another. A levee can invite more construction behind it. Air conditioning can save lives while stressing the grid and household budgets. Green infrastructure can raise rents. Road protection can preserve a settlement pattern that should be changed. A seawall can worsen erosion elsewhere. These are not edge cases; they are the reason every resilience claim needs a maladaptation gate.

IPCC identifies maladaptation as a real risk that can lock in vulnerability, exposure, and harms [S110]. Adaptive pathways make path dependency visible [S741]. Adaptation-investment and resilient-infrastructure materials both warn that finance and project delivery must be tied to outcomes, not only activity [S737][S745]. Nature-based-solution guidance supports benefits only when performance, monitoring, and maintenance are real [S738].

## Red-team questions

Before approval, ask:

- What risk is reduced, and for whom?
- What risk is transferred, and to whom?
- Does the project induce new exposure?
- Does it make later retreat, redesign, or service relocation harder?
- Does it depend on maintenance that is unfunded?
- Does it raise housing, tax, insurance, or utility cost burdens?
- Does the benefit-cost file ignore service users, renters, informal occupants, or downstream communities?

## Burden-of-proof rule

The proponent of a resilience project carries the burden of proving it does not create material future exposure or inequitable risk transfer. If the answer is uncertain, the approval should be conditional, staged, or paired with monitoring and compensation.

## Cube rule

The field `maladaptation_lockin_gate` should be filled for mitigation, adaptation, land-use, infrastructure, housing, energy, water, transport, coastal, and NBS packets. Blank means resilience may be a claim rather than a tested outcome.

---
Citations point to `sources/register.md`.
