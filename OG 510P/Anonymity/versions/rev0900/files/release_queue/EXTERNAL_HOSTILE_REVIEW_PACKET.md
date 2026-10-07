# External hostile review packet

- Packet format: `external-hostile-review-packet-v10`
- Generated for revision: `rev0900`
- Checked bundle: `Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`
- External review status: `packet_ready_signoff_missing`
- Publication authorized: `false`

## Why this exists

This packet only prepares external review. Publication remains blocked until a named external/adversarial reviewer or independent tool countersigns a reviewed packet or supplies a reviewed failure report.

## Required reviewer attacks

### `state_nat_bit_boundary`

- Must recompute: `epsilon_nat, epsilon_bits, horizon_bits, per_epoch_odds`
- Must try to break: `copy_nat_value_as_bit_exponent, multiply_by_ln2_instead_of_dividing, zero_delta_sanity_control`
- Acceptance rule: A reviewer must independently derive the bit conversion from the nat-bound source parameters and reject nat-as-bit or multiply-by-ln2 substitutions.

### `mucc_contact_floor_arithmetic`

- Must recompute: `p_floor, expected_contact_floor`
- Must try to break: `beta_instead_of_one_minus_beta, drop_alpha_denominator, multiply_by_alpha_instead_of_dividing, round_down_expected_contact_floor, underbudget_three_round_schedule`
- Acceptance rule: A reviewer must independently derive the expected contact floor and show that each listed shortcut underestimates or misstates the bound.

### `mucc_liveness_substitution_boundary`

- Must recompute: `lower_bound_liveness_guard, live_factor_non_substitution_guard, inner_alpha_lower_recomputed, forbidden_outer_as_inner_alpha, nested_quorum_alpha_overstatement_ratio`
- Must try to break: `lower_bound_liveness_as_theorem_evidence, live_yield_alpha_vs_lookup_concurrency_alpha, outer_d_t_as_inner_n_h_alpha_calibration`
- Acceptance rule: A reviewer must reject lower-bound liveness evidence as theorem evidence, reject lookup-concurrency alpha as live-yield alpha, and keep outer (d,t) distinct from inner (n,h,q,rho). The pinned drill must reproduce 0.3288404125 from (16,11,0.6,0), reject 0.8263296 from the forbidden outer-as-inner substitution, and confirm that no separate churn_alpha_table.tex artifact is claimed.

### `mucc_approximate_equalization_boundary`

- Must recompute: `approximate_mucc_required_destination_contact_average_A, one_sided_counterexample_expected_total_contacts, one_sided_counterexample_global_marginal_diameter, two_sided_radius_implied_diameter, two_sided_radius_correct_contact_floor`
- Must try to break: `one_sided_marginal_ceiling_as_approx_mucc, two_sided_radius_without_factor_two`
- Acceptance rule: A reviewer must reproduce the destination-only counterexample to a one-sided marginal ceiling, then derive the diameter floor dA+(M-d)(A-delta)_+ and apply delta<=2eta for a two-sided center radius. For eta=0.05 the reviewer must obtain 127.2, not 139.6 or the legacy 139.2 expression.

### `mucc_necessity_not_sufficiency_boundary`

- Must recompute: `iid_binomial_success_at_universal_floor, iid_binomial_success_at_predecessor, iid_binomial_minimum_integer_contacts, thinned_hypergeom_success_at_universal_floor, thinned_hypergeom_success_at_predecessor, thinned_hypergeom_minimum_integer_contacts`
- Must try to break: `universal_floor_as_success_certificate`
- Acceptance rule: A reviewer must reject the 152-contact universal Markov expectation floor as a 0.95 success certificate and independently verify that both named optimistic joint models fail at 227 and first pass at 228.

### `mucc_joint_assumption_sufficiency_ladder`

- Must recompute: `mucc_marginal_independent_success_at_optimistic_minimum, mucc_marginal_independent_success_at_predecessor, mucc_marginal_independent_minimum_integer_contacts, mean_only_liveness_success_lower_bound_at_full_contact, mean_only_liveness_required_contacts_unclipped`
- Must try to break: `optimistic_joint_model_as_mucc_marginal_certificate, independent_liveness_as_correlation_robust_certificate, upper_yield_alpha_as_sufficiency_input`
- Acceptance rule: A reviewer must derive the lower-convex-envelope guarantee from MUCC marginals, verify failure at 249 and first pass at 250 under exact independent liveness, then show that mean-only correlated liveness certifies only 0.68 at full contact and would require 310 contacts for a 0.95 bound. The reviewer must also check that alpha's evidentiary direction is not reversed.

