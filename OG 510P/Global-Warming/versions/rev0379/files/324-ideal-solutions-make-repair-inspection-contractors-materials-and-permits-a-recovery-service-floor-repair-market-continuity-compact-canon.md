---
id: '324'
revision_added: rev0272
status: canon
object_type: service_continuity
domain_tags:
- recovery
- repair
- inspection
- contractors
- materials
- permits
- maintenance
- building_safety
service_floor:
- repair_market_throughput
- safe_reoccupancy
- inspection_continuity
- materials_and_spares_access
hazard_tags:
- flood
- wildfire
- storm
- heat
- outage
- smoke
- supply_chain
- compound_shock
clock_tags:
- recovery_clock
- stock_turnover_clock
- finance_clock
- learning_clock
actor_tags:
- building_department
- contractor
- inspector
- supplier
- consumer_protection_agency
- insurer
- landlord
- housing_agency
- utility
instrument_tags:
- license
- inspect
- permit
- prequalify
- procure
- standardize
- anti_fraud
- price_watch
- warranty
- repair
routes_to:
- '250'
- '253'
- '258'
- '259'
- '262'
- '287'
- '288'
- '300'
- '315'
- '322'
source_ids:
- S121
- S126
- S579
- S584
upstream_dependencies:
- materials
- spare_parts
- inspectors
- licensed_contractors
- permits
- insurance_or_grants
- consumer_protection
- records
- transport
- utilities
downstream_consequences:
- delayed_return
- unsafe_housing
- homelessness
- school_disruption
- worker_exploitation
- fraud_loss
- mold_disease
- repeat_loss
equity_lenses:
- renters
- low_income_owners
- informal_residents
- older_adults
- disabled_people
- limited_english_speakers
- small_landlords
- mobile_home_residents
degraded_modes:
- emergency_repair_standard
- temporary_safe_occupancy_certificate
- mobile_inspection_team
- standard_bid_sheet
- trusted_contractor_pool
- repair_ombuds
- tenant_repair_bridge
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- licensed_contractor_shortage
- inspection_backlog
- materials_shortage
- permit_delay
- price_gouging
- uninsured_work
- mold_or_smoke_hidden_damage
- warranty_gap
- spare_parts_delay
failure_modes:
- cash_without_contractors
- unsafe_reoccupancy
- repair_fraud
- informal_tenant_exclusion
- mold_left_inside_walls
- permit_queue_blocks_recovery
- materials_capture
- rebuilds_same_risk
proof_ledgers:
- contractor_roster
- license_and_insurance_check
- inspection_queue_log
- permit_cycle_time_log
- materials_price_watch
- repair_quality_audit
- warranty_claim_log
- mold_clearance_record
restoration_conflicts:
- speed_vs_safe_reoccupancy
- simplified_permits_vs_code_integrity
- scarce_contractors_vs_equity
- repair_in_place_vs_relocation
assurance_tests:
- post_disaster_permit_surge_drill
- contractor_fraud_sweep
- inspection_backlog_stress_test
- tenant_repair_path_test
- materials_supplier_failover_test
---

# 324 — Ideal Solutions: Make repair, inspection, contractors, materials, and permits a recovery service floor

## Claim

A household cannot recover from a climate shock because a rebuilding grant exists on paper. Recovery requires a functioning **repair market**: licensed contractors, inspectors, permits, materials, spares, warranties, consumer protection, mold / smoke / contamination standards, utility reconnections, and money that can actually turn into safe work.

The archive already treats recovery as risk reduction, not loss repetition. This file adds a missing throughput layer: **repair capacity is climate infrastructure.** OECD infrastructure-governance work already stresses lifecycle management, operation, maintenance, monitoring, and asset-management duties [S121]. The GCA infrastructure handbook frames resilience across the full infrastructure lifecycle, including construction and operation [S579]. FTC disaster guidance shows the street-level failure mode: unlicensed contractors and scammers often appear in recovery zones and target people needing immediate cleanup or repair [S584].

House rule: **cash without safe repair capacity is not recovery; it is a queue, a fraud market, or a forced displacement pathway.**

## Fast rule

**Every recovery packet must prove a repair route: who can inspect, bid, permit, finance, perform, verify, warranty, and remedy the work under surge conditions.**

## The compact canon

### 1. Count repair as a service floor

Repair is not only a private transaction. After floods, fires, storms, heat failures, contamination, or outages, repair determines whether housing, schools, clinics, small businesses, roads, utilities, and care facilities reopen. If repair fails, recovery cash turns into rent burden, hotel stays, missed school, business closure, mold exposure, and debt.

### 2. Prequalify without creating capture

Governments can maintain prequalified contractor pools, standard scopes, price ranges, surge inspection rosters, reciprocal license recognition, and mobile permitting. But the pool must be transparent, open to qualified local firms, protected from bid-rigging, and paired with worker-safety and wage controls. Speed should not become a franchise for insiders.

### 3. Simplify permits without authorizing unsafe return

Post-disaster permitting should separate emergency stabilization, temporary safe occupancy, full repair, mitigation upgrade, and rebuild-in-risk-zone decisions. The degraded mode is not no code; it is staged code with visible conditions, deadlines, and appeal. Buildings with mold, smoke, structural damage, electrical hazards, or contamination should not be declared recovered by paperwork.

### 4. Treat materials, spares, and inspection as bottlenecks

Repairs fail when transformers, pumps, drywall, filtration, heat pumps, roofing, glass, wiring, lift parts, medical equipment parts, and water-treatment components are scarce. Supplier diversity, safety stocks, substitute specifications, repairability, and reverse logistics belong in the recovery plan [S126].

### 5. Build consumer protection into throughput

A serious repair floor provides written-bid templates, license checks, staged payments, escrow where needed, fraud hotlines, legal help, insurer / grant coordination, warranty records, and price-gouging surveillance. These are not niceties. They are how money becomes safe repair rather than extraction.

## Minimum readiness ledger

| Test | Minimum evidence | Failure signal |
|---|---|---|
| repair capacity | contractor roster, licensing check, surge workforce, worker-safety plan | funds wait because nobody safe can do the work |
| inspection / permits | cycle-time log, mobile teams, staged occupancy categories | homes reopen unsafe or stay closed indefinitely |
| materials and spares | supplier failover, substitute specs, price watch, inventory map | repair queue becomes supply-chain queue |
| fraud / remedy | standard bids, escrow, hotline, legal-help route, warranty ledger | post-disaster market extracts from survivors |

## Bottom line

Repair capacity is the recovery bottleneck that makes many other service floors true or false. The datacube should now ask every recovery claim: who does the work, who checks it, who pays for it, and who fixes the failure?

---
Citations point to `sources/register.md`.
