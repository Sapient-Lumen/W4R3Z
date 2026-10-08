from __future__ import annotations

import copy
import hashlib
import json
import math
import random
from typing import Any, Mapping


class CertifyError(ValueError):
    pass


_MEMORY_ONE_KEYS = ("p_cc", "p_cd", "p_dc", "p_dd")
_DEFAULT_SCREENING_SPEC: dict[str, Any] = {
    "schema_version": 1,
    "kind": "certify_memory_one_screening_spec",
    "spec_id": "canonical_proxy_v1",
    "status": "screening_proxy_contract",
    "steady_state": {
        "cesaro_fallback_steps": 4096,
    },
    "pairwise_fairness": {
        "metric": "payoff_gap",
        "threshold_kind": "max",
        "threshold_value": 0.0,
    },
    "recovery_proxy": {
        "metric": "recovery_rounds",
        "shock_protocol": "opponent_single_defection_from_mutual_cooperation_then_zero_noise_expected_payoff_recovery",
        "epsilon": 0.25,
        "horizon": 40,
        "cc_mass_min": 0.8,
        "threshold_kind": "max",
        "threshold_value": 40,
    },
    "repair_proxy": {
        "metric": "repair_abuse_rate",
        "k": 3,
        "rounds": 200,
        "repetitions": 30,
        "noise": 0.0,
        "threshold_kind": None,
        "threshold_value": None,
        "threshold_status": "pending",
    },
    "noisy_ecology": {
        "metric": "ecology_gap_noisy",
        "threshold_kind": "max",
        "threshold_value": 0.1,
        "noise": 0.02,
        "rounds": 200,
        "repetitions": 30,
        "pool": [
            {
                "family": "memory_one",
                "id": "tft",
                "p0": 1.0,
                "p_cc": 1.0,
                "p_cd": 1.0,
                "p_dc": 0.0,
                "p_dd": 1.0,
            },
            {
                "family": "memory_one",
                "id": "wsls",
                "p0": 1.0,
                "p_cc": 1.0,
                "p_cd": 1.0,
                "p_dc": 0.0,
                "p_dd": 0.0,
            },
            {
                "family": "memory_one",
                "id": "mem1_generous_tft",
                "p0": 1.0,
                "p_cc": 1.0,
                "p_cd": 1.0,
                "p_dc": 0.1,
                "p_dd": 1.0,
            },
            {
                "family": "memory_one",
                "id": "grim_trigger",
                "p0": 1.0,
                "p_cc": 1.0,
                "p_cd": 1.0,
                "p_dc": 0.0,
                "p_dd": 0.0,
            },
            {
                "family": "memory_one",
                "id": "always_c",
                "p0": 1.0,
                "p_cc": 1.0,
                "p_cd": 1.0,
                "p_dc": 1.0,
                "p_dd": 1.0,
            },
        ],
    },
}

_STATE_ORDER = ("CC", "CD", "DC", "DD")

_PAYOFFS = {
    ("C", "C"): (3.0, 3.0),
    ("C", "D"): (0.0, 5.0),
    ("D", "C"): (5.0, 0.0),
    ("D", "D"): (1.0, 1.0),
}
_PAYOFFS_A = [3.0, 0.0, 5.0, 1.0]
_PAYOFFS_B = [3.0, 5.0, 0.0, 1.0]

_ECOLOGY_SAMPLING_SEED_BASE = 7
_ECOLOGY_SAMPLING_SEED_STRIDE = 1000
_REPAIR_SAMPLING_SEED_BASE = 17
_REPAIR_SAMPLING_SEED_STRIDE = 1000

_UNCERTAINTY_CONTRACT_ID = "mc_interval_semantics_v1"
_ECOLOGY_INTERVAL_METHOD = "normal_approximation"
_ECOLOGY_INTERVAL_CONFIDENCE_LEVEL = 0.95
_ECOLOGY_INTERVAL_Z = 1.96
_REPAIR_INTERVAL_METHOD = "wilson_score"
_REPAIR_INTERVAL_CONFIDENCE_LEVEL = 0.95
_REPAIR_INTERVAL_Z = 1.96

_PROXY_MEASUREMENT_CONTRACT_ID = "anti_vampire_proxy_measurement_v1"

_STEADY_STATE_CONTRACT_ID = "memory_one_stationary_or_cesaro_v1"

_OPENING_DISTRIBUTION_CONTRACT_ID = "memory_one_independent_p0_product_v1"
_TRANSITION_KERNEL_CONTRACT_ID = "memory_one_state_product_kernel_v1"
_STATIONARY_SOLVER_METHOD = "gaussian_elimination_partial_pivot_4x4"
_STATIONARY_SOLVER_PIVOT_EPSILON = 1e-12
_STATIONARY_ZERO_CLEANUP_ABS_TOL = 1e-12
_STATIONARY_NEGATIVE_MASS_ABS_TOL = 1e-9
_STEADY_STATE_FALLBACK_TRIGGER = "stationary_system_singular_or_ill_conditioned"
_STEADY_STATE_FALLBACK_METHOD = "cesaro_average_from_declared_initial_distribution"
_GRAPH_EDGE_EPSILON = 1e-12


def default_screening_spec() -> dict[str, Any]:
    return copy.deepcopy(_DEFAULT_SCREENING_SPEC)


def _canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _canonical_screening_spec_payload(screening_spec: Mapping[str, Any]) -> dict[str, Any]:
    ecology = screening_spec["noisy_ecology"]
    pool_payload: list[dict[str, Any]] = []
    for entry in ecology["pool"]:
        if isinstance(entry, Mapping):
            pool_payload.append(
                {
                    "family": str(entry["family"]),
                    "id": str(entry["id"]),
                    "p0": float(entry["p0"]),
                    "p_cc": float(entry["p_cc"]),
                    "p_cd": float(entry["p_cd"]),
                    "p_dc": float(entry["p_dc"]),
                    "p_dd": float(entry["p_dd"]),
                }
            )
            continue
        opponent_id, params = entry
        p0, p_cc, p_cd, p_dc, p_dd = params
        pool_payload.append(
            {
                "family": "memory_one",
                "id": str(opponent_id),
                "p0": float(p0),
                "p_cc": float(p_cc),
                "p_cd": float(p_cd),
                "p_dc": float(p_dc),
                "p_dd": float(p_dd),
            }
        )
    return {
        "schema_version": int(screening_spec["schema_version"]),
        "kind": str(screening_spec["kind"]),
        "spec_id": str(screening_spec["spec_id"]),
        "status": str(screening_spec["status"]),
        "steady_state": {
            "cesaro_fallback_steps": int(screening_spec["steady_state"]["cesaro_fallback_steps"]),
        },
        "pairwise_fairness": {
            "metric": str(screening_spec["pairwise_fairness"]["metric"]),
            "threshold_kind": str(screening_spec["pairwise_fairness"]["threshold_kind"]),
            "threshold_value": float(screening_spec["pairwise_fairness"]["threshold_value"]),
        },
        "recovery_proxy": {
            "metric": str(screening_spec["recovery_proxy"]["metric"]),
            "shock_protocol": str(screening_spec["recovery_proxy"]["shock_protocol"]),
            "epsilon": float(screening_spec["recovery_proxy"]["epsilon"]),
            "horizon": int(screening_spec["recovery_proxy"]["horizon"]),
            "cc_mass_min": float(screening_spec["recovery_proxy"]["cc_mass_min"]),
            "threshold_kind": str(screening_spec["recovery_proxy"]["threshold_kind"]),
            "threshold_value": float(screening_spec["recovery_proxy"]["threshold_value"]),
        },
        "repair_proxy": {
            "metric": str(screening_spec["repair_proxy"]["metric"]),
            "k": int(screening_spec["repair_proxy"]["k"]),
            "rounds": int(screening_spec["repair_proxy"]["rounds"]),
            "repetitions": int(screening_spec["repair_proxy"]["repetitions"]),
            "noise": float(screening_spec["repair_proxy"]["noise"]),
            "threshold_kind": screening_spec["repair_proxy"]["threshold_kind"],
            "threshold_value": screening_spec["repair_proxy"]["threshold_value"],
            "threshold_status": str(screening_spec["repair_proxy"]["threshold_status"]),
        },
        "noisy_ecology": {
            "metric": str(ecology["metric"]),
            "threshold_kind": str(ecology["threshold_kind"]),
            "threshold_value": float(ecology["threshold_value"]),
            "noise": float(ecology["noise"]),
            "rounds": int(ecology["rounds"]),
            "repetitions": int(ecology["repetitions"]),
            "pool": pool_payload,
        },
    }


def screening_spec_fingerprint_sha256(screening_spec: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_screening_spec_payload(screening_spec))).hexdigest()


def _canonical_memory_one_strategy_payload(strategy: Mapping[str, Any]) -> dict[str, Any]:
    p0, p_cc, p_cd, p_dc, p_dd = _extract_memory_one_params(strategy, "strategy")
    strategy_id = strategy.get("id")
    if strategy_id is None:
        strategy_id = None
    elif not isinstance(strategy_id, str):
        strategy_id = str(strategy_id)
    return {
        "family": "memory_one",
        "id": strategy_id,
        "p0": float(p0),
        "p_cc": float(p_cc),
        "p_cd": float(p_cd),
        "p_dc": float(p_dc),
        "p_dd": float(p_dd),
    }


def _canonical_stage_game_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "memory_one_stage_game_ref",
        "stage_game_id": "iterated_prisoners_dilemma_t5_r3_p1_s0",
        "state_order": list(_STATE_ORDER),
        "payoff_matrix": {
            "CC": [float(_PAYOFFS[("C", "C")][0]), float(_PAYOFFS[("C", "C")][1])],
            "CD": [float(_PAYOFFS[("C", "D")][0]), float(_PAYOFFS[("C", "D")][1])],
            "DC": [float(_PAYOFFS[("D", "C")][0]), float(_PAYOFFS[("D", "C")][1])],
            "DD": [float(_PAYOFFS[("D", "D")][0]), float(_PAYOFFS[("D", "D")][1])],
        },
    }


