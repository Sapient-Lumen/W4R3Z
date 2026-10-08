#!/usr/bin/env python3
"""Source-conditioned fixed-region routing budgets for Family C.

REF-0735 Definition 7 separates two approximate-subsystem-orthogonality
parameters.  Condition 2 controls the full trace norm of the part of a
single-sector retained-region state outside its declared dominant block,
whereas Condition 1 controls off-diagonal large-code terms on the complementary
region.  This module translates the first condition into an explicit
sector-diagonal common-decoder budget and stress-tests the still-distinct
coherent-sector completion.

The calculations are finite-dimensional theorem cells.  They do not derive the
physical G- or N-dependence of any source error parameter.
"""
from __future__ import annotations

import math
import sys
from typing import Any

import numpy as np

sys.dont_write_bytecode = True

from benchmark_numeric import log_log_slope, stable_number
from familyc_operator_algebra import partial_trace, trace_norm_hermitian

TOLERANCE = 1e-12
SOURCE_EPS_ISO_SMALL = 1e-3
SOURCE_EPS_SUB_TR_ROWS = [0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.001]
COHERENT_LEAKAGE_ROWS = [0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005]
TARGET_TRACE_ERRORS = [0.5, 0.25, 0.1, 0.05, 0.01]
RARE_SECTOR_COUNTS = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]


def _projectors() -> tuple[np.ndarray, np.ndarray]:
    return (
        np.diag([1.0, 0.0]).astype(complex),
        np.diag([0.0, 1.0]).astype(complex),
    )


def _outer(vector: np.ndarray) -> np.ndarray:
    return np.outer(vector, vector.conj())


def _sector_diagonal_rows() -> list[dict[str, Any]]:
    """Verify the sharp linear Condition-2 routing bound."""
    z = 1.0 - SOURCE_EPS_ISO_SMALL
    rows: list[dict[str, Any]] = []
    target = np.diag([1.0, 0.0]).astype(complex)
    center_sign = np.diag([1.0, -1.0]).astype(complex)
    for epsilon_sub_tr in SOURCE_EPS_SUB_TR_ROWS:
        if epsilon_sub_tr >= z:
            raise ValueError("epsilon_sub_tr must be below the sector trace floor")
        unnormalized = np.diag([z - epsilon_sub_tr, epsilon_sub_tr]).astype(complex)
        dominant = np.diag([z - epsilon_sub_tr, 0.0]).astype(complex)
        subleading = unnormalized - dominant
        normalized = unnormalized / z
        wrong_probability = epsilon_sub_tr / z
        source_bound = 2.0 * epsilon_sub_tr / (1.0 - SOURCE_EPS_ISO_SMALL)
        trace_error = trace_norm_hermitian(normalized - target)
        center_error = abs(np.trace(center_sign @ normalized) - np.trace(center_sign @ target))
        rows.append(
            {
                "epsilon_iso_small": SOURCE_EPS_ISO_SMALL,
                "sector_trace_z": stable_number(z),
                "epsilon_sub_tr": epsilon_sub_tr,
                "source_subleading_trace_norm": stable_number(
                    trace_norm_hermitian(subleading)
                ),
                "normalized_wrong_block_probability": stable_number(wrong_probability),
                "normalized_state_to_dominant_block_trace_norm": stable_number(trace_error),
                "common_decoder_direct_sum_trace_norm_error": stable_number(trace_error),
                "center_sign_expectation_error": stable_number(center_error),
                "condition2_linear_bound": stable_number(source_bound),
                "bound_saturation_residual": stable_number(abs(trace_error - source_bound)),
            }
        )
    return rows


def _target_inversion_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    trace_floor = 1.0 - SOURCE_EPS_ISO_SMALL
    for target in TARGET_TRACE_ERRORS:
        block_certified = 0.5 * trace_floor * target
        full_sector_certified = 0.25 * trace_floor * target
        rows.append(
            {
                "target_common_decoder_trace_norm_error": target,
                "epsilon_iso_small": SOURCE_EPS_ISO_SMALL,
                "required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block": stable_number(
                    block_certified
                ),
                "required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state": stable_number(
                    full_sector_certified
                ),
                "dominant_block_bound_at_budget": stable_number(
                    2.0 * block_certified / trace_floor
                ),
                "full_sector_transport_bound_at_budget": stable_number(
                    4.0 * full_sector_certified / trace_floor
                ),
            }
        )
    return rows


