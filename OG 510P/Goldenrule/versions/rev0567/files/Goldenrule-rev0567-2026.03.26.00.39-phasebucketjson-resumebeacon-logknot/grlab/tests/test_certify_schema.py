import json
import unittest
from pathlib import Path

import jsonschema

from grlab.certify import (
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


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "certify_memory_one_result.schema.json"
SCREENING_SPEC_SCHEMA_PATH = ROOT / "schemas" / "certify_memory_one_screening_spec.schema.json"
SCREENING_SPEC_EXAMPLE_PATH = ROOT / "examples" / "certify" / "canonical_proxy_v1.json"


def _memory_one(
    *,
    strategy_id: str,
    p0: float,
    p_cc: float,
    p_cd: float,
    p_dc: float,
    p_dd: float,
) -> dict[str, object]:
    return {
        "family": "memory_one",
        "id": strategy_id,
        "p0": p0,
        "p_cc": p_cc,
        "p_cd": p_cd,
        "p_dc": p_dc,
        "p_dd": p_dd,
    }


class CertifySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.screening_spec_schema = json.loads(SCREENING_SPEC_SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.screening_spec_example = json.loads(SCREENING_SPEC_EXAMPLE_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(cls.schema)
        jsonschema.Draft202012Validator.check_schema(cls.screening_spec_schema)


    def test_screening_spec_example_matches_schema(self) -> None:
        jsonschema.validate(self.screening_spec_example, self.screening_spec_schema)

    def test_default_screening_spec_matches_shipped_canonical_example(self) -> None:
        self.assertEqual(default_screening_spec(), self.screening_spec_example)
        self.assertEqual(
            screening_spec_fingerprint_sha256(default_screening_spec()),
            screening_spec_fingerprint_sha256(self.screening_spec_example),
        )

    def test_exact_stationary_payload_matches_schema(self) -> None:
        a = _memory_one(strategy_id="always_c", p0=1.0, p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        b = _memory_one(strategy_id="always_d", p0=0.0, p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)

        payload = certify_memory_one_pair(a, b, ecology_rounds=20, ecology_reps=3)

        jsonschema.validate(payload, self.schema)
        self.assertEqual(payload["steady_state_method"], "exact_stationary")
        self.assertFalse(payload["anti_vampire_scorecard"]["screening_contract"]["gate_pass"])
        self.assertRegex(payload["screening_spec_ref"]["spec_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["stage_game_ref"]["stage_game_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(payload["state_order"], ["CC", "CD", "DC", "DD"])
        self.assertRegex(payload["strategy_a_ref"]["strategy_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["strategy_b_ref"]["strategy_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["pairing_ref"]["pairing_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["uncertainty_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["proxy_measurement_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["steady_state_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["opening_distribution_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["transition_kernel_contract_ref"]["contract_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(len(payload["transition_matrix"]), 4)
        self.assertTrue(all(len(row) == 4 for row in payload["transition_matrix"]))
        self.assertEqual(payload["schema_version"], 21)
        self.assertEqual(payload["asymptotic_distribution_method"], "closed_class_exact_mixture_from_initial_distribution")
        self.assertEqual(payload["asymptotic_distribution_from_initial_distribution"], [0.0, 1.0, 0.0, 0.0])
        self.assertAlmostEqual(payload["asymptotic_avg_payoff_a_from_initial_distribution"], 0.0, places=9)
        self.assertAlmostEqual(payload["asymptotic_avg_payoff_b_from_initial_distribution"], 5.0, places=9)
        self.assertAlmostEqual(payload["steady_state_distribution_l1_distance_to_asymptotic_distribution"], 0.0, places=9)
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
            payload["transition_graph_diagnostics"]["expected_steps_to_any_closed_class_from_initial_distribution"],
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
        self.assertRegex(payload["anti_vampire_scorecard"]["ecology_sampling_ref"]["sampling_plan_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["anti_vampire_scorecard"]["repair_sampling_ref"]["sampling_plan_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["anti_vampire_scorecard"]["ecology_sampling_ref"]["sampling_plan_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["anti_vampire_scorecard"]["repair_sampling_ref"]["sampling_plan_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertGreaterEqual(payload["anti_vampire_scorecard"]["ecology_gap_noisy_stderr"], 0.0)
        self.assertGreaterEqual(payload["anti_vampire_scorecard"]["ecology_gap_noisy_ci95_half_width"], 0.0)
        self.assertGreaterEqual(payload["anti_vampire_scorecard"]["repair_abuse_rate_ci95_high"], payload["anti_vampire_scorecard"]["repair_abuse_rate_ci95_low"])
        self.assertGreaterEqual(payload["anti_vampire_scorecard"]["ecology_gap_noisy_stderr"], 0.0)
        self.assertGreaterEqual(payload["anti_vampire_scorecard"]["ecology_gap_noisy_ci95_half_width"], 0.0)
        self.assertGreaterEqual(payload["anti_vampire_scorecard"]["repair_abuse_rate_ci95_high"], payload["anti_vampire_scorecard"]["repair_abuse_rate_ci95_low"])


    def test_cesaro_payload_matches_schema(self) -> None:
        wsls = _memory_one(strategy_id="wsls", p0=1.0, p_cc=1.0, p_cd=1.0, p_dc=0.0, p_dd=0.0)
        always_c = _memory_one(strategy_id="always_c", p0=1.0, p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)

        payload = certify_memory_one_pair(wsls, always_c, ecology_rounds=20, ecology_reps=3)

        jsonschema.validate(payload, self.schema)
        self.assertEqual(payload["steady_state_method"], "cesaro_from_initial_distribution")
        self.assertTrue(payload["anti_vampire_scorecard"]["screening_contract"]["gate_pass"])
        self.assertRegex(payload["screening_spec_ref"]["spec_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["stage_game_ref"]["stage_game_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(payload["state_order"], ["CC", "CD", "DC", "DD"])
        self.assertRegex(payload["strategy_a_ref"]["strategy_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["strategy_b_ref"]["strategy_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["pairing_ref"]["pairing_fingerprint_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(payload["transition_graph_diagnostics"]["closed_classes"], [["CC"], ["DC"]])
        self.assertEqual(payload["asymptotic_distribution_method"], "closed_class_exact_mixture_from_initial_distribution")
        self.assertEqual(payload["asymptotic_distribution_from_initial_distribution"], [1.0, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(payload["asymptotic_avg_payoff_a_from_initial_distribution"], 3.0, places=9)
        self.assertAlmostEqual(payload["asymptotic_avg_payoff_b_from_initial_distribution"], 3.0, places=9)
        self.assertAlmostEqual(payload["steady_state_distribution_l1_distance_to_asymptotic_distribution"], 0.0, places=9)
        self.assertEqual(
            payload["transition_graph_diagnostics"]["closed_class_entry_probabilities_from_initial_distribution"],
            [
                {"closed_class": ["CC"], "entry_probability": 1.0, "conditional_expected_entry_steps_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": 0.0, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": 0.0, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "CD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DC": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}, "DD": {"CC": 0.0, "CD": 0.0, "DC": 0.0, "DD": 0.0}}},
                {"closed_class": ["DC"], "entry_probability": 0.0, "conditional_expected_entry_steps_from_initial_distribution": None, "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": None, "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": None, "conditional_expected_visit_counts_before_entry_from_initial_distribution": {"CC": None, "CD": None, "DC": None, "DD": None}, "conditional_expected_transition_counts_before_entry_from_initial_distribution": {"CC": {"CC": None, "CD": None, "DC": None, "DD": None}, "CD": {"CC": None, "CD": None, "DC": None, "DD": None}, "DC": {"CC": None, "CD": None, "DC": None, "DD": None}, "DD": {"CC": None, "CD": None, "DC": None, "DD": None}}},
            ],
        )
        self.assertEqual(
            payload["transition_graph_diagnostics"]["closed_class_asymptotic_decomposition_from_initial_distribution"],
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


    def test_strategy_and_pairing_fingerprints_match_payload_refs(self) -> None:
        a = _memory_one(strategy_id="always_c", p0=1.0, p_cc=1.0, p_cd=1.0, p_dc=1.0, p_dd=1.0)
        b = _memory_one(strategy_id="always_d", p0=0.0, p_cc=0.0, p_cd=0.0, p_dc=0.0, p_dd=0.0)
        screening_spec = default_screening_spec()
        screening_spec["noisy_ecology"]["rounds"] = 20
        screening_spec["noisy_ecology"]["repetitions"] = 3

        payload = certify_memory_one_pair(a, b, ecology_rounds=20, ecology_reps=3)

        self.assertEqual(payload["strategy_a_ref"]["strategy_fingerprint_sha256"], strategy_fingerprint_sha256(a))
        self.assertEqual(payload["uncertainty_contract_ref"]["contract_fingerprint_sha256"], uncertainty_contract_fingerprint_sha256())
        self.assertEqual(payload["proxy_measurement_contract_ref"]["contract_fingerprint_sha256"], proxy_measurement_contract_fingerprint_sha256())
        self.assertEqual(payload["anti_vampire_scorecard"]["uncertainty_contract_ref"], payload["uncertainty_contract_ref"])
        self.assertEqual(payload["anti_vampire_scorecard"]["proxy_measurement_contract_ref"], payload["proxy_measurement_contract_ref"])
        self.assertEqual(payload["steady_state_contract_ref"]["contract_fingerprint_sha256"], steady_state_contract_fingerprint_sha256())
        self.assertEqual(payload["anti_vampire_scorecard"]["steady_state_contract_ref"], payload["steady_state_contract_ref"])
        self.assertEqual(payload["opening_distribution_contract_ref"]["contract_fingerprint_sha256"], opening_distribution_contract_fingerprint_sha256())
        self.assertEqual(payload["anti_vampire_scorecard"]["opening_distribution_contract_ref"], payload["opening_distribution_contract_ref"])
        self.assertEqual(payload["transition_kernel_contract_ref"]["contract_fingerprint_sha256"], transition_kernel_contract_fingerprint_sha256())
        self.assertEqual(payload["anti_vampire_scorecard"]["transition_kernel_contract_ref"], payload["transition_kernel_contract_ref"])
        self.assertEqual(payload["stage_game_ref"]["stage_game_fingerprint_sha256"], stage_game_fingerprint_sha256())
        self.assertEqual(
            payload["anti_vampire_scorecard"]["ecology_sampling_ref"]["sampling_plan_fingerprint_sha256"],
            ecology_sampling_plan_fingerprint_sha256(screening_spec),
        )
        self.assertEqual(
            payload["anti_vampire_scorecard"]["repair_sampling_ref"]["sampling_plan_fingerprint_sha256"],
            repair_sampling_plan_fingerprint_sha256(screening_spec),
        )
        self.assertEqual(payload["strategy_b_ref"]["strategy_fingerprint_sha256"], strategy_fingerprint_sha256(b))
        self.assertEqual(
            payload["pairing_ref"]["pairing_fingerprint_sha256"],
            pairing_fingerprint_sha256(a, b, screening_spec),
        )


if __name__ == "__main__":
    unittest.main()
