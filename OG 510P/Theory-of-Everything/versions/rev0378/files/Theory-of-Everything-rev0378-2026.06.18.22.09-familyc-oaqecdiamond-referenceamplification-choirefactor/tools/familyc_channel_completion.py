#!/usr/bin/env python3
"""Route-local channel-completion and exponent-transfer helpers for Family C.

This module owns theorem algebra, not release policy.  It turns a bounded
non-isometric encoding V into a genuine flagged channel while preserving the
source's normalized success state exactly, and it exposes the source-tail
power-counting wedge without assigning physical exponents.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from typing import Any

from familyc_operator_algebra import (
    bloch_state,
    hermitian,
    matrix_log_positive,
    matrix_sqrt_psd,
    quantum_relative_entropy_nats,
    trace_norm_hermitian,
)
from familyc_state_domain import spectral_floor_domain_geometry


def _as_probabilities(values: Sequence[float], *, label: str) -> list[float]:
    probabilities = [float(value) for value in values]
    if not probabilities:
        raise ValueError(f"{label} must be non-empty")
    if any(value < 0.0 for value in probabilities):
        raise ValueError(f"{label} contains a negative entry")
    total = sum(probabilities)
    if not math.isfinite(total) or abs(total - 1.0) > 1e-12:
        raise ValueError(f"{label} must sum to one; got {total!r}")
    return probabilities


def relative_entropy_nats(state: Sequence[float], reference: Sequence[float]) -> float:
    """Classical relative entropy with the standard extended-value convention."""
    state_values = _as_probabilities(state, label="state")
    reference_values = _as_probabilities(reference, label="reference")
    if len(state_values) != len(reference_values):
        raise ValueError("state/reference dimensions differ")
    result = 0.0
    for value, baseline in zip(state_values, reference_values):
        if value == 0.0:
            continue
        if baseline <= 0.0:
            return math.inf
        result += value * math.log(value / baseline)
    return result


def bernoulli_relative_entropy_nats(success: float, reference_success: float) -> float:
    return relative_entropy_nats(
        [float(success), 1.0 - float(success)],
        [float(reference_success), 1.0 - float(reference_success)],
    )


def centered_oscillation(values: Sequence[float]) -> float:
    """inf_c ||diag(values)-cI||_infinity for a real diagonal operator."""
    entries = [float(value) for value in values]
    if not entries:
        raise ValueError("centered oscillation needs at least one entry")
    return 0.5 * (max(entries) - min(entries))


def normalized_filter_state(
    state: Sequence[float], metric: Sequence[float]
) -> tuple[list[float], float]:
    """Return the normalized V-state and z=Tr(V^dagger V rho) in a diagonal cell."""
    probabilities = _as_probabilities(state, label="state")
    weights = [float(value) for value in metric]
    if len(probabilities) != len(weights):
        raise ValueError("state/metric dimensions differ")
    if any(value <= 0.0 for value in weights):
        raise ValueError("metric entries must be positive")
    normalization = sum(weight * probability for weight, probability in zip(weights, probabilities))
    if normalization <= 0.0 or not math.isfinite(normalization):
        raise ValueError("filter normalization is not positive and finite")
    return [
        weight * probability / normalization
        for weight, probability in zip(weights, probabilities)
    ], normalization


def flagged_probability_bounds(delta_isometry: float) -> dict[str, float]:
    """Uniform success/failure bounds for alpha=(1+delta)^-1 and ||M-I||<=delta."""
    delta = float(delta_isometry)
    if not 0.0 <= delta < 1.0:
        raise ValueError("delta_isometry must lie in [0,1)")
    alpha = 1.0 / (1.0 + delta)
    success_min = (1.0 - delta) / (1.0 + delta)
    failure_max = 1.0 - success_min
    return {
        "alpha": alpha,
        "success_probability_min": success_min,
        "failure_probability_max": failure_max,
    }


def flagged_channel_state(
    state: Sequence[float], metric: Sequence[float], delta_isometry: float
) -> dict[str, Any]:
    """Classical diagonal image of the CPTP flagged completion.

    Quantum form:
      Phi(rho)=alpha V rho V^dagger
               + Tr[(I-alpha V^dagger V)rho] |fail><fail|,
    with the success and failure sectors orthogonal.  The first term is stored
    as its diagonal distribution and the final list entry is the flag weight.
    """
    probabilities = _as_probabilities(state, label="state")
    weights = [float(value) for value in metric]
    if len(probabilities) != len(weights):
        raise ValueError("state/metric dimensions differ")
    bounds = flagged_probability_bounds(delta_isometry)
    alpha = bounds["alpha"]
    upper = 1.0 + float(delta_isometry)
    lower = 1.0 - float(delta_isometry)
    if any(value < lower - 1e-12 or value > upper + 1e-12 for value in weights):
        raise ValueError("metric violates the declared ||M-I|| bound")
    normalized, normalization = normalized_filter_state(probabilities, weights)
    success = alpha * normalization
    failure = 1.0 - success
    if failure < -1e-12:
        raise ValueError("flagged completion has negative failure probability")
    failure = max(0.0, failure)
    distribution = [success * value for value in normalized] + [failure]
    return {
        "distribution": distribution,
        "success_probability": success,
        "failure_probability": failure,
        "conditioned_success_state": normalized,
        "normalization": normalization,
    }


def normalized_map_pairwise_bound_nats(
    eta_nats: float, delta_isometry: float, modular_oscillation_nats: float
) -> float:
    """Owned rev0371 bound for the nonlinear normalized map."""
    eta = float(eta_nats)
    delta = float(delta_isometry)
    oscillation = float(modular_oscillation_nats)
    if eta < 0.0 or oscillation < 0.0:
        raise ValueError("eta and modular oscillation must be non-negative")
    if not 0.0 <= delta < 1.0:
        raise ValueError("delta_isometry must lie in [0,1)")
    return 2.0 * (eta + delta * oscillation) / (1.0 - delta)


def flagged_channel_pairwise_bound_nats(
    normalized_map_bound_nats: float,
    delta_isometry: float,
    relative_entropy_diameter_nats: float,
) -> float:
    """Uniform data-processing defect for the genuine flagged channel.

    For each ordered pair sigma,rho,
      D(Phi(sigma)||Phi(rho))
        = p_sigma D(W(sigma)||W(rho))
          + D_Ber(p_sigma||p_rho).
    In the JLMS application the comparison quantity is the bulk-wedge
    relative entropy D(sigma_r||rho_r), not necessarily the full-code
    relative entropy.  If
      D(sigma_r||rho_r)-D(W(sigma)||W(rho)) <= E_W
    and the reduced-state domain has D(sigma_r||rho_r)<=D_max, positivity
    of Bernoulli KL gives
      D(sigma_r||rho_r)-D(Phi(sigma)||Phi(rho)) <= E_W+q_max D_max.
    """
    normalized_bound = float(normalized_map_bound_nats)
    diameter = float(relative_entropy_diameter_nats)
    if normalized_bound < 0.0 or diameter < 0.0:
        raise ValueError("defect bounds and domain diameter must be non-negative")
    q_max = flagged_probability_bounds(delta_isometry)["failure_probability_max"]
    return normalized_bound + q_max * diameter


def universal_full_code_trace_bound_from_nats(
    defect_nats: float, theorem_constant: float
) -> float:
    defect = float(defect_nats)
    constant = float(theorem_constant)
    if defect < 0.0 or constant < 0.0:
        raise ValueError("defect and theorem constant must be non-negative")
    return constant * math.sqrt(defect / math.log(2.0))


def success_conditioned_recovery_bound(
    flagged_trace_bound: float, delta_isometry: float
) -> float:
    """Transfer a flagged-channel decoder to the source's success states.

    If R recovers Phi with trace error T and R_s is R restricted to the
    success block, then
      ||R_s(W(rho))-rho||_1 <= (T+2 q_max)/p_min
      = ((1+delta)T+4 delta)/(1-delta).
    """
    trace_bound = float(flagged_trace_bound)
    if trace_bound < 0.0:
        raise ValueError("flagged trace bound must be non-negative")
    bounds = flagged_probability_bounds(delta_isometry)
    return (
        trace_bound + 2.0 * bounds["failure_probability_max"]
    ) / bounds["success_probability_min"]


def flagged_completion_budget(
    *,
    eta_nats: float,
    delta_isometry: float,
    modular_oscillation_nats: float,
    relative_entropy_diameter_nats: float,
    theorem_constant: float,
) -> dict[str, float]:
    normalized_bound = normalized_map_pairwise_bound_nats(
        eta_nats, delta_isometry, modular_oscillation_nats
    )
    flagged_bound = flagged_channel_pairwise_bound_nats(
        normalized_bound,
        delta_isometry,
        relative_entropy_diameter_nats,
    )
    flagged_trace = universal_full_code_trace_bound_from_nats(
        flagged_bound, theorem_constant
    )
    conditioned_trace = success_conditioned_recovery_bound(
        flagged_trace, delta_isometry
    )
    values = {
        **flagged_probability_bounds(delta_isometry),
        "normalized_map_pairwise_bound_nats": normalized_bound,
        "flagged_channel_pairwise_defect_bound_nats": flagged_bound,
        "flagged_channel_trace_or_observable_bound": flagged_trace,
        "success_conditioned_trace_bound": conditioned_trace,
    }
    return values


def max_delta_for_success_target(
    *,
    target_trace_error: float,
    eta_nats: float,
    modular_oscillation: Callable[[float], float],
    relative_entropy_diameter: Callable[[float], float],
    theorem_constant: float,
    upper_delta: float = 0.25,
    iterations: int = 100,
) -> float:
    """Bisection inversion of the full flagged-success recovery budget."""
    target = float(target_trace_error)
    if not 0.0 < target <= 2.0:
        raise ValueError("target_trace_error must lie in (0,2]")
    if eta_nats < 0.0:
        raise ValueError("eta_nats must be non-negative")

    def admissible(delta: float) -> bool:
        result = flagged_completion_budget(
            eta_nats=eta_nats,
            delta_isometry=delta,
            modular_oscillation_nats=modular_oscillation(delta),
            relative_entropy_diameter_nats=relative_entropy_diameter(delta),
            theorem_constant=theorem_constant,
        )
        return result["success_conditioned_trace_bound"] <= target

    low = 0.0
    high = min(float(upper_delta), 1.0 - 1e-12)
    if admissible(high):
        return high
    for _ in range(iterations):
        midpoint = 0.5 * (low + high)
        if admissible(midpoint):
            low = midpoint
        else:
            high = midpoint
    return low


def source_tail_wedge(
    *,
    flm_power: float,
    tail_power: float,
    small_isometry_power: float,
    domain_diameter_power: float = 0.0,
    modular_oscillation_power: float = 0.0,
) -> dict[str, Any]:
    """Conditional power counting for Eq. (3.17) followed by flagged recovery.

    With eps_FLM~G^a, eps_tail~G^t, eps_iso,small~G^b,
      eps_pJLMS ~ G^((a-t)/2) + G^b |log G|.
    If delta_iso~G^b, D_max~G^-d, and L_K^osc~G^-ell, the flagged
    channel defect has the worst power among the source ratio, delta D_max,
    and delta L terms.  This is symbolic theorem propagation, not a physical
    exponent assignment.
    """
    a = float(flm_power)
    t = float(tail_power)
    b = float(small_isometry_power)
    d = float(domain_diameter_power)
    ell = float(modular_oscillation_power)
    source_ratio_power = 0.5 * (a - t)
    candidates = {
        "sqrt_eps_FLM_over_eps_tail": source_ratio_power,
        "eps_iso_small_log_eps_tail": b,
        "delta_iso_times_domain_diameter": b - d,
        "delta_iso_times_modular_oscillation": b - ell,
    }
    defect_power = min(candidates.values())
    operational_power = 0.5 * defect_power
    return {
        "flm_power_a": a,
        "tail_power_t": t,
        "small_isometry_power_b": b,
        "domain_diameter_growth_power_d": d,
        "modular_oscillation_growth_power_ell": ell,
        "tail_wedge_open": a > t > 0.0,
        "source_ratio_power": source_ratio_power,
        "candidate_flagged_defect_powers": candidates,
        "flagged_channel_defect_power_up_to_logs": defect_power,
        "success_recovery_trace_power_up_to_logs": operational_power,
        "convergent_through_this_chain": a > t > 0.0 and defect_power > 0.0,
    }


def full_system_flm_isometry_bound(
    *, epsilon_flm: float, epsilon_od: float = 0.0
) -> dict[str, float]:
    """Close the source's Appendix-C/Lemma-4 approximate-isometry chain.

    Appendix C gives eps_iso,small <= 2 sqrt(eps_FLM) when the approximate
    FLM relation is available on the entire small-code system after the
    source's rescaling.  Lemma 4 then gives

      delta_iso <= eps_iso,small + eps_OD

    for the large direct-sum encoding.  This is an optional stronger premise,
    not a consequence of a subregion FLM estimate alone.
    """
    flm = float(epsilon_flm)
    od = float(epsilon_od)
    if flm < 0.0 or od < 0.0:
        raise ValueError("epsilon_flm and epsilon_od must be non-negative")
    small = 2.0 * math.sqrt(flm)
    return {
        "epsilon_iso_small_upper": small,
        "epsilon_od": od,
        "delta_iso_large_upper": small + od,
    }


def source_closed_sector_wedge(
    *,
    flm_power: float,
    tail_power: float,
    exponential_sector_power: float,
) -> dict[str, Any]:
    """Power wedge after using full-system FLM to pay isometry debt.

    With eps_FLM~G^a and K~exp(c/G^gamma), Appendix C and Lemma 4 give
    delta_iso=O(G^(a/2)) when eps_OD is nonperturbative.  At fixed total
    sector-floor mass, D_max and L_K^osc are O(G^-gamma).  The flagged
    defect therefore has candidate powers

      (a-t)/2, a/2, a/2-gamma,

    up to logarithms and independently supplied nonperturbative terms.
    """
    a = float(flm_power)
    t = float(tail_power)
    gamma = float(exponential_sector_power)
    candidates = {
        "sqrt_eps_FLM_over_eps_tail": 0.5 * (a - t),
        "full_system_FLM_isometry_log_tail": 0.5 * a,
        "full_system_FLM_isometry_times_sector_geometry": 0.5 * a - gamma,
    }
    defect_power = min(candidates.values())
    return {
        "flm_power_a": a,
        "tail_power_t": t,
        "exponential_sector_power_gamma": gamma,
        "derived_small_isometry_power_b": 0.5 * a,
        "candidate_flagged_defect_powers": candidates,
        "flagged_channel_defect_power_up_to_logs": defect_power,
        "success_recovery_trace_power_up_to_logs": 0.5 * defect_power,
        "tail_wedge_open": a > t > 0.0,
        "sector_wedge_open": a > 2.0 * gamma,
        "convergent_through_this_chain": a > t > 0.0
        and a > 2.0 * gamma
        and defect_power > 0.0,
        "closed_form_condition": "a>max(t,2 gamma), assuming eps_OD and the remaining Theorem-5 terms are nonperturbative on the same domain",
    }


def simplex_grid(step_tenths: int = 1, floor_tenths: int = 1) -> list[list[float]]:
    """Deterministic three-outcome simplex grid used by the executable probe."""
    if step_tenths <= 0 or floor_tenths <= 0:
        raise ValueError("grid step and floor must be positive tenths")
    states: list[list[float]] = []
    for first in range(floor_tenths, 11, step_tenths):
        for second in range(floor_tenths, 11, step_tenths):
            third = 10 - first - second
            if third < floor_tenths:
                continue
            states.append([first / 10.0, second / 10.0, third / 10.0])
    return states


def max_over_ordered_pairs(
    states: Iterable[Sequence[float]], function: Callable[[Sequence[float], Sequence[float]], float]
) -> tuple[float, tuple[list[float], list[float]] | None]:
    materialized = [list(state) for state in states]
    maximum = -math.inf
    argmax: tuple[list[float], list[float]] | None = None
    for left in materialized:
        for right in materialized:
            value = float(function(left, right))
            if value > maximum:
                maximum = value
                argmax = (left, right)
    return maximum, argmax


def _modular_vector_nats(state: Sequence[float]) -> list[float]:
    return [-math.log(float(value)) for value in state]


def flagged_channel_completion_probe(
    *, delta_isometry: float, theorem_constant: float
) -> dict[str, Any]:
    """Executable three-outcome proof cell for the flagged completion."""
    from benchmark_numeric import stable_number

    delta = float(delta_isometry)
    metric = [1.0 + delta, 1.0, 1.0 - delta]
    states = simplex_grid(step_tenths=1, floor_tenths=1)

    def residual(state: list[float]) -> list[float]:
        normalized, _ = normalized_filter_state(state, metric)
        return [
            weight * (boundary_value - bulk_value)
            for weight, boundary_value, bulk_value in zip(
                metric,
                _modular_vector_nats(normalized),
                _modular_vector_nats(state),
            )
        ]

    eta = max(max(abs(value) for value in residual(state)) for state in states)
    modular_oscillation = 0.0
    relative_entropy_diameter = 0.0
    max_normalized_loss = 0.0
    max_absolute_normalized_defect = 0.0
    max_flagged_loss = 0.0
    max_block_identity_residual = 0.0
    max_success_state_residual = 0.0
    normalized_argmax: dict[str, Any] | None = None
    flagged_argmax: dict[str, Any] | None = None

    for sigma in states:
        w_sigma, _ = normalized_filter_state(sigma, metric)
        phi_sigma = flagged_channel_state(sigma, metric, delta)
        max_success_state_residual = max(
            max_success_state_residual,
            sum(
                abs(left - right)
                for left, right in zip(
                    w_sigma, phi_sigma["conditioned_success_state"]
                )
            ),
        )
        for rho in states:
            w_rho, _ = normalized_filter_state(rho, metric)
            phi_rho = flagged_channel_state(rho, metric, delta)
            input_relative_entropy = relative_entropy_nats(sigma, rho)
            normalized_relative_entropy = relative_entropy_nats(w_sigma, w_rho)
            flagged_relative_entropy = relative_entropy_nats(
                phi_sigma["distribution"], phi_rho["distribution"]
            )
            normalized_loss = input_relative_entropy - normalized_relative_entropy
            flagged_loss = input_relative_entropy - flagged_relative_entropy
            relative_entropy_diameter = max(
                relative_entropy_diameter, input_relative_entropy
            )
            max_absolute_normalized_defect = max(
                max_absolute_normalized_defect, abs(normalized_loss)
            )
            if normalized_loss > max_normalized_loss:
                max_normalized_loss = normalized_loss
                normalized_argmax = {
                    "sigma": [stable_number(value) for value in sigma],
                    "rho": [stable_number(value) for value in rho],
                    "input_relative_entropy_nats": stable_number(
                        input_relative_entropy
                    ),
                    "normalized_relative_entropy_nats": stable_number(
                        normalized_relative_entropy
                    ),
                }
            if flagged_loss > max_flagged_loss:
                max_flagged_loss = flagged_loss
                flagged_argmax = {
                    "sigma": [stable_number(value) for value in sigma],
                    "rho": [stable_number(value) for value in rho],
                    "input_relative_entropy_nats": stable_number(
                        input_relative_entropy
                    ),
                    "flagged_relative_entropy_nats": stable_number(
                        flagged_relative_entropy
                    ),
                }
            block_identity = (
                phi_sigma["success_probability"] * normalized_relative_entropy
                + bernoulli_relative_entropy_nats(
                    phi_sigma["success_probability"],
                    phi_rho["success_probability"],
                )
            )
            max_block_identity_residual = max(
                max_block_identity_residual,
                abs(flagged_relative_entropy - block_identity),
            )
            modular_difference = [
                left - right
                for left, right in zip(
                    _modular_vector_nats(rho), _modular_vector_nats(sigma)
                )
            ]
            modular_oscillation = max(
                modular_oscillation, centered_oscillation(modular_difference)
            )

    left = [0.8, 0.1, 0.1]
    right = [0.1, 0.1, 0.8]
    midpoint = [0.5 * (a + b) for a, b in zip(left, right)]
    phi_left = flagged_channel_state(left, metric, delta)["distribution"]
    phi_right = flagged_channel_state(right, metric, delta)["distribution"]
    phi_midpoint = flagged_channel_state(midpoint, metric, delta)["distribution"]
    affine_midpoint = [0.5 * (a + b) for a, b in zip(phi_left, phi_right)]
    flagged_affine_residual = sum(
        abs(a - b) for a, b in zip(phi_midpoint, affine_midpoint)
    )

    completion = flagged_completion_budget(
        eta_nats=eta,
        delta_isometry=delta,
        modular_oscillation_nats=modular_oscillation,
        relative_entropy_diameter_nats=relative_entropy_diameter,
        theorem_constant=theorem_constant,
    )
    actual_loss_flagged_bound = (
        max_normalized_loss
        + completion["failure_probability_max"] * relative_entropy_diameter
    )
    actual_loss_flagged_trace = universal_full_code_trace_bound_from_nats(
        actual_loss_flagged_bound, theorem_constant
    )
    actual_loss_success_trace = success_conditioned_recovery_bound(
        actual_loss_flagged_trace, delta
    )

    return {
        "model": "Three-outcome diagonal approximate encoding with M=diag(1+delta,1,1-delta) on the 0.1-spaced full-rank simplex; the completion appends one orthogonal failure flag.",
        "declared_state_count": len(states),
        "delta_isometry": delta,
        "metric_diagonal": metric,
        "channel_definition": "Phi(rho)=alpha V rho V^dagger on the success block plus Tr[(I-alpha V^dagger V)rho]|fail><fail|, alpha=(1+delta_iso)^-1.",
        "conditioned_success_identity": "Phi(rho)|success / p_rho = W_V(rho) exactly.",
        "uniform_projected_residual_eta_nats": stable_number(eta),
        "declared_modular_oscillation_nats": stable_number(modular_oscillation),
        "declared_relative_entropy_diameter_nats": stable_number(
            relative_entropy_diameter
        ),
        "max_actual_normalized_map_information_loss_nats": stable_number(
            max_normalized_loss
        ),
        "max_absolute_normalized_map_defect_nats": stable_number(
            max_absolute_normalized_defect
        ),
        "normalized_map_argmax": normalized_argmax,
        "max_actual_flagged_channel_information_loss_nats": stable_number(
            max_flagged_loss
        ),
        "flagged_channel_argmax": flagged_argmax,
        "max_block_relative_entropy_identity_residual": stable_number(
            max_block_identity_residual
        ),
        "max_conditioned_success_state_residual": stable_number(
            max_success_state_residual
        ),
        "flagged_channel_affine_residual": stable_number(flagged_affine_residual),
        "completion_budget": {
            key: stable_number(value) for key, value in completion.items()
        },
        "generic_bound_using_actual_normalized_loss": {
            "flagged_channel_pairwise_defect_bound_nats": stable_number(
                actual_loss_flagged_bound
            ),
            "flagged_channel_trace_or_observable_bound": stable_number(
                actual_loss_flagged_trace
            ),
            "success_conditioned_trace_bound": stable_number(
                actual_loss_success_trace
            ),
        },
        "interpretation": "The completion is a genuine channel and retains the source normalized state exactly on success. Its theorem defect pays the nonlinear-map bound plus q_max times the declared relative-entropy diameter. Restricting a flagged decoder to the success block adds the explicit (T+2q_max)/p_min transfer cost.",
    }



def noncommuting_flagged_channel_probe(*, delta_isometry: float) -> dict[str, Any]:
    """Noncommuting qubit audit of the flagged CPTP completion.

    The diagonal probe above exercises the budgeting logic.  This cell checks
    the genuinely quantum part independently: a non-diagonal positive metric,
    noncommuting full-rank states, an explicit Kraus completion, Choi
    positivity, trace preservation, conditioned-success identity, and the
    direct-sum quantum-relative-entropy formula.
    """
    import numpy as np

    from benchmark_numeric import stable_number

    delta = float(delta_isometry)
    if not 0.0 < delta < 1.0:
        raise ValueError("delta_isometry must lie in (0,1) for this probe")

    theta = 0.41
    phase = 0.37
    rotation = np.array(
        [
            [math.cos(theta), -math.sin(theta) * np.exp(-1j * phase)],
            [math.sin(theta) * np.exp(1j * phase), math.cos(theta)],
        ],
        dtype=complex,
    )
    metric = rotation @ np.diag([1.0 + delta, 1.0 - delta]) @ rotation.conj().T
    encoding = matrix_sqrt_psd(metric)
    alpha = 1.0 / (1.0 + delta)
    failure_effect = hermitian(np.eye(2, dtype=complex) - alpha * metric)

    success_kraus = np.zeros((3, 2), dtype=complex)
    success_kraus[:2, :] = math.sqrt(alpha) * encoding
    kraus = [success_kraus]
    fail_values, fail_vectors = np.linalg.eigh(failure_effect)
    for index, value in enumerate(fail_values):
        if value <= 1e-15:
            continue
        operator = np.zeros((3, 2), dtype=complex)
        operator[2, :] = math.sqrt(float(value)) * fail_vectors[:, index].conj()
        kraus.append(operator)

    completeness = sum(operator.conj().T @ operator for operator in kraus)
    completeness_residual = trace_norm_hermitian(completeness - np.eye(2))
    choi = sum(
        np.outer(operator.reshape(-1, order="F"), operator.reshape(-1, order="F").conj())
        for operator in kraus
    )
    min_choi_eigenvalue = float(np.linalg.eigvalsh(hermitian(choi)).min())

    states = [
        bloch_state((0.35, 0.20, 0.10)),
        bloch_state((-0.25, 0.30, -0.15)),
        bloch_state((0.10, -0.35, 0.25)),
        bloch_state((-0.30, -0.10, 0.20)),
        0.5 * np.eye(2, dtype=complex),
    ]

    def channel(state: Any) -> Any:
        return hermitian(sum(operator @ state @ operator.conj().T for operator in kraus))

    def normalized_success(state: Any) -> tuple[Any, float]:
        unnormalized = hermitian(encoding @ state @ encoding.conj().T)
        normalization = float(np.trace(unnormalized).real)
        return unnormalized / normalization, normalization

    max_trace_residual = 0.0
    min_output_eigenvalue = math.inf
    max_success_residual = 0.0
    outputs: list[Any] = []
    successes: list[float] = []
    normalized_states: list[Any] = []
    for state in states:
        output = channel(state)
        success_state, normalization = normalized_success(state)
        success_probability = alpha * normalization
        conditioned = output[:2, :2] / success_probability
        max_trace_residual = max(max_trace_residual, abs(float(np.trace(output).real) - 1.0))
        min_output_eigenvalue = min(
            min_output_eigenvalue, float(np.linalg.eigvalsh(output).min())
        )
        max_success_residual = max(
            max_success_residual, trace_norm_hermitian(conditioned - success_state)
        )
        outputs.append(output)
        successes.append(success_probability)
        normalized_states.append(success_state)

    mix_weight = 0.37
    mixed_input = mix_weight * states[0] + (1.0 - mix_weight) * states[1]
    affine_output = mix_weight * outputs[0] + (1.0 - mix_weight) * outputs[1]
    affine_residual = trace_norm_hermitian(channel(mixed_input) - affine_output)

    max_block_identity_residual = 0.0
    max_normalized_loss = 0.0
    max_flagged_loss = 0.0
    relative_entropy_diameter = 0.0
    for sigma_index, sigma in enumerate(states):
        for rho_index, rho in enumerate(states):
            input_relative_entropy = quantum_relative_entropy_nats(sigma, rho)
            normalized_relative_entropy = quantum_relative_entropy_nats(
                normalized_states[sigma_index], normalized_states[rho_index]
            )
            flagged_relative_entropy = quantum_relative_entropy_nats(
                outputs[sigma_index], outputs[rho_index]
            )
            block_value = (
                successes[sigma_index] * normalized_relative_entropy
                + bernoulli_relative_entropy_nats(
                    successes[sigma_index], successes[rho_index]
                )
            )
            max_block_identity_residual = max(
                max_block_identity_residual,
                abs(flagged_relative_entropy - block_value),
            )
            normalized_loss = input_relative_entropy - normalized_relative_entropy
            flagged_loss = input_relative_entropy - flagged_relative_entropy
            max_normalized_loss = max(max_normalized_loss, normalized_loss)
            max_flagged_loss = max(max_flagged_loss, flagged_loss)
            relative_entropy_diameter = max(
                relative_entropy_diameter, input_relative_entropy
            )

    probability_bounds = flagged_probability_bounds(delta)
    generic_bound = (
        max_normalized_loss
        + probability_bounds["failure_probability_max"] * relative_entropy_diameter
    )
    return {
        "model": "Noncommuting full-rank qubit states with a complex-rotated metric M=U diag(1+delta,1-delta) U^dagger and an explicit three-dimensional success/failure Kraus completion.",
        "declared_state_count": len(states),
        "delta_isometry": delta,
        "kraus_operator_count": len(kraus),
        "kraus_completeness_trace_norm_residual": stable_number(completeness_residual),
        "minimum_choi_eigenvalue": stable_number(min_choi_eigenvalue),
        "maximum_output_trace_residual": stable_number(max_trace_residual),
        "minimum_test_output_eigenvalue": stable_number(min_output_eigenvalue),
        "affine_trace_norm_residual": stable_number(affine_residual),
        "maximum_conditioned_success_trace_norm_residual": stable_number(
            max_success_residual
        ),
        "maximum_block_relative_entropy_identity_residual": stable_number(
            max_block_identity_residual
        ),
        "maximum_normalized_map_information_loss_nats": stable_number(
            max_normalized_loss
        ),
        "maximum_flagged_channel_information_loss_nats": stable_number(
            max_flagged_loss
        ),
        "declared_relative_entropy_diameter_nats": stable_number(
            relative_entropy_diameter
        ),
        "generic_flagged_defect_bound_nats": stable_number(generic_bound),
        "proof_device_boundary": "The orthogonal flag is an auxiliary channel-completion device, not an asserted physical boundary degree of freedom. The recovery consequence used by the bridge is the restriction of the theorem decoder to the original success block.",
    }

def flagged_target_budget_rows(
    *, target_trace_errors: Sequence[float], theorem_constant: float
) -> list[dict[str, Any]]:
    from benchmark_numeric import stable_number

    rows: list[dict[str, Any]] = []
    dimension = 2
    for floor in (1e-1, 1e-2, 1e-3, 1e-6):
        geometry = spectral_floor_domain_geometry(
            dimension=dimension, eigenvalue_floor=floor
        )
        diameter = float(geometry["exact_relative_entropy_diameter_nats"])
        modular_oscillation = float(
            geometry["exact_centered_modular_oscillation_nats"]
        )
        for target_value in target_trace_errors:
            target = float(target_value)
            delta_max = max_delta_for_success_target(
                target_trace_error=target,
                eta_nats=0.0,
                modular_oscillation=lambda _delta, value=modular_oscillation: value,
                relative_entropy_diameter=lambda _delta, value=diameter: value,
                theorem_constant=theorem_constant,
                upper_delta=0.1,
            )
            saturated = flagged_completion_budget(
                eta_nats=0.0,
                delta_isometry=delta_max,
                modular_oscillation_nats=modular_oscillation,
                relative_entropy_diameter_nats=diameter,
                theorem_constant=theorem_constant,
            )
            rows.append(
                {
                    "reconstructed_algebra_dimension": dimension,
                    "reference_spectral_floor": floor,
                    "domain_definition": "all dimension-2 density matrices with rho >= floor I",
                    "exact_relative_entropy_diameter_nats": stable_number(
                        diameter
                    ),
                    "exact_centered_modular_oscillation_nats": stable_number(
                        modular_oscillation
                    ),
                    "target_success_conditioned_trace_error": target,
                    "max_delta_iso_if_eta_zero": stable_number(delta_max),
                    "saturated_success_conditioned_bound": stable_number(
                        saturated["success_conditioned_trace_bound"]
                    ),
                    "status": "conditional theorem inversion; no physical delta_iso(G,N) is asserted",
                }
            )
    return rows


def source_tail_wedge_rows() -> list[dict[str, Any]]:
    scenarios = [
        ("open_balanced", 3.0, 1.0, 1.0, 0.0, 0.0),
        ("open_narrow_tail", 2.0, 1.5, 1.0, 0.0, 0.0),
        ("closed_at_tail_boundary", 1.0, 1.0, 1.0, 0.0, 0.0),
        ("domain_growth_erases_isometry_gain", 3.0, 1.0, 1.0, 1.0, 0.0),
        ("open_with_controlled_domain_growth", 4.0, 1.0, 2.0, 0.5, 0.5),
    ]
    rows: list[dict[str, Any]] = []
    for label, a, t, b, d, ell in scenarios:
        result = source_tail_wedge(
            flm_power=a,
            tail_power=t,
            small_isometry_power=b,
            domain_diameter_power=d,
            modular_oscillation_power=ell,
        )
        rows.append({"scenario": label, **result})
    return rows


def source_power_transfer_schedule(*, theorem_constant: float) -> dict[str, Any]:
    """Synthetic G-power cell for Eq. (3.17); not a fit to holographic data."""
    from benchmark_numeric import log_log_slope, stable_number

    a = 2.0
    t = 1.0
    b = 1.0
    rows: list[dict[str, Any]] = []
    for exponent in range(8, 81, 4):
        g_value = 2.0 ** (-exponent)
        epsilon_flm = g_value**a
        epsilon_tail = g_value**t
        epsilon_iso_small = g_value**b
        epsilon_pjlms = math.sqrt(epsilon_flm / epsilon_tail) + epsilon_iso_small * abs(
            math.log(epsilon_tail)
        )
        eta = epsilon_pjlms + epsilon_iso_small
        delta = epsilon_iso_small
        domain_log = abs(math.log(g_value))
        completion = flagged_completion_budget(
            eta_nats=eta,
            delta_isometry=delta,
            modular_oscillation_nats=domain_log,
            relative_entropy_diameter_nats=domain_log,
            theorem_constant=theorem_constant,
        )
        rows.append(
            {
                "G_test_vector": stable_number(g_value),
                "epsilon_FLM": stable_number(epsilon_flm),
                "epsilon_tail": stable_number(epsilon_tail),
                "epsilon_iso_small": stable_number(epsilon_iso_small),
                "epsilon_pJLMS": stable_number(epsilon_pjlms),
                "theorem5_eta_test_vector_nats": stable_number(eta),
                "flagged_channel_defect_bound_nats": stable_number(
                    completion["flagged_channel_pairwise_defect_bound_nats"]
                ),
                "success_conditioned_trace_bound": stable_number(
                    completion["success_conditioned_trace_bound"]
                ),
            }
        )
    asymptotic = rows[-8:]
    slopes = {
        "epsilon_pJLMS_vs_G": stable_number(
            log_log_slope(asymptotic, "G_test_vector", "epsilon_pJLMS")
        ),
        "flagged_channel_defect_vs_G": stable_number(
            log_log_slope(
                asymptotic,
                "G_test_vector",
                "flagged_channel_defect_bound_nats",
            )
        ),
        "success_conditioned_trace_bound_vs_G": stable_number(
            log_log_slope(
                asymptotic,
                "G_test_vector",
                "success_conditioned_trace_bound",
            )
        ),
    }
    return {
        "status": "synthetic symbolic-exponent transfer only; G values are theorem test vectors, not source measurements",
        "declared_source_rules": {
            "epsilon_FLM": "G^2",
            "epsilon_tail": "G^1",
            "epsilon_iso_small": "G^1",
            "epsilon_pJLMS": "sqrt(epsilon_FLM/epsilon_tail)+epsilon_iso_small |log epsilon_tail|",
            "theorem5_eta": "epsilon_pJLMS+epsilon_iso_small; all other source terms set to zero only for this transfer test",
            "domain_diameter_and_modular_oscillation": "|log G|",
        },
        "expected_power_exponents_up_to_logs": {
            "epsilon_pJLMS": 0.5,
            "flagged_channel_defect": 0.5,
            "success_conditioned_trace": 0.25,
        },
        "fitted_asymptotic_log_log_slopes": slopes,
        "rows": rows,
    }
