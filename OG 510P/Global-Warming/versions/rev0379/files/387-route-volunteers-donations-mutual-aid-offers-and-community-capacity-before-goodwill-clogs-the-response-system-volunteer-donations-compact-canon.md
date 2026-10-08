---
id: '387'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- volunteer_management
- donations
- community_organizations
- mutual_aid
- mass_care
- logistics
- safeguarding
service_floor:
- safe_useful_volunteer_capacity
- donation_offer_routing
- community_capacity_bridge
hazard_tags:
- compound_hazard
- flood
- wildfire
- storm
- heat
- smoke
- displacement
- outage
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- volunteer_coordinator
- voluntary_agency_liaison
- community_organization
- donations_manager
- safeguarding_officer
- logistics_section
instrument_tags:
- intake
- screen
- assign
- train
- refer
- decline
- demobilize
- protect
routes_to:
- '328'
- '332'
- '339'
- '343'
- '345'
- '350'
- '353'
- '361'
- '381'
- '386'
source_ids:
- S693
upstream_dependencies:
- public_information
- EOC
- resource_requests
- community_trust
- logistics
- safeguarding
- insurance_or_liability
downstream_consequences:
- unsafe_response
- warehouse_clog
- local_market_harm
- missed_needs
- worker_burnout
- protection_failure
equity_lenses:
- grassroots_groups
- faith_groups
- mutual_aid_networks
- immigrant_led_organizations
- disabled_volunteers
- youth_volunteers
- survivor_led_groups
degraded_modes:
- phone_offer_intake
- paper_volunteer_roster
- pre-cleared_community_roles
- microgrant_to_community_group
- decline_script_for_unsolicited_goods
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- unaffiliated_volunteers
- unsolicited_goods
- background_check_delay
- liability_unclear
- safeguarding_gap
- community_groups_unfunded
- offer_no_request_match
failure_modes:
- goodwill_clogs_roads_or_warehouses
- untrained_volunteers_enter_unsafe_sites
- aid_favors_visible_places
- donations_compete_with_local_markets
- exploitation_or_abuse_at_aid_interface
- community_groups_burn_out
proof_ledgers:
- volunteer_intake_log
- donations_offer_log
- request_match_log
- training_and_safety_log
- safeguarding_incident_log
- demobilization_log
volunteer_donations_management: offer intake, role assignment, safety/safeguarding, donation matching, decline/demobilization,
  and community funding posture
---

# 387 — Ideal Solutions: Route volunteers, donations, mutual aid offers, and community capacity before goodwill clogs the response system

## Core claim

Goodwill is not automatically capacity. Volunteers, donations, mutual aid offers, private trucks, church kitchens, social-media drives, medical volunteers, amateur responders, and community groups can save lives. They can also clog roads, fill warehouses with unusable goods, create safeguarding risks, bypass local priorities, exhaust community leaders, and compete with local markets.

FEMA's Volunteer and Donations Management Support Annex exists because unaffiliated volunteers and unsolicited donated goods are predictable operational problems, not rare inconveniences [S693]. The climate cube should therefore treat volunteer and donation routing as part of service-floor readiness.

## Minimum operating packet

The packet should include:

1. a public message: cash / requested goods / official volunteer channels;
2. an offer-intake form tied to EOC resource requests;
3. pre-cleared volunteer roles;
4. credential, background, safety, and safeguarding rules;
5. donations warehouse / sorting / refusal policy;
6. community-organization microgrant or reimbursement path;
7. demobilization and thank-you / closure process;
8. incident reporting for harm, exploitation, or fraud.

## Community capacity is not free

The archive should not romanticize mutual aid as an unlimited substitute for public duty. Community organizations need money, rest, insurance, staff, translation support, data protection, safety support, and a route to say no. A response that depends on them while refusing to fund or protect them is extracting trust.

## Anti-clog rule

If a donation or volunteer offer does not match a documented request, role, safety condition, or recipient path, the system should redirect or decline it. Saying no to unusable goods can be a pro-recovery act.

## Cube rule

Any packet that assumes volunteers, community groups, donated goods, faith organizations, mutual aid, or private offers should expose `volunteer_donations_management`. Blank means goodwill is being counted without governance.

---
Citations point to `sources/register.md`.
