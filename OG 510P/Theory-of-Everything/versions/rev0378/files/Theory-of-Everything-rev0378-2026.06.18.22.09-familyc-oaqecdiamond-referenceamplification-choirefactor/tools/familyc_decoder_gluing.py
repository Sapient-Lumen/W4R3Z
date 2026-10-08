#!/usr/bin/env python3
"""Fixed-region decoder gluing and target-algebra stress cells for Family C.

The exact operator-algebra question is narrower than full-Hilbert recovery.  A
large direct-sum code may reconstruct the block-diagonal algebra on one fixed
carrier while legitimately discarding off-diagonal sector coherence.  This
module makes that split executable, checks the erasure OAQEC commutant
criterion, and prices approximate sector confusion and hidden frame mismatch.
"""
from __future__ import annotations

import math
import sys
from typing import Any, Sequence

import numpy as np

sys.dont_write_bytecode = True

from benchmark_numeric import log_log_slope, stable_number
from familyc_operator_algebra import (
    block_diagonal,
    bloch_state,
    partial_trace,
    trace_norm_hermitian,
)

TOLERANCE = 1e-12


def rotation_y(angle: float) -> np.ndarray:
    """Return exp(-i angle sigma_y / 2) in a real convention."""
    half = 0.5 * float(angle)
    return np.array(
        [[math.cos(half), -math.sin(half)], [math.sin(half), math.cos(half)]],
        dtype=complex,
    )


def erasure_kraus_operators(
    encoding: Any,
    dimensions: Sequence[int],
    retained_subsystems: Sequence[int],
) -> list[np.ndarray]:
    """Kraus operators for encoding followed by erasure of the complement."""
    matrix = np.asarray(encoding, dtype=complex)
    dims = [int(value) for value in dimensions]
    retained = [int(index) for index in retained_subsystems]
    if math.prod(dims) != matrix.shape[0]:
        raise ValueError("encoding output dimension does not match subsystem dimensions")
    if len(set(retained)) != len(retained) or any(
        index < 0 or index >= len(dims) for index in retained
    ):
        raise ValueError("invalid retained subsystem list")
    erased = [index for index in range(len(dims)) if index not in retained]
    tensor = matrix.reshape(*(dims + [matrix.shape[1]]))
    tensor = np.transpose(tensor, retained + erased + [len(dims)])
    retained_dimension = math.prod(dims[index] for index in retained)
    erased_dimension = math.prod(dims[index] for index in erased)
    tensor = tensor.reshape(retained_dimension, erased_dimension, matrix.shape[1])
    return [tensor[:, index, :] for index in range(erased_dimension)]


def project_to_direct_sum_commutant(
    operator: Any,
    block_dimensions: Sequence[int],
) -> np.ndarray:
    """Orthogonally project onto ⊕_alpha C I_{d_alpha}."""
    matrix = np.asarray(operator, dtype=complex)
    blocks = [int(value) for value in block_dimensions]
    if matrix.shape[0] != matrix.shape[1] or sum(blocks) != matrix.shape[0]:
        raise ValueError("operator and direct-sum block dimensions do not match")
    projection = np.zeros_like(matrix)
    offset = 0
    for dimension in blocks:
        block_slice = slice(offset, offset + dimension)
        scalar = np.trace(matrix[block_slice, block_slice]) / dimension
        projection[block_slice, block_slice] = scalar * np.eye(dimension, dtype=complex)
        offset += dimension
    return projection


