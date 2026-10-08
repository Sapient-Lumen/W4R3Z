---
id: '338'
revision_added: rev0273
status: canon
object_type: integrity_gate
domain_tags:
- scenario_loadcase
- drills
- exercises
- compound_risk
- assurance
- after_action
- readiness
- nuclear_assurance
- nuclear_loadcase
service_floor:
- tested_readiness
- scenario_based_assurance
- corrected_after_action
hazard_tags:
- compound_shock
- heat
- smoke
- flood
- storm
- drought
- outage
- cyber
- disease
- supply_chain
- displacement
clock_tags:
- seasonal_clock
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- exercise_planner
- utility
- public_health_agency
- school_district
- service_operator
- community_reviewer
- auditor
instrument_tags:
- exercise
- loadcase
- inject
- evaluate
- red_team
- correct
- demote
- publish
- retest
routes_to:
- '83'
- '113'
- '114'
- '117'
- '118'
- '119'
- '120'
- '121'
- '122'
- '251'
- '252'
- '301'
- '308'
- '322'
- '331'
- '332'
- '430'
- '436'
- '438'
- '442'
- '443'
source_ids:
- S602
- S606
- S607
- S608
- S612
- S614
- S616
- S618
upstream_dependencies:
- scenario_library
- exercise_program
- evaluators
- community_participants
- operator_data
- correction_budget
- public_reporting
- leadership_authority
downstream_consequences:
- false_readiness
- uncorrected_failure
- exclusion_at_scale
- paper_compliance
- compound_cascade
- trust_loss
equity_lenses:
- disabled_people
- older_adults
- children
- low_income_households
- migrants
- people_without_smartphones
- people_in_custody
- rural_communities
- language_minority_groups
degraded_modes:
- manual_fallback_exercise
- community_observer
- public_readiness_score
- conditional_pass
- readiness_demotion
- targeted_retest
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- easy_scenario_bias
- tabletop_only
- no_real_users
- no_resource_constraint
- no_correction_budget
- confidential_findings
- exercise_not_tied_to_readiness_status
failure_modes:
- readiness_theatre
- exercise_passes_because_scenario_is_easy
- after_action_report_without_owner
- excluded_users_not_tested
- no_retest_after_failure
- compound_risk_hidden_by_single_hazard_plan
proof_ledgers:
- scenario_library
- exercise_inject_log
- participant_roster
- real_user_test_log
- after_action_improvement_plan
- correction_owner_register
- retest_log
- readiness_status_change
restoration_conflicts:
- public_transparency_vs_security_sensitivity
- hard_scenario_vs_political_comfort
- exercise_cost_vs_hidden_failure
- operator_reputation_vs_correction
assurance_tests:
- bad_day_compound_loadcase
- no_power_no_broadband_test
- excluded_user_journey
- staff_shortage_inject
- mutual_aid_saturation_inject
- correction_retest
exercise_load_case: compound_bad_day_with_real_resource_limits_and_real_user_paths
---
# 338 — Ideal Solutions: Test service floors against compound scenario loadcases before tabletops become readiness theatre

## Claim

A plan can pass a tabletop and still fail people. **Service floors should be tested against compound loadcases with real constraints, real users, failed dependencies, and funded correction.**

FEMA's HSEEP provides a common approach to exercise management, design, conduct, evaluation, and improvement planning, and FEMA Exercise Starter Kits help jurisdictions validate plans and policies [S602]. The archive's added rule is that climate continuity exercises must not choose easy scenarios that protect institutional confidence.

## Compact rule

**Readiness is scenario-relative. Name the loadcase before claiming the service is ready.**

A cooling plan may be ready for heat with power but not heat plus smoke plus outage. A payment system may be ready for broadband outage but not broadband outage plus cash-shipment delay. A water system may be ready for a pump failure but not pump failure plus chemical shortage plus flooded access road. A school plan may be ready for closure but not closure plus caregiver work disruption plus meal-program interruption.

## Required loadcases

Each service floor should be tested against at least four kinds of loadcase:

1. **same-hazard intensity:** the normal hazard becomes more severe or longer;
2. **dependency loss:** power, telecoms, transport, staff, records, payment, fuel, or water fails;
3. **simultaneous demand:** several services need the same scarce resource at once;
4. **excluded-user path:** someone without a car, smartphone, English, documents, money, home, caregiver, or legal status tries to use the service.

## Scoring rule

A passed drill should not mean everyone felt prepared. It should mean the service met a minimum threshold, failures were logged, corrective actions have owners and budgets, and the packet will be retested. A partial pass should create conditional readiness. A failed drill should demote readiness status.

## Cube routing

Route this file whenever a packet claims readiness, resilience, continuity, stress test, exercise, tabletop, red team, after-action, or drill. Pair with `322` for assurance, `331` for scarcity priority, `332` for mutual aid, and `308` for dependency mapping.

## Rev0274 loadcase extension — harmful-interface injects

Compound loadcases now require an interface failure, not only an infrastructure failure. Examples: a shelter is open but unsafe for a survivor; a priority registry leaks sensitive data; a wildfire evacuation fails because pets are excluded; recovery cash triggers contractor fraud; a mass-fatality event lacks family notification; a rural road closure strands medicine and fuel; a sacred site is cleared as debris. These injects route to `339`–`347` [S606][S607][S608][S612][S614][S616][S618].


## Rev0275 loadcase addendum — add proof-to-rebuild stressors

Compound loadcases should include administrative stressors: destroyed records, disputed title, tenants without leases, buyout uncertainty, emergency sole-source contracting, reimbursement delay, code-upgrade cost gaps, worker lodging failure, condo / HOA common-element deadlock, and post-closeout unmet needs.

## Rev0276 loadcase update

Scenario loadcases now explicitly include finance, insurance-market, border, basin, and informal-labour failure modes. A tabletop that never tests reimbursement delay, insurance nonrenewal, customs blockage, upstream water decision, or no-ID worker-camp heat exposure is still too easy.
---
Citations point to `sources/register.md`.
