---
id: '356'
revision_added: rev0276
status: canon
object_type: scoring_model
domain_tags:
- readiness_scoring
- datacube
- service_floor
- assurance
- maturity_model
- dashboard
- demotion
- nuclear_maturity_caps
service_floor:
- readiness_grade
- owned_floor
- tested_floor
- current_evidence
- degraded_mode_pass
hazard_tags:
- heat
- flood
- wildfire
- storm
- drought
- outage
- cyber_disruption
- displacement
- compound_hazard
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
- finance_clock
actor_tags:
- service_owner
- local_government
- regulator
- auditor
- community_organization
- emergency_manager
- finance_owner
- data_steward
instrument_tags:
- score
- audit
- demote
- publish
- red_team
- after_action
- correct
- retest
routes_to:
- '117'
- '122'
- '301'
- '302'
- '308'
- '322'
- '331'
- '338'
- '421'
- '422'
- '428'
- '438'
source_ids:
- S637
- S638
- S653
- S661
- S698
- S699
- S712
- S726
- S736
- S738
- S741
- S744
- S747
- S750
- S761
- S763
- S768
- S770
upstream_dependencies:
- front_matter
- owner_of_record
- scenario_loadcases
- proof_ledgers
- data_stewards
- community_feedback
- source_freshness
- audit_capacity
downstream_consequences:
- paper_readiness
- false_public_confidence
- misallocated_restoration_priority
- failure_hidden_by_aggregate_score
- uncorrected_after_action_items
equity_lenses:
- excluded_users
- people_without_documents
- disabled_people
- limited_english_speakers
- rural_residents
- informal_workers
- custodial_populations
- unbanked_households
degraded_modes:
- score_unknown_as_not_ready
- conditional_ready_by_loadcase
- manual_ledger_when_dashboard_down
- public_exception_note_when_data_sensitive
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- file_exists_but_floor_unowned
- readiness_claim_not_scenario_relative
- no_excluded_user_test
- no_degraded_mode_test
- stale_source
- dashboard_without_correction_budget
failure_modes:
- canon_note_mistaken_for_operational_readiness
- green_cell_without_drill
- score_hides_dependency_loss
- old_score_not_demoted_after_failure
- average_score_masks_excluded_population
proof_ledgers:
- readiness_scorecard
- loadcase_result_log
- excluded_user_journey_log
- dependency_status_log
- after_action_correction_log
- demotion_and_retest_register
restoration_conflicts:
- simple_score_vs_context
- optimism_vs_demotable_evidence
- public_dashboard_vs_sensitive_security_data
- sector_score_vs_cross_service_cascade
assurance_tests:
- score_random_audit
- loadcase_replay
- excluded_user_mystery_shop
- after_action_retest
- dependency_loss_drill
readiness_scoring: R0_unknown_R1_named_R2_planned_R3_tested_R4_maintained_and_demotable
---
# 356 — Ideal Solutions: Score service-floor readiness with owned, current, and tested grades before canon growth becomes paper maturity

## Claim

The archive now has enough service floors that the next failure is not absence of doctrine; it is **false maturity**. A note, template, register, or dashboard can make a system look ready while the real floor remains unowned, untested, outdated, or unreachable by the people most likely to fail the journey.

FEMA's National Resilience Guidance frames resilience as a whole-community discipline rather than a single agency plan [S637]. UNDRR's Disaster Resilience Scorecard gives local governments a scored assessment structure, including preliminary and detailed scoring tiers, to move resilience from aspiration into reviewable evidence [S638].

House rule: **a service floor is not ready because it has a file. It is ready only for a named hazard, loadcase, geography, population path, and degraded mode.**

## Fast rule

Use a five-grade readiness scale:

- **R0 — unknown:** no current owner, ledger, loadcase, or source check.
- **R1 — named:** the service floor is named, but no operating proof exists.
- **R2 — planned:** owner, threshold, route, and ledger exist, but the path is not tested.
- **R3 — tested:** at least one serious loadcase and excluded-user path passed.
- **R4 — maintained:** tested, funded, updated, demotable, and corrected after failure.

Any stale source, missing owner, untested degraded mode, or failed excluded-user path caps the score at R2 until retested.

## The compact canon

### 1. Score by loadcase, not by sector

A water system can be R4 for ordinary storms and R1 for heat-plus-cyber-plus-chemical-shortage. A shelter can be R3 for opening beds and R0 for clean air, disability access, pets, and safe exit. The score must attach to the scenario, not the agency brand.

### 2. Unknown is not neutral

