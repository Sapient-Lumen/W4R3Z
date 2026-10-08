---
id: '480'
title: 480 — Nuclear incident compensation, recovery fund, and claims-access assurance
object_type: integrity_gate
domain_tags:
- nuclear_energy
- incident_compensation
- emergency_recovery
- claims_access
- civil_rights
- public_health_monitoring
service_floor:
- nuclear_incident_compensation_claims_process
- nuclear_emergency_recovery_fund
- nuclear_public_health_monitoring_after_incident
- nuclear_evacuation_compensation_and_housing_support
- nuclear_damage_claims_public_docket
- nuclear_compensation_equity_access
- nuclear_emergency_worker_compensation
hazard_tags:
- claims_access_failure
- post_incident_displacement
- health_monitoring_gap
- compensation_delay
- language_access_failure
- emergency_worker_compensation_gap
clock_tags:
- first_72_hours_claims_intake
- first_30_days_recovery_payment
- annual_claims_access_exercise
- post_incident_public_health_monitoring_cycle
actor_tags:
- A_emergency_management_agency
- A_public_health_agency
- A_civil_rights_office
- A_nuclear_operator
- A_public_auditor
- A_host_community_reviewer
instrument_tags:
- claims_intake_pathway
- recovery_fund_trigger
- public_health_registry
- language_access_claims_protocol
- emergency_worker_compensation_rule
routes_to:
- '00'
- '01'
- '02'
- '04'
- '05'
- '327'
- '328'
- '329'
- '331'
- '332'
- '338'
- '339'
- '421'
- '423'
- '426'
- '428'
- '430'
- '442'
- '447'
- '479'
- '481'
- '482'
- '483'
source_ids:
- S876
- S877
- S882
- S883
- S884
- S885
- S886
upstream_dependencies:
- civil_rights_language_access_gate
- emergency_preparedness_modernization
- nuclear_liability_financial_protection
downstream_consequences:
- compensation_access_becomes_a_maturity_gate
- emergency_recovery_funding_is_publicly_challengeable
- claims_process_is_tested_for_excluded_users
equity_lenses:
- language_access
- disability_access
- renter_and_worker_compensation
- carless_evacuee_support
- low_income_household_liquidity
degraded_modes:
- paper_compensation_without_cashflow
- legal_claims_bottleneck
- health_monitoring_without_followup
- claimants_without_language_or_disability_access
evidence_grade: mixed
speculation_level: medium
revision_added: rev0299
status: canon
---

# 480 — Nuclear incident compensation, recovery fund, and claims-access assurance

## Audit function

This file converts nuclear incident response from an emergency-planning statement into a compensation and recovery proof layer. It asks whether displaced residents, workers, renters, businesses, public agencies, and emergency responders can actually access claims, health monitoring, housing support, and recovery cashflow.

## Nuclear-positive rule

Nuclear remains preferred where it lowers fossil and reliability harm. That preference is not a reason to ignore low-probability/high-consequence events. Rev0299 therefore treats claims access, public-health monitoring, emergency-worker compensation, and recovery-fund triggers as maturity gates.

## Refactor output

This file introduces `cube/nuclear-incident-compensation-claims.csv`, `cube/nuclear-cleanup-recovery-funding.csv`, and compensation/access rows in the nuclear liability backlog and traceability matrix.

## Sources

- [S876]
- [S877]
- [S882]
- [S883]
- [S884]
- [S885]
- [S886]
