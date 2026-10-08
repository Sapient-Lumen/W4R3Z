---
id: '325'
revision_added: rev0272
status: canon
object_type: service_continuity
domain_tags:
- insurance
- disaster_assistance
- claims
- loss_proof
- recovery_cashflow
- consumer_protection
- redress
service_floor:
- claims_and_assistance_continuity
- loss_proof_portability
- fair_recovery_cashflow
- appeals_access
hazard_tags:
- flood
- wildfire
- storm
- heat
- smoke
- displacement
- outage
- cyber
- compound_shock
clock_tags:
- emergency_clock
- recovery_clock
- finance_clock
- learning_clock
actor_tags:
- insurer
- insurance_regulator
- fema_or_disaster_agency
- bank
- legal_aid
- adjuster
- ombuds
- community_intermediary
- household
instrument_tags:
- claim
- appeal
- pause
- advance
- verify
- inspect
- substitute_documents
- redress
- audit
- protect
routes_to:
- '254'
- '255'
- '256'
- '257'
- '258'
- '289'
- '290'
- '291'
- '292'
- '318'
- '322'
source_ids:
- S580
- S581
- S582
- S584
upstream_dependencies:
- identity
- address_records
- property_records
- photos
- bank_or_cash_route
- inspectors
- adjusters
- telecoms
- legal_help
- payment_rails
downstream_consequences:
- delayed_repair
- debt_spiral
- eviction
- business_closure
- uninsured_loss
- fraud_loss
- mental_distress
- retreat_without_choice
equity_lenses:
- renters
- low_income_owners
- informal_residents
- migrants
- limited_english_speakers
- disabled_people
- older_adults
- people_without_bank_accounts
- small_businesses
degraded_modes:
- paper_claim_intake
- mobile_claim_desk
- document_substitution
- partial_advance
- community_casework
- cash_or_check_payment
- ombuds_escalation
- deadline_pause
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- documentation_loss
- adjuster_shortage
- portal_outage
- coverage_gap
- underinsurance
- claim_delay
- fraud_filter_error
- language_access
- bank_account_gap
- appeal_backlog
failure_modes:
- insured_but_unpaid
- eligible_but_unregistered
- advance_becomes_final_underpayment
- smoke_or_mold_denial
- renter_costs_invisible
- proof_maze
- fraud_controls_exclude
- duplicate_claim_confusion
proof_ledgers:
- claim_intake_log
- adjuster_assignment_log
- advance_payment_log
- denial_reason_register
- appeal_cycle_time_log
- document_substitution_log
- complaint_and_correction_log
- equity_claims_audit
restoration_conflicts:
- fast_advance_vs_complete_assessment
- fraud_control_vs_access
- insurer_solvency_vs_survivor_cashflow
- privacy_vs_case_coordination
assurance_tests:
- offline_claim_intake_drill
- document_loss_case_test
- limited_english_claim_path_test
- adjuster_surge_stress_test
- appeal_and_ombuds_audit
---

# 325 — Ideal Solutions: Make insurance, disaster assistance, loss proof, and claims handling a recovery service floor

## Claim

Protection gaps are not only about whether someone had insurance before a shock. They are also about whether claims, disaster assistance, advances, inspections, appeals, payments, and document-substitution routes work after the shock.

NAIC frames insurance commissioners as front-line disaster actors responsible for fair and fast claims payment and fraud protection [S580]. DisasterAssistance.gov is a central public doorway for FEMA assistance and recovery resources [S581]. CBO documents the policy problem created by climate-driven disaster risk and stressed property-insurance markets [S582]. The archive should therefore treat **claims handling as recovery infrastructure**, not as a private administrative afterthought.

House rule: **a household, tenant, farm, or small business is not financially protected until loss proof can become spendable recovery money with appeal and correction rights.**

## Fast rule

**Every recovery-cashflow packet must prove intake, document substitution, inspection, advance payment, denial reason, appeal, fraud protection, and payment access under outage and displacement.**

## The compact canon

### 1. Separate coverage from claims continuity

A policy, grant, or loan promise does not equal recovery. Claims continuity asks: can the person apply, prove loss, get inspected, receive an advance, understand exclusions, appeal, and access payment when records, phones, homes, mail, bank accounts, and transport are disrupted?

### 2. Design for lost proof

Climate shocks destroy leases, IDs, titles, receipts, photos, medical records, wage records, school records, and business books. The claim floor needs document-substitution standards, attestations, trusted intermediaries, mobile desks, language access, and audit trails that prevent both exclusion and fraud.

### 3. Make adjuster capacity visible

Claims fail when adjusters, inspectors, engineers, mold assessors, translators, and appeal officers are overwhelmed. Regulators should track assignment times, revisits, denial reasons, complaint themes, re-opened claims, appeal reversals, and whether temporary advances were later treated as ceilings.

### 4. Protect renters, informal residents, and small businesses

Standard property claims often privilege owners and structures. Service-floor claims should also see hotel costs, lost contents, childcare disruption, tools, medical equipment, smoke/mold exposure, business interruption, payroll, inventory, landlord delay, utility reconnection, and relocation costs.

### 5. Pair fraud control with remedy

Fraud controls are necessary, especially after disasters. But false positives can also block recovery. The integrity stack should include explainable flags, human review, rapid correction, ombuds escalation, legal-help routing, and public reporting of delay and denial patterns [S584].

## Minimum readiness ledger

| Test | Minimum evidence | Failure signal |
|---|---|---|
| intake access | online, phone, paper, mobile, community, and language-access paths | eligible people never enter the system |
| loss proof | substitute documents, photos, attestations, inspection, title/lease alternatives | proof maze excludes people hit hardest |
| cashflow | advance, partial payment, check/cash route, payment-rail fallback | approved money cannot be spent or arrives too late |
| redress | denial reasons, appeal times, complaint themes, regulator action | underpayment becomes final by exhaustion |

## Bottom line

Claims continuity is a public service floor because delayed, denied, or inaccessible recovery money becomes homelessness, debt, unsafe repair, business closure, and involuntary retreat. The cube should treat claims as infrastructure.

---
Citations point to `sources/register.md`.
