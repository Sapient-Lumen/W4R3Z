---
id: '389'
revision_added: rev0280
status: canon
object_type: router
domain_tags:
- stabilization
- recovery_pathway
- survivor_intake
- case_management
- service_floor
- durable_outcome
service_floor:
- intake_to_durable_outcome_pathway
- handoff_without_drop
- public_recovery_status
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- smoke
- storm
- outage
- displacement
- disease
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- recovery_coordinator
- case_manager
- housing_lead
- health_lead
- school_liaison
- benefits_agency
- legal_aid
- community_intermediary
instrument_tags:
- route
- refer
- track
- toll
- stack_benefits
- publish_status
- appeal
- close_or_reopen
routes_to:
- '385'
- '390'
- '391'
- '392'
- '393'
- '394'
- '395'
- '396'
- '355'
- '380'
source_ids:
- S698
- S699
- S713
upstream_dependencies:
- survivor_intake
- rapid_assessment
- case_management
- identity_or_substitute_documents
- privacy_controls
- payment_rails
- community_intermediaries
downstream_consequences:
- durable_housing
- health_continuity
- school_stability
- nutrition_access
- utility_continuity
- legal_redress
- trust
equity_lenses:
- renters
- unhoused_people
- limited_english_households
- disabled_people
- older_adults
- undocumented_people
- informal_workers
- rural_or_remote_households
- children
degraded_modes:
- paper_case_file
- phone_handoff
- community_case_table
- offline_deadline_hold
- mobile_recovery_team
- public_queue_status_without_private_data
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- intake_without_owner
- referral_without_acceptance
- temporary_shelter_becomes_default
- program_clocks_conflict
- case_status_hidden
- eligibility_rules_fragmented
failure_modes:
- survivor_is_registered_but_not_recovered
- household_repeats_story_to_many_agencies
- temporary_aid_expires_before_durable_solution
- case_closed_while_need_remains
- rights_deadline_runs_during_displacement
proof_ledgers:
- pathway_map
- handoff_acceptance_log
- case_status_log
- deadline_tolling_log
- benefit_stack_log
- unresolved_need_register
- reopen_log
stabilization_pathway: intake, assessment, case plan, benefit stack, deadline hold, durable destination, closure,
  and reopen path are mapped and owned
---

# 389 — Connect survivor intake to durable recovery pathways before assistance becomes a waiting room

## Core claim

Impact-to-intake is not recovery. A survivor can be found, registered, assessed, and referred, yet still remain trapped in a waiting room: a hotel with no housing path, a school without transport, a medical device without power, a food benefit without a store, a utility arrearage without a reconnection rule, or a legal deadline running while the household is displaced.

rev0279 made the first post-impact loop visible. rev0280 adds the next gate: every intake outcome must route to a stabilization pathway. FEMA's individual assistance and disaster survivor systems provide formal entry points [S698][S713], while the National Disaster Recovery Framework organizes longer recovery through recovery support functions [S699]. The archive's rule is stricter: a jurisdiction cannot claim recovery readiness unless it can prove the handoff from immediate aid to durable outcome.

## The pathway packet

A stabilization pathway has nine fields:

1. **entry trigger** — intake, assessment, field outreach, hospital discharge, school referral, utility outage, shelter roster, or community report;
2. **owner of record** — not simply an agency name, but a reachable operational owner;
3. **accepted handoff** — the receiving program acknowledges the case, not merely receives a referral;
4. **deadline hold** — applications, appeals, court dates, tax filings, benefit renewals, school enrollment, and utility bills are held or extended where the disaster makes ordinary compliance impossible;
5. **benefit stack** — FEMA, local aid, insurance, D-SNAP, Medicaid / health systems, utility assistance, legal aid, CDBG-DR, philanthropy, and voluntary-agency support are sequenced without double-count confusion;
6. **durable destination** — the household knows whether the path is return, repair, rental, relocation, buyout, institutional transition, or longer casework;
7. **status visibility** — private case status and public aggregate queue status exist;
8. **grievance and reopen route** — denials, missed outreach, expired aid, and failed referrals can be corrected;
9. **closure test** — closure means the need was resolved, transferred with acceptance, or publicly counted as unresolved.

## Why this belongs in the cube

Most disaster systems can count applications. Fewer can count completed recovery pathways. The cube should therefore distinguish `registered`, `referred`, `accepted`, `stabilized`, `durable`, `closed`, and `reopened`. This is not bureaucracy for its own sake. It prevents the assistance system from mistaking motion for recovery.

## Routing rule

Open this file whenever a service floor appears to exist but a person still cannot get from the emergency interface to a durable state. Then route to housing `390`, school `391`, health `392`, food `393`, utilities `394`, deadline tolling `395`, and no-wrong-door sequencing `396`.

## Cube rule

All people-facing service floors should expose `stabilization_pathway`. Blank means the archive should assume the system can start help but cannot prove it can carry people through the next gate.

## Rev0281 addendum — pathway completion requires household-function proof

The stabilization pathway now routes to `397`–`404` before closure. Intake becomes durable recovery only when the household can function and the remaining risks are owned: housing, tenancy, income, debt / credit, school, chronic care, nutrition, utilities, deadlines, benefits, mobility, essential devices, documents, accounts, and nonrecurrence.

---
Citations point to `sources/register.md`.
