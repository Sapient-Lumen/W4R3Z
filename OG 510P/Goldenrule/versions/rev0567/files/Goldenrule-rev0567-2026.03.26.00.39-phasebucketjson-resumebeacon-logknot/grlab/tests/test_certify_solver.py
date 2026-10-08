import unittest

from grlab.certify import (
    CertifyError,
    certify_memory_one_pair,
    default_screening_spec,
    ecology_sampling_plan_fingerprint_sha256,
    opening_distribution_contract_fingerprint_sha256,
    transition_kernel_contract_fingerprint_sha256,
    pairing_fingerprint_sha256,
    proxy_measurement_contract_fingerprint_sha256,
    steady_state_contract_fingerprint_sha256,
    uncertainty_contract_fingerprint_sha256,
    repair_sampling_plan_fingerprint_sha256,
    screening_spec_fingerprint_sha256,
    stage_game_fingerprint_sha256,
    strategy_fingerprint_sha256,
)


def _memory_one(
    *,
    strategy_id: str,
    p_cc: float,
    p_cd: float,
    p_dc: float,
    p_dd: float,
) -> dict[str, object]:
    return {
        "family": "memory_one",
        "id": strategy_id,
        "p0": p_cc,
        "p_cc": p_cc,
        "p_cd": p_cd,
        "p_dc": p_dc,
        "p_dd": p_dd,
    }


