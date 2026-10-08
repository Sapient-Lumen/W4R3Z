#!/usr/bin/env python3
"""Deterministic three-qutrit reconstruction stress cell for Family C.

This is an owned, finite-dimensional toy benchmark.  It verifies exact
single-erasure correction for the three-qutrit code, demonstrates two logical
hypotheses that collide on every one-share record but separate after any-two-
share decoding, sweeps a declared leakage deformation, and runs a repetition-
code negative control.  It is not a finite-N AdS/CFT calculation and carries
no route-promotion authority.
"""
from __future__ import annotations

import cmath
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from benchmark_numeric import stable_number
from generated_benchmark_artifact import (
    check_generated_texts,
    generated_texts,
    parse_write_check_args,
    write_generated_texts,
)

OUTPUT_JSON = "FAMILYC-QUTRIT-RECONSTRUCTION-BENCHMARK.json"
OUTPUT_MD = "docs/30-program/familyc-qutrit-reconstruction-benchmark.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYC-EW-CODE"
DECISION_ID = "DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY"
SOURCE_REFS = ["REF-0530", "REF-0531", "REF-0735"]
EPSILON_SWEEP = [0.0, 0.01, 0.03, 0.1, 0.2, 0.35]
TOLERANCE = 1e-12

BasisState = tuple[int, int, int]
SparseState = dict[BasisState, complex]
Matrix = list[list[complex]]


def clean_state(state: SparseState, tolerance: float = 1e-15) -> SparseState:
    return {basis: amplitude for basis, amplitude in state.items() if abs(amplitude) > tolerance}


def add_states(*terms: tuple[complex, SparseState]) -> SparseState:
    output: SparseState = {}
    for scale, state in terms:
        for basis, amplitude in state.items():
            output[basis] = output.get(basis, 0j) + scale * amplitude
    return clean_state(output)


def inner(left: SparseState, right: SparseState) -> complex:
    return sum(amplitude.conjugate() * right.get(basis, 0j) for basis, amplitude in left.items())


def exact_code_basis() -> list[SparseState]:
    """Return the standard exact three-qutrit code basis."""
    normalization = 1 / math.sqrt(3)
    return [
        {
            (j, (j + logical) % 3, (j + 2 * logical) % 3): normalization
            for j in range(3)
        }
        for logical in range(3)
    ]


def repetition_basis() -> list[SparseState]:
    """Return an isometric classical repetition encoding used as a control."""
    return [{(logical, logical, logical): 1 + 0j} for logical in range(3)]


def leakage_marker_basis() -> list[SparseState]:
    """Return orthonormal marker states outside the exact code support."""
    markers = [(0, 0, 1), (1, 1, 2), (2, 2, 0)]
    return [{markers[logical]: 1 + 0j} for logical in range(3)]


def deformed_basis(epsilon: float) -> list[SparseState]:
    """Mix exact codewords with declared orthogonal leakage markers."""
    exact = exact_code_basis()
    markers = leakage_marker_basis()
    exact_weight = math.sqrt(1 - epsilon * epsilon)
    return [
        add_states((exact_weight, exact[logical]), (epsilon, markers[logical]))
        for logical in range(3)
    ]


def encode(logical_state: list[complex], code_basis: list[SparseState]) -> SparseState:
    return add_states(*[(logical_state[index], code_basis[index]) for index in range(3)])


def matrix_index(values: tuple[int, ...]) -> int:
    index = 0
    for value in values:
        index = index * 3 + value
    return index


def reduced_operator(ket: SparseState, bra: SparseState, keep: tuple[int, ...]) -> Matrix:
    traced = tuple(index for index in range(3) if index not in keep)
    dimension = 3 ** len(keep)
    matrix = [[0j for _ in range(dimension)] for _ in range(dimension)]
    for ket_basis, ket_amplitude in ket.items():
        for bra_basis, bra_amplitude in bra.items():
            if all(ket_basis[index] == bra_basis[index] for index in traced):
                row = matrix_index(tuple(ket_basis[index] for index in keep))
                column = matrix_index(tuple(bra_basis[index] for index in keep))
                matrix[row][column] += ket_amplitude * bra_amplitude.conjugate()
    return matrix