Unknown readiness is operationally closer to not ready than to ready. If the ledger cannot show owner, threshold, degraded mode, dependency, last drill, source age, and correction status, the cube should mark the row R0 or R1 rather than let silence read as adequacy.

### 3. Excluded-user paths are part of the grade

A floor that works only for a car-owning, English-speaking, banked, documented household with smartphone access is not a general floor. Every score should include at least one excluded-user journey: no car, no documents, no bank, disability, medical dependence, custody, language barrier, remote geography, or informal employment.

### 4. Scores must demote automatically

Readiness decays. Staff leave, vendors fail, radios break, source documents age, mutual-aid neighbors are hit too, and dashboards drift. The grade should demote after missed review dates, failed real events, unfunded corrective actions, unfilled posts, stale sources, or new hazard evidence.

### 5. The score is a router, not a trophy

A good score sends attention somewhere: to the owner, bottleneck, next test, correction budget, source refresh, or public exception note. A score that merely celebrates readiness becomes a new form of theatre.

## Minimum packet

A readiness-scoring packet includes: service floor; owner of record; geography; hazard / loadcase; upstream dependencies; degraded mode; excluded-user path; minimum ledgers; last test; last source refresh; current grade; grade cap; correction owner; next retest date; and public note explaining any sensitive redactions.

## Bottom line

The cube should make maturity hard to fake. In rev0276, a canon packet should be treated as **unscored doctrine** until it is owned, current, tested, demotable, and corrected.

## Rev0277 scoring cap

No service floor should score above R2 if its operating status cannot be observed by a maintained dashboard, ledger, or tested manual reporting path. No service floor should score above R3 if affected users cannot challenge wrong status, stale data, unsafe clearance, or exclusion.

Automatic caps: unknown dashboard freshness caps at R2; no correction ledger caps at R2; no public challenge route caps at R3; no OT manual fallback for cyber-physical service floors caps at R2; no toxic-site overlay for relevant reentry or shelter plans caps at R2. Route to `365`, `368`, `369`, and `371` [S638][S653][S661].

## Rev0279 scoring cap — no R4 without impact-to-intake evidence

A service floor should not score R4 if it cannot show impact-to-intake evidence: an exercised incident-management route, rapid-assessment update rule, public restoration clock, safe-access gate, intake / grievance path, and emergency-power guardrail where restrictions or compulsion are possible. A beautiful pre-impact trigger that cannot receive survivors, assess damage, and correct the record after impact is capped below mature readiness.

## Rev0280 addition — stabilization-to-recovery pathways

rev0280 adds the rule that impact-to-intake is not recovery. A person can be registered, sheltered, assessed, or referred and still remain stranded. Climate service floors therefore need stabilization pathways: interim-to-durable housing, displaced-student stability, chronic-care continuity, nutrition-benefit continuity, utility-arrears protection, deadline tolling, and no-wrong-door benefit sequencing [S698][S699][S712].

The cube should now ask not only whether a service exists, but whether a household can move from first contact to a durable outcome without losing school, medicine, food, utilities, legal rights, or case status along the way.

## Rev0281 scoring addition — demote floors that close without outcome proof

Readiness grades should be demoted when a service floor can show intake, referral, award, or restoration but cannot show household functional outcome. A floor cannot be `green` if it lacks balance-sheet protection, tenancy stability, livelihood return, mobility to recovery tasks, essential property/device replacement, document/account recovery, or closeout nonrecurrence where those are material to the service.

## Rev0282 scoring extension

Risk-reduction packets should not receive mature readiness grades until they can show pipeline status, finance stack, benefit-cost / equity test, future-condition data, no-new-risk authority, maintenance owner, and post-project performance monitoring. A project can be eligible, awarded, or complete while still scoring low if it lacks lifecycle O&M, residual-risk disclosure, or evidence that the protected service performs under load [S726][S736][S738].

## Rev0283 routing note — pathway and portfolio tests

Route unresolved long-lived decisions through `413`–`420`: adaptive pathways, model governance, real options, maladaptation gates, asset-portfolio stress tests, service-level contracts, unsafe-asset exits, and professional duty. The key query is no longer only whether a service floor exists; it is whether the floor can change course before physical risk outruns its design [S741][S744][S747][S750].

## Rev0284 addendum — maturity caps

A readiness grade should be capped below mature when the evidence lacks source provenance, internal controls, corrective-action closure, civil-rights access testing, workforce backup, open procurement trail where relevant, or an assurance case for high-stakes floors. Route to `421`–`428` [S761][S763][S768][S770].

---
Citations point to `sources/register.md`.