def stage_game_fingerprint_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_stage_game_payload())).hexdigest()


def _stage_game_ref() -> dict[str, Any]:
    payload = _canonical_stage_game_payload()
    return {
        "schema_version": int(payload["schema_version"]),
        "kind": str(payload["kind"]),
        "stage_game_id": str(payload["stage_game_id"]),
        "stage_game_fingerprint_sha256": stage_game_fingerprint_sha256(),
    }


def _canonical_ecology_sampling_plan_payload(screening_spec: Mapping[str, Any]) -> dict[str, Any]:
    ecology = screening_spec["noisy_ecology"]
    return {
        "schema_version": 1,
        "kind": "replicated_rollout_sampling_plan",
        "sampling_plan_id": "ecology_replicated_rollout_ap_v1",
        "estimate_kind": "replicated_rollout_mean",
        "rounds": int(ecology["rounds"]),
        "repetitions": int(ecology["repetitions"]),
        "noise": float(ecology["noise"]),
        "seed_schedule": {
            "kind": "arithmetic_progression",
            "seed_base": _ECOLOGY_SAMPLING_SEED_BASE,
            "seed_stride": _ECOLOGY_SAMPLING_SEED_STRIDE,
        },
    }


def _canonical_repair_sampling_plan_payload(screening_spec: Mapping[str, Any]) -> dict[str, Any]:
    repair = screening_spec["repair_proxy"]
    return {
        "schema_version": 1,
        "kind": "repair_offer_sampling_plan",
        "sampling_plan_id": "repair_offer_proxy_ap_v1",
        "estimate_kind": "repair_offer_rate",
        "rounds": int(repair["rounds"]),
        "repetitions": int(repair["repetitions"]),
        "noise": float(repair["noise"]),
        "repair_proxy_k": int(repair["k"]),
        "seed_schedule": {
            "kind": "arithmetic_progression",
            "seed_base": _REPAIR_SAMPLING_SEED_BASE,
            "seed_stride": _REPAIR_SAMPLING_SEED_STRIDE,
        },
    }


def _canonical_uncertainty_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "certify_memory_one_uncertainty_contract",
        "contract_id": _UNCERTAINTY_CONTRACT_ID,
        "ecology_metric": "ecology_gap_noisy",
        "ecology_estimate_kind": "replicated_rollout_mean",
        "ecology_interval_method": _ECOLOGY_INTERVAL_METHOD,
        "ecology_confidence_level": _ECOLOGY_INTERVAL_CONFIDENCE_LEVEL,
        "ecology_z_value": _ECOLOGY_INTERVAL_Z,
        "repair_metric": "repair_abuse_rate",
        "repair_estimate_kind": "repair_offer_rate",
        "repair_interval_method": _REPAIR_INTERVAL_METHOD,
        "repair_confidence_level": _REPAIR_INTERVAL_CONFIDENCE_LEVEL,
        "repair_z_value": _REPAIR_INTERVAL_Z,
    }


def _canonical_proxy_measurement_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "certify_memory_one_proxy_measurement_contract",
        "contract_id": _PROXY_MEASUREMENT_CONTRACT_ID,
        "pairwise_fairness_metric_semantics": "avg_payoff_b_minus_avg_payoff_a",
        "ecology_member_metric_semantics": "avg_payoff_a_minus_avg_payoff_b",
        "ecology_pool_aggregation": "equal_weight_unweighted_mean",
        "recovery_metric_semantics": (
            "rounds_until_expected_payoff_a_ge_3_minus_epsilon_and_cc_mass_ge_cc_mass_min_"
            "after_canonical_single_opponent_defection_shock"
        ),
        "repair_offer_event_semantics": "opponent_action_transition_d_to_c_between_adjacent_rounds",
        "repair_abuse_event_semantics": (
            "fresh_opponent_defection_within_k_rounds_and_positive_cumulative_payoff_gap_b_minus_a_"
            "over_offer_window_inclusive_of_offer_round"
        ),
    }


def proxy_measurement_contract_fingerprint_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_proxy_measurement_contract_payload())).hexdigest()


def _proxy_measurement_contract_ref() -> dict[str, Any]:
    payload = _canonical_proxy_measurement_contract_payload()
    return {
        "schema_version": int(payload["schema_version"]),
        "kind": str(payload["kind"]),
        "contract_id": str(payload["contract_id"]),
        "contract_fingerprint_sha256": proxy_measurement_contract_fingerprint_sha256(),
    }


def _canonical_steady_state_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "certify_memory_one_steady_state_contract",
        "contract_id": _STEADY_STATE_CONTRACT_ID,
        "exact_method": _STATIONARY_SOLVER_METHOD,
        "pivot_epsilon": _STATIONARY_SOLVER_PIVOT_EPSILON,
        "zero_cleanup_abs_tolerance": _STATIONARY_ZERO_CLEANUP_ABS_TOL,
        "negative_mass_abs_tolerance": _STATIONARY_NEGATIVE_MASS_ABS_TOL,
        "fallback_trigger": _STEADY_STATE_FALLBACK_TRIGGER,
        "fallback_method": _STEADY_STATE_FALLBACK_METHOD,
        "fallback_steps_parameter": "screening_spec.steady_state.cesaro_fallback_steps",
    }


def steady_state_contract_fingerprint_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_steady_state_contract_payload())).hexdigest()


def _steady_state_contract_ref() -> dict[str, Any]:
    payload = _canonical_steady_state_contract_payload()
    return {
        "schema_version": int(payload["schema_version"]),
        "kind": str(payload["kind"]),
        "contract_id": str(payload["contract_id"]),
        "contract_fingerprint_sha256": steady_state_contract_fingerprint_sha256(),
    }


def ecology_sampling_plan_fingerprint_sha256(screening_spec: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        _canonical_json_bytes(_canonical_ecology_sampling_plan_payload(screening_spec))
    ).hexdigest()


def repair_sampling_plan_fingerprint_sha256(screening_spec: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        _canonical_json_bytes(_canonical_repair_sampling_plan_payload(screening_spec))
    ).hexdigest()


def _ecology_sampling_ref(screening_spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "replicated_rollout_sampling_ref",
        "sampling_plan_id": "ecology_replicated_rollout_ap_v1",
        "estimate_kind": "replicated_rollout_mean",
        "seed_schedule_kind": "arithmetic_progression",
        "seed_base": _ECOLOGY_SAMPLING_SEED_BASE,
        "seed_stride": _ECOLOGY_SAMPLING_SEED_STRIDE,
        "sampling_plan_fingerprint_sha256": ecology_sampling_plan_fingerprint_sha256(screening_spec),
    }


def _repair_sampling_ref(screening_spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "repair_offer_sampling_ref",
        "sampling_plan_id": "repair_offer_proxy_ap_v1",
        "estimate_kind": "repair_offer_rate",
        "seed_schedule_kind": "arithmetic_progression",
        "seed_base": _REPAIR_SAMPLING_SEED_BASE,
        "seed_stride": _REPAIR_SAMPLING_SEED_STRIDE,
        "sampling_plan_fingerprint_sha256": repair_sampling_plan_fingerprint_sha256(screening_spec),
    }


def _canonical_opening_distribution_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "certify_memory_one_opening_distribution_contract",
        "contract_id": _OPENING_DISTRIBUTION_CONTRACT_ID,
        "state_order": list(_STATE_ORDER),
        "action_model": "independent_bernoulli_opening_actions",
        "strategy_a_probability_source": "strategy_a.p0",
        "strategy_b_probability_source": "strategy_b.p0",
        "distribution_formula": {
            "CC": "p0_a*p0_b",
            "CD": "p0_a*(1-p0_b)",
            "DC": "(1-p0_a)*p0_b",
            "DD": "(1-p0_a)*(1-p0_b)",
        },
    }


def opening_distribution_contract_fingerprint_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_opening_distribution_contract_payload())).hexdigest()


def _opening_distribution_contract_ref() -> dict[str, Any]:
    payload = _canonical_opening_distribution_contract_payload()
    return {
        "schema_version": int(payload["schema_version"]),
        "kind": str(payload["kind"]),
        "contract_id": str(payload["contract_id"]),
        "contract_fingerprint_sha256": opening_distribution_contract_fingerprint_sha256(),
    }


def _canonical_transition_kernel_contract_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "certify_memory_one_transition_kernel_contract",
        "contract_id": _TRANSITION_KERNEL_CONTRACT_ID,
        "state_order": list(_STATE_ORDER),
        "row_semantics": "previous_joint_state_distribution_over_next_joint_state",
        "row_formula": {
            "CC": "[p_cc*q_cc, p_cc*(1-q_cc), (1-p_cc)*q_cc, (1-p_cc)*(1-q_cc)]",
            "CD": "[p_cd*q_cd, p_cd*(1-q_cd), (1-p_cd)*q_cd, (1-p_cd)*(1-q_cd)]",
            "DC": "[p_dc*q_dc, p_dc*(1-q_dc), (1-p_dc)*q_dc, (1-p_dc)*(1-q_dc)]",
            "DD": "[p_dd*q_dd, p_dd*(1-q_dd), (1-p_dd)*q_dd, (1-p_dd)*(1-q_dd)]",
        },
        "matrix_orientation": "row_stochastic",
        "strategy_b_condition_indexing": "mirrored_to_a_view_before_kernel_build",
    }


def transition_kernel_contract_fingerprint_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_transition_kernel_contract_payload())).hexdigest()


def _transition_kernel_contract_ref() -> dict[str, Any]:
    payload = _canonical_transition_kernel_contract_payload()
    return {
        "schema_version": int(payload["schema_version"]),
        "kind": str(payload["kind"]),
        "contract_id": str(payload["contract_id"]),
        "contract_fingerprint_sha256": transition_kernel_contract_fingerprint_sha256(),
    }


def uncertainty_contract_fingerprint_sha256() -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_uncertainty_contract_payload())).hexdigest()


def _uncertainty_contract_ref() -> dict[str, Any]:
    payload = _canonical_uncertainty_contract_payload()
    return {
        "schema_version": int(payload["schema_version"]),
        "kind": str(payload["kind"]),
        "contract_id": str(payload["contract_id"]),
        "contract_fingerprint_sha256": uncertainty_contract_fingerprint_sha256(),
    }


