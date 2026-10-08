---
id: '407'
revision_added: rev0282
status: canon
object_type: integrity_gate
domain_tags:
- hazard_mapping
- future_conditions
- risk_disclosure
- design_values
- climate_data
service_floor:
- current_hazard_map_access
- future_condition_design_values
- risk_disclosure_before_commitment
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
- mapping_agency
- planning_department
- building_official
- floodplain_administrator
- real_estate_regulator
- engineer
- public_works
instrument_tags:
- hazard_map
- future_conditions_factor
- risk_disclosure_form
- design_manual_update
- map_change_notice
- data_freshness_rule
routes_to:
- '326'
- '352'
- '358'
- '365'
- '366'
- '371'
- '406'
- '410'
- '412'
source_ids:
- S731
- S732
- S733
- S734
- S735
upstream_dependencies:
- NOAA_precipitation_data
- FEMA_flood_maps
- local_observations
- engineering_standards
- public_disclosure_law
downstream_consequences:
- mispriced_risk
- unsafe_siting
- failed_drainage_design
- buyer_renter_exclusion
- maladapted_assets
equity_lenses:
- renters
- first_time_buyers
- language_minorities
- low_income_homebuyers
- tribal_communities
- small_businesses
degraded_modes:
- interim_future_condition_factor
- public_risk_notice
- engineering_sensitivity_range
- community_map_comment_period
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- stationary_assumptions
- map_update_lag
- disclosure_gaps
- local_capacity_to_interpret_data
- design_standard_lag
failure_modes:
- buyers_and_renters_enter_hidden_risk
- infrastructure_built_to_past_climate
- official_map_treated_as_full_risk
- engineering_values_stale_at_design_lock
proof_ledgers:
- map_freshness_log
- future_condition_assumption
- disclosure_record
- design_value_crosswalk
- exception_register
- public_data_provenance
future_hazard_mapping_disclosure: requires map freshness, future-condition assumptions, disclosure before commitment,
  and design-value crosswalk for long-lived assets
---

# 407 — Govern hazard maps, risk disclosure, and future-condition design values before risk information becomes stale or hidden

## Core claim

Risk information is infrastructure. A map, design value, disclosure form, or dashboard can prevent loss only if it is current, legible, and binding before people buy, rent, permit, borrow, insure, design, or extend infrastructure into danger.

FEMA identifies flood maps as a tool communities use to understand high-risk areas and manage floodplains [S732]. FEMA's flood-risk disclosure guidance shows that disclosure laws and forms can be strengthened so buyers and renters are not surprised after commitment [S731]. NOAA Atlas 15 is designed to provide updated precipitation-frequency estimates and incorporate nonstationary and climate-model information for future trends [S733]. NIST and ASCE materials point in the same direction for future-hazard design standards [S734][S735].

## Future-condition rule

For long-lived assets, past climate cannot be the sole design climate. A packet should state:

- current official hazard source;
- date and known limits of the map or model;
- future-condition factor or sensitivity range;
- design life and consequence of failure;
- disclosure duty before sale, lease, loan, permit, or public investment;
- exception owner and public explanation.

## Disclosure rule

A risk disclosure is not fair if it arrives after commitment, appears only in English, ignores rental housing, omits known past damage, hides map uncertainty, or lacks an affordable remedy path.

## Cube rule

All siting, rebuild, infrastructure, and recovery-finance packets should expose `future_hazard_mapping_disclosure`. Blank means the archive should assume risk information may be stale, hidden, or nonbinding.

---
Citations point to `sources/register.md`.
