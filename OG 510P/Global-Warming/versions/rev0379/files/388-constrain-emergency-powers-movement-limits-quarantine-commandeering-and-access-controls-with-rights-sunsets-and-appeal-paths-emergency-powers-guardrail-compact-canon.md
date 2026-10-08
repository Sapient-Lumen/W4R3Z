---
id: '388'
revision_added: rev0279
status: canon
object_type: integrity_gate
domain_tags:
- emergency_powers
- civil_rights
- public_health_law
- access_control
- evacuation
- quarantine
- reentry
- public_trust
service_floor:
- rights_preserving_emergency_authority
- sunset_and_review_path
- appealable_restriction
hazard_tags:
- disease
- toxic_release
- wildfire
- flood
- storm
- heat
- smoke
- civil_unrest
- compound_hazard
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- governor_or_executive
- public_health_officer
- emergency_manager
- law_enforcement
- court
- civil_rights_officer
- ombuds
- community_liaison
instrument_tags:
- declare
- restrict
- waive
- commandeer
- quarantine
- evacuate
- curfew
- appeal
- sunset
- audit
routes_to:
- '291'
- '303'
- '314'
- '320'
- '336'
- '337'
- '342'
- '345'
- '374'
- '381'
- '385'
source_ids:
- S695
- S696
upstream_dependencies:
- legal_authority
- public_notice
- courts_or_appeal_body
- language_access
- civil_rights_staff
- public_information
- service_support
downstream_consequences:
- public_noncompliance
- litigation
- discriminatory_harm
- care_interruption
- worker_access_blocked
- loss_of_legitimacy
equity_lenses:
- disabled_people
- limited_english_households
- immigrants
- unhoused_people
- people_in_custody
- racialized_communities
- workers
- tribal_communities
degraded_modes:
- plain_language_order
- offline_appeal_intake
- community_exception_liaison
- periodic_public_review
- least_restrictive_alternative
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- authority_unclear
- restriction_overbroad
- appeal_unavailable
- language_access_gap
- policing_bias
- no_sunset
- private_property_or_worker_liability_unclear
failure_modes:
- emergency_power_substitutes_for_service
- rights_loss_targets_vulnerable_groups
- curfew_blocks_care_or_repair
- quarantine_without_support
- commandeering_without_compensation_path
- restrictions_never_sunset
proof_ledgers:
- emergency_order_register
- restriction_map
- rights_impact_log
- exception_and_appeal_log
- sunset_review_log
- civil_rights_complaint_log
emergency_powers_guardrail: authority, necessity, proportionality, support, exception, appeal, civil-rights review,
  compensation, and sunset posture
---

# 388 — Ideal Solutions: Constrain emergency powers, movement limits, quarantine, commandeering, and access controls with rights, sunsets, and appeal paths

## Core claim

Emergency powers are sometimes necessary. They can also become a service-floor failure when movement limits, curfews, quarantine, isolation, commandeering, roadblocks, evacuation orders, business closures, or reentry restrictions block care, work, repair, family reunification, legal access, disability support, or household survival.

The archive should not treat emergency authority as either automatically illegitimate or automatically justified. It should treat it as an **integrity gate**: power must be lawful, necessary, proportionate, time-limited, publicly explained, supported by services, reviewable, and correctable. CDC's public-health emergency law materials show why legal preparedness includes emergency declarations, quarantine / isolation, liability, licensure, and mutual aid [S696]. FEMA civil-rights materials remind the response system that equal access, language access, disability access, and complaint routes remain operational duties during disaster assistance [S695].

## The guardrail packet

Each emergency-power action should state:

1. legal authority;
2. hazard and necessity;
3. least-restrictive feasible alternative;
4. affected geography and population;
5. service support provided with the restriction;
6. exceptions for care, repair, disability, family, work, and legal needs;
7. appeal or complaint path;
8. civil-rights / equity review;
9. compensation or reimbursement where property or labor is compelled;
10. sunset and renewal standard.

## Support before coercion

A quarantine order without food, medicine, pay, disability support, care, and communication is not a health service floor. A curfew that blocks home-care workers, dialysis transport, pharmacy resupply, or family reunification is not public safety. A roadblock that lacks credential exceptions for critical workers and residents may reduce one risk while creating another.

## Anti-normalization rule

Emergency exceptions must not become ordinary governance. The cube should preserve orders, renewal justifications, appeals, denials, civil-rights complaints, and sunsets in a public-safe ledger. Restrictions that cannot be reviewed are not readiness; they are unbounded power.

## Cube rule

Any packet involving evacuation, shelter-in-place, quarantine, reentry, curfew, access control, commandeering, professional licensure waiver, data-sharing emergency, or compulsory movement should expose `emergency_powers_guardrail`.

---
Citations point to `sources/register.md`.
