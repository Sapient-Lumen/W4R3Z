#!/usr/bin/env python3
"""Translate a uniform JLMS remainder into an operational recovery budget.

This benchmark does not derive a finite-N holographic remainder.  It makes
three missing bridges executable: projected-JLMS to pairwise relative entropy,
that defect to a genuine recovery channel, and state-level sector errors to a
reference-stable operator-algebra criterion.  Negative controls expose
average-to-supremum laundering, approximate-isometry spectral amplification,
and reference-system amplification hidden by unassisted state norms.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from benchmark_numeric import log_log_slope, stable_number
from familyc_channel_completion import (
    flagged_channel_completion_probe,
    flagged_completion_budget,
    flagged_target_budget_rows,
    full_system_flm_isometry_bound,
    noncommuting_flagged_channel_probe,
    normalized_filter_state,
    relative_entropy_nats,
    source_closed_sector_wedge,
    source_power_transfer_schedule,
    source_tail_wedge_rows,
)
from familyc_decoder_gluing import (
    fixed_region_common_decoder_probe,
    state_dependent_wedge_probe,
)
from familyc_operator_algebra import (
    direct_sum_operator_algebra_probe,
    noncommuting_modular_rotation_schedule,
)
from familyc_oaqec_completion import oaqec_reference_completion_probe
from familyc_state_domain import (
    exact_geometry_probe,
    relative_floor_mass_geometry,
    sector_transport_log_smoothness_probe,
)
from familyc_source_routing import source_condition2_decoder_budget_probe
from generated_benchmark_artifact import (
    check_generated_texts,
    generated_texts,
    parse_write_check_args,
    write_generated_texts,
)

OUTPUT_JSON = "FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK.json"
OUTPUT_MD = "docs/30-program/familyc-jlms-recovery-budget-benchmark.generated.md"
ROUTE_ID = "R-OQ0057-FAMILYC-EW-CODE"
DECISION_ID = "DX-0015-FAMILYC-FINITE-N-QEC-ISLAND-DECODER-REPLAY"
SOURCE_REFS = ["REF-0528", "REF-0532", "REF-0533", "REF-0534", "REF-0535", "REF-0735", "REF-0736"]
RESOURCE_SCHEDULE = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
RARE_SECTOR_COUNTS = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
REMAINDER_COEFFICIENT = 0.25
TARGET_TRACE_ERRORS = [0.5, 0.25, 0.1, 0.05, 0.01]
UNIT_PROBE_NATS = 0.1
FULL_CODE_CONSTANT = 2.0 + math.sqrt(2.0 * math.log(2.0))
TOLERANCE = 1e-12
EXACT_CHANNEL_CROSSOVER = 0.01
EXACT_CHANNEL_GRID = [0.1 + 0.02 * index for index in range(41)]
ISOMETRY_STRESS_DELTA = 1e-3
ISOMETRY_STRESS_FLOORS = [1e-1, 1e-3, 1e-6, 1e-12]
SECTOR_GROWTH_BIT_EXPONENTS = [16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
SECTOR_TOTAL_FLOOR_MASS = 0.1
SECTOR_TRANSPORT_RADII = [8, 16, 32, 64, 128, 256]
SECTOR_TRANSPORT_CURVATURE = 0.2
SECTOR_TRANSPORT_LEAKAGE = 1e-8


def recovery_budget_row(resource: int, exponent: float) -> dict[str, Any]:
    epsilon = REMAINDER_COEFFICIENT * resource ** (-exponent)
    root_fidelity_lower = 2.0 ** (-epsilon / 2.0)
    squared_fidelity_infidelity_upper = 1.0 - 2.0 ** (-epsilon)
    local_trace_tight_from_fidelity = 2.0 * math.sqrt(squared_fidelity_infidelity_upper)
    local_trace_simple = 2.0 * math.sqrt(epsilon)
    full_trace_raw = FULL_CODE_CONSTANT * math.sqrt(epsilon)
    return {
        "resource": resource,
        "declared_uniform_relative_entropy_defect": stable_number(epsilon),
        "universal_recovery_root_fidelity_lower_bound": stable_number(root_fidelity_lower),
        "universal_recovery_squared_fidelity_infidelity_upper_bound": stable_number(
            squared_fidelity_infidelity_upper
        ),
        "local_recovery_trace_norm_bound_from_fidelity": stable_number(
            min(2.0, local_trace_tight_from_fidelity)
        ),
        "local_recovery_trace_norm_simple_bound": stable_number(min(2.0, local_trace_simple)),
        "full_code_trace_norm_and_normalized_observable_bound": stable_number(
            min(2.0, full_trace_raw)
        ),
        "full_code_raw_theorem_bound": stable_number(full_trace_raw),
    }


def recovery_schedule(exponent: float) -> dict[str, Any]:
    rows = [recovery_budget_row(resource, exponent) for resource in RESOURCE_SCHEDULE]
    slopes = {
        "relative_entropy_defect": stable_number(
            log_log_slope(rows, "resource", "declared_uniform_relative_entropy_defect")
        ),
        "squared_fidelity_infidelity": stable_number(
            log_log_slope(
                rows,
                "resource",
                "universal_recovery_squared_fidelity_infidelity_upper_bound",
            )
        ),
        "local_trace_norm": stable_number(
            log_log_slope(rows, "resource", "local_recovery_trace_norm_bound_from_fidelity")
        ),
        "full_code_trace_norm": stable_number(
            log_log_slope(
                rows,
                "resource",
                "full_code_trace_norm_and_normalized_observable_bound",
            )
        ),
    }
    return {
        "declared_remainder_rule": f"epsilon_R = {REMAINDER_COEFFICIENT} R^(-{exponent:g})",
        "rows": rows,
        "fitted_log_log_slopes": slopes,
        "expected_asymptotic_slopes": {
            "relative_entropy_defect": -exponent,
            "squared_fidelity_infidelity": -exponent,
            "local_trace_norm": -exponent / 2.0,
            "full_code_trace_norm": -exponent / 2.0,
        },
    }


def budget_inversion_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in TARGET_TRACE_ERRORS:
        epsilon_max = (target / FULL_CODE_CONSTANT) ** 2
        rows.append(
            {
                "target_full_code_trace_or_normalized_observable_error": target,
                "required_uniform_relative_entropy_defect_max": stable_number(epsilon_max),
                "required_R_over_coefficient_for_epsilon_equals_c_over_R": stable_number(
                    FULL_CODE_CONSTANT ** 2 / target ** 2
                ),
                "required_R_over_sqrt_coefficient_for_epsilon_equals_c_over_R_squared": stable_number(
                    FULL_CODE_CONSTANT / target
                ),
            }
        )
    return rows



def modular_vector_nats(state: list[float]) -> list[float]:
    return [-math.log(value) for value in state]


def binary_symmetric_channel(state: list[float], crossover: float) -> list[float]:
    return [
        (1.0 - crossover) * state[0] + crossover * state[1],
        crossover * state[0] + (1.0 - crossover) * state[1],
    ]


def binary_symmetric_adjoint(values: list[float], crossover: float) -> list[float]:
    return [
        (1.0 - crossover) * values[0] + crossover * values[1],
        crossover * values[0] + (1.0 - crossover) * values[1],
    ]


def exact_isometry_residual(state: list[float], crossover: float) -> list[float]:
    channel_state = binary_symmetric_channel(state, crossover)
    pulled_modular = binary_symmetric_adjoint(modular_vector_nats(channel_state), crossover)
    bulk_modular = modular_vector_nats(state)
    return [pulled - bulk for pulled, bulk in zip(pulled_modular, bulk_modular)]


def exact_isometry_join_probe() -> dict[str, Any]:
    """Numerically verify Delta D = Tr sigma (J_rho-J_sigma)."""
    states = [[value, 1.0 - value] for value in EXACT_CHANNEL_GRID]
    residuals = [exact_isometry_residual(state, EXACT_CHANNEL_CROSSOVER) for state in states]
    eta = max(max(abs(value) for value in residual) for residual in residuals)
    max_identity_residual = 0.0
    max_pairwise_defect = 0.0
    argmax: dict[str, Any] | None = None
    for sigma, j_sigma in zip(states, residuals):
        for rho, j_rho in zip(states, residuals):
            boundary_defect = relative_entropy_nats(
                binary_symmetric_channel(sigma, EXACT_CHANNEL_CROSSOVER),
                binary_symmetric_channel(rho, EXACT_CHANNEL_CROSSOVER),
            )
            bulk_defect = relative_entropy_nats(sigma, rho)
            pairwise_defect = boundary_defect - bulk_defect
            residual_identity = sum(
                probability * (right - left)
                for probability, right, left in zip(sigma, j_rho, j_sigma)
            )
            identity_error = abs(pairwise_defect - residual_identity)
            max_identity_residual = max(max_identity_residual, identity_error)
            if abs(pairwise_defect) > max_pairwise_defect:
                max_pairwise_defect = abs(pairwise_defect)
                argmax = {
                    "sigma": [stable_number(value) for value in sigma],
                    "rho": [stable_number(value) for value in rho],
                    "signed_pairwise_defect_nats": stable_number(pairwise_defect),
                }
    return {
        "model": "binary symmetric channel on a declared full-rank 41-state grid; it has an exact Stinespring isometry and no area term",
        "crossover": EXACT_CHANNEL_CROSSOVER,
        "declared_state_grid_size": len(states),
        "uniform_projected_residual_eta_nats": stable_number(eta),
        "max_absolute_pairwise_relative_entropy_defect_nats": stable_number(max_pairwise_defect),
        "two_eta_bound_nats": stable_number(2.0 * eta),
        "max_identity_residual": stable_number(max_identity_residual),
        "argmax_pair": argmax,
    }


def reweighted_boundary_state(state: list[float], delta: float) -> tuple[list[float], float]:
    return normalized_filter_state(state, [1.0 + delta, 1.0 - delta])


def approximate_isometry_residual(state: list[float], delta: float) -> list[float]:
    boundary, normalization = reweighted_boundary_state(state, delta)
    metric = [1.0 + delta, 1.0 - delta]
    boundary_modular = modular_vector_nats(boundary)
    bulk_modular = modular_vector_nats(state)
    return [
        weight * (boundary_value - bulk_value)
        for weight, boundary_value, bulk_value in zip(metric, boundary_modular, bulk_modular)
    ]


def approximate_isometry_stress_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    delta = ISOMETRY_STRESS_DELTA
    metric = [1.0 + delta, 1.0 - delta]
    sigma = [0.5, 0.5]
    j_sigma = approximate_isometry_residual(sigma, delta)
    boundary_sigma, z_sigma = reweighted_boundary_state(sigma, delta)
    for floor in ISOMETRY_STRESS_FLOORS:
        rho = [1.0 - floor, floor]
        boundary_rho, _ = reweighted_boundary_state(rho, delta)
        j_rho = approximate_isometry_residual(rho, delta)
        domain_residuals = [
            approximate_isometry_residual([value, 1.0 - value], delta)
            for value in (floor, 0.5, 1.0 - floor)
        ]
        eta = max(max(abs(value) for value in residual) for residual in domain_residuals)
        modular_rho = modular_vector_nats(rho)
        modular_sigma = modular_vector_nats(sigma)
        # The normalization-transport term is blind to scalar shifts because
        # Tr[sigma(M/z_sigma-I)]=0.  The load-bearing quantity is therefore
        # the centered operator norm (half the spectral diameter), not the raw
        # norm of a modular-Hamiltonian difference.
        modular_oscillation = 0.5 * math.log((1.0 - floor) / floor)
        actual_defect = relative_entropy_nats(boundary_sigma, boundary_rho) - relative_entropy_nats(
            sigma, rho
        )
        residual_difference_term = sum(
            probability * (right - left)
            for probability, right, left in zip(sigma, j_rho, j_sigma)
        ) / z_sigma
        normalization_transport_term = sum(
            probability
            * (weight / z_sigma - 1.0)
            * (rho_modular - sigma_modular)
            for probability, weight, rho_modular, sigma_modular in zip(
                sigma, metric, modular_rho, modular_sigma
            )
        )
        naive_bound = 2.0 * eta / (1.0 - delta)
        corrected_bound = 2.0 * (eta + delta * modular_oscillation) / (1.0 - delta)
        rows.append(
            {
                "bulk_eigenvalue_floor": floor,
                "delta_isometry": delta,
                "probe_sigma": sigma,
                "reference_rho": [stable_number(value) for value in rho],
                "normalization_z_sigma": stable_number(z_sigma),
                "uniform_residual_eta_nats_on_declared_three-state_domain": stable_number(eta),
                "bulk_modular_oscillation_LK_nats": stable_number(modular_oscillation),
                "actual_pairwise_relative_entropy_defect_nats": stable_number(actual_defect),
                "residual_difference_term_nats": stable_number(residual_difference_term),
                "normalization_transport_term_nats": stable_number(normalization_transport_term),
                "identity_residual": stable_number(
                    abs(actual_defect - residual_difference_term - normalization_transport_term)
                ),
                "naive_bound_omitting_delta_LK_nats": stable_number(naive_bound),
                "corrected_bound_nats": stable_number(corrected_bound),
                "naive_bound_violated": abs(actual_defect) > naive_bound + TOLERANCE,
                "corrected_bound_holds": abs(actual_defect) <= corrected_bound + TOLERANCE,
            }
        )
    return rows



def normalized_filter_channel_premise_probe() -> dict[str, Any]:
    """Expose non-affinity and the exact polar-channelization decomposition.

    The source map is W_V(rho)=V rho V^dagger/Tr(V rho V^dagger).  For
    M=V^dagger V not proportional to the identity this map is nonlinear, so a
    pairwise relative-entropy estimate for W_V is not yet an input to a
    recovery theorem whose premise is a quantum channel.  The diagonal cell
    also verifies the exact residual decomposition after polar correction.
    """
    delta = ISOMETRY_STRESS_DELTA
    rho_zero = [1.0, 0.0]
    rho_one = [0.0, 1.0]
    rho_mix = [0.5, 0.5]
    w_zero, _ = reweighted_boundary_state(rho_zero, delta)
    w_one, _ = reweighted_boundary_state(rho_one, delta)
    w_mix, _ = reweighted_boundary_state(rho_mix, delta)
    affine_mix = [0.5 * (left + right) for left, right in zip(w_zero, w_one)]
    nonaffinity = sum(abs(left - right) for left, right in zip(w_mix, affine_mix))

    probe = [0.7, 0.3]
    w_probe, _ = reweighted_boundary_state(probe, delta)
    metric = [1.0 + delta, 1.0 - delta]
    source_residual = approximate_isometry_residual(probe, delta)
    congruence_source_term = [
        residual / weight for residual, weight in zip(source_residual, metric)
    ]
    output_modular_transport = [
        bulk - filtered
        for bulk, filtered in zip(modular_vector_nats(probe), modular_vector_nats(w_probe))
    ]
    bulk_similarity_transport = [0.0, 0.0]
    polar_residual = [
        source + output + bulk
        for source, output, bulk in zip(
            congruence_source_term,
            output_modular_transport,
            bulk_similarity_transport,
        )
    ]
    return {
        "model": "Two-level normalized filter with M=diag(1+delta,1-delta); its polar isometry is U=I.",
        "delta_isometry": delta,
        "convex_domain_states": {
            "rho_0": rho_zero,
            "rho_1": rho_one,
            "midpoint": rho_mix,
        },
        "normalized_filter_midpoint": [stable_number(value) for value in w_mix],
        "midpoint_of_normalized_filter_outputs": [
            stable_number(value) for value in affine_mix
        ],
        "affine_defect_trace_norm": stable_number(nonaffinity),
        "is_quantum_channel_on_declared_convex_domain": nonaffinity <= TOLERANCE,
        "polar_isometry": "U=V M^(-1/2)=I; N_U(rho)=rho is a genuine channel",
        "polar_probe_state": probe,
        "source_residual_after_M_inverse_congruence": [
            stable_number(value) for value in congruence_source_term
        ],
        "output_modular_transport_term": [
            stable_number(value) for value in output_modular_transport
        ],
        "bulk_similarity_transport_term": bulk_similarity_transport,
        "polar_channel_residual": [stable_number(value) for value in polar_residual],
        "polar_decomposition_identity_residual": stable_number(
            max(abs(value) for value in polar_residual)
        ),
        "interpretation": "The normalized filter fails affinity by exactly delta in this cell. Polar correction restores a channel, but its output-modular transport cancels the transformed source residual; that cancellation is extra information not supplied by the source eta bound alone.",
    }


def projected_join_budget_rows(envelopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projected_terms = next(
        row["term_count"]
        for row in envelopes
        if row["result_kind"] == "projected_JLMS_log_smooth_operator_norm"
    )
    rows: list[dict[str, Any]] = []
    for target in budget_inversion_rows():
        epsilon_bits = float(target["required_uniform_relative_entropy_defect_max"])
        channel_residual_budget = 0.5 * math.log(2.0) * epsilon_bits
        rows.append(
            {
                "target_full_code_trace_or_observable_error": target[
                    "target_full_code_trace_or_normalized_observable_error"
                ],
                "required_uniform_pairwise_defect_bits": stable_number(epsilon_bits),
                "exact_channel_uniform_residual_budget_nats": stable_number(
                    channel_residual_budget
                ),
                "source_eta_max_if_polar_transport_zero_at_delta_1e_minus_3": stable_number(
                    (1.0 - ISOMETRY_STRESS_DELTA) * channel_residual_budget
                ),
                "polar_transport_chi_out_plus_chi_bulk_max_if_eta_zero_nats": stable_number(
                    channel_residual_budget
                ),
                "projected_source_term_count": projected_terms,
                "admissible_region": "eta/(1-delta_iso) + chi_out + chi_bulk <= exact_channel_uniform_residual_budget_nats",
                "status": "planning-only; exact-isometry uses chi_out=chi_bulk=delta_iso=0. Approximate source maps require a proved channelization decomposition on the identical state domain; no equal-share allocation is granted.",
            }
        )
    return rows


def large_code_source_envelopes() -> list[dict[str, Any]]:
    """Record the source's symbolic error envelopes without inventing scaling.

    These are faithful intake contracts for REF-0735.  None is silently renamed
    epsilon_R because the universal-recovery theorem needs a uniform pairwise
    relative-entropy defect, while the source bounds carry different norms and
    state restrictions.
    """
    return [
        {
            "source_result": "Dong-Marolf-Rath Theorem 3, Eq. (4.50)",
            "result_kind": "projected_JLMS_aligned_state_expectation",
            "symbolic_error_envelope": "eps_pJLMS + eps_iso + eps_enhanced + eps_sub_log + eps_l_align",
            "term_count": 5,
            "norm_and_quantifier": "expectation-value bound for a pair rho,sigma satisfying enhanced log-stability and log-alignment",
            "direct_uniform_pairwise_relative_entropy_input": False,
            "translation_debt": "Must be upgraded from an aligned-pair modular-Hamiltonian expectation bound to an absolute relative-entropy defect for every ordered pair in the declared recovery domain.",
        },
        {
            "source_result": "Dong-Marolf-Rath Theorem 5, Eq. (4.85)",
            "result_kind": "projected_JLMS_log_smooth_operator_norm",
            "symbolic_error_envelope": "eps_pJLMS + eps_iso + eps_enhanced + eps_sub_log + eps_l_smooth",
            "term_count": 5,
            "norm_and_quantifier": "operator-norm bound for a reference state rho that is enhanced-log-stable against every sigma and log-smooth",
            "direct_uniform_pairwise_relative_entropy_input": False,
            "conditional_normalized_map_pairwise_join_available": True,
            "direct_recovery_channel_join_available": False,
            "source_error_decomposition": {
                "epsilon_pJLMS_equation_3_17": "sqrt(eps_FLM/eps_tail) + eps_iso_small |log eps_tail|, up to the source's suppressed O(1) coefficients",
                "epsilon_iso_equation_4_24": "eps_iso_small + eps_OD",
                "appendix_C_full_system_branch": "If approximate FLM with the same eps_FLM is separately available on the entire small-code system, Appendix C gives eps_iso_small <= 2 sqrt(eps_FLM); Lemma 4 then gives delta_iso <= 2 sqrt(eps_FLM)+eps_OD for the large code.",
                "power_counting_boundary": "Without the extra full-system premise, eps_iso_small~G^b remains independent and the displayed square-root term vanishes only for a>t. With the Appendix-C branch and nonperturbative eps_OD, b=a/2; for K~exp(c/G^gamma), the flagged sector-geometry route further requires a>2 gamma.",
            },
            "translation_debt": "If the bound holds uniformly for every reference state, the residual controls all-pairs relative entropy for the source's normalized state map. That map is nonlinear whenever V^dagger V is not scalar. A direct recovery-theorem input therefore requires exact/scalar norm, polar transport bounds, or the explicit flagged channel completion used here together with a finite relative-entropy diameter on the identical state domain.",
        },
        {
            "source_result": "Dong-Marolf-Rath Theorem 6, Eq. (4.88)",
            "result_kind": "exponentiated_JLMS_smooth_operator_norm",
            "symbolic_error_envelope": "eps_eJLMS(s) + |s| eps_iso + eps_OD + eps_sub_tr + eps_sub_exp(s) + eps_e_smooth(s)",
            "term_count": 6,
            "norm_and_quantifier": "operator-norm bound at modular parameter s for log-stable small-code components and an exponentiated-smooth state rho",
            "direct_uniform_pairwise_relative_entropy_input": False,
            "translation_debt": "An exponentiated modular-flow bound is not automatically a uniform pairwise relative-entropy defect or a complementary-channel diamond distance; s-dependence and domain coverage must remain explicit.",
        },
    ]



def rare_sector_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sectors in RARE_SECTOR_COUNTS:
        bad_weight = 1.0 / sectors
        reference_mixture_defect = bad_weight
        invalid_uniform_bound = FULL_CODE_CONSTANT * math.sqrt(reference_mixture_defect)
        rows.append(
            {
                "sector_count": sectors,
                "bad_sector_weight_in_uniform_reference_mixture": stable_number(bad_weight),
                "reference_mixture_relative_entropy_defect_bits": stable_number(reference_mixture_defect),
                "bad_sector_probe_relative_entropy_defect": 1.0,
                "whole_domain_uniform_defect_lower_bound_from_probe": 1.0,
                "actual_reference_mixture_recovery_trace_norm_error": stable_number(bad_weight),
                "actual_worst_case_recovery_trace_norm_error": 1.0,
                "invalid_uniform_bound_if_reference_mixture_defect_is_laundered": stable_number(
                    invalid_uniform_bound
                ),
                "invalid_bound_below_actual_worst_case": invalid_uniform_bound < 1.0,
            }
        )
    return rows


def sector_proliferation_schedule() -> dict[str, Any]:
    """Stress the flagged bridge against direct-sum sector growth.

    The source large code is a direct sum.  A sector-local eigenvalue floor
    controls each internal block but does not control the classical sector
    weights p_alpha.  This schedule isolates that missing geometry without
    assigning a physical sector-count law to holography.
    """
    scenarios = [
        {
            "scenario": "exponential_sectors_power_matched_isometry",
            "sector_rule": "K=2^m with G=(m ln 2)^-1, hence log K=G^-1 exactly",
            "sector_growth": "exponential",
            "flm_power": 3.0,
            "tail_power": 1.0,
            "isometry_power": 1.0,
        },
        {
            "scenario": "polynomial_sectors_power_matched_isometry",
            "sector_rule": "K=ceil(G^-2)",
            "sector_growth": "polynomial",
            "flm_power": 3.0,
            "tail_power": 1.0,
            "isometry_power": 1.0,
        },
        {
            "scenario": "exponential_sectors_stronger_isometry",
            "sector_rule": "K=2^m with G=(m ln 2)^-1, hence log K=G^-1 exactly",
            "sector_growth": "exponential",
            "flm_power": 5.0,
            "tail_power": 1.0,
            "isometry_power": 2.0,
        },
    ]
    scenario_results: list[dict[str, Any]] = []
    for scenario in scenarios:
        rows: list[dict[str, Any]] = []
        for bit_exponent in SECTOR_GROWTH_BIT_EXPONENTS:
            g_value = 1.0 / (bit_exponent * math.log(2.0))
            if scenario["sector_growth"] == "exponential":
                log_sector_count = bit_exponent * math.log(2.0)
                sector_count_label = f"2^{bit_exponent}"
            else:
                sector_count = max(2, math.ceil(g_value ** -2.0))
                log_sector_count = math.log(sector_count)
                sector_count_label = str(sector_count)
            geometry = relative_floor_mass_geometry(
                log_dimension=log_sector_count,
                total_floor_mass=SECTOR_TOTAL_FLOOR_MASS,
            )
            epsilon_flm = g_value ** scenario["flm_power"]
            epsilon_tail = g_value ** scenario["tail_power"]
            epsilon_iso_small = g_value ** scenario["isometry_power"]
            epsilon_pjlms = math.sqrt(epsilon_flm / epsilon_tail) + epsilon_iso_small * abs(
                math.log(epsilon_tail)
            )
            source_eta = epsilon_pjlms + epsilon_iso_small
            budget = flagged_completion_budget(
                eta_nats=source_eta,
                delta_isometry=epsilon_iso_small,
                modular_oscillation_nats=float(
                    geometry["exact_centered_modular_oscillation_nats"]
                ),
                relative_entropy_diameter_nats=float(
                    geometry["exact_relative_entropy_diameter_nats"]
                ),
                theorem_constant=FULL_CODE_CONSTANT,
            )
            rows.append(
                {
                    "G": stable_number(g_value),
                    "sector_count": sector_count_label,
                    "log_sector_count_nats": stable_number(log_sector_count),
                    "total_sector_floor_mass": SECTOR_TOTAL_FLOOR_MASS,
                    "minimum_sector_weight_log": stable_number(
                        geometry["minimum_sector_weight_log"]
                    ),
                    "epsilon_FLM": stable_number(epsilon_flm),
                    "epsilon_tail": stable_number(epsilon_tail),
                    "epsilon_iso_small_and_delta_iso": stable_number(
                        epsilon_iso_small
                    ),
                    "source_eta_nats": stable_number(source_eta),
                    "exact_bulk_wedge_relative_entropy_diameter_nats": stable_number(
                        geometry["exact_relative_entropy_diameter_nats"]
                    ),
                    "exact_bulk_wedge_centered_modular_oscillation_nats": stable_number(
                        geometry["exact_centered_modular_oscillation_nats"]
                    ),
                    "flagged_channel_pairwise_defect_bound_nats": stable_number(
                        budget["flagged_channel_pairwise_defect_bound_nats"]
                    ),
                    "success_conditioned_trace_bound": stable_number(
                        budget["success_conditioned_trace_bound"]
                    ),
                }
            )
        asymptotic_rows = rows[-5:]
        slopes = {
            "source_eta_vs_G": stable_number(
                log_log_slope(asymptotic_rows, "G", "source_eta_nats")
            ),
            "flagged_defect_vs_G": stable_number(
                log_log_slope(
                    asymptotic_rows,
                    "G",
                    "flagged_channel_pairwise_defect_bound_nats",
                )
            ),
            "success_trace_vs_G": stable_number(
                log_log_slope(
                    asymptotic_rows, "G", "success_conditioned_trace_bound"
                )
            ),
        }
        scenario_results.append(
            {
                **scenario,
                "rows": rows,
                "fitted_last_five_log_log_slopes": slopes,
                "first_to_last_ratios": {
                    "source_eta": stable_number(
                        rows[-1]["source_eta_nats"] / rows[0]["source_eta_nats"]
                    ),
                    "flagged_defect": stable_number(
                        rows[-1]["flagged_channel_pairwise_defect_bound_nats"]
                        / rows[0]["flagged_channel_pairwise_defect_bound_nats"]
                    ),
                    "success_trace": stable_number(
                        rows[-1]["success_conditioned_trace_bound"]
                        / rows[0]["success_conditioned_trace_bound"]
                    ),
                },
            }
        )
    return {
        "model": "The reduced bulk-wedge algebra is restricted to the classical center of K direct-sum sectors. Every admissible sector weight obeys p_alpha >= mu/K with fixed total floor mass mu=0.1; internal sector states may be identical, so this is already a lower-complexity subdomain of the large code.",
        "exact_domain_geometry": exact_geometry_probe(),
        "sector_weight_formulas": {
            "minimum_weight": "lambda=mu/K",
            "maximum_weight": "a=1-mu+mu/K",
            "bulk_wedge_relative_entropy_diameter": "D_max=(1-mu) log(a/lambda)",
            "bulk_wedge_centered_modular_oscillation": "L_K^osc=log(a/lambda)",
            "asymptotic_growth": "D_max and L_K^osc are Theta(log K) at fixed mu<1",
        },
        "scenarios": scenario_results,
        "severe_failure": "In the exponential-sector, power-matched cell every displayed local source quantity tends to zero: eps_FLM~G^3, eps_tail~G, eps_iso_small=delta_iso~G, and eta~G|log G|. Nevertheless log K=1/G makes delta_iso D_max and delta_iso L_K^osc order one. The executable flagged defect and success-conditioned recovery bound plateau instead of converging. Sector-local log stability therefore cannot certify whole-large-code recovery.",
        "correction": "Declare and prove the sector-weight geometry on the same reconstructed algebra as the JLMS comparison. For K~exp(c/G^gamma) and delta_iso~G^b, this bridge needs b>gamma (plus a>t and uniform residual control); b=gamma is only order-one. A direct bound on D_max and L_K^osc may replace an explicit K law, but a within-sector epsilon_tail cannot.",
        "authority_boundary": "The K(G) schedules are adversarial theorem test vectors, not claims about the physical CFT sector count. They show which additional scaling theorem is necessary before the source envelope can carry recovery authority.",
    }


def full_system_flm_closure_schedule() -> dict[str, Any]:
    """Use the source's optional full-system FLM implication for isometry.

    The previous sector-growth stress treated eps_iso,small as an independent
    input, which is the correct premise when only a subregion FLM estimate is
    available.  REF-0735 Appendix C supplies a stronger branch: full-system
    FLM with error eps_FLM implies eps_iso,small <= 2 sqrt(eps_FLM), and Lemma
    4 adds eps_OD for the large code.  This schedule propagates that actual
    source implication through the owned flagged-channel bridge.
    """
    scenarios = [
        {
            "scenario": "full_system_FLM_critical_a_equals_2gamma",
            "flm_power_a": 2.0,
            "tail_power_t": 1.0,
            "sector_power_gamma": 1.0,
        },
        {
            "scenario": "full_system_FLM_open_a_3",
            "flm_power_a": 3.0,
            "tail_power_t": 1.0,
            "sector_power_gamma": 1.0,
        },
        {
            "scenario": "full_system_FLM_open_a_5",
            "flm_power_a": 5.0,
            "tail_power_t": 1.0,
            "sector_power_gamma": 1.0,
        },
    ]
    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        wedge = source_closed_sector_wedge(
            flm_power=scenario["flm_power_a"],
            tail_power=scenario["tail_power_t"],
            exponential_sector_power=scenario["sector_power_gamma"],
        )
        rows: list[dict[str, Any]] = []
        for bit_exponent in SECTOR_GROWTH_BIT_EXPONENTS:
            g_value = 1.0 / (bit_exponent * math.log(2.0))
            log_sector_count = g_value ** (-scenario["sector_power_gamma"])
            geometry = relative_floor_mass_geometry(
                log_dimension=log_sector_count,
                total_floor_mass=SECTOR_TOTAL_FLOOR_MASS,
            )
            epsilon_flm = g_value ** scenario["flm_power_a"]
            epsilon_tail = g_value ** scenario["tail_power_t"]
            epsilon_od = math.exp(-1.0 / g_value) if 1.0 / g_value < 745.0 else 0.0
            isometry = full_system_flm_isometry_bound(
                epsilon_flm=epsilon_flm,
                epsilon_od=epsilon_od,
            )
            epsilon_iso_small = isometry["epsilon_iso_small_upper"]
            delta_iso = isometry["delta_iso_large_upper"]
            epsilon_pjlms = math.sqrt(epsilon_flm / epsilon_tail) + epsilon_iso_small * abs(
                math.log(epsilon_tail)
            )
            # Best-case source closure cell: the remaining Theorem-5 terms are
            # set to zero, not asserted absent in AdS/CFT.
            source_eta = epsilon_pjlms + delta_iso
            budget = flagged_completion_budget(
                eta_nats=source_eta,
                delta_isometry=delta_iso,
                modular_oscillation_nats=float(
                    geometry["exact_centered_modular_oscillation_nats"]
                ),
                relative_entropy_diameter_nats=float(
                    geometry["exact_relative_entropy_diameter_nats"]
                ),
                theorem_constant=FULL_CODE_CONSTANT,
            )
            rows.append(
                {
                    "G": stable_number(g_value),
                    "sector_count": f"2^{bit_exponent}",
                    "log_sector_count_nats": stable_number(log_sector_count),
                    "epsilon_FLM": stable_number(epsilon_flm),
                    "epsilon_tail": stable_number(epsilon_tail),
                    "epsilon_OD_nonperturbative_test": stable_number(epsilon_od),
                    "appendix_C_epsilon_iso_small_upper": stable_number(
                        epsilon_iso_small
                    ),
                    "lemma_4_delta_iso_large_upper": stable_number(delta_iso),
                    "source_eta_best_case_nats": stable_number(source_eta),
                    "delta_iso_times_log_sector_count": stable_number(
                        delta_iso * log_sector_count
                    ),
                    "flagged_channel_pairwise_defect_bound_nats": stable_number(
                        budget["flagged_channel_pairwise_defect_bound_nats"]
                    ),
                    "success_conditioned_trace_bound": stable_number(
                        budget["success_conditioned_trace_bound"]
                    ),
                }
            )
        asymptotic_rows = rows[-5:]
        results.append(
            {
                **scenario,
                "source_closed_wedge": wedge,
                "rows": rows,
                "fitted_last_five_log_log_slopes": {
                    "source_eta_vs_G": stable_number(
                        log_log_slope(
                            asymptotic_rows, "G", "source_eta_best_case_nats"
                        )
                    ),
                    "delta_log_K_vs_G": stable_number(
                        log_log_slope(
                            asymptotic_rows,
                            "G",
                            "delta_iso_times_log_sector_count",
                        )
                    ),
                    "flagged_defect_vs_G": stable_number(
                        log_log_slope(
                            asymptotic_rows,
                            "G",
                            "flagged_channel_pairwise_defect_bound_nats",
                        )
                    ),
                    "success_trace_vs_G": stable_number(
                        log_log_slope(
                            asymptotic_rows,
                            "G",
                            "success_conditioned_trace_bound",
                        )
                    ),
                },
            }
        )
    return {
        "source_chain": {
            "appendix_C": "Full-system approximate FLM implies eps_iso,small <= 2 sqrt(eps_FLM) after the source's optimal rescaling.",
            "lemma_4": "Large-code delta_iso <= eps_iso,small + eps_OD.",
            "combined": "delta_iso <= 2 sqrt(eps_FLM) + eps_OD; this requires a full-system FLM premise and cannot be inferred from a subregion estimate alone.",
        },
        "closed_exponential_sector_wedge": "For eps_FLM~G^a, eps_tail~G^t, K~exp(c/G^gamma), and nonperturbative eps_OD plus remaining Theorem-5 terms, this flagged sufficient route requires a>max(t,2 gamma). Its success-trace power is min((a-t)/4, a/4-gamma/2), up to logarithms.",
        "scenarios": results,
        "correction_to_rev0373": "The rev0373 b=gamma plateau remains a valid independent-isometry stress, but it is not the strongest source-closed branch when full-system FLM is available. Appendix C ties b to a/2 and can reopen the wedge when a>2 gamma.",
        "authority_boundary": "The schedule uses unit coefficients, a synthetic exp(-1/G) eps_OD, and zero for other nonperturbative source terms. It proves exponent bookkeeping only, not a physical CFT remainder.",
    }


def compute_result(root: Path) -> dict[str, Any]:
    manifest = json.loads((root / "RELEASE-MANIFEST.json").read_text())
    revision = manifest["revision"]
    schedules = {
        "inverse_resource_remainder": recovery_schedule(1.0),
        "inverse_square_resource_remainder": recovery_schedule(2.0),
    }
    rare_rows = rare_sector_rows()
    source_envelopes = large_code_source_envelopes()
    projected_join_budgets = projected_join_budget_rows(source_envelopes)
    exact_join_probe = exact_isometry_join_probe()
    isometry_stress = approximate_isometry_stress_rows()
    channel_premise_probe = normalized_filter_channel_premise_probe()
    flagged_completion_probe = flagged_channel_completion_probe(
        delta_isometry=ISOMETRY_STRESS_DELTA,
        theorem_constant=FULL_CODE_CONSTANT,
    )
    quantum_flagged_probe = noncommuting_flagged_channel_probe(
        delta_isometry=ISOMETRY_STRESS_DELTA,
    )
    flagged_target_budgets = flagged_target_budget_rows(
        target_trace_errors=TARGET_TRACE_ERRORS,
        theorem_constant=FULL_CODE_CONSTANT,
    )
    tail_wedge_rows = source_tail_wedge_rows()
    power_transfer_schedule = source_power_transfer_schedule(
        theorem_constant=FULL_CODE_CONSTANT
    )
    sector_growth = sector_proliferation_schedule()
    full_system_flm_closure = full_system_flm_closure_schedule()
    sector_transport = sector_transport_log_smoothness_probe(
        radii=SECTOR_TRANSPORT_RADII,
        gaussian_curvature=SECTOR_TRANSPORT_CURVATURE,
        leakage_probability=SECTOR_TRANSPORT_LEAKAGE,
    )
    operator_algebra = direct_sum_operator_algebra_probe()
    modular_rotation = noncommuting_modular_rotation_schedule()
    fixed_region_gluing = fixed_region_common_decoder_probe()
    source_routing = source_condition2_decoder_budget_probe()
    oaqec_completion = oaqec_reference_completion_probe()
    wedge_compatibility = state_dependent_wedge_probe()
    rare_slopes = {
        "reference_mixture_defect_bits": stable_number(
            log_log_slope(rare_rows, "sector_count", "reference_mixture_relative_entropy_defect_bits")
        ),
        "actual_reference_mixture_error": stable_number(
            log_log_slope(
                rare_rows,
                "sector_count",
                "actual_reference_mixture_recovery_trace_norm_error",
            )
        ),
        "invalid_laundered_uniform_bound": stable_number(
            log_log_slope(
                rare_rows,
                "sector_count",
                "invalid_uniform_bound_if_reference_mixture_defect_is_laundered",
            )
        ),
    }

    checks: list[dict[str, Any]] = []

    def add(check: str, passed: bool, detail: Any) -> None:
        checks.append({"check": check, "passed": bool(passed), "detail": detail})

    for label, exponent in (("inverse_resource_remainder", 1.0), ("inverse_square_resource_remainder", 2.0)):
        slopes = schedules[label]["fitted_log_log_slopes"]
        add(
            f"{label} preserves the declared relative-entropy exponent",
            abs(slopes["relative_entropy_defect"] + exponent) < TOLERANCE,
            slopes["relative_entropy_defect"],
        )
        add(
            f"{label} recovery trace guarantees carry the square-root exponent",
            abs(slopes["full_code_trace_norm"] + exponent / 2.0) < 0.002
            and abs(slopes["local_trace_norm"] + exponent / 2.0) < 0.002,
            {
                "local": slopes["local_trace_norm"],
                "full_code": slopes["full_code_trace_norm"],
            },
        )
        add(
            f"{label} squared-fidelity infidelity retains the remainder exponent",
            abs(slopes["squared_fidelity_infidelity"] + exponent) < 0.002,
            slopes["squared_fidelity_infidelity"],
        )

    add(
        "budget inversion exactly saturates the full-code theorem constant",
        all(
            abs(
                FULL_CODE_CONSTANT
                * math.sqrt(row["required_uniform_relative_entropy_defect_max"])
                - row["target_full_code_trace_or_normalized_observable_error"]
            )
            < 1e-12
            for row in budget_inversion_rows()
        ),
        stable_number(FULL_CODE_CONSTANT),
    )
    add(
        "rare-sector reference mixture defect and its actual state-specific error both converge as K^-1",
        abs(rare_slopes["reference_mixture_defect_bits"] + 1.0) < TOLERANCE
        and abs(rare_slopes["actual_reference_mixture_error"] + 1.0) < TOLERANCE,
        rare_slopes,
    )
    add(
        "laundered reference-mixture bound only falls as K^-1/2",
        abs(rare_slopes["invalid_laundered_uniform_bound"] + 0.5) < TOLERANCE,
        rare_slopes["invalid_laundered_uniform_bound"],
    )
    add(
        "rare-sector worst-case defect and recovery error remain order one",
        all(
            row["bad_sector_probe_relative_entropy_defect"] == 1.0
            and row["whole_domain_uniform_defect_lower_bound_from_probe"] == 1.0
            and row["actual_worst_case_recovery_trace_norm_error"] == 1.0
            for row in rare_rows
        ),
        {
            "relative_entropy_defect_lower_bound_bits": 1.0,
            "trace_norm_error": 1.0,
        },
    )
    first_invalid = next(
        (row for row in rare_rows if row["invalid_bound_below_actual_worst_case"]),
        None,
    )
    add(
        "average-to-uniform laundering becomes numerically self-contradictory",
        first_invalid is not None and first_invalid["sector_count"] == 16,
        first_invalid,
    )
    unit_probe_bits = UNIT_PROBE_NATS / math.log(2.0)
    unit_probe_fidelity_bits = 2.0 ** (-unit_probe_bits / 2.0)
    unit_probe_fidelity_nats = math.exp(-UNIT_PROBE_NATS / 2.0)
    add(
        "nats-to-bits conversion preserves the recovery fidelity exponent",
        abs(unit_probe_fidelity_bits - unit_probe_fidelity_nats) < TOLERANCE,
        {
            "defect_nats": UNIT_PROBE_NATS,
            "defect_bits": stable_number(unit_probe_bits),
            "fidelity_from_bits": stable_number(unit_probe_fidelity_bits),
            "fidelity_from_nats": stable_number(unit_probe_fidelity_nats),
        },
    )
    add(
        "large-code source envelopes remain norm- and quantifier-separated from epsilon_R",
        len(source_envelopes) == 3
        and all(not row["direct_uniform_pairwise_relative_entropy_input"] for row in source_envelopes),
        [row["source_result"] for row in source_envelopes],
    )
    add(
        "non-isometric normalized source map fails the quantum-channel affinity premise",
        not channel_premise_probe["is_quantum_channel_on_declared_convex_domain"]
        and abs(
            channel_premise_probe["affine_defect_trace_norm"] - ISOMETRY_STRESS_DELTA
        )
        < TOLERANCE,
        channel_premise_probe,
    )
    add(
        "polar correction decomposition closes exactly in the diagnostic cell",
        channel_premise_probe["polar_decomposition_identity_residual"] < TOLERANCE,
        channel_premise_probe,
    )
    add(
        "flagged completion is affine and preserves the normalized success state",
        flagged_completion_probe["flagged_channel_affine_residual"] < TOLERANCE
        and flagged_completion_probe["max_conditioned_success_state_residual"] < TOLERANCE,
        {
            "affine_residual": flagged_completion_probe["flagged_channel_affine_residual"],
            "success_state_residual": flagged_completion_probe["max_conditioned_success_state_residual"],
        },
    )
    add(
        "flagged block relative-entropy identity closes on every declared ordered pair",
        flagged_completion_probe["max_block_relative_entropy_identity_residual"] < TOLERANCE,
        flagged_completion_probe["max_block_relative_entropy_identity_residual"],
    )
    add(
        "flagged channel defect is bounded by normalized-map loss plus failure weight times domain diameter",
        flagged_completion_probe["max_actual_flagged_channel_information_loss_nats"]
        <= flagged_completion_probe["generic_bound_using_actual_normalized_loss"][
            "flagged_channel_pairwise_defect_bound_nats"
        ]
        + TOLERANCE,
        {
            "actual_flagged_loss_nats": flagged_completion_probe[
                "max_actual_flagged_channel_information_loss_nats"
            ],
            "generic_bound_nats": flagged_completion_probe[
                "generic_bound_using_actual_normalized_loss"
            ]["flagged_channel_pairwise_defect_bound_nats"],
        },
    )
    add(
        "source-residual flagged completion bound dominates the executable channel loss",
        flagged_completion_probe["max_actual_flagged_channel_information_loss_nats"]
        <= flagged_completion_probe["completion_budget"][
            "flagged_channel_pairwise_defect_bound_nats"
        ]
        + TOLERANCE,
        {
            "actual_flagged_loss_nats": flagged_completion_probe[
                "max_actual_flagged_channel_information_loss_nats"
            ],
            "source_residual_bound_nats": flagged_completion_probe[
                "completion_budget"
            ]["flagged_channel_pairwise_defect_bound_nats"],
        },
    )
    add(
        "noncommuting flagged completion is explicitly CPTP",
        quantum_flagged_probe["kraus_completeness_trace_norm_residual"] < TOLERANCE
        and quantum_flagged_probe["minimum_choi_eigenvalue"] >= -TOLERANCE
        and quantum_flagged_probe["maximum_output_trace_residual"] < TOLERANCE
        and quantum_flagged_probe["minimum_test_output_eigenvalue"] >= -TOLERANCE,
        {
            "kraus_completeness_residual": quantum_flagged_probe[
                "kraus_completeness_trace_norm_residual"
            ],
            "minimum_choi_eigenvalue": quantum_flagged_probe[
                "minimum_choi_eigenvalue"
            ],
            "maximum_output_trace_residual": quantum_flagged_probe[
                "maximum_output_trace_residual"
            ],
            "minimum_test_output_eigenvalue": quantum_flagged_probe[
                "minimum_test_output_eigenvalue"
            ],
        },
    )
    add(
        "noncommuting flagged completion preserves affinity, success states, and the quantum block identity",
        quantum_flagged_probe["affine_trace_norm_residual"] < TOLERANCE
        and quantum_flagged_probe[
            "maximum_conditioned_success_trace_norm_residual"
        ]
        < TOLERANCE
        and quantum_flagged_probe[
            "maximum_block_relative_entropy_identity_residual"
        ]
        < 1e-11,
        {
            "affine_residual": quantum_flagged_probe["affine_trace_norm_residual"],
            "success_state_residual": quantum_flagged_probe[
                "maximum_conditioned_success_trace_norm_residual"
            ],
            "block_identity_residual": quantum_flagged_probe[
                "maximum_block_relative_entropy_identity_residual"
            ],
        },
    )
    add(
        "noncommuting flagged defect obeys the generic domain-diameter bound",
        quantum_flagged_probe["maximum_flagged_channel_information_loss_nats"]
        <= quantum_flagged_probe["generic_flagged_defect_bound_nats"] + TOLERANCE,
        {
            "actual_flagged_loss_nats": quantum_flagged_probe[
                "maximum_flagged_channel_information_loss_nats"
            ],
            "generic_bound_nats": quantum_flagged_probe[
                "generic_flagged_defect_bound_nats"
            ],
        },
    )
    add(
        "exact-isometry projected-JLMS identity closes on every declared ordered pair",
        exact_join_probe["max_identity_residual"] < TOLERANCE,
        exact_join_probe,
    )
    add(
        "uniform projected residual supplies the exact-isometry two-eta pairwise bound",
        exact_join_probe["max_absolute_pairwise_relative_entropy_defect_nats"]
        <= exact_join_probe["two_eta_bound_nats"] + TOLERANCE,
        {
            "max_pairwise_defect_nats": exact_join_probe[
                "max_absolute_pairwise_relative_entropy_defect_nats"
            ],
            "two_eta_bound_nats": exact_join_probe["two_eta_bound_nats"],
        },
    )
    add(
        "approximate-isometry identity separates residual and normalization transport",
        all(row["identity_residual"] < TOLERANCE for row in isometry_stress),
        {
            "row_count": len(isometry_stress),
            "max_identity_residual": max(row["identity_residual"] for row in isometry_stress),
        },
    )
    add(
        "delta-isometry centered modular-oscillation correction bounds every stress row",
        all(row["corrected_bound_holds"] for row in isometry_stress),
        {
            "row_count": len(isometry_stress),
            "minimum_corrected_margin_nats": min(
                row["corrected_bound_nats"]
                - abs(row["actual_pairwise_relative_entropy_defect_nats"])
                for row in isometry_stress
            ),
        },
    )
    first_naive_failure = next((row for row in isometry_stress if row["naive_bound_violated"]), None)
    add(
        "omitting delta times centered modular oscillation becomes a false bound",
        first_naive_failure is not None
        and first_naive_failure["bulk_eigenvalue_floor"] == 1e-6,
        first_naive_failure,
    )
    add(
        "derived channelized projected-JLMS budgets include the two-reference and log-unit factors",
        all(
            abs(
                row["exact_channel_uniform_residual_budget_nats"]
                * 2.0
                / math.log(2.0)
                - row["required_uniform_pairwise_defect_bits"]
            )
            < TOLERANCE
            for row in projected_join_budgets
        ),
        {
            "target_count": len(projected_join_budgets),
            "tightest_exact_channel_residual_budget_nats": min(
                row["exact_channel_uniform_residual_budget_nats"]
                for row in projected_join_budgets
            ),
        },
    )
    add(
        "flagged target inversions saturate their declared success-conditioned trace targets",
        all(
            abs(
                row["saturated_success_conditioned_bound"]
                - row["target_success_conditioned_trace_error"]
            )
            < 1e-10
            for row in flagged_target_budgets
        ),
        {
            "row_count": len(flagged_target_budgets),
            "tightest_delta_iso_budget": min(
                row["max_delta_iso_if_eta_zero"] for row in flagged_target_budgets
            ),
        },
    )
    tail_by_name = {row["scenario"]: row for row in tail_wedge_rows}
    add(
        "source tail wedge closes at a=t and domain-diameter growth can erase isometry convergence",
        not tail_by_name["closed_at_tail_boundary"]["convergent_through_this_chain"]
        and not tail_by_name["domain_growth_erases_isometry_gain"][
            "convergent_through_this_chain"
        ]
        and tail_by_name["open_balanced"]["convergent_through_this_chain"],
        {
            name: {
                "defect_power": row["flagged_channel_defect_power_up_to_logs"],
                "trace_power": row["success_recovery_trace_power_up_to_logs"],
                "convergent": row["convergent_through_this_chain"],
            }
            for name, row in tail_by_name.items()
        },
    )
    transfer_slopes = power_transfer_schedule["fitted_asymptotic_log_log_slopes"]
    add(
        "synthetic source power transfer exhibits the double square-root loss",
        abs(transfer_slopes["epsilon_pJLMS_vs_G"] - 0.5) < 1e-5
        and abs(transfer_slopes["flagged_channel_defect_vs_G"] - 0.5) < 1e-5
        and abs(
            transfer_slopes["success_conditioned_trace_bound_vs_G"] - 0.25
        )
        < 1e-5,
        transfer_slopes,
    )
    domain_probe = sector_growth["exact_domain_geometry"]
    add(
        "exact reconstructed-algebra spectral-floor geometry closes on explicit extremizers",
        domain_probe["maximum_extremal_entropy_formula_residual"] < TOLERANCE
        and domain_probe["maximum_extremal_oscillation_formula_residual"] < TOLERANCE
        and domain_probe["maximum_overlap_grid_excess_above_exact_diameter"] <= TOLERANCE,
        {
            "entropy_formula_residual": domain_probe[
                "maximum_extremal_entropy_formula_residual"
            ],
            "oscillation_formula_residual": domain_probe[
                "maximum_extremal_oscillation_formula_residual"
            ],
            "overlap_grid_excess": domain_probe[
                "maximum_overlap_grid_excess_above_exact_diameter"
            ],
        },
    )
    sector_by_name = {
        row["scenario"]: row for row in sector_growth["scenarios"]
    }
    matched_exponential = sector_by_name[
        "exponential_sectors_power_matched_isometry"
    ]
    matched_polynomial = sector_by_name[
        "polynomial_sectors_power_matched_isometry"
    ]
    stronger_exponential = sector_by_name[
        "exponential_sectors_stronger_isometry"
    ]
    add(
        "exponential sector proliferation defeats vanishing local source errors at b=gamma=1",
        matched_exponential["first_to_last_ratios"]["source_eta"] < 0.01
        and abs(
            matched_exponential["fitted_last_five_log_log_slopes"][
                "flagged_defect_vs_G"
            ]
        )
        < 0.03
        and abs(
            matched_exponential["fitted_last_five_log_log_slopes"][
                "success_trace_vs_G"
            ]
        )
        < 0.03
        and matched_exponential["rows"][-1][
            "flagged_channel_pairwise_defect_bound_nats"
        ]
        > 1.0,
        {
            "ratios": matched_exponential["first_to_last_ratios"],
            "slopes": matched_exponential["fitted_last_five_log_log_slopes"],
            "last_row": matched_exponential["rows"][-1],
        },
    )
    add(
        "polynomial sector growth remains compatible with b=1 convergence through the same bridge",
        matched_polynomial["fitted_last_five_log_log_slopes"][
            "flagged_defect_vs_G"
        ]
        > 0.8
        and matched_polynomial["fitted_last_five_log_log_slopes"][
            "success_trace_vs_G"
        ]
        > 0.4
        and matched_polynomial["first_to_last_ratios"]["flagged_defect"] < 0.02
        and matched_polynomial["first_to_last_ratios"]["success_trace"] < 0.1,
        {
            "ratios": matched_polynomial["first_to_last_ratios"],
            "slopes": matched_polynomial["fitted_last_five_log_log_slopes"],
        },
    )
    add(
        "exponential sector growth requires isometry improvement faster than its exponent",
        0.95
        < stronger_exponential["fitted_last_five_log_log_slopes"][
            "flagged_defect_vs_G"
        ]
        < 1.06
        and 0.47
        < stronger_exponential["fitted_last_five_log_log_slopes"][
            "success_trace_vs_G"
        ]
        < 0.54
        and stronger_exponential["rows"][-1][
            "success_conditioned_trace_bound"
        ]
        < stronger_exponential["rows"][0]["success_conditioned_trace_bound"],
        {
            "ratios": stronger_exponential["first_to_last_ratios"],
            "slopes": stronger_exponential["fitted_last_five_log_log_slopes"],
        },
    )
    closure_by_name = {
        row["scenario"]: row for row in full_system_flm_closure["scenarios"]
    }
    closure_critical = closure_by_name[
        "full_system_FLM_critical_a_equals_2gamma"
    ]
    closure_a3 = closure_by_name["full_system_FLM_open_a_3"]
    closure_a5 = closure_by_name["full_system_FLM_open_a_5"]
    add(
        "Appendix-C and Lemma-4 isometry chain is propagated without an independent b assignment",
        all(
            abs(
                row["appendix_C_epsilon_iso_small_upper"]
                - 2.0 * math.sqrt(row["epsilon_FLM"])
            )
            < 1e-12
            and abs(
                row["lemma_4_delta_iso_large_upper"]
                - row["appendix_C_epsilon_iso_small_upper"]
                - row["epsilon_OD_nonperturbative_test"]
            )
            < 1e-12
            for scenario in full_system_flm_closure["scenarios"]
            for row in scenario["rows"]
        ),
        full_system_flm_closure["source_chain"],
    )
    add(
        "full-system FLM closes exactly at a=2 gamma and leaves the sector tax order one",
        not closure_critical["source_closed_wedge"]["sector_wedge_open"]
        and abs(
            closure_critical["fitted_last_five_log_log_slopes"][
                "flagged_defect_vs_G"
            ]
        )
        < 0.03
        and closure_critical["rows"][-1][
            "flagged_channel_pairwise_defect_bound_nats"
        ]
        > 1.0,
        {
            "wedge": closure_critical["source_closed_wedge"],
            "slopes": closure_critical["fitted_last_five_log_log_slopes"],
            "last_row": closure_critical["rows"][-1],
        },
    )
    add(
        "full-system FLM reopens exponential-sector convergence for a=3 and a=5",
        closure_a3["source_closed_wedge"]["convergent_through_this_chain"]
        and closure_a5["source_closed_wedge"]["convergent_through_this_chain"]
        and abs(
            closure_a3["fitted_last_five_log_log_slopes"][
                "flagged_defect_vs_G"
            ]
            - 0.5
        )
        < 0.03
        and abs(
            closure_a3["fitted_last_five_log_log_slopes"][
                "success_trace_vs_G"
            ]
            - 0.25
        )
        < 0.03
        and abs(
            closure_a5["fitted_last_five_log_log_slopes"][
                "flagged_defect_vs_G"
            ]
            - 1.5
        )
        < 0.03
        and abs(
            closure_a5["fitted_last_five_log_log_slopes"][
                "success_trace_vs_G"
            ]
            - 0.75
        )
        < 0.03,
        {
            "a3": closure_a3["fitted_last_five_log_log_slopes"],
            "a5": closure_a5["fitted_last_five_log_log_slopes"],
        },
    )
    transport_last = sector_transport["rows"][-1]
    add(
        "tiny trace leakage does not control global operator-log smoothness in Gaussian tails",
        transport_last["symmetric_distance_only_transport"][
            "maximum_per_source_off_diagonal_leakage"
        ]
        <= SECTOR_TRANSPORT_LEAKAGE
        and transport_last["symmetric_distance_only_transport"][
            "total_variation_between_p_and_Tp"
        ]
        < 1e-8
        and transport_last["symmetric_distance_only_transport"][
            "exact_log_smoothness_nats"
        ]
        > 80.0
        and abs(
            sector_transport[
                "asymptotic_symmetric_log_smoothness_slope_per_radius"
            ]
            - sector_transport["predicted_tail_slope_per_radius"]
        )
        < 2e-5,
        {
            "last_row": transport_last,
            "fitted_slope": sector_transport[
                "asymptotic_symmetric_log_smoothness_slope_per_radius"
            ],
        },
    )
    add(
        "p-stationary detailed-balance transport removes the commuting log-smoothness tax",
        all(
            row["p_stationary_metropolis_transport"][
                "exact_log_smoothness_nats"
            ]
            < 1e-12
            and row["p_stationary_metropolis_transport"][
                "normalization_residual"
            ]
            < TOLERANCE
            for row in sector_transport["rows"]
        ),
        {
            "maximum_log_smoothness_residual": max(
                row["p_stationary_metropolis_transport"][
                    "exact_log_smoothness_nats"
                ]
                for row in sector_transport["rows"]
            ),
            "constructive_completion": sector_transport[
                "constructive_completion"
            ],
        },
    )
    algebra_block = operator_algebra["noncommuting_block_decomposition_probe"]
    algebra_geometry = operator_algebra["exact_product_domain_geometry"]
    add(
        "direct-sum relative entropy separates a commutative center from genuinely noncommuting factor blocks",
        algebra_block["decomposition_residual"] < TOLERANCE
        and algebra_block["modular_block_decomposition_operator_norm_residual"] < 1e-11
        and min(algebra_block["factor_commutator_trace_norms"]) > 0.05,
        {
            "decomposition_residual": algebra_block["decomposition_residual"],
            "modular_block_residual": algebra_block["modular_block_decomposition_operator_norm_residual"],
            "factor_commutator_trace_norms": algebra_block["factor_commutator_trace_norms"],
        },
    )
    add(
        "full reconstructed-algebra domain taxes add center and factor contributions exactly in the declared product cell",
        algebra_geometry["diameter_identity_residual"] < TOLERANCE
        and algebra_geometry["oscillation_identity_residual"] < TOLERANCE
        and algebra_geometry["center_only_diameter_fraction"] < 0.6
        and algebra_geometry["center_only_oscillation_fraction"] < 0.6,
        {
            "diameter_residual": algebra_geometry["diameter_identity_residual"],
            "oscillation_residual": algebra_geometry["oscillation_identity_residual"],
            "center_only_diameter_fraction": algebra_geometry["center_only_diameter_fraction"],
            "center_only_oscillation_fraction": algebra_geometry["center_only_oscillation_fraction"],
        },
    )
    rotation_slopes = modular_rotation["fitted_last_six_log_log_slopes"]
    rotation_last = modular_rotation["rows"][-1]
    add(
        "vanishing state perturbation can leave order-one noncommuting operator-log error",
        modular_rotation["maximum_matrix_formula_residual_on_moderate_floor_rows"] < 1e-5
        and abs(rotation_slopes["adversarial_state_trace_vs_G"] - 1.0) < 1e-3
        and abs(rotation_slopes["adversarial_operator_log_vs_G"]) < 1e-3
        and rotation_last["adversarial_theta_equals_G"]["state_trace_norm_perturbation"] < 0.01
        and rotation_last["adversarial_theta_equals_G"]["operator_log_difference_norm_nats"] > 0.99,
        {"slopes": rotation_slopes, "final_row": rotation_last},
    )
    add(
        "a stronger modular-frame rotation schedule repairs the within-factor log-smoothness stress",
        abs(rotation_slopes["repaired_state_trace_vs_G"] - 2.0) < 1e-3
        and abs(rotation_slopes["repaired_operator_log_vs_G"] - 1.0) < 1e-3
        and rotation_last["repaired_theta_equals_G_squared"]["operator_log_difference_norm_nats"] < 0.01,
        {"slopes": rotation_slopes, "final_row": rotation_last},
    )
    fixed_oaqec = fixed_region_gluing["oaqec_erasure_commutant_checks"]
    fixed_decoders = fixed_region_gluing["single_fixed_region_decoders"]
    add(
        "fixed-region sector decoders glue into one exact direct-sum algebra channel when the coherent sector tag shares the carrier",
        fixed_region_gluing["encoding_isometry_operator_norm_residual"] < TOLERANCE
        and fixed_oaqec["direct_sum_algebra"]["maximum_commutant_operator_norm_residual"] < TOLERANCE
        and fixed_oaqec["full_subspace_algebra"]["maximum_commutant_operator_norm_residual"] < TOLERANCE
        and fixed_decoders["maximum_full_state_trace_norm_error"] < TOLERANCE
        and fixed_decoders["block_diagonal_state_trace_norm_error"] < TOLERANCE
        and fixed_decoders["maximum_direct_sum_algebra_expectation_residual"] < TOLERANCE,
        {
            "direct_sum_oaqec": fixed_oaqec["direct_sum_algebra"],
            "full_subspace_oaqec": fixed_oaqec["full_subspace_algebra"],
            "decoders": fixed_decoders,
        },
    )
    add(
        "direct-sum algebra recovery is not failed by licensed off-diagonal sector dephasing",
        abs(
            fixed_decoders[
                "cross_sector_coherent_state_trace_norm_error_after_algebraic_decoder"
            ]
            - 1.0
        )
        < TOLERANCE
        and fixed_decoders["maximum_direct_sum_algebra_expectation_residual"] < TOLERANCE
        and fixed_decoders["maximum_full_state_trace_norm_error"] < TOLERANCE,
        fixed_decoders,
    )
    sector_instrument = fixed_region_gluing["approximate_sector_instrument"]
    add(
        "worst-sector routing confusion enters the common algebra-decoder budget linearly as two p_max in trace norm",
        abs(sector_instrument["fitted_log_log_slope"] - 1.0) < TOLERANCE
        and all(
            abs(
                row["deterministic_sector_trace_norm_error"]
                - row["gluing_bound_epsilon_local_plus_disturbance_plus_2p"]
            )
            < TOLERANCE
            and abs(
                row["center_observable_expectation_error"]
                - row["gluing_bound_epsilon_local_plus_disturbance_plus_2p"]
            )
            < TOLERANCE
            for row in sector_instrument["rows"]
        ),
        {
            "slope": sector_instrument["fitted_log_log_slope"],
            "last_row": sector_instrument["rows"][-1],
        },
    )
    source_diagonal = source_routing["sector_diagonal_linear_budget"]
    add(
        "REF-0735 Condition-2 retained-block leakage gives a sharp linear sector-diagonal common-decoder budget",
        abs(source_diagonal["fitted_log_log_slope"] - 1.0) < TOLERANCE
        and all(
            row["source_subleading_trace_norm"]
            <= row["epsilon_sub_tr"] + TOLERANCE
            and row["bound_saturation_residual"] < TOLERANCE
            and abs(
                row["common_decoder_direct_sum_trace_norm_error"]
                - row["center_sign_expectation_error"]
            )
            < TOLERANCE
            for row in source_diagonal["rows"]
        ),
        {
            "slope": source_diagonal["fitted_log_log_slope"],
            "last_row": source_diagonal["rows"][-1],
        },
    )
    source_targets = source_routing["target_inversion"]["rows"]
    add(
        "Condition-2 target inversion distinguishes dominant-block certificates from full-sector certificates",
        all(
            abs(
                row["dominant_block_bound_at_budget"]
                - row["target_common_decoder_trace_norm_error"]
            )
            < TOLERANCE
            and abs(
                row["full_sector_transport_bound_at_budget"]
                - row["target_common_decoder_trace_norm_error"]
            )
            < TOLERANCE
            and row[
                "required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block"
            ]
            == 2.0
            * row[
                "required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state"
            ]
            for row in source_targets
        ),
        source_targets,
    )
    coherent_routing = source_routing["coherent_superposition_completion_stress"]
    environment_rows = coherent_routing["environment_tagged_rows"]
    carrier_rows = coherent_routing["carrier_frame_rows"]
    coherent_slopes = coherent_routing["fitted_log_log_slopes"]
    add(
        "Condition-1 epsilon_OD exactly pays the environment-tagged coherent-sector center bias in the owned two-sector cell",
        all(
            row["encoding_isometry_operator_norm_residual"] < TOLERANCE
            and row["condition2_residual"] < TOLERANCE
            and row["epsilon_OD_payment_residual"] < TOLERANCE
            for row in environment_rows
        )
        and 0.48
        < coherent_slopes[
            "environment_tagged_coherent_error_vs_epsilon_sub_tr"
        ]
        < 0.51
        and abs(
            coherent_slopes["environment_tagged_coherent_error_vs_epsilon_OD"]
            - 1.0
        )
        < TOLERANCE,
        {
            "slopes": coherent_slopes,
            "last_row": environment_rows[-1],
        },
    )
    add(
        "Condition-2 full trace-norm leakage itself pays the carrier-frame coherent bias when epsilon_OD vanishes",
        all(
            row["encoding_isometry_operator_norm_residual"] < TOLERANCE
            and row["condition2_formula_residual"] < TOLERANCE
            and row["epsilon_OD_zero_residual"] < TOLERANCE
            and row["coherent_error_below_epsilon_sub_tr"]
            for row in carrier_rows
        )
        and 0.98
        < coherent_slopes["carrier_frame_coherent_error_vs_epsilon_sub_tr"]
        < 1.01,
        {
            "slopes": coherent_slopes,
            "last_row": carrier_rows[-1],
        },
    )
    source_rare = source_routing["rare_sector_uniformity_negative_control"]
    add(
        "an average epsilon_sub-tr can converge as K^-1 while the worst-sector common-decoder obstruction remains fixed",
        abs(source_rare["average_slope_vs_sector_count"] + 1.0) < TOLERANCE
        and all(
            row["worst_sector_common_decoder_trace_norm_error"] == 0.2
            and row["bad_sector_epsilon_sub_tr"] == 0.1
            for row in source_rare["rows"]
        )
        and source_rare["rows"][-1][
            "invalid_bound_if_average_is_substituted_for_uniform_epsilon_sub_tr"
        ]
        < 1e-4,
        {
            "slope": source_rare["average_slope_vs_sector_count"],
            "last_row": source_rare["rows"][-1],
        },
    )
    oaqec_contract = oaqec_completion["theorem_contract"]
    oaqec_targets = oaqec_completion["state_to_diamond_conversion"][
        "target_inversion_rows"
    ]
    add(
        "Beny OAQEC target inversion preserves the square-root sufficient theorem and the code-dimension lift",
        all(
            abs(
                row["required_complementary_diamond_defect_max"]
                - row["target_oaqec_diamond_reconstruction_error"] ** 2 / 4.0
            )
            < TOLERANCE
            and abs(
                row[
                    "required_state_only_defect_max_under_generic_dimension_lift"
                ]
                * row["code_dimension"]
                - row["required_complementary_diamond_defect_max"]
            )
            < TOLERANCE
            for row in oaqec_targets
        ),
        {
            "contract": oaqec_contract["necessary_and_sufficient_bounds"],
            "tightest_state_only_budget": min(
                row[
                    "required_state_only_defect_max_under_generic_dimension_lift"
                ]
                for row in oaqec_targets
            ),
        },
    )
    reference_control = oaqec_completion[
        "reference_amplification_negative_control"
    ]
    reference_slopes = reference_control["fitted_last_six_log_log_slopes"]
    reference_last = reference_control["rows"][-1]
    add(
        "state-level off-diagonal convergence can coexist with order-one reference-assisted OAQEC obstruction",
        -1.01 < reference_slopes["state_envelope_vs_dimension"] < -0.98
        and abs(reference_slopes["diamond_defect_vs_dimension"]) < 0.01
        and abs(reference_slopes["reconstruction_lower_bound_vs_dimension"]) < 0.02
        and reference_last["uniform_state_trace_norm_envelope"] < 5e-4
        and reference_last["exact_reference_assisted_diamond_defect"] > 0.999
        and reference_last["beny_minimum_reconstruction_error_lower_bound"] > 0.249
        and reference_last["diamond_to_state_envelope_ratio"] > 2000.0,
        {"slopes": reference_slopes, "last_row": reference_last},
    )
    add(
        "transpose-dephasing defect diamond formula closes through independent Choi Jordan marginals",
        all(
            row["positive_input_marginal_operator_norm_residual"] < TOLERANCE
            and row["negative_input_marginal_operator_norm_residual"] < TOLERANCE
            and row["exact_formula_residual"] < TOLERANCE
            for row in reference_control["choi_jordan_audit_rows"]
        ),
        {
            "row_count": len(reference_control["choi_jordan_audit_rows"]),
            "maximum_formula_residual": max(
                row["exact_formula_residual"]
                for row in reference_control["choi_jordan_audit_rows"]
            ),
        },
    )
    erasure_control = oaqec_completion["erasure_channel_positive_control"]
    add(
        "erasure-channel positive control gives one common decoder with exact complementary-diamond scaling",
        erasure_control[
            "maximum_maximally_entangled_choi_formula_residual"
        ]
        < TOLERANCE
        and all(
            abs(
                row["exact_complementary_diamond_defect"]
                - row[
                    "exact_reconstruction_diamond_error_of_replace_on_erasure_decoder"
                ]
            )
            < TOLERANCE
            and row["beny_necessary_lower_bound"]
            <= row["exact_complementary_diamond_defect"] + TOLERANCE
            and row["exact_complementary_diamond_defect"]
            <= row["beny_sufficient_upper_bound"] + TOLERANCE
            for row in erasure_control["rows"]
        ),
        {
            "choi_formula_residual": erasure_control[
                "maximum_maximally_entangled_choi_formula_residual"
            ],
            "row_count": len(erasure_control["rows"]),
        },
    )
    rate_scenarios = {
        row["scenario"]: row
        for row in oaqec_completion["large_code_reference_rate_wedge"][
            "scenarios"
        ]
    }
    add(
        "nonperturbative state error pays the reference dimension only when its exponential rate is stronger",
        rate_scenarios["insufficient_state_rate"]["small_G_outcome"]
        == "vacuous"
        and rate_scenarios["critical_rate_plateau"]["small_G_outcome"]
        == "plateau"
        and rate_scenarios["reference_stable_rate"]["small_G_outcome"]
        == "convergent"
        and rate_scenarios["insufficient_state_rate"]["rows"][-1][
            "generic_complementary_diamond_upper_bound"
        ]
        == 2.0
        and rate_scenarios["critical_rate_plateau"]["rows"][-1][
            "generic_complementary_diamond_upper_bound"
        ]
        == 1.0
        and rate_scenarios["reference_stable_rate"]["rows"][-1][
            "generic_complementary_diamond_upper_bound"
        ]
        < 2e-7,
        {
            name: scenario["rows"][-1]
            for name, scenario in rate_scenarios.items()
        },
    )
    hidden_frame = fixed_region_gluing["hidden_sector_frame_negative_control"]
    add(
        "discarding the sector tag leaves a linear common-decoder frame-mismatch obstruction despite exact sector-conditioned decoders",
        all(
            row["physical_output_identity_residual"] < TOLERANCE
            and row["any_common_decoder_minimax_trace_norm_lower_bound"] > 0.0
            and row["any_common_decoder_minimax_trace_norm_lower_bound"]
            <= row["midpoint_unitary_decoder_worst_case_upper_bound"] + TOLERANCE
            and row["sector_conditioned_decoder_error"] == 0.0
            for row in hidden_frame["rows"]
        )
        and 0.97
        < hidden_frame["fitted_log_log_slopes"][
            "minimax_lower_bound_vs_frame_separation"
        ]
        < 1.01
        and 0.97
        < hidden_frame["fitted_log_log_slopes"][
            "midpoint_upper_bound_vs_frame_separation"
        ]
        < 1.01,
        {
            "slopes": hidden_frame["fitted_log_log_slopes"],
            "last_row": hidden_frame["rows"][-1],
        },
    )
    wedge_fixed = wedge_compatibility["no_single_fixed_region_negative_control"]
    wedge_adaptive = wedge_compatibility["adaptive_region_choice_target_split"]
    wedge_union = wedge_compatibility["fixed_union_region_positive_control"]
    add(
        "sector-wise exact reconstruction does not imply one fixed-region decoder",
        wedge_compatibility["encoding_isometry_operator_norm_residual"] < TOLERANCE
        and wedge_compatibility["sector_local_reconstruction"]["maximum_sector_local_trace_norm_error"] < TOLERANCE
        and wedge_fixed["AC_output_distance_for_sector_1_orthogonal_logical_pair"] < TOLERANCE
        and wedge_fixed["BC_output_distance_for_sector_0_orthogonal_logical_pair"] < TOLERANCE
        and abs(wedge_fixed["exact_pair_minimax_recovery_trace_error_lower_bound"] - 1.0) < TOLERANCE
        and abs(wedge_fixed["constant_maximally_mixed_decoder_attains_pair_error"] - 1.0) < TOLERANCE,
        wedge_fixed,
    )
    add(
        "adaptive wedge routing recovers the direct-sum algebra but destroys cross-sector coherence unless it is quotiented out",
        wedge_adaptive["block_diagonal_operator_algebra_error"] < TOLERANCE
        and abs(wedge_adaptive["cross_sector_coherent_state_trace_norm_error"] - 1.0) < TOLERANCE
        and wedge_union["arbitrary_coherent_code_state_trace_norm_error"] < TOLERANCE
        and wedge_compatibility["oaqec_erasure_commutant_checks"]["ABC_direct_sum_algebra"]["maximum_commutant_operator_norm_residual"] < TOLERANCE,
        {"adaptive": wedge_adaptive, "fixed_union": wedge_union},
    )
    add(
        "toy dimension and physical finite-N resource remain explicitly unmapped",
        True,
        "No D=N, D=1/G, central-charge, area, or bond-dimension substitution is evaluated.",
    )

    failures = [check["check"] for check in checks if not check["passed"]]
    first_schedule = schedules["inverse_resource_remainder"]
    return {
        "artifact_id": "FAMILYC-JLMS-RECOVERY-BUDGET-BENCHMARK",
        "revision": revision,
        "route_id": ROUTE_ID,
        "decision_experiment_id": DECISION_ID,
        "epistemic_status": "owned theorem-translation and quantifier-stress cell; route-local S3 pressure only",
        "authority_cap": "S3",
        "scientific_question": "When does the large-code projected-JLMS and subsystem-orthogonality package imply one reference-stable recovery channel for the source's fixed-region direct-sum wedge algebra, after paying channelization, center/factor geometry, retained-block routing, coherent-sector contamination, and the code/reference dimension needed to lift state-level errors into complementary-channel diamond norm?",
        "source_refs": SOURCE_REFS,
        "theorem_contract": {
            "required_input": "A genuine quantum channel N plus an absolute bulk-output relative-entropy defect at most epsilon_R for every ordered pair rho,sigma in the declared convex state domain.",
            "relative_entropy_units": "epsilon_R is expressed in bits (base-2 logarithms), matching the stated theorem constant; a remainder in nats must be divided by ln 2 before use.",
            "root_fidelity_guarantee": "F(rho, R o N[rho]) >= 2^(-epsilon_R/2) for the universal recovery construction on the local channel.",
            "local_trace_norm_guarantee": "||rho - R o N[rho]||_1 <= 2 sqrt(1-2^(-epsilon_R)); the simpler published bound is <= 2 sqrt(epsilon_R).",
            "full_code_trace_and_observable_guarantee": f"For arbitrary code states under the theorem assumptions, delta <= (2+sqrt(2 ln 2)) sqrt(epsilon_R) = {stable_number(FULL_CODE_CONSTANT)} sqrt(epsilon_R).",
            "quantifier_boundary": "A mean over sectors, a sampled pair set, one fiducial/reference mixture, an expectation over states, or a nonlinear normalized filter is not the required channel-plus-supremum contract.",
        },
        "projected_jlms_to_pairwise_join": {
            "source_result": "REF-0735, Theorem 5, Eq. (4.85)",
            "residual_definition": "J_rho = V^dagger K_{W(rho)_R} V - M (A/4G + K_{rho_r}), with M=V^dagger V and z_sigma=Tr(M sigma).",
            "exact_identity": "D(W(sigma)_R || W(rho)_R) - D(sigma_r || rho_r) = z_sigma^-1 Tr[sigma (J_rho-J_sigma)] + Tr[sigma (M/z_sigma-I)(K_{rho_r}-K_{sigma_r})]. The area operator cancels between J_rho and J_sigma.",
            "exact_isometry_channel_corollary": "If M=I (or M is scalar and V is rescaled), W is a genuine channel. If ||J_rho||_infinity <= eta for every reference rho in the declared domain, its all-ordered-pairs defect is at most 2 eta in the same logarithm units and may enter the recovery theorem after unit conversion.",
            "approximate_normalized_map_corollary": "If ||M-I||_infinity <= delta_iso < 1 and L_K^osc = sup_{rho,sigma} inf_c ||K_{rho_r}-K_{sigma_r}-cI||_infinity, then the normalized map W obeys epsilon_pair,nats <= 2(eta + delta_iso L_K^osc)/(1-delta_iso). This is not yet a recovery-theorem input because W is generally nonlinear.",
            "polar_channelization_identity": "Let U=V M^(-1/2), N_U(rho)=Tr_complement[U rho U^dagger], H_rho=A/4G+K_{rho_r}, and J^U_rho=U^dagger K_{N_U(rho)_R} U-H_rho. Then J^U_rho=M^(-1/2)J^V_rho M^(-1/2)+U^dagger(K_{N_U(rho)_R}-K_{W_V(rho)_R})U+(M^(1/2)H_rho M^(-1/2)-H_rho).",
            "conditional_channelized_bound": "If the last two terms are uniformly bounded by chi_out and chi_bulk, then ||J^U_rho|| <= eta/(1-delta_iso)+chi_out+chi_bulk and the genuine polar channel has epsilon_pair,nats <= 2[eta/(1-delta_iso)+chi_out+chi_bulk].",
            "flagged_channel_completion": "Set alpha=(1+delta_iso)^-1 and define Phi(rho)=alpha V rho V^dagger on an orthogonal success block plus Tr[(I-alpha V^dagger V)rho]|fail><fail|. Phi is CPTP, p_rho lies in [(1-delta_iso)/(1+delta_iso),1], and its conditioned success state is exactly W_V(rho).",
            "flagged_channel_relative_entropy_identity": "D(Phi(sigma)||Phi(rho)) = p_sigma D(W_V(sigma)||W_V(rho)) + D_Ber(p_sigma||p_rho).",
            "flagged_channel_defect_bound": "If the declared reduced bulk-wedge/reconstructed-algebra domain has D(sigma_r||rho_r)<=D_max, then epsilon_flag,nats <= 2(eta+delta_iso L_K^osc)/(1-delta_iso) + [2 delta_iso/(1+delta_iso)] D_max.",
            "success_conditioned_decoder_transfer": "If a recovery channel for Phi has trace/normalized-observable bound T_flag, its restriction to the success block obeys T_success <= (T_flag+2 q_max)/p_min = [(1+delta_iso)T_flag+4 delta_iso]/(1-delta_iso). This yields one decoder on the source normalized success states without identifying W_V itself as a channel.",
            "load_bearing_quantifiers": [
                "Theorem 5 must hold with one uniform eta for every reference rho, not merely one smooth fiducial state.",
                "The probe sigma and reference rho must range over the identical declared state domain.",
                "Approximate normalized-map control requires delta_iso and finite centered modular oscillation L_K^osc; delta_iso already appearing inside eta does not remove the normalization-transport term.",
                "Recovery additionally requires channelization. The source's normalized map is nonlinear unless M is scalar. Polar channelization needs chi_out and chi_bulk; the flagged completion instead needs a finite same-domain relative-entropy diameter D_max and pays its failure probability explicitly.",
                "The orthogonal failure flag is an auxiliary proof completion, not an asserted CFT degree of freedom. The physical-output consequence is only the restricted decoder on the original success block, and it inherits the explicit success-conditioning cost.",
                "D_max and L_K^osc must be computed on the reduced bulk-wedge/reconstructed algebra appearing in the JLMS comparison; a full-code diameter or a within-sector floor is not a substitute.",
                "Theorem-5 log-smoothness has a commutative center component governed by relative incoming sector flux. Tiny per-sector trace leakage, Gaussian weights, or distance-only overlap decay do not bound it without a p-weighted transport theorem.",
                "Center control is not full-algebra control. The within-sector noncommuting factor blocks require their own spectral-floor/dimension and modular-frame transport bounds on the same reconstructed algebra.",
                "REF-0735 Definition 6 already fixes one G-independent boundary-region pair across all small-code sectors and makes the reduced wedge state block diagonal in a direct-sum algebra. Do not charge that source with a region switch or with preservation of off-diagonal sector coherence. The remaining decoder debt is one CPTP recovery on that fixed region with uniform worst-sector control; full-Hilbert coherence is a separate stronger target.",
                "The logarithm base of eta, L_K^osc, D_max, chi_out, and chi_bulk must be declared before conversion to the recovery theorem's epsilon_R.",
            ],
            "exact_isometry_numeric_probe": exact_join_probe,
            "channel_premise_and_polar_correction_probe": channel_premise_probe,
            "flagged_channel_completion_probe": flagged_completion_probe,
            "noncommuting_flagged_channel_probe": quantum_flagged_probe,
            "flagged_success_target_budgets": flagged_target_budgets,
            "reconstructed_algebra_domain_geometry": domain_probe,
            "approximate_isometry_spectral_stress": {
                "model": "Two-level diagonal non-isometric encoder with M=diag(1+delta,1-delta), normalized nonlinear boundary map W, sigma=(1/2,1/2), and references approaching a spectral edge.",
                "rows": isometry_stress,
                "severe_failure": "At fixed delta_iso=1e-3 the projected residual eta stays near 2e-3 nats, but the omitted normalization term grows with centered bulk modular oscillation. The naive residual-only normalized-map bound first fails at lambda_min=1e-6 and worsens as the spectral floor falls.",
                "correction": "A finite-N normalized-map claim must budget eta, delta_iso, and L_K^osc together. A recovery claim may pay polar transport chi_out+chi_bulk, or use the explicit flagged channel and pay q_max D_max plus the success-conditioning transfer. Small isometry error alone is neither a state-uniform nor a channel-level guarantee.",
            },
        },
        "unit_conversion_probe": {
            "defect_nats": UNIT_PROBE_NATS,
            "defect_bits_after_dividing_by_ln2": stable_number(unit_probe_bits),
            "root_fidelity_from_bit_formula": stable_number(unit_probe_fidelity_bits),
            "root_fidelity_from_natural_exponential": stable_number(unit_probe_fidelity_nats),
            "interpretation": "A source remainder in nats must be divided by ln 2 before entering the base-2 theorem contract; the two fidelity evaluations then agree exactly up to floating-point tolerance.",
        },
        "large_code_source_error_envelopes": {
            "source_ref": "REF-0735",
            "envelopes": source_envelopes,
            "derived_projected_join_budgets": projected_join_budgets,
            "flagged_success_target_budgets": flagged_target_budgets,
            "source_tail_power_wedge": {
                "equation_3_17": "eps_pJLMS = sqrt(eps_FLM/eps_tail) + eps_iso_small |log eps_tail|, up to suppressed O(1) factors",
                "equation_4_24": "eps_iso = eps_iso_small + eps_OD",
                "scenario_rows": tail_wedge_rows,
                "synthetic_exponent_transfer": power_transfer_schedule,
                "severe_failure": "Choosing eps_tail to vanish at least as fast as eps_FLM closes the displayed source ratio: for eps_FLM~G^a and eps_tail~G^t, a<=t gives no vanishing sqrt(eps_FLM/eps_tail). Even when a>t, growth of the same-domain relative-entropy diameter or modular oscillation can erase the delta_iso gain before recovery.",
                "conditional_exponent": "If non-displayed source terms are nonperturbative, eps_iso_small~G^b, D_max~G^-d, and L_K^osc~G^-ell, then the flagged-channel defect power is min((a-t)/2,b,b-d,b-ell) up to logarithms, and the success-conditioned trace guarantee carries half that power.",
            },
            "hard_boundary": "Theorem 5's symbolic sum becomes a normalized-map pairwise defect only under uniform reference-state coverage. It becomes a recovery-channel input in the exact/scalar case, after paid polar transport, or through the explicit flagged completion with a finite same-domain D_max. The rows are theorem budgets and symbolic power transfers, not measured or derived numerical eta(G,N), delta(G,N), D_max(G,N), or L_K(G,N) laws.",
        },
        "operational_scaling_schedules": schedules,
        "key_scaling_finding": {
            "finding": "A base-2 relative-entropy/JLMS remainder epsilon_R=O(R^-p) guarantees only O(R^-p/2) full-code trace-norm and normalized-observable accuracy through this theorem, while squared-fidelity infidelity remains O(R^-p). When epsilon_R itself inherits the source term sqrt(eps_FLM/eps_tail), recovery introduces a second square root: eps_FLM~G^a and eps_tail~G^t contribute only G^((a-t)/4) trace accuracy before other errors and domain growth.",
            "inverse_resource_example": {
                "remainder_slope": first_schedule["fitted_log_log_slopes"]["relative_entropy_defect"],
                "full_code_trace_slope": first_schedule["fitted_log_log_slopes"]["full_code_trace_norm"],
                "squared_fidelity_infidelity_slope": first_schedule["fitted_log_log_slopes"]["squared_fidelity_infidelity"],
            },
            "correction": "Do not transfer a quoted O(1/N) JLMS remainder directly into O(1/N) reconstruction error. Also do not read eps_FLM's power directly as a reconstruction power: Eq. (3.17)'s tail ratio and universal recovery can halve the exponent twice, while D_max or L_K^osc growth can remove convergence altogether.",
        },
        "target_budget_inversion": {
            "constant": stable_number(FULL_CODE_CONSTANT),
            "rows": budget_inversion_rows(),
            "interpretation": "These rows are the quantitative hurdle a future finite-N calculation must clear. They are conditional on a uniform defect over the declared state domain, not a statement that holography supplies the listed epsilon_R.",
        },
        "sector_proliferation_domain_negative_control": sector_growth,
        "full_system_flm_isometry_closure": full_system_flm_closure,
        "sector_transport_log_smoothness": sector_transport,
        "operator_algebra_center_factor_audit": operator_algebra,
        "noncommuting_modular_frame_stress": modular_rotation,
        "fixed_region_direct_sum_decoder_gluing": fixed_region_gluing,
        "source_condition2_decoder_routing": source_routing,
        "oaqec_reference_completion": oaqec_completion,
        "state_dependent_wedge_compatibility": wedge_compatibility,
        "rare_sector_negative_control": {
            "model": "A classical direct-sum code has K labeled sectors. K-1 sectors transmit a logical bit exactly; one rare sector replaces it by the uniform bit. The sector label is retained. The reference mixture is uniform over sectors.",
            "pair_used_for_defect": "Within each sector compare a deterministic logical bit with the uniform logical-bit reference, using base-2 relative entropy. The bad sector loses 1 bit; exact sectors lose zero.",
            "rows": rare_rows,
            "fitted_log_log_slopes": rare_slopes,
            "severe_failure": "The uniform reference mixture reports a base-2 defect 1/K and genuine state-specific recovery error 1/K, but a declared bad-sector probe witnesses a 1-bit defect and the channel has minimax trace-norm recovery error 1 on deterministic bit inputs. Thus any whole-domain uniform defect is at least 1 bit. Feeding the reference-mixture defect into the whole-code theorem produces a purported upper bound below the actual worst-case starting at K=16; the contradiction identifies a quantifier violation, not a theorem failure.",
            "correction": "Every finite-N/JLMS remainder entering a recovery claim must state its quantifier: supremum over a declared domain, state-class bound, weighted average, sample estimate, or single-reference result. Only the first supports a whole-domain universal-recovery guarantee without an additional concentration or coverage theorem.",
        },
        "large_code_source_bridge": {
            "completed_here": [
                "A direct algebraic join from a uniform projected-JLMS operator-norm residual to the all-pairs relative-entropy defect of the source's normalized map: 2 eta for exact isometry and 2(eta+delta_iso L_K^osc)/(1-delta_iso) for controlled approximate normalization.",
                "A channel-premise audit proving that the normalized non-isometric source map is non-affine, so its pairwise bound cannot be spent directly in a universal-recovery theorem.",
                "A constructive CPTP flagged completion that preserves the source normalized state exactly on success and replaces free polar-transport symbols by an explicit failure budget q_max D_max; both diagonal and noncommuting Kraus/Choi probes now replay the construction.",
                "A decoder-transfer inequality from the auxiliary flagged channel back to one decoder on the original normalized success states: T_success <= [(1+delta_iso)T_flag+4 delta_iso]/(1-delta_iso).",
                "An exact finite-dimensional formula for the reduced reconstructed-algebra relative-entropy diameter and centered modular oscillation under a spectral floor, verified on explicit extremizers.",
                "An executable direct-sum sector-growth stress showing that exponentially proliferating sector weights can keep the recovery budget order one even while every displayed local source remainder vanishes.",
                "A source-grounded optional closure using Appendix C and Lemma 4: full-system FLM gives eps_iso,small <= 2 sqrt(eps_FLM), so the exponential-sector sufficient wedge sharpens to a>max(t,2 gamma) when the other source terms are nonperturbative.",
                "An exact classical-center log-smoothness identity and transport stress: fixed 1e-8 nearest-neighbor leakage yields more than 80 nats of operator-log error in Gaussian tails, while p-stationary detailed balance removes the center tax at the same sector count.",
                "An exact direct-sum operator-algebra decomposition showing that D_max and L_K^osc contain additive commutative-center and noncommuting factor-block debts; in the declared product cell the center alone pays less than half of either total.",
                "A noncommuting modular-frame stress where trace-norm state error vanishes as G but operator-log error remains one nat, plus a G^2 rotation control that restores convergence.",
                "An exact fixed-region OAQEC gluing cell: orthogonal sector tags plus sector-conditioned frames admit one common direct-sum algebra decoder with zero commutant residual; algebraic dephasing has unit full-state coherence error but zero algebra-observable error. A worst-sector confusion channel saturates the 2 p_max trace-norm budget, while hiding the sector tag creates a linear frame-mismatch obstruction.",
                "A source-conditioned routing sublemma from REF-0735 Definition 7: on sector-diagonal/direct-sum inputs, epsilon_common <= epsilon_block + 2 epsilon_sub-tr/(1-epsilon_iso,small), with an owned family that exactly saturates the bound and an inverted target budget. A decoder certified only on the full sector output pays the looser 4 epsilon_sub-tr/(1-epsilon_iso,small) transport chain.",
                "Two exact-isometry coherent-sector cells separating the source roles: an environment-tagged cell where the block-instrument error scales as sqrt(epsilon_sub-tr) but equals epsilon_OD, and a carrier-frame cell where epsilon_OD=0 while the full Condition-2 trace-norm term itself pays the coherent bias. A rare-sector cell keeps the alpha-independent supremum distinct from a vanishing 1/K average.",
                "A reference-stable OAQEC completion using REF-0736: delta_A=||Nhat-Nhat o P_{A'}||_diamond obeys delta_A^2/4<=E_A<=2 sqrt(delta_A), with target inversion delta_A<=tau^2/4 and the generic state-to-diamond lift delta_A<=d_code epsilon_state. A transpose-dephasing channel family makes epsilon_state fall as 1/d while delta_A tends to one and E_A stays at least 1/4; an erasure-channel control gives an exact common decoder with delta_A=E_A=2p(1-1/d^2).",
                "A generic state-dependent-wedge comparator whose OAQEC commutant residual is one on either sector-local region and zero on the union; it is now explicitly quarantined from REF-0735, which fixes the same boundary region across sectors.",
                "An executable source-tail wedge from Eqs. (3.17) and (4.24), exposing the conditional double-square-root exponent loss and the possibility that state-domain growth destroys convergence.",
                "Rare-sector, spectral-floor, and sector-proliferation counterexamples separating state averages, small source residuals, approximate normalization, and uncontrolled domains from whole-domain recovery.",
            ],
            "source_conditioning": "Theorem 5 is a direct recovery bridge only when V^dagger V is scalar on the declared code domain. Otherwise it controls a nonlinear normalized map. The flagged completion supplies a genuine theorem channel and a decoder on the original success outputs after restriction, but no physical CFT flag is asserted. Full-system FLM can pay the isometry exponent through Appendix C and Lemma 4; subregion FLM alone cannot. REF-0735 fixes one boundary-region pair and a direct-sum reduced wedge algebra. Condition 2 pays a sharp worst-sector sector-diagonal routing budget, while Condition 1 epsilon_OD and the full Condition-2 trace term have distinct coherent-sector roles. Neither state-level parameter is yet the REF-0736 complementary-channel diamond defect: whole-code authority requires a direct cb/diamond estimate or an explicit code/reference dimension law strong enough to pay d_code epsilon_state, on the same channel, region, target algebra, and state domain as the center/factor and decoder budgets.",
            "still_missing": [
                "Derive physical scaling laws and hidden constants for full-system and subregion eps_FLM, eps_tail, eps_OD, eps_enhanced, eps_sub_log, and the resulting eta on one identical region/state domain; verify that the Appendix-C full-system premise actually holds with the needed error.",
                "Prove that every reference state in that domain satisfies enhanced log-stability and log-smoothness with uniform source parameters; one preferred reference state is insufficient.",
                "Derive the same-domain sector-count/sector-weight law, or direct D_max and L_K^osc bounds, for the reduced bulk-wedge/reconstructed algebra. Under the full-system FLM branch and K~exp(c/G^gamma), this sufficient route requires eps_FLM=o(G^(2 gamma)).",
                "Derive a sector-confusion/overlap kernel or equivalent weighted-inflow bound proving max_alpha |(T p)_alpha/p_alpha-1| is uniformly small. Unweighted eps_sub_tr, a Gaussian p_alpha, and distance-only decay are insufficient.",
                "Derive within-sector factor dimension/spectral-floor laws and a noncommuting modular-frame transport bound strong enough that eigenbasis rotation times the factor log-condition number vanishes uniformly.",
                "Derive physical same-domain scaling for the alpha-independent epsilon_sub-tr and epsilon_iso,small that clears the new sector-diagonal target inversion, and certify the sector decoders on the normalized dominant blocks rather than only on full sector outputs.",
                "Derive a same-domain complementary-channel defect Delta=Nhat-Nhat o P_{A'} from epsilon_OD, epsilon_sub-tr, approximate isometry, and sector-support data, and control it in diamond/cb norm with an external reference. The owned cells show that the two source errors are not interchangeable, while the new channel family shows that even a uniform unassisted state error can vanish as 1/d_code with order-one diamond defect.",
                "Provide the physical code/reference dimension or a dimension-free complete-boundedness theorem. Under only the generic lift, a target OAQEC error tau requires epsilon_state<=tau^2/(4 d_code); for d_code~exp(s/G^gamma) and epsilon_state~exp(-c/G^gamma), the sufficient reference-stable wedge needs c>s.",
                "Stress backreaction, non-AdS transport, and local-observer records after the algebra and fixed-region debts close.",
            ],
        },
        "resource_identity_audit": {
            "owned_toy_resource": "prime logical/local dimension D in FAMILYC-APPROXIMATE-RECOVERY-SCALING-BENCHMARK.json",
            "conditional_bridge_resource": "abstract resource R used only to expose theorem exponents and target budgets",
            "physical_source_resources": "G, CFT N/central charge, area-window width, code-subspace/state-class data, and source-specific error parameters",
            "identity_status": "unmapped",
            "forbidden_shortcuts": [
                "D=N",
                "D=1/G",
                "D=central charge",
                "D=bond dimension",
                "an operator-norm modular-Hamiltonian remainder equals a uniform pairwise relative-entropy defect without proof",
                "a nonlinear normalized non-isometric map is a quantum channel",
                "the source eps_iso term automatically pays polar output-modular or bulk-similarity transport",
                "the flagged completion removes the need to declare same-domain reduced-algebra D_max and L_K^osc",
                "the auxiliary failure flag is a physical CFT boundary degree of freedom or a postselection resource supplied by the source",
                "a power assigned to eps_FLM transfers unchanged through eps_pJLMS and recovery",
                "a within-sector spectral floor controls the direct-sum sector weights",
                "vanishing local source errors imply whole-large-code recovery without a sector-growth law",
                "Gaussian sector weights plus a small distance-only leakage norm imply global log-smoothness",
                "p-stationary center transport controls the noncommuting factor-block modular frame",
                "center-only D_max or L_K^osc equals the full reconstructed-algebra tax",
                "sector-wise exact decoders imply one fixed-region decoder",
                "adaptive region selection preserves cross-sector coherence without declaring a target-algebra quotient",
                "off-diagonal sector coherence is automatically part of a direct-sum wedge algebra",
                "REF-0735 uses a different boundary carrier region for each small-code sector",
                "an average sector-confusion rate substitutes for a worst-sector common-decoder bound",
                "epsilon_OD alone pays retained-region Condition-2 routing",
                "epsilon_sub-tr alone gives a linear whole-code coherent-superposition decoder bound",
                "a state-uniform trace-norm off-diagonal bound is already a complementary-channel diamond/cb bound",
                "nonperturbative epsilon_OD beats nonperturbative code/reference growth without comparing their rates",
                "an average or unassisted entanglement-fidelity metric substitutes for worst-reference diamond error",
                "a decoder certificate on the full sector output is automatically a certificate on the normalized dominant block",
                "a sector-weighted mean replaces Definition 7's alpha-independent epsilon_sub-tr",
                "the Appendix-C isometry bound follows from a subregion FLM estimate without a separate full-system premise",
                "a state average equals a whole-code supremum",
            ],
        },
        "acceptance_checks": checks,
        "validation_failures": failures,
        "hard_limits": [
            "No numerical physical finite-N, G, central-charge, area, or tensor-network scaling is derived or fitted. The source-tail rows propagate declared symbolic powers only.",
            "The resource schedules, flagged target inversions, full-system-FLM closure rows, and source-power schedule are conditional theorem test vectors, not holographic data.",
            "The binary-channel, non-affinity, polar-correction, flagged-completion, Kraus/Choi, direct-sum factor, modular-rotation, fixed-region gluing, source-routing, coherent-sector, reference-amplification, erasure, wedge-switching, and spectral-floor cells verify joins and failure modes; they are not models of AdS/CFT dynamics.",
            "The failure flag is an auxiliary proof-device output. This revision claims only the decoder obtained by restricting the theorem recovery map to the original success block; it does not claim the source supplies a physical flag or free postselection.",
            "The sector-weight, center-transport, factor-frame, sector-confusion, wedge-switching, and rare-sector schedules are theorem stress tests, not physical fits or models of AdS/CFT dynamics. The Metropolis kernel, coherent controlled decoder, and fixed-union decoder are mathematical controls, not claimed gravitational mechanisms.",
            "The full-code constant is a sufficient theorem bound and need not be optimal.",
            "Passing the benchmark creates no acquired evidence, observed-sector recovery, public-record closure, or route promotion.",
        ],
        "next_kernel_step": "On REF-0735's fixed region, construct the actual complementary defect Delta=Nhat-Nhat o P_{A'} for the declared direct-sum algebra and derive either a uniform diamond/cb bound directly or a state-to-diamond lift with explicit d_code/reference growth. Insert the same-domain epsilon_OD, epsilon_sub-tr, approximate-isometry, dominant-block decoder, center/factor geometry, and FLM/JLMS errors; test the new tau^2/(4 d_code) budget and the c>s rate wedge; then compare the resulting genuine OAQEC error with the owned complementary-channel benchmark without identifying computational D with physical N.",
    }


def render_markdown(result: dict[str, Any]) -> str:
    p1 = result["operational_scaling_schedules"]["inverse_resource_remainder"]
    p2 = result["operational_scaling_schedules"]["inverse_square_resource_remainder"]
    rare = result["rare_sector_negative_control"]
    sector_growth = result["sector_proliferation_domain_negative_control"]
    flm_closure = result["full_system_flm_isometry_closure"]
    sector_transport = result["sector_transport_log_smoothness"]
    operator_algebra = result["operator_algebra_center_factor_audit"]
    modular_rotation = result["noncommuting_modular_frame_stress"]
    fixed_region = result["fixed_region_direct_sum_decoder_gluing"]
    source_routing = result["source_condition2_decoder_routing"]
    oaqec_completion = result["oaqec_reference_completion"]
    wedge_compatibility = result["state_dependent_wedge_compatibility"]
    domain_geometry = sector_growth["exact_domain_geometry"]
    finding = result["key_scaling_finding"]
    join = result["projected_jlms_to_pairwise_join"]
    exact = join["exact_isometry_numeric_probe"]
    channel = join["channel_premise_and_polar_correction_probe"]
    flagged = join["flagged_channel_completion_probe"]
    quantum_flagged = join["noncommuting_flagged_channel_probe"]
    spectral = join["approximate_isometry_spectral_stress"]
    source_envelopes = result["large_code_source_error_envelopes"]
    tail_wedge = source_envelopes["source_tail_power_wedge"]
    theorem5 = next(
        row
        for row in source_envelopes["envelopes"]
        if row["result_kind"] == "projected_JLMS_log_smooth_operator_norm"
    )
    lines = [
        "# Family-C JLMS-to-recovery budget benchmark (generated)",
        "",
        "This cell audits the full source-to-recovery chain. It distinguishes (1) an operator-norm projected-JLMS residual, (2) a pairwise relative-entropy bound for the source's normalized map, and (3) the stronger channel-level hypothesis required by universal recovery. It does **not** invent a physical finite-`N` remainder.",
        "",
        f"- Route: `{result['route_id']}`",
        f"- Decision experiment: `{result['decision_experiment_id']}`",
        f"- Status: {result['epistemic_status']}",
        "- Replay: `python3 tools/familyc_jlms_recovery_budget_benchmark.py --check`",
        f"- Validation failures: `{len(result['validation_failures'])}`",
        "",
        "## Recovery theorem contract",
        "",
        "The load-bearing input is a **genuine quantum channel** and an absolute relative-entropy defect bounded for every ordered pair in one declared convex state domain. A state average, one reference mixture, or a nonlinear normalized filter is not that premise.",
        "",
        f"For a valid base-2 defect `epsilon_R`, root fidelity is at least `2^(-epsilon_R/2)` and the arbitrary-code-state trace/normalized-observable guarantee used here is `{result['target_budget_inversion']['constant']} sqrt(epsilon_R)`.",
        "",
        "### Unit conversion probe",
        "",
        f"A `{result['unit_conversion_probe']['defect_nats']}`-nat defect becomes `{result['unit_conversion_probe']['defect_bits_after_dividing_by_ln2']}` bits. The base-2 and natural-exponential fidelity evaluations both give `{result['unit_conversion_probe']['root_fidelity_from_bit_formula']}`.",
        "",
        "## Source envelopes and the exact algebraic join",
        "",
        "REF-0735 supplies three distinct envelopes. None is silently renamed a recovery-theorem defect.",
        "",
        "| Source result | Symbolic envelope | Norm / state quantifier | Direct channel input? |",
        "|---|---|---|---:|",
    ]
    for envelope in result["large_code_source_error_envelopes"]["envelopes"]:
        lines.append(
            "| `{source}` | `{expr}` | {quantifier} | `{direct}` |".format(
                source=envelope["source_result"],
                expr=envelope["symbolic_error_envelope"],
                quantifier=envelope["norm_and_quantifier"].replace("|", "\\|"),
                direct=str(envelope["direct_uniform_pairwise_relative_entropy_input"]).lower(),
            )
        )
    decomposition = theorem5["source_error_decomposition"]
    lines += [
        "",
        "The source's displayed small-code inputs are now kept explicit rather than compressed into an unexplained `eta`:",
        "",
        f"- Eq. (3.17): `{decomposition['epsilon_pJLMS_equation_3_17']}`",
        f"- Eq. (4.24): `{decomposition['epsilon_iso_equation_4_24']}`",
        f"- Appendix-C branch: {decomposition['appendix_C_full_system_branch']}",
        f"- Power boundary: {decomposition['power_counting_boundary']}",
        "",
        f"Residual: `{join['residual_definition']}`",
        "",
        f"Exact identity: `{join['exact_identity']}`",
        "",
        f"Exact/scalar-norm corollary: {join['exact_isometry_channel_corollary']}",
        "",
        "### Exact-isometry executable probe",
        "",
        f"The `{exact['model']}` checks `{exact['declared_state_grid_size']}` states. Its maximum identity residual is `{exact['max_identity_residual']}`; maximum pairwise defect is `{exact['max_absolute_pairwise_relative_entropy_defect_nats']}` nats against the valid `2 eta` bound `{exact['two_eta_bound_nats']}` nats.",
        "",
        "## Severe channel-premise failure and correction",
        "",
        "The source explicitly normalizes a non-isometric linear map. Unless `M=V^dagger V` is scalar on the domain, that normalization is nonlinear and therefore is not a quantum channel.",
        "",
        f"In the owned midpoint probe, `delta_iso={channel['delta_isometry']}` and the affine defect is `{channel['affine_defect_trace_norm']}` in trace norm. Channel status: `{str(channel['is_quantum_channel_on_declared_convex_domain']).lower()}`.",
        "",
        "**Correction:** the approximate normalized-map defect cannot be fed directly into universal recovery. Use exact/scalar norm, or channelize explicitly.",
        "",
        "### Polar channelization",
        "",
        f"`{join['polar_channelization_identity']}`",
        "",
        f"Conditional bound: `{join['conditional_channelized_bound']}`",
        "",
        f"The diagnostic polar cell closes with residual `{channel['polar_decomposition_identity_residual']}`. It also shows why source `eta` cannot be spent alone: the transformed source term is cancelled by an output-modular transport term in this toy, and that cancellation is not encoded in the scalar source bound.",
        "",
        "### Flagged channel completion: constructive path without free transport symbols",
        "",
        f"`{join['flagged_channel_completion']}`",
        "",
        f"Block identity: `{join['flagged_channel_relative_entropy_identity']}`",
        "",
        f"Channel defect: `{join['flagged_channel_defect_bound']}`",
        "",
        f"Success decoder transfer: `{join['success_conditioned_decoder_transfer']}`",
        "",
        f"The executable `{flagged['model']}` checks `{flagged['declared_state_count']}` states. Affinity residual is `{flagged['flagged_channel_affine_residual']}` and the conditioned-success state residual is `{flagged['max_conditioned_success_state_residual']}`. The exact block-relative-entropy identity closes to `{flagged['max_block_relative_entropy_identity_residual']}`.",
        "",
        f"Its actual maximum flagged-channel information loss is `{flagged['max_actual_flagged_channel_information_loss_nats']}` nats. The generic bound using the measured normalized-map loss is `{flagged['generic_bound_using_actual_normalized_loss']['flagged_channel_pairwise_defect_bound_nats']}` nats; the source-residual bound is `{flagged['completion_budget']['flagged_channel_pairwise_defect_bound_nats']}` nats. The resulting success-conditioned theorem bound is `{flagged['completion_budget']['success_conditioned_trace_bound']}`.",
        "",
        "#### Noncommuting Kraus / Choi audit",
        "",
        f"The `{quantum_flagged['model']}` uses `{quantum_flagged['kraus_operator_count']}` explicit Kraus operators. Kraus-completeness residual is `{quantum_flagged['kraus_completeness_trace_norm_residual']}`, the minimum Choi eigenvalue is `{quantum_flagged['minimum_choi_eigenvalue']}`, and maximum output-trace residual is `{quantum_flagged['maximum_output_trace_residual']}`.",
        "",
        f"On `{quantum_flagged['declared_state_count']}` noncommuting full-rank states, the affine residual is `{quantum_flagged['affine_trace_norm_residual']}`, conditioned-success residual is `{quantum_flagged['maximum_conditioned_success_trace_norm_residual']}`, and the quantum block-relative-entropy identity closes to `{quantum_flagged['maximum_block_relative_entropy_identity_residual']}`. Actual flagged information loss `{quantum_flagged['maximum_flagged_channel_information_loss_nats']}` nats is below the generic domain-diameter bound `{quantum_flagged['generic_flagged_defect_bound_nats']}` nats.",
        "",
        f"**Proof-device boundary:** {quantum_flagged['proof_device_boundary']}",
        "",
        "#### Isometry budgets after success conditioning (`eta=0`)",
        "",
        "These inversions isolate the isometry/domain cost. They are conditional theorem requirements, not estimates of physical `delta_iso`.",
        "",
        "| spectral floor | target success trace error | max delta_iso | D_max (nats) | L_K^osc (nats) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in join["flagged_success_target_budgets"]:
        if row["target_success_conditioned_trace_error"] not in {0.1, 0.01}:
            continue
        lines.append(
            "| `{floor}` | `{target}` | `{delta}` | `{diameter}` | `{osc}` |".format(
                floor=row["reference_spectral_floor"],
                target=row["target_success_conditioned_trace_error"],
                delta=row["max_delta_iso_if_eta_zero"],
                diameter=row["exact_relative_entropy_diameter_nats"],
                osc=row["exact_centered_modular_oscillation_nats"],
            )
        )
    lines += [
        "",
        "## Approximate-normalization spectral stress",
        "",
        f"{join['approximate_normalized_map_corollary']}",
        "",
        "| bulk eigenvalue floor | eta (nats) | centered modular oscillation | actual defect | naive eta-only bound | corrected normalized-map bound | naive violated? |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in spectral["rows"]:
        lines.append(
            "| `{floor}` | `{eta}` | `{lk}` | `{actual}` | `{naive}` | `{corrected}` | `{violated}` |".format(
                floor=row["bulk_eigenvalue_floor"],
                eta=row["uniform_residual_eta_nats_on_declared_three-state_domain"],
                lk=row["bulk_modular_oscillation_LK_nats"],
                actual=row["actual_pairwise_relative_entropy_defect_nats"],
                naive=row["naive_bound_omitting_delta_LK_nats"],
                corrected=row["corrected_bound_nats"],
                violated=str(row["naive_bound_violated"]).lower(),
            )
        )
    lines += [
        "",
        f"**Severe failure:** {spectral['severe_failure']}",
        "",
        f"**Correction:** {spectral['correction']}",
        "",
        "## Polar-channel comparison budgets",
        "",
        "These legacy comparison rows retain the polar admissible region. The flagged completion above is now the constructive default because it replaces unpriced transport symbols with explicit failure/domain costs.",
        "",
        "| target trace/observable error | required pairwise defect (bits) | exact-channel residual budget (nats) | max source eta if polar transport vanishes at delta=1e-3 | max chi_out+chi_bulk if eta=0 |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in result["large_code_source_error_envelopes"]["derived_projected_join_budgets"]:
        lines.append(
            "| `{target}` | `{epsilon}` | `{budget}` | `{eta}` | `{chi}` |".format(
                target=row["target_full_code_trace_or_observable_error"],
                epsilon=row["required_uniform_pairwise_defect_bits"],
                budget=row["exact_channel_uniform_residual_budget_nats"],
                eta=row["source_eta_max_if_polar_transport_zero_at_delta_1e_minus_3"],
                chi=row["polar_transport_chi_out_plus_chi_bulk_max_if_eta_zero_nats"],
            )
        )
    lines += [
        "",
        "## Scaling consequence after a valid channel join",
        "",
        finding["finding"],
        "",
        "| Conditional channel-level remainder | defect slope | squared-fidelity infidelity slope | local trace slope | full-code trace/observable slope |",
        "|---|---:|---:|---:|---:|",
        f"| `{p1['declared_remainder_rule']}` | `{p1['fitted_log_log_slopes']['relative_entropy_defect']}` | `{p1['fitted_log_log_slopes']['squared_fidelity_infidelity']}` | `{p1['fitted_log_log_slopes']['local_trace_norm']}` | `{p1['fitted_log_log_slopes']['full_code_trace_norm']}` |",
        f"| `{p2['declared_remainder_rule']}` | `{p2['fitted_log_log_slopes']['relative_entropy_defect']}` | `{p2['fitted_log_log_slopes']['squared_fidelity_infidelity']}` | `{p2['fitted_log_log_slopes']['local_trace_norm']}` | `{p2['fitted_log_log_slopes']['full_code_trace_norm']}` |",
        "",
        f"**Correction:** {finding['correction']}",
        "",
        "## Source-tail and growing-domain exponent wedge",
        "",
        f"Eq. (3.17): `{tail_wedge['equation_3_17']}`",
        "",
        f"Conditional transfer: {tail_wedge['conditional_exponent']}",
        "",
        "| scenario | a | t | b | D growth d | L growth ell | flagged-defect power | success-trace power | convergent? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in tail_wedge["scenario_rows"]:
        lines.append(
            "| `{scenario}` | `{a}` | `{t}` | `{b}` | `{d}` | `{ell}` | `{defect}` | `{trace}` | `{convergent}` |".format(
                scenario=row["scenario"],
                a=row["flm_power_a"],
                t=row["tail_power_t"],
                b=row["small_isometry_power_b"],
                d=row["domain_diameter_growth_power_d"],
                ell=row["modular_oscillation_growth_power_ell"],
                defect=row["flagged_channel_defect_power_up_to_logs"],
                trace=row["success_recovery_trace_power_up_to_logs"],
                convergent=str(row["convergent_through_this_chain"]).lower(),
            )
        )
    transfer = tail_wedge["synthetic_exponent_transfer"]
    slopes = transfer["fitted_asymptotic_log_log_slopes"]
    lines += [
        "",
        f"**Severe failure:** {tail_wedge['severe_failure']}",
        "",
        f"The synthetic `eps_FLM=G^2`, `eps_tail=G`, `eps_iso_small=G` transfer fits slopes `{slopes['epsilon_pJLMS_vs_G']}` for `eps_pJLMS`, `{slopes['flagged_channel_defect_vs_G']}` for the flagged defect, and `{slopes['success_conditioned_trace_bound_vs_G']}` for success-conditioned trace error. This is the executable double-square-root loss `G^(1/2) -> G^(1/4)`, not a physical fit.",
        "",
        "## Exact reconstructed-algebra geometry",
        "",
        "The JLMS comparison uses reduced bulk-wedge states. For the full-rank domain `rho >= lambda I` in dimension `d`, the benchmark now computes the exact domain taxes rather than inserting an ad hoc `-log lambda` upper bound:",
        "",
        f"- `{domain_geometry['exact_formulas']['relative_entropy_diameter']}`",
        f"- `{domain_geometry['exact_formulas']['centered_modular_oscillation']}`",
        "",
        "| dimension | floor | maximum eigenvalue | exact D_max (nats) | extremizer replay | exact L_K^osc (nats) | extremizer replay |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in domain_geometry["rows"]:
        lines.append(
            "| `{dimension}` | `{floor}` | `{maximum}` | `{diameter}` | `{direct_d}` | `{osc}` | `{direct_l}` |".format(
                dimension=row["dimension"],
                floor=row["eigenvalue_floor"],
                maximum=row["maximum_eigenvalue"],
                diameter=row["exact_relative_entropy_diameter_nats"],
                direct_d=row["extremal_pair_relative_entropy_nats"],
                osc=row["exact_centered_modular_oscillation_nats"],
                direct_l=row["extremal_pair_centered_modular_oscillation_nats"],
            )
        )
    lines += [
        "",
        f"Formula residuals: relative entropy `{domain_geometry['maximum_extremal_entropy_formula_residual']}`; centered modular oscillation `{domain_geometry['maximum_extremal_oscillation_formula_residual']}`.",
        "",
        "## Direct-sum sector-proliferation negative control",
        "",
        sector_growth["model"],
        "",
        "At fixed total sector floor mass `mu=0.1`, both exact domain taxes grow as `Theta(log K)`. A within-sector `eps_tail` therefore does not control the classical center of the large direct sum.",
        "",
        "| scenario | sector law | final source eta | final D_max | final flagged defect | defect slope vs G | final success trace | trace slope vs G |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in sector_growth["scenarios"]:
        last = scenario["rows"][-1]
        scenario_slopes = scenario["fitted_last_five_log_log_slopes"]
        lines.append(
            "| `{scenario}` | `{rule}` | `{eta}` | `{diameter}` | `{defect}` | `{defect_slope}` | `{trace}` | `{trace_slope}` |".format(
                scenario=scenario["scenario"],
                rule=scenario["sector_rule"],
                eta=last["source_eta_nats"],
                diameter=last["exact_bulk_wedge_relative_entropy_diameter_nats"],
                defect=last["flagged_channel_pairwise_defect_bound_nats"],
                defect_slope=scenario_slopes["flagged_defect_vs_G"],
                trace=last["success_conditioned_trace_bound"],
                trace_slope=scenario_slopes["success_trace_vs_G"],
            )
        )
    matched = next(
        item
        for item in sector_growth["scenarios"]
        if item["scenario"] == "exponential_sectors_power_matched_isometry"
    )
    lines += [
        "",
        "### Power-matched exponential-sector replay",
        "",
        "| G | K | source eta | exact D_max | exact L_K^osc | flagged defect | success trace bound |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    selected_sector_rows = {0, 4, len(matched["rows"]) - 1}
    for index, row in enumerate(matched["rows"]):
        if index not in selected_sector_rows:
            continue
        lines.append(
            "| `{g}` | `{k}` | `{eta}` | `{diameter}` | `{osc}` | `{defect}` | `{trace}` |".format(
                g=row["G"],
                k=row["sector_count"],
                eta=row["source_eta_nats"],
                diameter=row["exact_bulk_wedge_relative_entropy_diameter_nats"],
                osc=row["exact_bulk_wedge_centered_modular_oscillation_nats"],
                defect=row["flagged_channel_pairwise_defect_bound_nats"],
                trace=row["success_conditioned_trace_bound"],
            )
        )
    lines += [
        "",
        f"**Severe failure:** {sector_growth['severe_failure']}",
        "",
        f"**Correction:** {sector_growth['correction']}",
        "",
        f"**Authority boundary:** {sector_growth['authority_boundary']}",
        "",
        "## Source-grounded full-system FLM isometry closure",
        "",
        flm_closure["source_chain"]["combined"],
        "",
        flm_closure["closed_exponential_sector_wedge"],
        "",
        "| scenario | a | t | gamma | derived b=a/2 | defect power | fitted defect slope | trace power | fitted trace slope | convergent? |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in flm_closure["scenarios"]:
        wedge = scenario["source_closed_wedge"]
        scenario_slopes = scenario["fitted_last_five_log_log_slopes"]
        lines.append(
            "| `{scenario}` | `{a}` | `{t}` | `{gamma}` | `{b}` | `{defect}` | `{defect_fit}` | `{trace}` | `{trace_fit}` | `{convergent}` |".format(
                scenario=scenario["scenario"],
                a=wedge["flm_power_a"],
                t=wedge["tail_power_t"],
                gamma=wedge["exponential_sector_power_gamma"],
                b=wedge["derived_small_isometry_power_b"],
                defect=wedge["flagged_channel_defect_power_up_to_logs"],
                defect_fit=scenario_slopes["flagged_defect_vs_G"],
                trace=wedge["success_recovery_trace_power_up_to_logs"],
                trace_fit=scenario_slopes["success_trace_vs_G"],
                convergent=str(wedge["convergent_through_this_chain"]).lower(),
            )
        )
    lines += [
        "",
        f"**Correction to the prior stress:** {flm_closure['correction_to_rev0373']}",
        "",
        f"**Authority boundary:** {flm_closure['authority_boundary']}",
        "",
        "## Sector-transport log-smoothness audit",
        "",
        sector_transport["commuting_identity"],
        "",
        sector_transport["relative_stationarity_condition"],
        "",
        "| radius L | sectors | symmetric leakage | total variation | symmetric eps_l-smooth (nats) | p-stationary eps_l-smooth (nats) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sector_transport["rows"]:
        symmetric = row["symmetric_distance_only_transport"]
        stationary = row["p_stationary_metropolis_transport"]
        lines.append(
            "| `{radius}` | `{count}` | `{leak}` | `{tv}` | `{bad}` | `{good}` |".format(
                radius=row["radius"],
                count=row["sector_count"],
                leak=symmetric["maximum_per_source_off_diagonal_leakage"],
                tv=symmetric["total_variation_between_p_and_Tp"],
                bad=symmetric["exact_log_smoothness_nats"],
                good=stationary["exact_log_smoothness_nats"],
            )
        )
    lines += [
        "",
        f"The bad-tail fitted slope is `{sector_transport['asymptotic_symmetric_log_smoothness_slope_per_radius']}` nats per radius against the exact asymptotic prediction `{sector_transport['predicted_tail_slope_per_radius']}`.",
        "",
        f"**Severe failure:** {sector_transport['severe_failure']}",
        "",
        f"**Constructive completion:** {sector_transport['constructive_completion']}",
        "",
        "## Direct-sum operator-algebra center/factor audit",
        "",
        operator_algebra["algebra"],
        "",
        f"**Terminology correction:** {operator_algebra['terminology_correction']}",
        "",
    ]
    algebra_block = operator_algebra["noncommuting_block_decomposition_probe"]
    algebra_geometry = operator_algebra["exact_product_domain_geometry"]
    lines += [
        "| full relative entropy | center contribution | weighted factor contribution | decomposition residual | factor commutator trace norms |",
        "|---:|---:|---:|---:|---|",
        "| `{full}` | `{center}` | `{factor}` | `{residual}` | `{commutators}` |".format(
            full=algebra_block["full_relative_entropy_nats"],
            center=algebra_block["classical_center_relative_entropy_nats"],
            factor=algebra_block["weighted_factor_relative_entropy_nats"],
            residual=algebra_block["decomposition_residual"],
            commutators=algebra_block["factor_commutator_trace_norms"],
        ),
        "",
        algebra_block["identity"],
        "",
        "| domain tax | center | factor | full predicted | full observed | residual | center-only fraction |",
        "|---|---:|---:|---:|---:|---:|---:|",
        "| relative-entropy diameter | `{center}` | `{factor}` | `{predicted}` | `{observed}` | `{residual}` | `{fraction}` |".format(
            center=algebra_geometry["center_relative_entropy_diameter_nats"],
            factor=algebra_geometry["factor_relative_entropy_diameter_nats"],
            predicted=algebra_geometry["predicted_full_relative_entropy_diameter_nats"],
            observed=algebra_geometry["observed_full_relative_entropy_diameter_nats"],
            residual=algebra_geometry["diameter_identity_residual"],
            fraction=algebra_geometry["center_only_diameter_fraction"],
        ),
        "| centered modular oscillation | `{center}` | `{factor}` | `{predicted}` | `{observed}` | `{residual}` | `{fraction}` |".format(
            center=algebra_geometry["center_centered_modular_oscillation_nats"],
            factor=algebra_geometry["factor_centered_modular_oscillation_nats"],
            predicted=algebra_geometry["predicted_full_centered_modular_oscillation_nats"],
            observed=algebra_geometry["observed_full_centered_modular_oscillation_nats"],
            residual=algebra_geometry["oscillation_identity_residual"],
            fraction=algebra_geometry["center_only_oscillation_fraction"],
        ),
        "",
        f"**Correction:** {operator_algebra['correction']}",
        "",
        "## Noncommuting modular-frame stress",
        "",
        modular_rotation["model"],
        "",
        "| G | adversarial state trace error (theta=G) | adversarial operator-log error | repaired state error (theta=G^2) | repaired operator-log error |",
        "|---:|---:|---:|---:|---:|",
    ]
    selected_rotation_rows = {0, 4, len(modular_rotation["rows"]) - 1}
    for index, row in enumerate(modular_rotation["rows"]):
        if index not in selected_rotation_rows:
            continue
        adversarial = row["adversarial_theta_equals_G"]
        repaired = row["repaired_theta_equals_G_squared"]
        lines.append(
            "| `{g}` | `{a_state}` | `{a_log}` | `{r_state}` | `{r_log}` |".format(
                g=row["G"],
                a_state=adversarial["state_trace_norm_perturbation"],
                a_log=adversarial["operator_log_difference_norm_nats"],
                r_state=repaired["state_trace_norm_perturbation"],
                r_log=repaired["operator_log_difference_norm_nats"],
            )
        )
    lines += [
        "",
        f"Fitted last-six slopes: `{modular_rotation['fitted_last_six_log_log_slopes']}`.",
        "",
        f"**Severe failure:** {modular_rotation['severe_failure']}",
        "",
        f"**Constructive control:** {modular_rotation['constructive_control']}",
        "",
        "## Fixed-region direct-sum decoder gluing",
        "",
        fixed_region["model"],
        "",
        "The source-specific correction is load-bearing: REF-0735 already fixes one boundary-region pair across sectors and its wedge state is block diagonal in the direct-sum algebra. The relevant debt is therefore one fixed-region CPTP decoder with worst-sector control—not an invented region switch or an automatic demand for off-diagonal sector coherence.",
        "",
    ]
    fixed_direct = fixed_region["oaqec_erasure_commutant_checks"]["direct_sum_algebra"]
    fixed_full = fixed_region["oaqec_erasure_commutant_checks"]["full_subspace_algebra"]
    fixed_decoders = fixed_region["single_fixed_region_decoders"]
    lines += [
        "| exact fixed-region check | direct-sum algebra | full-subspace algebra / coherent target |",
        "|---|---:|---:|",
        f"| OAQEC commutant residual | `{fixed_direct['maximum_commutant_operator_norm_residual']}` | `{fixed_full['maximum_commutant_operator_norm_residual']}` |",
        f"| Kraus completeness residual | `{fixed_direct['kraus_completeness_operator_norm_residual']}` | `{fixed_full['kraus_completeness_operator_norm_residual']}` |",
        "",
        "| one fixed-region decoder test | result |",
        "|---|---:|",
        f"| coherent controlled-decoder full-state error | `{fixed_decoders['maximum_full_state_trace_norm_error']}` |",
        f"| algebra decoder block-state error | `{fixed_decoders['block_diagonal_state_trace_norm_error']}` |",
        f"| direct-sum algebra expectation residual | `{fixed_decoders['maximum_direct_sum_algebra_expectation_residual']}` |",
        f"| algebra-decoder cross-sector coherence error | `{fixed_decoders['cross_sector_coherent_state_trace_norm_error_after_algebraic_decoder']}` |",
        "",
        fixed_decoders["target_interpretation"],
        "",
        "### Approximate sector-instrument budget",
        "",
        fixed_region["approximate_sector_instrument"]["generic_trace_norm_bound"],
        "",
        "| worst-sector confusion p | state trace error | center-observable error | gluing bound |",
        "|---:|---:|---:|---:|",
    ]
    confusion_rows = fixed_region["approximate_sector_instrument"]["rows"]
    for index in (0, 3, len(confusion_rows) - 1):
        row = confusion_rows[index]
        lines.append(
            "| `{p}` | `{state}` | `{center}` | `{bound}` |".format(
                p=row["worst_sector_misrouting_probability"],
                state=row["deterministic_sector_trace_norm_error"],
                center=row["center_observable_expectation_error"],
                bound=row["gluing_bound_epsilon_local_plus_disturbance_plus_2p"],
            )
        )
    lines += [
        "",
        f"Fitted confusion-error slope: `{fixed_region['approximate_sector_instrument']['fitted_log_log_slope']}`.",
        "",
        "### REF-0735 Condition-2 routing translation",
        "",
        source_routing["source_contract"]["condition2"],
        "",
        source_routing["source_contract"]["block_certified_common_decoder"],
        "",
        source_routing["source_contract"]["full_sector_certificate_conversion"],
        "",
        "| epsilon_sub-tr | normalized wrong-block probability | common-decoder error | sharp bound |",
        "|---:|---:|---:|---:|",
    ]
    source_diagonal_rows = source_routing["sector_diagonal_linear_budget"]["rows"]
    for index in (0, 3, len(source_diagonal_rows) - 1):
        row = source_diagonal_rows[index]
        lines.append(
            "| `{epsilon}` | `{wrong}` | `{error}` | `{bound}` |".format(
                epsilon=row["epsilon_sub_tr"],
                wrong=row["normalized_wrong_block_probability"],
                error=row["common_decoder_direct_sum_trace_norm_error"],
                bound=row["condition2_linear_bound"],
            )
        )
    lines += [
        "",
        f"Fitted source-routing slope: `{source_routing['sector_diagonal_linear_budget']['fitted_log_log_slope']}`.",
        "",
        "The target inversion is operational: a decoder certified on the dominant block buys twice the source `epsilon_sub-tr` budget of a certificate stated only on the full sector output under this conservative transport chain.",
        "",
        "| target common-decoder error | epsilon_sub-tr max, dominant-block certificate | epsilon_sub-tr max, full-sector certificate |",
        "|---:|---:|---:|",
    ]
    for row in source_routing["target_inversion"]["rows"]:
        if row["target_common_decoder_trace_norm_error"] not in (0.1, 0.05, 0.01):
            continue
        lines.append(
            "| `{target}` | `{block}` | `{full}` |".format(
                target=row["target_common_decoder_trace_norm_error"],
                block=row[
                    "required_epsilon_sub_tr_max_if_decoder_is_certified_on_dominant_block"
                ],
                full=row[
                    "required_epsilon_sub_tr_max_if_decoder_is_only_certified_on_full_sector_state"
                ],
            )
        )
    coherent_source = source_routing["coherent_superposition_completion_stress"]
    lines += [
        "",
        "### Coherent-sector completion split",
        "",
        coherent_source["environment_tagged_interpretation"],
        "",
        "| wrong mass r | epsilon_sub-tr | epsilon_OD | block-instrument center error |",
        "|---:|---:|---:|---:|",
    ]
    environment_rows = coherent_source["environment_tagged_rows"]
    for index in (0, 3, len(environment_rows) - 1):
        row = environment_rows[index]
        lines.append(
            "| `{r}` | `{sub}` | `{od}` | `{error}` |".format(
                r=row["wrong_block_probability_per_sector"],
                sub=row["epsilon_sub_tr_per_sector"],
                od=row["epsilon_OD_for_equal_coherent_superposition"],
                error=row["block_instrument_center_trace_norm_error"],
            )
        )
    lines += [
        "",
        coherent_source["carrier_frame_interpretation"],
        "",
        "| wrong mass r | epsilon_sub-tr | epsilon_OD | block-instrument center error |",
        "|---:|---:|---:|---:|",
    ]
    carrier_rows = coherent_source["carrier_frame_rows"]
    for index in (0, 3, len(carrier_rows) - 1):
        row = carrier_rows[index]
        lines.append(
            "| `{r}` | `{sub}` | `{od}` | `{error}` |".format(
                r=row["wrong_block_probability_per_sector"],
                sub=row["epsilon_sub_tr_per_sector"],
                od=row["epsilon_OD_for_equal_coherent_superposition"],
                error=row["block_instrument_center_trace_norm_error"],
            )
        )
    source_rare = source_routing["rare_sector_uniformity_negative_control"]
    lines += [
        "",
        f"Fitted coherent-routing slopes: `{coherent_source['fitted_log_log_slopes']}`.",
        "",
        f"**Remaining theorem join:** {coherent_source['required_completion']}",
        "",
        f"**Rare-sector failure:** {source_rare['severe_failure']}",
        "",
        "| K sectors | average epsilon_sub-tr | average decoder error | worst-sector decoder error |",
        "|---:|---:|---:|---:|",
    ]
    for row in source_rare["rows"]:
        if row["sector_count"] not in (2, 16, 256, 4096):
            continue
        lines.append(
            "| `{k}` | `{avg}` | `{avg_error}` | `{worst}` |".format(
                k=row["sector_count"],
                avg=row["reference_mixture_average_epsilon_sub_tr"],
                avg_error=row["reference_mixture_average_decoder_trace_norm_error"],
                worst=row["worst_sector_common_decoder_trace_norm_error"],
            )
        )
    oaqec_negative = oaqec_completion["reference_amplification_negative_control"]
    oaqec_erasure = oaqec_completion["erasure_channel_positive_control"]
    lines += [
        "",
        "## Reference-stable OAQEC completion",
        "",
        "Whole-code operator-algebra recovery is now measured in the complementary-channel diamond norm rather than an unassisted state trace norm. For target algebra `A`, define `delta_A=||Nhat-Nhat o P_{A'}||_diamond` and optimal reconstruction error `E_A=min_R ||R o N-P_A||_diamond`. REF-0736 gives `delta_A^2/4 <= E_A <= 2 sqrt(delta_A)`.",
        "",
        "The sufficient target inversion is therefore `delta_A<=tau^2/4`. If only a state-uniform defect `epsilon_state` is known on a `d_code`-dimensional input, the generic finite-dimensional lift used here is `delta_A<=d_code epsilon_state`; the dimension cannot be silently dropped.",
        "",
        "| target OAQEC error tau | d_code | max delta_A | max state-only defect under generic lift |",
        "|---:|---:|---:|---:|",
    ]
    for row in oaqec_completion["state_to_diamond_conversion"]["target_inversion_rows"]:
        if row["target_oaqec_diamond_reconstruction_error"] not in (0.1, 0.01):
            continue
        if row["code_dimension"] not in (16, 256, 4096):
            continue
        lines.append(
            "| `{target}` | `{dimension}` | `{diamond}` | `{state}` |".format(
                target=row["target_oaqec_diamond_reconstruction_error"],
                dimension=row["code_dimension"],
                diamond=row["required_complementary_diamond_defect_max"],
                state=row[
                    "required_state_only_defect_max_under_generic_dimension_lift"
                ],
            )
        )
    lines += [
        "",
        "### Severe reference-amplification control",
        "",
        oaqec_negative["model"],
        "",
        "Its state-level off-diagonal envelope vanishes as `1/d`, but the exact reference-assisted diamond defect tends to one. The Choi Jordan decomposition independently proves the exact value; this is not a numerical SDP guess.",
        "",
        "| d_code | state envelope | coherent-state witness | exact diamond defect | minimum recovery-error lower bound | diamond/state ratio |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in oaqec_negative["rows"]:
        if row["code_dimension"] not in (2, 16, 256, 4096):
            continue
        lines.append(
            "| `{dimension}` | `{state}` | `{witness}` | `{diamond}` | `{lower}` | `{ratio}` |".format(
                dimension=row["code_dimension"],
                state=row["uniform_state_trace_norm_envelope"],
                witness=row["maximally_coherent_state_trace_norm_witness"],
                diamond=row["exact_reference_assisted_diamond_defect"],
                lower=row["beny_minimum_reconstruction_error_lower_bound"],
                ratio=row["diamond_to_state_envelope_ratio"],
            )
        )
    lines += [
        "",
        f"Fitted tail slopes: `{oaqec_negative['fitted_last_six_log_log_slopes']}`.",
        "",
        f"Maximum Choi exact-formula residual: `{max(row['exact_formula_residual'] for row in oaqec_negative['choi_jordan_audit_rows'])}`.",
        "",
        f"**Severe failure:** {oaqec_negative['severe_failure']}",
        "",
        "### Positive common-decoder control",
        "",
        oaqec_erasure["model"],
        "",
        oaqec_erasure["exact_identity"],
        "",
        "| d_code | erasure probability | exact complementary defect | exact decoder error | theorem sufficient upper bound |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in oaqec_erasure["rows"]:
        if row["code_dimension"] not in (2, 16):
            continue
        if row["erasure_probability"] not in (0.1, 0.01, 0.001):
            continue
        lines.append(
            "| `{dimension}` | `{probability}` | `{defect}` | `{error}` | `{upper}` |".format(
                dimension=row["code_dimension"],
                probability=row["erasure_probability"],
                defect=row["exact_complementary_diamond_defect"],
                error=row[
                    "exact_reconstruction_diamond_error_of_replace_on_erasure_decoder"
                ],
                upper=row["beny_sufficient_upper_bound"],
            )
        )
    rate_wedge = oaqec_completion["large_code_reference_rate_wedge"]
    lines += [
        "",
        "### Nonperturbative rate wedge",
        "",
        rate_wedge["declared_schedule"],
        "",
        "| scenario | c | final state-only error | final generic diamond bound | outcome |",
        "|---|---:|---:|---:|---|",
    ]
    for scenario in rate_wedge["scenarios"]:
        row = scenario["rows"][-1]
        lines.append(
            "| `{name}` | `{rate}` | `{state}` | `{diamond}` | `{outcome}` |".format(
                name=scenario["scenario"],
                rate=scenario["state_error_rate_c"],
                state=row["state_only_error"],
                diamond=row["generic_complementary_diamond_upper_bound"],
                outcome=scenario["small_G_outcome"],
            )
        )
    lines += [
        "",
        f"**Correction:** {rate_wedge['conditional_open_wedge']}",
        "",
        f"**Source join:** {oaqec_completion['source_join']['what_is_still_required']}",
        "",
        "### Hidden-sector frame negative control",
        "",
        fixed_region["hidden_sector_frame_negative_control"]["model"],
        "",
        "| frame separation | identical-output residual | common-decoder lower bound | midpoint upper bound |",
        "|---:|---:|---:|---:|",
    ]
    frame_rows = fixed_region["hidden_sector_frame_negative_control"]["rows"]
    for index in (0, 3, len(frame_rows) - 1):
        row = frame_rows[index]
        lines.append(
            "| `{theta}` | `{output}` | `{lower}` | `{upper}` |".format(
                theta=row["sector_frame_separation_radians"],
                output=row["physical_output_identity_residual"],
                lower=row["any_common_decoder_minimax_trace_norm_lower_bound"],
                upper=row["midpoint_unitary_decoder_worst_case_upper_bound"],
            )
        )
    lines += [
        "",
        f"Fitted small-angle slopes: `{fixed_region['hidden_sector_frame_negative_control']['fitted_log_log_slopes']}`.",
        "",
        f"**Correction:** {fixed_region['correction']}",
        "",
        "## Generic state-dependent-wedge negative control",
        "",
        wedge_compatibility["model"],
        "",
        wedge_compatibility["source_scope_boundary"],
        "",
    ]
    wedge_fixed = wedge_compatibility["no_single_fixed_region_negative_control"]
    wedge_adaptive = wedge_compatibility["adaptive_region_choice_target_split"]
    wedge_union = wedge_compatibility["fixed_union_region_positive_control"]
    lines += [
        "| test | result |",
        "|---|---:|",
        f"| maximum sector-local reconstruction error | `{wedge_compatibility['sector_local_reconstruction']['maximum_sector_local_trace_norm_error']}` |",
        f"| fixed AC output distance for sector-1 orthogonal pair | `{wedge_fixed['AC_output_distance_for_sector_1_orthogonal_logical_pair']}` |",
        f"| fixed BC output distance for sector-0 orthogonal pair | `{wedge_fixed['BC_output_distance_for_sector_0_orthogonal_logical_pair']}` |",
        f"| exact fixed-region pair minimax recovery-error lower bound | `{wedge_fixed['exact_pair_minimax_recovery_trace_error_lower_bound']}` |",
        f"| adaptive block-algebra error | `{wedge_adaptive['block_diagonal_operator_algebra_error']}` |",
        f"| adaptive cross-sector coherence error | `{wedge_adaptive['cross_sector_coherent_state_trace_norm_error']}` |",
        f"| fixed full-union coherent-state decoder error | `{wedge_union['arbitrary_coherent_code_state_trace_norm_error']}` |",
        f"| AC direct-sum OAQEC commutant residual | `{wedge_compatibility['oaqec_erasure_commutant_checks']['AC_direct_sum_algebra']['maximum_commutant_operator_norm_residual']}` |",
        f"| BC direct-sum OAQEC commutant residual | `{wedge_compatibility['oaqec_erasure_commutant_checks']['BC_direct_sum_algebra']['maximum_commutant_operator_norm_residual']}` |",
        f"| ABC direct-sum OAQEC commutant residual | `{wedge_compatibility['oaqec_erasure_commutant_checks']['ABC_direct_sum_algebra']['maximum_commutant_operator_norm_residual']}` |",
        "",
        f"**Fixed-region obstruction:** {wedge_fixed['proof']}",
        "",
        f"**Target split:** {wedge_adaptive['interpretation']}",
        "",
        f"**Correction:** {wedge_compatibility['correction']}",
        "",
        "## Rare-sector quantifier negative control",
        "",
        rare["model"],
        "",
        "| K sectors | reference-mixture defect | actual mixture error | bad-sector defect | actual worst-case error | invalid whole-code bound |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    selected_counts = {2, 4, 8, 16, 64, 256, 1024, 4096}
    for row in rare["rows"]:
        if row["sector_count"] not in selected_counts:
            continue
        lines.append(
            "| `{k}` | `{avg_defect}` | `{avg_error}` | `{worst_defect}` | `{worst_error}` | `{invalid}` |".format(
                k=row["sector_count"],
                avg_defect=row["reference_mixture_relative_entropy_defect_bits"],
                avg_error=row["actual_reference_mixture_recovery_trace_norm_error"],
                worst_defect=row["bad_sector_probe_relative_entropy_defect"],
                worst_error=row["actual_worst_case_recovery_trace_norm_error"],
                invalid=row["invalid_uniform_bound_if_reference_mixture_defect_is_laundered"],
            )
        )
    lines += [
        "",
        f"**Severe failure:** {rare['severe_failure']}",
        "",
        f"**Correction:** {rare['correction']}",
        "",
        "## What is now completed—and what remains",
        "",
    ]
    lines.extend(f"- Completed: {item}" for item in result["large_code_source_bridge"]["completed_here"])
    lines.append(f"- Source conditioning: {result['large_code_source_bridge']['source_conditioning']}")
    lines.extend(f"- Still missing: {item}" for item in result["large_code_source_bridge"]["still_missing"])
    lines += [
        "",
        "## Resource-identity audit",
        "",
        f"Owned toy resource: `{result['resource_identity_audit']['owned_toy_resource']}`. Conditional theorem resource: `{result['resource_identity_audit']['conditional_bridge_resource']}`. Physical variables: `{result['resource_identity_audit']['physical_source_resources']}`. Identity status: **{result['resource_identity_audit']['identity_status']}**.",
        "",
        "## Acceptance checks",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]
    for check in result["acceptance_checks"]:
        detail = str(check["detail"]).replace("|", "\\|")
        lines.append(f"| {check['check']} | `{str(check['passed']).lower()}` | {detail} |")
    lines += ["", "## Hard limits and next denominator", ""]
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
            print("FAMILYC JLMS RECOVERY BUDGET BENCHMARK FAILED")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print("FAMILYC JLMS RECOVERY BUDGET BENCHMARK OK")
        return 0

    write_generated_texts(root, texts)
    if result["validation_failures"]:
        print("FAMILYC JLMS RECOVERY BUDGET BENCHMARK WROTE FAILING RESULT")
        for failure in result["validation_failures"]:
            print(f"- {failure}")
        return 1
    print(f"WROTE {OUTPUT_JSON}")
    print(f"WROTE {OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
