---
id: '368'
revision_added: rev0277
status: canon
object_type: service_continuity
domain_tags:
- operational_technology
- SCADA
- industrial_control_systems
- cybersecurity
- utilities
- cyber_physical_safety
service_floor:
- cyber_physical_control_safety
- manual_fallback_for_critical_controls
hazard_tags:
- cyberattack
- outage
- flood
- heat
- storm
- supply_chain_disruption
- operator_error
clock_tags:
- emergency_clock
- stock_turnover_clock
- recovery_clock
- learning_clock
actor_tags:
- utility_operator
- OT_engineer
- cybersecurity_team
- vendor
- regulator
- emergency_manager
- procurement_officer
instrument_tags:
- inventory
- segment
- monitor
- secure_remote_access
- procure_securely
- drill
- isolate
- recover
routes_to:
- '17'
- '252'
- '297'
- '298'
- '317'
- '322'
- '333'
source_ids:
- S301
- S302
- S656
- S657
- S658
upstream_dependencies:
- asset_inventory
- network_segmentation
- identity_and_access_management
- backup_power
- vendor_support
- operator_training
- secure_procurement
downstream_consequences:
- water_treatment_failure
- grid_outage
- hospital_disruption
- transport_shutdown
- payment_failure
- public_confidence_loss
equity_lenses:
- small_utilities
- rural_systems
- underfunded_municipalities
- hospital_patients
- water_customers
- critical_load_users
degraded_modes:
- manual_operation
- isolated_local_control
- safe_shutdown
- paper_dispatch
- preapproved_vendor_response
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- unknown_OT_assets
- legacy_systems
- vendor_lock_in
- insecure_remote_access
- no_manual_fallback
- IT_OT_silo
- patching_without_safety_window
failure_modes:
- digital_failure_becomes_physical_service_failure
- ransomware_blocks_utility_operations
- exposed_controller_used_for_disruption
- remote_vendor_access_uncontrolled
- cyber_drill_ignores_manual_operations
proof_ledgers:
- OT_asset_inventory
- network_segmentation_map
- remote_access_log
- backup_and_restore_test
- manual_control_drill
- vendor_security_requirement_log
restoration_conflicts:
- availability_vs_security
- patching_vs_operational_safety
- secrecy_vs_public_assurance
- vendor_speed_vs_secure_design
assurance_tests:
- OT_asset_inventory_pull
- manual_fallback_drill
- remote_access_shutdown_test
- ransomware_service_floor_loadcase
- vendor_security_review
ot_cyber_safety: OT_readiness_requires_asset_inventory_segmentation_secure_remote_access_manual_fallback_vendor_controls_and_drills
---

# 368 — Ideal Solutions: Secure operational technology, SCADA, and cyber-physical controls before digital failure becomes service failure

## Claim

Digital continuity is not enough. Power, water, wastewater, pipelines, ports, hospitals, traffic systems, building controls, industrial plants, and emergency facilities depend on operational technology that controls physical processes. OT failure can become water failure, energy failure, transport failure, or toxic release.

NIST's Cybersecurity Framework 2.0 organizes cyber risk around governance, identification, protection, detection, response, and recovery [S301]. CISA's cross-sector cybersecurity goals provide baseline protections for critical infrastructure [S302]. CISA's OT materials emphasize industrial control systems, OT-specific constraints, and the need for secure-by-design and secure-by-demand choices when OT owners procure products [S656][S657][S658].

House rule: **no service floor is cyber-ready unless the physical controls that operate it can fail safely, be isolated, and be operated in degraded mode.**

## Fast rule

Every critical service floor should identify its OT dependencies, asset owner, remote-access path, manual fallback, backup and restore evidence, vendor support path, and safety-constrained patching rule.

## The compact canon

### 1. OT is not ordinary IT

The main goal is safe, reliable physical operation. A perfect IT policy can still fail if the pump station, substation, traffic signal, lab freezer, wastewater plant, or building-management system cannot be isolated, monitored, or manually operated.

### 2. Asset inventory is the first control

You cannot protect unknown controllers, firmware, remote links, vendor accounts, sensors, or HMIs. The cube should treat OT asset inventory as a proof ledger for water, power, transport, health, waste, labs, shelters, and critical buildings.

### 3. Remote access is a climate dependency

Remote operations and vendor support matter when roads close, smoke keeps staff indoors, or specialists are scarce. But unmanaged remote access is also an attack surface. Secure remote access, logging, emergency disablement, and backup operators are part of resilience.

### 4. Manual fallback must be drilled

Manual operation, local islanding, safe shutdown, paper dispatch, and pre-approved substitutions should be tested before a cyber event, not improvised while ransomware, outage, flood, or heat stress is live.

### 5. Procurement sets the future attack surface

Critical OT products should be bought with secure-by-demand requirements: logging, identity, patchability, vulnerability disclosure, hardening guidance, support life, secure defaults, and data portability.

## Minimum packet

An OT continuity packet includes: OT asset inventory; owner; safety-critical process list; segmentation map; remote access log; vendor register; backup and restore test; manual fallback drill; safe shutdown procedure; patching window rule; incident contact; and public assurance statement.

## Bottom line

The archive should stop treating cyber as only a data risk. For climate service floors, cyber can be a physical hazard amplifier.

---
Citations point to `sources/register.md`.
