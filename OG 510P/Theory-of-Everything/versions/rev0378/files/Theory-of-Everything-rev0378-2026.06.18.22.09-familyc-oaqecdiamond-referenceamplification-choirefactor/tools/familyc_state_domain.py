#!/usr/bin/env python3
"""Exact state-domain geometry for the Family-C recovery bridge.

The large-code source is a direct sum of mutually orthogonal sectors.  Its
reduced bulk state therefore carries a classical sector-weight distribution in
addition to each sector's internal density matrix.  Sector-local log-stability
does not by itself bound the relative-entropy diameter or modular oscillation
created by a growing sector simplex.

This module owns the exact finite-dimensional geometry used to price that debt.
It contains no release policy and assigns no physical sector-count law.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any


def _validate_dimension(dimension: int) -> int:
    value = int(dimension)
    if value != dimension or value < 2:
        raise ValueError("dimension must be an integer >= 2")
    return value


def spectral_floor_domain_geometry(*, dimension: int, eigenvalue_floor: float) -> dict[str, float | int]:
    """Exact geometry of D_{d,lambda}={rho: rho>=lambda I, Tr rho=1}.

    Write x=1-d*lambda and a=lambda+x=1-(d-1)lambda.  The extreme
    points are lambda I+x|psi><psi|.  Joint convexity of relative entropy
    allows its maximum over the compact domain to be attained on two extreme
    points; orthogonal |psi>,|phi> maximize it.  Hence

      D_max = x log(a/lambda).

    Since every modular Hamiltonian has spectrum in [-log a,-log lambda],
    the centered oscillation of K_rho-K_sigma is at most log(a/lambda),
    and the same orthogonal pair attains the bound.  Both formulas are exact.
    """
    d = _validate_dimension(dimension)
    floor = float(eigenvalue_floor)
    if not math.isfinite(floor) or not 0.0 < floor <= 1.0 / d:
        raise ValueError("eigenvalue_floor must lie in (0,1/d]")
    residual_mass = max(0.0, 1.0 - d * floor)
    maximum_eigenvalue = floor + residual_mass
    if residual_mass == 0.0:
        log_condition_number = 0.0
    else:
        log_condition_number = math.log(maximum_eigenvalue / floor)
    return {
        "dimension": d,
        "eigenvalue_floor": floor,
        "maximum_eigenvalue": maximum_eigenvalue,
        "residual_extreme_mass": residual_mass,
        "log_condition_number_nats": log_condition_number,
        "exact_relative_entropy_diameter_nats": residual_mass * log_condition_number,
        "exact_centered_modular_oscillation_nats": log_condition_number,
    }


def relative_floor_mass_geometry(*, log_dimension: float, total_floor_mass: float) -> dict[str, float]:
    """Exact sector-simplex geometry when each of K sectors has floor mu/K.

    The input is log(K), which lets the executable stress test represent
    astronomical direct sums without constructing them.  For mu in (0,1],
    lambda=mu/K, x=1-mu, and a=1-mu+mu/K.  Therefore

      L_K^osc = log(a/lambda),
      D_max   = (1-mu) L_K^osc.
    """
    log_d = float(log_dimension)
    mu = float(total_floor_mass)
    if not math.isfinite(log_d) or log_d < math.log(2.0):
        raise ValueError("log_dimension must describe a dimension >= 2")
    if not math.isfinite(mu) or not 0.0 < mu <= 1.0:
        raise ValueError("total_floor_mass must lie in (0,1]")
    inverse_dimension = math.exp(-log_d) if log_d < 745.0 else 0.0
    maximum_weight = 1.0 - mu + mu * inverse_dimension
    if mu == 1.0:
        log_condition_number = 0.0
    else:
        log_condition_number = log_d + math.log(maximum_weight) - math.log(mu)
    return {
        "log_dimension": log_d,
        "total_floor_mass": mu,
        "minimum_sector_weight_log": math.log(mu) - log_d,
        "maximum_sector_weight": maximum_weight,
        "residual_extreme_mass": 1.0 - mu,
        "log_condition_number_nats": log_condition_number,
        "exact_relative_entropy_diameter_nats": (1.0 - mu) * log_condition_number,
        "exact_centered_modular_oscillation_nats": log_condition_number,
    }


def extremal_probability_pair(*, dimension: int, eigenvalue_floor: float) -> tuple[list[float], list[float]]:
    geometry = spectral_floor_domain_geometry(
        dimension=dimension, eigenvalue_floor=eigenvalue_floor
    )
    d = int(geometry["dimension"])
    floor = float(geometry["eigenvalue_floor"])
    maximum = float(geometry["maximum_eigenvalue"])
    left = [floor] * d
    right = [floor] * d
    left[0] = maximum
    right[1] = maximum
    return left, right


def classical_relative_entropy_nats(state: Sequence[float], reference: Sequence[float]) -> float:
    if len(state) != len(reference) or not state:
        raise ValueError("state and reference must have the same nonzero dimension")
    result = 0.0
    for value, baseline in zip(state, reference):
        p = float(value)
        q = float(baseline)
        if p < 0.0 or q < 0.0:
            raise ValueError("probabilities must be non-negative")
        if p == 0.0:
            continue
        if q == 0.0:
            return math.inf
        result += p * math.log(p / q)
    return result


def centered_diagonal_oscillation(values: Sequence[float]) -> float:
    entries = [float(value) for value in values]
    if not entries:
        raise ValueError("values must be non-empty")
    return 0.5 * (max(entries) - min(entries))


def _logsumexp(values: Sequence[float]) -> float:
    entries = [float(value) for value in values]
    if not entries:
        raise ValueError("log-sum-exp input must be non-empty")
    maximum = max(entries)
    return maximum + math.log(sum(math.exp(value - maximum) for value in entries))


def gaussian_sector_log_weights(*, radius: int, curvature: float) -> list[float]:
    """Normalized log weights p_alpha proportional to exp(-s alpha^2)."""
    size = int(radius)
    sharpness = float(curvature)
    if size < 1:
        raise ValueError("radius must be an integer >= 1")
    if not math.isfinite(sharpness) or sharpness <= 0.0:
        raise ValueError("curvature must be positive")
    raw = [-sharpness * float(alpha * alpha) for alpha in range(-size, size + 1)]
    normalization = _logsumexp(raw)
    return [value - normalization for value in raw]


def _nearest_neighbor_columns(
    log_weights: Sequence[float], *, leakage_probability: float, metropolis: bool
) -> tuple[list[dict[int, float]], float]:
    """Return column-stochastic nearest-neighbor sector transport.

    Columns are indexed by the source sector beta and map to target sectors
    alpha.  The symmetric model accepts every nearest-neighbor proposal.  The
    Metropolis model accepts with min(1,p_alpha/p_beta), making the declared
    reference distribution stationary by detailed balance.
    """
    logs = [float(value) for value in log_weights]
    leakage = float(leakage_probability)
    if len(logs) < 3:
        raise ValueError("at least three sectors are required")
    if not 0.0 < leakage < 1.0:
        raise ValueError("leakage_probability must lie in (0,1)")
    columns: list[dict[int, float]] = []
    maximum_off_diagonal = 0.0
    for source in range(len(logs)):
        column: dict[int, float] = {}
        outgoing = 0.0
        for target in (source - 1, source + 1):
            if target < 0 or target >= len(logs):
                continue
            proposal = 0.5 * leakage
            if metropolis:
                acceptance = min(1.0, math.exp(min(0.0, logs[target] - logs[source])))
            else:
                acceptance = 1.0
            transition = proposal * acceptance
            if transition > 0.0:
                column[target] = transition
                outgoing += transition
        column[source] = 1.0 - outgoing
        columns.append(column)
        maximum_off_diagonal = max(maximum_off_diagonal, outgoing)
    return columns, maximum_off_diagonal


def _transport_log_ratios(
    log_weights: Sequence[float], columns: Sequence[dict[int, float]]
) -> list[float]:
    """Compute log[(T p)_alpha/p_alpha] without materializing tiny weights."""
    logs = [float(value) for value in log_weights]
    incoming: list[list[float]] = [[] for _ in logs]
    for source, column in enumerate(columns):
        for target, probability in column.items():
            if probability <= 0.0:
                continue
            incoming[target].append(
                math.log(probability) + logs[source] - logs[target]
            )
    return [_logsumexp(terms) for terms in incoming]


def _transport_total_variation(
    log_weights: Sequence[float], log_ratios: Sequence[float]
) -> tuple[float, float]:
    """Return total variation and normalization residual for q=T p."""
    probabilities = [math.exp(value) if value > -745.0 else 0.0 for value in log_weights]
    outputs = [
        math.exp(log_p + log_ratio) if log_p + log_ratio > -745.0 else 0.0
        for log_p, log_ratio in zip(log_weights, log_ratios)
    ]
    total_variation = 0.5 * sum(abs(output - input_) for output, input_ in zip(outputs, probabilities))
    normalization_residual = abs(sum(outputs) - sum(probabilities))
    return total_variation, normalization_residual


def sector_transport_log_smoothness_probe(
    *,
    radii: Sequence[int],
    gaussian_curvature: float,
    leakage_probability: float,
) -> dict[str, Any]:
    """Exact classical-center probe for the source log-smoothness condition.

    In the commuting sector-label reduction, the dominant diagonal state has
    weights p and sector confusion produces q=T p.  Definition-12
    log-smoothness is then exactly

      epsilon_l-smooth = max_alpha |log(q_alpha/p_alpha)|.

    A tiny per-sector trace-leakage bound therefore controls the operator-log
    error only when the incoming leakage is small relative to the target
    sector weight.  Detailed balance with p is one sufficient completion.
    """
    from benchmark_numeric import linear_slope, stable_number

    sharpness = float(gaussian_curvature)
    leakage = float(leakage_probability)
    rows: list[dict[str, Any]] = []
    for radius_value in radii:
        radius = int(radius_value)
        logs = gaussian_sector_log_weights(radius=radius, curvature=sharpness)
        symmetric_columns, symmetric_leakage = _nearest_neighbor_columns(
            logs, leakage_probability=leakage, metropolis=False
        )
        metropolis_columns, metropolis_leakage = _nearest_neighbor_columns(
            logs, leakage_probability=leakage, metropolis=True
        )
        symmetric_ratios = _transport_log_ratios(logs, symmetric_columns)
        metropolis_ratios = _transport_log_ratios(logs, metropolis_columns)
        symmetric_tv, symmetric_norm = _transport_total_variation(
            logs, symmetric_ratios
        )
        metropolis_tv, metropolis_norm = _transport_total_variation(
            logs, metropolis_ratios
        )
        right_tail_exact = math.log(
            1.0
            - 0.5 * leakage
            + 0.5 * leakage * math.exp(sharpness * (2.0 * radius - 1.0))
        )
        rows.append(
            {
                "radius": radius,
                "sector_count": 2 * radius + 1,
                "minimum_log_sector_weight": stable_number(min(logs)),
                "symmetric_distance_only_transport": {
                    "maximum_per_source_off_diagonal_leakage": stable_number(
                        symmetric_leakage
                    ),
                    "total_variation_between_p_and_Tp": stable_number(symmetric_tv),
                    "exact_log_smoothness_nats": stable_number(
                        max(abs(value) for value in symmetric_ratios)
                    ),
                    "right_tail_exact_log_ratio_nats": stable_number(
                        right_tail_exact
                    ),
                    "maximum_log_relative_inflow_nats": stable_number(
                        max(symmetric_ratios)
                    ),
                    "normalization_residual": stable_number(symmetric_norm),
                },
                "p_stationary_metropolis_transport": {
                    "maximum_per_source_off_diagonal_leakage": stable_number(
                        metropolis_leakage
                    ),
                    "total_variation_between_p_and_Tp": stable_number(metropolis_tv),
                    "exact_log_smoothness_nats": stable_number(
                        max(abs(value) for value in metropolis_ratios)
                    ),
                    "maximum_log_stationarity_residual_nats": stable_number(
                        max(abs(value) for value in metropolis_ratios)
                    ),
                    "normalization_residual": stable_number(metropolis_norm),
                },
            }
        )
    asymptotic_rows = [
        {
            "radius": row["radius"],
            "epsilon": row["symmetric_distance_only_transport"][
                "exact_log_smoothness_nats"
            ],
        }
        for row in rows[-3:]
    ]
    fitted_slope = linear_slope(asymptotic_rows, "radius", "epsilon")
    return {
        "commuting_identity": "For q=T p on the classical sector center, epsilon_l_smooth=max_alpha |log(q_alpha/p_alpha)| exactly.",
        "relative_stationarity_condition": "If zeta=max_alpha |(T p)_alpha/p_alpha-1|<1, then epsilon_l_smooth <= -log(1-zeta). The dimension-free quantity is relative incoming flux, not total trace leakage.",
        "reference_weights": "p_alpha proportional to exp(-s alpha^2) on alpha=-L,...,L",
        "transport_models": {
            "symmetric_distance_only": "A nearest-neighbor proposal leaks tau/2 in each available direction regardless of p.",
            "p_stationary_metropolis": "The same proposal is accepted with min(1,p_alpha/p_beta), so detailed balance makes T p=p.",
        },
        "parameters": {
            "gaussian_curvature_s": sharpness,
            "proposal_leakage_tau": leakage,
            "radii": [int(value) for value in radii],
        },
        "rows": rows,
        "asymptotic_symmetric_log_smoothness_slope_per_radius": stable_number(
            fitted_slope
        ),
        "predicted_tail_slope_per_radius": stable_number(2.0 * sharpness),
        "severe_failure": "A fixed, tiny nearest-neighbor trace leakage can leave total variation near zero while operator-log error diverges in Gaussian tails. Gaussian sector weights plus distance-only decay therefore do not, by themselves, certify global log-smoothness.",
        "constructive_completion": "Require a p-weighted incoming-flux or approximate-stationarity theorem. Exact detailed balance is stronger than necessary but makes the commuting log-smoothness tax identically zero at any sector count.",
    }


def exact_geometry_probe() -> dict[str, Any]:
    """Replay the exact extremizer formulas across several domain sizes."""
    from benchmark_numeric import stable_number

    rows: list[dict[str, Any]] = []
    maximum_entropy_residual = 0.0
    maximum_oscillation_residual = 0.0
    maximum_overlap_grid_excess = 0.0
    for dimension, total_floor_mass in ((2, 0.2), (3, 0.2), (5, 0.2), (8, 0.2)):
        floor = total_floor_mass / dimension
        geometry = spectral_floor_domain_geometry(
            dimension=dimension, eigenvalue_floor=floor
        )
        left, right = extremal_probability_pair(
            dimension=dimension, eigenvalue_floor=floor
        )
        direct_entropy = classical_relative_entropy_nats(left, right)
        modular_difference = [
            -math.log(p) + math.log(q) for p, q in zip(left, right)
        ]
        direct_oscillation = centered_diagonal_oscillation(modular_difference)
        entropy_residual = abs(
            direct_entropy - float(geometry["exact_relative_entropy_diameter_nats"])
        )
        oscillation_residual = abs(
            direct_oscillation
            - float(geometry["exact_centered_modular_oscillation_nats"])
        )
        maximum_entropy_residual = max(maximum_entropy_residual, entropy_residual)
        maximum_oscillation_residual = max(
            maximum_oscillation_residual, oscillation_residual
        )

        # Two depolarized pure-state extremes with squared overlap c have
        # D=x(1-c)log(a/lambda).  The grid verifies that c=0 is maximal.
        x = float(geometry["residual_extreme_mass"])
        log_condition = float(geometry["log_condition_number_nats"])
        exact_maximum = float(geometry["exact_relative_entropy_diameter_nats"])
        for index in range(101):
            overlap_squared = index / 100.0
            value = x * (1.0 - overlap_squared) * log_condition
            maximum_overlap_grid_excess = max(
                maximum_overlap_grid_excess, value - exact_maximum
            )
        rows.append(
            {
                "dimension": dimension,
                "total_floor_mass": total_floor_mass,
                "eigenvalue_floor": stable_number(floor),
                "maximum_eigenvalue": stable_number(
                    geometry["maximum_eigenvalue"]
                ),
                "exact_relative_entropy_diameter_nats": stable_number(
                    geometry["exact_relative_entropy_diameter_nats"]
                ),
                "extremal_pair_relative_entropy_nats": stable_number(
                    direct_entropy
                ),
                "exact_centered_modular_oscillation_nats": stable_number(
                    geometry["exact_centered_modular_oscillation_nats"]
                ),
                "extremal_pair_centered_modular_oscillation_nats": stable_number(
                    direct_oscillation
                ),
            }
        )
    return {
        "domain": "D_{d,lambda}={rho >= lambda I, Tr rho=1}; for the sector-simplex interpretation lambda=mu/d",
        "exact_formulas": {
            "maximum_eigenvalue": "a=1-(d-1)lambda",
            "relative_entropy_diameter": "D_max=(1-d lambda) log(a/lambda)",
            "centered_modular_oscillation": "L_K^osc=log(a/lambda)",
        },
        "source_alignment": "For rho_r=direct_sum_alpha p_alpha rho_r^alpha with identical internal sector states, both quantities reduce exactly to the sector-weight simplex; sector-local epsilon_tail does not bound the p_alpha geometry.",
        "rows": rows,
        "maximum_extremal_entropy_formula_residual": stable_number(
            maximum_entropy_residual
        ),
        "maximum_extremal_oscillation_formula_residual": stable_number(
            maximum_oscillation_residual
        ),
        "maximum_overlap_grid_excess_above_exact_diameter": stable_number(
            maximum_overlap_grid_excess
        ),
    }
