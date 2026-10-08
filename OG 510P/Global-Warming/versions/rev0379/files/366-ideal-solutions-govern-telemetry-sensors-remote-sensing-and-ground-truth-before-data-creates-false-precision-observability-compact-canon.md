---
id: '366'
revision_added: rev0277
status: canon
object_type: integrity_gate
domain_tags:
- telemetry
- sensors
- remote_sensing
- ground_truth
- environmental_monitoring
- community_science
service_floor:
- trusted_climate_observability
- ground_truth_correction_path
hazard_tags:
- flood
- wildfire
- smoke
- heat
- drought
- landslide
- outage
- toxic_release
- sensor_failure
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- data_steward
- meteorological_service
- public_health_agency
- utility
- emergency_manager
- community_monitor
- lab
instrument_tags:
- sense
- sample
- verify
- calibrate
- map
- publish
- correct
- protect_privacy
routes_to:
- '19'
- '263'
- '300'
- '330'
- '365'
- '370'
source_ids:
- S299
- S654
- S666
upstream_dependencies:
- sensor_network
- lab_capacity
- remote_sensing_access
- field_validation
- data_dictionary
- privacy_rule
- community_trust
downstream_consequences:
- wrong_evacuation_boundary
- missed_hotspot
- unsafe_return
- misallocated_repair
- exposure_denial
- legal_dispute_over_data
equity_lenses:
- indoor_exposure
- informal_settlements
- rural_areas
- tribal_lands
- renters
- people_without_reporting_power
degraded_modes:
- manual_sampling
- community_reporting_hotline
- portable_monitor_pool
- uncertainty_overlay
- conservative_safety_default
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- sensor_gap
- false_precision
- model_without_ground_truth
- inaccessible_data
- no_calibration_log
- community_report_ignored
failure_modes:
- map_shows_assets_not_people
- satellite_view_misses_indoor_exposure
- sensor_down_time_treated_as_safe_time
- community_observation_dismissed_without_review
- uncertain_model_used_as enforcement_truth
proof_ledgers:
- sensor_inventory
- calibration_log
- uptime_and_gap_log
- remote_sensing_product_version
- field_validation_log
- community_report_triage_log
restoration_conflicts:
- fast_mapping_vs_verified_mapping
- privacy_vs_granularity
- proprietary_sensor_vs_public_need
- expert_model_vs_local_ground_truth
assurance_tests:
- sensor_blackout_loadcase
- satellite_ground_truth_comparison
- community_report_response_test
- calibration_pull_audit
telemetry_integrity: sensor_remote_sensing_and_community_observations_need_calibration_gap_flags_and_ground_truth_routes
---

# 366 — Ideal Solutions: Govern telemetry, sensors, remote sensing, and ground truth before data creates false precision

## Claim

Climate governance increasingly depends on sensors, satellites, dashboards, models, sampling networks, and automated alerts. These tools are powerful, but they can create false precision when coverage, calibration, interpretation, privacy, and ground-truth loops are weak.

NASA says Earth-observing satellite data can help map natural hazards and support disaster mitigation and response, with near-real-time data for floods, fires, hurricanes, landslides, drought, and heat [S654]. WMO's greenhouse-gas watch source already in the archive shows the wider shift toward measurement-backed climate truth infrastructure [S299]. Open Data for Resilience emphasizes that disaster-risk data should be open, locally owned, co-created, and used for decision-making [S666].

House rule: **a map is not proof unless its blind spots, update time, uncertainty, and ground-truth process are visible.**

## Fast rule

Every sensor or remote-sensing product used for climate service floors needs: inventory, owner, calibration, uptime / gap flag, version, privacy boundary, field-validation rule, and challenge path.

## The compact canon

### 1. No sensor coverage is not no risk

Absence of readings can mean absence of instruments, power, connectivity, maintenance, calibration, or permission. The default status for unmonitored high-risk places should be unknown, not safe.

### 2. Remote sensing needs lived ground truth

Satellites can see burn scars, flood extent, heat surfaces, landslides, and damage patterns. They may not see indoor heat, mold, medication loss, cash failure, coercion, or legal exclusion. Pair remote sensing with field checks and community reports.

### 3. Sampling chains are proof rails

Air, water, soil, mold, wastewater, hazardous waste, and disease surveillance depend on sampling design, chain of custody, laboratory turnaround, public notice, and clearance criteria. A lab result without provenance is weak proof.

### 4. Community observations need triage, not condescension

Hot apartments, overflowing drains, missed debris, foul odors, blocked accessible routes, dead livestock, and illness clusters can be early signals. The system should log, triage, verify, and respond without requiring residents to become unpaid inspectors.

### 5. Data products need conservative fallbacks

When sensors fail, models disagree, or reports are unverified, service floors should default toward safety for exposed people. False precision should not delay evacuation, cooling, filtration, water notice, or toxic-site inspection.

## Minimum packet

An observability packet includes: instrument inventory; coverage map; blind-spot layer; calibration and maintenance log; uptime / outage record; source version; field-validation protocol; privacy limit; community-report intake; and correction route when data and lived reality disagree.

## Bottom line

The archive should treat data as infrastructure. Bad data does not merely misdescribe climate risk; it can route people into heat, smoke, floodwater, contamination, denial, or delay.

---
Citations point to `sources/register.md`.
