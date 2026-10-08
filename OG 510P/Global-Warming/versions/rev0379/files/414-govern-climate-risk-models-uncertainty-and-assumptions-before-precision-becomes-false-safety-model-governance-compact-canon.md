---
id: '414'
revision_added: rev0283
status: canon
object_type: integrity_gate
domain_tags:
- model_governance
- climate_risk_assessment
- uncertainty
- data_quality
- design_values
service_floor:
- climate_model_governance
- assumption_ledger
- uncertainty_disclosure_before_design
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
- climate_service_provider
- engineer
- planner
- risk_modeler
- finance_officer
- regulator
- community_monitor
instrument_tags:
- model_inventory
- assumption_register
- scenario_set
- uncertainty_band
- data_quality_grade
- peer_review
- exception_note
routes_to:
- '110'
- '356'
- '366'
- '371'
- '407'
- '412'
- '413'
- '416'
- '420'
source_ids:
- S270
- S733
- S734
- S743
- S744
- S748
upstream_dependencies:
- observations
- remote_sensing
- hazard_maps
- future_condition_standards
- telemetry
- community_reports
- professional_review
downstream_consequences:
- design_failure
- hidden_residual_risk
- financial_repricing
- legal_dispute
- public_mistrust
equity_lenses:
- communities_outside_model_resolution
- informal_settlements
- tribal_data_sovereignty
- non_English_speakers
- renters
- small_utilities
degraded_modes:
- conservative_default
- range_based_design
- adaptive_trigger
- human_review_panel
- public_uncertainty_note
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- black_box_vendor_model
- historical_baseline_only
- precision_without_uncertainty
- assumptions_not_versioned
- model_output_not_ground_truthed
failure_modes:
- false_safety
- overconfidence
- mispriced_risk
- bad_design_value
- invisible_equity_harm
- uncontestable_decision
proof_ledgers:
- model_inventory
- assumption_ledger
- scenario_version_log
- uncertainty_statement
- model_validation_record
- local_observation_crosswalk
climate_model_governance: model has owner, version, assumptions, scenarios, uncertainty range, validation, and public
  exception process
---

# 414 — Govern climate-risk models, uncertainty, and assumptions before precision becomes false safety

## Core claim

Climate-risk models should make uncertainty governable, not hide it. A precise-looking flood depth, heat projection, wind map, asset-loss curve, or financial stress result can be more dangerous than a visibly uncertain range if decision makers treat the number as a guarantee.

ISO 14090 frames adaptation as an organizational process for integrating climate impacts and uncertainties into decisions [S743]. ISO 14091 gives guidelines for present and future climate-risk assessment, vulnerability, impacts, and risk [S744]. NOAA, NIST, and infrastructure-standard materials already push the archive toward future-condition design values [S733][S734]. TCFD and NGFS scenario materials make the same point for balance sheets: climate risk needs forward-looking scenarios, not only historical loss records [S748][S270].

## Model-governance packet

A model used for a climate-relevant decision should carry:

- decision being supported;
- model owner and reviewer;
- version and date;
- input data and spatial / temporal resolution;
- baseline period and future scenario set;
- design life or financial horizon;
- uncertainty range;
- calibration and ground-truth check;
- local knowledge or field-observation crosswalk;
- equity and exclusion note;
- public explanation of residual uncertainty.

## Anti-black-box rule

No model should receive more authority than its assumptions can bear. Proprietary or expert-only tools may inform decisions, but they should not extinguish contestability. Where the public cannot inspect the model, the owner must disclose assumptions, sensitivity tests, and the reason the model is fit for the decision.

## Cube rule

The field `climate_model_governance` marks whether a packet has a model inventory, assumption ledger, uncertainty statement, and validation route. Blank means model outputs may be treated as facts without provenance.

---
Citations point to `sources/register.md`.