def oaqec_erasure_commutant_residual(
    encoding: Any,
    dimensions: Sequence[int],
    retained_subsystems: Sequence[int],
    block_dimensions: Sequence[int],
) -> dict[str, Any]:
    """Evaluate P E_i^† E_j P ∈ A' for A=⊕ B(C^{d_alpha})."""
    matrix = np.asarray(encoding, dtype=complex)
    kraus = erasure_kraus_operators(matrix, dimensions, retained_subsystems)
    completeness = sum((item.conj().T @ item for item in kraus), np.zeros((matrix.shape[1], matrix.shape[1]), dtype=complex))
    completeness_residual = float(np.linalg.norm(completeness - np.eye(matrix.shape[1]), ord=2))
    maximum_operator_residual = -1.0
    maximum_frobenius_residual = -1.0
    argmax = (0, 0)
    for left_index, left in enumerate(kraus):
        for right_index, right in enumerate(kraus):
            product = left.conj().T @ right
            residual = product - project_to_direct_sum_commutant(product, block_dimensions)
            operator_residual = float(np.linalg.norm(residual, ord=2))
            frobenius_residual = float(np.linalg.norm(residual, ord="fro"))
            if operator_residual > maximum_operator_residual:
                maximum_operator_residual = operator_residual
                maximum_frobenius_residual = frobenius_residual
                argmax = (left_index, right_index)
    return {
        "target_algebra": "direct sum of full matrix blocks with dimensions "
        + str([int(value) for value in block_dimensions]),
        "retained_subsystems": [int(index) for index in retained_subsystems],
        "erased_kraus_count": len(kraus),
        "kraus_completeness_operator_norm_residual": stable_number(completeness_residual),
        "maximum_commutant_operator_norm_residual": stable_number(maximum_operator_residual),
        "maximum_commutant_frobenius_residual": stable_number(maximum_frobenius_residual),
        "argmax_erasure_kraus_pair": [int(argmax[0]), int(argmax[1])],
        "exactly_correctable_at_tolerance": bool(
            completeness_residual < TOLERANCE and maximum_operator_residual < TOLERANCE
        ),
    }


def _controlled_frame_encoding(frame_separation_radians: float) -> tuple[np.ndarray, list[np.ndarray]]:
    """Encode sector tag and logical qubit into one fixed carrier plus fixed junk."""
    frames = [
        rotation_y(-0.5 * frame_separation_radians),
        rotation_y(0.5 * frame_separation_radians),
    ]
    encoding = np.zeros((8, 4), dtype=complex)  # tag x carrier x fixed environment

    def physical_index(tag: int, carrier: int, environment: int) -> int:
        return tag * 4 + carrier * 2 + environment

    for sector, frame in enumerate(frames):
        for logical in range(2):
            for carrier in range(2):
                encoding[physical_index(sector, carrier, 0), 2 * sector + logical] = frame[
                    carrier, logical
                ]
    return encoding, frames


def _dephase_direct_sum(state: Any, block_dimensions: Sequence[int]) -> np.ndarray:
    matrix = np.asarray(state, dtype=complex)
    blocks: list[np.ndarray] = []
    offset = 0
    for dimension in block_dimensions:
        blocks.append(matrix[offset : offset + dimension, offset : offset + dimension])
        offset += dimension
    return block_diagonal(blocks)


