---
id: '382'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- damage_assessment
- needs_assessment
- rapid_assessment
- public_assistance
- individual_assistance
- public_health
- humanitarian_coordination
service_floor:
- rapid_impact_assessment
- needs_to_action_route
- excluded_user_detection
hazard_tags:
- flood
- storm
- wildfire
- heat
- smoke
- drought
- outage
- toxic_release
- disease
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- damage_assessment_team
- public_health_agency
- emergency_manager
- housing_official
- infrastructure_owner
- community_organization
- tribal_local_authority
instrument_tags:
- assess
- sample
- validate
- route
- declare
- appeal
- update
routes_to:
- '325'
- '330'
- '348'
- '351'
- '355'
- '365'
- '366'
- '371'
- '381'
- '383'
- '385'
source_ids:
- S688
- S689
- S690
upstream_dependencies:
- field_access
- trained_assessors
- maps
- communications
- forms
- community_trust
- civil_rights_access
downstream_consequences:
- aid_delay
- misallocation
- unmet_needs_backlog
- public_assistance_gap
- household_exclusion
equity_lenses:
- renters
- undocumented_people
- limited_english_households
- tribal_communities
- remote_island_communities
- disabled_people
- informal_housing
degraded_modes:
- paper_forms
- phone_sampling
- community_report_triage
- door_to_door_teams
- satellite_plus_ground_truth
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- access_blocked
- sample_bias
- forms_not_interoperable
- households_unreachable
- damage_category_mismatch
- declaration_gate_delay
failure_modes:
- declaration_metrics_hide_need
- initial_assessment_becomes_stale
- unassessed_places_mistaken_for_unharmed_places
- data_collection_extracts_without_service
- needs_not_linked_to_owner
proof_ledgers:
- initial_damage_assessment_log
- PDA_package
- CASPER_or_needs_assessment_report
- unassessed_area_map
- assistance_routing_log
- data_revision_log
rapid_assessment_state: initial_damage_assessment plus household/public-health needs assessment plus revision log
readiness_scoring: assessment readiness graded by timeliness, coverage, validation, routing, and correction
---

# 382 — Ideal Solutions: Convert rapid damage, impact, and needs assessments into routed recovery actions before declarations become the only proof

## Core claim

After a shock, the archive must distinguish **assessment for declaration** from **assessment for action**. Preliminary damage assessments matter because they support formal assistance and public funding, but climate service floors also need rapid household, infrastructure, health, access, and exclusion assessments that route help before paperwork becomes the only recognized truth [S688].

CDC's CASPER model is useful because it treats rapid assessment as household-level decision support for public-health leaders and emergency managers, not as a press-release exercise [S689]. The humanitarian MIRA model adds a parallel lesson: in sudden-onset emergencies, coordinated initial assessment should identify strategic priorities, not produce disconnected sector surveys [S690].

## The assessment chain

A serious impact-to-action chain has five pieces.

1. **Initial scan:** hazard footprint, lifeline outages, exposed facilities, blocked access, missing communications, and known worst-hit zones.
2. **Damage assessment:** homes, infrastructure, public facilities, private nonprofit assets, utilities, roads, environmental releases, and service assets.
3. **Needs assessment:** food, water, medicine, shelter, cash, documents, transport, care, safety, language access, disability access, and household coping capacity.
4. **Routing:** every assessed need gets an owner, programme, referral, denial reason, or public gap label.
5. **Revision:** the assessment is updated when access improves, hidden damage appears, or community reports contradict the first map.

## Missingness is a finding

The cube should treat unassessed places as red or amber, not blank. Flooded informal settlements, isolated islands, worker camps, nursing homes, prisons, rural roads, mobile-home parks, and undocumented households can disappear from formal damage counts. That invisibility then cascades into underfunded shelter, missing medicines, denied repair help, inaccurate public dashboards, and bad restoration priority.

## Operating test

A jurisdiction passes this note only if it can produce a joined ledger: assessed parcels / facilities, sampled households, unassessed areas, urgent service failures, civil-rights / language / disability access gaps, action owner, referral status, revision date, and public explanation. Assessment without routing is extraction. Routing without revision is stale truth.

## Cube rule

All post-impact service-floor packets should expose `rapid_assessment_state`. The field should name the method, owner, coverage, update clock, unassessed-area rule, and assistance-routing link.

---
Citations point to `sources/register.md`.
