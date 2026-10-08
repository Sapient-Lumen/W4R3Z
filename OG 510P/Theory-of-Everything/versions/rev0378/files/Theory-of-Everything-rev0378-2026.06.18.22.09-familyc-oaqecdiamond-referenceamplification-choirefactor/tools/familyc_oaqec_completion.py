#!/usr/bin/env python3
"""Reference-stable operator-algebra recovery completion for Family C.

The large-code source controls state-level reduced operators.  Whole-code
operator-algebra recovery is stronger: its natural error is a complementary-
channel diamond norm, which is stable under arbitrary reference systems.  This
route-local helper makes that missing conversion executable, supplies a sharp
reference-amplification counterexample, and includes a positive erasure-channel
control.  It claims no physical finite-N scaling law.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from benchmark_numeric import log_log_slope, stable_number
from familyc_operator_algebra import (
    diagonal_correlation_projector,
    partial_trace,
    swap_operator,
    trace_norm_hermitian,
    unnormalized_maximally_entangled_vector,
)

REFERENCE_DIMENSIONS = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
CHOI_AUDIT_DIMENSIONS = [2, 3, 4, 8, 16]
TARGET_RECOVERY_ERRORS = [0.5, 0.25, 0.1, 0.05, 0.01]
TARGET_CODE_DIMENSIONS = [2, 16, 256, 4096]
ERASURE_DIMENSIONS = [2, 4, 8, 16]
ERASURE_PROBABILITIES = [0.1, 0.03, 0.01, 0.003, 0.001]
RATE_G_VALUES = [1.0 / value for value in (4, 8, 16, 32, 64)]
TOLERANCE = 1e-12


def _choi_jordan_marginal_audit(dimension: int) -> dict[str, Any]:
    """Verify the exact diamond norm of the transpose/dephasing defect.

    For Delta=(transpose - transpose o dephase)/(d+1), the Choi matrix is
    (F-Q)/(d+1).  Its positive and negative parts have the same input marginal
    c I.  They are therefore c times channel Choi matrices, giving an upper
    bound 2c.  The maximally entangled input reaches 2c, so the bound is exact.
    """
    swap = swap_operator(dimension)
    diagonal = diagonal_correlation_projector(dimension)
    choi = (swap - diagonal) / (dimension + 1.0)
    eigenvalues, eigenvectors = np.linalg.eigh(0.5 * (choi + choi.conj().T))
    positive = eigenvectors @ np.diag(np.clip(eigenvalues, 0.0, None)) @ eigenvectors.conj().T
    negative = eigenvectors @ np.diag(np.clip(-eigenvalues, 0.0, None)) @ eigenvectors.conj().T
    marginal_constant = (dimension - 1.0) / (2.0 * (dimension + 1.0))
    expected_marginal = marginal_constant * np.eye(dimension, dtype=complex)
    positive_marginal = partial_trace(positive, [dimension, dimension], [1])
    negative_marginal = partial_trace(negative, [dimension, dimension], [1])
    maximally_entangled_lower = trace_norm_hermitian(choi) / dimension
    exact = (dimension - 1.0) / (dimension + 1.0)
    return {
        "dimension": dimension,
        "minimum_choi_eigenvalue": stable_number(float(eigenvalues.min())),
        "maximum_choi_eigenvalue": stable_number(float(eigenvalues.max())),
        "positive_input_marginal_operator_norm_residual": stable_number(
            float(np.linalg.norm(positive_marginal - expected_marginal, ord=2))
        ),
        "negative_input_marginal_operator_norm_residual": stable_number(
            float(np.linalg.norm(negative_marginal - expected_marginal, ord=2))
        ),
        "jordan_upper_bound": stable_number(2.0 * marginal_constant),
        "maximally_entangled_lower_bound": stable_number(maximally_entangled_lower),
        "analytic_exact_diamond_defect": stable_number(exact),
        "exact_formula_residual": stable_number(
            max(
                abs(maximally_entangled_lower - exact),
                abs(2.0 * marginal_constant - exact),
            )
        ),
    }


def _reference_amplification_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dimension in REFERENCE_DIMENSIONS:
        state_envelope = 2.0 / (dimension + 1.0)
        coherent_state_witness = 2.0 * (dimension - 1.0) / (
            dimension * (dimension + 1.0)
        )
        diamond = (dimension - 1.0) / (dimension + 1.0)
        rows.append(
            {
                "code_dimension": dimension,
                "uniform_state_trace_norm_envelope": stable_number(state_envelope),
                "maximally_coherent_state_trace_norm_witness": stable_number(
                    coherent_state_witness
                ),
                "exact_reference_assisted_diamond_defect": stable_number(diamond),
                "beny_minimum_reconstruction_error_lower_bound": stable_number(
                    diamond * diamond / 4.0
                ),
                "diamond_to_state_envelope_ratio": stable_number(
                    diamond / state_envelope
                ),
                "diamond_to_coherent_state_witness_ratio": stable_number(
                    diamond / coherent_state_witness
                ),
                "generic_dimension_lift_upper_bound": stable_number(
                    min(2.0, dimension * state_envelope)
                ),
            }
        )
    return rows


def _target_inversion_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in TARGET_RECOVERY_ERRORS:
        diamond_budget = target * target / 4.0
        for dimension in TARGET_CODE_DIMENSIONS:
            rows.append(
                {
                    "target_oaqec_diamond_reconstruction_error": target,
                    "code_dimension": dimension,
                    "required_complementary_diamond_defect_max": stable_number(
                        diamond_budget
                    ),
                    "required_state_only_defect_max_under_generic_dimension_lift": stable_number(
                        diamond_budget / dimension
                    ),
                }
            )
    return rows


def _erasure_positive_control() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    maximum_choi_formula_residual = 0.0
    for dimension in ERASURE_DIMENSIONS:
        exact_id_minus_depolarizing = 2.0 * (1.0 - 1.0 / (dimension * dimension))
        omega = unnormalized_maximally_entangled_vector(dimension)
        identity_choi = np.outer(omega, omega.conj())
        depolarizing_choi = np.eye(dimension * dimension, dtype=complex) / dimension
        choi_witness = trace_norm_hermitian(identity_choi - depolarizing_choi) / dimension
        maximum_choi_formula_residual = max(
            maximum_choi_formula_residual,
            abs(choi_witness - exact_id_minus_depolarizing),
        )
        for probability in ERASURE_PROBABILITIES:
            defect = probability * exact_id_minus_depolarizing
            rows.append(
                {
                    "code_dimension": dimension,
                    "erasure_probability": probability,
                    "exact_complementary_diamond_defect": stable_number(defect),
                    "exact_reconstruction_diamond_error_of_replace_on_erasure_decoder": stable_number(
                        defect
                    ),
                    "beny_necessary_lower_bound": stable_number(defect * defect / 4.0),
                    "beny_sufficient_upper_bound": stable_number(
                        min(2.0, 2.0 * math.sqrt(defect))
                    ),
                }
            )
    target_rows: list[dict[str, Any]] = []
    for target in TARGET_RECOVERY_ERRORS:
        for dimension in ERASURE_DIMENSIONS:
            coefficient = 2.0 * (1.0 - 1.0 / (dimension * dimension))
            target_rows.append(
                {
                    "target_reconstruction_diamond_error": target,
                    "code_dimension": dimension,
                    "exact_erasure_probability_budget": stable_number(target / coefficient),
                    "beny_theorem_only_sufficient_erasure_probability_budget": stable_number(
                        target * target / (4.0 * coefficient)
                    ),
                }
            )
    return {
        "model": "d-dimensional erasure channel with receiver output (1-p)rho plus an orthogonal erasure flag; the complement receives rho only on erasure.",
        "exact_identity": "For the full matrix algebra, delta_A = E_A = 2 p (1-1/d^2) when the erasure decoder replaces the lost input by I/d.",
        "rows": rows,
        "target_inversion_rows": target_rows,
        "maximum_maximally_entangled_choi_formula_residual": stable_number(
            maximum_choi_formula_residual
        ),
        "interpretation": "A complete complementary-channel diamond defect produces one common decoder with exact operational scaling. The general Bény sufficient upper bound is valid but intentionally conservative in this soluble family.",
    }


def _large_code_rate_wedge() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    dimension_rate = 1.0
    for label, state_error_rate in (
        ("insufficient_state_rate", 0.75),
        ("critical_rate_plateau", 1.0),
        ("reference_stable_rate", 1.25),
    ):
        rows: list[dict[str, Any]] = []
        for gravity_parameter in RATE_G_VALUES:
            log_code_dimension = dimension_rate / gravity_parameter
            log_state_error = -state_error_rate / gravity_parameter
            log_lift = log_code_dimension + log_state_error
            if log_lift >= math.log(2.0):
                diamond_upper = 2.0
            else:
                diamond_upper = math.exp(log_lift)
            recovery_upper = min(2.0, 2.0 * math.sqrt(diamond_upper))
            rows.append(
                {
                    "G": stable_number(gravity_parameter),
                    "log_code_dimension": stable_number(log_code_dimension),
                    "state_only_error": stable_number(math.exp(log_state_error)),
                    "log_unclipped_dimension_lift": stable_number(log_lift),
                    "generic_complementary_diamond_upper_bound": stable_number(
                        diamond_upper
                    ),
                    "beny_sufficient_reconstruction_upper_bound": stable_number(
                        recovery_upper
                    ),
                }
            )
        scenarios.append(
            {
                "scenario": label,
                "dimension_rate_s": dimension_rate,
                "state_error_rate_c": state_error_rate,
                "rows": rows,
                "small_G_outcome": (
                    "vacuous"
                    if state_error_rate < dimension_rate
                    else "plateau"
                    if state_error_rate == dimension_rate
                    else "convergent"
                ),
            }
        )
    return {
        "declared_schedule": "d_code(G)=exp(s/G) and epsilon_state(G)=exp(-c/G); the generic reference-stable lift is bounded by exp((s-c)/G), capped at the channel maximum 2.",
        "conditional_open_wedge": "This generic route requires c>s. Calling epsilon_OD merely 'nonperturbatively small' is insufficient when the large-code/reference dimension also grows nonperturbatively.",
        "scenarios": scenarios,
        "authority_boundary": "The schedules are symbolic rate tests. They do not identify d_code with CFT N, central charge, area, or the number of source sectors, and they do not assign a physical c or s.",
    }


def oaqec_reference_completion_probe() -> dict[str, Any]:
    """Return theorem contract, sharp failure, positive control, and rate wedge."""
    reference_rows = _reference_amplification_rows()
    tail_rows = reference_rows[-6:]
    slopes = {
        "state_envelope_vs_dimension": stable_number(
            log_log_slope(
                tail_rows,
                "code_dimension",
                "uniform_state_trace_norm_envelope",
            )
        ),
        "coherent_state_witness_vs_dimension": stable_number(
            log_log_slope(
                tail_rows,
                "code_dimension",
                "maximally_coherent_state_trace_norm_witness",
            )
        ),
        "diamond_defect_vs_dimension": stable_number(
            log_log_slope(
                tail_rows,
                "code_dimension",
                "exact_reference_assisted_diamond_defect",
            )
        ),
        "reconstruction_lower_bound_vs_dimension": stable_number(
            log_log_slope(
                tail_rows,
                "code_dimension",
                "beny_minimum_reconstruction_error_lower_bound",
            )
        ),
    }
    return {
        "theorem_contract": {
            "reference": "REF-0736, Theorem 1",
            "target": "A finite-dimensional observable algebra A and a noise channel N with complementary channel Nhat.",
            "complementary_defect": "delta_A(N)=||Nhat-Nhat o P_{A'}||_diamond, where P_{A'} projects onto the commutant algebra.",
            "optimal_reconstruction_error": "E_A(N)=min_R ||R o N-P_A||_diamond.",
            "necessary_and_sufficient_bounds": "delta_A(N)^2/4 <= E_A(N) <= 2 sqrt(delta_A(N)).",
            "target_inversion": "To certify E_A<=tau from the sufficient side, require delta_A<=tau^2/4.",
            "reference_stability": "The diamond norm includes arbitrary entanglement with a reference system; a state-only trace-norm supremum on the code is not the same contract.",
        },
        "state_to_diamond_conversion": {
            "generic_finite_dimension_bound": "For a Hermiticity-preserving defect map Delta on a d_code-dimensional input, ||Delta||_diamond <= d_code sup_rho ||Delta(rho)||_1.",
            "target_inversion_rows": _target_inversion_rows(),
            "boundary": "This conversion may be loose, but without additional complete-boundedness structure its d_code factor cannot be dropped. The source epsilon_OD must first be shown to control the same complementary defect map and normalization/domain as Delta.",
        },
        "reference_amplification_negative_control": {
            "model": "Let Nhat_d(rho)=(Tr(rho) I + rho^T)/(d+1), a transpose-depolarizing channel, and let A be the diagonal algebra so P_{A'} is basis dephasing. Then Delta_d=Nhat_d-Nhat_d o P_{A'}=(rho^T-diag(rho))/(d+1).",
            "channel_audit": "The Choi matrix of Nhat_d is (I+F)/(d+1)=2 P_sym/(d+1), so Nhat_d is CPTP. The defect Choi matrix is (F-Q)/(d+1).",
            "exact_diamond_proof": "The positive and negative Choi parts have identical input marginal [(d-1)/(2(d+1))]I, giving an upper bound (d-1)/(d+1); the maximally entangled input reaches it.",
            "rows": reference_rows,
            "fitted_last_six_log_log_slopes": slopes,
            "choi_jordan_audit_rows": [
                _choi_jordan_marginal_audit(dimension)
                for dimension in CHOI_AUDIT_DIMENSIONS
            ],
            "severe_failure": "The uniform state-level envelope falls as 1/d, yet the exact complementary-channel diamond defect tends to one and Bény's minimum reconstruction-error lower bound tends to 1/4. Reference amplification therefore blocks whole-code OAQEC convergence.",
        },
        "erasure_channel_positive_control": _erasure_positive_control(),
        "large_code_reference_rate_wedge": _large_code_rate_wedge(),
        "source_join": {
            "what_condition1_supplies": "REF-0735 Definition 7 Condition 1 is a state-level trace-norm bound on complementary-region off-diagonal contributions, uniform in the declared large-code state but not stated as a diamond/cb norm with an external reference.",
            "what_is_still_required": "Either derive delta_A directly in complementary-channel diamond norm on the same fixed region and target algebra, or provide an explicit d_code/reference law and a state-to-diamond theorem whose rate clears d_code epsilon_OD -> 0 together with the other normalization, routing, center, and factor errors.",
            "non_substitution_rule": "epsilon_OD, epsilon_sub-tr, an average entanglement fidelity, and an unassisted state supremum cannot be renamed delta_A without a reference-stable proof.",
        },
    }