def fixed_region_common_decoder_probe() -> dict[str, Any]:
    """Construct one exact fixed-region decoder and quantify its target split."""
    frame_separation = 1.1
    encoding, frames = _controlled_frame_encoding(frame_separation)
    isometry_residual = float(
        np.linalg.norm(encoding.conj().T @ encoding - np.eye(4), ord=2)
    )
    retained_region = partial_trace(
        encoding @ np.eye(4, dtype=complex) @ encoding.conj().T / 4.0,
        [2, 2, 2],
        [0, 1],
    )
    retained_trace_residual = abs(float(np.trace(retained_region).real) - 1.0)
    coherent_decoder_unitary = block_diagonal([frame.conj().T for frame in frames])

    block_state = block_diagonal(
        [
            0.35 * bloch_state((0.24, -0.18, 0.31)),
            0.65 * bloch_state((-0.11, 0.29, -0.21)),
        ]
    )
    coherent_vector = np.array([0.5, 0.25j, -0.4, math.sqrt(0.5875)], dtype=complex)
    coherent_vector /= np.linalg.norm(coherent_vector)
    coherent_state = np.outer(coherent_vector, coherent_vector.conj())
    sector_plus_vector = np.array([1.0, 0.0, 1.0, 0.0], dtype=complex) / math.sqrt(2.0)
    sector_plus_state = np.outer(sector_plus_vector, sector_plus_vector.conj())
    test_states = [block_state, coherent_state, sector_plus_state]

    maximum_coherent_decoder_error = 0.0
    maximum_algebra_expectation_residual = 0.0
    algebra_basis: list[np.ndarray] = []
    paulis = [
        np.eye(2, dtype=complex),
        np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex),
        np.array([[0.0, -1j], [1j, 0.0]], dtype=complex),
        np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex),
    ]
    zero = np.zeros((2, 2), dtype=complex)
    for pauli in paulis:
        algebra_basis.append(block_diagonal([pauli, zero]))
        algebra_basis.append(block_diagonal([zero, pauli]))

    decoded_by_state: list[tuple[np.ndarray, np.ndarray]] = []
    for code_state in test_states:
        physical_state = encoding @ code_state @ encoding.conj().T
        region_state = partial_trace(physical_state, [2, 2, 2], [0, 1])
        coherent_decoded = (
            coherent_decoder_unitary @ region_state @ coherent_decoder_unitary.conj().T
        )
        algebra_decoded = _dephase_direct_sum(coherent_decoded, [2, 2])
        decoded_by_state.append((coherent_decoded, algebra_decoded))
        maximum_coherent_decoder_error = max(
            maximum_coherent_decoder_error,
            trace_norm_hermitian(coherent_decoded - code_state),
        )
        for observable in algebra_basis:
            expected = np.trace(observable @ code_state)
            observed = np.trace(observable @ algebra_decoded)
            maximum_algebra_expectation_residual = max(
                maximum_algebra_expectation_residual, abs(expected - observed)
            )

    block_algebraic_error = trace_norm_hermitian(decoded_by_state[0][1] - block_state)
    coherent_algebraic_state_error = trace_norm_hermitian(
        decoded_by_state[2][1] - sector_plus_state
    )

    direct_sum_oaqec = oaqec_erasure_commutant_residual(
        encoding, [2, 2, 2], [0, 1], [2, 2]
    )
    full_subspace_oaqec = oaqec_erasure_commutant_residual(
        encoding, [2, 2, 2], [0, 1], [4]
    )

    confusion_rows: list[dict[str, Any]] = []
    sector_swap = np.block(
        [
            [np.zeros((2, 2), dtype=complex), np.eye(2, dtype=complex)],
            [np.eye(2, dtype=complex), np.zeros((2, 2), dtype=complex)],
        ]
    )
    deterministic_sector_state = block_diagonal(
        [np.diag([1.0, 0.0]).astype(complex), np.zeros((2, 2), dtype=complex)]
    )
    center_sign = block_diagonal(
        [np.eye(2, dtype=complex), -np.eye(2, dtype=complex)]
    )
    for confusion in [0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.001]:
        confused = (
            (1.0 - confusion) * deterministic_sector_state
            + confusion * sector_swap @ deterministic_sector_state @ sector_swap.conj().T
        )
        trace_error = trace_norm_hermitian(confused - deterministic_sector_state)
        center_error = abs(
            np.trace(center_sign @ confused)
            - np.trace(center_sign @ deterministic_sector_state)
        )
        confusion_rows.append(
            {
                "worst_sector_misrouting_probability": confusion,
                "deterministic_sector_trace_norm_error": stable_number(trace_error),
                "center_observable_expectation_error": stable_number(center_error),
                "gluing_bound_epsilon_local_plus_disturbance_plus_2p": stable_number(
                    2.0 * confusion
                ),
            }
        )
    confusion_slope = log_log_slope(
        confusion_rows,
        "worst_sector_misrouting_probability",
        "deterministic_sector_trace_norm_error",
    )

    frame_rows: list[dict[str, Any]] = []
    basis_zero = np.array([1.0, 0.0], dtype=complex)
    basis_zero_state = np.outer(basis_zero, basis_zero.conj())
    for separation in [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]:
        left_frame = rotation_y(-0.5 * separation)
        right_frame = rotation_y(0.5 * separation)
        common_output_vector = left_frame @ basis_zero
        hidden_partner_vector = right_frame.conj().T @ common_output_vector
        hidden_partner_state = np.outer(hidden_partner_vector, hidden_partner_vector.conj())
        output_residual = trace_norm_hermitian(
            np.outer(common_output_vector, common_output_vector.conj())
            - right_frame @ hidden_partner_state @ right_frame.conj().T
        )
        indistinguishable_input_distance = trace_norm_hermitian(
            basis_zero_state - hidden_partner_state
        )
        minimax_lower = 0.5 * indistinguishable_input_distance
        midpoint_error = trace_norm_hermitian(
            left_frame @ basis_zero_state @ left_frame.conj().T - basis_zero_state
        )
        frame_rows.append(
            {
                "sector_frame_separation_radians": separation,
                "physical_output_identity_residual": stable_number(output_residual),
                "indistinguishable_input_logical_trace_norm_distance": stable_number(
                    indistinguishable_input_distance
                ),
                "any_common_decoder_minimax_trace_norm_lower_bound": stable_number(
                    minimax_lower
                ),
                "midpoint_unitary_decoder_worst_case_upper_bound": stable_number(
                    midpoint_error
                ),
                "sector_conditioned_decoder_error": 0.0,
            }
        )
    frame_slopes = {
        "minimax_lower_bound_vs_frame_separation": stable_number(
            log_log_slope(
                frame_rows,
                "sector_frame_separation_radians",
                "any_common_decoder_minimax_trace_norm_lower_bound",
            )
        ),
        "midpoint_upper_bound_vs_frame_separation": stable_number(
            log_log_slope(
                frame_rows,
                "sector_frame_separation_radians",
                "midpoint_unitary_decoder_worst_case_upper_bound",
            )
        ),
    }

    return {
        "model": "Two direct-sum logical sectors share one fixed boundary carrier. An orthogonal sector tag and sector-conditioned logical frames are both contained in that carrier; a fixed environment is discarded.",
        "frame_separation_radians": frame_separation,
        "encoding_isometry_operator_norm_residual": stable_number(isometry_residual),
        "retained_region_trace_residual": stable_number(retained_trace_residual),
        "oaqec_erasure_commutant_checks": {
            "direct_sum_algebra": direct_sum_oaqec,
            "full_subspace_algebra": full_subspace_oaqec,
        },
        "single_fixed_region_decoders": {
            "region": "tag-plus-logical carrier R; no sector-dependent region switch",
            "coherent_decoder": "one controlled inverse unitary on R",
            "maximum_full_state_trace_norm_error": stable_number(
                maximum_coherent_decoder_error
            ),
            "algebraic_decoder": "the same controlled inverse followed by sector dephasing",
            "block_diagonal_state_trace_norm_error": stable_number(block_algebraic_error),
            "maximum_direct_sum_algebra_expectation_residual": stable_number(
                maximum_algebra_expectation_residual
            ),
            "cross_sector_coherent_state_trace_norm_error_after_algebraic_decoder": stable_number(
                coherent_algebraic_state_error
            ),
            "target_interpretation": "The dephasing decoder is exact for the direct-sum operator algebra even though it is not full-Hilbert recovery. The coherent controlled decoder shows that full coherence is also recoverable when the sector tag itself is coherently available on the same carrier.",
        },
        "approximate_sector_instrument": {
            "generic_trace_norm_bound": "epsilon_common <= epsilon_local + mu_nondemolition + 2 p_max for block-diagonal target states",
            "owned_cell_parameters": "epsilon_local=0 and mu_nondemolition=0; a symmetric sector-bit confusion channel saturates 2 p_max on a deterministic sector state and its center-sign observable",
            "rows": confusion_rows,
            "fitted_log_log_slope": stable_number(confusion_slope),
        },
        "hidden_sector_frame_negative_control": {
            "model": "The sector label is discarded while the same logical qubit is emitted in two unitary frames separated by theta. Sector-conditioned decoders are exact, but two distinct logical inputs can produce the identical carrier record.",
            "rows": frame_rows,
            "fitted_log_log_slopes": frame_slopes,
            "proof": "For the identical-output pair, the triangle inequality forces any one decoder to incur at least half their input trace-norm distance. A midpoint unitary gives the reported constructive upper bound; both bounds are linear for small frame separation.",
        },
        "correction": "A direct-sum algebra target must not be failed merely because a valid algebra decoder removes off-diagonal sector coherence. The actual gluing debts are a fixed carrier, one CPTP instrument, uniform sector-local decoder errors, nondemolition sector routing, and a worst-sector—not average—confusion bound. Full-Hilbert coherence is a separate stronger target.",
    }


