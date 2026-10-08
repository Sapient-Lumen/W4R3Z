---
id: '381'
revision_added: rev0279
status: canon
object_type: service_continuity
domain_tags:
- incident_management
- eoc
- common_operating_picture
- resource_management
- public_safety
- local_administration
service_floor:
- owned_incident_coordination
- service_floor_common_operating_picture
- typed_resource_request_path
hazard_tags:
- compound_hazard
- flood
- wildfire
- storm
- heat
- smoke
- outage
- cyber_disruption
- supply_chain_disruption
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- incident_commander
- eoc_manager
- emergency_manager
- public_safety_agency
- utility_liaison
- health_liaison
- community_liaison
- finance_logistics_section
instrument_tags:
- coordinate
- request
- prioritize
- document
- communicate
- demobilize
- review
routes_to:
- '303'
- '308'
- '322'
- '331'
- '332'
- '356'
- '364'
- '365'
- '372'
- '382'
- '383'
source_ids:
- S536
- S687
- S697
upstream_dependencies:
- communications
- power
- staffing
- trained_liaisons
- resource_typing
- data_products
- public_information
downstream_consequences:
- restoration_priorities_conflict
- aid_arrives_to_wrong_place
- public_trust_declines
- service_floor_dashboard_becomes_symbolic
equity_lenses:
- remote_communities
- disabled_people
- limited_english_households
- institutionalized_people
- informal_settlements
- tribal_and_island_communities
degraded_modes:
- paper_sitrep
- radio_resource_request
- liaison_runner
- offline_map_board
- manual_public_brief
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- unclear_command_role
- stale_sitrep
- non_typed_request
- liaison_missing
- political_override_without_record
- dashboard_not_operational
failure_modes:
- briefings_without_decisions
- resource_requests_lost
- lifelines_reported_green_while_users_are_cut_off
- equity_gaps_hidden_by_aggregate_status
- mutual_aid_arrives_without_tasking
proof_ledgers:
- incident_action_plan
- situation_report
- resource_request_log
- lifeline_status_board
- decision_log
- after_action_correction_log
incident_management_state: ICS/EOC/common-operating-picture/resource-request posture named, drilled, and corrected
owner_accountability: incident_owner;operational_liaison_owner;resource_log_owner;public_information_owner
readiness_scoring: R0-R4 based on exercised EOC resource-request loadcase
---

# 381 — Ideal Solutions: Run incident command, EOCs, common operating pictures, and resource requests as service-floor machinery, not theatre

## Core claim

The service-floor cube now needs an incident-management layer. A service floor cannot be protected by a dashboard, alert, or forecast if the incident organization cannot turn status into assignments, resource requests, public messages, and corrected priorities.

NIMS-style incident management matters here not because the archive should become an emergency-management manual, but because climate service floors fail at the exact interfaces NIMS tries to govern: command, coordination, resources, information, mutual aid, EOC support, and public communication [S687][S697]. FEMA's Community Lifelines frame also points in this direction: lifelines are supposed to help officials understand impacts and promote unity of effort around services essential to health, safety, economic security, and incident stabilization [S536].

## What this adds to the cube

`381` turns the EOC / ICS layer into a proof requirement. The question is no longer "is there an emergency operations plan?" The question is whether the service floor can be routed through an operating room that knows who owns the action, what resources are requested, what status is public, what status is uncertain, and what exception path protects missed users.

A serious common operating picture should show at least six different things:

1. **Incident objectives** tied to service floors, not vague mission language.
2. **Lifeline status** with degraded modes and uncertainty labels.
3. **Resource requests** that are typed, prioritized, time-stamped, assigned, and closed.
4. **Equity exceptions** where aggregate green status hides specific blocked users.
5. **Public messages** that match operational reality.
6. **Decision logs** that make after-action review replayable.

## Minimum operating packet

A climate EOC packet should include an incident action plan, operational-period objectives, service-floor liaison roster, resource-request board, public-information clearance path, common operating picture, access / reentry coordination, and finance / logistics documentation path. It should also include the manual fallback: paper maps, radio channels, runner protocol, whiteboard status, preprinted request forms, and public briefing scripts.

The test is deliberately practical: if power, cloud systems, or telecoms fail, can the EOC still see which shelters lack water, which pharmacies need power, which roads block fuel, which critical customers need oxygen, which cooling sites are full, which neighborhoods have no alert confirmation, and which resource requests are still unassigned?

## Failure modes

The most common failure is ceremonial coordination: meetings occur, acronyms are used, and situation reports are produced, but no named owner can prove that the report changed an action. Another failure is status flattening. A jurisdiction reports "water mostly restored" or "shelters open" while disabled users, no-car households, informal settlements, clinics, and remote communities remain outside the working service floor.

## Cube rule

Any packet that uses forecasts, dashboards, lifeline status, mutual aid, pre-positioning, reentry, or scarce restoration should expose `incident_management_state`. Blank means the archive should assume the action path is not yet operational.

---
Citations point to `sources/register.md`.
