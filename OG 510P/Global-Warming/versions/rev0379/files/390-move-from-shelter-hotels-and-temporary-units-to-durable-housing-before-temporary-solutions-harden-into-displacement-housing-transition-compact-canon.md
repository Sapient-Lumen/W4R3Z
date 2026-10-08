---
id: '390'
revision_added: rev0280
status: canon
object_type: service_continuity
domain_tags:
- housing_transition
- temporary_housing
- rental_repair
- cdbg_dr
- managed_relocation
- shelter_exit
service_floor:
- safe_interim_housing
- durable_housing_pathway
- housing_exit_without_drop
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
- stock_turnover_clock
- learning_clock
actor_tags:
- housing_lead
- FEMA_or_national_assistance
- local_housing_authority
- HUD_or_housing_ministry
- landlord
- tenant_advocate
- case_manager
- building_department
instrument_tags:
- temporary_shelter
- rental_assistance
- repair_grant
- direct_housing
- cdbg_dr
- buyout
- relocation
- tenant_protection
- inspection
routes_to:
- '287'
- '288'
- '339'
- '348'
- '349'
- '352'
- '354'
- '355'
- '389'
- '396'
source_ids:
- S698
- S700
- S701
upstream_dependencies:
- safe_refuge
- building_safety_placards
- property_proof
- repair_market
- case_management
- public_recovery_finance
downstream_consequences:
- homelessness
- school_instability
- health_decline
- job_loss
- family_separation
- rebuilding_in_risk_zone
equity_lenses:
- renters
- manufactured_housing_residents
- mobile_home_park_residents
- condo_or_HOA_residents
- unhoused_people
- large_families
- disabled_people
- pets_or_service_animals
- undocumented_households
degraded_modes:
- host_family_with_support
- master_leased_units
- hotel_with_case_plan
- mobile_home_repair_team
- paper_tenant_protection_notice
- community_landlord_pool
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- rental_stock_shortage
- repair_permit_queue
- title_gap
- landlord_nonparticipation
- hotel_exit_without_destination
- temporary_unit_siting_delay
- funding_gap_between_relief_and_rebuild
failure_modes:
- hotel_program_expires_into_homelessness
- manufactured_unit_becomes_indefinite_camp
- repair_money_arrives_after_household_leaves
- tenant_excluded_from_owner_facing_program
- return_to_unsafe_or_uninsurable_home
proof_ledgers:
- shelter_to_housing_roster
- interim_housing_duration_log
- repair_permit_and_inspection_queue
- rental_stock_register
- tenant_protection_log
- cdbg_dr_unmet_housing_need_log
- exit_destination_log
interim_to_durable_housing: temporary housing has exit dates, durable destination classes, repair/rental/relocation
  owners, tenant protections, and unresolved-need ledger
---

# 390 — Move from shelter, hotels, and temporary units to durable housing before temporary solutions harden into displacement

## Core claim

Temporary housing is a bridge, not a destination. After climate shocks, shelter, hotels, rental assistance, manufactured units, host-family arrangements, repairs, buyouts, CDBG-DR housing programs, and voluntary-agency help often run on different clocks. If those clocks are not governed together, the household falls between them.

FEMA's housing and individual-assistance policies define several formal assistance routes [S698]. FEMA's pre-disaster housing planning guidance emphasizes that housing decisions before and after disasters shape longer recovery [S700]. HUD's CDBG-DR program is explicitly meant to support long-term recovery and low-income disaster-impacted areas when appropriated [S701]. The cube rule is that these tools must be sequenced, not merely listed.

## The housing transition floor

A serious housing transition floor contains:

- a safe refuge entry point;
- a habitability and placard decision;
- an interim placement with a known review date;
- a durable path class: return, repair, rental, reconstruction, relocation, buyout, institutional transition, or unresolved;
- transport and school stability checks;
- pets, service animals, disability, household size, language, and safety constraints;
- tenant protections and owner / landlord participation rules;
- a funding bridge across FEMA / local aid / insurance / CDBG-DR / philanthropy / private repair;
- an exit ledger that records where people actually went.

## Anti-displacement rule

A programme should not count a household as housed merely because it is no longer in a public shelter. A household exited to a car, unsafe structure, unaffordable rent, exploitative host arrangement, distant motel, or inaccessible unit remains a service-floor failure.

## Rebuild discipline

Durable housing cannot mean rebuilding the same vulnerability. The housing transition file must route to code upgrades, managed retreat where appropriate, flood or wildfire risk, utility reconnection, insurance retreat, property proof, and tenant voice. Fast return and safe return are not the same.

## Cube rule

All shelter, housing, repair, and relocation packets should expose `interim_to_durable_housing`. Blank means the archive should assume the programme can place people temporarily but cannot prove durable housing recovery.

---
Citations point to `sources/register.md`.
