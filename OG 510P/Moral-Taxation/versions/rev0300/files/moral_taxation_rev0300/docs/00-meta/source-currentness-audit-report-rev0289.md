# Rev0289 source-currentness audit report

## Registry-to-route use

| Source | Route records tracking it |
|---|---|
| S15 | `data_center_local_burden`, `frontier_ai_host_market_controller_jurisdiction`, `frontier_scarce_capacity_threshold` |
| S443 | `mandatory_private_tax_rail_and_bankless_fallback`, `public_filing_refund_floor` |
| S444 | `mandatory_private_tax_rail_and_bankless_fallback`, `public_filing_refund_floor` |
| S462 | `customs_tariff_carbon_border` |
| S463 | `customs_tariff_carbon_border` |
| S498 | `labor_tax_wedge_classification_social_insurance`, `platform_worker_portable_benefits_classification_fringe` |
| S526 | `beneficial_ownership_registry_privacy_small_entity` |
| S527 | `beneficial_ownership_registry_privacy_small_entity` |
| S594 | `release_integrity_source_bijection_regression_harness` |
| S632 | `telecom_universal_service_broadband_affordability_surcharge` |
| S633 | `telecom_universal_service_broadband_affordability_surcharge` |
| S635 | `gambling_prediction_markets_event_contracts_addiction` |
| S636 | `media_attention_digital_advertising_tax_speech_transparency` |
| S637 | `media_attention_digital_advertising_tax_speech_transparency` |
| S638 | `cumulative_burden_environmental_justice_siting_tax` |
| S639 | `cumulative_burden_environmental_justice_siting_tax` |
| S640 | `cumulative_burden_environmental_justice_siting_tax` |
| S641 | `platform_worker_portable_benefits_classification_fringe` |
| S645 | `release_integrity_source_bijection_regression_harness` |
| S646 | `release_integrity_source_bijection_regression_harness` |
| S647 | `telecom_universal_service_broadband_affordability_surcharge` |
| S648 | `mandatory_private_tax_rail_and_bankless_fallback` |
| S649 | `media_attention_digital_advertising_tax_speech_transparency` |
| S650 | `insurance_reinsurance_protection_gap_public_backstop` |
| S651 | `insurance_reinsurance_protection_gap_public_backstop` |
| S652 | `international_coordination_claim_split` |
| S653 | `telecom_universal_service_broadband_affordability_surcharge` |
| S654 | `taxpayer_side_ai_preparer_agent_reliance_and_liability` |
| S655 | `taxpayer_side_ai_preparer_agent_reliance_and_liability` |
| S656 | `taxpayer_side_ai_preparer_agent_reliance_and_liability` |
| S657 | `taxpayer_side_ai_preparer_agent_reliance_and_liability` |
| S658 | `taxpayer_side_ai_preparer_agent_reliance_and_liability` |
| S659 | `taxpayer_side_ai_preparer_agent_reliance_and_liability` |
| S660 | `model_assisted_enforcement_red_team`, `model_assisted_tax_administration_minimum` |
| S661 | `public_filing_refund_floor` |

## Claim discipline

Every `source_currentness_refs` entry must have an accompanying `source_currentness_claims` object with the same source ID, a concise current claim, and a review reason. `tools/audit_source_currentness.py` makes this enforceable.

## Rev0289 note

The remedy-spine pass did not promote any additional ordinary citations into currentness refs. Remedy profiles inherit source-currentness linkage only from already-tracked volatile sources.
