---
id: '350'
revision_added: rev0275
status: canon
object_type: integrity_gate
domain_tags:
- procurement
- contracting
- emergency_waivers
- anti_corruption
- beneficial_ownership
- conflict_of_interest
- audit
service_floor:
- procurement_integrity
- contracting_speed_with_control
- recovery_value_for_money
- anti_capture
hazard_tags:
- flood
- wildfire
- storm
- heat
- pandemic
- supply_chain
- cyber
- corruption
clock_tags:
- emergency_clock
- recovery_clock
- stock_turnover_clock
- learning_clock
actor_tags:
- local_government
- procurement_officer
- finance_officer
- contractor
- auditor
- FEMA_recipient
- HUD_grantee
- inspector_general
- community_observer
instrument_tags:
- compete
- waive
- document
- disclose
- monitor
- audit
- prequalify
- debar
- complain
- publish
routes_to:
- '132'
- '133'
- '244'
- '247'
- '253'
- '315'
- '324'
- '330'
- '343'
- '351'
- '352'
- '355'
source_ids:
- S620
- S624
- S626
upstream_dependencies:
- pre_event_contracts
- legal_authority
- vendor_pool
- finance_staff
- procurement_policy
- market_price_data
- contract_monitoring
- public_records
- audit_capacity
downstream_consequences:
- fraud
- grant_disallowance
- unsafe_work
- delayed_recovery
- public_mistrust
- cost_overrun
- capture
- small_vendor_exclusion
equity_lenses:
- small_local_businesses
- minority_owned_businesses
- rural_governments
- tribal_governments
- low_capacity_localities
- households_dependent_on_public_repairs
degraded_modes:
- prequalified_pool
- framework_contract
- public_emergency_waiver_log
- sample_contract_file
- mutual_aid_procurement_support
- independent_monitor
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- emergency_sole_source
- vendor_capture
- weak_cost_reasonableness
- missing_contract_files
- conflict_of_interest
- beneficial_owner_hidden
- change_order_abuse
- monitoring_shortage
- grant_disallowance
failure_modes:
- fast_contract_becomes_fraud
- audit_clawback_delays_recovery
- politically_connected_vendor_captures_work
- inferior_repair_installed
- community_loses_trust
- small_local_firms_excluded
- emergency_waiver_never_ends
proof_ledgers:
- procurement_method_log
- emergency_waiver_justification
- conflict_disclosure_register
- beneficial_ownership_file
- cost_reasonableness_analysis
- contract_monitoring_log
- complaint_and_protest_log
- change_order_register
restoration_conflicts:
- speed_vs_competition
- local_preference_vs_open_competition
- emergency_waiver_vs_auditability
- anti_fraud_vs_small_vendor_access
- public_transparency_vs_security
assurance_tests:
- sole_source_red_team
- contract_file_audit
- conflict_of_interest_spot_check
- small_vendor_access_test
- change_order_anomaly_review
procurement_integrity_rule: emergency_speed_allowed_only_with_written_trigger_scope_duration_price_check_conflict_disclosure_and_closeout
---

# 350 — Ideal Solutions: Make emergency procurement, contracting, conflict of interest, and beneficial ownership a climate-integrity gate

## Claim

Recovery is a contracting event. Debris, shelters, inspections, repairs, generators, pumps, communications, case management, modular housing, trailers, roads, bridges, labs, legal help, and monitoring all move through procurement. If procurement is weak, climate recovery becomes a capture machine.

FEMA's procurement-under-grants resources emphasize that recipients and subrecipients purchasing under FEMA awards must follow federal procurement rules in 2 CFR Part 200 [S624]. HUD CDBG-DR and GFOA materials also show that recovery program design, documentation, audits, and cost records must be built into the grant lifecycle [S620][S626].

House rule: **emergency procurement may move fast, but it may not become undocumented procurement.**

## Fast rule

Every emergency contract needs a trigger, scope, price-reasonableness basis, conflict-of-interest check, procurement method, monitoring owner, change-order log, complaint path, and sunset or rebid date.

## The compact canon

### 1. Emergency waivers need expiration dates

A sole-source contract may be justified during immediate life-safety response. It is not automatically justified for months of permanent work. The ledger should show when the emergency began, why competition was impracticable, what work was covered, when the waiver expires, and when a competitive process resumes.

### 2. Prequalified does not mean captured

Pre-event vendor pools, framework contracts, mutual-aid procurement support, small-business rosters, and cooperative purchasing can increase speed. They also need periodic competition, conflict disclosure, performance review, pricing benchmarks, beneficial-ownership visibility, and complaint routes.

### 3. Contract files are recovery infrastructure

A missing contract file can become a funding clawback, delayed reimbursement, or disallowed cost. The cube should treat procurement records as proof rails: solicitation, bids, evaluation, award, cost analysis, insurance, bonding, monitoring notes, invoices, deliverables, photographs, acceptance, and change orders.

### 4. Anti-corruption must not exclude small local firms

Integrity systems can accidentally favor large firms with compliance departments. Serious recovery procurement should include technical assistance, simplified small contracts where lawful, prompt payment, bonding support, language access, local vendor outreach, and fair protest procedures.

### 5. Publish enough to preserve trust

Public dashboards should show contract purpose, vendor, amount, procurement method, emergency justification, delivery status, change orders, complaints, and completion where disclosure is lawful and safe. Silence breeds rumor and capture.

## Minimum packet

A procurement-integrity packet includes pre-event policies; emergency clause; price benchmarks; vendor pool; conflict and beneficial-ownership register; procurement-method log; contract-file checklist; monitoring plan; change-order register; complaint / protest path; small-vendor access plan; and post-event audit.

## Bottom line

The climate state cannot buy its way out of shocks unless it can buy honestly. Procurement integrity is not bureaucracy around recovery; it is one of recovery's load-bearing rails.

---
Citations point to `sources/register.md`.
