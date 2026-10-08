---
id: '428'
object_type: router
domain_tags:
- assurance_case
- service_floor_maturity
- evidence_argument
- public_accountability
- cube_validation
- nuclear_assurance_case
- nuclear_energy
- nuclear_regulatory_legitimacy
- nuclear_bankability
- nuclear_buildability
- nuclear_market_design
- nuclear_supply_chain
- nuclear_public_value
- nuclear_integrated_energy_systems
- nuclear_cogeneration
- nuclear_desalination
- nuclear_hydrogen
- nuclear_data_centers
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_cyber_digital_assurance
service_floor:
- resilience_assurance_case
- claim_evidence_argument
- maturity_attestation
hazard_tags:
- compound_hazard
- outage
- cyber_disruption
clock_tags:
- learning_clock
- emergency_clock
- finance_clock
- recovery_clock
- standards_clock
actor_tags:
- service_owner
- auditor
- civil_rights_office
- data_steward
- community_reviewer
- elected_body
instrument_tags:
- assurance_case
- claim_tree
- evidence_map
- exception_register
- red_team_review
- public_attestation
routes_to:
- '356'
- '364'
- '371'
- '421'
- '422'
- '423'
- '424'
- '426'
- '427'
- '438'
- '439'
- '440'
- '441'
- '442'
- '443'
- '444'
- '445'
- '446'
- '447'
- '448'
- '454'
- '455'
- '456'
- '457'
- '458'
- '464'
- '465'
- '466'
- '467'
- '468'
- '498'
source_ids:
- S756
- S758
- S759
- S761
- S770
upstream_dependencies:
- cube_normalization_state
- internal_control_posture
- corrective_action_state
- independent_audit_redress
- civil_rights_language_access_gate
- workforce_competency_succession
downstream_consequences:
- credible_maturity_grade
- public_trust
- audit_ready_claim
- better_budget_decisions
equity_lenses:
- excluded_users
- future_users
- frontline_workers
- low_capacity_local_governments
- public_reviewers
degraded_modes:
- limited_scope_assurance_case
- manual_evidence_binder
- conditional_maturity_with_expiry
evidence_grade: synthesis
speculation_level: low
revision_added: rev0284
status: canon
bottlenecks:
- evidence_scattered
- claim_scope_vague
- exceptions_hidden
- user_path_not_tested
- owner_not_accountable
failure_modes:
- maturity_badge_without_evidence
- false_confidence
- audit_failure
- excluded_user_harm
- repeat_service_failure
proof_ledgers:
- claim_tree
- source_edge_table
- control_matrix
- corrective_action_register
- civil_rights_access_gate
- exercise_result
- management_attestation
resilience_assurance_case: high-stakes maturity claim has scoped claim, evidence map,
  provenance, controls, tests, exceptions, civil-rights gate, owner attestation, and
  independent challenge path
---

# 428 — Require a resilience assurance case before high-stakes service floors are declared mature

## Core claim

A high-stakes service floor should not be called mature because it has many rows in the cube. It should be called mature only when a structured assurance case connects the claim to evidence, provenance, controls, tests, exceptions, access gates, correction history, and accountable owners.

The W3C Data Cube model supports multidimensional data; PROV-O supports explicit provenance; FAIR supports machine and human reuse; the Green Book supports reliable reporting and internal control; and ISO 22301 supports maintained and continually improved continuity-management systems [S756][S758][S759][S761][S770]. Together they imply a stricter doctrine: a maturity grade is not the evidence. It is the conclusion of an argument that can be inspected.

## Assurance-case packet

For life-safety, rights, housing, health, income, water, power, shelter, evacuation, benefits, or recovery finance, the archive should expect:

- explicit claim and scope;
- protected service floor and loadcase;
- owner and backup owner;
- evidence map and provenance;
- internal-control packet;
- exercise or event result;
- civil-rights and excluded-user test;
- known exceptions and expiry dates;
- corrective-action closure evidence;
- independent review or public challenge path.

## Badge rule

Readiness grades should expire if evidence goes stale, owners change, corrective actions remain open, excluded-user tests fail, or assumptions drift beyond their signposts.

## Cube rule

The field `resilience_assurance_case` is the maturity capstone. Blank means the cube may contain many useful signals, but it has not yet assembled them into an inspectable case.

---
Citations point to `sources/register.md`.
