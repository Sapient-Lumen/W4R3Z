---
id: '336'
revision_added: rev0273
status: canon
object_type: service_continuity
domain_tags:
- elections
- democracy
- public_participation
- civic_continuity
- records
- legitimacy
- governance
service_floor:
- election_continuity
- public_participation_continuity
- civic_decision_legitimacy
hazard_tags:
- flood
- wildfire
- heat
- storm
- outage
- cyber
- displacement
- smoke
- violence
- misinformation
clock_tags:
- seasonal_clock
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- election_official
- emergency_manager
- local_government
- civil_society
- court
- media
- poll_worker
- postal_service
- registrar
instrument_tags:
- contingency_plan
- relocate
- extend
- notify
- audit
- secure
- observe
- appeal
- translate
- accommodate
routes_to:
- '04'
- '35'
- '58'
- '95'
- '129'
- '260'
- '263'
- '291'
- '293'
- '294'
- '315'
- '322'
source_ids:
- S598
- S599
upstream_dependencies:
- election_records
- poll_workers
- polling_sites
- ballots
- power
- telecoms
- transport
- mail
- courts
- public_information
- translation
- accessibility
downstream_consequences:
- lost_vote_access
- illegitimate_decision
- delayed_recovery_authority
- capture_of_rebuilding_decisions
- civil_unrest
- trust_loss
equity_lenses:
- displaced_voters
- disabled_voters
- language_minority_voters
- older_adults
- rural_voters
- low_income_voters
- people_without_mail_access
- people_without_documents
degraded_modes:
- relocated_polling_place
- extended_voting_window
- paper_backup
- mobile_voting_support_where_legal
- radio_notice
- accessible_public_hearing
- emergency_observer_protocol
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- polling_place_loss
- poll_worker_displacement
- voter_displacement
- power_outage
- paper_ballot_supply
- communications_failure
- misinformation
- deadline_rigidity
- inaccessible_relocation
failure_modes:
- disaster_suppresses_turnout
- emergency_rule_changes_untrusted
- polling_site_moved_without_notice
- displaced_voters_lose_registration_access
- climate_decisions_made_without_public_hearing
- recovery_plan_loses_legitimacy
proof_ledgers:
- election_contingency_plan
- polling_place_relocation_log
- voter_notice_log
- accessible_voting_log
- ballot_chain_of_custody
- public_meeting_access_log
- emergency_rule_change_register
- post_event_participation_audit
restoration_conflicts:
- speed_vs_participation
- emergency_authority_vs_due_process
- security_vs_access
- flexibility_vs_equal_treatment
- misinformation_control_vs_free_expression
assurance_tests:
- natural_hazard_election_tabletop
- polling_place_relocation_drill
- paper_backup_test
- accessible_notice_test
- displaced_voter_scenario
- public_hearing_degraded_mode_test
civic_legitimacy_check: emergency_decisions_keep_notice_access_record_appeal_and_audit
---

# 336 — Ideal Solutions: Protect elections, public participation, and civic decision continuity during climate shocks

## Claim

Climate shocks can interrupt democracy as well as infrastructure. **Elections, public participation, public hearings, grievance routes, and civic decision records are climate-critical services because recovery authority and transition legitimacy depend on them.**

The U.S. Election Assistance Commission states that elections and voting-related activities are essential governmental operations and that election officials are expected to continue their work during crisis [S598]. International IDEA now tracks and analyzes natural-hazard disruptions to elections, including hazards likely to increase with climate change [S599].

The archive does not turn climate policy into election law. It adds a narrower continuity rule: climate shocks should not silently decide who can vote, object, testify, appeal, observe, or shape recovery.

## Compact rule

**Emergency flexibility must preserve access, chain of custody, notice, equal treatment, and after-action audit.**

A resilient election or public-decision process needs fallback polling sites, poll-worker surge, ballot and equipment chain-of-custody, power and communications backup, accessible notice, transportation and disability access, language access, displaced-voter rules, cyber contingency, and clear legal authority for emergency changes.

Public participation needs similar degraded modes. A rebuilding plan, utility-rate hearing, relocation decision, debris-site siting, school-closure decision, floodway rule, or carbon-market project should not become legitimate merely because a disaster made normal participation hard.

## Minimum packet

The minimum civic-continuity packet includes:

- election / meeting contingency plan;
- hazard calendar and facility-risk screen;
- backup sites, paper modes, power, communications, and secure storage;
- voter / resident notice in accessible formats and languages;
- displaced-person participation pathway;
- observer, media, and public-record rules;
- emergency legal authority and sunset;
- post-event participation audit.

## Failure modes

Bad continuity suppresses people without saying so. A polling place moves but the notice reaches only smartphone users. An early-voting site closes in the affected area. A public hearing moves online during an outage. A relocation plan is approved while displaced residents lack mail, documents, childcare, translation, or transport. A climate project claims community consent based on meetings held during disaster recovery.

## Cube routing

Route this file whenever a climate programme depends on public consent, elections, siting, hearings, grievance, emergency rulemaking, disaster declarations, rate cases, relocation, recovery planning, or claims about community approval. Pair with `260`, `270`, `291`, `293`, `294`, `315`, and `322`.

---
Citations point to `sources/register.md`.
