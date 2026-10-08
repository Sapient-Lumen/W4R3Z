#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grlab.certify import CertifyError, certify_memory_one_pair


def _memory_one(strategy_id: str, p_cc: float, p_cd: float, p_dc: float, p_dd: float) -> dict[str, object]:
    return {
        "family": "memory_one",
        "id": strategy_id,
        "p0": p_cc,
        "p_cc": p_cc,
        "p_cd": p_cd,
        "p_dc": p_dc,
        "p_dd": p_dd,
    }


def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def main() -> int:
    root = ROOT
    out = root / "artifacts" / "formal" / "certify_invariants.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    pairs = [
        {
            "id": "allc_vs_allc",
            "a": _memory_one("allc", 1.0, 1.0, 1.0, 1.0),
            "b": _memory_one("allc", 1.0, 1.0, 1.0, 1.0),
            "expected": {"avg_payoff_a": 3.0, "avg_payoff_b": 3.0, "state_idx": 0},
        },
        {
            "id": "alld_vs_alld",
            "a": _memory_one("alld", 0.0, 0.0, 0.0, 0.0),
            "b": _memory_one("alld", 0.0, 0.0, 0.0, 0.0),
            "expected": {"avg_payoff_a": 1.0, "avg_payoff_b": 1.0, "state_idx": 3},
        },
        {
            "id": "allc_vs_alld",
            "a": _memory_one("allc", 1.0, 1.0, 1.0, 1.0),
            "b": _memory_one("alld", 0.0, 0.0, 0.0, 0.0),
            "expected": {"avg_payoff_a": 0.0, "avg_payoff_b": 5.0, "state_idx": 1},
        },
        {
            "id": "tft_vs_tft",
            "a": _memory_one("tft", 1.0, 0.0, 1.0, 0.0),
            "b": _memory_one("tft", 1.0, 0.0, 1.0, 0.0),
            "expected": {"avg_payoff_a": 3.0, "avg_payoff_b": 3.0, "state_idx": 0},
            "expected_method": "cesaro_from_initial_distribution",
        },
    ]

    checks: list[dict[str, object]] = []
    failed = False

    for pair in pairs:
        row: dict[str, object] = {"id": pair["id"], "ok": True}
        try:
            result = certify_memory_one_pair(pair["a"], pair["b"])
        except CertifyError as exc:
            expected_error = str(pair.get("expected_error", "")).strip().lower()
            got_error = str(exc)
            if expected_error and expected_error in got_error.lower():
                row["expected_error"] = expected_error
                row["error"] = got_error
                row["ok"] = True
            else:
                row["ok"] = False
                row["error"] = got_error
                failed = True
            checks.append(row)
            continue

        dist = result["steady_state_distribution"]
        total = sum(float(x) for x in dist)
        in_range = all(0.0 <= float(x) <= 1.0 for x in dist)
        payoff_range = 0.0 <= float(result["avg_payoff_a"]) <= 5.0 and 0.0 <= float(result["avg_payoff_b"]) <= 5.0
        symmetry = _approx(float(result["avg_payoff_a"]) - float(result["avg_payoff_b"]), 0.0) if pair["a"]["id"] == pair["b"]["id"] else True

        expected_match = True
        expected = pair.get("expected")
        if isinstance(expected, dict):
            expected_match = (
                _approx(float(result["avg_payoff_a"]), float(expected["avg_payoff_a"]))
                and _approx(float(result["avg_payoff_b"]), float(expected["avg_payoff_b"]))
                and _approx(float(dist[int(expected["state_idx"])]), 1.0)
            )
        expected_method_ok = True
        expected_method = pair.get("expected_method")
        if isinstance(expected_method, str) and expected_method:
            expected_method_ok = str(result.get("steady_state_method")) == expected_method

        ecology_sampling_ref = result["anti_vampire_scorecard"].get("ecology_sampling_ref", {})
        repair_sampling_ref = result["anti_vampire_scorecard"].get("repair_sampling_ref", {})
        sampling_refs_present = (
            isinstance(ecology_sampling_ref.get("sampling_plan_fingerprint_sha256"), str)
            and len(ecology_sampling_ref["sampling_plan_fingerprint_sha256"]) == 64
            and isinstance(repair_sampling_ref.get("sampling_plan_fingerprint_sha256"), str)
            and len(repair_sampling_ref["sampling_plan_fingerprint_sha256"]) == 64
        )

        proxy_measurement_ref = result.get("proxy_measurement_contract_ref", {})
        proxy_measurement_ref_present = (
            isinstance(proxy_measurement_ref.get("contract_fingerprint_sha256"), str)
            and len(proxy_measurement_ref["contract_fingerprint_sha256"]) == 64
        )

        steady_state_ref = result.get("steady_state_contract_ref", {})
        steady_state_ref_present = (
            isinstance(steady_state_ref.get("contract_fingerprint_sha256"), str)
            and len(steady_state_ref["contract_fingerprint_sha256"]) == 64
        )

        opening_distribution_ref = result.get("opening_distribution_contract_ref", {})
        opening_distribution_ref_present = (
            isinstance(opening_distribution_ref.get("contract_fingerprint_sha256"), str)
            and len(opening_distribution_ref["contract_fingerprint_sha256"]) == 64
        )

        transition_kernel_ref = result.get("transition_kernel_contract_ref", {})
        transition_kernel_ref_present = (
            isinstance(transition_kernel_ref.get("contract_fingerprint_sha256"), str)
            and len(transition_kernel_ref["contract_fingerprint_sha256"]) == 64
        )
        transition_matrix = result.get("transition_matrix", [])
        transition_matrix_shape_ok = (
            isinstance(transition_matrix, list)
            and len(transition_matrix) == 4
            and all(isinstance(row, list) and len(row) == 4 for row in transition_matrix)
            and all(_approx(sum(float(x) for x in row), 1.0, tol=1e-9) for row in transition_matrix)
        )

        transition_graph_diagnostics = result.get("transition_graph_diagnostics", {})
        closed_class_entry_probabilities = transition_graph_diagnostics.get(
            "closed_class_entry_probabilities_from_initial_distribution", []
        )
        closed_class_entry_probabilities_present = (
            isinstance(closed_class_entry_probabilities, list)
            and all(
                isinstance(item, dict)
                and isinstance(item.get("closed_class"), list)
                and isinstance(item.get("entry_probability"), (int, float))
                and 0.0 <= float(item["entry_probability"]) <= 1.0
                and (
                    item.get("conditional_expected_entry_steps_from_initial_distribution") is None
                    or (
                        isinstance(item.get("conditional_expected_entry_steps_from_initial_distribution"), (int, float))
                        and float(item["conditional_expected_entry_steps_from_initial_distribution"]) >= 0.0
                    )
                )
                for item in closed_class_entry_probabilities
            )
        )
        closed_class_entry_probabilities_sum_ok = (
            closed_class_entry_probabilities_present
            and _approx(sum(float(item["entry_probability"]) for item in closed_class_entry_probabilities), 1.0, tol=1e-9)
        )
        closed_class_decomposition = transition_graph_diagnostics.get(
            "closed_class_asymptotic_decomposition_from_initial_distribution", []
        )
        closed_class_decomposition_present = (
            isinstance(closed_class_decomposition, list)
            and all(
                isinstance(item, dict)
                and isinstance(item.get("closed_class"), list)
                and isinstance(item.get("entry_probability"), (int, float))
                and isinstance(item.get("class_stationary_distribution"), list)
                and len(item.get("class_stationary_distribution", [])) == 4
                and isinstance(item.get("weighted_steady_state_contribution"), list)
                and len(item.get("weighted_steady_state_contribution", [])) == 4
                and isinstance(item.get("class_avg_payoff_a"), (int, float))
                and isinstance(item.get("class_avg_payoff_b"), (int, float))
                and _approx(sum(float(x) for x in item["class_stationary_distribution"]), 1.0, tol=1e-9)
                and _approx(
                    sum(float(x) for x in item["weighted_steady_state_contribution"]),
                    float(item["entry_probability"]),
                    tol=1e-9,
                )
                for item in closed_class_decomposition
            )
        )
        asymptotic_distribution = result.get("asymptotic_distribution_from_initial_distribution", [])
        closed_class_decomposition_reconstructs_asymptotic_distribution = False
        if closed_class_decomposition_present and isinstance(asymptotic_distribution, list) and len(asymptotic_distribution) == 4:
            reconstructed = [
                sum(float(item["weighted_steady_state_contribution"][i]) for item in closed_class_decomposition)
                for i in range(4)
            ]
            closed_class_decomposition_reconstructs_asymptotic_distribution = all(
                _approx(reconstructed[i], float(asymptotic_distribution[i]), tol=1e-9) for i in range(4)
            )
        asymptotic_surface_present = (
            result.get("asymptotic_distribution_method") == "closed_class_exact_mixture_from_initial_distribution"
            and isinstance(asymptotic_distribution, list)
            and len(asymptotic_distribution) == 4
            and _approx(sum(float(x) for x in asymptotic_distribution), 1.0, tol=1e-9)
            and isinstance(result.get("asymptotic_avg_payoff_a_from_initial_distribution"), (int, float))
            and isinstance(result.get("asymptotic_avg_payoff_b_from_initial_distribution"), (int, float))
            and isinstance(result.get("steady_state_distribution_l1_distance_to_asymptotic_distribution"), (int, float))
            and float(result["steady_state_distribution_l1_distance_to_asymptotic_distribution"]) >= 0.0
        )
        transition_graph_diagnostics_present = (
            transition_graph_diagnostics.get("state_order") == ["CC", "CD", "DC", "DD"]
            and isinstance(transition_graph_diagnostics.get("reducible"), bool)
            and isinstance(transition_graph_diagnostics.get("communicating_class_count"), int)
            and isinstance(transition_graph_diagnostics.get("closed_class_count"), int)
            and isinstance(transition_graph_diagnostics.get("communicating_classes"), list)
            and isinstance(transition_graph_diagnostics.get("closed_classes"), list)
            and isinstance(transition_graph_diagnostics.get("initial_support_states"), list)
            and isinstance(transition_graph_diagnostics.get("reachable_states_from_initial_support"), list)
            and isinstance(transition_graph_diagnostics.get("expected_steps_to_any_closed_class_from_initial_distribution"), (int, float))
            and float(transition_graph_diagnostics.get("expected_steps_to_any_closed_class_from_initial_distribution", 0.0)) >= 0.0
            and isinstance(
                transition_graph_diagnostics.get(
                    "multiple_closed_classes_with_positive_entry_probability_from_initial_distribution"
                ),
                bool,
            )
            and closed_class_entry_probabilities_present
            and closed_class_decomposition_present
        )

        row.update(
            {
                "sum_to_one": _approx(total, 1.0),
                "dist_in_range": in_range,
                "payoff_in_range": payoff_range,
                "symmetry_if_identical": symmetry,
                "expected_match": expected_match,
                "expected_method_ok": expected_method_ok,
                "sampling_refs_present": sampling_refs_present,
                "proxy_measurement_ref_present": proxy_measurement_ref_present,
                "steady_state_ref_present": steady_state_ref_present,
                "opening_distribution_ref_present": opening_distribution_ref_present,
                "transition_kernel_ref_present": transition_kernel_ref_present,
                "transition_matrix_shape_ok": transition_matrix_shape_ok,
                "transition_graph_diagnostics_present": transition_graph_diagnostics_present,
                "closed_class_entry_probabilities_sum_ok": closed_class_entry_probabilities_sum_ok,
                "asymptotic_surface_present": asymptotic_surface_present,
                "closed_class_decomposition_reconstructs_asymptotic_distribution": closed_class_decomposition_reconstructs_asymptotic_distribution,
                "result": result,
            }
        )

        row_ok = bool(row["sum_to_one"] and row["dist_in_range"] and row["payoff_in_range"] and row["symmetry_if_identical"] and row["expected_match"] and row["expected_method_ok"] and row["sampling_refs_present"] and row["proxy_measurement_ref_present"] and row["steady_state_ref_present"] and row["opening_distribution_ref_present"] and row["transition_kernel_ref_present"] and row["transition_matrix_shape_ok"] and row["transition_graph_diagnostics_present"] and row["closed_class_entry_probabilities_sum_ok"] and row["asymptotic_surface_present"] and row["closed_class_decomposition_reconstructs_asymptotic_distribution"])
        row["ok"] = row_ok
        if not row_ok:
            failed = True
        checks.append(row)

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "check": "certify_invariants",
        "cases": checks,
        "ok": not failed,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"formal: wrote {out}")

    if failed:
        print("formal: certify invariants failed", file=sys.stderr)
        return 1
    print(f"formal: certify invariants ok ({len(checks)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