def matrix_difference(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] - right[row][column] for column in range(len(left))]
        for row in range(len(left))
    ]


def frobenius_norm(matrix: Matrix) -> float:
    return math.sqrt(sum(abs(value) ** 2 for row in matrix for value in row))


def isometry_residual(code_basis: list[SparseState]) -> float:
    return max(
        abs(inner(code_basis[left], code_basis[right]) - (1 if left == right else 0))
        for left in range(3)
        for right in range(3)
    )


def knill_laflamme_erasure_residual(code_basis: list[SparseState]) -> tuple[float, list[float]]:
    """Measure the single-erasure Knill-Laflamme residual on each share."""
    residuals: list[float] = []
    for share in range(3):
        reduced = [
            [reduced_operator(code_basis[left], code_basis[right], (share,)) for right in range(3)]
            for left in range(3)
        ]
        reference = [
            [sum(reduced[index][index][row][column] for index in range(3)) / 3 for column in range(3)]
            for row in range(3)
        ]
        share_residual = 0.0
        for left in range(3):
            for right in range(3):
                for row in range(3):
                    for column in range(3):
                        target = reference[row][column] if left == right else 0j
                        share_residual = max(
                            share_residual,
                            abs(reduced[left][right][row][column] - target),
                        )
        residuals.append(share_residual)
    return max(residuals), residuals


def one_share_basis_record_spread(code_basis: list[SparseState]) -> tuple[float, list[float]]:
    residuals: list[float] = []
    for share in range(3):
        records = [reduced_operator(codeword, codeword, (share,)) for codeword in code_basis]
        residuals.append(
            max(
                frobenius_norm(matrix_difference(records[left], records[right]))
                for left in range(3)
                for right in range(left + 1, 3)
            )
        )
    return max(residuals), residuals


def one_share_coherence_leakage(code_basis: list[SparseState]) -> tuple[float, list[float]]:
    residuals: list[float] = []
    for share in range(3):
        residuals.append(
            max(
                frobenius_norm(reduced_operator(code_basis[left], code_basis[right], (share,)))
                for left in range(3)
                for right in range(3)
                if left != right
            )
        )
    return max(residuals), residuals


def exact_decoder_map(retained: tuple[int, int]) -> tuple[int, dict[tuple[int, int], tuple[int, int]]]:
    """Infer the exact-code permutation decoder for a retained share pair."""
    missing = next(index for index in range(3) if index not in retained)
    mapping: dict[tuple[int, int], tuple[int, int]] = {}
    for logical in range(3):
        for j in range(3):
            physical = (j, (j + logical) % 3, (j + 2 * logical) % 3)
            pair = (physical[retained[0]], physical[retained[1]])
            mapping[pair] = (logical, physical[missing])
    if len(mapping) != 9:
        raise RuntimeError(f"decoder map for {retained} is not bijective")
    return missing, mapping


def decode_with_exact_map(state: SparseState, retained: tuple[int, int]) -> SparseState:
    missing, mapping = exact_decoder_map(retained)
    output: SparseState = {}
    for physical, amplitude in state.items():
        logical, ancilla = mapping[(physical[retained[0]], physical[retained[1]])]
        decoded = (logical, ancilla, physical[missing])
        output[decoded] = output.get(decoded, 0j) + amplitude
    return clean_state(output)


def ideal_decoded_state(logical_state: list[complex]) -> SparseState:
    normalization = 1 / math.sqrt(3)
    return {
        (logical, marker, marker): logical_state[logical] * normalization
        for logical in range(3)
        for marker in range(3)
        if abs(logical_state[logical]) > 0
    }


