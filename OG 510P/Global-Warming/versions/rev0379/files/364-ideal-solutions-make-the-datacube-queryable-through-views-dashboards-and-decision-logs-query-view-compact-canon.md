---
id: '364'
revision_added: rev0277
status: canon
object_type: router
domain_tags:
- datacube
- query_views
- dashboards
- decision_logs
- public_accountability
- disaster_risk_data
service_floor:
- queryable_service_floor_operating_view
- public_decision_trace
hazard_tags:
- all_hazards
- data_staleness
- paper_readiness
- hidden_exclusion
- accountability_failure
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- data_steward
- emergency_manager
- service_owner
- public_auditor
- community_organization
- ombuds
instrument_tags:
- query
- publish
- route
- log_decision
- demote
- correct
- audit
routes_to:
- '301'
- '322'
- '356'
- '357'
- '358'
- '365'
- '371'
- '421'
source_ids:
- S638
- S653
- S666
- S667
- S698
- S699
- S712
- S729
- S733
- S736
- S738
- S741
- S744
- S747
- S750
- S756
- S757
- S758
- S760
upstream_dependencies:
- cube_schema
- source_register
- readiness_scores
- owner_table
- public_ledgers
- open_data_rules
- correction_budget
- user_journey_tests
downstream_consequences:
- unqueryable_canon
- false_operational_confidence
- opaque_restoration_priority
- low_public_trust
- no_route_from_finding_to_fix
equity_lenses:
- nontechnical_users
- community_auditors
- people_without_portal_access
- language_access
- disability_access
- small_jurisdictions
degraded_modes:
- printable_query_cards
- offline_csv_snapshot
- manual_decision_log
- community_anchor_dashboard_printout
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- prose_without_filters
- dashboard_without_route
- score_without_loadcase
- decision_without_log
- excluded_user_not_encoded
failure_modes:
- cube_exists_but_cannot_answer_operational_questions
- dashboard_as_communications_product_only
- query_result_hides_stale_evidence
- readiness_score_without_owner_or_appeal
proof_ledgers:
- query_view_catalog
- decision_log
- route_trace
- stale_result_warning
- public_correction_register
restoration_conflicts:
- simplicity_vs_explainability
- security_vs_public_visibility
- speed_vs_due_process
- dashboard_score_vs_context
assurance_tests:
- messy_prompt_route_test
- stale_source_query_test
- excluded_user_query_test
- decision_log_replay
public_ledger_contestability: each_query_result_should_show_owner_freshness_correction_status_and_appeal_path
query_view: service_floor_questions_must_map_to_filters_columns_routes_ledgers_and_decision_logs
---

# 364 — Ideal Solutions: Make the datacube queryable through views, dashboards, and decision logs

## Claim

A datacube that cannot answer operational questions is only decorated prose. Rev0276 made service floors scoreable and ownable. Rev0277 adds the next requirement: the cube needs explicit **query views** that translate messy human questions into fields, filters, ledgers, owners, and correction paths.

UNDRR scorecards and Sendai monitoring show the value of scored, comparable risk information [S638][S653]. Open data for resilience emphasizes local ownership, collaborative data creation, and use of risk information in disaster-risk management [S666]. Open government doctrine treats transparency, integrity, accountability, and participation as operating principles, not communications extras [S667].

House rule: **if a service-floor claim cannot be queried, routed, replayed, and corrected, it is not yet an operating object.**

## Fast rule

For every recurring question, build a named query view with: purpose, filters, returned columns, source fields, freshness rule, owner, access limits, excluded-user path, and decision log.

## The compact canon

### 1. Views are doctrine

A view says what the archive thinks matters enough to ask repeatedly. The view `which_service_floors_are_R0_or_R1_before_heat_season` is not a UI convenience. It is an admission that unready service floors before a predictable hazard season are a governance failure.

### 2. Query results need routes, not only answers

