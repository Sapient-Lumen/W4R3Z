#!/usr/bin/env python3
"""Finite-dimensional operator-algebra and wedge-compatibility probes.

This route-local helper owns quantum-matrix mechanics used by the Family-C
recovery benchmark.  It separates the commutative center of a direct-sum
algebra from its noncommuting factor blocks, and it makes state-dependent
reconstruction-region failure executable.  It contains no release policy and
claims no physical CFT scaling law.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

from benchmark_numeric import log_log_slope, stable_number
from familyc_state_domain import (
    relative_floor_mass_geometry,
    spectral_floor_domain_geometry,
)


def hermitian(matrix: Any) -> np.ndarray:
    array = np.asarray(matrix, dtype=complex)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError("matrix must be square")
    return 0.5 * (array + array.conj().T)


def matrix_sqrt_psd(matrix: Any, *, tolerance: float = 1e-13) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    if float(values.min()) < -tolerance:
        raise ValueError("matrix is not positive semidefinite")
    return vectors @ np.diag(np.sqrt(np.clip(values, 0.0, None))) @ vectors.conj().T


def matrix_log_positive(matrix: Any) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    if float(values.min()) <= 0.0:
        raise ValueError("matrix logarithm requires a positive-definite matrix")
    return vectors @ np.diag(np.log(values)) @ vectors.conj().T


def quantum_relative_entropy_nats(state: Any, reference: Any) -> float:
    left = hermitian(state)
    right = hermitian(reference)
    if left.shape != right.shape:
        raise ValueError("state and reference must have the same shape")
    value = np.trace(left @ (matrix_log_positive(left) - matrix_log_positive(right)))
    return float(np.real_if_close(value).real)


def trace_norm(matrix: Any) -> float:
    array = np.asarray(matrix, dtype=complex)
    if array.ndim != 2:
        raise ValueError("trace norm requires a matrix")
    return float(np.sum(np.linalg.svd(array, compute_uv=False)))


def trace_norm_hermitian(matrix: Any) -> float:
    return float(np.sum(np.abs(np.linalg.eigvalsh(hermitian(matrix)))))


def unnormalized_maximally_entangled_vector(dimension: int) -> np.ndarray:
    """Return sum_i |i,i> in output-input tensor ordering."""
    dimension = int(dimension)
    if dimension < 1:
        raise ValueError("dimension must be positive")
    vector = np.zeros(dimension * dimension, dtype=complex)
    for index in range(dimension):
        vector[index * dimension + index] = 1.0
    return vector


def swap_operator(dimension: int) -> np.ndarray:
    """Return the swap F|i,j>=|j,i> on C^d tensor C^d."""
    dimension = int(dimension)
    if dimension < 1:
        raise ValueError("dimension must be positive")
    output = np.zeros((dimension * dimension, dimension * dimension), dtype=complex)
    for left in range(dimension):
        for right in range(dimension):
            output[left * dimension + right, right * dimension + left] = 1.0
    return output


def diagonal_correlation_projector(dimension: int) -> np.ndarray:
    """Return sum_i |i,i><i,i| in output-input tensor ordering."""
    vector_indices = [index * dimension + index for index in range(int(dimension))]
    output = np.zeros((dimension * dimension, dimension * dimension), dtype=complex)
    output[vector_indices, vector_indices] = 1.0
    return output


def centered_operator_oscillation(matrix: Any) -> float:
    values = np.linalg.eigvalsh(hermitian(matrix))
    return 0.5 * float(values.max() - values.min())


def block_diagonal(blocks: Sequence[Any]) -> np.ndarray:
    arrays = [np.asarray(block, dtype=complex) for block in blocks]
    if not arrays:
        raise ValueError("at least one block is required")
    if any(block.ndim != 2 or block.shape[0] != block.shape[1] for block in arrays):
        raise ValueError("every block must be square")
    dimension = sum(block.shape[0] for block in arrays)
    output = np.zeros((dimension, dimension), dtype=complex)
    offset = 0
    for block in arrays:
        size = block.shape[0]
        output[offset : offset + size, offset : offset + size] = block
        offset += size
    return output


def bloch_state(vector: Sequence[float]) -> np.ndarray:
    if len(vector) != 3:
        raise ValueError("Bloch vector must have three components")
    x, y, z = (float(value) for value in vector)
    if x * x + y * y + z * z >= 1.0:
        raise ValueError("Bloch state must be full rank")
    sigma_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    sigma_y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
    sigma_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    return hermitian(
        0.5
        * (
            np.eye(2, dtype=complex)
            + x * sigma_x
            + y * sigma_y
            + z * sigma_z
        )
    )


def _classical_relative_entropy(weights: Sequence[float], reference: Sequence[float]) -> float:
    if len(weights) != len(reference) or not weights:
        raise ValueError("weight vectors must have the same nonzero length")
    return sum(
        float(left) * math.log(float(left) / float(right))
        for left, right in zip(weights, reference)
    )


def direct_sum_operator_algebra_probe() -> dict[str, Any]:
    """Audit center/factor separation for A=direct_sum_alpha M_2.

    Block-diagonal relative entropy decomposes into a classical center term and
    a weighted sum of within-sector quantum relative entropies.  The exact
    state-domain diameter and centered modular oscillation therefore acquire a
    factor-block contribution that a center-only audit cannot see.
    """
    reference_weights = [0.55, 0.30, 0.15]
    state_weights = [0.20, 0.50, 0.30]
    reference_blocks = [
        bloch_state((0.00, 0.00, 0.55)),
        bloch_state((0.35, -0.15, 0.20)),
        bloch_state((-0.25, 0.30, -0.10)),
    ]
    state_blocks = [
        bloch_state((0.30, 0.20, 0.10)),
        bloch_state((-0.15, 0.45, 0.05)),
        bloch_state((0.20, -0.25, 0.35)),
    ]
    reference = block_diagonal(
        [weight * block for weight, block in zip(reference_weights, reference_blocks)]
    )
    state = block_diagonal(
        [weight * block for weight, block in zip(state_weights, state_blocks)]
    )
    full_relative_entropy = quantum_relative_entropy_nats(state, reference)
    center_relative_entropy = _classical_relative_entropy(
        state_weights, reference_weights
    )
    factor_relative_entropy = sum(
        weight * quantum_relative_entropy_nats(left, right)
        for weight, left, right in zip(
            state_weights, state_blocks, reference_blocks
        )
    )
    commutator_norms = [
        trace_norm(left @ right - right @ left)
        for left, right in zip(state_blocks, reference_blocks)
    ]
    reference_modular = -matrix_log_positive(reference)
    reconstructed_reference_modular = block_diagonal(
        [
            -math.log(weight) * np.eye(2, dtype=complex)
            - matrix_log_positive(block)
            for weight, block in zip(reference_weights, reference_blocks)
        ]
    )

    sector_count = 4
    total_center_floor_mass = 0.20
    factor_eigenvalue_floor = 0.05
    center_geometry = relative_floor_mass_geometry(
        log_dimension=math.log(sector_count),
        total_floor_mass=total_center_floor_mass,
    )
    factor_geometry = spectral_floor_domain_geometry(
        dimension=2,
        eigenvalue_floor=factor_eigenvalue_floor,
    )
    center_floor = total_center_floor_mass / sector_count
    center_maximum = 1.0 - total_center_floor_mass + center_floor
    state_center = [center_maximum, center_floor, center_floor, center_floor]
    reference_center = [center_floor, center_maximum, center_floor, center_floor]
    factor_maximum = 1.0 - factor_eigenvalue_floor
    state_factor = np.diag([factor_maximum, factor_eigenvalue_floor]).astype(complex)
    reference_factor = np.diag([factor_eigenvalue_floor, factor_maximum]).astype(complex)
    extremal_state = block_diagonal(
        [weight * state_factor for weight in state_center]
    )
    extremal_reference = block_diagonal(
        [weight * reference_factor for weight in reference_center]
    )
    observed_full_diameter = quantum_relative_entropy_nats(
        extremal_state, extremal_reference
    )
    modular_difference = (
        matrix_log_positive(extremal_state)
        - matrix_log_positive(extremal_reference)
    )
    observed_full_oscillation = centered_operator_oscillation(modular_difference)
    predicted_full_diameter = (
        float(center_geometry["exact_relative_entropy_diameter_nats"])
        + float(factor_geometry["exact_relative_entropy_diameter_nats"])
    )
    predicted_full_oscillation = (
        float(center_geometry["exact_centered_modular_oscillation_nats"])
        + float(factor_geometry["exact_centered_modular_oscillation_nats"])
    )

    return {
        "algebra": "A = direct_sum_{alpha=1}^K M_2; its center is the commutative algebra generated by sector projectors, while each M_2 factor is noncommutative.",
        "terminology_correction": "A center is commutative by definition. The unpaid quantum debt is noncommuting factor-block and edge-mode transport, not a 'noncommuting center'.",
        "noncommuting_block_decomposition_probe": {
            "sector_count": len(state_weights),
            "full_relative_entropy_nats": stable_number(full_relative_entropy),
            "classical_center_relative_entropy_nats": stable_number(
                center_relative_entropy
            ),
            "weighted_factor_relative_entropy_nats": stable_number(
                factor_relative_entropy
            ),
            "decomposition_residual": stable_number(
                abs(
                    full_relative_entropy
                    - center_relative_entropy
                    - factor_relative_entropy
                )
            ),
            "factor_commutator_trace_norms": [
                stable_number(value) for value in commutator_norms
            ],
            "modular_block_decomposition_operator_norm_residual": stable_number(
                float(
                    np.linalg.norm(
                        reference_modular - reconstructed_reference_modular,
                        ord=2,
                    )
                )
            ),
            "identity": "D(direct_sum q_alpha sigma_alpha || direct_sum p_alpha rho_alpha) = D(q||p) + sum_alpha q_alpha D(sigma_alpha||rho_alpha).",
        },
        "exact_product_domain_geometry": {
            "sector_count": sector_count,
            "total_center_floor_mass": total_center_floor_mass,
            "factor_dimension": 2,
            "factor_eigenvalue_floor": factor_eigenvalue_floor,
            "center_relative_entropy_diameter_nats": stable_number(
                float(center_geometry["exact_relative_entropy_diameter_nats"])
            ),
            "factor_relative_entropy_diameter_nats": stable_number(
                float(factor_geometry["exact_relative_entropy_diameter_nats"])
            ),
            "predicted_full_relative_entropy_diameter_nats": stable_number(
                predicted_full_diameter
            ),
            "observed_full_relative_entropy_diameter_nats": stable_number(
                observed_full_diameter
            ),
            "diameter_identity_residual": stable_number(
                abs(observed_full_diameter - predicted_full_diameter)
            ),
            "center_centered_modular_oscillation_nats": stable_number(
                float(center_geometry["exact_centered_modular_oscillation_nats"])
            ),
            "factor_centered_modular_oscillation_nats": stable_number(
                float(factor_geometry["exact_centered_modular_oscillation_nats"])
            ),
            "predicted_full_centered_modular_oscillation_nats": stable_number(
                predicted_full_oscillation
            ),
            "observed_full_centered_modular_oscillation_nats": stable_number(
                observed_full_oscillation
            ),
            "oscillation_identity_residual": stable_number(
                abs(observed_full_oscillation - predicted_full_oscillation)
            ),
            "center_only_diameter_fraction": stable_number(
                float(center_geometry["exact_relative_entropy_diameter_nats"])
                / predicted_full_diameter
            ),
            "center_only_oscillation_fraction": stable_number(
                float(center_geometry["exact_centered_modular_oscillation_nats"])
                / predicted_full_oscillation
            ),
            "exact_rule": "For the independent center-floor x factor-floor domain used here, D_max(full algebra)=D_max(center)+D_max(factor), and L_K^osc(full algebra)=L_K^osc(center)+L_K^osc(factor).",
        },
        "correction": "A p-stationary sector kernel can remove the commutative center tax while leaving the within-sector noncommuting modular contribution untouched. The recovery budget must price both on the identical reconstructed algebra.",
    }


def noncommuting_modular_rotation_schedule() -> dict[str, Any]:
    """Expose logarithmic amplification inside one noncommuting factor block.

    Let rho_G=diag(1-lambda_G,lambda_G), lambda_G=exp(-1/G), and rotate its
    eigenbasis by theta_G.  The state trace distance is O(theta_G), while the
    operator-log difference is log((1-lambda)/lambda)|sin theta_G|.  Choosing
    theta_G=G makes the state perturbation vanish but leaves an O(1) modular
    error.  theta_G=G^2 is a constructive sufficient repair in this cell.
    """
    resources = [
        1.0 / value
        for value in (8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256)
    ]
    rows: list[dict[str, Any]] = []
    maximum_matrix_formula_residual = 0.0
    for index, resource in enumerate(resources):
        eigenvalue_floor = math.exp(-1.0 / resource)
        state_gap = 1.0 - 2.0 * eigenvalue_floor
        log_condition_number = (
            math.log1p(-eigenvalue_floor) - math.log(eigenvalue_floor)
        )
        adversarial_angle = resource
        repaired_angle = resource * resource

        def quantities(angle: float) -> tuple[float, float]:
            sine = abs(math.sin(angle))
            return (
                2.0 * state_gap * sine,
                log_condition_number * sine,
            )

        adversarial_trace, adversarial_log = quantities(adversarial_angle)
        repaired_trace, repaired_log = quantities(repaired_angle)

        if index < 5:
            state = np.diag(
                [1.0 - eigenvalue_floor, eigenvalue_floor]
            ).astype(complex)
            rotation = np.array(
                [
                    [math.cos(adversarial_angle), -math.sin(adversarial_angle)],
                    [math.sin(adversarial_angle), math.cos(adversarial_angle)],
                ],
                dtype=complex,
            )
            rotated = hermitian(rotation @ state @ rotation.conj().T)
            matrix_trace = trace_norm_hermitian(rotated - state)
            matrix_log = float(
                np.linalg.norm(
                    matrix_log_positive(rotated) - matrix_log_positive(state),
                    ord=2,
                )
            )
            maximum_matrix_formula_residual = max(
                maximum_matrix_formula_residual,
                abs(matrix_trace - adversarial_trace),
                abs(matrix_log - adversarial_log),
            )

        rows.append(
            {
                "G": stable_number(resource),
                "eigenvalue_floor_exp_minus_1_over_G": stable_number(
                    eigenvalue_floor
                ),
                "log_condition_number_nats": stable_number(log_condition_number),
                "adversarial_theta_equals_G": {
                    "rotation_angle": stable_number(adversarial_angle),
                    "state_trace_norm_perturbation": stable_number(
                        adversarial_trace
                    ),
                    "operator_log_difference_norm_nats": stable_number(
                        adversarial_log
                    ),
                },
                "repaired_theta_equals_G_squared": {
                    "rotation_angle": stable_number(repaired_angle),
                    "state_trace_norm_perturbation": stable_number(repaired_trace),
                    "operator_log_difference_norm_nats": stable_number(
                        repaired_log
                    ),
                },
            }
        )

    def flattened(key: str, nested: str) -> list[dict[str, float]]:
        return [
            {
                "G": float(row["G"]),
                "value": float(row[key][nested]),
            }
            for row in rows[-6:]
        ]

    slopes = {
        "adversarial_state_trace_vs_G": stable_number(
            log_log_slope(
                flattened(
                    "adversarial_theta_equals_G",
                    "state_trace_norm_perturbation",
                ),
                "G",
                "value",
            )
        ),
        "adversarial_operator_log_vs_G": stable_number(
            log_log_slope(
                flattened(
                    "adversarial_theta_equals_G",
                    "operator_log_difference_norm_nats",
                ),
                "G",
                "value",
            )
        ),
        "repaired_state_trace_vs_G": stable_number(
            log_log_slope(
                flattened(
                    "repaired_theta_equals_G_squared",
                    "state_trace_norm_perturbation",
                ),
                "G",
                "value",
            )
        ),
        "repaired_operator_log_vs_G": stable_number(
            log_log_slope(
                flattened(
                    "repaired_theta_equals_G_squared",
                    "operator_log_difference_norm_nats",
                ),
                "G",
                "value",
            )
        ),
    }
    return {
        "model": "One full-rank qubit factor with eigenvalue floor lambda(G)=exp(-1/G); the state is conjugated by a real basis rotation.",
        "exact_formulas": {
            "state_trace_norm": "2(1-2 lambda)|sin theta|",
            "operator_log_norm": "log((1-lambda)/lambda)|sin theta|",
            "required_noncommuting_modular_frame_condition": "|sin theta(G)| log((1-lambda(G))/lambda(G)) -> 0",
        },
        "rows": rows,
        "fitted_last_six_log_log_slopes": slopes,
        "maximum_matrix_formula_residual_on_moderate_floor_rows": stable_number(
            maximum_matrix_formula_residual
        ),
        "severe_failure": "With theta=G and lambda=exp(-1/G), the trace-norm state perturbation vanishes linearly while the operator-log error tends to one nat. Exact sector-weight stationarity does not touch this within-factor failure.",
        "constructive_control": "In the declared theta=G^2 schedule, the operator-log error falls as G. More generally, a same-domain proof needs a modular-frame/eigenbasis transport bound weighted by the within-sector log condition number, not only sector inflow or trace leakage.",
    }


def partial_trace(state: Any, dimensions: Sequence[int], keep: Sequence[int]) -> np.ndarray:
    matrix = np.asarray(state, dtype=complex)
    dims = [int(value) for value in dimensions]
    kept = sorted(int(index) for index in keep)
    if any(value < 1 for value in dims):
        raise ValueError("all subsystem dimensions must be positive")
    total = math.prod(dims)
    if matrix.shape != (total, total):
        raise ValueError("matrix shape does not match subsystem dimensions")
    if len(set(kept)) != len(kept) or any(index < 0 or index >= len(dims) for index in kept):
        raise ValueError("invalid kept subsystem list")
    traced = [index for index in range(len(dims)) if index not in kept]
    tensor = matrix.reshape(*(dims + dims))
    current_dims = list(dims)
    for subsystem in sorted(traced, reverse=True):
        tensor = np.trace(tensor, axis1=subsystem, axis2=subsystem + len(current_dims))
        current_dims.pop(subsystem)
    kept_dimension = math.prod(current_dims)
    return hermitian(tensor.reshape(kept_dimension, kept_dimension))
