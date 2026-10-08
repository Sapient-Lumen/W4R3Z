---
id: '373'
revision_added: rev0278
status: canon
object_type: service_continuity
domain_tags:
- anticipatory_finance
- early_action_protocols
- forecast_based_financing
- disaster_risk_finance
- humanitarian_finance
service_floor:
- prearranged_early_action_finance
- triggered_preimpact_release
hazard_tags:
- flood
- cyclone
- heat
- drought
- wildfire
- cold
- food_shock
- disease
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- finance_ministry
- emergency_manager
- humanitarian_agency
- national_society
- local_government
- social_protection_agency
- auditor
instrument_tags:
- preagree_funding
- trigger_release
- preposition
- cash_transfer
- procure
- audit
- review
routes_to:
- '247'
- '318'
- '319'
- '351'
- '359'
- '372'
- '378'
- '379'
- '380'
source_ids:
- S671
- S672
- S673
- S674
- S675
upstream_dependencies:
- trigger_rule
- risk_analysis
- preapproved_budget
- delivery_system
- procurement_authority
- payment_rail
downstream_consequences:
- late_cash
- asset_sales
- evacuation_barrier
- unfunded_shelter_activation
- preventable_loss
equity_lenses:
- unregistered_household
- no_bank_account
- remote_community
- migrant_worker
- female_headed_household
- disabled_person
degraded_modes:
- cash_plus_manual_delivery
- voucher_or_in_kind_fallback
- community_roster
- field_override
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- money_after_damage
- trigger_not_linked_to_budget
- procurement_delay
- registry_exclusion
- audit_fear_blocks_release
failure_modes:
- finance_waits_for_loss
- false_alarm_punishment
- cash_cannot_reach_excluded_users
- prepared_plan_unfunded
proof_ledgers:
- triggered_release_log
- early_action_protocol
- cash_delivery_log
- procurement_activation_log
- false_alarm_review
restoration_conflicts:
- speed_vs_targeting
- audit_control_vs_fast_release
- forecast_confidence_vs_need
- central_fund_vs_local_knowledge
assurance_tests:
- early_action_activation_drill
- finance_release_clock_test
- excluded_household_cash_test
- procurement_under_trigger_test
anticipatory_finance_rule: prearranged_release_before_impact
forecast_trigger_rule: predefined_threshold_or_governed_judgment
---
# 373 — Ideal Solutions: Pre-arrange anticipatory finance and early action protocols before disaster budgets arrive too late

## Core claim

Disaster finance that arrives only after verified loss is a recovery instrument, not a protection instrument. A climate service floor needs **money that can move before impact** when a credible trigger is met.

Early warning and early action means taking steps to protect people before disaster strikes based on forecasts or warnings, and it must be built with at-risk communities rather than delivered as a remote technical product [S671]. The IFRC-DREF Anticipatory Pillar operationalizes this through forecast-based financing: funding is agreed in advance and released automatically when predefined forecast thresholds or triggers are met; Early Action Protocols specify the actions, readiness activities, and pre-positioning needed for those triggers [S672].

## The finance packet

An anticipatory finance packet should include:

- trigger definition and uncertainty rule;
- eligible early actions;
- advance procurement and logistics authority;
- cash, voucher, in-kind, staff, transport, and shelter modalities;
- eligibility and exclusion tests;
- data-sharing and privacy rules;
- pre-event communications;
- audit and anti-fraud controls;
- false-alarm and no-regrets rule;
- review after activation or non-activation.

A fund that cannot release until the road is washed out, the heat deaths are visible, the crops fail, or the household has sold livestock is too late for anticipatory action.

## What should be pre-financed

The archive should not confine early action to humanitarian relief. Triggered pre-finance can support:

- evacuation transport and accessible shelters;
- clean-air room activation and filtration;
- drinking water, electrolytes, cooling, outreach, and clinical surge before heat peaks;
- livestock feed, veterinary support, seed protection, and irrigation scheduling before drought or flood;
- cash top-ups before evacuation, work stoppage, or commodity price spikes;
- temporary staffing, fuel, repair contractors, and communication teams;
- school, care, custody, and shelter protective measures.

The key is that the action is protective, time-bound, auditable, and community-tested. OCHA and CERF also frame anticipatory action as acting ahead of predicted hazards and financing action before impacts fully unfold [S673][S674]. The PrepareCenter resource hub emphasizes trigger development, early-action design, financing mechanisms, coordination, monitoring, learning, and simulation exercises [S675].

## Integrity guardrails

Anticipatory finance can fail in at least five ways: it can exclude people not in registries, release to the wrong geography, activate too late, require procurement steps that cannot clear before impact, or be punished politically after a false alarm. The rule should be: if the action is genuinely no-regrets or low-regrets, a false alarm is evidence for recalibration, not evidence that pre-impact finance was wrong.

This file routes to `380` for social-protection delivery systems, `379` for pre-positioning, `378` for false-alarm learning, and `351` for audit trails.

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
