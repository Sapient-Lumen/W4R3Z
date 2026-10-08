---
id: '385'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- survivor_intake
- case_navigation
- help_line
- grievance
- civil_rights
- legal_access
- social_protection
- field_outreach
service_floor:
- reachable_survivor_intake
- case_status_visibility
- grievance_and_appeal_route
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- smoke
- outage
- displacement
- disease
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- disaster_survivor_assistance_team
- caseworker
- call_center
- community_organization
- legal_aid
- benefits_agency
- civil_rights_officer
instrument_tags:
- intake
- refer
- track
- appeal
- translate
- accommodate
- correct
routes_to:
- '274'
- '291'
- '318'
- '325'
- '342'
- '343'
- '348'
- '355'
- '380'
- '382'
- '383'
source_ids:
- S581
- S694
- S695
upstream_dependencies:
- communications
- identity_or_substitute_documents
- payment_rails
- field_staff
- trusted_intermediaries
- privacy_controls
downstream_consequences:
- unmet_needs
- wrongful_denial
- fraud_exposure
- delayed_cash
- health_decline
- trust_loss
equity_lenses:
- limited_english_households
- deaf_or_hard_of_hearing_people
- disabled_people
- older_adults
- unhoused_people
- no_ID_households
- undocumented_people
- remote_communities
degraded_modes:
- paper_intake
- mobile_field_teams
- community_intake_sites
- phone_hotline
- SMS_status
- trusted_intermediary_referral
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- portal_down
- call_center_overloaded
- language_gap
- document_gap
- case_status_hidden
- field_teams_not_reaching_unhoused_or_remote_users
failure_modes:
- survivor_repeats_story_to_many_agencies
- denial_without_route
- no_status_tracking
- digital_only_access
- civil_rights_complaints_not_routed
- aid_navigation_privatised_by_scammers
proof_ledgers:
- intake_channel_status
- case_status_log
- referral_outcome_log
- grievance_log
- language_access_log
- field_outreach_coverage_map
survivor_intake_access: multi-channel, accessible, field-capable intake with case status, referral outcome, grievance,
  and civil-rights route
---

# 385 — Ideal Solutions: Make survivor intake, field navigation, 211/311-style help, case status, and grievances a service floor after shocks

## Core claim

Survivor intake is a service floor. After climate shocks, people do not experience "programmes" as a neat stack. They experience a maze: FEMA or national assistance, local shelter, utilities, insurers, landlords, legal aid, schools, health care, food support, cash, documents, employers, contractors, and debt collectors. The cube needs one visible intake / navigation layer that can route people across that maze.

DisasterAssistance.gov is one formal assistance portal [S581], and FEMA describes Disaster Survivor Assistance as field presence focused on survivor needs and targeted information collection [S694]. The archive's rule is broader: any jurisdiction claiming service-floor recovery must be able to prove reachable intake, status visibility, referrals, grievances, language access, disability access, and field outreach [S695].

## The intake packet

The minimum packet has eight channels:

1. digital application;
2. phone hotline;
3. in-person recovery center;
4. mobile field teams;
5. trusted community intermediary;
6. legal-aid / rights referral;
7. case status lookup;
8. grievance / appeal / correction path.

A ninth channel is often needed: outreach to people who will not come to the system because they lack ID, fear immigration or policing consequences, are isolated, are institutionalized, lack phone / internet, are displaced, cannot hear or read the alert, or have been scammed before.

## Case status is a dignity floor

A person should not have to retell loss twenty times to discover that a form is missing, a programme is ineligible, a referral was never accepted, or a contractor has no route. Intake readiness therefore includes a case status ledger: need, document status, referral, owner, deadline, denial reason, appeal status, payment status, and closure or unresolved gap.

## Anti-scam rule

When official intake is slow or opaque, scammers, predatory contractors, high-cost lenders, fake charities, and fee-charging navigators fill the gap. Survivor intake is therefore part of consumer protection. The public should know which channels are official, which services are free, where to complain, and how to get help without paying for access.

## Cube rule

All household-facing service floors should expose `survivor_intake_access`. Blank means the archive should assume the service exists for people who can already navigate it, not for people under disaster conditions.

---
Citations point to `sources/register.md`.