def pure_state_fidelity(left: SparseState, right: SparseState) -> float:
    denominator = inner(left, left).real * inner(right, right).real
    if denominator <= 0:
        return 0.0
    return min(1.0, max(0.0, abs(inner(left, right)) ** 2 / denominator))


def logical_density_after_decode(state: SparseState, retained: tuple[int, int]) -> Matrix:
    return reduced_operator(decode_with_exact_map(state, retained), decode_with_exact_map(state, retained), (0,))


def logical_probes() -> dict[str, list[complex]]:
    normalization = 1 / math.sqrt(3)
    omega = cmath.exp(2j * math.pi / 3)
    return {
        "basis_0": [1, 0, 0],
        "basis_1": [0, 1, 0],
        "basis_2": [0, 0, 1],
        "uniform": [normalization, normalization, normalization],
        "fourier_phase": [normalization, normalization * omega, normalization * omega * omega],
    }


def decoder_fidelity_metrics(code_basis: list[SparseState]) -> tuple[float, dict[str, float]]:
    pair_minimums: dict[str, float] = {}
    for retained in [(0, 1), (0, 2), (1, 2)]:
        fidelities = [
            pure_state_fidelity(
                decode_with_exact_map(encode(probe, code_basis), retained),
                ideal_decoded_state(probe),
            )
            for probe in logical_probes().values()
        ]
        pair_minimums[f"{retained[0]}{retained[1]}"] = min(fidelities)
    return min(pair_minimums.values()), pair_minimums


def same_record_discriminator_metrics(code_basis: list[SparseState]) -> dict[str, Any]:
    """Compare two declared logical dictionaries on restricted/richer records."""
    normalization = 1 / math.sqrt(3)
    dictionary_a = encode([1, 0, 0], code_basis)
    dictionary_b = encode([normalization, normalization, normalization], code_basis)

    single_share_distances = [
        frobenius_norm(
            matrix_difference(
                reduced_operator(dictionary_a, dictionary_a, (share,)),
                reduced_operator(dictionary_b, dictionary_b, (share,)),
            )
        )
        for share in range(3)
    ]
    pair_witness_gaps: list[float] = []
    for retained in [(0, 1), (0, 2), (1, 2)]:
        decoded_a = logical_density_after_decode(dictionary_a, retained)
        decoded_b = logical_density_after_decode(dictionary_b, retained)
        pair_witness_gaps.append(abs(decoded_a[0][0].real - decoded_b[0][0].real))

    return {
        "dictionary_a": "named logical record 0 maps to encoded |0>",
        "dictionary_b": "named logical record 0 maps to encoded (|0>+|1>+|2>)/sqrt(3)",
        "one_share_record_distance_max": stable_number(max(single_share_distances)),
        "one_share_record_distance_by_share": [stable_number(value) for value in single_share_distances],
        "any_two_share_logical_zero_witness_gap_min": stable_number(min(pair_witness_gaps)),
        "any_two_share_logical_zero_witness_gap_by_pair": [stable_number(value) for value in pair_witness_gaps],
        "global_state_overlap_squared": stable_number(abs(inner(dictionary_a, dictionary_b)) ** 2),
    }


def summarize_code(code_basis: list[SparseState]) -> dict[str, Any]:
    kl_max, kl_by_share = knill_laflamme_erasure_residual(code_basis)
    spread_max, spread_by_share = one_share_basis_record_spread(code_basis)
    coherence_max, coherence_by_share = one_share_coherence_leakage(code_basis)
    decoder_min, decoder_by_pair = decoder_fidelity_metrics(code_basis)
    return {
        "isometry_residual_max": stable_number(isometry_residual(code_basis)),
        "single_erasure_knill_laflamme_residual_max": stable_number(kl_max),
        "single_erasure_knill_laflamme_residual_by_share": [stable_number(value) for value in kl_by_share],
        "one_share_basis_record_spread_max": stable_number(spread_max),
        "one_share_basis_record_spread_by_share": [stable_number(value) for value in spread_by_share],
        "one_share_coherence_leakage_max": stable_number(coherence_max),
        "one_share_coherence_leakage_by_share": [stable_number(value) for value in coherence_by_share],
        "any_two_share_decoder_fidelity_min": stable_number(decoder_min),
        "any_two_share_decoder_fidelity_by_pair": {
            pair: stable_number(value) for pair, value in decoder_by_pair.items()
        },
        "same_record_discriminator": same_record_discriminator_metrics(code_basis),
    }