def _environment_tagged_coherent_row(wrong_mass: float) -> dict[str, Any]:
    """Exact-isometry cell where eps_OD pays coherent-sector contamination."""
    r = float(wrong_mass)
    if not 0.0 < r < 0.5:
        raise ValueError("wrong_mass must lie in (0, 1/2)")
    # Tensor order is R x Rbar.  The two columns are globally orthonormal.
    sector_zero = np.array([math.sqrt(1.0 - r), 0.0, 0.0, math.sqrt(r)], dtype=complex)
    sector_one = np.array([math.sqrt(r), 0.0, 0.0, -math.sqrt(1.0 - r)], dtype=complex)
    encoding = np.column_stack([sector_zero, sector_one])
    p0, p1 = _projectors()
    rho_zero_r = partial_trace(_outer(sector_zero), [2, 2], [0])
    rho_one_r = partial_trace(_outer(sector_one), [2, 2], [0])
    epsilon_sub_zero = trace_norm_hermitian(rho_zero_r - p0 @ rho_zero_r @ p0)
    epsilon_sub_one = trace_norm_hermitian(rho_one_r - p1 @ rho_one_r @ p1)

    plus = (sector_zero + sector_one) / math.sqrt(2.0)
    plus_r = partial_trace(_outer(plus), [2, 2], [0])
    block_output = p0 @ plus_r @ p0 + p1 @ plus_r @ p1
    target_center = 0.5 * np.eye(2, dtype=complex)
    center_error = trace_norm_hermitian(block_output - target_center)

    off_diagonal_global = 0.5 * (
        np.outer(sector_zero, sector_one.conj())
        + np.outer(sector_one, sector_zero.conj())
    )
    off_diagonal_complement = partial_trace(off_diagonal_global, [2, 2], [1])
    epsilon_od = trace_norm_hermitian(off_diagonal_complement)
    expected = 2.0 * math.sqrt(r * (1.0 - r))
    return {
        "wrong_block_probability_per_sector": r,
        "epsilon_sub_tr_per_sector": stable_number(max(epsilon_sub_zero, epsilon_sub_one)),
        "epsilon_OD_for_equal_coherent_superposition": stable_number(epsilon_od),
        "block_instrument_center_trace_norm_error": stable_number(center_error),
        "analytic_coherent_error": stable_number(expected),
        "encoding_isometry_operator_norm_residual": stable_number(
            float(np.linalg.norm(encoding.conj().T @ encoding - np.eye(2), ord=2))
        ),
        "condition2_residual": stable_number(
            max(abs(epsilon_sub_zero - r), abs(epsilon_sub_one - r))
        ),
        "epsilon_OD_payment_residual": stable_number(abs(center_error - epsilon_od)),
    }


def _carrier_frame_coherent_row(wrong_mass: float) -> dict[str, Any]:
    """Exact-isometry cell where eps_sub-tr itself pays coherent contamination."""
    r = float(wrong_mass)
    if not 0.0 < r < 0.5:
        raise ValueError("wrong_mass must lie in (0, 1/2)")
    # Both code vectors use the same complement state; orthogonality is wholly on R.
    sector_zero = np.array([math.sqrt(1.0 - r), 0.0, math.sqrt(r), 0.0], dtype=complex)
    sector_one = np.array([math.sqrt(r), 0.0, -math.sqrt(1.0 - r), 0.0], dtype=complex)
    encoding = np.column_stack([sector_zero, sector_one])
    p0, p1 = _projectors()
    rho_zero_r = partial_trace(_outer(sector_zero), [2, 2], [0])
    rho_one_r = partial_trace(_outer(sector_one), [2, 2], [0])
    epsilon_sub_zero = trace_norm_hermitian(rho_zero_r - p0 @ rho_zero_r @ p0)
    epsilon_sub_one = trace_norm_hermitian(rho_one_r - p1 @ rho_one_r @ p1)

    plus = (sector_zero + sector_one) / math.sqrt(2.0)
    plus_r = partial_trace(_outer(plus), [2, 2], [0])
    block_output = p0 @ plus_r @ p0 + p1 @ plus_r @ p1
    target_center = 0.5 * np.eye(2, dtype=complex)
    center_error = trace_norm_hermitian(block_output - target_center)

    off_diagonal_global = 0.5 * (
        np.outer(sector_zero, sector_one.conj())
        + np.outer(sector_one, sector_zero.conj())
    )
    off_diagonal_complement = partial_trace(off_diagonal_global, [2, 2], [1])
    epsilon_od = trace_norm_hermitian(off_diagonal_complement)
    expected_sub = math.sqrt(4.0 * r - 3.0 * r * r)
    expected_error = 2.0 * math.sqrt(r * (1.0 - r))
    return {
        "wrong_block_probability_per_sector": r,
        "epsilon_sub_tr_per_sector": stable_number(max(epsilon_sub_zero, epsilon_sub_one)),
        "epsilon_OD_for_equal_coherent_superposition": stable_number(epsilon_od),
        "block_instrument_center_trace_norm_error": stable_number(center_error),
        "analytic_epsilon_sub_tr": stable_number(expected_sub),
        "analytic_coherent_error": stable_number(expected_error),
        "encoding_isometry_operator_norm_residual": stable_number(
            float(np.linalg.norm(encoding.conj().T @ encoding - np.eye(2), ord=2))
        ),
        "condition2_formula_residual": stable_number(
            max(abs(epsilon_sub_zero - expected_sub), abs(epsilon_sub_one - expected_sub))
        ),
        "epsilon_OD_zero_residual": stable_number(epsilon_od),
        "coherent_error_below_epsilon_sub_tr": bool(center_error <= expected_sub + TOLERANCE),
    }


