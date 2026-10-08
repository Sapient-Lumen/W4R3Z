---
id: '425'
object_type: ledger
domain_tags:
- open_contracting
- public_procurement
- grants
- contractor_performance
- anti_corruption
- nuclear_open_contracting
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
service_floor:
- procurement_open_data_integrity
- delivery_transparency
- contractor_performance_ledger
hazard_tags:
- compound_hazard
- price_shock
clock_tags:
- finance_clock
- recovery_clock
- capital_clock
- learning_clock
actor_tags:
- procurement_officer
- grant_manager
- contractor
- auditor
- community_reviewer
- supplier
instrument_tags:
- open_contracting_data
- beneficial_ownership
- contract_milestone
- change_order_log
- invoice_check
- performance_scorecard
routes_to:
- '350'
- '351'
- '408'
- '418'
- '422'
- '424'
- '431'
- '437'
- '438'
- '440'
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
source_ids:
- S350
- S619
- S766
- S767
upstream_dependencies:
- procurement_integrity_rule
- reimbursement_cashflow
- open_data_platform
- internal_control_posture
downstream_consequences:
- market_confidence
- auditability
- faster_delivery
- reduced_extraction
- public_trust
equity_lenses:
- small_suppliers
- minority_owned_businesses
- local_businesses
- low_capacity_governments
- survivors_waiting_for_delivery
degraded_modes:
- emergency_contract_public_notice
- manual_award_log
- post_award_publication_with_deadline
evidence_grade: synthesis
speculation_level: low
revision_added: rev0284
status: canon
bottlenecks:
- emergency_procurement_opacity
- single_bidder_dependency
- subcontractor_invisible
- change_orders_unexplained
- invoice_without_delivery_proof
failure_modes:
- price_gouging
- substandard_delivery
- collusion
- delayed_rebuild
- public_money_lost
- service_floor_not_delivered
proof_ledgers:
- procurement_plan
- bidder_list
- award_notice
- contract_documents
- milestone_log
- invoice_payment_log
- change_order_register
- complaint_record
procurement_open_data_integrity: procurement and grant data expose needs, bids, awards, contracts, milestones, invoices,
  amendments, performance, complaints, and supplier integrity checks
---
# 425 — Publish procurement, grant, and contractor data before resilience spending becomes opaque

## Core claim

Resilience money does not become resilience until goods, works, services, repairs, grants, and maintenance are delivered. Opaque procurement converts climate urgency into extraction risk.

OECD's 2026 integrity outlook identifies post-award procurement risks including substandard delivery, collusion with supervising officials, and invoices for goods or services not supplied; it also links procurement integrity to public safety, trust, competition, and value for money [S766]. The Open Contracting Data Standard describes how to publish contracting data and documents for goods, works, and services in a common model that supports visualization, monitoring, analysis, transparency, integrity, value for money, and competition [S767]. The archive's earlier procurement and reimbursement packets already require emergency contracting and auditability; rev0284 adds the open-data layer [S350][S619].

## Open-contracting packet

A resilience procurement or grant ledger should expose, subject to lawful privacy/security limits:

- need and funding source;
- procurement method and emergency justification;
- bidders, noncompetition reason, or supplier-pool constraint;
- beneficial ownership and conflict checks;
- award, scope, price, and timeline;
- subcontractors where material;
- milestones, invoices, payments, and change orders;
- inspection and performance results;
- complaints, protests, remedies, and debarment flags.

## Anti-extraction rule

Emergency speed is not a waiver of public memory. Where publication must be delayed for safety, privacy, or security, the archive should require a delayed-disclosure clock and an independent audit trail.

## Cube rule

The field `procurement_open_data_integrity` asks whether money-to-delivery can be followed. Blank means the archive cannot tell whether resilience spending produced resilient service.

---
Citations point to `sources/register.md`.
