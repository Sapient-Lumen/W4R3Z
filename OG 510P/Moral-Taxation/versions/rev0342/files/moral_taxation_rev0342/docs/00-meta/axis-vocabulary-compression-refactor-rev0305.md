# Axis vocabulary compression refactor — rev0305

Rev0305 is the second compression pass after placeholder extinction and sentinel extinction. Rev0304 compressed `anti_pattern` and `review_trigger`; this pass targets the more semantically dangerous axes that still made the cube hard to query: `base`, `instrument`, and `proof_posture`.

## Why this was risky

These axes carried the archive's largest singleton load after Rev0304. Many values were route-local spellings of the same reusable concept: a tax/fee/assessment, a credit/subsidy/exemption, a reporting/attestation rule, a cross-border record gap, a valuation/fiscal projection gap, a public-service access record, or a source/manifest regression record.

## What changed

| Axis | Unique before | Unique after | Singletons before | Singletons after |
|---|---:|---:|---:|---:|
| `base` | 356 | 20 | 299 | 0 |
| `instrument` | 344 | 21 | 266 | 0 |
| `proof_posture` | 244 | 29 | 189 | 0 |

Live-route buckets now include:

- `public_finance_design_or_capacity_base`, `tax_administration_access_base`, `cross_border_claim_or_coordination_base`, `environment_climate_or_commons_base`, `labor_care_or_benefit_floor_base`, and `release_integrity_or_currentness_base`;
- `charge_tax_fee_or_assessment`, `credit_rebate_subsidy_or_exemption`, `classification_routing_or_formula_rule`, `public_option_or_fallback_channel`, and `penalty_clawback_or_coercive_collection`;
- `valuation_price_or_fiscal_projection_gap`, `status_authority_or_liability_contested`, `incidence_or_benefit_trace_record`, `foreign_or_cross_border_record_gap`, and `source_manifest_or_regression_record`.

## Guardrail

This is a live-cube compression pass, not a deletion of nuance. Case contracts keep sharper scenario terms where a regression needs them; route memos keep narrative detail. The cube now provides the reusable query surface.
