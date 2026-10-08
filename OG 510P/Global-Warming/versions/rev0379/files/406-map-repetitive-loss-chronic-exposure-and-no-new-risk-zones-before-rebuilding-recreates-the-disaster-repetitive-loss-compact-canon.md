---
id: '406'
revision_added: rev0282
status: canon
object_type: ledger
domain_tags:
- repetitive_loss
- chronic_exposure
- flood_risk
- wildfire_risk
- retreat
- risk_hotspot
service_floor:
- repetitive_loss_exposure_register
- chronic_risk_hotspot_map
- no_new_risk_screen
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
- floodplain_administrator
- hazard_mitigation_officer
- planning_department
- insurance_program
- housing_agency
- community_recovery_group
instrument_tags:
- multiple_loss_dataset
- risk_hotspot_map
- buyout_queue
- elevation_queue
- disclosure_notice
- no_rebuild_review
routes_to:
- '349'
- '352'
- '360'
- '397'
- '399'
- '405'
- '410'
- '412'
source_ids:
- S728
- S729
- S730
- S740
upstream_dependencies:
- damage_assessment
- insurance_claim_data
- hazard_maps
- property_records
- community_reporting
- social_vulnerability_data
downstream_consequences:
- repeat_displacement
- insurance_unaffordability
- public_assistance_recurrence
- tax_base_loss
- trust_loss
equity_lenses:
- uninsured_households
- renters
- heirs_property_owners
- manufactured_home_residents
- tribal_and_customary_landholders
- low_income_homeowners
degraded_modes:
- community_reported_hotspot_list
- probable_repeat_loss_watchlist
- temporary_no_new_risk_hold
- risk_exit_counseling
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- loss_history_hidden
- parcel_data_fragmented
- renters_invisible
- informal_occupants_absent_from_records
- political_pressure_to_rebuild_in_place
failure_modes:
- repetitive_loss_becomes_normalized
- public_money_rebuilds_private_risk
- new_residents_enter_known_hazard_without_notice
- mitigation_targets_only_insured_properties
proof_ledgers:
- repetitive_loss_register
- chronic_exposure_map
- risk_exit_offer_log
- uninsured_loss_supplement
- tenant_notice_record
- no_new_risk_exception_log
repetitive_loss_exposure_register: tracks repeated insured and uninsured losses, chronic service failure, risk-exit
  offers, and no-new-risk review before rebuild funding proceeds
---

# 406 — Map repetitive loss, chronic exposure, and no-new-risk zones before rebuilding recreates the disaster

## Core claim

A climate recovery system that does not know where harm repeats will rebuild repetition. Repetitive loss is not only an insurance category. It is a signal that a location, structure, drainage path, access route, utility segment, housing market, or service floor is absorbing climate risk faster than ordinary repair can reduce it.

FEMA's OpenFEMA multiple-loss dataset shows how flood-loss history can be turned into a planning signal [S729]. FEMA floodplain-management and Community Rating System materials support communities going beyond minimum requirements to reduce flood risk [S728][S730]. FEMA's substantial-damage and safer-rebuild materials show why post-disaster repair decisions are key moments for stronger standards, elevation, relocation, or other mitigation [S740].

## Register rule

The repetitive-loss register should include:

- insured losses and known uninsured losses;
- repeated service outage, access loss, heat, smoke, or evacuation failure;
- renter and informal-occupant exposure;
- critical-facility and infrastructure recurrence;
- mitigation offered, accepted, refused, or unaffordable;
- no-new-risk decision for rebuilding, extension, or new occupancy;
- residual risk and owner.

## No-hidden-loss rule

Insurance data is useful but incomplete. A cube row that only sees insured structures will miss renters, informal housing, small businesses, public housing, mobile homes, migrant camps, undocumented households, and public assets repaired without claims.

## Cube rule

All rebuild and closeout packets should expose `repetitive_loss_exposure_register`. Blank means the archive should assume the system can rebuild in known-risk places without naming the recurrence.

---
Citations point to `sources/register.md`.
