---
id: '422'
revision_added: rev0284
status: canon
object_type: integrity_gate
domain_tags:
- internal_control
- service_floor_assurance
- risk_management
- reporting_reliability
- nuclear_internal_control
- nuclear_energy
- nuclear_regulatory_legitimacy
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
- internal_control_posture
- reliable_service_floor_claim
- exception_and_correction_path
hazard_tags:
- compound_hazard
- outage
- cyber_disruption
clock_tags:
- learning_clock
- finance_clock
- emergency_clock
actor_tags:
- service_owner
- finance_owner
- auditor
- programme_manager
- data_product_owner
instrument_tags:
- control_object
- risk_register
- preventive_control
- detective_control
- exception_log
- management_review
routes_to:
- '356'
- '357'
- '365'
- '371'
- '421'
- '423'
- '428'
- '438'
- '439'
- '441'
- '443'
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
- '494'
- '498'
source_ids:
- S758
- S761
- S762
upstream_dependencies:
- owner_accountability
- data_product_status
- source_edge_table
- readiness_scoring
downstream_consequences:
- reliable_reporting
- less_false_maturity
- auditable_readiness
- corrective_action_trigger
equity_lenses:
- program_users
- excluded_users
- public_reviewers
- low_capacity_local_governments
degraded_modes:
- manual_control_log
- sampled_evidence_review
- temporary_exception_with_due_date
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- dashboard_not_tied_to_control_owner
- evidence_not_reconciled
- exceptions_are_informal
- controls_do_not_cover_operations
failure_modes:
- dashboard_green_but_service_fails
- unverified_readiness_claim
- manual_workaround_unseen
- audit_finding_repeats
proof_ledgers:
- control_matrix
- risk_control_self_assessment
- exception_log
- evidence_packet
- management_review_record
internal_control_posture: objective-risk-control-evidence-exception-correction packet
  required for material service-floor claims
---

# 422 — Treat service-floor claims as internal-control objects before dashboards become unmanaged representations

## Core claim

A service-floor dashboard is a representation, not a control. It becomes trustworthy only when every material claim has an objective, risk, owner, control, evidence source, exception path, and correction loop.

GAO's 2025 Green Book sets standards for effective internal control and frames internal control as a process used by management to achieve objectives, run operations effectively, report reliable information, and comply with law [S761]. OMB Circular A-123 similarly requires governance structures, risk evaluation, internal-control evaluation, and targeted reviews of operational areas when needed for reasonable assurance over compliance, operations, or reporting [S762]. PROV-O supplies the provenance logic needed to connect a visible claim to the activity and evidence that produced it [S758].

## Control packet

A service-floor claim should carry:

- protected objective;
- operational risk;
- control owner and backup owner;
- preventive control;
- detective control;
- evidence source and refresh rule;
- exception threshold;
- escalation owner;
- corrective action and retest requirement.

## Dashboard rule

Dashboards should not show maturity without also showing stale evidence, exceptions, owner gaps, manual overrides, and unresolved corrective actions. A green status without a control packet is a user-interface decoration.

## Cube rule

The field `internal_control_posture` tests whether the claim is governed as a control object. Blank means the cube may describe readiness without proving management control.

---
Citations point to `sources/register.md`.
