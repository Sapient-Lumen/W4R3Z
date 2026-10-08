# Router runtime, risk coverage, and case-vocabulary refactor — rev0319

This revision targets the riskiest gap left by rev0318: the archive had good answer contracts but no execution boundary. The work intentionally avoids adding another registry. It adds one small runtime, wires it into the existing case audit, expands thin high-risk coverage, and cleans dead case vocabulary exposed by the audit.

## Priority changes made

1. Added `tools/route_case.py`, a deterministic candidate router that scores live golden-case facts against live route records and route memo vocabulary without reading expected route IDs.
2. Rewrote `tools/audit_case_contracts.py` so the release fails if the router's top-3 candidates miss any expected route.
3. Expanded golden cases from 84 to 101, with emphasis on controller/AI, legal-enforcement, tax-administration access, public-finance, and review/sunset risk.
4. Raised route coverage from 80/155 to 98/155 (63.2%) and raised the non-regression floor from 80 to 90 covered routes.
5. Corrected misdirected contracts: the low-capacity presumptive-levy case is now composite, the payroll-platform case now routes through trust-fund recovery and labor-tax-wedge classification rather than taxpayer-side AI, and the model-assisted enforcement case now routes to the model-assisted tax-administration minimum.
6. Refactored declared axis vocabulary so it exactly matches live route usage plus active case-contract requirements; dead legacy case-only values are preserved only where explicitly listed as legacy flags in cases, not as live route vocabulary.
7. Updated the golden-cases route memo to state the runtime boundary instead of treating cases as examples or declarative fixtures only.
8. Added `tools/run_semantic_audits.py` so packaging still runs the actual semantic scripts but avoids repeated interpreter startup waste.

## Runtime result

- Runtime status: `deterministic_candidate_router_invoked`
- Candidate limit: 3
- Case contracts: 101
- Runtime top-3 route recall: 107/107
- Runtime top-N exact cases: 101/101
- Runtime primary matches: 101/101
- Candidate misses: 0

## Coverage after this pass

- `controller_ai`: 11/21
- `cross_border_reporting`: 5/6
- `environment_climate_commons`: 9/10
- `financial_system_risk`: 6/8
- `labor_care_benefits`: 7/11
- `legal_enforcement_penalty`: 7/11
- `public_finance_core`: 21/44
- `public_procurement_industrial_policy`: 5/5
- `regulated_networks_platforms`: 4/4
- `release_integrity_currentness`: 4/4
- `social_floor_public_services`: 6/8
- `tax_administration_access`: 10/17
- `wealth_property_rent`: 3/6

## What remains riskiest

The runtime is still only a candidate router. The next risky gap is an answer emitter that returns selected routes, precedence decisions, duties/remedies, must-not-answer warnings, citations, unknowns, and confidence. Quantitative revenue/distributional modeling and claim-level provenance remain separate missing layers.

## Uncovered routes still needing cases

- `administration_explanation_and_appeal_minimum`
- `annual_wealth_backstop_visibility_grouping_and_liquidity`
- `assessment_unit_and_care_load`
- `base_ordering_overlap_creditability_and_non_substitution`
- `beneficial_ownership_and_controller_chain`
- `beneficiary_composite_netting_and_residual_ordering`
- `beneficiary_home_market_and_local_burden_claim_split`
- `burden_salience_disclosure_and_hidden_tax`
- `channel_pluralism_access_independence_and_fallback`
- `charitable_public_benefit_transfer_and_retained_surplus`
- `collection_anchor_choice_and_remittance_chain`
- `compliance_cost_assisted_filing_and_preparer_dependence`
- `controller_map_confidence_unknowns_and_bounded_imputation`
- `controller_map_contest_window_counter_map_and_finality`
- `controller_map_event_log_retention_and_preservation`
- `controller_map_field_severability_partial_acceptance_and_issue_scoped_correction`
- `controller_map_integrity_correction_safe_harbor_and_sanction`
- `controller_map_packet_identity_canonical_fields_and_supersession`
- `controller_map_reuse_portability_and_cross_regime_reliance`
- `controller_map_signer_authority_delegation_and_joint_attestation`
- `controller_map_verification_sampling_and_review_intensity`
- `creditor_distress_netting_and_retained_surplus`
- `culpability_penalty_safe_harbor_and_criminal_referral`
- `customer_benefit_price_access_and_retained_surplus`
- `data_minimization_credential_reuse_and_sensitive_attribute_firewall`
- `failure_waterfall_and_ex_ante_security`
- `frontier_scarce_capacity_threshold`
- `insurance_policyholder_benefit_and_retained_surplus`
- `interim_liability_stays_escrow_and_hardship_relief`
- `international_coordination_claim_split`
- `land_site_rent_netting_and_retained_surplus`
- `loss_recognition_symmetry`
- `measurement_cadence_and_proxy_graduation`
- `net_fiscal_stack_disclosure_and_substitution`
- `pension_pass_through_incidence_and_proceeds`
- `precaution_threshold_gating`
- `proceeds_visibility_local_share_and_earmarking`
- `provisional_controller_filing_escrow_and_true_up`
- `public_input_reciprocity_contribution`
- `public_service_member_relief_and_local_repair`
- `real_value_indexation_and_reset_cadence`
- `regressivity_repair_channel_and_delivery_sync`
- `reinvestment_prefunding_ring_fence_and_retained_surplus`
- `relabeling_dependence_and_category_integrity`
- `reliance_privilege_phase_in_and_grandfathering`
- `reportable_transaction_material_advisor_promoter_and_advisee_list`
- `same_facts_reuse_portability_and_delta_update`
- `standing_bundle_and_non_conflicted_representation`
- `status_proxy_disparate_impact_and_accessibility_repair`
- `supplier_benefit_net_terms_and_retained_surplus`
- `third_party_reporting_correction_and_bounded_recipient_shelter`
- `threshold_cliff_smoothing_and_graduation`
- `timing_cashflow_liquidity_deferral_and_prefunding`
- `transferee_nominee_alter_ego_successor_and_wrongful_levy`
- `verification_sampling_and_review_intensity`
- `whistleblower_tip_classification_confidentiality_award_and_accused_taxpayer_protection`
- `worker_benefit_pay_hours_member_share_and_local_repair`
