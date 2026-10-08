---
id: '399'
revision_added: rev0281
status: canon
object_type: integrity_gate
domain_tags:
- renter_recovery
- tenant_rights
- fair_housing
- anti_displacement
- CDBG_DR
- habitability
service_floor:
- tenancy_stability
- return_rights
- anti_displacement_recovery
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
- housing_lead
- fair_housing_office
- legal_aid
- landlord
- tenant_organization
- CDBG_DR_grantee
- code_official
instrument_tags:
- tenant_notice
- habitability_inspection
- rent_stabilization_condition
- right_to_return
- relocation_assistance
- fair_housing_review
- eviction_hold
- complaint
routes_to:
- '287'
- '288'
- '348'
- '352'
- '354'
- '390'
- '395'
- '396'
source_ids:
- S698
- S700
- S701
- S720
upstream_dependencies:
- housing_assistance
- legal_aid
- property_records
- building_safety
- repair_contractors
- CDBG_DR_action_plan
- benefit_casework
downstream_consequences:
- homelessness
- school_disruption
- work_loss
- neighborhood_displacement
- segregated_relocation
- trust_loss
equity_lenses:
- renters
- public_housing_residents
- voucher_holders
- mobile_home_residents
- roommates
- informal_tenants
- students
- migrant_households
- disabled_tenants
degraded_modes:
- tenant_attestation
- community_roster
- legal_clinic
- paper_notice
- mobile_housing_casework
- temporary_return_or_relocation_path
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- owner_records_dominate_aid
- renters_lack_repair_control
- landlord_raises_rent_after_public_repair
- temporary_displacement_breaks_lease_rights
- fair_housing_review_too_late
failure_modes:
- renter_displaced_while_owner_recovery_is_funded
- public_money_repairs_units_without_affordability_or_return
- eviction_or_rent_spike_counts_as_private_market_not_recovery_failure
proof_ledgers:
- tenant_roster
- right_to_return_log
- relocation_assistance_log
- habitability_and_repair_order
- rent_change_monitor
- fair_housing_review
- eviction_filing_watch
tenancy_stability_protection: public recovery funds, repair permissions, relocation, and temporary housing are conditioned
  on renter notice, habitability, affordability, return rights, fair housing, and appeal paths
---

# 399 — Protect renters, lease rights, return rights, and anti-displacement rails before housing recovery favors owners

## Core claim

Housing recovery often sees owners first because deeds, insurance, repair contracts, and property-damage assessments are easier to count than tenancy. But renters can lose housing even when the building survives: notices fail, leases lapse, rent rises, landlords do not repair, public money repairs units without return rights, or relocation moves households away from schools, jobs, care, and community.

FEMA individual assistance and housing planning materials create temporary and repair pathways [S698][S700]. HUD's CDBG-DR programme can finance long-term recovery in low-income areas [S701]. HUD's fair-housing office reviews CDBG-DR and mitigation for consistency with fair housing and civil-rights obligations [S720]. The archive's addition is a tenancy proof rule: recovery is not equitable unless renters' right to notice, safe return, affordability, relocation support, and appeal is visible in the same ledger as owner repair.

## Renter recovery packet

The packet should include:

- tenant rosters that do not depend only on landlord cooperation;
- disaster notice standards for displaced tenants;
- habitability and repair-order status;
- right-to-return and relocation assistance where public funds touch housing;
- rent-change and eviction-filing watch;
- voucher and public-housing continuity;
- mobile-home and manufactured-housing park rules;
- fair-housing and civil-rights review before siting replacement housing.

## Anti-owner-only rule

A repaired housing unit is not a housing recovery success if the pre-disaster renter cannot afford or legally access the unit afterward without due process, relocation support, or fair-housing review.

## Cube rule

Housing and benefit-sequencing packets should expose `tenancy_stability_protection`. Blank means the archive should assume the recovery path is owner-biased until proven otherwise.

---
Citations point to `sources/register.md`.