### `mucc_joint_privacy_nonclaim_boundary`

- Must recompute: `perfect_leakage_fixed_contact_count, perfect_leakage_contact_marginal, perfect_leakage_support_intersection_size, perfect_leakage_total_variation_distance, perfect_leakage_bayes_recovery, perfect_leakage_mutual_information_bits, perfect_leakage_success_probability_D0, perfect_leakage_success_probability_D1`
- Must try to break: `exact_mucc_as_joint_contact_privacy`
- Acceptance rule: A reviewer must enumerate the two 256-shift orbit supports, verify exact 250/256 contact marginals for every label, verify zero support intersection and therefore TV=1/perfect destination recovery, and independently recompute success 0.9628928 and 0.9628032 under alpha=0.8. The k0=250 sufficiency row must be accepted only as availability, never as anonymity evidence.

### `mceq_tv_support_ratio_boundary`

- Must recompute: `one_step_maximal_leakage_bits, one_step_uniform_prior_recovery, repeated_maximal_leakage_bits, repeated_uniform_prior_recovery, support_contained_maximal_leakage_bound_bits, support_contained_pairwise_max_divergence_bound_bits`
- Must try to break: `tv_as_finite_reference_ratio_without_support_containment, pairwise_tv_as_alphabet_free_maximal_leakage, repeated_off_support_tag_horizon, support_contained_uniform_cover_bound, singleton_tv_factor_two_overstatement`
- Acceptance rule: A reviewer must derive the N-destination off-support tag family, verify TV(P_d,Q)=TV(P_d,P_d')=delta, verify infinite D_infinity to Q, and reproduce 2.608809242676 bits plus 0.023828125 recovery at N=256, delta=0.02. The six-step attack must reproduce 4.912180044586 bits and 0.117617940936 recovery. The reviewer must then verify that the finite ratio bounds require support containment and q>0, yielding 0.339501170198 and 0.692863304520 bits for k=8, epsilon=0.005, T=6.

### `mceq_worked_binding_nonclaim`

- Must recompute: `worked_fallback_observation_sum, worked_fallback_publication_eligible`
- Must try to break: `worked_fallback_vector_as_mceq_certificate`
- Acceptance rule: A reviewer must trace 0.056345507023 to the three maintained observation-attenuation terms, confirm that the retired MC-EQ horizon/slack fields do not exist, and reject the row as MC-EQ or joint-channel MaxL evidence because its composition evidence is assumption-only and publication_eligible=false.

### `cppc_alert_necessity_sufficiency_boundary`

- Must recompute: `alpha_0_02_beta_0_10_two_sided_floor_bits, natural_log_mislabeled_value, correct_bit_value, reverse_direction_example_forward_bits, reverse_direction_example_reverse_bits, reverse_direction_example_two_sided_bits, alpha_0_01_beta_0_10_two_sided_floor_bits`
- Must try to break: `one_sided_lower_bound_as_cap_certificate, natural_log_values_labeled_as_bits, missing_reverse_direction, six_bit_target_impossibility, published_calibration_inherited_alert_claim`
- Acceptance rule: A reviewer must derive both weighted-error inequalities in bit units, reproduce the 5.491853 lower bound and the zero-probability counterexample showing it is not a certificate, recover 2.890372 nats versus 4.169925 bits for the unit trap, and verify that the missing reverse direction changes the (beta,alpha)=(0.01,0.05) row from 4.307429 to 6.569856 bits. The immutable public calibration row must remain withdrawn rather than silently repaired in place.

### `cppc_mechanism_composition_and_artifact_boundary`

- Must recompute: `rr_q_0_1_one_slot_bits, rr_q_0_1_two_slot_bits`
- Must try to break: `rr_q_target_incompatibility, rr_fixed_slot_composition, delay_as_eventual_privacy_amplification, bare_hash_as_hiding_commitment`
- Acceptance rule: A reviewer must prove the randomized-response upper guarantee, verify q=0.1 gives 3.169925001 bits for one slot and 6.339850003 for two, reject any 0.02 false-alarm target under that q, and confirm that delay alone does not discount an eventual plaintext transcript and that a bare hash of a low-entropy alert is not a hiding commitment. No deployment CPPC may be inferred from the illustrative card.

### `endpoint_pml_mass_true_odds_boundary`

- Must recompute: `deterministic_reveal_pml_bits, deterministic_reveal_true_odds, uniform_4096_mass_factor, uniform_4096_true_odds_factor, uniform_4096_true_odds_bits`
- Must try to break: `pml_mass_as_true_odds, prior_cap_true_odds_conversion, published_legacy_odds_wording_as_true_odds`
- Acceptance rule: A reviewer must derive that log2(pi(i|o)/pi(i)) is posterior-mass inflation/PML, not one-vs-complement odds; verify deterministic binary revelation has one bit of PML but infinite true odds; and reproduce the guarded N=4096, epsilon=0.75 conversion 1.681792830507 -> 1.682072885510, or 0.750240220031 bits. The reviewer must reject any finite prior-independent odds conversion and confirm that immutable legacy wording is withdrawn from true-odds reuse rather than silently rewritten.

### `endpoint_hockey_stick_tail_boundary`

- Must recompute: `hockey_stick_counterexample_slack, hockey_stick_counterexample_positive_loss_tail, hockey_stick_tail_to_slack_ratio`
- Must try to break: `hockey_stick_delta_as_tail_probability, tail_implies_hockey_stick_not_converse`
- Acceptance rule: A reviewer must evaluate P1=(0.51,0.49), P2=(0.49,0.51), P=(0.5,0.5), verify E_1(P_i||P)=TV=0.01 while the positive-loss event has probability 0.51, and prove only the forward implication tail<=eta => hockey-stick<=eta. Hockey-stick delta must not be described as a bad-transcript probability without a separate tail theorem.

### `endpoint_tv_singleton_and_hot_lane_regression`

- Must recompute: `singleton_tv_corrected_bits, singleton_tv_legacy_double_bits, published_ready_sources_scanned, published_ready_semantic_alias_violations`
- Must try to break: `singleton_tv_factor_two_overpayment, published_ready_semantic_alias_scan`
- Acceptance rule: A reviewer must use the singleton event consequence |P(o)-Q(o)|<=TV(P,Q), reproduce 0.289506617195 bits for q_min=0.1 and delta=0.01, and reject the legacy doubled-deviation value 0.584962500721 bits as unnecessary payment. The reviewer must also rerun the Published-ready semantic scan and obtain zero known PML-as-odds aliases.

### `bossfight_scalar_observation_and_contact_correlation`

- Must recompute: `cyclic_reveal_scalar_erasure_bits, cyclic_reveal_actual_maximal_leakage_bits, cyclic_reveal_scalar_exact_guess, cyclic_reveal_actual_exact_guess, independent_any_hit_probability, equal_marginal_any_hit_lower, equal_marginal_any_hit_upper`
- Must try to break: `equal_observation_marginals_not_independent_erasure, correlated_contacts_break_independent_any_hit`
- Acceptance rule: A reviewer must enumerate the three-secret cyclic-reveal channel, verify equal reveal probability 1/2, recover one bit of actual maximal leakage and exact guessing 2/3, and contrast them with 0.321928094887 bits and 5/12 under the independent-erasure model. The reviewer must also prove that rho=0.1 and m=10 permit any-hit probability from 0.1 to 1 under equal marginals, while 0.6513215599 requires independence.

### `bossfight_partial_visibility_filter_and_allocation_boundary`

- Must recompute: `partial_subset_target_in_probability, partial_subset_target_erased_probability, retrospective_overshoot_bits`
- Must try to break: `partial_subset_target_can_be_erased, retrospective_pml_not_no_overshoot_filter, equal_share_not_empirical_average`
- Acceptance rule: A reviewer must verify in the N=5,k=2,m=1,q=0.2 partial-subset drill that the target-erased branch has probability 0.064 rather than zero and the target-observed branch has probability 0.128. The reviewer must then show that a one-bit triggering output crosses a 0.5-bit cap before a retrospective odometer can stop it, and distinguish B/Q as an optional equal-share design from a history-uniform per-round theorem.

### `bossfight_model_binding_and_joint_tier_boundary`

- Must recompute: `cyclic_reveal_scalar_erasure_bits, cyclic_reveal_actual_maximal_leakage_bits, tier_synergy_joint_bits`
- Must try to break: `arithmetic_verifier_without_channel_binding, marginal_tiers_can_have_joint_synergy`
- Acceptance rule: A reviewer must show that the same scalar model tuple can make a deterministic arithmetic checker pass for two deployments with different actual channels, so the honest verdict is arithmetic-valid-under-model-digest rather than deployment anonymous. The reviewer must also reproduce the one-time-pad tier construction in which each marginal tier has zero maximal leakage but the joint pair leaks one bit, and reject marginal-vector composition without a joint witness.

### `bossfight_active_consumer_propagation_audit`

- Must recompute: `independent_any_hit_probability, equal_marginal_any_hit_lower, equal_marginal_any_hit_upper, cyclic_reveal_actual_maximal_leakage_bits`
- Must try to break: `equal_observation_marginals_not_independent_erasure, correlated_contacts_break_independent_any_hit, arithmetic_verifier_without_channel_binding`
- Acceptance rule: A reviewer must inspect the active Eval 2 source/note and Synthesis 17 source/note, verify that 0.871488 and approximately 0.992 are labeled independent-control sensitivity values rather than deployment evidence, and verify that 0.056345507023 and 0.26590 are labeled non-authorizing arithmetic with composition_evidence_status=assumption_only_no_joint_channel_witness and publication_eligible=false. Any active consumer that shortens these to an observation probability, anonymity certificate, or published privacy total fails the review.

### `threat_transfer_nonclaim_boundary`

- Must recompute: `native_theorem_row_count, external_transfer_authorized_rows, key_independence_counterexample_global_marginal_diameter`
- Must try to break: `ipfs_kademlia_provider_records, ipfs_delegated_routing_http_v1, peer2pir_ipfs_query_privacy, ohttp_role_separation, tor_low_latency_circuits, i2p_netdb_floodfill_tunnels, key_independence_as_mucc_label_uniformity`
- Acceptance rule: A reviewer must reject IPFS, delegated-routing, Peer2PIR, OHTTP, Tor, and I2P rows as theorem-bearing MUCC transfers until each has a new source-bound model/card. The reviewer must also reject destination-independence or DP-style stability as committee-label-uniform MUCC unless a symmetry or global marginal-diameter bridge is proved, and reject any MUCC-only row as joint contact-set privacy.

## Current internal values for independent recomputation

- State target: `series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex`
- State recomputed values: `{"epsilon_bits": 0.14426950408889633, "epsilon_nat": 0.09999999999999999, "horizon_bits": 2.3083120654223412, "horizon_epochs": 16, "per_epoch_odds": 1.1051709180756477}`
- MUCC target: `series/anondht_state_series/paper2_mucc_committee_contact_privacy/paper.tex`
- MUCC recomputed values: `{"M": 256, "alpha": 0.8, "approximate_mucc_required_destination_contact_average_A": 0.5937499999999999, "beta": 0.05, "claimed_success_floor": 0.95, "d": 8, "expected_contact_floor": 151.99999999999997, "forbidden_outer_as_inner_alpha": 0.8263296, "iid_binomial_minimum_integer_contacts": 228, "iid_binomial_predecessor_contacts": 227, "iid_binomial_success_at_minimum": 0.9512147249231547, "iid_binomial_success_at_predecessor": 0.9490195143921485, "iid_binomial_success_at_universal_floor": 0.5808056947074889, "inner_alpha_lower_recomputed": 0.3288404125089791, "inner_committee_members_n": 16, "inner_common_outage_rho": 0.0, "inner_member_reachability_q": 0.6, "inner_quorum_h": 11, "key_independence_counterexample_global_marginal_diameter": 1.0, "mean_only_liveness_required_contacts_unclipped": 310, "mean_only_liveness_success_lower_bound_at_full_contact": 0.68, "mean_only_liveness_target_certifiable_within_M": false, "mucc_marginal_independent_minimum_integer_contacts": 250, "mucc_marginal_independent_predecessor_contacts": 249, "mucc_marginal_independent_success_at_minimum": 0.9524838400000001, "mucc_marginal_independent_success_at_optimistic_minimum": 0.81641472, "mucc_marginal_independent_success_at_predecessor": 0.9462988800000001, "mucc_marginal_independent_success_at_universal_floor": 0.34635776, "nested_quorum_alpha_overstatement": 0.4974891874910209, "nested_quorum_alpha_overstatement_ratio": 2.512859029993574, "one_sided_counterexample_expected_total_contacts": 4.749999999999999, "one_sided_counterexample_global_marginal_diameter": 0.5937499999999999, "one_sided_counterexample_wrong_Mp_cover_floor": 151.99999999999997, "p_floor": 0.5937499999999999, "perfect_leakage_bayes_recovery": 1.0, "perfect_leakage_contact_marginal": 0.9765625, "perfect_leakage_fixed_contact_count": 250, "perfect_leakage_mutual_information_bits": 1.0, "perfect_leakage_success_probability_D0": 0.9628928000000043, "perfect_leakage_success_probability_D1": 0.9628032000000043, "perfect_leakage_support_intersection_size": 0, "perfect_leakage_total_variation_distance": 1.0, "t": 4, "thinned_hypergeom_minimum_integer_contacts": 228, "thinned_hypergeom_predecessor_contacts": 227, "thinned_hypergeom_success_at_minimum": 0.9520315268325863, "thinned_hypergeom_success_at_predecessor": 0.9498728266435995, "thinned_hypergeom_success_at_universal_floor": 0.5817235988129154, "two_sided_radius_correct_contact_floor": 127.19999999999997, "two_sided_radius_example_eta": 0.05, "two_sided_radius_implied_diameter": 0.1, "underbudget_total_contacts": 144, "universal_expected_contact_floor_ceiling": 152}`
- MC-EQ target: `series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex`
- MC-EQ recomputed values: `{"N": 256, "delta": 0.02, "one_step_maximal_leakage_bits": 2.608809242675524, "one_step_uniform_prior_recovery": 0.023828125, "published_calibration_correction_notice_present": true, "published_calibration_legacy_claim_present": true, "published_calibration_snapshot_sha256": "bc566ec5d37eb65175af33cb0376c9d59e88a97e09fd7a092fb45138612572cf", "repeated_maximal_leakage_bits": 4.912180044586173, "repeated_uniform_prior_recovery": 0.11761794093625008, "steps": 6, "support_contained_maximal_leakage_bound_bits": 0.3395011701982051, "support_contained_pairwise_max_divergence_bound_bits": 0.6928633045196171, "worked_fallback_observation_sum": 0.056345507023, "worked_fallback_publication_eligible": false}`
- CPPC target: `series/anondht_state_series/paper3_closed_view_auditing_cppc/paper.tex`
- CPPC recomputed values: `{"alpha_0_01_beta_0_10_two_sided_floor_bits": 6.491853096329675, "alpha_0_02_beta_0_10_two_sided_floor_bits": 5.491853096329675, "correct_bit_value": 4.169925001442312, "natural_log_mislabeled_value": 2.8903717578961645, "published_calibration_alert_correction_notice_present": true, "published_calibration_snapshot_sha256": "bc566ec5d37eb65175af33cb0376c9d59e88a97e09fd7a092fb45138612572cf", "reverse_direction_example_forward_bits": 4.307428525192247, "reverse_direction_example_reverse_bits": 6.569855608330948, "reverse_direction_example_two_sided_bits": 6.569855608330948, "rr_q_0_1_one_slot_bits": 3.169925001442312, "rr_q_0_1_two_slot_bits": 6.339850002884624, "rr_two_slot_six_bit_minimum_public_error": 0.1111111111111111, "rr_two_slot_six_bit_minimum_q": 0.1111111111111111}`
- Endpoint target: `series/anonymity_series/paperA_odds_inflation_anonymity/paper.tex`
- Endpoint recomputed values: `{"deterministic_reveal_pml_bits": 1.0, "deterministic_reveal_true_odds": "infinite", "hockey_stick_counterexample_positive_loss_tail": 0.51, "hockey_stick_counterexample_slack": 0.01, "hockey_stick_tail_to_slack_ratio": 51.0, "published_ready_semantic_alias_violations": 0, "published_ready_sources_scanned": 8, "singleton_tv_corrected_bits": 0.28950661719498477, "singleton_tv_legacy_double_bits": 0.5849625007211562, "uniform_4096_mass_factor": 1.681792830507429, "uniform_4096_true_odds_bits": 0.7502402200312348, "uniform_4096_true_odds_factor": 1.6820728855095612}`
- Boss Fight target: `series/bossfight_series/paperA_bossfight_budgets/paper.tex`
- Boss Fight recomputed values: `{"cyclic_reveal_actual_exact_guess": 0.6666666666666666, "cyclic_reveal_actual_maximal_leakage_bits": 1.0, "cyclic_reveal_scalar_erasure_bits": 0.32192809488736235, "cyclic_reveal_scalar_exact_guess": 0.4166666666666667, "equal_marginal_any_hit_lower": 0.1, "equal_marginal_any_hit_upper": 1.0, "independent_any_hit_probability": 0.6513215599, "partial_subset_target_erased_probability": 0.06400000000000002, "partial_subset_target_in_probability": 0.12800000000000003, "retrospective_overshoot_bits": 0.5, "tier_synergy_joint_bits": 1.0}`
- External theorem-transfer rows authorized: `0`

## Minimum return artifact

Required fields: `reviewer_identity_or_tool, reviewed_packet_sha256, surface_digests_checked, findings, state_result, mucc_result, mceq_result, cppc_result, endpoint_result, bossfight_result, threat_transfer_result, signature_or_reproducible_command`

## Rule

If any input digest changes, rebuild this packet before review. If external review is absent, inconclusive, or unsigned, keep publication_authorized=false.
