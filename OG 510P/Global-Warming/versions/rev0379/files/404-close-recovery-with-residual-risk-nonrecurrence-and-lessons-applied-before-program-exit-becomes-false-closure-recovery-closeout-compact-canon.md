---
id: '404'
revision_added: rev0281
status: canon
object_type: audit
domain_tags:
- recovery_closeout
- residual_risk
- nonrecurrence
- after_action
- mitigation
- programme_exit
- lessons_applied
service_floor:
- recovery_closeout_with_nonrecurrence
- residual_risk_transfer
- lessons_to_standards
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- smoke
- storm
- outage
- displacement
- disease
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- legal_clock
- learning_clock
actor_tags:
- recovery_coordinator
- local_government
- hazard_mitigation_officer
- finance_officer
- community_recovery_group
- inspector
- auditor
- elected_body
instrument_tags:
- closeout_audit
- residual_risk_register
- after_action_correction
- mitigation_project_route
- maintenance_budget
- code_update
- public_hearing
- reopen_rule
routes_to:
- '110'
- '334'
- '338'
- '349'
- '356'
- '371'
- '397'
- '399'
source_ids:
- S699
- S714
- S715
- S716
- S727
- S729
- S733
- S736
- S738
upstream_dependencies:
- functional_recovery_outcomes
- damage_assessment
- finance_closeout
- code_enforcement
- maintenance_plan
- community_participation
- public_ledger
downstream_consequences:
- repeat_loss
- maladaptation
- hidden_unmet_needs
- fiscal_cliff
- insurance_retreat
- future_displacement
- legitimacy_loss
equity_lenses:
- low_income_neighborhoods
- renters
- tribal_or_customary_landholders
- rural_communities
- disabled_people
- language_minorities
- small_businesses
- future_residents
degraded_modes:
- conditional_closeout
- public_residual_risk_note
- community_monitoring
- annual_reopen_window
- mitigation_waitlist
- maintenance_escrow
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- funding_ends_before_risk_is_reduced
- lessons_recorded_but_not_applied
- unresolved_needs_written_off
- maintenance_unfunded
- repeat_loss_area_rebuilt_without_new_rule
failure_modes:
- same_failure_repeats
- public_trust_declines
- assets_rebuilt_to_obsolete_standard
- households_reenter_risk
- audit_compliance_replaces_learning
proof_ledgers:
- closeout_report
- residual_risk_register
- unresolved_needs_table
- lessons_applied_log
- mitigation_to_budget_crosswalk
- maintenance_commitment
- public_hearing_record
- reopen_log
recovery_exit_nonrecurrence: program exit requires proof of functional recovery, unresolved needs, residual risk,
  maintenance finance, mitigation routing, public explanation, and lessons applied to standards or budgets
---

# 404 — Close recovery with residual risk, nonrecurrence, and lessons applied before program exit becomes false closure

## Core claim

Recovery closeout is dangerous if it rewards spend-down, paperwork, and ribbon-cutting rather than reduced future harm. A programme may exit while households remain unstable, assets are rebuilt to obsolete standards, maintenance is unfunded, flood or fire exposure remains, and the after-action lessons never become codes, budgets, procurement rules, or triggers.

FEMA's NDRF frames recovery as restoring and revitalizing community systems [S699]. NIST's resilience guide asks communities to set priorities and align built-environment recovery with critical functions [S715]. FEMA's community recovery toolkit supports long-term recovery management [S716], while the lifelines toolkit shows why stabilization and recovery outcomes must be distinguished [S714]. The archive's addition is a nonrecurrence rule: closeout should prove what will not be allowed to fail the same way again.

## Closeout packet

A recovery closeout should publish:

- functional recovery outcomes and unresolved needs;
- residual physical, fiscal, legal, health, and service risks;
- mitigation or retreat routes for repeat-loss areas;
- code, standard, procurement, trigger, or maintenance changes;
- budget commitments for lifecycle costs;
- community review and correction record;
- reopen conditions and owner;
- lessons applied, not merely lessons learned.

## Anti-false-exit rule

A programme can close funding without closing recovery. When closeout occurs before households, services, and risks are stable, the remaining risk must be transferred to a named public owner with budget, deadline, and public ledger.

## Cube rule

All recovery packets should expose `recovery_exit_nonrecurrence`. Blank means the archive should assume the system can declare success without preventing recurrence.

## Rev0282 handoff

Closeout now has a required downstream handoff. If the closeout report finds repeated loss, chronic outage, unsafe rebuild, obsolete design values, hidden residual risk, or maintenance debt, it must route to the risk-reduction pipeline (`405`), repetitive-loss register (`406`), future-condition disclosure and design gate (`407`), finance stack (`408`), selection test (`409`), no-new-risk land-use gate (`410`), NBS lifecycle ledger (`411`), or performance-monitoring audit (`412`) [S727][S729][S733][S736][S738].

---
Citations point to `sources/register.md`.
