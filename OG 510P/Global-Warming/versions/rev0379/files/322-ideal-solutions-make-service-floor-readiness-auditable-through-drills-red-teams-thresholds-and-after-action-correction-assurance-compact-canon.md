---
id: '322'
revision_added: rev0271
status: canon
object_type: integrity_gate
domain_tags:
- assurance
- drills
- red_team
- readiness
- audit
- service_floors
- after_action
service_floor:
- auditable_service_floor_readiness
- correction_enforcement
hazard_tags:
- compound_shock
- outage
- cyber
- flood
- heat
- smoke
- drought
- conflict
- staff_shortage
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- auditor
- emergency_manager
- regulator
- service_operator
- community_reviewer
- inspector
- funder
instrument_tags:
- drill
- audit
- threshold
- inspect
- red_team
- publish
- correct
- demote
routes_to:
- '83'
- '114'
- '117'
- '118'
- '119'
- '120'
- '121'
- '122'
- '251'
- '252'
- '253'
- '301'
- '302'
- '308'
source_ids:
- S602
- S605
- S606
- S607
- S608
- S612
- S614
- S616
- S654
- S655
- S657
- S663
upstream_dependencies:
- data
- inspectors
- users
- budgets
- legal_authority
- service_operators
- community_feedback
- procurement
downstream_consequences:
- false_readiness
- repeated_failure
- uncorrected_exclusion
- unfunded_lessons
- service_floor_collapse
- trust_loss
equity_lenses:
- disabled_people
- children
- older_adults
- migrants
- renters
- informal_workers
- people_in_custody
- low_income_households
- remote_communities
degraded_modes:
- public_readiness_status
- conditional_operation
- compensating_measure
- manual_fallback
- community_override
- readiness_demotion
evidence_grade: design_judgment
speculation_level: medium
bottlenecks:
- paper_readiness
- stale_plan
- untested_fallback
- inaccessible_drill
- no_correction_budget
- hidden_near_miss
failure_modes:
- brochureware_resilience
- tabletop_only_claim
- no_after_action_money
- metrics_without_service
- green_checkmark_theatre
proof_ledgers:
- drill_record
- threshold_breach_log
- near_miss_log
- service_user_test
- correction_budget
- readiness_status_change
restoration_conflicts:
- operator_self_certification_vs_public_evidence
- fast_reopening_vs_safe_reopening
- confidentiality_vs_accountability
- scorecard_vs_lived_access
assurance_tests:
- bad_day_drill
- excluded_user_test
- manual_fallback_test
- after_action_correction_audit
- readiness_demotion_review
---

# 322 — Ideal Solutions: Make service-floor readiness auditable through drills, red teams, thresholds, and after-action correction

## Claim

rev0269 made the archive queryable.
rev0270 made service floors into dependency graphs.
rev0271 adds the assurance gate: **a service floor is not ready because a plan exists; it is ready only to the extent that drills, excluded-user tests, thresholds, ledgers, and funded after-action corrections prove it.**

The archive has many readiness concepts: stress tests, live duties, after-action duties, readiness states, demotion tests, and correction cycles.
This file compresses them for the service-floor era.

A cooling centre is not ready until a no-car household can reach it, a wheelchair user can enter it, a person without a smartphone can find it, and a medically dependent person can keep equipment powered.
A payment system is not ready until cash-out, merchant acceptance, offline mode, fraud control, and redress are tested.
A medical-product plan is not ready until oxygen, pharmacy, cold chain, dialysis, and emergency refill drills work.
A public-safety plan is not ready until dispatch, search and rescue, mass-casualty, family reunification, and records can operate in degraded mode.

House rule: **readiness without tested users is a paper claim.**

## Fast rule

**Every service-continuity packet should carry a readiness status that can be promoted, demoted, conditioned, or quarantined based on drills, thresholds, near misses, excluded-user tests, and funded corrections.**

## Minimum assurance stack

The stack has seven layers:

1. **named service floor** — what must remain true;
2. **dependency map** — what must work around it;
3. **thresholds** — what counts as failure or degraded operation;
4. **drills** — what has been tested under bad-day assumptions;
5. **excluded-user tests** — who normal systems miss;
6. **after-action ledger** — what failed, harmed, or nearly failed;
7. **correction budget** — what is funded and assigned before the next hazard season.

House rule: **a lesson without a budget is a note, not a correction.**

## Red-team questions

For each service floor, ask:

- What if power fails for 72 hours?
- What if telecoms fail but people still need payments, alerts, and care?
- What if the portal works but the user has no phone, ID, car, bank account, or safe household control?
- What if the named shelter is full, too hot, unsafe, or inaccessible?
- What if the pharmacy is open but cold chain failed?
- What if debris blocks the route to dialysis or oxygen delivery?
- What if the data is correct but no agency owns response?
- What if the contractor can deliver only to easy places?
- What if the plan depends on unpaid local organizations?
- What if the first failure is not the hazard but the administration?

