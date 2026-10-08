---
id: '420'
revision_added: rev0283
status: canon
object_type: integrity_gate
domain_tags:
- professional_duty
- standard_of_care
- engineering
- planning
- climate_design
- certification
service_floor:
- professional_duty_standard
- climate_informed_review
- duty_to_disclose_residual_risk
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- storm
- drought
- sea_level
- smoke
clock_tags:
- capital_clock
- standards_clock
- land_use_clock
- learning_clock
- recovery_clock
actor_tags:
- engineer
- architect
- planner
- asset_owner
- regulator
- code_official
- insurer
- professional_board
- procurement_officer
instrument_tags:
- climate_informed_scope
- professional_attestation
- residual_risk_disclosure
- peer_review
- design_standard_exception
- competence_requirement
routes_to:
- '108'
- '352'
- '407'
- '414'
- '417'
- '418'
source_ids:
- S734
- S735
- S743
- S744
- S750
- S751
upstream_dependencies:
- model_governance
- future_hazard_mapping
- code_upgrade_state
- asset_portfolio_stress_test
- resilience_service_level_contract
downstream_consequences:
- unsafe_design
- disputed_standard_of_care
- hidden_residual_risk
- delayed_codes
- false_compliance
equity_lenses:
- small_clients
- low_capacity_local_governments
- renters
- future_users
- tribal_governments
- public_school_students
degraded_modes:
- climate_review_appendix
- conservative_default
- peer_review_panel
- owner_acknowledgment_of_residual_risk
- scope_escalation_notice
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- historical_code_minimum_treated_as_safe
- client_scope_excludes_future_risk
- professional_cannot_access_climate_data
- residual_risk_not_disclosed
- liability_fear_suppresses_adaptation_advice
failure_modes:
- underdesigned_asset
- professional_blind_spot
- uninsured_claim
- unsafe_occupancy
- litigation_after_failure
- public_mistrust
proof_ledgers:
- scope_of_services
- climate_design_basis
- professional_attestation
- residual_risk_note
- peer_review_record
- exception_register
professional_duty_standard: professional scope names climate data, future conditions, residual-risk disclosure,
  competence, peer review, and exception handling
---

# 420 — Make climate-informed professional duty explicit before standards of care lag physical risk

## Core claim

Climate-informed design cannot wait for every code, map, procurement template, and professional norm to update perfectly. A professional duty layer is needed so engineers, architects, planners, asset managers, auditors, and public officials know when historical data and minimum code compliance are no longer enough for the service life and risk profile of the asset.

ASCE's climate-change policy statement calls for policies that anticipate climate impacts and for revising engineering design standards, codes, regulations, and laws to strengthen infrastructure resilience [S750]. Professional commentary on climate and the engineering standard of care emphasizes that historical climate assumptions may not remain adequate for project design life under changing conditions [S751]. NIST, ASCE, and ISO adaptation-risk materials support the same operating rule: future conditions, impacts, vulnerability, uncertainty, and decision relevance must enter professional practice [S734][S735][S743][S744].

## Duty packet

A climate-informed professional scope should state:

- design life or decision horizon;
- climate data and future-condition assumptions;
- hazards considered and excluded;
- residual risk disclosed to owner and users;
- code minimum versus risk-informed recommendation;
- competence, peer review, or specialist input required;
- exception language when the owner rejects climate-informed advice;
- public-interest trigger when rejection creates material safety risk.

## Compliance-is-not-safety rule

Code compliance is a floor, not a guarantee that the asset is safe for future conditions. Where physical risk is visibly changing, the archive should expect professional judgment to explain why historical minima remain adequate or why a higher standard is required.

## Cube rule

The field `professional_duty_standard` tests whether climate-informed responsibility is explicit. Blank means professional practice may be lagging physical reality.

---
Citations point to `sources/register.md`.
