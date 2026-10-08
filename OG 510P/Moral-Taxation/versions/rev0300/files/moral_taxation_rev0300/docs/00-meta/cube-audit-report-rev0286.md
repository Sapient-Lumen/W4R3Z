# Rev0286 cube audit report

## What was audited

Rev0286 audits the datacube records themselves, not only the surrounding prose. The audit examined required-axis coverage, semantic leakage of AI/preparer values, route-family assignment, source-currentness references, and whether blank axes were hiding classification uncertainty.

## Findings

1. **Semantic leakage found and repaired.** `ai_tax_advice`, `model_output`, and taxpayer-side-AI source logic had leaked into unrelated calibration records. Rev0286 removes those values from non-AI families and makes the contamination rule executable.
2. **Frontier-AI and agency-side model administration were separated from taxpayer-side AI advice.** `frontier_ai_host_market_controller_jurisdiction` now uses `frontier_ai_compute`, while model-assisted administration records use `model_assisted_administration`; only the taxpayer-side AI/preparer route uses `ai_tax_advice`.
3. **Silent blanks are now explicit sentinels.** Every route record now carries all 23 required axes. Where a dimension is not applicable or not yet route-specific, the record uses explicit sentinel values such as `not_market_specific`, `not_channel_specific`, `not_remedy_specific`, or `incidence_uncertain`.
4. **Routes now have families.** Each record now has a `family` field so future audits can compare the semantic content of axes against the route's editorial home.
5. **The checker now fails on cube-shape drift.** Missing required axes, missing `family`, non-compact audit schema, and AI-axis contamination are release blockers.

## Family counts

| Family | Records |
|---|---:|
| controller_ai | 21 |
| cross_border_reporting | 6 |
| environment_climate_commons | 10 |
| financial_system_risk | 8 |
| labor_care_benefits | 11 |
| legal_enforcement_penalty | 11 |
| public_finance_core | 41 |
| public_procurement_industrial_policy | 5 |
| regulated_networks_platforms | 4 |
| release_integrity_currentness | 3 |
| social_floor_public_services | 8 |
| tax_administration_access | 17 |
| wealth_property_rent | 6 |

## Known records cleaned in the AI-axis pass

- `beneficial_ownership_and_controller_chain`
- `beneficiary_home_market_and_local_burden_claim_split`
- `charitable_public_benefit_transfer_and_retained_surplus`
- `collection_anchor_choice_and_remittance_chain`
- `creditor_distress_netting_and_retained_surplus`
- `customer_benefit_price_access_and_retained_surplus`
- `failure_waterfall_and_ex_ante_security`
- `insurance_policyholder_benefit_and_retained_surplus`
- `international_coordination_claim_split`
- `land_site_rent_netting_and_retained_surplus`
- `mandatory_private_tax_rail_and_bankless_fallback`
- `public_service_member_relief_and_local_repair`
- `regressivity_repair_channel_and_delivery_sync`
- `reinvestment_prefunding_ring_fence_and_retained_surplus`
- `status_proxy_disparate_impact_and_accessibility_repair`
- `supplier_benefit_net_terms_and_retained_surplus`
- `worker_benefit_pay_hours_member_share_and_local_repair`

## Remaining contamination

`[]`

## Editorial rule going forward

A cube record should be allowed to say `not_applicable` or `incidence_uncertain`, but it should not be allowed to say nothing. Blanks made Rev0285 look cleaner than it was; Rev0286 treats explicit uncertainty as better than invisible drift.