House rule: **the useful red team attacks assumptions, not slogans.**

## Readiness states

Use a simple state model:

| Status | Meaning |
|---|---|
| draft | service floor named, but dependency and evidence incomplete |
| paper_ready | plan exists, owners named, but degraded mode not tested |
| drill_ready | degraded mode tested with operators and users |
| season_ready | resources, contracts, staff, and public instructions are current for the next hazard season |
| live_conditioned | allowed to operate only with compensating measures |
| demoted | readiness claim withdrawn after failure, stale data, missed group, or unfunded correction |
| quarantined | claim should not be used for public assurance, funding eligibility, or political credit |

House rule: **demotion is not punishment; it is how the archive stays honest.**

## Minimum proof ledger

| Question | Evidence required |
|---|---|
| Was the fallback tested? | drill design, participant list, failure injects, and results |
| Were excluded users included? | user-path tests for disability, language, no car, no phone, no ID, low income, custody, and displacement |
| Did thresholds trigger action? | threshold breach and activation logs |
| What near miss occurred? | near-miss, workaround, and operator-report log |
| Was correction funded? | budget line, procurement action, owner, and deadline |
| Did status change? | promotion, condition, demotion, or quarantine record |

## What this routes to

- use `322` when a prompt asks whether a service floor is actually ready, how to audit resilience, how to design drills, how to avoid paper compliance, or how to manage readiness status;
- pair with `301` and `302` for cube schema and packet admission;
- pair with `308` for dependency mapping;
- pair with `251` for compound-shock stress testing;
- pair with `253` for after-action correction;
- pair with any service-continuity file from `275` onward.

## Compression rule

**A service floor is ready only to the extent that bad-day drills, excluded-user tests, thresholds, ledgers, and funded corrections prove it.**

## Rev0272 assurance update — test recovery rails, not only emergency response

A service-floor drill should now test the recovery rails that make restoration real: fuel or charging, black-start / islanding, repair contractors, inspectors, claims intake, document substitution, drainage clearance, small-business reopening, community referrals, agrifood input delivery, lab sampling, and public clearance. A plan that performs during the first hours but cannot pass the first weeks of recovery should be marked conditionally ready, not ready.

## Rev0273 assurance patch — pass/fail depends on scenario loadcase and correction

Assurance now has a scenario-loadcase rule. A drill does not prove readiness unless the loadcase is hard enough to matter, includes resource scarcity, tests at least one excluded-user path, names correction owners, funds correction, and retests. rev0273 therefore routes readiness claims through `331` for scarcity, `332` for mutual aid, `333` for spares, and `338` for compound scenario design [S602].

## Rev0274 assurance extension — red-team the access point

Every readiness drill should now include at least one harmful-interface inject: unsafe shelter layout, registry privacy refusal, contractor fraud, pet-inclusive evacuation, mass-fatality family assistance, GBV risk in an aid queue, remote single-road failure, or cultural-site reentry. Readiness that passes infrastructure but fails the human interface is conditional at best [S605][S606][S607][S608][S612][S614][S616].


## Rev0275 assurance note — test the paperwork that moves physical recovery

Readiness drills should now include lost-document applications, buyout limbo, sole-source contract files, project worksheet cost capture, substantial-damage determinations, heat / smoke worker rotations, mobile-home park utility failure, and closed-case follow-up. Paperwork is not peripheral when paperwork controls whether physical recovery happens.

## Rev0276 assurance update

Assurance now has a scoring output. A drill should not only produce lessons learned; it should update the R0-R4 grade, cap the score where sources or owners are stale, identify which owner pays for correction, and set a retest date. Readiness claims that cannot be demoted are not assurance claims.

## Rev0277 assurance extension: observe the red team

Readiness assurance should now include observability failure. Red teams should break not only plans but also dashboards, sensors, rumor response, OT fallback, toxic-site overlays, disease signals, and public-ledger appeals. A service can pass a tabletop while its public status feed, field sensor, or complaint channel fails.

Add five checks to assurance: dashboard stale-data check, sensor blind-spot check, rumor-injection drill, OT manual-fallback drill, and public-ledger challenge test. Route to `365`–`371` [S654][S655][S657][S663].

## Rev0278 assurance addition — activation drills

Readiness assurance now needs activation drills under forecast uncertainty. Test whether owners can release money, staff, shelter, transport, cooling, clean air, cash, and public instructions when a trigger is met, and whether the after-action process can learn from a false alarm or missed alarm without punishing reasonable early action.

---
Citations point to `sources/register.md`.