def strategy_fingerprint_sha256(strategy: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(_canonical_memory_one_strategy_payload(strategy))).hexdigest()


def _strategy_ref(strategy: Mapping[str, Any]) -> dict[str, Any]:
    payload = _canonical_memory_one_strategy_payload(strategy)
    return {
        "schema_version": 1,
        "kind": "memory_one_strategy_ref",
        "family": str(payload["family"]),
        "strategy_id": payload["id"],
        "strategy_fingerprint_sha256": hashlib.sha256(_canonical_json_bytes(payload)).hexdigest(),
    }


def pairing_fingerprint_sha256(
    strategy_a: Mapping[str, Any],
    strategy_b: Mapping[str, Any],
    screening_spec: Mapping[str, Any],
) -> str:
    payload = {
        "schema_version": 1,
        "kind": "certify_memory_one_pairing_ref",
        "stage_game_ref": _stage_game_ref(),
        "strategy_a_ref": _strategy_ref(strategy_a),
        "strategy_b_ref": _strategy_ref(strategy_b),
        "screening_spec_ref": _screening_spec_ref(screening_spec),
        "ecology_sampling_ref": _ecology_sampling_ref(screening_spec),
        "repair_sampling_ref": _repair_sampling_ref(screening_spec),
        "uncertainty_contract_ref": _uncertainty_contract_ref(),
        "proxy_measurement_contract_ref": _proxy_measurement_contract_ref(),
        "steady_state_contract_ref": _steady_state_contract_ref(),
        "opening_distribution_contract_ref": _opening_distribution_contract_ref(),
        "transition_kernel_contract_ref": _transition_kernel_contract_ref(),
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _pairing_ref(
    strategy_a: Mapping[str, Any],
    strategy_b: Mapping[str, Any],
    screening_spec: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "certify_memory_one_pairing_ref",
        "pairing_fingerprint_sha256": pairing_fingerprint_sha256(strategy_a, strategy_b, screening_spec),
    }


def _as_prob(name: str, value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise CertifyError(f"{name} must be numeric")
    p = float(value)
    if p < 0.0 or p > 1.0:
        raise CertifyError(f"{name} must be in [0, 1], got {p}")
    return p


def _as_non_negative_float(name: str, value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise CertifyError(f"{name} must be numeric")
    out = float(value)
    if out < 0.0:
        raise CertifyError(f"{name} must be non-negative, got {out}")
    return out


def _as_positive_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise CertifyError(f"{name} must be an integer")
    if value <= 0:
        raise CertifyError(f"{name} must be positive, got {value}")
    return value


def _as_optional_number(name: str, value: Any) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        raise CertifyError(f"{name} must be numeric or null")
    return float(value)


def _extract_memory_one_probabilities(strategy: Mapping[str, Any], label: str) -> list[float]:
    family = strategy.get("family")
    if family != "memory_one":
        raise CertifyError(f"{label} is not memory_one (family={family!r})")
    return [_as_prob(f"{label}.{k}", strategy.get(k)) for k in _MEMORY_ONE_KEYS]


def _extract_memory_one_params(strategy: Mapping[str, Any], label: str) -> tuple[float, float, float, float, float]:
    probs = _extract_memory_one_probabilities(strategy, label)
    p0_raw = strategy.get("p0", strategy.get("p_cc"))
    return (_as_prob(f"{label}.p0", p0_raw), *probs)


def _extract_screening_spec(
    spec: Mapping[str, Any] | None,
    *,
    ecology_noise_override: float | None,
    ecology_rounds_override: int | None,
    ecology_reps_override: int | None,
) -> dict[str, Any]:
    raw = default_screening_spec() if spec is None else copy.deepcopy(dict(spec))
    if int(raw.get("schema_version", 0)) != 1:
        raise CertifyError(f"screening_spec.schema_version must be 1, got {raw.get('schema_version')!r}")
    if raw.get("kind") != "certify_memory_one_screening_spec":
        raise CertifyError(
            "screening_spec.kind must be 'certify_memory_one_screening_spec'"
        )
    spec_id = raw.get("spec_id")
    if not isinstance(spec_id, str) or not spec_id:
        raise CertifyError("screening_spec.spec_id must be a non-empty string")

    steady_state = raw.get("steady_state")
    if not isinstance(steady_state, Mapping):
        raise CertifyError("screening_spec.steady_state must be an object")
    cesaro_steps = _as_positive_int(
        "screening_spec.steady_state.cesaro_fallback_steps",
        steady_state.get("cesaro_fallback_steps"),
    )

    pairwise = raw.get("pairwise_fairness")
    if not isinstance(pairwise, Mapping):
        raise CertifyError("screening_spec.pairwise_fairness must be an object")
    pairwise_threshold = _as_optional_number(
        "screening_spec.pairwise_fairness.threshold_value",
        pairwise.get("threshold_value"),
    )
    if pairwise_threshold is None:
        raise CertifyError("screening_spec.pairwise_fairness.threshold_value must be numeric")

    recovery = raw.get("recovery_proxy")
    if not isinstance(recovery, Mapping):
        raise CertifyError("screening_spec.recovery_proxy must be an object")
    recovery_epsilon = _as_non_negative_float(
        "screening_spec.recovery_proxy.epsilon",
        recovery.get("epsilon"),
    )
    recovery_horizon = _as_positive_int(
        "screening_spec.recovery_proxy.horizon",
        recovery.get("horizon"),
    )
    recovery_cc_mass_min = _as_prob(
        "screening_spec.recovery_proxy.cc_mass_min",
        recovery.get("cc_mass_min"),
    )
    recovery_threshold = _as_optional_number(
        "screening_spec.recovery_proxy.threshold_value",
        recovery.get("threshold_value"),
    )
    if recovery_threshold is None:
        raise CertifyError("screening_spec.recovery_proxy.threshold_value must be numeric")
    shock_protocol = recovery.get("shock_protocol")
    if not isinstance(shock_protocol, str) or not shock_protocol:
        raise CertifyError("screening_spec.recovery_proxy.shock_protocol must be a non-empty string")

    repair = raw.get("repair_proxy")
    if not isinstance(repair, Mapping):
        raise CertifyError("screening_spec.repair_proxy must be an object")
    repair_proxy_k = _as_positive_int("screening_spec.repair_proxy.k", repair.get("k"))
    repair_rounds = _as_positive_int("screening_spec.repair_proxy.rounds", repair.get("rounds"))
    repair_repetitions = _as_positive_int(
        "screening_spec.repair_proxy.repetitions",
        repair.get("repetitions"),
    )
    repair_noise = _as_prob("screening_spec.repair_proxy.noise", repair.get("noise"))
    repair_threshold_status = repair.get("threshold_status")
    if repair_threshold_status not in {"pending", "declared"}:
        raise CertifyError(
            "screening_spec.repair_proxy.threshold_status must be 'pending' or 'declared'"
        )
    repair_threshold = _as_optional_number(
        "screening_spec.repair_proxy.threshold_value",
        repair.get("threshold_value"),
    )

    ecology = raw.get("noisy_ecology")
    if not isinstance(ecology, Mapping):
        raise CertifyError("screening_spec.noisy_ecology must be an object")
    ecology_threshold = _as_optional_number(
        "screening_spec.noisy_ecology.threshold_value",
        ecology.get("threshold_value"),
    )
    if ecology_threshold is None:
        raise CertifyError("screening_spec.noisy_ecology.threshold_value must be numeric")
    ecology_noise = _as_prob("screening_spec.noisy_ecology.noise", ecology.get("noise"))
    ecology_rounds = _as_positive_int("screening_spec.noisy_ecology.rounds", ecology.get("rounds"))
    ecology_reps = _as_positive_int(
        "screening_spec.noisy_ecology.repetitions",
        ecology.get("repetitions"),
    )
    if ecology_noise_override is not None:
        ecology_noise = _as_prob("ecology_noise_override", ecology_noise_override)
    if ecology_rounds_override is not None:
        ecology_rounds = _as_positive_int("ecology_rounds_override", ecology_rounds_override)
    if ecology_reps_override is not None:
        ecology_reps = _as_positive_int("ecology_reps_override", ecology_reps_override)

    pool_raw = ecology.get("pool")
    if not isinstance(pool_raw, list) or not pool_raw:
        raise CertifyError("screening_spec.noisy_ecology.pool must be a non-empty array")
    pool: list[tuple[str, tuple[float, float, float, float, float]]] = []
    for idx, entry in enumerate(pool_raw):
        if not isinstance(entry, Mapping):
            raise CertifyError(f"screening_spec.noisy_ecology.pool[{idx}] must be an object")
        opponent_id = entry.get("id")
        if not isinstance(opponent_id, str) or not opponent_id:
            raise CertifyError(f"screening_spec.noisy_ecology.pool[{idx}].id must be a non-empty string")
        pool.append((opponent_id, _extract_memory_one_params(entry, f"screening_spec.noisy_ecology.pool[{idx}]")))

    return {
        "schema_version": 1,
        "kind": "certify_memory_one_screening_spec",
        "spec_id": spec_id,
        "status": str(raw.get("status", "screening_proxy_contract")),
        "steady_state": {
            "cesaro_fallback_steps": cesaro_steps,
        },
        "pairwise_fairness": {
            "metric": str(pairwise.get("metric", "payoff_gap")),
            "threshold_kind": str(pairwise.get("threshold_kind", "max")),
            "threshold_value": pairwise_threshold,
        },
        "recovery_proxy": {
            "metric": str(recovery.get("metric", "recovery_rounds")),
            "shock_protocol": shock_protocol,
            "epsilon": recovery_epsilon,
            "horizon": recovery_horizon,
            "cc_mass_min": recovery_cc_mass_min,
            "threshold_kind": str(recovery.get("threshold_kind", "max")),
            "threshold_value": recovery_threshold,
        },
        "repair_proxy": {
            "metric": str(repair.get("metric", "repair_abuse_rate")),
            "k": repair_proxy_k,
            "rounds": repair_rounds,
            "repetitions": repair_repetitions,
            "noise": repair_noise,
            "threshold_kind": repair.get("threshold_kind"),
            "threshold_value": repair_threshold,
            "threshold_status": repair_threshold_status,
        },
        "noisy_ecology": {
            "metric": str(ecology.get("metric", "ecology_gap_noisy")),
            "threshold_kind": str(ecology.get("threshold_kind", "max")),
            "threshold_value": ecology_threshold,
            "noise": ecology_noise,
            "rounds": ecology_rounds,
            "repetitions": ecology_reps,
            "pool": pool,
        },
    }


def _screening_spec_ref(screening_spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": int(screening_spec["schema_version"]),
        "kind": str(screening_spec["kind"]),
        "spec_id": str(screening_spec["spec_id"]),
        "spec_fingerprint_sha256": screening_spec_fingerprint_sha256(screening_spec),
    }


def _build_transition_matrix_memory_one(p: list[float], q: list[float]) -> list[list[float]]:
    matrix: list[list[float]] = []
    for i in range(4):
        row = [
            p[i] * q[i],
            p[i] * (1.0 - q[i]),
            (1.0 - p[i]) * q[i],
            (1.0 - p[i]) * (1.0 - q[i]),
        ]
        matrix.append(row)
    return matrix


def _graph_reachability(graph: list[set[int]], start: int) -> set[int]:
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for nxt in graph[node]:
            if nxt in seen:
                continue
            seen.add(nxt)
            stack.append(nxt)
    return seen


def _graph_reachability_from_many(graph: list[set[int]], starts: list[int]) -> set[int]:
    seen: set[int] = set(starts)
    stack = list(starts)
    while stack:
        node = stack.pop()
        for nxt in graph[node]:
            if nxt in seen:
                continue
            seen.add(nxt)
            stack.append(nxt)
    return seen


def _solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(a)
    eps = _STATIONARY_SOLVER_PIVOT_EPSILON
    if n == 0:
        return []
    if any(len(row) != n for row in a) or len(b) != n:
        raise CertifyError("expected a square linear system")

    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < eps:
            raise CertifyError("linear system is singular or ill-conditioned")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]

        pivot_val = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= pivot_val

        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if abs(factor) < eps:
                continue
            for j in range(col, n + 1):
                aug[r][j] -= factor * aug[col][j]

    return [aug[i][n] for i in range(n)]


def _hitting_probability_and_expected_steps_indicator(
    matrix: list[list[float]],
    target_idx: set[int],
    *,
    solve_idx: list[int] | None = None,
) -> tuple[list[float], list[float]]:
    active_idx = [idx for idx in range(4) if idx not in target_idx] if solve_idx is None else list(solve_idx)
    if any(idx in target_idx for idx in active_idx):
        raise CertifyError("solve_idx must exclude target states")
    active_pos = {idx: pos for pos, idx in enumerate(active_idx)}

    h = [1.0 if idx in target_idx else 0.0 for idx in range(4)]
    if active_idx:
        a: list[list[float]] = []
        rhs: list[float] = []
        for src in active_idx:
            row = [0.0] * len(active_idx)
            row[active_pos[src]] = 1.0
            for dst in active_idx:
                row[active_pos[dst]] -= float(matrix[src][dst])
            a.append(row)
            rhs.append(sum(float(matrix[src][dst]) for dst in target_idx))
        solved_h = _solve_linear_system(a, rhs)
        for idx, value in zip(active_idx, solved_h):
            h[idx] = max(0.0, min(1.0, float(value)))

    g = [0.0] * 4
    if active_idx:
        a = []
        rhs = []
        for src in active_idx:
            row = [0.0] * len(active_idx)
            row[active_pos[src]] = 1.0
            for dst in active_idx:
                row[active_pos[dst]] -= float(matrix[src][dst])
            a.append(row)
            rhs.append(float(h[src]))
        solved_g = _solve_linear_system(a, rhs)
        for idx, value in zip(active_idx, solved_g):
            g[idx] = max(0.0, float(value))

    return (h, g)


def _expected_cumulative_reward_before_closed_class_entry(
    matrix: list[list[float]],
    recurrent_idx: set[int],
    rewards: list[float],
) -> list[float]:
    values = [0.0] * 4
    transient_idx = [idx for idx in range(4) if idx not in recurrent_idx]
    if transient_idx:
        transient_pos = {idx: pos for pos, idx in enumerate(transient_idx)}
        a: list[list[float]] = []
        rhs: list[float] = []
        for src in transient_idx:
            row = [0.0] * len(transient_idx)
            row[transient_pos[src]] = 1.0
            for dst in transient_idx:
                row[transient_pos[dst]] -= float(matrix[src][dst])
            a.append(row)
            rhs.append(float(rewards[src]))
        solved = _solve_linear_system(a, rhs)
        for idx, value in zip(transient_idx, solved):
            values[idx] = float(value)
    return values


def _conditional_expected_cumulative_reward_before_target_entry(
    matrix: list[list[float]],
    rewards: list[float],
    initial_dist: list[float],
    target_idx: set[int],
    recurrent_idx: set[int],
) -> tuple[float, float | None]:
    transient_idx = [idx for idx in range(4) if idx not in recurrent_idx]
    h, _ = _hitting_probability_and_expected_steps_indicator(
        matrix,
        target_idx,
        solve_idx=transient_idx,
    )
    entry_probability = sum(float(initial_dist[idx]) * h[idx] for idx in range(4))
    reward_indicator = [float(rewards[idx]) * float(h[idx]) for idx in range(4)]
    reward_times_indicator = _expected_cumulative_reward_before_closed_class_entry(
        matrix,
        recurrent_idx,
        reward_indicator,
    )
    expected_reward_times_indicator = sum(
        float(initial_dist[idx]) * float(reward_times_indicator[idx]) for idx in range(4)
    )
    conditional_expected_reward: float | None
    if entry_probability > _GRAPH_EDGE_EPSILON:
        conditional_expected_reward = float(expected_reward_times_indicator / entry_probability)
    else:
        conditional_expected_reward = None
    return (float(entry_probability), conditional_expected_reward)


def _expected_visit_counts_before_closed_class_entry(
    matrix: list[list[float]],
    recurrent_idx: set[int],
) -> dict[str, list[float]]:
    visit_counts_by_state: dict[str, list[float]] = {}
    for state_idx, state_label in enumerate(_STATE_ORDER):
        rewards = [1.0 if idx == state_idx else 0.0 for idx in range(4)]
        visit_counts_by_state[str(state_label)] = _expected_cumulative_reward_before_closed_class_entry(
            matrix,
            recurrent_idx,
            rewards,
        )
    return visit_counts_by_state


def _expected_transition_counts_from_expected_visit_counts(
    matrix: list[list[float]],
    expected_visit_counts_by_state: dict[str, float],
    recurrent_idx: set[int],
) -> dict[str, dict[str, float]]:
    transition_counts: dict[str, dict[str, float]] = {}
    for src_idx, src_label in enumerate(_STATE_ORDER):
        visits = 0.0 if src_idx in recurrent_idx else float(expected_visit_counts_by_state[str(src_label)])
        transition_counts[str(src_label)] = {
            str(dst_label): float(visits * float(matrix[src_idx][dst_idx]))
            for dst_idx, dst_label in enumerate(_STATE_ORDER)
        }
    return transition_counts


def _conditional_expected_transition_counts_before_target_entry(
    matrix: list[list[float]],
    initial_dist: list[float],
    target_idx: set[int],
    recurrent_idx: set[int],
    conditional_expected_visit_counts: dict[str, float | None],
) -> tuple[float, dict[str, dict[str, float | None]]]:
    transient_idx = [idx for idx in range(4) if idx not in recurrent_idx]
    h, _ = _hitting_probability_and_expected_steps_indicator(
        matrix,
        target_idx,
        solve_idx=transient_idx,
    )
    entry_probability = sum(float(initial_dist[idx]) * h[idx] for idx in range(4))
    if entry_probability <= _GRAPH_EDGE_EPSILON:
        return (
            float(entry_probability),
            {
                str(src_label): {str(dst_label): None for dst_label in _STATE_ORDER}
                for src_label in _STATE_ORDER
            },
        )

    transition_counts: dict[str, dict[str, float | None]] = {}
    for src_idx, src_label in enumerate(_STATE_ORDER):
        src_key = str(src_label)
        row: dict[str, float | None] = {}
        if src_idx in recurrent_idx:
            row = {str(dst_label): 0.0 for dst_label in _STATE_ORDER}
        else:
            visits = conditional_expected_visit_counts[src_key]
            visits_value = 0.0 if visits is None else float(visits)
            if h[src_idx] <= _GRAPH_EDGE_EPSILON or visits_value <= _GRAPH_EDGE_EPSILON:
                row = {str(dst_label): 0.0 for dst_label in _STATE_ORDER}
            else:
                for dst_idx, dst_label in enumerate(_STATE_ORDER):
                    transformed_prob = float(matrix[src_idx][dst_idx]) * float(h[dst_idx]) / float(h[src_idx])
                    row[str(dst_label)] = float(visits_value * transformed_prob)
        transition_counts[src_key] = row
    return (float(entry_probability), transition_counts)


def _closed_class_entry_probabilities_from_initial_distribution(
    matrix: list[list[float]],
    initial_dist: list[float],
    closed_classes_idx: list[list[int]],
) -> list[dict[str, Any]]:
    recurrent_idx = {idx for component in closed_classes_idx for idx in component}
    transient_idx = [idx for idx in range(4) if idx not in recurrent_idx]
    visit_counts_before_closed_class_entry = _expected_visit_counts_before_closed_class_entry(
        matrix,
        recurrent_idx,
    )
    results: list[dict[str, Any]] = []
    for component in closed_classes_idx:
        h, g = _hitting_probability_and_expected_steps_indicator(
            matrix,
            set(component),
            solve_idx=transient_idx,
        )
        entry_probability = sum(float(initial_dist[idx]) * h[idx] for idx in range(4))
        expected_steps_weighted = sum(float(initial_dist[idx]) * g[idx] for idx in range(4))
        _, conditional_expected_payoff_a = _conditional_expected_cumulative_reward_before_target_entry(
            matrix,
            _PAYOFFS_A,
            initial_dist,
            set(component),
            recurrent_idx,
        )
        _, conditional_expected_payoff_b = _conditional_expected_cumulative_reward_before_target_entry(
            matrix,
            _PAYOFFS_B,
            initial_dist,
            set(component),
            recurrent_idx,
        )
        conditional_expected_visit_counts = {}
        for state_label in _STATE_ORDER:
            _, conditional_expected_visits = _conditional_expected_cumulative_reward_before_target_entry(
                matrix,
                [1.0 if label == state_label else 0.0 for label in _STATE_ORDER],
                initial_dist,
                set(component),
                recurrent_idx,
            )
            conditional_expected_visit_counts[str(state_label)] = conditional_expected_visits
        _, conditional_expected_transition_counts = _conditional_expected_transition_counts_before_target_entry(
            matrix,
            initial_dist,
            set(component),
            recurrent_idx,
            conditional_expected_visit_counts,
        )
        conditional_expected_steps: float | None
        if entry_probability > _GRAPH_EDGE_EPSILON:
            conditional_expected_steps = float(expected_steps_weighted / entry_probability)
        else:
            conditional_expected_steps = None
        results.append(
            {
                "closed_class": [str(_STATE_ORDER[idx]) for idx in component],
                "entry_probability": float(max(0.0, min(1.0, entry_probability))),
                "conditional_expected_entry_steps_from_initial_distribution": conditional_expected_steps,
                "conditional_expected_cumulative_payoff_a_before_entry_from_initial_distribution": conditional_expected_payoff_a,
                "conditional_expected_cumulative_payoff_b_before_entry_from_initial_distribution": conditional_expected_payoff_b,
                "conditional_expected_visit_counts_before_entry_from_initial_distribution": conditional_expected_visit_counts,
                "conditional_expected_transition_counts_before_entry_from_initial_distribution": conditional_expected_transition_counts,
            }
        )
    return results


def _stationary_distribution_on_closed_class(
    matrix: list[list[float]],
    component: list[int],
) -> list[float]:
    n = len(component)
    if n == 0:
        raise CertifyError("closed class must be non-empty")
    if n == 1:
        return [1.0]

    sub = [[float(matrix[src][dst]) for dst in component] for src in component]
    a = [[sub[i][j] - (1.0 if i == j else 0.0) for i in range(n)] for j in range(n)]
    b = [0.0] * n
    a[n - 1] = [1.0] * n
    b[n - 1] = 1.0

    v = _solve_linear_system(a, b)
    cleaned = [0.0 if abs(x) < _STATIONARY_ZERO_CLEANUP_ABS_TOL else float(x) for x in v]
    if any(x < -_STATIONARY_NEGATIVE_MASS_ABS_TOL for x in cleaned):
        raise CertifyError(f"computed invalid closed-class stationary distribution: {cleaned}")

    non_negative = [max(0.0, x) for x in cleaned]
    total = sum(non_negative)
    if total <= 0.0:
        raise CertifyError("computed zero-mass closed-class stationary distribution")
    return [x / total for x in non_negative]


def _closed_class_asymptotic_decomposition_from_initial_distribution(
    matrix: list[list[float]],
    closed_class_entry_probs: list[dict[str, Any]],
    closed_classes_idx: list[list[int]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for component, entry_item in zip(closed_classes_idx, closed_class_entry_probs):
        local_stationary = _stationary_distribution_on_closed_class(matrix, component)
        embedded_stationary = [0.0] * 4
        for local_idx, state_idx in enumerate(component):
            embedded_stationary[state_idx] = float(local_stationary[local_idx])
        entry_probability = float(entry_item["entry_probability"])
        weighted_contribution = [float(entry_probability * mass) for mass in embedded_stationary]
        avg_payoff_a = sum(embedded_stationary[i] * _PAYOFFS_A[i] for i in range(4))
        avg_payoff_b = sum(embedded_stationary[i] * _PAYOFFS_B[i] for i in range(4))
        results.append(
            {
                "closed_class": [str(_STATE_ORDER[idx]) for idx in component],
                "entry_probability": entry_probability,
                "class_stationary_distribution": embedded_stationary,
                "weighted_steady_state_contribution": weighted_contribution,
                "class_avg_payoff_a": float(avg_payoff_a),
                "class_avg_payoff_b": float(avg_payoff_b),
            }
        )
    return results


def _asymptotic_distribution_from_closed_class_decomposition(
    closed_class_decomposition: list[dict[str, Any]],
) -> list[float]:
    return [
        sum(float(item["weighted_steady_state_contribution"][i]) for item in closed_class_decomposition)
        for i in range(4)
    ]


def _payoffs_from_distribution(distribution: list[float]) -> tuple[float, float]:
    avg_payoff_a = sum(float(distribution[i]) * _PAYOFFS_A[i] for i in range(4))
    avg_payoff_b = sum(float(distribution[i]) * _PAYOFFS_B[i] for i in range(4))
    return (float(avg_payoff_a), float(avg_payoff_b))


def _transition_graph_diagnostics(
    matrix: list[list[float]],
    initial_dist: list[float],
) -> dict[str, Any]:
    graph = [
        {dst for dst, prob in enumerate(row) if float(prob) > _GRAPH_EDGE_EPSILON}
        for row in matrix
    ]
    reverse_graph = [set() for _ in range(4)]
    for src, nbrs in enumerate(graph):
        for dst in nbrs:
            reverse_graph[dst].add(src)

    classes_idx: list[list[int]] = []
    assigned: set[int] = set()
    for idx in range(4):
        if idx in assigned:
            continue
        forward = _graph_reachability(graph, idx)
        backward = _graph_reachability(reverse_graph, idx)
        component = sorted(forward & backward)
        classes_idx.append(component)
        assigned.update(component)
    classes_idx.sort(key=lambda nodes: min(nodes))

    closed_classes_idx: list[list[int]] = []
    for component in classes_idx:
        component_set = set(component)
        if all(dst in component_set for src in component for dst in graph[src]):
            closed_classes_idx.append(component)

    initial_support_idx = sorted(idx for idx, mass in enumerate(initial_dist) if float(mass) > _GRAPH_EDGE_EPSILON)
    reachable_idx = sorted(_graph_reachability_from_many(graph, initial_support_idx)) if initial_support_idx else []
    reachable_closed_classes_idx = [
        component for component in closed_classes_idx if any(idx in reachable_idx for idx in component)
    ]

    absorbing_idx = [
        idx
        for idx, row in enumerate(matrix)
        if row[idx] >= 1.0 - _GRAPH_EDGE_EPSILON
        and all(j == idx or value <= _GRAPH_EDGE_EPSILON for j, value in enumerate(row))
    ]

    recurrent_idx = {idx for component in closed_classes_idx for idx in component}
    transient_idx = [idx for idx in range(4) if idx not in recurrent_idx]
    closed_class_entry_probs = _closed_class_entry_probabilities_from_initial_distribution(
        matrix,
        initial_dist,
        closed_classes_idx,
    )
    _, closed_union_steps_indicator = _hitting_probability_and_expected_steps_indicator(
        matrix,
        recurrent_idx,
        solve_idx=transient_idx,
    )
    expected_steps_to_any_closed_class_from_initial_distribution = sum(
        float(initial_dist[idx]) * float(closed_union_steps_indicator[idx]) for idx in range(4)
    )
    cumulative_payoff_a_before_closed_class_entry = _expected_cumulative_reward_before_closed_class_entry(
        matrix,
        recurrent_idx,
        _PAYOFFS_A,
    )
    cumulative_payoff_b_before_closed_class_entry = _expected_cumulative_reward_before_closed_class_entry(
        matrix,
        recurrent_idx,
        _PAYOFFS_B,
    )
    visit_counts_before_closed_class_entry = _expected_visit_counts_before_closed_class_entry(
        matrix,
        recurrent_idx,
    )
    expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution = sum(
        float(initial_dist[idx]) * float(cumulative_payoff_a_before_closed_class_entry[idx]) for idx in range(4)
    )
    expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution = sum(
        float(initial_dist[idx]) * float(cumulative_payoff_b_before_closed_class_entry[idx]) for idx in range(4)
    )
    expected_visit_counts_before_any_closed_class_entry_from_initial_distribution = {
        state_label: float(
            sum(float(initial_dist[idx]) * float(values[idx]) for idx in range(4))
        )
        for state_label, values in visit_counts_before_closed_class_entry.items()
    }
    expected_transition_counts_before_any_closed_class_entry_from_initial_distribution = (
        _expected_transition_counts_from_expected_visit_counts(
            matrix,
            expected_visit_counts_before_any_closed_class_entry_from_initial_distribution,
            recurrent_idx,
        )
    )
    positive_entry_components = [
        item for item in closed_class_entry_probs if float(item["entry_probability"]) > _GRAPH_EDGE_EPSILON
    ]
    closed_class_asymptotic_decomposition = _closed_class_asymptotic_decomposition_from_initial_distribution(
        matrix,
        closed_class_entry_probs,
        closed_classes_idx,
    )

    def labels(indices: list[int]) -> list[str]:
        return [str(_STATE_ORDER[idx]) for idx in indices]

    return {
        "state_order": list(_STATE_ORDER),
        "graph_edge_epsilon": float(_GRAPH_EDGE_EPSILON),
        "reducible": len(classes_idx) > 1,
        "communicating_class_count": len(classes_idx),
        "closed_class_count": len(closed_classes_idx),
        "multiple_recurrent_classes": len(closed_classes_idx) > 1,
        "absorbing_states": labels(absorbing_idx),
        "communicating_classes": [labels(component) for component in classes_idx],
        "closed_classes": [labels(component) for component in closed_classes_idx],
        "transient_states": labels(transient_idx),
        "initial_support_states": labels(initial_support_idx),
        "reachable_states_from_initial_support": labels(reachable_idx),
        "reachable_closed_classes_from_initial_support": [
            labels(component) for component in reachable_closed_classes_idx
        ],
        "expected_steps_to_any_closed_class_from_initial_distribution": float(
            expected_steps_to_any_closed_class_from_initial_distribution
        ),
        "expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution": float(
            expected_cumulative_payoff_a_before_any_closed_class_entry_from_initial_distribution
        ),
        "expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution": float(
            expected_cumulative_payoff_b_before_any_closed_class_entry_from_initial_distribution
        ),
        "expected_visit_counts_before_any_closed_class_entry_from_initial_distribution": expected_visit_counts_before_any_closed_class_entry_from_initial_distribution,
        "expected_transition_counts_before_any_closed_class_entry_from_initial_distribution": expected_transition_counts_before_any_closed_class_entry_from_initial_distribution,
        "closed_class_entry_probabilities_from_initial_distribution": closed_class_entry_probs,
        "closed_class_asymptotic_decomposition_from_initial_distribution": closed_class_asymptotic_decomposition,
        "multiple_closed_classes_with_positive_entry_probability_from_initial_distribution": (
            len(positive_entry_components) > 1
        ),
    }


def _solve_linear_4x4(a: list[list[float]], b: list[float]) -> list[float]:
    if len(a) != 4 or any(len(row) != 4 for row in a) or len(b) != 4:
        raise CertifyError("expected a 4x4 linear system")
    return _solve_linear_system(a, b)


def _stationary_distribution(matrix: list[list[float]]) -> list[float]:
    # Solve (P^T - I)v = 0 with sum(v) = 1.
    a = [[matrix[i][j] - (1.0 if i == j else 0.0) for i in range(4)] for j in range(4)]
    b = [0.0, 0.0, 0.0, 0.0]

    # Replace one equation with normalization to get a full-rank system.
    a[3] = [1.0, 1.0, 1.0, 1.0]
    b[3] = 1.0

    v = _solve_linear_4x4(a, b)

    cleaned = [0.0 if abs(x) < _STATIONARY_ZERO_CLEANUP_ABS_TOL else float(x) for x in v]
    if any(x < -_STATIONARY_NEGATIVE_MASS_ABS_TOL for x in cleaned):
        raise CertifyError(f"computed invalid stationary distribution: {cleaned}")

    non_negative = [max(0.0, x) for x in cleaned]
    total = sum(non_negative)
    if total <= 0.0:
        raise CertifyError("computed zero-mass stationary distribution")
    return [x / total for x in non_negative]


def _mem1_action(
    params: tuple[float, float, float, float, float],
    last_self: str | None,
    last_opp: str | None,
    rng: random.Random,
) -> str:
    p0, p_cc, p_cd, p_dc, p_dd = params
    if last_self is None:
        p = p0
    elif last_self == "C" and last_opp == "C":
        p = p_cc
    elif last_self == "C" and last_opp == "D":
        p = p_cd
    elif last_self == "D" and last_opp == "C":
        p = p_dc
    else:
        p = p_dd
    return "C" if rng.random() < p else "D"


def _run_match(
    strat_a: tuple[float, float, float, float, float],
    strat_b: tuple[float, float, float, float, float],
    *,
    rounds: int,
    seed: int,
    noise: float,
) -> tuple[float, float]:
    rng = random.Random(seed)
    last_a: str | None = None
    last_b: str | None = None
    total_a = 0.0
    total_b = 0.0
    for _ in range(rounds):
        action_a = _mem1_action(strat_a, last_a, last_b, rng)
        action_b = _mem1_action(strat_b, last_b, last_a, rng)
        if noise > 0.0:
            if rng.random() < noise:
                action_a = "D" if action_a == "C" else "C"
            if rng.random() < noise:
                action_b = "D" if action_b == "C" else "C"
        payoff_a, payoff_b = _PAYOFFS[(action_a, action_b)]
        total_a += payoff_a
        total_b += payoff_b
        last_a = action_a
        last_b = action_b
    return (total_a / rounds, total_b / rounds)


def _mean_stderr(values: list[float]) -> tuple[float, float]:
    if not values:
        raise CertifyError("expected at least one value")
    mean = sum(values) / len(values)
    if len(values) == 1:
        return (float(mean), 0.0)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return (float(mean), math.sqrt(variance / len(values)))


def _wilson_interval(successes: int, trials: int, *, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        return (0.0, 0.0)
    p = successes / trials
    z2 = z * z
    denom = 1.0 + (z2 / trials)
    center = (p + (z2 / (2.0 * trials))) / denom
    radius = (z / denom) * math.sqrt((p * (1.0 - p) / trials) + (z2 / (4.0 * trials * trials)))
    return (max(0.0, center - radius), min(1.0, center + radius))


def _ci95_interval(center: float, half_width: float) -> tuple[float, float]:
    return (center - half_width, center + half_width)


def _max_threshold_decision_state(
    *,
    observed_value: float | int,
    threshold_value: float | int,
    interval_low: float | None = None,
    interval_high: float | None = None,
) -> str:
    if interval_low is None or interval_high is None:
        return "exact_pass" if observed_value <= threshold_value else "exact_fail"
    if interval_high <= threshold_value:
        return "clear_pass"
    if interval_low > threshold_value:
        return "clear_fail"
    return "borderline_ci95_crosses_threshold"


def _run_match_replicated_stats(
    strat_a: tuple[float, float, float, float, float],
    strat_b: tuple[float, float, float, float, float],
    *,
    rounds: int,
    reps: int,
    noise: float,
) -> dict[str, float | int | list[tuple[float, float]]]:
    results = [
        _run_match(strat_a, strat_b, rounds=rounds, seed=(rep * _ECOLOGY_SAMPLING_SEED_STRIDE) + _ECOLOGY_SAMPLING_SEED_BASE, noise=noise)
        for rep in range(reps)
    ]
    payoffs_a = [pair[0] for pair in results]
    payoffs_b = [pair[1] for pair in results]
    gaps = [a - b for a, b in results]
    avg_a, stderr_a = _mean_stderr(payoffs_a)
    avg_b, stderr_b = _mean_stderr(payoffs_b)
    gap_mean, gap_stderr = _mean_stderr(gaps)
    return {
        "avg_a": avg_a,
        "avg_b": avg_b,
        "stderr_a": stderr_a,
        "stderr_b": stderr_b,
        "gap_mean": gap_mean,
        "gap_stderr": gap_stderr,
        "reps": reps,
    }


def _run_match_replicated(
    strat_a: tuple[float, float, float, float, float],
    strat_b: tuple[float, float, float, float, float],
    *,
    rounds: int,
    reps: int,
    noise: float,
) -> tuple[float, float]:
    stats = _run_match_replicated_stats(strat_a, strat_b, rounds=rounds, reps=reps, noise=noise)
    return (float(stats["avg_a"]), float(stats["avg_b"]))


def _advance_distribution(dist: list[float], matrix: list[list[float]]) -> list[float]:
    out = [0.0, 0.0, 0.0, 0.0]
    for src in range(4):
        for dst in range(4):
            out[dst] += dist[src] * matrix[src][dst]
    return out


def _initial_distribution(
    params_a: tuple[float, float, float, float, float],
    params_b: tuple[float, float, float, float, float],
) -> list[float]:
    p0_a = params_a[0]
    p0_b = params_b[0]
    return [
        p0_a * p0_b,
        p0_a * (1.0 - p0_b),
        (1.0 - p0_a) * p0_b,
        (1.0 - p0_a) * (1.0 - p0_b),
    ]


def _cesaro_average_distribution(
    matrix: list[list[float]],
    initial_dist: list[float],
    *,
    steps: int,
) -> list[float]:
    if steps <= 0:
        raise CertifyError(f"steps must be positive, got {steps}")
    dist = [float(x) for x in initial_dist]
    avg = [0.0, 0.0, 0.0, 0.0]
    for _ in range(steps):
        for idx, value in enumerate(dist):
            avg[idx] += value
        dist = _advance_distribution(dist, matrix)
    total = float(steps)
    return [value / total for value in avg]


def _steady_state_distribution(
    matrix: list[list[float]],
    *,
    initial_dist: list[float],
    cesaro_steps: int,
) -> tuple[list[float], str]:
    try:
        return (_stationary_distribution(matrix), "exact_stationary")
    except CertifyError as err:
        if "singular or ill-conditioned" not in str(err):
            raise
        return (
            _cesaro_average_distribution(matrix, initial_dist, steps=cesaro_steps),
            "cesaro_from_initial_distribution",
        )


def _estimate_recovery_rounds(
    matrix: list[list[float]],
    *,
    recovery_epsilon: float,
    recovery_horizon: int,
    recovery_cc_mass_min: float,
) -> int:
    # Canonical shock: start at mutual cooperation, then the opponent defects once while the focal cooperates.
    dist = [0.0, 1.0, 0.0, 0.0]
    target_payoff = 3.0 - recovery_epsilon
    for rounds_after_shock in range(1, recovery_horizon + 1):
        dist = _advance_distribution(dist, matrix)
        expected_payoff = sum(dist[i] * _PAYOFFS_A[i] for i in range(4))
        if expected_payoff >= target_payoff and dist[0] >= recovery_cc_mass_min:
            return rounds_after_shock
    return recovery_horizon + 1


def _simulate_action_history(
    strat_a: tuple[float, float, float, float, float],
    strat_b: tuple[float, float, float, float, float],
    *,
    rounds: int,
    seed: int,
    noise: float,
) -> list[tuple[str, str, float, float]]:
    rng = random.Random(seed)
    last_a: str | None = None
    last_b: str | None = None
    history: list[tuple[str, str, float, float]] = []
    for _ in range(rounds):
        action_a = _mem1_action(strat_a, last_a, last_b, rng)
        action_b = _mem1_action(strat_b, last_b, last_a, rng)
        if noise > 0.0:
            if rng.random() < noise:
                action_a = "D" if action_a == "C" else "C"
            if rng.random() < noise:
                action_b = "D" if action_b == "C" else "C"
        payoff_a, payoff_b = _PAYOFFS[(action_a, action_b)]
        history.append((action_a, action_b, payoff_a, payoff_b))
        last_a = action_a
        last_b = action_b
    return history


def _estimate_repair_abuse_rate(
    strat_a: tuple[float, float, float, float, float],
    strat_b: tuple[float, float, float, float, float],
    *,
    rounds: int,
    reps: int,
    noise: float,
    repair_proxy_k: int,
) -> dict[str, float | int]:
    repair_offer_count = 0
    repair_abuse_count = 0
    for rep in range(reps):
        history = _simulate_action_history(
            strat_a,
            strat_b,
            rounds=rounds,
            seed=(rep * _REPAIR_SAMPLING_SEED_STRIDE) + _REPAIR_SAMPLING_SEED_BASE,
            noise=noise,
        )
        for idx in range(1, len(history)):
            prev_b = history[idx - 1][1]
            curr_b = history[idx][1]
            if prev_b != "D" or curr_b != "C":
                continue
            repair_offer_count += 1
            future_window = history[idx : min(len(history), idx + repair_proxy_k)]
            fresh_defection = any(row[1] == "D" for row in history[idx + 1 : min(len(history), idx + 1 + repair_proxy_k)])
            payoff_gap = sum(row[3] - row[2] for row in future_window)
            if fresh_defection and payoff_gap > 0.0:
                repair_abuse_count += 1

    if repair_offer_count == 0:
        return {
            "repair_abuse_rate": 0.0,
            "repair_offer_count": 0,
            "repair_abuse_count": 0,
            "repair_abuse_rate_ci95_low": 0.0,
            "repair_abuse_rate_ci95_high": 0.0,
        }
    ci95_low, ci95_high = _wilson_interval(repair_abuse_count, repair_offer_count)
    return {
        "repair_abuse_rate": repair_abuse_count / repair_offer_count,
        "repair_offer_count": repair_offer_count,
        "repair_abuse_count": repair_abuse_count,
        "repair_abuse_rate_ci95_low": ci95_low,
        "repair_abuse_rate_ci95_high": ci95_high,
    }


def _build_screening_contract(
    *,
    payoff_gap: float,
    ecology_gap_noisy: float,
    ecology_gap_noisy_ci95_half_width: float,
    recovery_rounds: int,
    repair_abuse_rate: float,
    repair_abuse_rate_ci95_low: float,
    repair_abuse_rate_ci95_high: float,
    screening_spec: Mapping[str, Any],
) -> dict[str, Any]:
    pairwise_threshold = float(screening_spec["pairwise_fairness"]["threshold_value"])
    ecology_threshold = float(screening_spec["noisy_ecology"]["threshold_value"])
    recovery_threshold = float(screening_spec["recovery_proxy"]["threshold_value"])
    repair_threshold_kind = screening_spec["repair_proxy"]["threshold_kind"]
    repair_threshold_value = screening_spec["repair_proxy"]["threshold_value"]

    pairwise_fairness_pass = bool(payoff_gap <= pairwise_threshold)
    noisy_ecology_pass = bool(ecology_gap_noisy <= ecology_threshold)
    recovery_proxy_pass = bool(recovery_rounds <= recovery_threshold)

    ecology_ci95_low, ecology_ci95_high = _ci95_interval(ecology_gap_noisy, ecology_gap_noisy_ci95_half_width)
    pairwise_decision_state = _max_threshold_decision_state(
        observed_value=payoff_gap,
        threshold_value=pairwise_threshold,
    )
    ecology_decision_state = _max_threshold_decision_state(
        observed_value=ecology_gap_noisy,
        threshold_value=ecology_threshold,
        interval_low=ecology_ci95_low,
        interval_high=ecology_ci95_high,
    )
    recovery_decision_state = _max_threshold_decision_state(
        observed_value=recovery_rounds,
        threshold_value=recovery_threshold,
    )

    checks = {
        "pairwise_fairness": {
            "binding": True,
            "metric": str(screening_spec["pairwise_fairness"]["metric"]),
            "threshold_kind": str(screening_spec["pairwise_fairness"]["threshold_kind"]),
            "threshold_value": pairwise_threshold,
            "observed_value": float(payoff_gap),
            "passed": pairwise_fairness_pass,
            "reason_code": "pairwise_fairness_pass" if pairwise_fairness_pass else "pairwise_fairness_gap_positive",
            "estimate_kind": "exact",
            "uncertainty_interval_kind": None,
            "uncertainty_low": None,
            "uncertainty_high": None,
            "threshold_decision_state": pairwise_decision_state,
        },
        "noisy_ecology": {
            "binding": True,
            "metric": str(screening_spec["noisy_ecology"]["metric"]),
            "threshold_kind": str(screening_spec["noisy_ecology"]["threshold_kind"]),
            "threshold_value": ecology_threshold,
            "observed_value": float(ecology_gap_noisy),
            "passed": noisy_ecology_pass,
            "reason_code": "noisy_ecology_pass" if noisy_ecology_pass else "noisy_ecology_extraction_positive",
            "estimate_kind": "replicated_rollout_mean",
            "uncertainty_interval_kind": "two_sided_ci95",
            "uncertainty_low": float(ecology_ci95_low),
            "uncertainty_high": float(ecology_ci95_high),
            "threshold_decision_state": ecology_decision_state,
        },
        "recovery_proxy": {
            "binding": False,
            "metric": str(screening_spec["recovery_proxy"]["metric"]),
            "threshold_kind": str(screening_spec["recovery_proxy"]["threshold_kind"]),
            "threshold_value": recovery_threshold,
            "observed_value": int(recovery_rounds),
            "passed": recovery_proxy_pass,
            "reason_code": "recovery_proxy_within_horizon" if recovery_proxy_pass else "recovery_proxy_exceeds_horizon",
            "estimate_kind": "exact_proxy",
            "uncertainty_interval_kind": None,
            "uncertainty_low": None,
            "uncertainty_high": None,
            "threshold_decision_state": recovery_decision_state,
            "notes": [
                "proxy_only_threshold",
                "world_contract_pending",
            ],
        },
        "repair_proxy": {
            "binding": False,
            "metric": str(screening_spec["repair_proxy"]["metric"]),
            "threshold_kind": repair_threshold_kind,
            "threshold_value": repair_threshold_value,
            "observed_value": float(repair_abuse_rate),
            "passed": None,
            "reason_code": "repair_proxy_threshold_pending",
            "estimate_kind": "repair_offer_rate",
            "uncertainty_interval_kind": "wilson_ci95",
            "uncertainty_low": float(repair_abuse_rate_ci95_low),
            "uncertainty_high": float(repair_abuse_rate_ci95_high),
            "threshold_decision_state": "threshold_pending",
            "notes": [
                "repair_threshold_not_declared",
                "repair_channel_semantics_not_world_declared",
            ],
        },
    }

    failure_reasons: list[str] = []
    advisory_reasons: list[str] = []
    for key in ("pairwise_fairness", "noisy_ecology"):
        if not bool(checks[key]["passed"]):
            failure_reasons.append(str(checks[key]["reason_code"]))
    if not bool(checks["recovery_proxy"]["passed"]):
        advisory_reasons.append(str(checks["recovery_proxy"]["reason_code"]))
    advisory_reasons.append(str(checks["repair_proxy"]["reason_code"]))

    if pairwise_decision_state == "exact_fail" or ecology_decision_state == "clear_fail":
        binding_gate_status = "fail"
        gate_stability = "stable"
    elif pairwise_decision_state == "exact_pass" and ecology_decision_state == "clear_pass":
        binding_gate_status = "pass"
        gate_stability = "stable"
    else:
        binding_gate_status = "borderline"
        gate_stability = "borderline_sampling_uncertainty"

    return {
        "contract_version": 2,
        "status": "screening_proxy_contract",
        "gate_kind": "pairwise_fairness_and_noisy_ecology_with_proxy_advisories",
        "binding_checks": ["pairwise_fairness", "noisy_ecology"],
        "advisory_checks": ["recovery_proxy", "repair_proxy"],
        "checks": checks,
        "gate_pass": bool(pairwise_fairness_pass and noisy_ecology_pass),
        "binding_gate_status": binding_gate_status,
        "gate_stability": gate_stability,
        "failure_reasons": failure_reasons,
        "advisory_reasons": advisory_reasons,
        "full_certification_ready": False,
        "full_certification_blockers": [
            "recovery_threshold_still_proxy_only",
            "repair_abuse_threshold_still_proxy_only",
            "repair_channel_semantics_not_world_declared",
        ],
    }



def _build_anti_vampire_scorecard(
    strategy: Mapping[str, Any],
    strategy_b: Mapping[str, Any],
    own_payoff: float,
    payoff_gap: float,
    *,
    matrix: list[list[float]],
    screening_spec: Mapping[str, Any],
) -> dict[str, Any]:
    strat_params = _extract_memory_one_params(strategy, "strategy_a")
    opp_params = _extract_memory_one_params(strategy_b, "strategy_b")
    ecology_gap_by_opponent: dict[str, float] = {}
    ecology_own_by_opponent: dict[str, float] = {}
    ecology_gap_stderr_by_opponent: dict[str, float] = {}
    ecology_own_payoff_stderr_by_opponent: dict[str, float] = {}
    ecology_gaps: list[float] = []
    ecology_owns: list[float] = []
    ecology_gap_var_terms: list[float] = []
    ecology_own_var_terms: list[float] = []
    ecology_settings = screening_spec["noisy_ecology"]
    for opponent_id, opponent_params in ecology_settings["pool"]:
        stats = _run_match_replicated_stats(
            strat_params,
            opponent_params,
            rounds=int(ecology_settings["rounds"]),
            reps=int(ecology_settings["repetitions"]),
            noise=float(ecology_settings["noise"]),
        )
        gap = float(stats["gap_mean"])
        avg_a = float(stats["avg_a"])
        gap_stderr = float(stats["gap_stderr"])
        own_stderr = float(stats["stderr_a"])
        ecology_gap_by_opponent[opponent_id] = gap
        ecology_own_by_opponent[opponent_id] = avg_a
        ecology_gap_stderr_by_opponent[opponent_id] = gap_stderr
        ecology_own_payoff_stderr_by_opponent[opponent_id] = own_stderr
        ecology_gaps.append(gap)
        ecology_owns.append(avg_a)
        ecology_gap_var_terms.append(gap_stderr * gap_stderr)
        ecology_own_var_terms.append(own_stderr * own_stderr)

    ecology_gap_noisy = sum(ecology_gaps) / len(ecology_gaps)
    ecology_own_payoff = sum(ecology_owns) / len(ecology_owns)
    ecology_gap_noisy_stderr = math.sqrt(sum(ecology_gap_var_terms)) / len(ecology_gap_var_terms)
    ecology_own_payoff_stderr = math.sqrt(sum(ecology_own_var_terms)) / len(ecology_own_var_terms)
    ecology_gap_noisy_ci95_half_width = 1.96 * ecology_gap_noisy_stderr
    ecology_own_payoff_ci95_half_width = 1.96 * ecology_own_payoff_stderr
    recovery_settings = screening_spec["recovery_proxy"]
    recovery_rounds = _estimate_recovery_rounds(
        matrix,
        recovery_epsilon=float(recovery_settings["epsilon"]),
        recovery_horizon=int(recovery_settings["horizon"]),
        recovery_cc_mass_min=float(recovery_settings["cc_mass_min"]),
    )
    repair_settings = screening_spec["repair_proxy"]
    repair_proxy_stats = _estimate_repair_abuse_rate(
        strat_params,
        opp_params,
        rounds=int(repair_settings["rounds"]),
        reps=int(repair_settings["repetitions"]),
        noise=float(repair_settings["noise"]),
        repair_proxy_k=int(repair_settings["k"]),
    )
    repair_abuse_rate = float(repair_proxy_stats["repair_abuse_rate"])
    repair_offer_count = int(repair_proxy_stats["repair_offer_count"])

    screening_contract = _build_screening_contract(
        payoff_gap=payoff_gap,
        ecology_gap_noisy=ecology_gap_noisy,
        ecology_gap_noisy_ci95_half_width=ecology_gap_noisy_ci95_half_width,
        recovery_rounds=recovery_rounds,
        repair_abuse_rate=repair_abuse_rate,
        repair_abuse_rate_ci95_low=float(repair_proxy_stats["repair_abuse_rate_ci95_low"]),
        repair_abuse_rate_ci95_high=float(repair_proxy_stats["repair_abuse_rate_ci95_high"]),
        screening_spec=screening_spec,
    )

    return {
        "scorecard_version": 13,
        "status": "screening_proxy",
        "screening_spec_ref": _screening_spec_ref(screening_spec),
        "ecology_sampling_ref": _ecology_sampling_ref(screening_spec),
        "repair_sampling_ref": _repair_sampling_ref(screening_spec),
        "uncertainty_contract_ref": _uncertainty_contract_ref(),
        "proxy_measurement_contract_ref": _proxy_measurement_contract_ref(),
        "steady_state_contract_ref": _steady_state_contract_ref(),
        "opening_distribution_contract_ref": _opening_distribution_contract_ref(),
        "transition_kernel_contract_ref": _transition_kernel_contract_ref(),
        "own_payoff": float(own_payoff),
        "payoff_gap": float(payoff_gap),
        "recovery_rounds": int(recovery_rounds),
        "shock_protocol": str(recovery_settings["shock_protocol"]),
        "recovery_epsilon": float(recovery_settings["epsilon"]),
        "recovery_horizon": int(recovery_settings["horizon"]),
        "recovery_cc_mass_min": float(recovery_settings["cc_mass_min"]),
        "repair_abuse_rate": float(repair_abuse_rate),
        "repair_proxy_k": int(repair_settings["k"]),
        "repair_offer_count": repair_offer_count,
        "repair_abuse_count": int(repair_proxy_stats["repair_abuse_count"]),
        "repair_abuse_rate_ci95_low": float(repair_proxy_stats["repair_abuse_rate_ci95_low"]),
        "repair_abuse_rate_ci95_high": float(repair_proxy_stats["repair_abuse_rate_ci95_high"]),
        "repair_noise": float(repair_settings["noise"]),
        "repair_rounds": int(repair_settings["rounds"]),
        "repair_repetitions": int(repair_settings["repetitions"]),
        "ecology_gap_noisy": float(ecology_gap_noisy),
        "ecology_gap_noisy_stderr": float(ecology_gap_noisy_stderr),
        "ecology_gap_noisy_ci95_half_width": float(ecology_gap_noisy_ci95_half_width),
        "ecology_own_payoff": float(ecology_own_payoff),
        "ecology_own_payoff_stderr": float(ecology_own_payoff_stderr),
        "ecology_own_payoff_ci95_half_width": float(ecology_own_payoff_ci95_half_width),
        "canonical_vampire_id": "extortion_chi3",
        "ecology_pool_ids": [opponent_id for opponent_id, _ in ecology_settings["pool"]],
        "ecology_gap_by_opponent": ecology_gap_by_opponent,
        "ecology_gap_stderr_by_opponent": ecology_gap_stderr_by_opponent,
        "ecology_own_payoff_by_opponent": ecology_own_by_opponent,
        "ecology_own_payoff_stderr_by_opponent": ecology_own_payoff_stderr_by_opponent,
        "ecology_noise": float(ecology_settings["noise"]),
        "ecology_rounds": int(ecology_settings["rounds"]),
        "ecology_repetitions": int(ecology_settings["repetitions"]),
        "ecology_estimate_kind": "replicated_rollout_mean",
        "pairwise_fairness_pass": bool(screening_contract["checks"]["pairwise_fairness"]["passed"]),
        "noisy_ecology_pass": bool(screening_contract["checks"]["noisy_ecology"]["passed"]),
        "screening_contract": screening_contract,
        "full_certification_ready": bool(screening_contract["full_certification_ready"]),
        "full_certification_blockers": list(screening_contract["full_certification_blockers"]),
    }


def certify_memory_one_pair(
    strategy_a: Mapping[str, Any],
    strategy_b: Mapping[str, Any],
    *,
    screening_spec: Mapping[str, Any] | None = None,
    ecology_noise: float | None = None,
    ecology_rounds: int | None = None,
    ecology_reps: int | None = None,
) -> dict[str, Any]:
    normalized_screening_spec = _extract_screening_spec(
        screening_spec,
        ecology_noise_override=ecology_noise,
        ecology_rounds_override=ecology_rounds,
        ecology_reps_override=ecology_reps,
    )
    params_a = _extract_memory_one_params(strategy_a, "strategy_a")
    params_b = _extract_memory_one_params(strategy_b, "strategy_b")
    p = list(params_a[1:])
    q_raw = list(params_b[1:])
    # Mirror B's conditional states so both players use [CC, CD, DC, DD] from A's viewpoint.
    q = [q_raw[0], q_raw[2], q_raw[1], q_raw[3]]

    matrix = _build_transition_matrix_memory_one(p, q)
    initial_dist = _initial_distribution(params_a, params_b)
    v, steady_state_method = _steady_state_distribution(
        matrix,
        initial_dist=initial_dist,
        cesaro_steps=int(normalized_screening_spec["steady_state"]["cesaro_fallback_steps"]),
    )

    avg_a, avg_b = _payoffs_from_distribution(v)
    payoff_gap = avg_b - avg_a
    transition_graph_diagnostics = _transition_graph_diagnostics(matrix, initial_dist)
    asymptotic_distribution = _asymptotic_distribution_from_closed_class_decomposition(
        transition_graph_diagnostics["closed_class_asymptotic_decomposition_from_initial_distribution"]
    )
    asymptotic_avg_a, asymptotic_avg_b = _payoffs_from_distribution(asymptotic_distribution)
    steady_state_l1_distance_to_asymptotic = sum(
        abs(float(v[i]) - float(asymptotic_distribution[i])) for i in range(4)
    )

    return {
        "schema_version": 21,
        "kind": "certify_memory_one_result",
        "screening_spec_ref": _screening_spec_ref(normalized_screening_spec),
        "stage_game_ref": _stage_game_ref(),
        "state_order": list(_STATE_ORDER),
        "strategy_a": strategy_a.get("id"),
        "strategy_b": strategy_b.get("id"),
        "strategy_a_ref": _strategy_ref(strategy_a),
        "strategy_b_ref": _strategy_ref(strategy_b),
        "uncertainty_contract_ref": _uncertainty_contract_ref(),
        "proxy_measurement_contract_ref": _proxy_measurement_contract_ref(),
        "steady_state_contract_ref": _steady_state_contract_ref(),
        "opening_distribution_contract_ref": _opening_distribution_contract_ref(),
        "transition_kernel_contract_ref": _transition_kernel_contract_ref(),
        "pairing_ref": _pairing_ref(strategy_a, strategy_b, normalized_screening_spec),
        "initial_distribution": [float(x) for x in initial_dist],
        "transition_matrix": [[float(x) for x in row] for row in matrix],
        "transition_graph_diagnostics": transition_graph_diagnostics,
        "steady_state_distribution": [float(x) for x in v],
        "steady_state_method": steady_state_method,
        "asymptotic_distribution_from_initial_distribution": [float(x) for x in asymptotic_distribution],
        "asymptotic_distribution_method": "closed_class_exact_mixture_from_initial_distribution",
        "asymptotic_avg_payoff_a_from_initial_distribution": float(asymptotic_avg_a),
        "asymptotic_avg_payoff_b_from_initial_distribution": float(asymptotic_avg_b),
        "steady_state_distribution_l1_distance_to_asymptotic_distribution": float(
            steady_state_l1_distance_to_asymptotic
        ),
        "avg_payoff_a": float(avg_a),
        "avg_payoff_b": float(avg_b),
        "payoff_diff": float(abs(avg_a - avg_b)),
        "anti_vampire_scorecard": _build_anti_vampire_scorecard(
            strategy_a,
            strategy_b,
            avg_a,
            payoff_gap,
            matrix=matrix,
            screening_spec=normalized_screening_spec,
        ),
    }
