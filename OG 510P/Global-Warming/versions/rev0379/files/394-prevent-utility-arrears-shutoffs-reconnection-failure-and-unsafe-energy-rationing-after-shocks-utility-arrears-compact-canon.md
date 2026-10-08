---
id: '394'
revision_added: rev0280
status: canon
object_type: service_continuity
domain_tags:
- utility_affordability
- arrears
- shutoff_protection
- reconnection
- energy_burden
- water_affordability
- customer_assistance
service_floor:
- utility_arrears_protection
- reconnection_without_impossible_debt
- life_safety_energy_and_water_access
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
- cold
- extreme_precipitation
clock_tags:
- emergency_clock
- recovery_clock
- billing_clock
- finance_clock
- learning_clock
actor_tags:
- electric_utility
- gas_utility
- water_utility
- public_utility_commission
- social_service_agency
- LIHEAP_agency
- customer_assistance_program
- consumer_advocate
instrument_tags:
- shutoff_moratorium
- arrears_management
- bill_credit
- lifeline_rate
- reconnection
- LIHEAP
- water_CAP
- medical_baseline
- payment_plan
routes_to:
- '256'
- '277'
- '289'
- '297'
- '298'
- '323'
- '380'
- '389'
- '396'
source_ids:
- S708
- S709
upstream_dependencies:
- billing_data
- payment_rails
- social_service_agency
- regulatory_authority
- utility_customer_records
- public_information
downstream_consequences:
- heat_or_cold_exposure
- water_insecurity
- unsafe_generator_use
- eviction_or_housing_loss
- medical_device_failure
- political_backlash
equity_lenses:
- low_income_households
- renters_with_submetering
- medically_dependent_people
- older_adults
- disabled_people
- large_families
- informal_tenants
- people_displaced_from_billing_address
degraded_modes:
- manual_payment_plan
- paper hardship attestation
- community_assistance_site
- temporary_reconnection
- arrears_hold
- offline_customer_lookup
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- billing_system_unavailable
- arrears_accumulate_during_displacement
- customer_cannot_prove_hardship
- utility_revenue_need_conflicts_with_protection
- water_assistance_underfunded
- medical_baseline_list_stale
failure_modes:
- home_is_repaired_but_power_or_water_not_reconnected
- household_chooses_food_or_medicine_over_bill
- shutoff_during_heat_cold_or_medical_need
- debt_blocks_return
- utility_costs_erode_consent_for_resilience_investment
proof_ledgers:
- shutoff_moratorium_log
- arrears_aging_dashboard
- reconnection_queue
- medical_baseline_or_critical_customer_log
- LIHEAP_or_energy_assistance_referral_log
- water_CAP_usage_log
- complaint_and_appeal_log
utility_arrears_protection: shutoff holds, reconnection, arrears management, LIHEAP/energy aid, water CAPs, critical-customer
  rules, and appeals are tied to disaster case status
---

# 394 — Prevent utility arrears, shutoffs, reconnection failure, and unsafe energy rationing after shocks

## Core claim

A repaired home is not habitable if power, heat, cooling, water, wastewater, or communications are disconnected by arrears. Climate shocks create billing shocks: lost income, spoiled food, relocation costs, high cooling or heating demand, insurance gaps, and delayed aid. If arrears are treated as ordinary debt, recovery can convert into shutoff.

ACF describes LIHEAP as assistance to reduce costs associated with home energy bills, energy crises, weatherization, and minor energy-related home repairs [S708]. EPA's water customer-assistance compendium describes tools such as bill discounts, flexible terms, lifeline rates, temporary assistance, and efficiency support [S709]. The cube's rule is that these affordability tools become disaster-continuity controls when shocks drive unsafe rationing.

## The utility protection packet

A minimum packet includes:

- heat, cold, medical, displacement, and declared-disaster shutoff holds;
- reconnection priority for repaired or return-ready homes;
- arrears aging and debt-forgiveness / payment-plan options;
- LIHEAP, crisis assistance, weatherization, water CAP, and local fund referrals;
- protections for renters, master-metered buildings, submetered units, mobile-home parks, and informal tenants;
- medical-baseline / critical-customer updates;
- appeal, complaint, and anti-retaliation paths;
- ratepayer / utility revenue plan so protection does not silently create another infrastructure failure.

## Anti-habitability rule

Habitability requires service. A building placard, repair permit, or rental unit should not be counted as restored until essential utilities are connected or a safe degraded mode is documented.

## Cube rule

All housing, energy, water, finance, health, and return packets should expose `utility_arrears_protection`. Blank means the archive should assume bills and shutoffs are outside the recovery system, which is a design failure.

---
Citations point to `sources/register.md`.