A useful query returns the next file, owner, proof ledger, correction deadline, and appeal path. The cube should route from “what is broken?” to “who must fix it?” and “how will the correction be proven?”

### 3. Every dashboard cell should be replayable

A green cell should expose the underlying loadcase, source date, drill result, excluded-user test, owner, and correction status. A red cell should expose the trigger, consequence, workaround, and escalation route. A grey cell should be treated as unknown, not safe.

### 4. Query views should include absence

The most important queries often ask for missing things: no owner, no backup owner, no ledger, no freshness date, no excluded-user test, no degraded mode, no public correction budget, no manual fallback, no appeal path.

### 5. The public view and the secure view are different but linked

Some details should not be public in real time: cyber vulnerabilities, exact security layouts, vulnerable-person addresses, facility attack surfaces, or law-enforcement-sensitive routes. But the public should still see whether the floor is owned, tested, corrected, appealable, and subject to independent audit.

## Minimum packet

A query-view packet includes: natural-language question; cube filter; returned columns; allowed users; public-safe columns; freshness warning; owner; decision use; exclusion test; correction route; citation rule; and sample bad result that forces action.

## Bottom line

The cube should stop being only a map of the archive. It should become a machine-readable operating loop: ask, route, decide, log, correct, retest, and demote stale claims.

## Rev0278 query addition — trigger views

The datacube now needs views that ask: which predictable hazards have no trigger, which triggers lack money, which warnings lack accessible channels, which action packets lack false-alarm review, which heat and smoke thresholds are informational only, and which social-protection systems cannot pay before impact. Route to `372`–`380`.

## Rev0279 query addition — find post-impact conversion gaps

The cube should support views that find service floors with no `incident_management_state`, no `rapid_assessment_state`, no `lifeline_stabilization_clock`, no `survivor_intake_access`, or no `emergency_powers_guardrail` where restrictions are used. These views expose the difference between a doctrinal service floor and an operational recovery path.

## Rev0280 addition — stabilization-to-recovery pathways

rev0280 adds the rule that impact-to-intake is not recovery. A person can be registered, sheltered, assessed, or referred and still remain stranded. Climate service floors therefore need stabilization pathways: interim-to-durable housing, displaced-student stability, chronic-care continuity, nutrition-benefit continuity, utility-arrears protection, deadline tolling, and no-wrong-door benefit sequencing [S698][S699][S712].

The cube should now ask not only whether a service exists, but whether a household can move from first contact to a durable outcome without losing school, medicine, food, utilities, legal rights, or case status along the way.

## Rev0281 query addition — household-function views

The cube now needs views that query beyond administrative throughput: closed cases with unresolved needs, credit and debt damage, renter displacement, work-loss gaps, recovery-trip failures, essential-device loss, document/account lockout, and closeout without nonrecurrence. These views should be public in aggregate, privacy-protected at household level, and correctable by affected people.

## Rev0282 query extension

The query layer should now answer: which closeout findings lack mitigation projects; which repeated-loss places lack a risk-exit or no-new-risk decision; which maps and design values are stale; which resilience projects lack finance, equity selection, O&M, or performance monitoring; and which nature-based solutions lack a maintenance owner or measured protection function. Route these views to `405`–`412` [S729][S733][S736][S738].

## Rev0283 routing note — pathway and portfolio tests

Route unresolved long-lived decisions through `413`–`420`: adaptive pathways, model governance, real options, maladaptation gates, asset-portfolio stress tests, service-level contracts, unsafe-asset exits, and professional duty. The key query is no longer only whether a service floor exists; it is whether the floor can change course before physical risk outruns its design [S741][S744][S747][S750].

## Rev0284 addendum — query the normalized cube

Query views should now prefer normalized edge tables when testing tags, routes, sources, and field coverage. The wide index remains useful, but source-edge, tag-edge, route-edge, and field-coverage tables make audits and regressions easier to run [S756][S757][S758][S760].

---
Citations point to `sources/register.md`.
