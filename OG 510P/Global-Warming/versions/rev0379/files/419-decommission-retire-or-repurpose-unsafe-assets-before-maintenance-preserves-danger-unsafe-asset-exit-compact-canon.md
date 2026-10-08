---
id: '419'
revision_added: rev0283
status: canon
object_type: delivery_packet
domain_tags:
- decommissioning
- unsafe_assets
- stranded_assets
- managed_retreat
- asset_exit
- service_replacement
service_floor:
- unsafe_asset_exit_plan
- service_replacement_before_retirement
- decommissioning_or_repurpose_route
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
- asset_owner
- public_works
- utility
- school_district
- housing_agency
- finance_officer
- regulator
- community_recovery_group
instrument_tags:
- asset_exit_register
- service_replacement_plan
- decommissioning_budget
- repurpose_screen
- stranded_asset_note
- community_transition_agreement
routes_to:
- '334'
- '349'
- '351'
- '360'
- '404'
- '408'
- '410'
- '417'
- '418'
source_ids:
- S268
- S269
- S728
- S740
- S746
- S755
upstream_dependencies:
- asset_portfolio_stress_test
- retreat_or_buyout_rule
- no_new_risk_land_use
- recovery_closeout
- finance_stack
- public_ledger
downstream_consequences:
- service_gap
- economic_dislocation
- residual_pollution
- ratepayer_burden
- political_backlash
equity_lenses:
- rural_service_users
- tribal_governments
- low_income_ratepayers
- workers_at_the_asset
- students
- patients
- elderly_residents
degraded_modes:
- temporary_service_replacement
- repurpose_with_hazard_control
- phased_retirement
- mobile_service
- shared_regional_asset
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- maintenance_budget_keeps_unsafe_asset_alive
- service_replacement_not_funded
- retirement_cost_hidden
- stranded_debt_blocks_exit
- community_loss_not_addressed
failure_modes:
- danger_maintained
- unplanned_service_loss
- fiscal_trap
- environmental_hazard
- community_abandonment
- repeat_loss
proof_ledgers:
- unsafe_asset_register
- exit_decision_log
- service_replacement_map
- decommissioning_budget
- stranded_cost_note
- community_transition_record
unsafe_asset_exit_plan: asset has retirement, repurpose, or decommissioning route with service replacement, budget,
  stranded-cost treatment, and community transition record
---

# 419 — Decommission, retire, or repurpose unsafe assets before maintenance preserves danger

## Core claim

Maintenance is not always resilience. Sometimes maintenance preserves danger: a road that repeatedly washes out, a school that cannot be cooled, a treatment plant in chronic flood, a mobile-home park without safe retrofit path, a public building beyond safe access, or a utility asset whose protection costs exceed service value. The archive needs an asset-exit doctrine so risk reduction can retire, relocate, repurpose, or decommission assets without abandoning people.

Infrastructure asset-management materials require lifecycle decisions, not only repair lists [S746][S755]. Floodplain and substantial-damage rules already show that rebuild gates can force safer repair, elevation, relocation, or mitigation [S728][S740]. Planned-relocation and real-estate repricing materials show the human and financial risk of leaving exit decisions implicit [S268][S269].

## Exit packet

An unsafe-asset exit plan should include:

- asset and protected service;
- reason continued operation is unsafe, uneconomic, or maladaptive;
- service replacement before retirement;
- user and worker transition plan;
- stranded debt or cost treatment;
- environmental remediation;
- cultural or community loss handling;
- interim degraded mode;
- date by which maintenance no longer substitutes for exit.

## No-abandonment rule

Retiring an asset is not the same as retiring a service. The service floor must have a replacement path before the old asset is allowed to fail or be withdrawn.

## Cube rule

The field `unsafe_asset_exit_plan` marks whether retirement, repurposing, decommissioning, and service replacement are governed. Blank means maintenance may be preserving exposure.

---
Citations point to `sources/register.md`.
