---
id: '398'
revision_added: rev0281
status: canon
object_type: shock_absorber
domain_tags:
- household_finance
- debt
- credit
- forbearance
- consumer_protection
- insurance
- mortgage
- rent
service_floor:
- household_balance_sheet_repair
- credit_damage_prevention
- debt_standstill_and_forbearance
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- smoke
- storm
- outage
- displacement
- disease
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- legal_clock
- learning_clock
actor_tags:
- consumer_finance_regulator
- benefits_agency
- case_manager
- lender_or_servicer
- credit_furnisher
- insurer
- legal_aid
- community_lender
instrument_tags:
- forbearance
- credit_reporting_code
- debt_collection_pause
- insurance_advance
- emergency_cash
- appeal
- financial_counseling
- consumer_complaint
routes_to:
- '289'
- '290'
- '325'
- '343'
- '380'
- '394'
- '395'
- '396'
source_ids:
- S717
- S718
- S721
upstream_dependencies:
- payment_rails
- benefit_sequencing
- case_management
- legal_help
- lender_contact
- insurance_claim
- identity_documents
downstream_consequences:
- eviction
- foreclosure
- repossession
- credit_score_damage
- benefit_clawback
- predatory_finance
- delayed_repair
equity_lenses:
- renters
- homeowners_with_mortgages
- unbanked_households
- informal_workers
- small_business_owners
- older_adults
- limited_english_households
- mixed_status_households
degraded_modes:
- cash_or_voucher_bridge
- paper_servicer_contact
- community_financial_counselor
- temporary_debt_standstill
- manual_credit_correction
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- creditors_act_faster_than_aid
- survivor_cannot_reach_servicer
- debt_collection_resumes_before_benefits
- natural_disaster_code_not_used
- insurance_and_aid_sequences_are_unclear
failure_modes:
- missed_payments_become_credit_damage
- household_uses_high_cost_debt_to_bridge_aid_delay
- asset_sale_or_vehicle_loss_blocks_recovery
- debt_collection_undoes_public_assistance
proof_ledgers:
- credit_disaster_code_log
- forbearance_offer_log
- debt_collection_hold_log
- insurance_advance_log
- complaint_and_resolution_log
- financial_stabilization_plan
household_balance_sheet_repair: forbearance, credit protection, debt collection holds, insurance advances, emergency
  cash, and complaint routes are sequenced before aid delay becomes permanent financial damage
---

# 398 — Repair household balance sheets, credit, debt, and forbearance before disaster aid becomes asset loss

## Core claim

A climate shock is also a balance-sheet shock. Food spoils, work stops, rent is due, loans continue, credit cards bridge the gap, cars are damaged, utilities accrue arrears, insurance is slow, and public aid arrives in programme fragments. Without a household balance-sheet rail, disaster assistance can stabilize the event while leaving the household poorer, more indebted, or excluded from future housing and credit.

CFPB's disaster guidance tells survivors to contact lenders and notes that lenders can add natural-disaster codes to credit reports so delayed or missed payment context is visible [S717]. CFPB also routes survivors to insurance, mortgage servicers, lenders, and record-protection steps after a disaster [S718]. FEMA's individual assistance may cover certain housing, personal property, transportation, medical, dental, funeral, childcare, and other needs, but those categories do not automatically repair credit or stop collection pressure [S721].

## Balance-sheet packet

A serious packet should include:

- immediate cash or benefit bridge;
- forbearance and payment-plan pathways;
- credit-furnishing disaster codes or correction routes;
- debt-collection pause / complaint routes;
- insurance advance and claim-status tracking;
- utility-arrears and reconnection protection;
- legal-aid referral for foreclosure, eviction, repossession, garnishment, or debt collection;
- financial-counseling and fraud-protection access.

## Anti-asset-loss rule

Public recovery should not force households to sell cars, tools, devices, livestock, land, or durable possessions before aid arrives. Asset liquidation is often a hidden maladaptation: it creates future vulnerability while making current need look smaller.

## Cube rule

All household-facing recovery packets should expose `household_balance_sheet_repair`. Blank means the archive should assume cash, debt, credit, and asset loss are not governed as recovery outcomes.

---
Citations point to `sources/register.md`.