def _rare_sector_rows() -> list[dict[str, Any]]:
    bad_epsilon = 0.1
    worst_error = 2.0 * bad_epsilon
    return [
        {
            "sector_count": count,
            "reference_mixture_average_epsilon_sub_tr": stable_number(bad_epsilon / count),
            "reference_mixture_average_decoder_trace_norm_error": stable_number(
                worst_error / count
            ),
            "bad_sector_epsilon_sub_tr": bad_epsilon,
            "worst_sector_common_decoder_trace_norm_error": worst_error,
            "invalid_bound_if_average_is_substituted_for_uniform_epsilon_sub_tr": stable_number(
                worst_error / count
            ),
        }
        for count in RARE_SECTOR_COUNTS
    ]


def source_condition2_decoder_budget_probe() -> dict[str, Any]:
    """Return the executable source-to-routing translation and stress cells."""
    sector_rows = _sector_diagonal_rows()
    target_rows = _target_inversion_rows()
    environment_rows = [
        _environment_tagged_coherent_row(value) for value in COHERENT_LEAKAGE_ROWS
    ]
    carrier_rows = [_carrier_frame_coherent_row(value) for value in COHERENT_LEAKAGE_ROWS]
    rare_rows = _rare_sector_rows()

    slopes = {
        "sector_diagonal_error_vs_epsilon_sub_tr": stable_number(
            log_log_slope(
                sector_rows,
                "epsilon_sub_tr",
                "common_decoder_direct_sum_trace_norm_error",
            )
        ),
        "environment_tagged_coherent_error_vs_epsilon_sub_tr": stable_number(
            log_log_slope(
                environment_rows,
                "epsilon_sub_tr_per_sector",
                "block_instrument_center_trace_norm_error",
            )
        ),
        "environment_tagged_coherent_error_vs_epsilon_OD": stable_number(
            log_log_slope(
                environment_rows,
                "epsilon_OD_for_equal_coherent_superposition",
                "block_instrument_center_trace_norm_error",
            )
        ),
        "carrier_frame_coherent_error_vs_epsilon_sub_tr": stable_number(
            log_log_slope(
                carrier_rows,
                "epsilon_sub_tr_per_sector",
                "block_instrument_center_trace_norm_error",
            )
        ),
        "rare_sector_average_vs_sector_count": stable_number(
            log_log_slope(
                rare_rows,
                "sector_count",
                "reference_mixture_average_epsilon_sub_tr",
            )
        ),
    }

    return {
        "source_contract": {
            "reference": "REF-0735 Definition 7, Condition 2, Eqs. (4.9)-(4.12)",
            "retained_region": "one alpha-independent fixed boundary region R with orthogonal carrier blocks H_Ralpha",
            "condition2": "For every sector alpha and every state in that sector, hat rho_R^alpha = hat rho_Ralpha^alpha + hat rho_R,sub^alpha with ||hat rho_R,sub^alpha||_1 <= epsilon_sub-tr, using one alpha-independent epsilon_sub-tr.",
            "normalization_floor": "The small-code approximate-isometry premise gives z_alpha=Tr(hat rho_R^alpha) >= 1-epsilon_iso,small.",
            "wrong_block_probability": "q_alpha <= epsilon_sub-tr/z_alpha <= epsilon_sub-tr/(1-epsilon_iso,small).",
            "normalized_state_transport": "The normalized full sector state differs from its normalized dominant block by at most 2 epsilon_sub-tr/(1-epsilon_iso,small) in trace norm.",
            "block_certified_common_decoder": "On the sector-diagonal/direct-sum state domain, if each dominant block has one sector decoder with trace-norm error epsilon_block, the projective block instrument followed by those decoders obeys epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small).",
            "full_sector_certificate_conversion": "If a sector decoder is certified only on the normalized full sector output, transporting that certificate to the dominant block and then routing gives the looser sufficient bound epsilon_common <= epsilon_full + 4 epsilon_sub-tr/(1-epsilon_iso,small).",
            "scope_boundary": "These are routing sublemmas after the channel/normalization premise is paid. The sector-diagonal result is not by itself a whole-convex-code OAQEC theorem for coherent superpositions across sectors.",
        },
        "sector_diagonal_linear_budget": {
            "rows": sector_rows,
            "fitted_log_log_slope": slopes["sector_diagonal_error_vs_epsilon_sub_tr"],
            "sharpness": "The owned diagonal wrong-block family exactly saturates the 2 epsilon_sub-tr/(1-epsilon_iso,small) state and center-observable bound.",
        },
        "target_inversion": {
            "rows": target_rows,
            "interpretation": "A dominant-block decoder certificate permits twice the epsilon_sub-tr budget of a certificate stated only on the full sector output under this conservative transport chain.",
        },
        "coherent_superposition_completion_stress": {
            "environment_tagged_rows": environment_rows,
            "carrier_frame_rows": carrier_rows,
            "fitted_log_log_slopes": {
                key: value
                for key, value in slopes.items()
                if key.startswith("environment_") or key.startswith("carrier_")
            },
            "environment_tagged_interpretation": "Here epsilon_sub-tr=r, but the block-instrument error is 2 sqrt(r(1-r)); the source's separate epsilon_OD for the coherent input is exactly the same quantity. Substituting epsilon_sub-tr alone as a linear whole-code coherent bound loses a square root.",
            "carrier_frame_interpretation": "Here epsilon_OD is zero because the complement carries no sector record, while Condition 2's full trace-norm subleading term already includes the carrier coherence and upper-bounds the block-instrument error. The two source errors have distinct, non-interchangeable roles.",
            "required_completion": "A whole-code algebra decoder needs a uniform bound on coherent off-diagonal contamination after the chosen fixed-region block instrument, derived from the same-domain epsilon_OD, epsilon_sub-tr, approximate-isometry, and sector-support assumptions. The present cells do not assert a universal sum rule between those parameters.",
        },
        "rare_sector_uniformity_negative_control": {
            "rows": rare_rows,
            "average_slope_vs_sector_count": slopes[
                "rare_sector_average_vs_sector_count"
            ],
            "severe_failure": "One bad sector makes the reference-mixture average epsilon_sub-tr and average decoder error fall as 1/K while the worst-sector common-decoder error remains 0.2. Definition 7's alpha-independent bound must remain a supremum, not a sector average.",
        },
        "parameter_role_split": {
            "epsilon_sub_tr": "retained-region single-sector dominant-block leakage, including wrong diagonal blocks and carrier-block coherences",
            "epsilon_OD": "off-diagonal large-code contribution on the complementary region; in the environment-tagged coherent cell it exactly pays the center bias that epsilon_sub-tr alone would price only through a square root",
            "epsilon_iso_small": "normalization floor for each small-code sector; it appears in the denominator and is not a routing-confusion parameter",
            "forbidden_substitutions": [
                "epsilon_OD alone pays retained-region wrong-block routing",
                "epsilon_sub-tr alone gives a linear whole-code coherent-superposition decoder bound",
                "a sector-weighted mean replaces the alpha-independent uniform epsilon_sub-tr",
                "a decoder certified on the full sector output is automatically certified on the normalized dominant block",
            ],
        },
    }
