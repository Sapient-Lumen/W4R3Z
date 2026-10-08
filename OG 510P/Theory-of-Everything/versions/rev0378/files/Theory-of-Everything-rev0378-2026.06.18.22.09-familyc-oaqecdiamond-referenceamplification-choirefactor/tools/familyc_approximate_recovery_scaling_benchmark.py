#!/usr/bin/env python3
"""Deterministic finite-resource approximate-erasure benchmark for Family C.

The benchmark constructs a prime-dimension family of three-share polynomial
encodings.  A logical-dependent modulation of the codeword amplitudes makes the
erased share weakly informative.  Because the complementary channel is
classical-quantum, its distance from a constant channel is available exactly in
diamond norm.  The declared algebraic decoder also has an exact worst-case
entanglement fidelity.  A fixed-leakage control demonstrates the dimension-
dilution failure of max-entry Knill-Laflamme residuals.

This is an owned quantum-information stress cell, not a derivation of finite-N
AdS/CFT, JLMS, backreaction, or a boundary observer map.  It carries no route-
promotion authority.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True

from benchmark_numeric import log_log_slope, stable_number
from generated_benchmark_artifact import (
    check_generated_texts,
    generated_texts,
    parse_write_check_args,
    write_generated_texts,
)

OUTPUT_JSON = "FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json"
OUTPUT_MD = "docs/30-program/familyc-approximate-recovery-scaling-benchmark.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYC-EW-CODE"
DECISION_ID = "DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY"
SOURCE_REFS = ["REF-0531", "REF-0533", "REF-0735"]
DIMENSIONS = [7, 11, 13, 17, 19, 23, 29, 31, 37, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
SHIFT_BETA = 3
SCALED_KAPPA = 0.8
SCALED_EXPONENT = 0.5
FIXED_DELTA = 0.3
TOLERANCE = 1e-12


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def base_distribution(dimension: int, delta: float) -> list[float]:
    """Return p_D(x) = [1 + delta cos(2 pi x / D)] / D."""
    return [
        (1.0 + delta * math.cos(2.0 * math.pi * x / dimension)) / dimension
        for x in range(dimension)
    ]


def shifted_distribution(base: list[float], shift: int) -> list[float]:
    dimension = len(base)
    return [base[(x - shift) % dimension] for x in range(dimension)]


def l1_distance(left: list[float], right: list[float]) -> float:
    return sum(abs(a - b) for a, b in zip(left, right))


def bhattacharyya(left: list[float], right: list[float]) -> float:
    return sum(math.sqrt(max(0.0, a * b)) for a, b in zip(left, right))


def code_family_metrics(dimension: int, delta: float) -> dict[str, Any]:
    """Compute exact operational metrics for one family member.

    Encoding rule:
      V_D |i> = sum_j sqrt(p_D(j - beta i)) |j, j+i, j+2i>.

    For erased share s, the environment output for logical basis state i is a
    translate q_i^(s)(x) = p_D(x - (beta+s)i).  Prime D>5 makes all three
    translation coefficients invertible.  The complementary channel is thus a
    measure-in-the-logical-basis cq channel whose average output is uniform.
    """
    if not is_prime(dimension) or dimension <= SHIFT_BETA + 2:
        raise ValueError(f"dimension must be prime and > {SHIFT_BETA + 2}: {dimension}")
    if not (0.0 <= delta < 1.0):
        raise ValueError(f"delta must be in [0,1): {delta}")

    base = base_distribution(dimension, delta)
    uniform = [1.0 / dimension] * dimension
    normalization_residual = abs(sum(base) - 1.0)
    minimum_probability = min(base)

    support_states = [
        (j, (j + logical) % dimension, (j + 2 * logical) % dimension)
        for logical in range(dimension)
        for j in range(dimension)
    ]
    support_collision_count = len(support_states) - len(set(support_states))
    decoder_pair_collision_counts: dict[str, int] = {}
    for retained in ((0, 1), (0, 2), (1, 2)):
        pair_map: dict[tuple[int, int], tuple[int, int]] = {}
        collisions = 0
        missing = next(index for index in range(3) if index not in retained)
        for logical in range(dimension):
            for j in range(dimension):
                physical = (j, (j + logical) % dimension, (j + 2 * logical) % dimension)
                pair = (physical[retained[0]], physical[retained[1]])
                target = (logical, physical[missing])
                if pair in pair_map and pair_map[pair] != target:
                    collisions += 1
                pair_map[pair] = target
        collisions += dimension * dimension - len(pair_map)
        decoder_pair_collision_counts[f"{retained[0]}{retained[1]}"] = collisions

    per_share: list[dict[str, Any]] = []
    for erased_share in range(3):
        coefficient = SHIFT_BETA + erased_share
        outputs = [shifted_distribution(base, coefficient * logical) for logical in range(dimension)]
        average = [sum(output[x] for output in outputs) / dimension for x in range(dimension)]

        # For this cq complementary channel, reference assistance cannot beat a
        # logical-basis input, so max_i ||q_i - average||_1 is the exact diamond
        # norm distance to the declared constant channel.
        diamond_distance = max(l1_distance(output, average) for output in outputs)
        operational_trace_distance = 0.5 * diamond_distance
        max_entry_residual = max(
            abs(output[x] - average[x])
            for output in outputs
            for x in range(dimension)
        )

        coherence = [
            [bhattacharyya(outputs[left], outputs[right]) for right in range(dimension)]
            for left in range(dimension)
        ]
        row_sums = [sum(row) for row in coherence]
        row_sum_spread = max(row_sums) - min(row_sums)

        # The declared pair decoder yields a Schur/dephasing logical channel
        # with Gram matrix C_ik = BC(q_i,q_k).  C is positive semidefinite and
        # circulant, so uniform logical populations minimize p^T C p exactly.
        worst_case_entanglement_fidelity = sum(row_sums) / (dimension * dimension)
        direct_closed_form_fidelity = sum(math.sqrt(value) for value in base) ** 2 / dimension

        per_share.append(
            {
                "erased_share": erased_share,
                "translation_coefficient": coefficient,
                "translation_coefficient_invertible": math.gcd(coefficient, dimension) == 1,
                "average_environment_uniform_residual_l1": stable_number(l1_distance(average, uniform)),
                "complementary_channel_diamond_norm_to_constant": stable_number(diamond_distance),
                "environment_operational_trace_distance": stable_number(operational_trace_distance),
                "max_entry_knill_laflamme_residual": stable_number(max_entry_residual),
                "decoder_worst_case_entanglement_fidelity": stable_number(worst_case_entanglement_fidelity),
                "decoder_worst_case_entanglement_infidelity": stable_number(1.0 - worst_case_entanglement_fidelity),
                "decoder_closed_form_residual": stable_number(
                    abs(worst_case_entanglement_fidelity - direct_closed_form_fidelity)
                ),
                "coherence_gram_row_sum_spread": stable_number(row_sum_spread),
            }
        )

    diamond_values = [row["complementary_channel_diamond_norm_to_constant"] for row in per_share]
    max_entry_values = [row["max_entry_knill_laflamme_residual"] for row in per_share]
    infidelities = [row["decoder_worst_case_entanglement_infidelity"] for row in per_share]
    trace_distances = [row["environment_operational_trace_distance"] for row in per_share]

    return {
        "dimension": dimension,
        "logical_dimension": dimension,
        "physical_share_dimension": dimension,
        "physical_hilbert_dimension": dimension ** 3,
        "delta": stable_number(delta),
        "normalization_residual": stable_number(normalization_residual),
        "minimum_probability": stable_number(minimum_probability),
        "support_collision_count": support_collision_count,
        "decoder_pair_collision_counts": decoder_pair_collision_counts,
        "isometry_residual": stable_number(normalization_residual if support_collision_count == 0 else 1.0),
        "per_erased_share": per_share,
        "complementary_channel_diamond_norm_to_constant_max": stable_number(max(diamond_values)),
        "environment_operational_trace_distance_max": stable_number(max(trace_distances)),
        "max_entry_knill_laflamme_residual_max": stable_number(max(max_entry_values)),
        "decoder_worst_case_entanglement_infidelity_max": stable_number(max(infidelities)),
        "share_symmetry_diamond_spread": stable_number(max(diamond_values) - min(diamond_values)),
        "share_symmetry_infidelity_spread": stable_number(max(infidelities) - min(infidelities)),
        "same_record_discriminator": {
            "dictionary_a": "logical basis state |0>",
            "dictionary_b": "uniform logical superposition D^(-1/2) sum_i |i>",
            "restricted_record": "one erased-share environment record",
            "restricted_record_trace_distance": stable_number(0.5 * max(diamond_values)),
            "richer_record": "retained pair followed by the declared algebraic decoder",
            "decoded_logical_zero_witness_gap": stable_number(1.0 - 1.0 / dimension),
            "global_state_overlap_squared": stable_number(1.0 / dimension),
        },
        "information_disturbance_ratio": stable_number(
            max(infidelities) / (max(diamond_values) ** 2) if max(diamond_values) > 0 else 0.0
        ),
    }


def family_rows(delta_rule: Callable[[int], float]) -> list[dict[str, Any]]:
    return [code_family_metrics(dimension, delta_rule(dimension)) for dimension in DIMENSIONS]


def increasing(values: list[float], tolerance: float = 0.0) -> bool:
    return all(right >= left - tolerance for left, right in zip(values, values[1:]))


def decreasing(values: list[float], tolerance: float = 0.0) -> bool:
    return all(right <= left + tolerance for left, right in zip(values, values[1:]))


def compute_result(root: Path) -> dict[str, Any]:
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text())
    revision = manifest["revision"]

    scaled_rows = family_rows(lambda dimension: SCALED_KAPPA * dimension ** (-SCALED_EXPONENT))
    fixed_rows = family_rows(lambda _dimension: FIXED_DELTA)

    metric_keys = {
        "diamond": "complementary_channel_diamond_norm_to_constant_max",
        "max_entry": "max_entry_knill_laflamme_residual_max",
        "decoder_infidelity": "decoder_worst_case_entanglement_infidelity_max",
    }
    scaled_slopes = {name: stable_number(log_log_slope(scaled_rows, "dimension", key)) for name, key in metric_keys.items()}
    fixed_slopes = {name: stable_number(log_log_slope(fixed_rows, "dimension", key)) for name, key in metric_keys.items()}

    acceptance_checks: list[dict[str, Any]] = []

    def add(check: str, passed: bool, detail: Any) -> None:
        acceptance_checks.append({"check": check, "passed": bool(passed), "detail": detail})

    all_rows = scaled_rows + fixed_rows
    add(
        "dimension schedule uses distinct primes above every decoder coefficient",
        all(is_prime(dimension) and dimension > SHIFT_BETA + 2 for dimension in DIMENSIONS),
        DIMENSIONS,
    )
    add(
        "all code-family probability laws are normalized and positive",
        all(row["normalization_residual"] < TOLERANCE and row["minimum_probability"] > 0 for row in all_rows),
        f"max_normalization_residual={max(row['normalization_residual'] for row in all_rows)}",
    )
    add(
        "encoding support is collision-free and every retained-pair decoder map is bijective",
        all(
            row["support_collision_count"] == 0
            and all(count == 0 for count in row["decoder_pair_collision_counts"].values())
            for row in all_rows
        ),
        f"max_support_collisions={max(row['support_collision_count'] for row in all_rows)}; max_decoder_pair_collisions={max(count for row in all_rows for count in row['decoder_pair_collision_counts'].values())}",
    )
    add(
        "all three erased-share translation maps stay invertible",
        all(
            share["translation_coefficient_invertible"]
            for row in all_rows
            for share in row["per_erased_share"]
        ),
        "coefficients=3,4,5",
    )
    add(
        "closed-form and Gram-matrix decoder fidelities agree",
        max(
            share["decoder_closed_form_residual"]
            for row in all_rows
            for share in row["per_erased_share"]
        ) < TOLERANCE,
        f"max_residual={max(share['decoder_closed_form_residual'] for row in all_rows for share in row['per_erased_share'])}",
    )
    add(
        "erased-share operational metrics are symmetric",
        max(
            max(row["share_symmetry_diamond_spread"], row["share_symmetry_infidelity_spread"])
            for row in all_rows
        ) < TOLERANCE,
        f"max_spread={max(max(row['share_symmetry_diamond_spread'], row['share_symmetry_infidelity_spread']) for row in all_rows)}",
    )
    add(
        "scaled family complementary-channel diamond norm follows D^-1/2",
        -0.53 <= scaled_slopes["diamond"] <= -0.47,
        scaled_slopes["diamond"],
    )
    add(
        "scaled family declared-decoder infidelity follows D^-1",
        -1.04 <= scaled_slopes["decoder_infidelity"] <= -0.96,
        scaled_slopes["decoder_infidelity"],
    )
    add(
        "scaled family max-entry residual follows the dimension-diluted D^-3/2 law",
        -1.51 <= scaled_slopes["max_entry"] <= -1.49,
        scaled_slopes["max_entry"],
    )
    add(
        "fixed-leakage diamond norm does not falsely converge",
        abs(fixed_slopes["diamond"]) <= 0.01,
        fixed_slopes["diamond"],
    )
    add(
        "fixed-leakage decoder infidelity does not falsely converge",
        abs(fixed_slopes["decoder_infidelity"]) <= 0.01,
        fixed_slopes["decoder_infidelity"],
    )
    add(
        "fixed-leakage max-entry residual falsely falls as D^-1",
        -1.01 <= fixed_slopes["max_entry"] <= -0.99,
        fixed_slopes["max_entry"],
    )
    add(
        "scaled same-record collision improves monotonically",
        decreasing([row["same_record_discriminator"]["restricted_record_trace_distance"] for row in scaled_rows]),
        [
            scaled_rows[0]["same_record_discriminator"]["restricted_record_trace_distance"],
            scaled_rows[-1]["same_record_discriminator"]["restricted_record_trace_distance"],
        ],
    )
    add(
        "scaled richer-record witness gap survives and grows",
        increasing([row["same_record_discriminator"]["decoded_logical_zero_witness_gap"] for row in scaled_rows]),
        [
            scaled_rows[0]["same_record_discriminator"]["decoded_logical_zero_witness_gap"],
            scaled_rows[-1]["same_record_discriminator"]["decoded_logical_zero_witness_gap"],
        ],
    )
    asymptotic_anchors = {
        "diamond_prefactor": stable_number(2.0 * SCALED_KAPPA / math.pi),
        "max_entry_prefactor": stable_number(SCALED_KAPPA),
        "decoder_infidelity_prefactor": stable_number(SCALED_KAPPA ** 2 / 8.0),
        "information_disturbance_ratio": stable_number(math.pi ** 2 / 32.0),
    }
    last_scaled = scaled_rows[-1]
    last_dimension = float(last_scaled["dimension"])
    observed_anchors = {
        "diamond_prefactor": stable_number(
            last_scaled["complementary_channel_diamond_norm_to_constant_max"]
            * last_dimension ** SCALED_EXPONENT
        ),
        "max_entry_prefactor": stable_number(
            last_scaled["max_entry_knill_laflamme_residual_max"]
            * last_dimension ** (1.0 + SCALED_EXPONENT)
        ),
        "decoder_infidelity_prefactor": stable_number(
            last_scaled["decoder_worst_case_entanglement_infidelity_max"] * last_dimension
        ),
        "information_disturbance_ratio": last_scaled["information_disturbance_ratio"],
    }
    add(
        "large-D operational prefactors approach the analytic small-leakage anchors",
        all(
            abs(observed_anchors[key] - asymptotic_anchors[key])
            <= {
                "diamond_prefactor": 5e-4,
                "max_entry_prefactor": 1e-12,
                "decoder_infidelity_prefactor": 2e-3,
                "information_disturbance_ratio": 1e-3,
            }[key]
            for key in asymptotic_anchors
        ),
        {"observed_at_D_max": observed_anchors, "analytic_limit": asymptotic_anchors},
    )
    add(
        "information-disturbance ratio remains finite and stable",
        all(0.28 <= row["information_disturbance_ratio"] <= 0.34 for row in scaled_rows),
        [scaled_rows[0]["information_disturbance_ratio"], scaled_rows[-1]["information_disturbance_ratio"]],
    )

    failures = [check["check"] for check in acceptance_checks if not check["passed"]]
    first_fixed = fixed_rows[0]
    last_fixed = fixed_rows[-1]
    max_entry_reduction = (
        first_fixed["max_entry_knill_laflamme_residual_max"]
        / last_fixed["max_entry_knill_laflamme_residual_max"]
    )
    diamond_reduction = (
        first_fixed["complementary_channel_diamond_norm_to_constant_max"]
        / last_fixed["complementary_channel_diamond_norm_to_constant_max"]
    )

    return {
        "artifact_id": "FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK",
        "revision": revision,
        "route_id": ROUTE_ID,
        "decision_experiment_id": DECISION_ID,
        "epistemic_status": "owned finite-resource approximate-QEC stress cell; route-local S3 pressure only",
        "authority_cap": "S3",
        "scientific_question": "Can a growing code family expose an operational approximate-recovery scaling law while detecting the false convergence produced by dimension-diluted max-entry residuals?",
        "source_refs": SOURCE_REFS,
        "model_definition": {
            "dimension_schedule": DIMENSIONS,
            "resource_parameter": "prime local/logical dimension D; physical Hilbert dimension D^3",
            "encoding_rule": "V_D|i> = sum_j sqrt(p_D(j-3i)) |j, j+i mod D, j+2i mod D>",
            "base_probability_rule": "p_D(x) = [1 + delta_D cos(2*pi*x/D)]/D",
            "erasure_model": "erase exactly one of the three physical shares",
            "declared_decoder": "invert the retained polynomial pair to recover logical i and the erased-share label; discard the decoder ancilla",
            "scaled_leakage_rule": f"delta_D = {SCALED_KAPPA} D^(-{SCALED_EXPONENT})",
            "fixed_leakage_control_rule": f"delta_D = {FIXED_DELTA}",
            "physical_status": "The D-scaling is a declared finite-resource model selected to test information-disturbance and norm scaling. D is not identified with CFT N, 1/G, bond dimension, central charge, area, or a physical finite-N correction.",
        },
        "metric_definitions": {
            "complementary_channel_diamond_norm_to_constant": "Exact ||N_c - S_uniform||_diamond. Exactness follows because N_c is a logical-basis measure-and-prepare channel; a basis input attains the maximum and reference assistance cannot exceed it.",
            "environment_operational_trace_distance": "One half of the diamond norm, giving the optimal single-use record distinguishability convention.",
            "max_entry_knill_laflamme_residual": "Largest absolute matrix-entry deviation of an erased-share output from the average output. It is retained only to demonstrate dimension dilution and is forbidden as a cross-size convergence metric.",
            "decoder_worst_case_entanglement_infidelity": "1 - min_rho F_e(rho, R_declared o N). For the circulant positive-semidefinite coherence Gram matrix, uniform logical populations attain the exact minimum.",
        },
        "scaled_family": {
            "rows": scaled_rows,
            "fitted_log_log_slopes": scaled_slopes,
            "expected_slopes": {
                "diamond": -0.5,
                "max_entry": -1.5,
                "decoder_infidelity": -1.0,
            },
            "analytic_small_leakage_anchors": {
                "derivation": "For p_D=(1+delta cos)/D, ||N_c-S||_diamond tends to 2 delta/pi; the declared-decoder infidelity tends to delta^2/8; max-entry residual equals delta/D. With delta=kappa D^-1/2 this fixes the three prefactors and the asymptotic ratio infidelity/diamond^2=pi^2/32.",
                "predicted_prefactors": asymptotic_anchors,
                "observed_at_largest_dimension": observed_anchors,
            },
            "interpretation": "Operational environment leakage falls as D^-1/2 and the declared decoder's worst-case entanglement infidelity falls as D^-1. The squared relationship and its pi^2/32 asymptotic ratio are the substantive approximate-recovery result of this toy family.",
        },
        "fixed_leakage_negative_control": {
            "rows": fixed_rows,
            "fitted_log_log_slopes": fixed_slopes,
            "expected_slopes": {
                "diamond": 0.0,
                "max_entry": -1.0,
                "decoder_infidelity": 0.0,
            },
            "interpretation": "Increasing Hilbert-space dimension alone does not improve operational recoverability. The max-entry residual nevertheless tends to zero as 1/D, creating a false convergence signal.",
        },
        "norm_dilution_audit": {
            "severity": "severe cross-size metric failure",
            "finding": "A max-entry Knill-Laflamme residual is valid as a same-dimension diagnostic but unsafe as a growing-dimension convergence norm. In the fixed-leakage control it shrinks by the dimension ratio while the exact complementary-channel diamond norm and decoder infidelity stay constant.",
            "first_dimension": first_fixed["dimension"],
            "last_dimension": last_fixed["dimension"],
            "max_entry_residual_reduction_factor": stable_number(max_entry_reduction),
            "diamond_norm_reduction_factor": stable_number(diamond_reduction),
            "correction": "Cross-size Family-C recovery claims must report an operational channel norm or a dimension-aware bound plus a declared recovery fidelity; max-entry residuals may not carry scaling language by themselves.",
        },
        "acceptance_checks": acceptance_checks,
        "validation_failures": failures,
        "hard_limits": [
            "This is a deterministic polynomial-code family with a chosen amplitude modulation, not a boundary CFT or gravitational code.",
            "The resource D is not a physical finite-N/JLMS parameter and no map to G, central charge, area, bond dimension, or backreaction is supplied.",
            "The benchmark treats one-share erasure only; it does not implement operator-algebra centers, edge modes, islands, QES competition, or state-dependent wedge changes.",
            "The declared algebraic decoder is evaluated exactly, but no claim of globally optimal recovery is made.",
            "Passing the cell creates no acquired evidence, observed-sector recovery, public-record closure, or Theory-of-Everything identity.",
        ],
        "next_kernel_step": "Use FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json to join separate full-system/subregion FLM control, eps_OD, the remaining projected-JLMS terms, and a p-weighted sector-inflow/log-smoothness bound on one state domain; then relate the source-closed flagged recovery budget to this complementary-channel norm without setting D=N and test whether the exponent and same-record discriminator survive code-subspace growth and a non-AdS observer map.",
    }


def render_markdown(result: dict[str, Any]) -> str:
    scaled = result["scaled_family"]
    fixed = result["fixed_leakage_negative_control"]
    audit = result["norm_dilution_audit"]
    lines = [
        "# Family-C approximate-recovery scaling benchmark (generated)",
        "",
        "This owned finite-resource code family replaces a free leakage sweep with an explicit resource parameter, an exact complementary-channel diamond norm, and an exact worst-case entanglement fidelity for the declared decoder. It remains a quantum-information toy model, not finite-N holography.",
        "",
        f"- Route: `{result['route_id']}`",
        f"- Decision experiment: `{result['decision_experiment_id']}`",
        f"- Status: {result['epistemic_status']}",
        f"- Replay: `python3 tools/familyc_approximate_recovery_scaling_benchmark.py --check`",
        f"- Validation failures: `{len(result['validation_failures'])}`",
        "",
        "## Construction",
        "",
        "For each prime `D > 5`, the encoder uses",
        "",
        "`V_D|i> = sum_j sqrt(p_D(j-3i)) |j, j+i, j+2i>`,",
        "",
        "with `p_D(x) = [1 + delta_D cos(2*pi*x/D)]/D`. Any retained pair algebraically identifies the logical label and erased-share label, but the erased share carries weak logical information whenever `delta_D != 0`.",
        "",
        "The complementary channel is classical-quantum, so its distance from the uniform constant channel is available exactly in diamond norm. The declared decoder yields a circulant dephasing channel, whose exact worst-case entanglement fidelity is attained by uniform logical populations.",
        "",
        "## Resource-scaled family",
        "",
        f"Declared rule: `delta_D = {SCALED_KAPPA} D^(-{SCALED_EXPONENT})`.",
        "",
        "| D | delta | complement diamond norm | max-entry KL residual | decoder infidelity | restricted-record distance | richer witness gap |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in scaled["rows"]:
        same = row["same_record_discriminator"]
        lines.append(
            "| `{dimension}` | `{delta}` | `{diamond}` | `{entry}` | `{infidelity}` | `{record}` | `{gap}` |".format(
                dimension=row["dimension"],
                delta=row["delta"],
                diamond=row["complementary_channel_diamond_norm_to_constant_max"],
                entry=row["max_entry_knill_laflamme_residual_max"],
                infidelity=row["decoder_worst_case_entanglement_infidelity_max"],
                record=same["restricted_record_trace_distance"],
                gap=same["decoded_logical_zero_witness_gap"],
            )
        )
    lines += [
        "",
        "### Fitted scaling",
        "",
        "| Metric | Fitted slope | Declared expectation |",
        "|---|---:|---:|",
        f"| Complement diamond norm | `{scaled['fitted_log_log_slopes']['diamond']}` | `-0.5` |",
        f"| Decoder worst-case entanglement infidelity | `{scaled['fitted_log_log_slopes']['decoder_infidelity']}` | `-1.0` |",
        f"| Max-entry residual | `{scaled['fitted_log_log_slopes']['max_entry']}` | `-1.5` |",
        "",
        "The operational leakage falls as `D^-1/2`, while declared-decoder infidelity falls as `D^-1`. The same restricted-record collision improves with size, while the decoded logical-zero witness gap remains large and tends to one.",
        "",
        "### Analytic asymptotic anchor",
        "",
        "For small leakage, the cosine family gives `||N_c-S||_diamond -> 2 delta/pi`, declared-decoder infidelity `-> delta^2/8`, and max-entry residual exactly `delta/D`. Thus `delta=0.8 D^-1/2` predicts prefactors `1.6/pi`, `0.08`, and `0.8`, together with `infidelity/diamond^2 -> pi^2/32`. The largest-D computation is checked against all four anchors; this makes the fitted slopes a replay of an analytic limit rather than a free regression story.",
        "",
        "## Fixed-leakage negative control",
        "",
        f"The control holds `delta_D = {FIXED_DELTA}` while increasing `D`.",
        "",
        "| Metric | Fitted slope | Correct reading |",
        "|---|---:|---|",
        f"| Complement diamond norm | `{fixed['fitted_log_log_slopes']['diamond']}` | no operational convergence |",
        f"| Decoder infidelity | `{fixed['fitted_log_log_slopes']['decoder_infidelity']}` | no recovery convergence |",
        f"| Max-entry residual | `{fixed['fitted_log_log_slopes']['max_entry']}` | false `1/D` convergence from entry dilution |",
        "",
        "## Severe metric failure corrected",
        "",
        audit["finding"],
        "",
        f"Across `D={audit['first_dimension']}` to `D={audit['last_dimension']}`, the max-entry residual improves by a factor of `{audit['max_entry_residual_reduction_factor']}`, while the exact diamond norm changes only by a factor of `{audit['diamond_norm_reduction_factor']}`.",
        "",
        f"**Correction:** {audit['correction']}",
        "",
        "## Acceptance checks",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["acceptance_checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['check']} | `{str(check['passed']).lower()}` | {detail} |")
    lines += [
        "",
        "## Hard limits and next denominator",
        "",
    ]
    lines.extend(f"- {limit}" for limit in result["hard_limits"])
    lines += ["", f"Next kernel step: {result['next_kernel_step']}", ""]
    return "\n".join(lines)


def main() -> int:
    args = parse_write_check_args(__doc__ or "")
    root = Path(__file__).resolve().parents[1]
    result = compute_result(root)
    texts = generated_texts(OUTPUT_JSON, OUTPUT_MD, result, render_markdown(result))
    if args.check:
        failures = check_generated_texts(root, texts, result["validation_failures"])
        if failures:
            print("FAMILYC APPROXIMATE RECOVERY SCALING BENCHMARK FAILED")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("FAMILYC APPROXIMATE RECOVERY SCALING BENCHMARK OK")
        return 0

    write_generated_texts(root, texts)
    if result["validation_failures"]:
        print("FAMILYC APPROXIMATE RECOVERY SCALING BENCHMARK WROTE FAILING RESULT")
        for failure in result["validation_failures"]:
            print(f"- {failure}")
        return 1
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
