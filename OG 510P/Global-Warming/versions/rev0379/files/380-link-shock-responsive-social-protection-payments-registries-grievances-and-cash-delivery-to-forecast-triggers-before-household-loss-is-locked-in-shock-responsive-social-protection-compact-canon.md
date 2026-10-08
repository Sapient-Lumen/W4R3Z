---
id: '380'
revision_added: rev0278
status: canon
object_type: service_continuity
domain_tags:
- adaptive_social_protection
- cash_transfers
- payments
- registries
- grievances
- household_finance
service_floor:
- triggered_household_cash_floor
- shock_responsive_delivery_system
hazard_tags:
- flood
- heat
- drought
- storm
- wildfire
- smoke
- food_price_shock
- displacement
- outage
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- social_protection_agency
- finance_ministry
- payment_provider
- frontline_worker
- community_organization
- humanitarian_agency
- ombuds
instrument_tags:
- top_up
- pay
- include
- appeal
- protect_privacy
- monitor_liquidity
- review
routes_to:
- '274'
- '290'
- '318'
- '325'
- '342'
- '359'
- '363'
- '373'
- '378'
source_ids:
- S684
upstream_dependencies:
- registry
- payment_rail
- cash_out_agents
- frontline_workers
- grievance_system
- privacy_rules
- forecast_trigger
downstream_consequences:
- missed_evacuation
- asset_sale
- debt_trap
- food_insecurity
- medicine_gap
- exclusion
equity_lenses:
- no_ID
- no_address
- unbanked
- migrant_worker
- informal_worker
- domestic_violence_survivor
- disabled_person
- female_headed_household
degraded_modes:
- manual_enrollment
- cash_or_voucher_fallback
- trusted_intermediary
- paper_grievance
- offline_payment
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- registry_incomplete
- payment_outage
- agent_liquidity_shortage
- privacy_fear
- grievance_backlog
failure_modes:
- cash_too_late
- excluded_households
- predatory_fees
- benefit_diversion
- unsafe_cashout
proof_ledgers:
- triggered_cash_log
- coverage_gap_log
- cashout_liquidity_log
- grievance_resolution_log
- privacy_incident_log
restoration_conflicts:
- speed_vs_targeting
- fraud_control_vs_access
- privacy_vs_outreach
- digital_efficiency_vs_cash_access
assurance_tests:
- triggered_cash_drill
- unbanked_cashout_test
- field_inclusion_mystery_shop
- grievance_surging_test
anticipatory_finance_rule: cash_before_loss_when_threshold_reached
shock_responsive_cash: triggered_top_up_with_offline_inclusion_and_grievance
---
# 380 — Ideal Solutions: Link shock-responsive social protection, payments, registries, grievances, and cash delivery to forecast triggers before household loss is locked in

## Core claim

Households often need money before the damage ledger is complete: to evacuate, replace wages, buy medicine, protect assets, move livestock, pay transport, maintain rent, avoid debt, and avoid selling productive goods. Shock-responsive social protection should therefore become part of the forecast-to-action layer.

World Bank material on climate shock-responsive delivery systems describes delivery systems as the core infrastructure that adaptive social protection programs need to identify, reach, and support vulnerable households in normal times and during shocks, including ID systems, registries, payment arrangements, grievance mechanisms, and frontline providers [S684]. The climate-cube version is: those systems must connect to triggers and operate under outage, displacement, informality, and exclusion.

## The anticipatory cash packet

A shock-responsive packet should define:

- eligible trigger and geography;
- beneficiary registry plus community and manual inclusion path;
- top-up amount, timing, and duration;
- payment rail and cash-out liquidity;
- offline and no-ID degraded mode;
- grievance and appeal route;
- data privacy and consent rule;
- gender, disability, child, migrant, and informal-worker checks;
- debt-collection and predatory-fee safeguards;
- after-action review of coverage, timing, and use.

## Why this differs from disaster assistance

Post-disaster assistance often waits for damage proof, application, inspection, and eligibility determination. Anticipatory social protection acts on exposure before loss is locked in. It is not a replacement for repair grants, insurance, unemployment support, or humanitarian assistance; it is the floor that prevents the first spiral: missed evacuation, unsafe work, food insecurity, asset sales, high-cost debt, and loss of medicines.

## The exclusion problem

Registries are powerful but dangerous if treated as complete truth. Informal settlements, migrants, no-address households, tenants, domestic workers, people fleeing violence, people without bank accounts, and people with privacy fears may be absent or misclassified. Therefore the service floor requires a field inclusion route, trusted intermediary route, paper/offline route, and appeal route.

## Payment-rail dependency

This note routes back to `318`: cash access, agent liquidity, merchant acceptance, offline payments, fraud controls, and remittances are not peripheral. A triggered cash top-up that cannot be cashed out before flood, heat, smoke, or displacement is a dashboard entry, not household protection.

## Operating test

The file is operational only if a named owner can answer five questions before the event, not while the event is already unfolding:

1. What signal activates the action?
2. Who is authorized to act without waiting for a new meeting?
3. What money, staff, contracts, routes, and public messages are already pre-cleared?
4. Which households, workers, institutions, or places are likely to be missed by the nominal channel?
5. How will the decision be reviewed if the forecast misses, the hazard shifts, or the action causes harm?

A forecast, warning, model, dashboard, or alert is not a service floor by itself. It becomes a service floor only when it releases an owned action bundle with funding, authority, equity checks, degraded modes, public explanation, and after-action learning.

## Cube rule

Every trigger-facing packet should expose `forecast_trigger_rule`, `impact_based_decision_support`, `anticipatory_finance_rule`, `protective_action_authority`, `alert_interoperability_state`, `false_alarm_learning`, and `prepositioning_state` where relevant. Blank fields mean the cube should demote the readiness score, not assume the prose is sufficient.

---
Citations point to `sources/register.md`.
