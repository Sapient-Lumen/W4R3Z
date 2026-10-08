import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class CertifyCliTests(unittest.TestCase):
    def test_certify_memory_one_pair(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a.json"
            b = root / "b.json"
            a.write_text(
                json.dumps(
                    {
                        "family": "memory_one",
                        "id": "a",
                        "p0": 1.0,
                        "p_cc": 1.0,
                        "p_cd": 1.0,
                        "p_dc": 1.0,
                        "p_dd": 1.0,
                    }
                ),
                encoding="utf-8",
            )
            b.write_text(
                json.dumps(
                    {
                        "family": "memory_one",
                        "id": "b",
                        "p0": 0.0,
                        "p_cc": 0.0,
                        "p_cd": 0.0,
                        "p_dc": 0.0,
                        "p_dd": 0.0,
                    }
                ),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "certify",
                    "--a",
                    str(a),
                    "--b",
                    str(b),
                    "--ecology-rounds",
                    "50",
                    "--ecology-reps",
                    "5",
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["schema_version"], 21)
            self.assertEqual(payload["screening_spec_ref"]["spec_id"], "canonical_proxy_v1")
            self.assertEqual(payload["stage_game_ref"]["stage_game_id"], "iterated_prisoners_dilemma_t5_r3_p1_s0")
            self.assertRegex(payload["stage_game_ref"]["stage_game_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(payload["state_order"], ["CC", "CD", "DC", "DD"])
            self.assertRegex(payload["screening_spec_ref"]["spec_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(payload["strategy_a_ref"]["strategy_id"], "a")
            self.assertEqual(payload["strategy_b_ref"]["strategy_id"], "b")
            self.assertRegex(payload["strategy_a_ref"]["strategy_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(payload["strategy_b_ref"]["strategy_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(payload["pairing_ref"]["pairing_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(payload["uncertainty_contract_ref"]["contract_id"], "mc_interval_semantics_v1")
            self.assertEqual(payload["proxy_measurement_contract_ref"]["contract_id"], "anti_vampire_proxy_measurement_v1")
            self.assertEqual(payload["steady_state_contract_ref"]["contract_id"], "memory_one_stationary_or_cesaro_v1")
            self.assertEqual(payload["opening_distribution_contract_ref"]["contract_id"], "memory_one_independent_p0_product_v1")
            self.assertEqual(payload["transition_kernel_contract_ref"]["contract_id"], "memory_one_state_product_kernel_v1")
            self.assertRegex(payload["uncertainty_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(payload["opening_distribution_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(payload["kind"], "certify_memory_one_result")
            self.assertEqual(payload["anti_vampire_scorecard"]["screening_spec_ref"]["spec_id"], "canonical_proxy_v1")
            self.assertAlmostEqual(payload["avg_payoff_a"], 0.0, places=9)
            self.assertAlmostEqual(payload["avg_payoff_b"], 5.0, places=9)
            self.assertEqual(payload["steady_state_method"], "exact_stationary")
            self.assertEqual(payload["initial_distribution"], [0.0, 1.0, 0.0, 0.0])
            self.assertEqual(payload["asymptotic_distribution_method"], "closed_class_exact_mixture_from_initial_distribution")
            self.assertEqual(payload["asymptotic_distribution_from_initial_distribution"], [0.0, 1.0, 0.0, 0.0])
            self.assertAlmostEqual(payload["asymptotic_avg_payoff_a_from_initial_distribution"], 0.0, places=9)
            self.assertAlmostEqual(payload["asymptotic_avg_payoff_b_from_initial_distribution"], 5.0, places=9)
            self.assertAlmostEqual(payload["steady_state_distribution_l1_distance_to_asymptotic_distribution"], 0.0, places=9)
            self.assertIn("anti_vampire_scorecard", payload)
            self.assertEqual(payload["anti_vampire_scorecard"]["ecology_rounds"], 50)
            self.assertEqual(payload["anti_vampire_scorecard"]["ecology_repetitions"], 5)
            self.assertEqual(payload["anti_vampire_scorecard"]["recovery_rounds"], 41)
            self.assertEqual(payload["anti_vampire_scorecard"]["repair_abuse_rate"], 0.0)
            self.assertEqual(payload["anti_vampire_scorecard"]["repair_offer_count"], 0)
            self.assertEqual(payload["anti_vampire_scorecard"]["repair_abuse_count"], 0)
            self.assertEqual(payload["anti_vampire_scorecard"]["repair_abuse_rate_ci95_low"], 0.0)
            self.assertEqual(payload["anti_vampire_scorecard"]["repair_abuse_rate_ci95_high"], 0.0)
            self.assertGreaterEqual(payload["anti_vampire_scorecard"]["ecology_gap_noisy_stderr"], 0.0)
            self.assertGreaterEqual(payload["anti_vampire_scorecard"]["ecology_gap_noisy_ci95_half_width"], 0.0)
            self.assertEqual(payload["anti_vampire_scorecard"]["ecology_estimate_kind"], "replicated_rollout_mean")
            self.assertEqual(payload["anti_vampire_scorecard"]["uncertainty_contract_ref"], payload["uncertainty_contract_ref"])
            self.assertEqual(payload["anti_vampire_scorecard"]["proxy_measurement_contract_ref"], payload["proxy_measurement_contract_ref"])
            self.assertEqual(payload["anti_vampire_scorecard"]["steady_state_contract_ref"], payload["steady_state_contract_ref"])
            self.assertEqual(payload["anti_vampire_scorecard"]["opening_distribution_contract_ref"], payload["opening_distribution_contract_ref"])
            self.assertEqual(payload["anti_vampire_scorecard"]["transition_kernel_contract_ref"], payload["transition_kernel_contract_ref"])
            self.assertEqual(payload["transition_matrix"], [[0.0, 1.0, 0.0, 0.0]] * 4)
            self.assertTrue(payload["transition_graph_diagnostics"]["reducible"])
            self.assertEqual(payload["transition_graph_diagnostics"]["closed_classes"], [["CD"]])
            self.assertEqual(payload["transition_graph_diagnostics"]["absorbing_states"], ["CD"])
            self.assertEqual(
                payload["transition_graph_diagnostics"]["closed_class_entry_probabilities_from_initial_distribution"],
                [{"closed_class": ["CD"], "entry_probability": 1.0, "conditional_expected_entry_steps_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 0.0, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}}],
            )
            self.assertEqual(
                payload["transition_graph_diagnostics"]["closed_class_asymptotic_decomposition_from_initial_distribution"],
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
            self.assertFalse(
                payload["transition_graph_diagnostics"]["multiple_closed_classes_with_positive_entry_probability_from_initial_distribution"]
            )
            self.assertAlmostEqual(
                payload["transition_graph_diagnostics"]["expected_steps_to_any_closed_class_from_initial_distribution"],
                0.0,
                places=9,
            )
            self.assertAlmostEqual(
                payload["transition_graph_diagnostics"]["expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution"],
                0.0,
                places=9,
            )
            self.assertAlmostEqual(
                payload["transition_graph_diagnostics"]["expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution"],
                0.0,
                places=9,
            )
            self.assertEqual(
                payload["transition_graph_diagnostics"]["expected_visit_counts_before_any_closed_class_entry_from_initial_distribution"],
                {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0},
            )
            self.assertEqual(
                payload["transition_graph_diagnostics"]["expected_transition_counts_before_any_closed_class_entry_from_initial_distribution"],
                {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}},
            )
            self.assertFalse(payload["anti_vampire_scorecard"]["screening_contract"]["gate_pass"])
            self.assertIn(
                "pairwise_fairness_gap_positive",
                payload["anti_vampire_scorecard"]["screening_contract"]["failure_reasons"],
            )


    def test_certify_memory_one_pair_with_custom_screening_spec(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a.json"
            b = root / "b.json"
            spec = root / "screening_spec.json"
            a.write_text(
                json.dumps(
                    {
                        "family": "memory_one",
                        "id": "a",
                        "p0": 1.0,
                        "p_cc": 1.0,
                        "p_cd": 1.0,
                        "p_dc": 1.0,
                        "p_dd": 1.0,
                    }
                ),
                encoding="utf-8",
            )
            b.write_text(
                json.dumps(
                    {
                        "family": "memory_one",
                        "id": "b",
                        "p0": 0.0,
                        "p_cc": 0.0,
                        "p_cd": 0.0,
                        "p_dc": 0.0,
                        "p_dd": 0.0,
                    }
                ),
                encoding="utf-8",
            )
            spec.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "certify_memory_one_screening_spec",
                        "spec_id": "strict_demo",
                        "status": "screening_proxy_contract",
                        "steady_state": {"cesaro_fallback_steps": 4096},
                        "pairwise_fairness": {"metric": "payoff_gap", "threshold_kind": "max", "threshold_value": 10.0},
                        "recovery_proxy": {
                            "metric": "recovery_rounds",
                            "shock_protocol": "opponent_single_defection_from_mutual_cooperation_then_zero_noise_expected_payoff_recovery",
                            "epsilon": 0.25,
                            "horizon": 40,
                            "cc_mass_min": 0.8,
                            "threshold_kind": "max",
                            "threshold_value": 40
                        },
                        "repair_proxy": {
                            "metric": "repair_abuse_rate",
                            "k": 3,
                            "rounds": 200,
                            "repetitions": 30,
                            "noise": 0.0,
                            "threshold_kind": None,
                            "threshold_value": None,
                            "threshold_status": "pending"
                        },
                        "noisy_ecology": {
                            "metric": "ecology_gap_noisy",
                            "threshold_kind": "max",
                            "threshold_value": 10.0,
                            "noise": 0.02,
                            "rounds": 20,
                            "repetitions": 3,
                            "pool": [
                                {
                                    "family": "memory_one",
                                    "id": "always_c",
                                    "p0": 1.0,
                                    "p_cc": 1.0,
                                    "p_cd": 1.0,
                                    "p_dc": 1.0,
                                    "p_dd": 1.0
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    "python3",
                    "-m",
                    "grlab",
                    "certify",
                    "--a",
                    str(a),
                    "--b",
                    str(b),
                    "--screening-spec",
                    str(spec),
                ],
                cwd=str(Path(__file__).resolve().parents[2]),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["screening_spec_ref"]["spec_id"], "strict_demo")
            self.assertRegex(payload["screening_spec_ref"]["spec_fingerprint_sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(payload["anti_vampire_scorecard"]["screening_contract"]["gate_pass"])


if __name__ == "__main__":
    unittest.main()
