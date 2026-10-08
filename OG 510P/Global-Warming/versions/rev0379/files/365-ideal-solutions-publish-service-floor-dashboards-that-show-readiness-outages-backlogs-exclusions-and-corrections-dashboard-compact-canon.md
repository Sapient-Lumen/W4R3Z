---
id: '365'
revision_added: rev0277
status: canon
object_type: ledger
domain_tags:
- dashboards
- service_floors
- public_reporting
- disaster_loss_data
- accountability
service_floor:
- public_service_floor_dashboard
- correction_visible_dashboard
hazard_tags:
- all_hazards
- outage
- backlog
- exclusion
- misinformation
- stale_data
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- public_information_officer
- data_steward
- service_owner
- emergency_manager
- public_auditor
- civil_society
instrument_tags:
- publish
- warn
- update
- annotate
- demote
- correct
- audit
routes_to:
- '293'
- '294'
- '301'
- '322'
- '356'
- '364'
- '371'
source_ids:
- S638
- S653
- S654
- S667
upstream_dependencies:
- data_dictionary
- owner_table
- source_freshness
- field_reports
- correction_budget
- public_information_channel
- accessibility_support
downstream_consequences:
- public_trust_loss
- unsafe_behavior
- services_misrouted
- political_capture_of_status
- repeated_unfixed_failure
equity_lenses:
- low_bandwidth_users
- people_without_smartphones
- disability_access
- limited_English_users
- rural_users
- renters
- undocumented_people
degraded_modes:
- paper_status_board
- radio_readout
- call_center_script
- community_anchor_snapshot
evidence_grade: design_judgment
speculation_level: low
bottlenecks:
- dashboard_without_operational_owner
- stale_data_not_labelled
- average_hides_exclusion
- backlog_not_public
- correction_budget_absent
failure_modes:
- dashboard_theatre
- public_confusion_about_status
- green_status_masks_unreachable_service
- unverified_map_reused_as_truth
- correction_never_funded
proof_ledgers:
- dashboard_data_dictionary
- update_cadence_log
- outage_and_backlog_feed
- exclusion_metric_log
- correction_status_register
- public_change_log
restoration_conflicts:
- fast_public_notice_vs_data_quality
- privacy_vs_transparency
- simple_message_vs_uncertainty
- reputation_management_vs_public_truth
assurance_tests:
- stale_dashboard_detection_test
- screen_reader_and_language_test
- offline_printout_test
- excluded_neighborhood_dashboard_audit
data_product_status: dashboard_must_show_status_freshness_uncertainty_owner_backlog_exclusion_and_correction
public_ledger_contestability: dashboard_cells_need_public_change_log_and_challenge_route
---

# 365 — Ideal Solutions: Publish service-floor dashboards that show readiness, outages, backlogs, exclusions, and corrections

## Claim

A dashboard can be a public service, a rumor-control tool, a management console, or a propaganda wall. The difference is whether it shows readiness, outage, backlog, exclusion, uncertainty, owner, and correction status.

NASA Earthdata shows how natural-hazard data can support mapping, response, exposure analysis, and near-real-time disaster information [S654]. Sendai monitoring and resilience scorecards show the value of comparable risk and loss indicators [S638][S653]. Open-government doctrine says public information should support transparency, integrity, accountability, and participation [S667].

House rule: **a dashboard that hides uncertainty, backlog, owner, or correction status should not be treated as public proof.**

## Fast rule

Each service-floor dashboard must answer six public questions: what is working, what is degraded, who is missed, how fresh is the data, who owns the fix, and when will the next correction be visible?

## The compact canon

### 1. Readiness, live status, and recovery status are different

A floor can be planned but not ready, ready but currently down, restored but inaccessible, or open but unsafe. The dashboard should not collapse these states into a single green / yellow / red icon.

### 2. Backlog is a climate indicator

Repair queues, benefits appeals, shelter exits, debris tickets, lab turnaround time, permit queues, contractor complaints, medical refill failures, and unpaid claims are not administrative noise. They are recovery-speed indicators.

### 3. Exclusion should be measured directly

The dashboard should test whether no-car, no-phone, no-ID, no-bank, limited-language, disabled, undocumented, remote, custodial, renter, camp, and informal users can actually complete the service path.

### 4. Uncertainty should be labelled, not hidden

Missing sensors, blocked roads, unverified reports, modelled estimates, privacy suppression, and delayed feeds should have visible status. Unknown should be grey, not green.

### 5. The dashboard must show correction, not only condition

A public status feed without a funded correction path turns the public into spectators. The dashboard should publish responsible owner, correction budget, deadline, and retest date where public disclosure is safe.

## Minimum packet

A service-floor dashboard packet includes: data dictionary; owner; source feeds; update cadence; downtime / backlog / exclusion metrics; quality flags; public-safe field list; manual fallback; accessibility check; correction register; and archive route for each metric.

## Bottom line

The dashboard is not the goal. The goal is faster, fairer correction. Publish status only in a form that helps people act and helps the public see whether government and utilities are fixing the right failures.

## Rev0278 dashboard addition — next action, not just status

Public dashboards should show not only status but next action: threshold reached or not, owner, expected action, time window, uncertainty, accessible channels, grievance route, and last update. A red dashboard cell without a named action owner is not public proof.

---
Citations point to `sources/register.md`.