def state_dependent_wedge_probe() -> dict[str, Any]:
    """Generic comparator where different sectors genuinely require different regions."""
    logical_dimension = 4  # sector qubit x logical qubit
    physical_dimension = 8  # A x B x C
    encoding = np.zeros((physical_dimension, logical_dimension), dtype=complex)

    def physical_index(a: int, b: int, c: int) -> int:
        return a * 4 + b * 2 + c

    encoding[physical_index(0, 0, 0), 0] = 1.0
    encoding[physical_index(1, 0, 0), 1] = 1.0
    encoding[physical_index(0, 0, 1), 2] = 1.0
    encoding[physical_index(0, 1, 1), 3] = 1.0
    isometry_residual = float(
        np.linalg.norm(encoding.conj().T @ encoding - np.eye(logical_dimension), ord=2)
    )

    logical_test_vectors = [
        np.array([math.sqrt(0.30), math.sqrt(0.70)], dtype=complex),
        np.array([1.0, 1j], dtype=complex) / math.sqrt(2.0),
        np.array([math.sqrt(0.60), -math.sqrt(0.40)], dtype=complex),
    ]
    maximum_sector_local_error = 0.0
    for vector in logical_test_vectors:
        logical_state = np.outer(vector, vector.conj())
        sector_zero = np.zeros((logical_dimension, logical_dimension), dtype=complex)
        sector_zero[:2, :2] = logical_state
        encoded_zero = encoding @ sector_zero @ encoding.conj().T
        region_ac = partial_trace(encoded_zero, [2, 2, 2], [0, 2])
        decoded_zero = partial_trace(region_ac, [2, 2], [0])
        maximum_sector_local_error = max(
            maximum_sector_local_error,
            trace_norm_hermitian(decoded_zero - logical_state),
        )

        sector_one = np.zeros((logical_dimension, logical_dimension), dtype=complex)
        sector_one[2:, 2:] = logical_state
        encoded_one = encoding @ sector_one @ encoding.conj().T
        region_bc = partial_trace(encoded_one, [2, 2, 2], [1, 2])
        decoded_one = partial_trace(region_bc, [2, 2], [0])
        maximum_sector_local_error = max(
            maximum_sector_local_error,
            trace_norm_hermitian(decoded_one - logical_state),
        )

    basis_states = []
    for index in range(logical_dimension):
        vector = np.zeros(logical_dimension, dtype=complex)
        vector[index] = 1.0
        logical_state = np.outer(vector, vector.conj())
        physical_state = encoding @ logical_state @ encoding.conj().T
        basis_states.append(
            {
                "AC": partial_trace(physical_state, [2, 2, 2], [0, 2]),
                "BC": partial_trace(physical_state, [2, 2, 2], [1, 2]),
            }
        )
    ac_erased_pair_output_distance = trace_norm_hermitian(
        basis_states[2]["AC"] - basis_states[3]["AC"]
    )
    bc_erased_pair_output_distance = trace_norm_hermitian(
        basis_states[0]["BC"] - basis_states[1]["BC"]
    )
    constant_half_state = 0.5 * np.eye(2, dtype=complex)
    constant_decoder_pair_error = max(
        trace_norm_hermitian(
            constant_half_state - np.diag([1.0, 0.0]).astype(complex)
        ),
        trace_norm_hermitian(
            constant_half_state - np.diag([0.0, 1.0]).astype(complex)
        ),
    )

    coherent_vector = np.array([1.0, 0.0, 1.0, 0.0], dtype=complex) / math.sqrt(2.0)
    coherent_state = np.outer(coherent_vector, coherent_vector.conj())
    sector_dephased = _dephase_direct_sum(coherent_state, [2, 2])
    adaptive_coherence_error = trace_norm_hermitian(coherent_state - sector_dephased)
    block_diagonal_state = block_diagonal(
        [
            0.4 * bloch_state((0.20, 0.10, 0.30)),
            0.6 * bloch_state((-0.10, 0.25, -0.20)),
        ]
    )
    block_diagonal_dephasing_error = trace_norm_hermitian(
        block_diagonal_state - _dephase_direct_sum(block_diagonal_state, [2, 2])
    )

    general_vector = np.array([0.30, 0.40j, -0.50, math.sqrt(0.50)], dtype=complex)
    general_vector /= np.linalg.norm(general_vector)
    general_state = np.outer(general_vector, general_vector.conj())
    encoded_general = encoding @ general_state @ encoding.conj().T
    decoded_general = encoding.conj().T @ encoded_general @ encoding
    union_decoder_error = trace_norm_hermitian(decoded_general - general_state)

    commutant_checks = {
        "AC_direct_sum_algebra": oaqec_erasure_commutant_residual(
            encoding, [2, 2, 2], [0, 2], [2, 2]
        ),
        "BC_direct_sum_algebra": oaqec_erasure_commutant_residual(
            encoding, [2, 2, 2], [1, 2], [2, 2]
        ),
        "ABC_direct_sum_algebra": oaqec_erasure_commutant_residual(
            encoding, [2, 2, 2], [0, 1, 2], [2, 2]
        ),
    }

    return {
        "model": "Generic two-sector comparator: sector 0 stores the logical qubit in A and sector 1 stores it in B; C is an orthogonal sector flag.",
        "source_scope_boundary": "This is not the geometry assumed by REF-0735 Definition 6, which fixes the same boundary-region pair for every small-code sector. It remains a negative control for later state-dependent-wedge extrapolations.",
        "encoding_isometry_operator_norm_residual": stable_number(isometry_residual),
        "sector_local_reconstruction": {
            "region_for_sector_0": "AC",
            "region_for_sector_1": "BC",
            "declared_nontrivial_logical_state_count": len(logical_test_vectors),
            "maximum_sector_local_trace_norm_error": stable_number(
                maximum_sector_local_error
            ),
        },
        "oaqec_erasure_commutant_checks": commutant_checks,
        "no_single_fixed_region_negative_control": {
            "AC_output_distance_for_sector_1_orthogonal_logical_pair": stable_number(
                ac_erased_pair_output_distance
            ),
            "BC_output_distance_for_sector_0_orthogonal_logical_pair": stable_number(
                bc_erased_pair_output_distance
            ),
            "input_logical_pair_trace_distance": 2.0,
            "exact_pair_minimax_recovery_trace_error_lower_bound": 1.0,
            "constant_maximally_mixed_decoder_attains_pair_error": stable_number(
                constant_decoder_pair_error
            ),
            "proof": "Each fixed region maps one orthogonal logical pair to the same record. The OAQEC commutant residual is also one on AC and BC, while it vanishes on ABC.",
        },
        "adaptive_region_choice_target_split": {
            "block_diagonal_operator_algebra_error": stable_number(
                block_diagonal_dephasing_error
            ),
            "cross_sector_coherent_state_trace_norm_error": stable_number(
                adaptive_coherence_error
            ),
            "interpretation": "External sector-dependent routing recovers the direct-sum blocks but is not one fixed-subregion channel. Its coherence loss matters only if full-Hilbert recovery, rather than the direct-sum algebra, is the declared target.",
        },
        "fixed_union_region_positive_control": {
            "region": "ABC",
            "arbitrary_coherent_code_state_trace_norm_error": stable_number(
                union_decoder_error
            ),
        },
        "correction": "Keep this comparator quarantined from source-specific debts. For a fixed-region direct-sum construction, apply the OAQEC commutant criterion and an explicit common decoder before charging cross-sector coherence as a missing observable.",
    }