def nondecreasing(values: list[float], tolerance: float = 1e-14) -> bool:
    return all(values[index + 1] + tolerance >= values[index] for index in range(len(values) - 1))


def nonincreasing(values: list[float], tolerance: float = 1e-14) -> bool:
    return all(values[index + 1] <= values[index] + tolerance for index in range(len(values) - 1))


def compute_result(root: Path) -> dict[str, Any]:
    exact = summarize_code(exact_code_basis())
    repetition = summarize_code(repetition_basis())
    sweep = []
    for epsilon in EPSILON_SWEEP:
        metrics = summarize_code(deformed_basis(epsilon))
        sweep.append({"epsilon": epsilon, **metrics})

    checks = [
        {
            "check": "exact encoding is isometric",
            "passed": exact["isometry_residual_max"] <= TOLERANCE,
            "detail": f"residual={exact['isometry_residual_max']}",
        },
        {
            "check": "exact code satisfies every single-erasure Knill-Laflamme condition",
            "passed": exact["single_erasure_knill_laflamme_residual_max"] <= TOLERANCE,
            "detail": f"residual={exact['single_erasure_knill_laflamme_residual_max']}",
        },
        {
            "check": "exact decoder recovers all declared probes from every retained pair",
            "passed": exact["any_two_share_decoder_fidelity_min"] >= 1 - TOLERANCE,
            "detail": f"minimum_fidelity={exact['any_two_share_decoder_fidelity_min']}",
        },
        {
            "check": "rival dictionaries collide on every one-share record",
            "passed": exact["same_record_discriminator"]["one_share_record_distance_max"] <= TOLERANCE,
            "detail": f"maximum_distance={exact['same_record_discriminator']['one_share_record_distance_max']}",
        },
        {
            "check": "rival dictionaries separate after any-two-share decoding",
            "passed": exact["same_record_discriminator"]["any_two_share_logical_zero_witness_gap_min"] >= 0.65,
            "detail": f"minimum_gap={exact['same_record_discriminator']['any_two_share_logical_zero_witness_gap_min']}",
        },
        {
            "check": "declared rival global overlap remains one third",
            "passed": abs(exact["same_record_discriminator"]["global_state_overlap_squared"] - 1 / 3) <= TOLERANCE,
            "detail": f"overlap_squared={exact['same_record_discriminator']['global_state_overlap_squared']}",
        },
        {
            "check": "repetition-code control fails the quantum erasure condition",
            "passed": repetition["single_erasure_knill_laflamme_residual_max"] >= 0.6,
            "detail": f"residual={repetition['single_erasure_knill_laflamme_residual_max']}",
        },
        {
            "check": "repetition-code control leaks basis records to one share",
            "passed": repetition["one_share_basis_record_spread_max"] >= 1.4,
            "detail": f"spread={repetition['one_share_basis_record_spread_max']}",
        },
        {
            "check": "exact-code decoder rejects the repetition-code control",
            "passed": repetition["any_two_share_decoder_fidelity_min"] <= TOLERANCE,
            "detail": f"minimum_fidelity={repetition['any_two_share_decoder_fidelity_min']}",
        },
        {
            "check": "declared leakage monotonically worsens the erasure residual",
            "passed": nondecreasing([row["single_erasure_knill_laflamme_residual_max"] for row in sweep]),
            "detail": str([row["single_erasure_knill_laflamme_residual_max"] for row in sweep]),
        },
        {
            "check": "declared leakage monotonically lowers decoder fidelity",
            "passed": nonincreasing([row["any_two_share_decoder_fidelity_min"] for row in sweep]),
            "detail": str([row["any_two_share_decoder_fidelity_min"] for row in sweep]),
        },
        {
            "check": "declared leakage monotonically exposes the formerly hidden dictionary difference",
            "passed": nondecreasing(
                [row["same_record_discriminator"]["one_share_record_distance_max"] for row in sweep]
            ),
            "detail": str(
                [row["same_record_discriminator"]["one_share_record_distance_max"] for row in sweep]
            ),
        },
    ]
    failures = [f"{row['check']}: {row['detail']}" for row in checks if not row["passed"]]

    script_path = Path(__file__).resolve()
    return {
        "artifact_id": "FAMILYC-QUTRIT-RECONSTRUCTION-BENCHMARK",
        "revision": json.loads((root / "RELEASE-MANIFEST.json").read_text())["revision"],
        "route_id": ROUTE_ID,
        "decision_experiment_id": DECISION_ID,
        "epistemic_status": "owned finite-dimensional toy-model stress cell; route-local S3 pressure only",
        "scientific_question": "Can a declared code subspace hide logical distinctions from every one-share record while allowing exact recovery from any two shares, and do explicit controls expose when that statement fails?",
        "code_definition": {
            "logical_dimension": 3,
            "physical_shares": 3,
            "physical_share_dimension": 3,
            "basis_rule": "|e_i> = (1/sqrt(3)) sum_j |j, j+i mod 3, j+2i mod 3>",
            "decoder_rule": "for each retained pair, apply the exact support permutation that returns |logical>|missing_value>|missing_value>",
        },
        "exact_code_result": exact,
        "same_record_result": {
            "restricted_record": "one physical share",
            "richer_record": "any two physical shares followed by the declared exact decoder",
            **exact["same_record_discriminator"],
            "interpretation": "The restricted record cannot distinguish the two declared logical dictionaries, while the richer record can. This is a finite-dimensional QEC discriminator, not a bulk-locality or finite-N holography demonstration.",
        },
        "leakage_deformation": {
            "definition": "V_epsilon|i> = sqrt(1-epsilon^2)|e_i> + epsilon|w_i>, with orthonormal marker states |001>, |112>, |220> outside the exact code support",
            "physical_status": "declared diagnostic deformation only; not derived from 1/N, backreaction, an island saddle, or a boundary theory",
            "sweep": sweep,
        },
        "negative_control": {
            "name": "three-qutrit repetition encoding |i> -> |iii>",
            "purpose": "show that isometry alone does not imply quantum erasure correction or record hiding",
            "result": repetition,
        },
        "acceptance_checks": checks,
        "validation_failures": failures,
        "source_refs": SOURCE_REFS,
        "replay": {
            "command": "python3 tools/familyc_qutrit_reconstruction_benchmark.py --check",
            "runtime_dependencies": "Python standard library only",
            "numerical_tolerance": TOLERANCE,
            "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        },
        "authority_cap": "S3",
        "hard_limits": [
            "The benchmark is a 3-qutrit exact toy code, not a finite-N CFT or gravitational calculation.",
            "The leakage deformation is diagnostic and carries no physical 1/N or backreaction interpretation.",
            "Its max-entry Knill-Laflamme residual is a same-dimension diagnostic only; cross-size scaling must use the operational norm in FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json.",
            "No island choice, area operator, edge-mode quotient, local observer map, or non-AdS transport is implemented.",
            "Passing the cell does not create acquired evidence, public-record closure, observed-sector recovery, or Theory-of-Everything identity.",
        ],
        "next_kernel_step": "Use FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json as the exact cross-size norm baseline and FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json as the theorem-translation layer; next instantiate one same-domain full-system/subregion FLM and sector-transport tuple, prove weighted log-smoothness, and then test algebraic, state-dependent-wedge, and non-AdS observer transport.",
    }


def render_markdown(result: dict[str, Any]) -> str:
    exact = result["exact_code_result"]
    same = result["same_record_result"]
    repetition = result["negative_control"]["result"]
    lines = [
        "# Family-C three-qutrit reconstruction benchmark (generated)",
        "",
        "This is the first owned executable reconstruction stress cell for the strongest live Family-C route. It is deliberately small: exact finite-dimensional quantum error correction, not a finite-N holographic result.",
        "",
        f"- Route: `{result['route_id']}`",
        f"- Decision experiment: `{result['decision_experiment_id']}`",
        f"- Status: {result['epistemic_status']}",
        f"- Replay: `{result['replay']['command']}`",
        f"- Validation failures: `{len(result['validation_failures'])}`",
        "",
        "## Exact code result",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Isometry residual | `{exact['isometry_residual_max']}` |",
        f"| Single-erasure Knill-Laflamme residual | `{exact['single_erasure_knill_laflamme_residual_max']}` |",
        f"| One-share logical-basis record spread | `{exact['one_share_basis_record_spread_max']}` |",
        f"| One-share coherence leakage | `{exact['one_share_coherence_leakage_max']}` |",
        f"| Minimum any-two-share decoder fidelity | `{exact['any_two_share_decoder_fidelity_min']}` |",
        "",
        "## Same-restricted-record discriminator",
        "",
        "The named logical record `0` is assigned two rival dictionaries: encoded `|0>` versus encoded `(|0>+|1>+|2>)/sqrt(3)`. Every one-share reduced record collides, but the declared decoder on any retained pair separates them.",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Maximum one-share record distance | `{same['one_share_record_distance_max']}` |",
        f"| Minimum any-two-share logical-zero witness gap | `{same['any_two_share_logical_zero_witness_gap_min']}` |",
        f"| Global state overlap squared | `{same['global_state_overlap_squared']}` |",
        "",
        "This is a concrete demonstration of record-relative distinguishability. It is not evidence that a physical boundary dictionary, finite-N code subspace, or bulk observer map has been identified.",
        "",
        "## Declared leakage sweep",
        "",
        "The deformation mixes each exact codeword with an orthogonal marker. It is a diagnostic stress parameter, not a physical `1/N` expansion.",
        "",
        "| epsilon | KL residual | one-share record distance | decoder fidelity | pair witness gap |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in result["leakage_deformation"]["sweep"]:
        lines.append(
            "| `{epsilon}` | `{kl}` | `{distance}` | `{fidelity}` | `{gap}` |".format(
                epsilon=row["epsilon"],
                kl=row["single_erasure_knill_laflamme_residual_max"],
                distance=row["same_record_discriminator"]["one_share_record_distance_max"],
                fidelity=row["any_two_share_decoder_fidelity_min"],
                gap=row["same_record_discriminator"]["any_two_share_logical_zero_witness_gap_min"],
            )
        )
    lines += [
        "",
        "## Negative control",
        "",
        "The isometric repetition encoding `|i> -> |iii>` fails as a quantum erasure code:",
        "",
        f"- Knill-Laflamme residual: `{repetition['single_erasure_knill_laflamme_residual_max']}`",
        f"- One-share basis-record spread: `{repetition['one_share_basis_record_spread_max']}`",
        f"- Minimum fidelity under the exact-code decoder: `{repetition['any_two_share_decoder_fidelity_min']}`",
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
            print("FAMILYC QUTRIT RECONSTRUCTION BENCHMARK FAILED")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("FAMILYC QUTRIT RECONSTRUCTION BENCHMARK OK")
        return 0

    write_generated_texts(root, texts)
    if result["validation_failures"]:
        print("FAMILYC QUTRIT RECONSTRUCTION BENCHMARK WROTE FAILING RESULT")
        for failure in result["validation_failures"]:
            print(f"- {failure}")
        return 1
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
