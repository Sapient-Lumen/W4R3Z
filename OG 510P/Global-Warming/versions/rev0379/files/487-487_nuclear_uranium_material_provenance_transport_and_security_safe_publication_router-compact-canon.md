---
id: '487'
title: Nuclear uranium material provenance, transport, and security-safe publication
  router
object_type: router
domain_tags:
- nuclear_energy
- uranium_transport
- material_provenance
- security_safe_publication
- chain_of_custody
- sensitive_publication
service_floor:
- nuclear_uranium_transport_ore_concentrate
- nuclear_uranium_mine_milling_security_publication_boundary
hazard_tags:
- ore_transport_notice_failure
- security_sensitive_route_disclosure
- chain_of_custody_break
- material_accountability_gap
clock_tags:
- transport_plan_review_before_shipment
- chain_of_custody_reconciliation_cycle
- publication_control_pre_release_review
actor_tags:
- A_transport_authority
- A_mining_regulator
- A_nuclear_security_authority
- A_fuel_supplier
- A_public_auditor
- A_host_community_reviewer
instrument_tags:
- transport_notice_protocol
- material_chain_of_custody
- security_redaction_boundary
- public_summary_withheld_details
routes_to:
- '00'
- '03'
- '05'
- '441'
- '459'
- '462'
- '472'
- '484'
- '485'
- '486'
- '488'
source_ids:
- S890
- S893
- S894
- S895
- S898
- S900
upstream_dependencies:
- mine_source_record
- ore_or_yellowcake_transport_plan
- security_redaction_rule
- community_notice_protocol
downstream_consequences:
- uranium_provenance_becomes_audit_visible_without_exposing_routes_or_security_controls
- transport_and_security_publication_boundary_coded_as_maturity_gate
equity_lenses:
- route_community_notice
- tribal_government_notification
- worker_transport_safety
- public_right_to_know_with_security_redaction
degraded_modes:
- publication_overredaction
- route_disclosure_security_risk
- transport_without_notice
- source_substitution_without_chain_of_custody
evidence_grade: mixed
speculation_level: medium
revision_added: rev0300
status: canon
---

# 487 — Nuclear uranium material provenance, transport, and security-safe publication router

## Router rule

Responsible nuclear supply requires material provenance and transport accountability, but public transparency must not disclose exact route, timing, package, security, or vulnerability details that would increase risk.

## Control output

The cube adds chain-of-custody, community notice, transport-safety, security-redaction, and material-accountability proof surfaces for upstream uranium movement.

## Maturity cap

Nuclear fuel supply claims are capped if they cannot demonstrate provenance and safe transport governance, or if their public artifacts either hide material facts or disclose security-sensitive details.

## Sources

- [S890]
- [S893]
- [S894]
- [S895]
- [S898]
- [S900]
