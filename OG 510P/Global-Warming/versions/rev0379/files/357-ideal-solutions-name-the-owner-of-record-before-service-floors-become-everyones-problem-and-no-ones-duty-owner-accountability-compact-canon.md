---
id: '357'
revision_added: rev0276
status: canon
object_type: governance_packet
domain_tags:
- owner_accountability
- continuity
- service_floor
- RACI
- decision_rights
- records
- public_authority
service_floor:
- owner_of_record
- decision_owner
- ledger_owner
- finance_owner
- public_redress_owner
hazard_tags:
- all_hazards
- compound_hazard
- outage
- displacement
- records_loss
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
- finance_clock
actor_tags:
- executive_owner
- operational_owner
- finance_owner
- data_steward
- civil_rights_owner
- public_information_officer
- community_feedback_body
instrument_tags:
- assign
- delegate
- publish
- escalate
- appeal
- audit
- continuity_plan
- succession
routes_to:
- '105'
- '106'
- '107'
- '121'
- '301'
- '315'
- '322'
- '331'
- '351'
- '356'
- '438'
source_ids:
- S637
- S639
upstream_dependencies:
- legal_authority
- budget_authority
- continuity_plan
- succession_order
- records_system
- public_notice_channel
- data_sharing_rule
downstream_consequences:
- unowned_correction
- late_repair
- conflicting_orders
- unappealable_denial
- paper_continuity
- loss_of_public_trust
equity_lenses:
- users_without_political_visibility
- private_tenants
- tribal_governments
- rural_communities
- disabled_people
- limited_english_speakers
- informal_settlement_residents
degraded_modes:
- backup_owner
- manual_roster
- mutual_aid_owner_substitution
- public_exception_notice
- temporary_delegation_order
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- diffuse_responsibility
- owner_without_budget
- operator_without_decision_rights
- private_asset_public_consequence
- vacant_position
- succession_gap
failure_modes:
- service_floor_is_everyones_problem
- after_action_finds_no_corrective_owner
- dashboard_exists_without_budget_authority
- private_operator_controls_public_floor_without_redress
- owner_changes_and_ledger_breaks
proof_ledgers:
- owner_of_record_table
- decision_rights_map
- succession_roster
- delegation_order
- contact_and_backup_roster
- public_redress_log
- correction_budget_register
restoration_conflicts:
- political_owner_vs_operational_owner
- public_interest_vs_private_asset_control
- privacy_steward_vs_coordination_need
- finance_owner_vs_service_owner
assurance_tests:
- owner_contact_drill
- decision_escalation_drill
- succession_tabletop
- private_operator_failure_test
- appeal_path_test
owner_accountability: executive_owner_operational_owner_ledger_owner_finance_owner_and_redress_owner_must_be_named
---
# 357 — Ideal Solutions: Name the owner of record before service floors become everyone's problem and no one's duty

## Claim

A service floor with no owner of record is an aspiration. A service floor with an owner but no budget, authority, succession, ledger, or appeal path is still fragile.

FEMA's continuity guidance is built around maintaining essential functions when normal operations are disrupted [S639]. The National Resilience Guidance likewise treats resilience as a coordinated whole-community responsibility, not a slogan assigned to an emergency office after failure [S637].

House rule: **every service floor needs an owner of record, and every owner of record needs decision rights, money path, backup, public ledger, and redress path.**

## Fast rule

Do not ask only, "Who is responsible?" Ask six questions:

1. Who owns the service consequence?
2. Who can order action during degraded operations?
3. Who owns the ledger that proves action?
4. Who controls or unlocks money?
5. Who receives complaints and appeals?
6. Who takes over if the first owner is unavailable?

## The compact canon

### 1. Split ownership roles explicitly

The executive owner sets the obligation. The operational owner executes. The finance owner pays or reimburses. The records owner preserves proof. The privacy or civil-rights owner prevents harmful access practices. The redress owner handles denial, complaint, and appeal.

Putting all roles in one box hides failure. Splitting them without escalation rules creates paralysis. The cube should show both assignment and collision rules.

### 2. Private control does not erase public consequence

Telecoms, pharmacies, supermarkets, payment agents, apartment buildings, fuel distributors, insurers, contractors, cloud platforms, warehouses, and utilities may be privately owned. Their failure can still collapse public service floors. The owner table should distinguish asset ownership from service-consequence accountability.

### 3. Succession is part of readiness

The named owner may evacuate, lose power, lose family care, resign, become ill, or be unreachable. Owner records need backup names, authority triggers, contact modes, and delegated powers.

### 4. Ownership must be visible enough to challenge

People should know where to report a blocked shelter, failed generator, inaccessible bus, denied repair grant, unsafe contractor, missing interpreter, mold clearance dispute, or payment failure. If the owner table is secret, redress becomes luck.

### 5. A correction without an owner is not a correction

After-action reports often say "improve coordination" or "strengthen communications." The cube should reject that language unless the correction has an owner, deadline, funding path, and retest.

## Minimum packet

An owner-accountability packet includes: service floor; owner of record; statutory or contractual basis; operational lead; finance lead; records lead; privacy / civil-rights lead; community liaison; backup owner; escalation trigger; public contact; complaint path; and after-action correction owner.

## Bottom line

The datacube should make responsibility concrete. A floor is not operational until somebody can be named, reached, funded, challenged, replaced, and audited.

---
Citations point to `sources/register.md`.