class CertifySolverTests(unittest.TestCase):
    def test_always_cooperate_pair(self) -> None:
        a = _memory_one(strategy_id="a", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        b = _memory_one(strategy_id="b", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        res = certify_memory_one_pair(a, b)
        self.assertEqual(res["schema_version"], 21)
        self.assertEqual(res["kind"], "certify_memory_one_result")
        self.assertAlmostEqual(res["avg_payoff_a"], 3.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 3.0, places=9)
        self.assertTrue(res["transition_graph_diagnostics"]["reducible"])
        self.assertEqual(res["transition_graph_diagnostics"]["closed_classes"], [["CC"]])
        self.assertEqual(res["transition_graph_diagnostics"]["reachable_closed_classes_from_initial_support"], [["CC"]])
        self.assertEqual(
            res["transition_graph_diagnostics"]["closed_class_entry_probabilities_from_initial_distribution"],
            [{"closed_class": ["CC"], "entry_probability": 1.0, "conditional_expected_entry_steps_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 0.0, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}}],
        )
        self.assertFalse(
            res["transition_graph_diagnostics"]["multiple_closed_classes_with_positive_entry_probability_from_initial_distribution"]
        )
        self.assertAlmostEqual(
            res["transition_graph_diagnostics"]["expected_steps_to_any_closed_class_from_initial_distribution"],
            0.0,
            places=9,
        )
        self.assertAlmostEqual(
            res["transition_graph_diagnostics"]["expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution"],
            0.0,
            places=9,
        )
        self.assertAlmostEqual(
            res["transition_graph_diagnostics"]["expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution"],
            0.0,
            places=9,
        )
        self.assertEqual(
            res["transition_graph_diagnostics"]["expected_visit_counts_before_any_closed_class_entry_from_initial_distribution"],
            {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0},
        )
        self.assertEqual(
            res["transition_graph_diagnostics"]["expected_transition_counts_before_any_closed_class_entry_from_initial_distribution"],
            {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}},
        )
        self.assertAlmostEqual(
            res["transition_graph_diagnostics"]["expected_steps_to_any_closed_class_from_initial_distribution"],
            0.0,
            places=9,
        )
        self.assertEqual(
            res["transition_graph_diagnostics"]["closed_class_asymptotic_decomposition_from_initial_distribution"],
            [
                {
                    "closed_class": ["CC"],
                    "entry_probability": 1.0,
                    "class_stationary_distribution": [1.0, 0.0, 0.0, 0.0],
                    "weighted_steady_state_contribution": [1.0, 0.0, 0.0, 0.0],
                    "class_avg_payoff_a": 3.0,
                    "class_avg_payoff_b": 3.0,
                }
            ],
        )
        self.assertAlmostEqual(res["steady_state_distribution"][0], 1.0, places=9)
        self.assertEqual(res["asymptotic_distribution_method"], "closed_class_exact_mixture_from_initial_distribution")
        self.assertEqual(res["asymptotic_distribution_from_initial_distribution"], [1.0, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(res["asymptotic_avg_payoff_a_from_initial_distribution"], 3.0, places=9)
        self.assertAlmostEqual(res["asymptotic_avg_payoff_b_from_initial_distribution"], 3.0, places=9)
        self.assertAlmostEqual(res["steady_state_distribution_l1_distance_to_asymptotic_distribution"], 0.0, places=9)
        scorecard = res["anti_vampire_scorecard"]
        self.assertEqual(scorecard["scorecard_version"], 13)
        self.assertEqual(res["screening_spec_ref"]["spec_id"], "canonical_proxy_v1")
        self.assertEqual(
            res["screening_spec_ref"]["spec_fingerprint_sha256"],
            screening_spec_fingerprint_sha256(default_screening_spec()),
        )
        self.assertEqual(scorecard["screening_spec_ref"]["spec_id"], "canonical_proxy_v1")
        self.assertEqual(res["stage_game_ref"]["stage_game_id"], "iterated_prisoners_dilemma_t5_r3_p1_s0")
        self.assertEqual(
            res["stage_game_ref"]["stage_game_fingerprint_sha256"],
            stage_game_fingerprint_sha256(),
        )
        self.assertEqual(res["state_order"], ["CC", "CD", "DC", "DD"])
        self.assertEqual(res["strategy_a_ref"]["strategy_id"], "a")
        self.assertEqual(res["strategy_b_ref"]["strategy_id"], "b")
        self.assertEqual(res["strategy_a_ref"]["strategy_fingerprint_sha256"], strategy_fingerprint_sha256(a))
        self.assertEqual(res["strategy_b_ref"]["strategy_fingerprint_sha256"], strategy_fingerprint_sha256(b))
        self.assertEqual(
            res["pairing_ref"]["pairing_fingerprint_sha256"],
            pairing_fingerprint_sha256(a, b, default_screening_spec()),
        )
        self.assertEqual(scorecard["shock_protocol"], "opponent_single_defection_from_mutual_cooperation_then_zero_noise_expected_payoff_recovery")
        self.assertAlmostEqual(scorecard["own_payoff"], 3.0, places=9)
        self.assertAlmostEqual(scorecard["payoff_gap"], 0.0, places=9)
        self.assertLessEqual(scorecard["ecology_gap_noisy"], -1.0)
        self.assertEqual(scorecard["recovery_rounds"], 1)
        self.assertEqual(scorecard["repair_abuse_rate"], 0.0)
        self.assertEqual(scorecard["repair_offer_count"], 0)
        self.assertEqual(scorecard["repair_abuse_count"], 0)
        self.assertEqual(scorecard["repair_abuse_rate_ci95_low"], 0.0)
        self.assertEqual(scorecard["repair_abuse_rate_ci95_high"], 0.0)
        self.assertGreaterEqual(scorecard["ecology_gap_noisy_stderr"], 0.0)
        self.assertGreaterEqual(scorecard["ecology_gap_noisy_ci95_half_width"], 0.0)
        self.assertGreaterEqual(scorecard["ecology_own_payoff_stderr"], 0.0)
        self.assertGreaterEqual(scorecard["ecology_own_payoff_ci95_half_width"], 0.0)
        self.assertEqual(scorecard["ecology_estimate_kind"], "replicated_rollout_mean")
        self.assertEqual(scorecard["ecology_sampling_ref"]["sampling_plan_id"], "ecology_replicated_rollout_ap_v1")
        self.assertEqual(scorecard["repair_sampling_ref"]["sampling_plan_id"], "repair_offer_proxy_ap_v1")
        self.assertEqual(res["uncertainty_contract_ref"]["contract_id"], "mc_interval_semantics_v1")
        self.assertEqual(
            res["uncertainty_contract_ref"]["contract_fingerprint_sha256"],
            uncertainty_contract_fingerprint_sha256(),
        )
        self.assertEqual(scorecard["uncertainty_contract_ref"], res["uncertainty_contract_ref"])
        self.assertEqual(res["proxy_measurement_contract_ref"]["contract_id"], "anti_vampire_proxy_measurement_v1")
        self.assertEqual(
            res["proxy_measurement_contract_ref"]["contract_fingerprint_sha256"],
            proxy_measurement_contract_fingerprint_sha256(),
        )
        self.assertEqual(scorecard["proxy_measurement_contract_ref"], res["proxy_measurement_contract_ref"])
        self.assertEqual(res["steady_state_contract_ref"]["contract_id"], "memory_one_stationary_or_cesaro_v1")
        self.assertEqual(
            res["steady_state_contract_ref"]["contract_fingerprint_sha256"],
            steady_state_contract_fingerprint_sha256(),
        )
        self.assertEqual(scorecard["steady_state_contract_ref"], res["steady_state_contract_ref"])
        self.assertEqual(res["opening_distribution_contract_ref"]["contract_id"], "memory_one_independent_p0_product_v1")
        self.assertEqual(
            res["opening_distribution_contract_ref"]["contract_fingerprint_sha256"],
            opening_distribution_contract_fingerprint_sha256(),
        )
        self.assertEqual(res["transition_kernel_contract_ref"]["contract_id"], "memory_one_state_product_kernel_v1")
        self.assertEqual(
            res["transition_kernel_contract_ref"]["contract_fingerprint_sha256"],
            transition_kernel_contract_fingerprint_sha256(),
        )
        self.assertEqual(scorecard["transition_kernel_contract_ref"], res["transition_kernel_contract_ref"])
        self.assertEqual(res["transition_matrix"], [[1.0, 0.0, 0.0, 0.0]] * 4)
        self.assertTrue(res["transition_graph_diagnostics"]["reducible"])
        self.assertEqual(res["transition_graph_diagnostics"]["absorbing_states"], ["CC"])
        self.assertEqual(res["transition_graph_diagnostics"]["closed_classes"], [["CC"]])
        self.assertEqual(res["transition_graph_diagnostics"]["initial_support_states"], ["CC"])
        self.assertEqual(res["transition_graph_diagnostics"]["reachable_states_from_initial_support"], ["CC"])
        self.assertEqual(scorecard["opening_distribution_contract_ref"], res["opening_distribution_contract_ref"])
        self.assertEqual(
            scorecard["ecology_sampling_ref"]["sampling_plan_fingerprint_sha256"],
            ecology_sampling_plan_fingerprint_sha256(default_screening_spec()),
        )
        self.assertEqual(
            scorecard["repair_sampling_ref"]["sampling_plan_fingerprint_sha256"],
            repair_sampling_plan_fingerprint_sha256(default_screening_spec()),
        )
        self.assertFalse(scorecard["full_certification_ready"])
        self.assertTrue(scorecard["screening_contract"]["gate_pass"])
        self.assertEqual(scorecard["screening_contract"]["binding_gate_status"], "pass")
        self.assertEqual(scorecard["screening_contract"]["gate_stability"], "stable")
        self.assertEqual(scorecard["screening_contract"]["checks"]["pairwise_fairness"]["threshold_decision_state"], "exact_pass")
        self.assertEqual(scorecard["screening_contract"]["checks"]["noisy_ecology"]["threshold_decision_state"], "clear_pass")
        self.assertEqual(scorecard["screening_contract"]["checks"]["repair_proxy"]["threshold_decision_state"], "threshold_pending")
        self.assertEqual(scorecard["screening_contract"]["failure_reasons"], [])
        self.assertIn("repair_proxy_threshold_pending", scorecard["screening_contract"]["advisory_reasons"])

    def test_always_defect_pair(self) -> None:
        a = _memory_one(strategy_id="a", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        b = _memory_one(strategy_id="b", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        res = certify_memory_one_pair(a, b)
        self.assertAlmostEqual(res["avg_payoff_a"], 1.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 1.0, places=9)
        self.assertAlmostEqual(res["steady_state_distribution"][3], 1.0, places=9)
        self.assertGreater(res["anti_vampire_scorecard"]["recovery_rounds"], 40)

    def test_cooperator_vs_defector(self) -> None:
        coop = _memory_one(strategy_id="coop", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        defect = _memory_one(strategy_id="def", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        res = certify_memory_one_pair(coop, defect)
        self.assertAlmostEqual(res["avg_payoff_a"], 0.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 5.0, places=9)
        self.assertAlmostEqual(sum(res["steady_state_distribution"]), 1.0, places=9)
        self.assertGreater(res["anti_vampire_scorecard"]["payoff_gap"], 0.0)
        self.assertEqual(res["transition_graph_diagnostics"]["closed_classes"], [["CD"]])
        self.assertEqual(res["transition_graph_diagnostics"]["absorbing_states"], ["CD"])
        self.assertEqual(res["transition_graph_diagnostics"]["initial_support_states"], ["CD"])
        self.assertEqual(res["transition_graph_diagnostics"]["reachable_closed_classes_from_initial_support"], [["CD"]])
        self.assertEqual(
            res["transition_graph_diagnostics"]["closed_class_entry_probabilities_from_initial_distribution"],
            [{"closed_class": ["CD"], "entry_probability": 1.0, "conditional_expected_entry_steps_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 0.0, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}}],
        )
        self.assertEqual(
            res["transition_graph_diagnostics"]["closed_class_asymptotic_decomposition_from_initial_distribution"],
            [
                {
                    "closed_class": ["CD"],
                    "entry_probability": 1.0,
                    "class_stationary_distribution": [0.0, 1.0, 0.0, 0.0],
                    "weighted_steady_state_contribution": [0.0, 1.0, 0.0, 0.0],
                    "class_avg_payoff_a": 0.0,
                    "class_avg_payoff_b": 5.0,
                }
            ],
        )

    def test_reducible_chain_falls_back_to_initial_cesaro_distribution(self) -> None:
        wsls = _memory_one(strategy_id="wsls", p_cc=1.0, p_cd=1.0, p_dc=0.0, p_dd=0.0)
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)

        res = certify_memory_one_pair(wsls, always_c)

        self.assertEqual(res["steady_state_method"], "cesaro_from_initial_distribution")
        self.assertEqual(res["initial_distribution"], [1.0, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(res["steady_state_distribution"][0], 1.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_a"], 3.0, places=9)
        self.assertAlmostEqual(res["avg_payoff_b"], 3.0, places=9)
        self.assertTrue(res["transition_graph_diagnostics"]["reducible"])
        self.assertEqual(res["transition_graph_diagnostics"]["closed_classes"], [["CC"], ["DC"]])
        self.assertEqual(res["transition_graph_diagnostics"]["reachable_closed_classes_from_initial_support"], [["CC"]])
        self.assertEqual(
            res["transition_graph_diagnostics"]["closed_class_entry_probabilities_from_initial_distribution"],
            [
                {"closed_class": ["CC"], "entry_probability": 1.0, "conditional_expected_entry_steps_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 0.0, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}},
                {"closed_class": ["DC"], "entry_probability": 0.0, "conditional_expected_entry_steps_from_initial_distribution": None, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": None, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": None, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": None, "CD": None, "DC": None, "DD": None}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": None, "CD": None, "DC": None, "DD": None}, "CD": {"CC": None, "CD": None, "DC": None, "DD": None}, "DC": {"CC": None, "CD": None, "DC": None, "DD": None}, "DD": {"CC": None, "CD": None, "DC": None, "DD": None}}},
            ],
        )
        self.assertFalse(
            res["transition_graph_diagnostics"]["multiple_closed_classes_with_positive_entry_probability_from_initial_distribution"]
        )
        self.assertAlmostEqual(
            res["transition_graph_diagnostics"]["expected_steps_to_any_closed_class_from_initial_distribution"],
            0.0,
            places=9,
        )
        self.assertEqual(
            res["transition_graph_diagnostics"]["closed_class_asymptotic_decomposition_from_initial_distribution"],
            [
                {
                    "closed_class": ["CC"],
                    "entry_probability": 1.0,
                    "class_stationary_distribution": [1.0, 0.0, 0.0, 0.0],
                    "weighted_steady_state_contribution": [1.0, 0.0, 0.0, 0.0],
                    "class_avg_payoff_a": 3.0,
                    "class_avg_payoff_b": 3.0,
                },
                {
                    "closed_class": ["DC"],
                    "entry_probability": 0.0,
                    "class_stationary_distribution": [0.0, 0.0, 1.0, 0.0],
                    "weighted_steady_state_contribution": [0.0, 0.0, 0.0, 0.0],
                    "class_avg_payoff_a": 5.0,
                    "class_avg_payoff_b": 0.0,
                },
            ],
        )

    def test_initial_distribution_can_split_across_multiple_closed_classes(self) -> None:
        split_a = {
            "family": "memory_one",
            "id": "split_a",
            "p0": 0.5,
            "p_cc": 1.0,
            "p_cd": 1.0,
            "p_dc": 0.0,
            "p_dd": 0.0,
        }
        split_b = {
            "family": "memory_one",
            "id": "split_b",
            "p0": 0.5,
            "p_cc": 1.0,
            "p_cd": 0.0,
            "p_dc": 1.0,
            "p_dd": 0.0,
        }

        res = certify_memory_one_pair(split_a, split_b)
        diag = res["transition_graph_diagnostics"]

        self.assertEqual(res["steady_state_method"], "cesaro_from_initial_distribution")
        self.assertEqual(res["initial_distribution"], [0.25, 0.25, 0.25, 0.25])
        self.assertEqual(res["asymptotic_distribution_method"], "closed_class_exact_mixture_from_initial_distribution")
        self.assertEqual(res["asymptotic_distribution_from_initial_distribution"], [0.5, 0.0, 0.0, 0.5])
        self.assertAlmostEqual(res["asymptotic_avg_payoff_a_from_initial_distribution"], 2.0, places=9)
        self.assertAlmostEqual(res["asymptotic_avg_payoff_b_from_initial_distribution"], 2.0, places=9)
        self.assertGreater(res["steady_state_distribution_l1_distance_to_asymptotic_distribution"], 0.0)
        self.assertLess(res["steady_state_distribution_l1_distance_to_asymptotic_distribution"], 0.01)
        self.assertEqual(diag["closed_classes"], [["CC"], ["DD"]])
        self.assertEqual(
            diag["closed_class_entry_probabilities_from_initial_distribution"],
            [
                {"closed_class": ["CC"], "entry_probability": 0.5, "conditional_expected_entry_steps_from_initial_distribution": 0.5, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 2.5, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.5, "DC": 0.0, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.5, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}},
                {"closed_class": ["DD"], "entry_probability": 0.5, "conditional_expected_entry_steps_from_initial_distribution": 0.5, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 2.5, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 0.0, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.0, "DC": 0.5, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.5}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}},
            ],
        )
        self.assertTrue(
            diag["multiple_closed_classes_with_positive_entry_probability_from_initial_distribution"]
        )
        self.assertAlmostEqual(
            diag["expected_steps_to_any_closed_class_from_initial_distribution"],
            0.5,
            places=9,
        )
        self.assertAlmostEqual(
            diag["expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution"],
            1.25,
            places=9,
        )
        self.assertAlmostEqual(
            diag["expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution"],
            1.25,
            places=9,
        )
        self.assertEqual(
            diag["expected_visit_counts_before_any_closed_class_entry_from_initial_distribution"],
            {"CC": 0.0, "CD": 0.25, "DC": 0.25, "DD": 0.0},
        )
        self.assertEqual(
            diag["expected_transition_counts_before_any_closed_class_entry_from_initial_distribution"],
            {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.25, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.25}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}},
        )
        self.assertEqual(
            diag["closed_class_asymptotic_decomposition_from_initial_distribution"],
            [
                {
                    "closed_class": ["CC"],
                    "entry_probability": 0.5,
                    "class_stationary_distribution": [1.0, 0.0, 0.0, 0.0],
                    "weighted_steady_state_contribution": [0.5, 0.0, 0.0, 0.0],
                    "class_avg_payoff_a": 3.0,
                    "class_avg_payoff_b": 3.0,
                },
                {
                    "closed_class": ["DD"],
                    "entry_probability": 0.5,
                    "class_stationary_distribution": [0.0, 0.0, 0.0, 1.0],
                    "weighted_steady_state_contribution": [0.0, 0.0, 0.0, 0.5],
                    "class_avg_payoff_a": 1.0,
                    "class_avg_payoff_b": 1.0,
                },
            ],
        )

    def test_recovery_proxy_matches_canonical_shock_examples(self) -> None:
        tft = _memory_one(strategy_id="tft", p_cc=1.0, p_cd=0.0, p_dc=1.0, p_dd=0.0)
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        extortion = {
            "family": "memory_one",
            "id": "extortion_chi3",
            "p0": 1.0,
            "p_cc": 0.8461538461538461,
            "p_cd": 0.5,
            "p_dc": 0.2692307692307692,
            "p_dd": 0.0,
        }

        tft_res = certify_memory_one_pair(tft, always_c)
        extortion_res = certify_memory_one_pair(extortion, always_c)

        self.assertEqual(tft_res["anti_vampire_scorecard"]["recovery_rounds"], 2)
        self.assertGreater(extortion_res["avg_payoff_a"], 3.0)
        self.assertGreater(extortion_res["anti_vampire_scorecard"]["recovery_rounds"], 40)

    def test_repair_abuse_proxy_flags_forgiveness_farming(self) -> None:
        generous_tft = _memory_one(strategy_id="mem1_generous_tft", p_cc=1.0, p_cd=0.3333333333, p_dc=1.0, p_dd=0.3333333333)
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        extortion = {
            "family": "memory_one",
            "id": "extortion_chi3",
            "p0": 1.0,
            "p_cc": 0.8461538461538461,
            "p_cd": 0.5,
            "p_dc": 0.2692307692307692,
            "p_dd": 0.0,
        }

        always_c_res = certify_memory_one_pair(always_c, extortion)
        generous_res = certify_memory_one_pair(generous_tft, extortion)

        self.assertGreater(always_c_res["anti_vampire_scorecard"]["repair_offer_count"], 0)
        self.assertGreater(always_c_res["anti_vampire_scorecard"]["repair_abuse_count"], 0)
        self.assertGreater(always_c_res["anti_vampire_scorecard"]["repair_abuse_rate"], 0.25)
        self.assertLessEqual(always_c_res["anti_vampire_scorecard"]["repair_abuse_rate_ci95_low"], always_c_res["anti_vampire_scorecard"]["repair_abuse_rate"])
        self.assertGreaterEqual(always_c_res["anti_vampire_scorecard"]["repair_abuse_rate_ci95_high"], always_c_res["anti_vampire_scorecard"]["repair_abuse_rate"])
        self.assertLess(generous_res["anti_vampire_scorecard"]["repair_abuse_rate"], always_c_res["anti_vampire_scorecard"]["repair_abuse_rate"])

    def test_screening_contract_exposes_binding_failures(self) -> None:
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        extortion = {
            "family": "memory_one",
            "id": "extortion_chi3",
            "p0": 1.0,
            "p_cc": 0.8461538461538461,
            "p_cd": 0.5,
            "p_dc": 0.2692307692307692,
            "p_dd": 0.0,
        }

        victim_res = certify_memory_one_pair(always_c, extortion)
        victim_contract = victim_res["anti_vampire_scorecard"]["screening_contract"]
        predator_res = certify_memory_one_pair(extortion, always_c)
        predator_contract = predator_res["anti_vampire_scorecard"]["screening_contract"]

        self.assertFalse(victim_contract["gate_pass"])
        self.assertIn("pairwise_fairness_gap_positive", victim_contract["failure_reasons"])
        self.assertEqual(victim_contract["checks"]["pairwise_fairness"]["threshold_value"], 0.0)
        self.assertEqual(victim_contract["checks"]["noisy_ecology"]["threshold_value"], 0.1)
        self.assertFalse(victim_contract["checks"]["pairwise_fairness"]["passed"])
        self.assertTrue(victim_contract["checks"]["noisy_ecology"]["passed"])
        self.assertFalse(victim_contract["checks"]["recovery_proxy"]["binding"])
        self.assertIsNone(victim_contract["checks"]["repair_proxy"]["passed"])

        self.assertFalse(predator_contract["gate_pass"])
        self.assertEqual(victim_contract["binding_gate_status"], "fail")
        self.assertEqual(victim_contract["gate_stability"], "stable")
        self.assertEqual(victim_contract["checks"]["pairwise_fairness"]["threshold_decision_state"], "exact_fail")
        self.assertEqual(victim_contract["checks"]["noisy_ecology"]["threshold_decision_state"], "clear_pass")
        self.assertIn("noisy_ecology_extraction_positive", predator_contract["failure_reasons"])
        self.assertEqual(predator_contract["binding_gate_status"], "fail")
        self.assertEqual(predator_contract["gate_stability"], "stable")
        self.assertTrue(predator_contract["checks"]["pairwise_fairness"]["passed"])
        self.assertFalse(predator_contract["checks"]["noisy_ecology"]["passed"])
        self.assertEqual(predator_contract["checks"]["noisy_ecology"]["threshold_decision_state"], "clear_fail")

    def test_noisy_ecology_separates_extortion_from_generous_tft(self) -> None:
        extortion = _memory_one(strategy_id="extortion_chi3", p_cc=1.0, p_cd=0.0, p_dc=(1.0 / 3.0), p_dd=0.0)
        generous_tft = _memory_one(strategy_id="mem1_generous_tft", p_cc=1.0, p_cd=0.1, p_dc=1.0, p_dd=0.0)
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)

        extortion_res = certify_memory_one_pair(extortion, always_c)
        generous_res = certify_memory_one_pair(generous_tft, always_c)

        self.assertGreater(extortion_res["anti_vampire_scorecard"]["ecology_gap_noisy"], 0.1)
        self.assertGreaterEqual(extortion_res["anti_vampire_scorecard"]["ecology_gap_noisy_stderr"], 0.0)
        self.assertGreaterEqual(extortion_res["anti_vampire_scorecard"]["ecology_gap_noisy_ci95_half_width"], 0.0)
        self.assertFalse(extortion_res["anti_vampire_scorecard"]["noisy_ecology_pass"])
        self.assertLessEqual(generous_res["anti_vampire_scorecard"]["ecology_gap_noisy"], 0.1)
        self.assertGreaterEqual(generous_res["anti_vampire_scorecard"]["ecology_gap_noisy_stderr"], 0.0)
        self.assertGreaterEqual(generous_res["anti_vampire_scorecard"]["ecology_gap_noisy_ci95_half_width"], 0.0)
        self.assertTrue(generous_res["anti_vampire_scorecard"]["noisy_ecology_pass"])

    def test_uncertainty_overlay_marks_borderline_binding_gate(self) -> None:
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        always_d = _memory_one(strategy_id="always_d", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        screening_spec = default_screening_spec()
        screening_spec["spec_id"] = "borderline_demo"
        screening_spec["pairwise_fairness"]["threshold_value"] = 10.0
        screening_spec["noisy_ecology"]["threshold_value"] = -1.1

        res = certify_memory_one_pair(always_c, always_d, screening_spec=screening_spec)
        contract = res["anti_vampire_scorecard"]["screening_contract"]

        self.assertTrue(contract["gate_pass"])
        self.assertEqual(contract["binding_gate_status"], "borderline")
        self.assertEqual(contract["gate_stability"], "borderline_sampling_uncertainty")
        self.assertEqual(contract["checks"]["noisy_ecology"]["threshold_decision_state"], "borderline_ci95_crosses_threshold")
        self.assertLessEqual(contract["checks"]["noisy_ecology"]["uncertainty_low"], contract["checks"]["noisy_ecology"]["threshold_value"])
        self.assertGreater(contract["checks"]["noisy_ecology"]["uncertainty_high"], contract["checks"]["noisy_ecology"]["threshold_value"])

    def test_custom_screening_spec_changes_thresholds_and_provenance(self) -> None:
        always_c = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        extortion = {
            "family": "memory_one",
            "id": "extortion_chi3",
            "p0": 1.0,
            "p_cc": 0.8461538461538461,
            "p_cd": 0.5,
            "p_dc": 0.2692307692307692,
            "p_dd": 0.0,
        }
        screening_spec = default_screening_spec()
        screening_spec["spec_id"] = "lenient_proxy_demo"
        screening_spec["pairwise_fairness"]["threshold_value"] = 5.0
        screening_spec["noisy_ecology"]["threshold_value"] = 1.0

        res = certify_memory_one_pair(always_c, extortion, screening_spec=screening_spec)

        self.assertEqual(res["screening_spec_ref"]["spec_id"], "lenient_proxy_demo")
        self.assertEqual(res["anti_vampire_scorecard"]["screening_spec_ref"]["spec_id"], "lenient_proxy_demo")
        self.assertEqual(
            res["screening_spec_ref"]["spec_fingerprint_sha256"],
            screening_spec_fingerprint_sha256(screening_spec),
        )
        contract = res["anti_vampire_scorecard"]["screening_contract"]
        self.assertTrue(contract["gate_pass"])
        self.assertEqual(contract["checks"]["pairwise_fairness"]["threshold_value"], 5.0)
        self.assertEqual(contract["checks"]["noisy_ecology"]["threshold_value"], 1.0)

    def test_execution_overrides_change_effective_screening_spec_fingerprint(self) -> None:
        a = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        b = _memory_one(strategy_id="always_d", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)

        base = certify_memory_one_pair(a, b)
        overridden = certify_memory_one_pair(a, b, ecology_rounds=20, ecology_reps=3)

        self.assertEqual(base["screening_spec_ref"]["spec_id"], overridden["screening_spec_ref"]["spec_id"])
        self.assertNotEqual(
            base["screening_spec_ref"]["spec_fingerprint_sha256"],
            overridden["screening_spec_ref"]["spec_fingerprint_sha256"],
        )


    def test_sampling_plan_fingerprint_changes_when_execution_budget_changes(self) -> None:
        a = _memory_one(strategy_id="always_c", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        b = _memory_one(strategy_id="always_d", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)

        base = certify_memory_one_pair(a, b)
        overridden = certify_memory_one_pair(a, b, ecology_rounds=20, ecology_reps=3)

        self.assertNotEqual(
            base["anti_vampire_scorecard"]["ecology_sampling_ref"]["sampling_plan_fingerprint_sha256"],
            overridden["anti_vampire_scorecard"]["ecology_sampling_ref"]["sampling_plan_fingerprint_sha256"],
        )
        self.assertEqual(
            base["anti_vampire_scorecard"]["repair_sampling_ref"]["sampling_plan_fingerprint_sha256"],
            overridden["anti_vampire_scorecard"]["repair_sampling_ref"]["sampling_plan_fingerprint_sha256"],
        )



    def test_strategy_fingerprint_changes_when_payload_changes_under_same_id(self) -> None:
        base = _memory_one(strategy_id="same", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        variant = _memory_one(strategy_id="same", p_cc=1.0, p_cd=1.0, p_dc=0.0, p_dd=1.0)

        self.assertNotEqual(
            strategy_fingerprint_sha256(base),
            strategy_fingerprint_sha256(variant),
        )

    def test_pairing_fingerprint_changes_when_strategy_order_changes(self) -> None:
        coop = _memory_one(strategy_id="coop", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        defect = _memory_one(strategy_id="defect", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)

        forward = certify_memory_one_pair(coop, defect)
        reverse = certify_memory_one_pair(defect, coop)

        self.assertNotEqual(
            forward["pairing_ref"]["pairing_fingerprint_sha256"],
            reverse["pairing_ref"]["pairing_fingerprint_sha256"],
        )

    def test_pairing_fingerprint_changes_when_strategy_payload_changes_under_same_id(self) -> None:
        base = _memory_one(strategy_id="candidate", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        variant = _memory_one(strategy_id="candidate", p_cc=1.0, p_cd=1.0, p_dc=0.0, p_dd=1.0)
        opp = _memory_one(strategy_id="opp", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)

        base_res = certify_memory_one_pair(base, opp)
        variant_res = certify_memory_one_pair(variant, opp)

        self.assertEqual(base_res["strategy_a"], variant_res["strategy_a"])
        self.assertNotEqual(
            base_res["strategy_a_ref"]["strategy_fingerprint_sha256"],
            variant_res["strategy_a_ref"]["strategy_fingerprint_sha256"],
        )
        self.assertNotEqual(
            base_res["pairing_ref"]["pairing_fingerprint_sha256"],
            variant_res["pairing_ref"]["pairing_fingerprint_sha256"],
        )

    def test_stage_game_ref_is_stable_and_ordered_vectors_are_declared(self) -> None:
        coop = _memory_one(strategy_id="coop", p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        defect = _memory_one(strategy_id="defect", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)

        res = certify_memory_one_pair(coop, defect)

        self.assertEqual(res["state_order"], ["CC", "CD", "DC", "DD"])
        self.assertEqual(res["stage_game_ref"]["stage_game_id"], "iterated_prisoners_dilemma_t5_r3_p1_s0")
        self.assertEqual(
            res["stage_game_ref"]["stage_game_fingerprint_sha256"],
            stage_game_fingerprint_sha256(),
        )


    def test_invalid_probability_rejected(self) -> None:
        bad = _memory_one(strategy_id="bad", p_cc=1.1, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        ok = _memory_one(strategy_id="ok", p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        with self.assertRaises(CertifyError):
            certify_memory_one_pair(bad, ok)


if __name__ == "__main__":
    unittest.main()
