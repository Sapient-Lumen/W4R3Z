---
id: '400'
revision_added: rev0281
status: canon
object_type: service_continuity
domain_tags:
- livelihoods
- wage_replacement
- unemployment
- reemployment
- workers
- small_business
- informal_work
service_floor:
- livelihood_return
- income_continuity
- reemployment_access
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
- labor_agency
- unemployment_agency
- employer
- small_business_support
- case_manager
- workforce_board
- union_or_worker_center
- benefits_agency
instrument_tags:
- disaster_unemployment_assistance
- payroll_bridge
- wage_replacement
- reemployment_service
- worker_outreach
- informal_worker_cash
- retaliation_complaint
- job_transport
routes_to:
- '285'
- '286'
- '327'
- '353'
- '380'
- '394'
- '395'
- '398'
source_ids:
- S719
- S721
upstream_dependencies:
- employer_records
- benefit_application
- payment_rails
- childcare
- transport
- safe_worksite
- small_business_recovery
- identity_documents
downstream_consequences:
- debt
- eviction
- school_absence
- worker_injury
- business_closure
- migration_pressure
equity_lenses:
- informal_workers
- self_employed_workers
- gig_workers
- migrant_workers
- caregivers
- low_wage_workers
- small_business_employees
- workers_without_bank_accounts
degraded_modes:
- cash_bridge
- paper_wage_attestation
- worker_center_outreach
- mobile_claim_clinic
- temporary_job_transport
- unsafe_work_refusal_path
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- work_loss_not_registered_as_disaster_need
- informal_or_self_employed_workers_excluded
- payroll_stops_before_aid
- job_sites_reopen_unsafely
- childcare_and_transport_block_return_to_work
failure_modes:
- income_loss_drives_debt_eviction_and_medical_delay
- workers_return_to_unsafe_jobs
- small_firms_lose_staff
- informal_workers_become_invisible
proof_ledgers:
- wage_loss_roster
- DUA_claim_log
- payroll_bridge_log
- reemployment_referral
- unsafe_return_complaint
- informal_worker_outreach_log
livelihood_return_pathway: wage loss, self-employment interruption, payroll continuity, safe reemployment, childcare,
  transport, and worker remedies are tracked as recovery outcomes
---

# 400 — Connect wage replacement, unemployment, payroll, and reemployment before work loss becomes recovery failure

## Core claim

A household cannot recover if income does not. Climate recovery must therefore treat wage replacement, disaster unemployment, payroll continuity, safe work, reemployment, childcare, transport, and informal-worker outreach as a service floor rather than a side effect of economic recovery.

The U.S. Department of Labor describes Disaster Unemployment Assistance as help for people whose employment or self-employment is lost or interrupted as a direct result of a major disaster and who are not eligible for regular unemployment insurance [S719]. FEMA also lists Disaster Unemployment Assistance among recovery support programmes and includes other needs that intersect with work, such as childcare and transportation [S721]. The archive's addition is a pathway rule: income support must be connected to safe reemployment and household service floors, not only to individual claims.

## Livelihood-return packet

The packet should include:

- worker and self-employment loss intake;
- DUA / unemployment / cash referral;
- payroll bridge for essential and small-business workers where appropriate;
- safe return-to-work rules for heat, smoke, flood, cleanup, and contaminated sites;
- childcare and transport linkage;
- wage-theft, retaliation, and unsafe-work complaint routes;
- informal-worker and migrant-worker outreach;
- reemployment and training connection where jobs do not return.

## No unsafe return rule

Reemployment is not a recovery outcome if the worker must choose between income and unsafe exposure. Worksite safety, transport, care, and wage continuity are part of the livelihood floor.

## Cube rule

Worker, household-finance, and recovery packets should expose `livelihood_return_pathway`. Blank means the archive should assume income loss is hidden inside household debt, rent arrears, and delayed care.

---
Citations point to `sources/register.md`.
