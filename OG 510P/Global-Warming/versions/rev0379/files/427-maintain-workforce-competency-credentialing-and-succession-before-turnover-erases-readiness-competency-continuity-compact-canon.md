---
id: '427'
revision_added: rev0284
status: canon
object_type: delivery_packet
domain_tags:
- workforce_competency
- credentialing
- succession
- training
- business_continuity
service_floor:
- workforce_competency_succession
- role_depth
- competency_retention
hazard_tags:
- compound_hazard
- outage
- cyber_disruption
- disease
- displacement
clock_tags:
- learning_clock
- emergency_clock
- seasonal_clock
- finance_clock
actor_tags:
- human_resources
- emergency_manager
- service_owner
- union
- mutual_aid_coordinator
- training_officer
instrument_tags:
- role_roster
- credential_matrix
- succession_plan
- training_record
- mutual_aid_credential
- fatigue_control
routes_to:
- '332'
- '353'
- '357'
- '381'
- '422'
- '423'
- '428'
source_ids:
- S602
- S687
- S763
- S770
upstream_dependencies:
- mutual_aid_status
- owner_accountability
- essential_worker_sustainment
- internal_control_posture
downstream_consequences:
- faster_recovery
- less_key_person_risk
- safe_surge
- continuity_across_administrations
equity_lenses:
- small_jurisdictions
- tribal_governments
- rural_departments
- frontline_workers
- care_workers
degraded_modes:
- regional_pool
- remote_expert_support
- temporary credential recognition
- retiree reserve
- cross_training
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- single_point_expert
- credential_not_mutually_recognized
- training_not_repeated
- surge_staff_unfunded
- burnout_after_events
failure_modes:
- continuity_plan_unstaffed
- permit_or_inspection_backlog
- mutual_aid_arrives_but_cannot_work
- dashboard_unmaintained
- tribal_or_local_capacity_gap
proof_ledgers:
- role_depth_matrix
- training_completion_log
- credential_inventory
- succession_roster
- surge_staff_agreement
- fatigue_and_relief_log
workforce_competency_succession: critical roles have trained backups, credential recognition, surge roster, relief/fatigue
  controls, and retest after turnover
---

# 427 — Maintain workforce competency, credentialing, and succession before turnover erases readiness

## Core claim

Readiness can disappear when one planner retires, one inspector burns out, one vendor account lapses, one credential is not recognized, or one dashboard maintainer leaves. Workforce competency is a continuity asset.

ISO 22301 frames business continuity as a documented management system that is planned, established, implemented, operated, monitored, reviewed, maintained, and continually improved for disruptive incidents [S770]. FEMA's exercise and incident-management doctrine already requires common systems, training, resource management, and improvement planning [S602][S687]. The continuous-improvement layer makes the same point for people: readiness must survive turnover and fatigue [S763].

## Competency packet

Every critical service floor should identify:

- essential roles;
- primary and backup people or organizations;
- minimum competency and credential;
- mutual-aid recognition path;
- surge and relief staffing;
- training refresh interval;
- fatigue and family-support controls;
- succession if the owner changes job, office, or administration.

## Key-person rule

A service floor dependent on one expert, one contractor, one password, one retired official, or one unrecorded local memory should be downgraded until role depth is proven.

## Cube rule

The field `workforce_competency_succession` tests whether readiness survives turnover. Blank means service continuity may depend on invisible human single points of failure.

---
Citations point to `sources/register.md`.
