#!/usr/bin/env python3
"""Source-only reconstruction helpers for the spectral anonymity repair.

This script is intentionally compact: it gives auditors the exact chi-squared
identity implementation, the conservative certificate, the normal/reversible
shortcut guard, observation-channel / post-processing / randomized-length visibility checks,
independent-selector visibility checks, adaptive/initiator-correlated selector checks, joint-observation composition checks, adaptive-transcript composition checks, pairwise/session support checks,
post-processing tail-reuse checks, separation-vs-upper-ratio checks, prior-baseline-minimum checks, estimator-certification checks, estimator-confidence/multiplicity checks, success-only/censoring conditioning checks, finite-support truncation-tail checks, empirical mixture-law uncertainty checks, adaptive-transcript history-scope checks, tail/PML/MaxL conversion checks, and the raw sanity-table anchors shipped next to this file.
Rendered plots/logs are not stored in the archive because the archive policy is
source-only for transient render artifacts.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
import numpy as np


def validate_markov_kernel(P: np.ndarray, atol: float = 1e-10) -> None:
    """Fail closed unless P is a finite row-stochastic Markov kernel."""
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be square")
    if np.any(P < -atol):
        raise ValueError("P must be entrywise nonnegative up to tolerance")
    if not np.allclose(P.sum(axis=1), 1.0, atol=atol):
        raise ValueError("P rows must sum to one")


def validate_distribution(q: np.ndarray, n: int, name: str = "distribution", atol: float = 1e-10) -> None:
    """Fail closed unless q is a strictly positive probability vector of length n."""
    q = np.asarray(q, dtype=float)
    if q.shape != (n,):
        raise ValueError(f"{name} must have one entry per state")
    if np.any(q <= 0):
        raise ValueError(f"{name} must be strictly positive")
    if not np.isclose(float(np.sum(q)), 1.0, atol=atol):
        raise ValueError(f"{name} must sum to one")





def observation_channel_expected_chi2(W: np.ndarray, rho: np.ndarray, atol: float = 1e-12) -> float:
    """Exact E_Y[chi^2(Pr[S|Y] || rho)] for a finite observation channel.

    Columns with zero marginal probability are ignored.  This generic identity
    covers fixed-length delegates (W=P^t), hidden randomized length
    (W=sum_t p_t P^t), and visible hopcount (W(s,(t,d))=p_t P^t(s,d)).
    """
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    m = observation_marginal(W, rho)
    support = m > atol
    if not np.any(support):
        raise ValueError("observation marginal has empty support")
    M = (np.sqrt(rho)[:, None] * W[:, support]) / np.sqrt(m[support])[None, :]
    return float(np.linalg.norm(M, "fro") ** 2 - 1.0)


def observation_channel_values(W: np.ndarray, rho: np.ndarray, atol: float = 1e-12) -> tuple[np.ndarray, np.ndarray]:
    """Return chi^2 values X_y and weights m(y) over positive-mass observations."""
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    m = observation_marginal(W, rho)
    support = np.flatnonzero(m > atol)
    values = []
    weights = []
    for y in support:
        posterior = rho * W[:, y] / m[y]
        values.append(float(np.sum(posterior * posterior / rho) - 1.0))
        weights.append(float(m[y]))
    return np.asarray(values, dtype=float), np.asarray(weights, dtype=float)


def observation_channel_moments(W: np.ndarray, rho: np.ndarray) -> dict:
    """Return mean, variance, values, and weights for X_Y=chi^2(Pr[S|Y]||rho)."""
    values, weights = observation_channel_values(W, rho)
    mean = float(np.sum(weights * values))
    variance = float(np.sum(weights * (values - mean) ** 2))
    return {"mean": mean, "variance": variance, "values": values.tolist(), "weights": weights.tolist()}

def validate_kernel(P: np.ndarray, pi: np.ndarray, atol: float = 1e-10) -> None:
    """Fail closed unless P is a Markov kernel with stationary prior pi."""
    P = np.asarray(P, dtype=float)
    pi = np.asarray(pi, dtype=float)
    validate_markov_kernel(P, atol=atol)
    validate_distribution(pi, P.shape[0], name="pi", atol=atol)
    if not np.allclose(pi @ P, pi, atol=atol):
        raise ValueError("pi must be stationary for P")


def discriminant(P: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """Return D = Pi^{1/2} P Pi^{-1/2}."""
    P = np.asarray(P, dtype=float)
    pi = np.asarray(pi, dtype=float)
    validate_kernel(P, pi)
    s = np.sqrt(pi)
    return (s[:, None] * P) / s[None, :]


def exact_expected_chi2(P: np.ndarray, pi: np.ndarray, t: int) -> float:
    """Exact E_D[chi^2(mu_D || pi)] for a stationary t-step delegation chain."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    D = discriminant(P, pi)
    Dt = np.linalg.matrix_power(D, t)
    return float(np.linalg.norm(Dt, "fro") ** 2 - 1.0)


def posterior_expected_chi2_direct(P: np.ndarray, pi: np.ndarray, t: int) -> float:
    """Direct Bayes-sum computation used to cross-check the Frobenius identity."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    validate_kernel(P, pi)
    Pt = np.linalg.matrix_power(np.asarray(P, dtype=float), t)
    pi = np.asarray(pi, dtype=float)
    total = 0.0
    for d in range(Pt.shape[0]):
        mu = pi * Pt[:, d] / pi[d]
        total += pi[d] * (float(np.sum(mu * mu / pi)) - 1.0)
    return float(total)


def prior_delegate_marginal(P: np.ndarray, rho: np.ndarray, t: int) -> np.ndarray:
    """Return m = rho P^t for a non-stationary initiator prior rho."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    P = np.asarray(P, dtype=float)
    rho = np.asarray(rho, dtype=float)
    validate_markov_kernel(P)
    validate_distribution(rho, P.shape[0], name="rho")
    return rho @ np.linalg.matrix_power(P, t)


def prior_expected_chi2_frobenius(P: np.ndarray, rho: np.ndarray, t: int) -> float:
    """Exact E_{D~rho P^t}[chi^2(mu_D || rho)] for an arbitrary full-support prior.

    This is the prior-aware Frobenius identity
        || diag(sqrt(rho)) P^t diag(1/sqrt(m)) ||_F^2 - 1,
    where m = rho P^t.  It reduces to the stationary discriminant identity
    only when rho is stationary and m=rho.
    """
    P = np.asarray(P, dtype=float)
    if t < 0:
        raise ValueError("t must be nonnegative")
    K = np.linalg.matrix_power(P, t)
    return prior_expected_chi2_kernel_frobenius(K, rho)


def posterior_expected_chi2_direct_prior(P: np.ndarray, rho: np.ndarray, t: int) -> float:
    """Direct Bayes-sum check for the arbitrary-prior chi-squared identity."""
    P = np.asarray(P, dtype=float)
    if t < 0:
        raise ValueError("t must be nonnegative")
    K = np.linalg.matrix_power(P, t)
    return posterior_expected_chi2_direct_kernel(K, rho)



def validate_observation_channel(W: np.ndarray, n_starts: int | None = None, atol: float = 1e-10) -> None:
    """Fail closed unless W is a finite row-stochastic observation channel."""
    W = np.asarray(W, dtype=float)
    if W.ndim != 2:
        raise ValueError("W must be a two-dimensional observation channel")
    if n_starts is not None and W.shape[0] != n_starts:
        raise ValueError(f"W must have {n_starts} initiator rows")
    if W.shape[1] == 0:
        raise ValueError("W must have at least one observation column")
    if np.any(W < -atol):
        raise ValueError("W must be entrywise nonnegative up to tolerance")
    if not np.allclose(W.sum(axis=1), 1.0, atol=atol):
        raise ValueError("W rows must sum to one")


def observation_marginal(W: np.ndarray, rho: np.ndarray, atol: float = 1e-10) -> np.ndarray:
    """Return m = rho W for an arbitrary observation channel W."""
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    validate_observation_channel(W, n_starts=rho.shape[0] if rho.ndim == 1 else None, atol=atol)
    validate_distribution(rho, W.shape[0], name="rho", atol=atol)
    m = rho @ W
    if np.any(m < -atol):
        raise ValueError("observation marginal must be nonnegative")
    return np.maximum(m, 0.0)


def prior_expected_chi2_observation_frobenius(W: np.ndarray, rho: np.ndarray) -> float:
    """Exact E_{Y~rho W}[chi^2(Pr[S|Y] || rho)] for any observation channel."""
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    m = observation_marginal(W, rho)
    positive = m > 0
    if not np.any(positive):
        raise ValueError("observation marginal must have nonempty support")
    M = (np.sqrt(rho)[:, None] * W[:, positive]) / np.sqrt(m[positive])[None, :]
    return float(np.linalg.norm(M, "fro") ** 2 - 1.0)


def posterior_expected_chi2_direct_observation(W: np.ndarray, rho: np.ndarray) -> float:
    """Direct Bayes-sum check for the arbitrary observation-channel identity."""
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    m = observation_marginal(W, rho)
    total = 0.0
    for y in range(W.shape[1]):
        if m[y] <= 0:
            continue
        mu = rho * W[:, y] / m[y]
        total += m[y] * (float(np.sum(mu * mu / rho)) - 1.0)
    return float(total)


def postprocess_observation_channel(W: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Return the coarsened channel W R for an observation postprocessor R.

    R is row-stochastic from old observations y to new observations z and is
    independent of the initiator given y. Data processing says the expected
    posterior chi-squared leakage for W R cannot exceed that for W under the
    same initiator prior.
    """
    W = np.asarray(W, dtype=float)
    R = np.asarray(R, dtype=float)
    validate_observation_channel(W)
    if R.ndim != 2 or R.shape[0] != W.shape[1] or R.shape[1] == 0:
        raise ValueError("R must have one row per original observation and at least one output column")
    validate_observation_channel(R, n_starts=W.shape[1])
    Z = W @ R
    validate_observation_channel(Z, n_starts=W.shape[0])
    return Z

def trim_zero_marginal_observations(W: np.ndarray, rho: np.ndarray, atol: float = 1e-12) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """Delete observation columns with zero marginal mass under rho.

    The observation-channel Frobenius identity divides by m(y), so receipt
    surfaces should explicitly work on the positive-marginal support.  Zero-mass
    columns carry no posterior event and do not change the expected chi-squared
    value, but retaining them with an implicit inverse square root is audit-hostile.
    """
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    m = observation_marginal(W, rho, atol=atol)
    keep = np.flatnonzero(m > atol)
    if keep.size == 0:
        raise ValueError("observation marginal has empty positive support")
    trimmed = W[:, keep]
    validate_observation_channel(trimmed, n_starts=W.shape[0], atol=atol)
    return trimmed, m[keep], keep.astype(int).tolist()


def support_trimming_sanity() -> dict:
    """Check that zero-marginal observation columns are ignored, not inverted."""
    rho = np.asarray([0.60, 0.40], dtype=float)
    # The third observation is impossible from every initiator.  It is a common
    # artifact of declaring a large transcript alphabet before all modes are live.
    W = np.asarray([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ], dtype=float)
    validate_observation_channel(W, n_starts=2)
    m = observation_marginal(W, rho)
    trimmed_W, trimmed_m, support = trim_zero_marginal_observations(W, rho)
    expected_full = observation_channel_expected_chi2(W, rho)
    expected_trimmed = observation_channel_expected_chi2(trimmed_W, rho)
    direct_full = posterior_expected_chi2_direct_observation(W, rho)
    direct_trimmed = posterior_expected_chi2_direct_observation(trimmed_W, rho)
    return {
        "zero_marginal_observation_support": {
            "rho": rho.tolist(),
            "channel_with_impossible_column": W.tolist(),
            "observation_marginal": m.tolist(),
            "positive_support_indices": support,
            "trimmed_channel": trimmed_W.tolist(),
            "trimmed_marginal": trimmed_m.tolist(),
            "zero_marginal_column_count": int(np.sum(m <= 1e-12)),
            "expected_chi2_full_support_safe": expected_full,
            "expected_chi2_after_trimming": expected_trimmed,
            "direct_bayes_full_support_safe": direct_full,
            "direct_bayes_after_trimming": direct_trimmed,
            "zero_column_does_not_change_value": bool(np.isclose(expected_full, expected_trimmed) and np.isclose(direct_full, direct_trimmed)),
            "frobenius_matches_direct_after_support_trim": bool(np.isclose(expected_trimmed, direct_trimmed)),
            "receipt_rule": "Observation-channel identities are evaluated only on positive-marginal observations; zero-marginal columns are trimmed before applying diag(m^{-1/2}).",
        }
    }

def prior_delegate_marginal_kernel(K: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """Return m = rho K for an arbitrary row-stochastic delegation kernel K."""
    K = np.asarray(K, dtype=float)
    validate_markov_kernel(K)
    return observation_marginal(K, rho)


def prior_expected_chi2_kernel_frobenius(K: np.ndarray, rho: np.ndarray) -> float:
    """Exact E_{D~rho K}[chi^2(mu_D || rho)] for any delegation kernel K.

    This generic form is the prior-aware witness used for fixed t-step kernels,
    common-stationary schedules after composing K=P_1...P_t, and hidden-length
    mixtures K=sum_t p_t P^t.  It intentionally does not assume rho is
    stationary for K.
    """
    K = np.asarray(K, dtype=float)
    validate_markov_kernel(K)
    return prior_expected_chi2_observation_frobenius(K, rho)


def posterior_expected_chi2_direct_kernel(K: np.ndarray, rho: np.ndarray) -> float:
    """Direct Bayes-sum check for the generic arbitrary-prior kernel identity."""
    K = np.asarray(K, dtype=float)
    validate_markov_kernel(K)
    return posterior_expected_chi2_direct_observation(K, rho)

def validate_kernel_sequence(kernels: list[np.ndarray], pi: np.ndarray, atol: float = 1e-10) -> None:
    """Fail closed unless every kernel shares the same stationary prior pi."""
    if not kernels:
        raise ValueError("kernel sequence must be nonempty")
    n = np.asarray(kernels[0], dtype=float).shape[0]
    for idx, P in enumerate(kernels):
        P = np.asarray(P, dtype=float)
        if P.shape != (n, n):
            raise ValueError(f"kernel {idx} has shape {P.shape}, expected {(n, n)}")
        validate_kernel(P, pi, atol=atol)


def kernel_product(kernels: list[np.ndarray]) -> np.ndarray:
    """Return the row-kernel product P_1 ... P_t in delegation order."""
    if not kernels:
        raise ValueError("kernel sequence must be nonempty")
    product = np.eye(np.asarray(kernels[0], dtype=float).shape[0])
    for P in kernels:
        product = product @ np.asarray(P, dtype=float)
    return product


def discriminant_product(kernels: list[np.ndarray], pi: np.ndarray) -> np.ndarray:
    """Return D_1 ... D_t for a common-stationary inhomogeneous walk."""
    validate_kernel_sequence(kernels, pi)
    product = np.eye(np.asarray(kernels[0], dtype=float).shape[0])
    for P in kernels:
        product = product @ discriminant(P, pi)
    return product


def exact_expected_chi2_sequence(kernels: list[np.ndarray], pi: np.ndarray) -> float:
    """Exact E_D[chi^2(mu_D || pi)] for a common-stationary kernel sequence."""
    M = discriminant_product(kernels, pi)
    return float(np.linalg.norm(M, "fro") ** 2 - 1.0)


def posterior_expected_chi2_direct_sequence(kernels: list[np.ndarray], pi: np.ndarray) -> float:
    """Direct Bayes-sum check for the ordered product P_1 ... P_t."""
    validate_kernel_sequence(kernels, pi)
    K = kernel_product(kernels)
    pi = np.asarray(pi, dtype=float)
    total = 0.0
    for d in range(K.shape[0]):
        mu = pi * K[:, d] / pi[d]
        total += pi[d] * (float(np.sum(mu * mu / pi)) - 1.0)
    return float(total)


def ordered_product_singular_witness(kernels: list[np.ndarray], pi: np.ndarray) -> dict:
    """Return singular values of the actual ordered inhomogeneous product."""
    M = discriminant_product(kernels, pi)
    eta = np.linalg.svd(M, compute_uv=False)
    return {
        "length": len(kernels),
        "eta": eta.tolist(),
        "expected_chi2": float(np.sum(eta[1:] ** 2)),
        "frobenius_expected_chi2": exact_expected_chi2_sequence(kernels, pi),
    }





def exact_expected_chi2_schedule(kernels: list[np.ndarray], pi: np.ndarray) -> float:
    """Exact E_D[chi^2(mu_D || pi)] for a shared-stationary kernel schedule.

    The exact object is the Frobenius norm of the product
    D_1 D_2 ... D_t, not a product/sum of one-step singular values.
    """
    if not kernels:
        return 0.0
    product = np.eye(np.asarray(kernels[0]).shape[0])
    for P in kernels:
        product = product @ discriminant(P, pi)
    return float(np.linalg.norm(product, "fro") ** 2 - 1.0)


def posterior_expected_chi2_direct_schedule(kernels: list[np.ndarray], pi: np.ndarray) -> float:
    """Direct Bayes-sum cross-check for a shared-stationary kernel schedule."""
    if not kernels:
        return 0.0
    pi = np.asarray(pi, dtype=float)
    Pt = np.eye(np.asarray(kernels[0]).shape[0])
    for P in kernels:
        validate_kernel(P, pi)
        Pt = Pt @ np.asarray(P, dtype=float)
    total = 0.0
    for d in range(Pt.shape[0]):
        mu = pi * Pt[:, d] / pi[d]
        total += pi[d] * (float(np.sum(mu * mu / pi)) - 1.0)
    return float(total)


def schedule_conservative_chi2_bound(kernels: list[np.ndarray], pi: np.ndarray) -> float:
    """Conservative shared-stationary schedule bound (n-1) prod_i sigma_2(D_i)^2."""
    if not kernels:
        return 0.0
    n = np.asarray(kernels[0]).shape[0]
    bound = float(n - 1)
    for P in kernels:
        s = np.linalg.svd(discriminant(P, pi), compute_uv=False)
        bound *= float(s[1] ** 2)
    return float(bound)


def schedule_sanity() -> dict:
    """Small exact-vs-direct check for an inhomogeneous shared-stationary schedule."""
    n = 8
    pi = np.full(n, 1 / n)
    kernels = [lazy_cycle_kernel(n), lazy_debruijn_kernel(3), lazy_cycle_kernel(n)]
    exact = exact_expected_chi2_schedule(kernels, pi)
    direct = posterior_expected_chi2_direct_schedule(kernels, pi)
    bound = schedule_conservative_chi2_bound(kernels, pi)
    sigmas = [float(np.linalg.svd(discriminant(P, pi), compute_uv=False)[1]) for P in kernels]
    return {
        "shared_stationary_schedule": {
            "steps": len(kernels),
            "exact_product_frobenius": exact,
            "direct_bayes_sum": direct,
            "conservative_product_bound": bound,
            "one_step_sigma2_values": sigmas,
            "frobenius_matches_direct": bool(np.isclose(exact, direct)),
            "bound_is_conservative": bool(bound + 1e-12 >= exact),
        }
    }

def _length_weight_items(weights: dict[int, float] | list[float] | tuple[float, ...]) -> list[tuple[int, float]]:
    """Normalize finite length weights into sorted (t, p_t) pairs."""
    if isinstance(weights, dict):
        items = [(int(t), float(p)) for t, p in weights.items()]
    else:
        items = [(idx, float(p)) for idx, p in enumerate(weights)]
    if not items:
        raise ValueError("weights must be nonempty")
    for t, prob in items:
        if t < 0:
            raise ValueError("lengths must be nonnegative")
        if prob < -1e-15:
            raise ValueError("weights must be nonnegative")
    total = sum(prob for _, prob in items)
    if not np.isclose(total, 1.0, atol=1e-10):
        raise ValueError("weights must sum to one")
    return sorted((t, max(prob, 0.0)) for t, prob in items if prob > 0.0)


def random_length_mixture_discriminant(P: np.ndarray, pi: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return M_T = sum_t p_t D^t for a hidden randomized length."""
    D = discriminant(P, pi)
    items = _length_weight_items(weights)
    M = np.zeros_like(D)
    for t, prob in items:
        M += prob * np.linalg.matrix_power(D, t)
    return M


def random_length_kernel(P: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return the hidden-length row kernel K_T = sum_t p_t P^t."""
    P = np.asarray(P, dtype=float)
    validate_markov_kernel(P)
    K = np.zeros_like(P)
    for t, prob in _length_weight_items(weights):
        K += prob * np.linalg.matrix_power(P, t)
    validate_markov_kernel(K)
    return K




def revealed_random_length_channel(P: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return the observation channel W(s,(t,d))=p_t P^t(s,d) for visible hopcount."""
    P = np.asarray(P, dtype=float)
    validate_markov_kernel(P)
    items = _length_weight_items(weights)
    n = P.shape[0]
    W = np.zeros((n, n * len(items)), dtype=float)
    for block, (t, prob) in enumerate(items):
        W[:, block * n:(block + 1) * n] = prob * np.linalg.matrix_power(P, t)
    validate_observation_channel(W)
    return W


def exact_expected_chi2_random_length_visible(P: np.ndarray, pi: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> float:
    """Exact E[chi^2] when the adversary observes both delegate and hopcount."""
    validate_kernel(P, pi)
    return observation_channel_expected_chi2(revealed_random_length_channel(P, weights), pi)



def visible_random_length_channel(P: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return W(s,(t,d)) = p_t P^t(s,d) for an observed hopcount/delegate pair."""
    P = np.asarray(P, dtype=float)
    validate_markov_kernel(P)
    blocks = []
    for t, prob in _length_weight_items(weights):
        blocks.append(prob * np.linalg.matrix_power(P, t))
    W = np.concatenate(blocks, axis=1)
    validate_observation_channel(W, n_starts=P.shape[0])
    return W


def drop_visible_length_postprocessor(P: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return R((t,d),d')=1[d=d'], the postprocessor that hides hopcount."""
    P = np.asarray(P, dtype=float)
    validate_markov_kernel(P)
    items = _length_weight_items(weights)
    n = P.shape[0]
    R = np.zeros((n * len(items), n), dtype=float)
    for block, _ in enumerate(items):
        for d in range(n):
            R[block * n + d, d] = 1.0
    validate_observation_channel(R, n_starts=n * len(items))
    return R


def exact_expected_chi2_random_length(P: np.ndarray, pi: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> float:
    """Exact hidden-length E_D[chi^2(mu_D||pi)] via the mixture discriminant."""
    M = random_length_mixture_discriminant(P, pi, weights)
    frob_value = float(np.linalg.norm(M, "fro") ** 2 - 1.0)
    channel_value = observation_channel_expected_chi2(random_length_kernel(P, weights), pi)
    if not np.isclose(frob_value, channel_value):
        raise AssertionError("hidden-length channel and mixture-discriminant values differ")
    return frob_value


def posterior_expected_chi2_direct_random_length(P: np.ndarray, pi: np.ndarray, weights: dict[int, float] | list[float] | tuple[float, ...]) -> float:
    """Direct Bayes-sum cross-check for hidden randomized length."""
    validate_kernel(P, pi)
    return observation_channel_expected_chi2(random_length_kernel(P, weights), pi)


def random_length_sanity() -> dict:
    """Check hidden-vs-visible randomized length semantics and Jensen leakage reduction."""
    P = lazy_debruijn_kernel(3)
    pi = np.full(8, 1 / 8)
    weights = {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}
    exact_hidden = exact_expected_chi2_random_length(P, pi, weights)
    direct_hidden = posterior_expected_chi2_direct_random_length(P, pi, weights)
    hidden_channel = observation_channel_expected_chi2(random_length_kernel(P, weights), pi)
    visible_channel = exact_expected_chi2_random_length_visible(P, pi, weights)
    revealed_average = float(sum(prob * exact_expected_chi2(P, pi, t) for t, prob in _length_weight_items(weights)))

    zero_weights = {0: 0.5, 4: 0.5}
    zero_hidden = exact_expected_chi2_random_length(P, pi, zero_weights)
    zero_visible = exact_expected_chi2_random_length_visible(P, pi, zero_weights)
    zero_revealed_average = float(sum(prob * exact_expected_chi2(P, pi, t) for t, prob in _length_weight_items(zero_weights)))
    return {
        "lazy_debruijn_n8_uniform_T_1_to_4": {
            "weights": {str(t): prob for t, prob in _length_weight_items(weights)},
            "hidden_length_mixture_frobenius": exact_hidden,
            "hidden_length_observation_channel": hidden_channel,
            "direct_bayes_sum": direct_hidden,
            "visible_hopcount_observation_channel": visible_channel,
            "revealed_length_average_expected_chi2": revealed_average,
            "mixture_matches_direct": bool(np.isclose(exact_hidden, direct_hidden)),
            "hidden_channel_matches_mixture": bool(np.isclose(exact_hidden, hidden_channel)),
            "visible_matches_revealed_average": bool(np.isclose(visible_channel, revealed_average)),
            "hidden_no_more_than_revealed_average": bool(exact_hidden <= revealed_average + 1e-12),
        },
        "zero_length_atom_warning": {
            "weights": {str(t): prob for t, prob in _length_weight_items(zero_weights)},
            "hidden_length_expected_chi2": zero_hidden,
            "visible_hopcount_expected_chi2": zero_visible,
            "revealed_length_average_expected_chi2": zero_revealed_average,
            "visible_matches_revealed_average": bool(np.isclose(zero_visible, zero_revealed_average)),
            "zero_atom_retains_short_walk_leakage": bool(zero_hidden > exact_hidden),
        },
    }



def truncation_tail_sanity() -> dict:
    """Show that finite-support truncation of a hidden selector needs tail accounting.

    A common implementation path for countably supported hopcounts/selectors is to
    keep a finite prefix and silently drop or renormalize the remainder.  That is
    not receipt-safe: a small omitted mass can carry an identity-like channel.  A
    conservative fallback is the convexity bound
        L((1-eps) W0 + eps Wtail) <= (1-eps) L(W0) + eps (1/rho_min - 1),
    unless a sharper certified remainder bound is provided.
    """
    n = 4
    rho = np.full(n, 1 / n)
    U = np.full((n, n), 1 / n, dtype=float)  # perfectly private captured prefix
    I = np.eye(n, dtype=float)               # worst-case omitted selector tail
    eps = 0.05
    full_W = (1.0 - eps) * U + eps * I
    captured_only = observation_channel_expected_chi2(U, rho)
    full_value = observation_channel_expected_chi2(full_W, rho)
    direct_full = posterior_expected_chi2_direct_observation(full_W, rho)
    worst_case_cap = (1.0 - eps) * captured_only + eps * (1.0 / float(np.min(rho)) - 1.0)
    omitted_remainder = eps * I
    if not np.isclose(float(omitted_remainder.sum(axis=1)[0]), eps):
        raise AssertionError("tail mass construction changed")
    return {
        "hidden_selector_truncated_tail": {
            "captured_mass": 1.0 - eps,
            "truncation_tail_mass": eps,
            "captured_prefix_expected_chi2": captured_only,
            "full_hidden_mixture_expected_chi2": full_value,
            "direct_bayes_sum_full_mixture": direct_full,
            "convexity_worst_case_cap": worst_case_cap,
            "silent_truncation_understates": bool(captured_only + 1e-12 < full_value),
            "convexity_cap_covers_full": bool(worst_case_cap + 1e-12 >= full_value),
            "tail_mass_requires_remainder_certificate": True,
            "receipt_rule": "Finite truncations of hidden length/selector/transcript supports must serialize truncation_tail_mass and either a certified remainder_chi2_cap or a worst-case reference-min fallback; the renormalized prefix alone is estimate-only for receipt purposes.",
        }
    }


def empirical_mixture_law_sanity() -> dict:
    """Show that plug-in hidden-mixture weights from calibration logs need uncertainty accounting.

    Hidden hopcount/selector mixture identities assume a certified selector law.
    If the law is estimated from finite calibration data, a plug-in frequency can
    miss a rare high-leakage branch.  For zero observed rare-branch samples in N
    Bernoulli trials, the exact one-sided Clopper--Pearson upper bound is
        eps <= 1 - alpha**(1/N).
    A receipt must either use known/protocol weights, evaluate a certified
    confidence set for the weights, or keep the plug-in value as estimate-only.
    """
    n = 4
    rho = np.full(n, 1 / n)
    U = np.full((n, n), 1 / n, dtype=float)
    I = np.eye(n, dtype=float)
    true_eps = 0.05
    calibration_samples = 50
    observed_rare = 0
    alpha = 0.05
    plugin_eps = observed_rare / calibration_samples
    cp_zero_success_ucb = 1.0 - alpha ** (1.0 / calibration_samples)

    plugin_W = (1.0 - plugin_eps) * U + plugin_eps * I
    true_W = (1.0 - true_eps) * U + true_eps * I
    cp_W = (1.0 - cp_zero_success_ucb) * U + cp_zero_success_ucb * I

    plugin_value = observation_channel_expected_chi2(plugin_W, rho)
    true_value = observation_channel_expected_chi2(true_W, rho)
    direct_true = posterior_expected_chi2_direct_observation(true_W, rho)
    cp_exact_cap = observation_channel_expected_chi2(cp_W, rho)
    cp_linear_cap = (1.0 - cp_zero_success_ucb) * observation_channel_expected_chi2(U, rho) + cp_zero_success_ucb * observation_channel_expected_chi2(I, rho)
    zero_count_probability = (1.0 - true_eps) ** calibration_samples

    return {
        "empirical_hidden_selector_weight_uncertainty": {
            "reference_prior": rho.tolist(),
            "private_branch_channel": U.tolist(),
            "rare_identity_branch_channel": I.tolist(),
            "true_rare_branch_weight": true_eps,
            "calibration_sample_count": calibration_samples,
            "observed_rare_branch_count": observed_rare,
            "plug_in_rare_branch_weight": plugin_eps,
            "weight_confidence_alpha": alpha,
            "clopper_pearson_zero_success_weight_ucb": cp_zero_success_ucb,
            "zero_count_probability_under_true_weight": zero_count_probability,
            "plug_in_expected_chi2": plugin_value,
            "true_expected_chi2": true_value,
            "direct_bayes_sum_true_channel": direct_true,
            "ucb_weight_exact_mixture_chi2_cap": cp_exact_cap,
            "ucb_weight_linear_convexity_cap": cp_linear_cap,
            "plug_in_understates_true": bool(plugin_value + 1e-12 < true_value),
            "zero_count_event_plausible_under_true_weight": bool(zero_count_probability > alpha),
            "weight_ucb_covers_true_weight": bool(cp_zero_success_ucb + 1e-12 >= true_eps),
            "ucb_exact_cap_covers_true_chi2": bool(cp_exact_cap + 1e-12 >= true_value),
            "linear_cap_covers_true_chi2": bool(cp_linear_cap + 1e-12 >= true_value),
            "receipt_rule": "Hidden length/selector mixture weights must be protocol-known or carry empirical-law certification: mixture_law_source, calibration_sample_count, observed counts, weight_confidence/alpha, and a worst-case/evaluator-certified leakage bound over the weight confidence set. A plug-in frequency is estimate-only.",
        }
    }


def kernel_model_uncertainty_sanity() -> dict:
    """Show that a plug-in transition/observation model is not a live-kernel certificate.

    The Frobenius and observation-channel identities are exact for the declared
    channel W.  If W is reconstructed from a stale topology snapshot, learned
    transition counts, sampled graph, or approximate stationary distribution, a
    plug-in model can miss a small live identity-like perturbation.  Receipt-grade
    reuse must therefore certify the model itself or take a worst-case/evaluator
    bound over a declared uncertainty set.
    """
    n = 4
    rho = np.full(n, 1 / n)
    uniform_channel = np.full((n, n), 1 / n, dtype=float)
    identity_channel = np.eye(n, dtype=float)
    true_eps = 0.04
    certified_eps_cap = 0.06

    plug_in_channel = uniform_channel
    live_channel = (1.0 - true_eps) * uniform_channel + true_eps * identity_channel
    robust_channel = (1.0 - certified_eps_cap) * uniform_channel + certified_eps_cap * identity_channel

    plug_in_value = observation_channel_expected_chi2(plug_in_channel, rho)
    live_value = observation_channel_expected_chi2(live_channel, rho)
    direct_live = posterior_expected_chi2_direct_observation(live_channel, rho)
    robust_cap = observation_channel_expected_chi2(robust_channel, rho)
    row_l1_drift = float(np.max(np.sum(np.abs(live_channel - plug_in_channel), axis=1)))

    return {
        "plug_in_kernel_snapshot_vs_live_channel": {
            "reference_prior": rho.tolist(),
            "model_scope": "delegate-only observation channel",
            "kernel_source": "plug-in topology/transition snapshot",
            "plug_in_channel": plug_in_channel.tolist(),
            "live_channel": live_channel.tolist(),
            "true_kernel_perturbation_epsilon": true_eps,
            "certified_kernel_epsilon_cap": certified_eps_cap,
            "max_row_l1_drift_from_plugin": row_l1_drift,
            "plug_in_expected_chi2": plug_in_value,
            "live_expected_chi2": live_value,
            "direct_bayes_sum_live_channel": direct_live,
            "uncertainty_set_worst_case_chi2_cap": robust_cap,
            "plug_in_understates_live": bool(plug_in_value + 1e-12 < live_value),
            "live_matches_direct": bool(np.isclose(live_value, direct_live)),
            "robust_cap_covers_live": bool(robust_cap + 1e-12 >= live_value),
            "model_uncertainty_required": True,
            "receipt_rule": "Spectral/observation-channel witnesses are conditional on the declared live kernel/channel. If the transition kernel, graph/topology snapshot, routing weights, observation channel, or stationary distribution is estimated, stale, or learned, serialize kernel_source, model_scope, model_confidence, kernel_uncertainty_set/stationary_residual, and model_uncertainty_policy; the receipt bound must hold over that set or carry an evaluator certificate. A plug-in kernel is estimate-only.",
        }
    }

def numeric_serialization_sanity() -> dict:
    """Show that deterministic numeric rounding/serialization can understate a bound.

    Even when the correct finite-channel value is computed exactly enough for audit
    purposes, a receipt field such as chi2_bound is an upper-bound field.  If the
    value is rounded down, truncated, or emitted without an error budget, the
    serialized number can be smaller than the certified value and the downstream
    PML/MaxL conversion is too optimistic.  Receipt-grade exports therefore need
    an explicit numeric_error_policy, rounding_direction, precision/safety margin,
    or an interval upper endpoint.
    """
    n = 8
    rho = np.full(n, 1 / n)
    uniform_channel = np.full((n, n), 1 / n, dtype=float)
    identity_channel = np.eye(n, dtype=float)
    eps = 0.037
    W = (1.0 - eps) * uniform_channel + eps * identity_channel

    exact_value = observation_channel_expected_chi2(W, rho)
    decimals = 3
    scale = 10 ** decimals
    rounded_down = math.floor(exact_value * scale) / scale
    rounded_up = math.ceil(exact_value * scale) / scale
    deterministic_margin = 1.0 / scale
    margin_cap = rounded_down + deterministic_margin
    reference_min = float(np.min(rho))

    return {
        "decimal_chi2_serialization": {
            "reference_prior": rho.tolist(),
            "identity_mixture_epsilon": eps,
            "exact_expected_chi2": exact_value,
            "serialized_decimal_places": decimals,
            "rounded_down_chi2_bound": rounded_down,
            "rounded_up_chi2_bound": rounded_up,
            "deterministic_safety_margin": deterministic_margin,
            "margin_adjusted_bound": margin_cap,
            "reference_min": reference_min,
            "pml_bits_from_exact_value": pml_bits_from_chi2_bound(exact_value, reference_min),
            "pml_bits_from_rounded_down": pml_bits_from_chi2_bound(rounded_down, reference_min),
            "pml_bits_from_rounded_up": pml_bits_from_chi2_bound(rounded_up, reference_min),
            "rounding_down_understates": bool(rounded_down + 1e-15 < exact_value),
            "upward_rounding_covers": bool(rounded_up + 1e-15 >= exact_value),
            "margin_cap_covers": bool(margin_cap + 1e-15 >= exact_value),
            "pml_understated_by_rounding_down": bool(pml_bits_from_chi2_bound(rounded_down, reference_min) + 1e-15 < pml_bits_from_chi2_bound(exact_value, reference_min)),
            "receipt_rule": "Numeric/serialization exports of upper-bound fields must record numeric_error_policy, rounding_direction, precision_bits or decimal_places, and a safety_margin or interval_upper_endpoint. Rounded-down or tolerance-unqualified chi2_bound/PML/MaxL values are estimate-only, even when the underlying algebra is exact.",
        }
    }


def observation_channel_sanity() -> dict:
    """Check generic observation-channel chi^2 for hidden and visible hopcount."""
    P = lazy_debruijn_kernel(3)
    pi = np.full(8, 1 / 8)
    rho = np.asarray([0.30, 0.20, 0.15, 0.10, 0.08, 0.07, 0.06, 0.04], dtype=float)
    rho = rho / float(np.sum(rho))
    weights = {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}

    hidden_W = random_length_kernel(P, weights)
    visible_W = revealed_random_length_channel(P, weights)

    hidden_stat = observation_channel_expected_chi2(hidden_W, pi)
    visible_stat = observation_channel_expected_chi2(visible_W, pi)
    revealed_average = float(sum(prob * exact_expected_chi2(P, pi, t) for t, prob in _length_weight_items(weights)))
    visible_values, visible_obs_weights = observation_channel_values(visible_W, pi)
    visible_quantile = chi2_tail_bound_from_values(visible_values, visible_obs_weights, 0.05)

    hidden_prior = observation_channel_expected_chi2(hidden_W, rho)
    visible_prior = observation_channel_expected_chi2(visible_W, rho)
    hidden_prior_direct = posterior_expected_chi2_direct_kernel(hidden_W, rho)
    visible_prior_values, visible_prior_weights = observation_channel_values(visible_W, rho)
    visible_prior_direct = float(np.sum(visible_prior_weights * visible_prior_values))

    return {
        "visible_vs_hidden_hopcount_stationary": {
            "weights": {str(t): prob for t, prob in _length_weight_items(weights)},
            "hidden_channel_expected_chi2": hidden_stat,
            "visible_hopcount_expected_chi2": visible_stat,
            "revealed_length_average_expected_chi2": revealed_average,
            "visible_matches_revealed_average": bool(np.isclose(visible_stat, revealed_average)),
            "hidden_no_more_than_visible": bool(hidden_stat <= visible_stat + 1e-12),
            "visible_observation_count": int(visible_W.shape[1]),
            "visible_exact_weighted_quantile_delta_0_05": visible_quantile,
        },
        "visible_vs_hidden_hopcount_biased_prior": {
            "rho": rho.tolist(),
            "hidden_channel_expected_chi2": hidden_prior,
            "hidden_direct_bayes_sum": hidden_prior_direct,
            "visible_hopcount_expected_chi2": visible_prior,
            "visible_direct_bayes_sum": visible_prior_direct,
            "visible_identity_matches_direct": bool(np.isclose(visible_prior, visible_prior_direct)),
            "hidden_identity_matches_direct": bool(np.isclose(hidden_prior, hidden_prior_direct)),
            "hidden_no_more_than_visible": bool(hidden_prior <= visible_prior + 1e-12),
        },
    }


def postprocessing_sanity() -> dict:
    """Check observation-channel data processing / coarsening direction."""
    P = lazy_debruijn_kernel(3)
    pi = np.full(8, 1 / 8)
    rho = np.asarray([0.30, 0.20, 0.15, 0.10, 0.08, 0.07, 0.06, 0.04], dtype=float)
    rho = rho / float(np.sum(rho))
    weights = {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}
    visible_W = visible_random_length_channel(P, weights)
    R_drop_T = drop_visible_length_postprocessor(P, weights)
    coarsened_W = postprocess_observation_channel(visible_W, R_drop_T)
    hidden_W = random_length_kernel(P, weights)

    visible_stat = observation_channel_expected_chi2(visible_W, pi)
    coarsened_stat = observation_channel_expected_chi2(coarsened_W, pi)
    hidden_stat = observation_channel_expected_chi2(hidden_W, pi)
    visible_prior = observation_channel_expected_chi2(visible_W, rho)
    coarsened_prior = observation_channel_expected_chi2(coarsened_W, rho)
    hidden_prior = observation_channel_expected_chi2(hidden_W, rho)

    return {
        "drop_hopcount_postprocessing": {
            "weights": {str(t): prob for t, prob in _length_weight_items(weights)},
            "postprocessor_shape": list(R_drop_T.shape),
            "coarsened_channel_matches_hidden_length_kernel": bool(np.allclose(coarsened_W, hidden_W)),
            "stationary_visible_expected_chi2": visible_stat,
            "stationary_coarsened_expected_chi2": coarsened_stat,
            "stationary_hidden_expected_chi2": hidden_stat,
            "stationary_data_processing_holds": bool(coarsened_stat <= visible_stat + 1e-12),
            "stationary_reverse_reuse_forbidden": bool(hidden_stat + 1e-12 < visible_stat),
            "biased_prior_visible_expected_chi2": visible_prior,
            "biased_prior_coarsened_expected_chi2": coarsened_prior,
            "biased_prior_hidden_expected_chi2": hidden_prior,
            "biased_prior_data_processing_holds": bool(coarsened_prior <= visible_prior + 1e-12),
            "biased_prior_reverse_reuse_forbidden": bool(hidden_prior + 1e-12 < visible_prior),
        }
    }


def _selector_weight_items(weights: dict[int, float] | list[float] | tuple[float, ...], count: int) -> list[tuple[int, float]]:
    """Normalize finite selector weights into sorted (a, q_a) pairs."""
    if count <= 0:
        raise ValueError("selector channel list must be nonempty")
    if isinstance(weights, dict):
        items = [(int(a), float(q)) for a, q in weights.items()]
    else:
        items = [(idx, float(q)) for idx, q in enumerate(weights)]
    if not items:
        raise ValueError("selector weights must be nonempty")
    seen = set()
    for a, prob in items:
        if a < 0 or a >= count:
            raise ValueError("selector index out of range")
        if a in seen:
            raise ValueError("duplicate selector index")
        seen.add(a)
        if prob < -1e-15:
            raise ValueError("selector weights must be nonnegative")
    if seen != set(range(count)):
        raise ValueError("selector weights must cover every channel")
    total = sum(prob for _, prob in items)
    if not np.isclose(total, 1.0, atol=1e-10):
        raise ValueError("selector weights must sum to one")
    return sorted((a, max(prob, 0.0)) for a, prob in items if prob > 0.0)


def hidden_selector_channel(channels: list[np.ndarray], weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return the hidden-selector mixture channel W_hid=sum_a q_a W_a."""
    if not channels:
        raise ValueError("channels must be nonempty")
    arrays = [np.asarray(W, dtype=float) for W in channels]
    first_shape = arrays[0].shape
    for W in arrays:
        if W.shape != first_shape:
            raise ValueError("hidden-selector mixture requires a common observation alphabet")
        validate_observation_channel(W, n_starts=first_shape[0])
    W_mix = np.zeros_like(arrays[0])
    for a, prob in _selector_weight_items(weights, len(arrays)):
        W_mix += prob * arrays[a]
    validate_observation_channel(W_mix, n_starts=first_shape[0])
    return W_mix


def visible_selector_channel(channels: list[np.ndarray], weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return the visible-selector channel W(s,(a,y))=q_a W_a(s,y)."""
    if not channels:
        raise ValueError("channels must be nonempty")
    arrays = [np.asarray(W, dtype=float) for W in channels]
    n_starts = arrays[0].shape[0]
    for W in arrays:
        if W.shape[0] != n_starts:
            raise ValueError("selector channels must share initiator rows")
        validate_observation_channel(W, n_starts=n_starts)
    blocks = []
    for a, prob in _selector_weight_items(weights, len(arrays)):
        blocks.append(prob * arrays[a])
    W_vis = np.concatenate(blocks, axis=1)
    validate_observation_channel(W_vis, n_starts=n_starts)
    return W_vis


def drop_visible_selector_postprocessor(channels: list[np.ndarray], weights: dict[int, float] | list[float] | tuple[float, ...]) -> np.ndarray:
    """Return the postprocessor that hides selector label A while retaining Y."""
    if not channels:
        raise ValueError("channels must be nonempty")
    arrays = [np.asarray(W, dtype=float) for W in channels]
    first_shape = arrays[0].shape
    for W in arrays:
        if W.shape != first_shape:
            raise ValueError("dropping selector label requires a common observation alphabet")
        validate_observation_channel(W, n_starts=first_shape[0])
    m = first_shape[1]
    items = _selector_weight_items(weights, len(arrays))
    R = np.zeros((len(items) * m, m), dtype=float)
    for block, _ in enumerate(items):
        for y in range(m):
            R[block * m + y, y] = 1.0
    validate_observation_channel(R, n_starts=len(items) * m)
    return R


def selector_visibility_sanity() -> dict:
    """Check hidden-vs-visible selector semantics and fail-closed reuse direction."""
    n = 8
    pi = np.full(n, 1.0 / n)
    rho = np.asarray([0.30, 0.20, 0.15, 0.10, 0.08, 0.07, 0.06, 0.04], dtype=float)
    rho = rho / float(np.sum(rho))
    P_cycle = lazy_cycle_kernel(n)
    P_deb = lazy_debruijn_kernel(3)
    # Two common-stationary but noncommuting schedule branches with the same delegate alphabet.
    channels = [P_cycle @ P_deb, P_deb @ P_cycle]
    weights = {0: 0.35, 1: 0.65}
    hidden_W = hidden_selector_channel(channels, weights)
    visible_W = visible_selector_channel(channels, weights)
    R_drop_A = drop_visible_selector_postprocessor(channels, weights)
    coarsened_W = postprocess_observation_channel(visible_W, R_drop_A)

    hidden_stat = observation_channel_expected_chi2(hidden_W, pi)
    visible_stat = observation_channel_expected_chi2(visible_W, pi)
    revealed_average = float(sum(prob * observation_channel_expected_chi2(channels[a], pi) for a, prob in _selector_weight_items(weights, len(channels))))
    hidden_prior = observation_channel_expected_chi2(hidden_W, rho)
    visible_prior = observation_channel_expected_chi2(visible_W, rho)
    revealed_average_prior = float(sum(prob * observation_channel_expected_chi2(channels[a], rho) for a, prob in _selector_weight_items(weights, len(channels))))

    return {
        "two_schedule_branch_selector": {
            "weights": {str(a): prob for a, prob in _selector_weight_items(weights, len(channels))},
            "hidden_selector_expected_chi2": hidden_stat,
            "visible_selector_expected_chi2": visible_stat,
            "revealed_selector_average_expected_chi2": revealed_average,
            "coarsened_channel_matches_hidden_selector": bool(np.allclose(coarsened_W, hidden_W)),
            "visible_matches_revealed_average": bool(np.isclose(visible_stat, revealed_average)),
            "hidden_no_more_than_visible": bool(hidden_stat <= visible_stat + 1e-12),
            "reverse_reuse_forbidden": bool(hidden_stat + 1e-12 < visible_stat),
            "biased_prior_hidden_selector_expected_chi2": hidden_prior,
            "biased_prior_visible_selector_expected_chi2": visible_prior,
            "biased_prior_revealed_average_expected_chi2": revealed_average_prior,
            "biased_prior_visible_matches_revealed_average": bool(np.isclose(visible_prior, revealed_average_prior)),
            "biased_prior_hidden_no_more_than_visible": bool(hidden_prior <= visible_prior + 1e-12),
            "receipt_rule": "A hidden selector mixture cannot be reused when selector identity, schedule branch, latency class, retry mode, or another independent branch label is visible; declare selector_scope and certify the target observation channel.",
        }
    }


def adaptive_selector_sanity() -> dict:
    """Show that initiator-correlated selectors are not independent mixtures.

    A hidden selector mixture sum_a q_a W_a is valid only when A is independent
    of S.  Here A=S chooses a deterministic branch.  Replacing that with the
    unconditional branch frequencies would certify zero leakage, while the true
    hidden observation channel is perfectly revealing.
    """
    rho = np.asarray([0.5, 0.5], dtype=float)
    W0 = np.asarray([[1.0, 0.0], [1.0, 0.0]], dtype=float)
    W1 = np.asarray([[0.0, 1.0], [0.0, 1.0]], dtype=float)
    channels = [W0, W1]
    unconditional_weights = {0: 0.5, 1: 0.5}
    independent_mixture = hidden_selector_channel(channels, unconditional_weights)
    # True hidden channel with A=S: row 0 uses W0, row 1 uses W1.
    true_hidden = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=float)
    # Visible selector is also perfectly revealing in this example.
    true_visible = np.asarray([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype=float)
    naive = observation_channel_expected_chi2(independent_mixture, rho)
    hidden = observation_channel_expected_chi2(true_hidden, rho)
    visible = observation_channel_expected_chi2(true_visible, rho)
    return {
        "initiator_correlated_selector": {
            "rho": rho.tolist(),
            "selector_law": "A=S, not A independent of S",
            "branch_channels": [W0.tolist(), W1.tolist()],
            "unconditional_branch_weights": {str(k): v for k, v in unconditional_weights.items()},
            "naive_independent_hidden_mixture_channel": independent_mixture.tolist(),
            "true_hidden_channel": true_hidden.tolist(),
            "true_visible_channel": true_visible.tolist(),
            "naive_independent_mixture_expected_chi2": naive,
            "true_hidden_expected_chi2": hidden,
            "true_visible_expected_chi2": visible,
            "naive_mixture_understates_leakage": bool(naive + 1e-12 < hidden),
            "true_hidden_reveals_start": bool(hidden > 0.999999),
            "visible_matches_hidden_here": bool(np.isclose(visible, hidden)),
            "receipt_rule": "The hidden-selector mixture sum_a q_a W_a requires selector independence from S/path. Adaptive, path-dependent, or initiator-correlated selectors require the full induced observation channel or evaluator-certified law.",
        }
    }


def kl_divergence(p: np.ndarray, q: np.ndarray, atol: float = 1e-15) -> float:
    """KL(p||q), returning +inf for support mismatch."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if p.shape != q.shape:
        raise ValueError("p and q must have the same shape")
    if np.any(p < -atol) or np.any(q < -atol):
        raise ValueError("probabilities must be nonnegative")
    p = np.maximum(p, 0.0)
    q = np.maximum(q, 0.0)
    if not np.isclose(float(np.sum(p)), 1.0, atol=1e-10) or not np.isclose(float(np.sum(q)), 1.0, atol=1e-10):
        raise ValueError("p and q must sum to one")
    if np.any((p > atol) & (q <= atol)):
        return float("inf")
    mask = p > atol
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def pairwise_session_support_sanity() -> dict:
    """Show that average posterior chi^2 is not a support-safe pairwise/session certificate."""
    rho = np.asarray([0.99, 0.01], dtype=float)
    # A rare initiator occasionally emits a marker impossible under the common initiator.
    W = np.asarray([
        [1.00, 0.00],
        [0.99, 0.01],
    ], dtype=float)
    validate_observation_channel(W, n_starts=2)
    average_chi2 = observation_channel_expected_chi2(W, rho)
    direct_chi2 = posterior_expected_chi2_direct_observation(W, rho)
    kl_rare_common = kl_divergence(W[1], W[0])
    kl_common_rare = kl_divergence(W[0], W[1])
    k = 100
    linked_tv_exact = float(1.0 - (1.0 - W[1, 1]) ** k)
    return {
        "rare_marker_support_mismatch": {
            "rho": rho.tolist(),
            "channel_rows_common_then_rare": W.tolist(),
            "average_posterior_chi2": average_chi2,
            "direct_bayes_average_posterior_chi2": direct_chi2,
            "average_identity_matches_direct": bool(np.isclose(average_chi2, direct_chi2)),
            "average_chi2_below_0_02": bool(average_chi2 < 0.02),
            "kl_rare_vs_common": "inf" if math.isinf(kl_rare_common) else kl_rare_common,
            "kl_common_vs_rare": kl_common_rare,
            "pairwise_kl_infinite_due_to_support": bool(math.isinf(kl_rare_common)),
            "linked_repetitions": k,
            "linked_tv_common_vs_rare_exact": linked_tv_exact,
            "linked_tv_exceeds_0_5": bool(linked_tv_exact > 0.5),
            "receipt_rule": "Pairwise/session endpoints need pairwise laws, support/absolute-continuity evidence, and a linkage model; prior-averaged posterior chi^2 is not by itself a support-safe linked-session certificate.",
        }
    }


def t_step_singular_witness(P: np.ndarray, pi: np.ndarray, t: int) -> dict:
    """Return the direct t-step singular-value witness tau_i(t)."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    D = discriminant(P, pi)
    tau = np.linalg.svd(np.linalg.matrix_power(D, t), compute_uv=False)
    return {
        "t": t,
        "tau": tau.tolist(),
        "expected_chi2": float(np.sum(tau[1:] ** 2)),
        "frobenius_expected_chi2": exact_expected_chi2(P, pi, t),
    }


def conservative_chi2_bound(P: np.ndarray, pi: np.ndarray, t: int) -> float:
    """Conservative directed-chain certificate (n-1) sigma_2(D)^(2t)."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    D = discriminant(P, pi)
    s = np.linalg.svd(D, compute_uv=False)
    return float((P.shape[0] - 1) * s[1] ** (2 * t))


def normal_shortcut_chi2(P: np.ndarray, pi: np.ndarray, t: int, atol: float = 1e-10) -> float:
    """Use sum_{i>=2} sigma_i(D)^(2t), but only after certifying normality."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    D = discriminant(P, pi)
    if not np.allclose(D @ D.T, D.T @ D, atol=atol):
        raise ValueError("normal/reversible certificate absent; use the t-step Frobenius witness")
    s = np.linalg.svd(D, compute_uv=False)
    return float(np.sum(s[1:] ** (2 * t)))


def chi2_tail_bound_from_expectation(expected_chi2: float, delta: float) -> float:
    """Convert E[chi^2] to a 1-delta tail bound by Markov's inequality."""
    if expected_chi2 < 0:
        raise ValueError("expected_chi2 must be nonnegative")
    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0, 1)")
    return float(expected_chi2 / delta)


def chi2_values_over_delegates(P: np.ndarray, pi: np.ndarray, t: int) -> np.ndarray:
    """Return X_d = chi^2(mu_d || pi) for each observed delegate d."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    validate_kernel(P, pi)
    Pt = np.linalg.matrix_power(np.asarray(P, dtype=float), t)
    pi = np.asarray(pi, dtype=float)
    values = []
    for d in range(Pt.shape[0]):
        mu = pi * Pt[:, d] / pi[d]
        values.append(float(np.sum(mu * mu / pi) - 1.0))
    return np.asarray(values, dtype=float)


def chi2_moments_over_delegates(P: np.ndarray, pi: np.ndarray, t: int) -> dict:
    """Return mean and variance of X_D = chi^2(mu_D || pi), D~pi."""
    values = chi2_values_over_delegates(P, pi, t)
    pi = np.asarray(pi, dtype=float)
    mean = float(np.sum(pi * values))
    variance = float(np.sum(pi * (values - mean) ** 2))
    return {"mean": mean, "variance": variance, "values": values.tolist()}


def chi2_tail_bound_from_moments(expected_chi2: float, variance: float, delta: float) -> float:
    """One-sided Chebyshev/Cantelli 1-delta tail bound for chi^2 leakage."""
    if expected_chi2 < 0:
        raise ValueError("expected_chi2 must be nonnegative")
    if variance < -1e-15:
        raise ValueError("variance must be nonnegative")
    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0, 1)")
    variance = max(float(variance), 0.0)
    return float(expected_chi2 + math.sqrt(variance) * math.sqrt(1.0 / delta - 1.0))


def chi2_tail_bound_from_values(values: np.ndarray, weights: np.ndarray, delta: float) -> float:
    """Exact weighted 1-delta upper quantile for enumerated delegate chi^2 values."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if values.ndim != 1 or weights.shape != values.shape:
        raise ValueError("values and weights must be same-length vectors")
    if np.any(values < -1e-15):
        raise ValueError("chi^2 values must be nonnegative")
    if np.any(weights < -1e-15):
        raise ValueError("weights must be nonnegative")
    total = float(np.sum(weights))
    if not np.isclose(total, 1.0, atol=1e-10):
        raise ValueError("weights must sum to one")
    if not 0 < delta < 1:
        raise ValueError("delta must lie in (0, 1)")
    order = np.argsort(values)
    cumulative = 0.0
    target = 1.0 - delta
    for idx in order:
        cumulative += max(float(weights[idx]), 0.0)
        if cumulative + 1e-15 >= target:
            return float(max(values[idx], 0.0))
    return float(max(values[order[-1]], 0.0))


def pml_bits_from_chi2_bound(chi2_bound: float, reference_min: float) -> float:
    """Pointwise/realized odds-inflation cap from a chi-squared bound.

    If the chi-squared bound is only high-probability, this is a high-probability
    PML/odds-inflation envelope, not a channel-level MaxL budget.  Use
    maxl_bits_from_tail_chi2_bound to include the failure-mass fallback.
    """
    if chi2_bound < 0:
        raise ValueError("chi2_bound must be nonnegative")
    if not 0 < reference_min <= 1:
        raise ValueError("reference_min must lie in (0, 1]")
    factor = 1.0 + math.sqrt(chi2_bound / reference_min)
    fallback_factor = 1.0 / reference_min
    return float(math.log2(min(factor, fallback_factor)))


def maxl_bits_from_tail_chi2_bound(chi2_bound: float, reference_min: float, delta: float) -> float:
    """Channel-level MaxL cap from a 1-delta chi-squared tail envelope.

    On the good event, the posterior odds-inflation factor is at most
    1+sqrt(chi2_bound/reference_min); on the failure event, the universal posterior
    ratio cap is 1/reference_min.  The log-moment identity for MaxL then gives the
    mixture/failure-mass fallback below.  For pointwise chi-squared bounds, set
    delta=0.
    """
    if chi2_bound < 0:
        raise ValueError("chi2_bound must be nonnegative")
    if not 0 <= delta < 1:
        raise ValueError("delta must lie in [0, 1)")
    if not 0 < reference_min <= 1:
        raise ValueError("reference_min must lie in (0, 1]")
    good_factor = min(1.0 + math.sqrt(chi2_bound / reference_min), 1.0 / reference_min)
    fallback_factor = 1.0 / reference_min
    return float(math.log2((1.0 - delta) * good_factor + delta * fallback_factor))


def posterior_odds_factors_over_delegates(P: np.ndarray, pi: np.ndarray, t: int) -> np.ndarray:
    """Return max_s mu_d(s)/pi(s), the realized odds-inflation factor for each delegate d."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    validate_kernel(P, pi)
    Pt = np.linalg.matrix_power(np.asarray(P, dtype=float), t)
    pi = np.asarray(pi, dtype=float)
    factors = []
    for d in range(Pt.shape[0]):
        mu = pi * Pt[:, d] / pi[d]
        factors.append(float(np.max(mu / pi)))
    return np.asarray(factors, dtype=float)


def channel_maxl_bits_from_factors(factors: np.ndarray, weights: np.ndarray) -> float:
    """Exact prior-scoped channel MaxL bits from realized odds-inflation factors."""
    factors = np.asarray(factors, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if factors.ndim != 1 or weights.shape != factors.shape:
        raise ValueError("factors and weights must be same-length vectors")
    if np.any(factors < 1.0 - 1e-12):
        raise ValueError("odds-inflation factors should be at least one")
    if np.any(weights < -1e-15) or not np.isclose(float(np.sum(weights)), 1.0, atol=1e-10):
        raise ValueError("weights must be a probability vector")
    return float(math.log2(float(np.sum(weights * factors))))


def observation_channel_odds_factors(W: np.ndarray, rho: np.ndarray, atol: float = 1e-12) -> tuple[np.ndarray, np.ndarray]:
    """Return prior-relative odds factors and observation weights for a finite channel."""
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    m = observation_marginal(W, rho)
    factors = []
    weights = []
    for y in np.flatnonzero(m > atol):
        posterior = rho * W[:, y] / m[y]
        factors.append(float(np.max(posterior / rho)))
        weights.append(float(m[y]))
    if not factors:
        raise ValueError("observation marginal has empty support")
    return np.asarray(factors, dtype=float), np.asarray(weights, dtype=float)


def tail_postprocess_sanity() -> dict:
    """Show that rich-channel exact quantiles need not survive coarsening unchanged.

    Expected chi-squared and channel-level MaxL obey data processing. Pointwise
    chi-squared caps also transfer through post-processing. But a high-probability
    rich-observation quantile is an event over rich observations; after coarsening,
    a small bad rich cell can be merged with good cells and make a larger coarse
    cell exceed the same threshold. Receipt reuse must therefore record the
    endpoint kind and either recompute the target-scope quantile or provide a
    contamination/expectation-to-tail certificate for the coarsened channel.
    """
    rho = np.asarray([0.5, 0.5], dtype=float)
    delta = 0.10
    B = 0.04
    rich_weights = np.asarray([0.10, 0.40, 0.40, 0.10], dtype=float)
    rich_posteriors = np.asarray([
        [0.60, 0.40],  # good, chi^2 = 0.04
        [0.60, 0.40],  # good, chi^2 = 0.04
        [0.50, 0.50],  # good, chi^2 = 0
        [0.00, 1.00],  # bad, chi^2 = 1
    ], dtype=float)
    # Build W(s,y)=Pr[Y=y|S=s] from the desired posterior/marginal pair.
    W = (rich_weights[None, :] * rich_posteriors.T) / rho[:, None]
    validate_observation_channel(W, n_starts=2)
    if not np.allclose(observation_marginal(W, rho), rich_weights):
        raise ValueError("constructed channel has wrong observation marginal")

    # Coarsen by merging the high-leakage cell with one good cell.
    R = np.asarray([
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 1.0],
        [1.0, 0.0],
    ], dtype=float)
    Z = postprocess_observation_channel(W, R)

    rich_values, rich_marginal = observation_channel_values(W, rho)
    coarse_values, coarse_marginal = observation_channel_values(Z, rho)
    rich_expected = float(np.sum(rich_marginal * rich_values))
    coarse_expected = float(np.sum(coarse_marginal * coarse_values))
    rich_quantile = chi2_tail_bound_from_values(rich_values, rich_marginal, delta)
    coarse_quantile = chi2_tail_bound_from_values(coarse_values, coarse_marginal, delta)
    rich_good_mass_at_B = float(np.sum(rich_marginal[rich_values <= B + 1e-12]))
    coarse_good_mass_at_B = float(np.sum(coarse_marginal[coarse_values <= B + 1e-12]))
    rich_pointwise = float(np.max(rich_values))
    coarse_pointwise = float(np.max(coarse_values))
    rich_markov = chi2_tail_bound_from_expectation(rich_expected, delta)
    coarse_good_mass_at_rich_markov = float(np.sum(coarse_marginal[coarse_values <= rich_markov + 1e-12]))
    rich_factors, rich_factor_weights = observation_channel_odds_factors(W, rho)
    coarse_factors, coarse_factor_weights = observation_channel_odds_factors(Z, rho)
    rich_maxl = channel_maxl_bits_from_factors(rich_factors, rich_factor_weights)
    coarse_maxl = channel_maxl_bits_from_factors(coarse_factors, coarse_factor_weights)

    return {
        "source": "Post-processing decreases expected chi^2 and channel MaxL, and pointwise caps transfer, but a rich-channel high-probability quantile/PML good event need not remain valid after coarsening unless the target quantile is recomputed or a contamination/expectation-to-tail certificate is provided.",
        "delta": delta,
        "threshold_B": B,
        "rho": rho.tolist(),
        "rich_observation_weights": rich_marginal.tolist(),
        "rich_posteriors": rich_posteriors.tolist(),
        "rich_chi2_values": rich_values.tolist(),
        "coarsening_matrix": R.tolist(),
        "coarse_observation_weights": coarse_marginal.tolist(),
        "coarse_chi2_values": coarse_values.tolist(),
        "rich_expected_chi2": rich_expected,
        "coarse_expected_chi2": coarse_expected,
        "expected_data_processing_holds": bool(coarse_expected <= rich_expected + 1e-12),
        "rich_exact_quantile_chi2_bound": rich_quantile,
        "coarse_exact_quantile_chi2_bound": coarse_quantile,
        "rich_good_mass_at_B": rich_good_mass_at_B,
        "coarse_good_mass_at_B": coarse_good_mass_at_B,
        "rich_tail_valid_at_B": bool(rich_good_mass_at_B + 1e-12 >= 1.0 - delta),
        "same_B_not_valid_for_coarse_tail": bool(coarse_good_mass_at_B + 1e-12 < 1.0 - delta),
        "rich_pointwise_chi2_cap": rich_pointwise,
        "coarse_pointwise_chi2_cap": coarse_pointwise,
        "pointwise_cap_transfers": bool(coarse_pointwise <= rich_pointwise + 1e-12),
        "rich_markov_tail_bound": rich_markov,
        "coarse_good_mass_at_rich_markov_bound": coarse_good_mass_at_rich_markov,
        "markov_from_rich_expectation_remains_valid_for_coarse": bool(coarse_good_mass_at_rich_markov + 1e-12 >= 1.0 - delta),
        "rich_channel_maxl_bits": rich_maxl,
        "coarse_channel_maxl_bits": coarse_maxl,
        "channel_maxl_data_processing_holds": bool(coarse_maxl <= rich_maxl + 1e-12),
        "receipt_rule": "For coarsened receipt reuse, expected values, pointwise caps, Markov caps derived from richer expectations, and channel-level MaxL caps are safe in the data-processing direction; exact quantiles, Cantelli/moment bounds, and high-probability PML good events should be recomputed on the target channel or paired with a coarsening-contamination certificate.",
    }



def max_relative_density(P: np.ndarray, pi: np.ndarray, t: int) -> float:
    """Return max_{s,d} P^t(s,d)/pi(d), the upper relative-density cap."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    validate_kernel(P, pi)
    Pt = np.linalg.matrix_power(np.asarray(P, dtype=float), t)
    pi = np.asarray(pi, dtype=float)
    return float(np.max(Pt / pi[None, :]))


def separation_distance(P: np.ndarray, pi: np.ndarray, t: int) -> float:
    """Return max_s separation distance 1 - min_d P^t(s,d)/pi(d)."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    validate_kernel(P, pi)
    Pt = np.linalg.matrix_power(np.asarray(P, dtype=float), t)
    pi = np.asarray(pi, dtype=float)
    return float(1.0 - np.min(Pt / pi[None, :]))


def separation_ratio_sanity() -> dict:
    """Show that separation is a lower-coverage diagnostic, not an upper odds cap."""
    n = 64
    pi = np.full(n, 1 / n)
    alpha = 0.05
    P = (1.0 - alpha) * np.ones((n, n), dtype=float) / n + alpha * np.eye(n)
    validate_kernel(P, pi)
    sep = separation_distance(P, pi, 1)
    max_ratio = max_relative_density(P, pi, 1)
    factors = posterior_odds_factors_over_delegates(P, pi, 1)
    maxl_bits = channel_maxl_bits_from_factors(factors, pi)
    return {
        "sticky_teleport_kernel": {
            "n": n,
            "alpha": alpha,
            "separation_distance": sep,
            "max_relative_density": max_ratio,
            "max_relative_density_bits": float(math.log2(max_ratio)),
            "exact_channel_maxl_bits": maxl_bits,
            "separation_small": bool(sep < 0.10),
            "max_ratio_nontrivial": bool(max_ratio > 4.0),
            "maxl_bits_nontrivial": bool(maxl_bits > 2.0),
            "separation_not_upper_ratio_cap": bool(max_ratio > 1.0 / max(1e-12, 1.0 - sep)),
            "reuse_rule": "separation_distance uses a minimum relative density; max-relative-density or pointwise/tail chi2 conversion is required for upper posterior-ratio/PML/MaxL claims",
        }
    }

def prior_baseline_min_sanity() -> dict:
    """Check that chi2-to-PML conversion uses the declared reference prior minimum."""
    rho = np.asarray([0.99, 0.01], dtype=float)
    unrelated_stationary = np.asarray([0.5, 0.5], dtype=float)
    posterior = np.asarray([0.90, 0.10], dtype=float)
    chi2 = float(np.sum((posterior - rho) ** 2 / rho))
    actual_factor = float(np.max(posterior / rho))
    rho_min = float(np.min(rho))
    wrong_min = float(np.min(unrelated_stationary))
    correct_pml = pml_bits_from_chi2_bound(chi2, rho_min)
    wrong_pml = pml_bits_from_chi2_bound(chi2, wrong_min)
    correct_factor_cap = 2.0 ** correct_pml
    wrong_factor_cap = 2.0 ** wrong_pml
    return {
        "biased_prior_reference_minimum": {
            "rho": rho.tolist(),
            "unrelated_stationary_prior": unrelated_stationary.tolist(),
            "posterior": posterior.tolist(),
            "chi2_relative_to_rho": chi2,
            "actual_odds_factor": actual_factor,
            "rho_min": rho_min,
            "unrelated_pi_min": wrong_min,
            "pml_bits_using_rho_min": correct_pml,
            "pml_bits_using_unrelated_pi_min": wrong_pml,
            "factor_cap_using_rho_min": correct_factor_cap,
            "factor_cap_using_unrelated_pi_min": wrong_factor_cap,
            "rho_min_cap_covers_actual_factor": bool(correct_factor_cap + 1e-12 >= actual_factor),
            "unrelated_pi_min_cap_is_unsafe": bool(wrong_factor_cap + 1e-12 < actual_factor),
            "receipt_rule": "For chi2(mu||rho), the PML/MaxL conversion uses min_s rho(s). Stationary pi_min is valid only when pi is the declared reference prior.",
        }
    }


def tail_translation_sanity() -> dict:
    """Demonstrate expectation-to-tail conversion and split PML from MaxL semantics."""
    P = lazy_debruijn_kernel(3)
    pi = np.full(8, 1 / 8)
    t = 4
    delta = 0.05
    moments = chi2_moments_over_delegates(P, pi, t)
    expected = moments["mean"]
    variance = moments["variance"]
    values = np.asarray(moments["values"], dtype=float)
    odds_factors = posterior_odds_factors_over_delegates(P, pi, t)
    exact_channel_maxl = channel_maxl_bits_from_factors(odds_factors, pi)
    markov_tail = chi2_tail_bound_from_expectation(expected, delta)
    cantelli_tail = chi2_tail_bound_from_moments(expected, variance, delta)
    quantile_tail = chi2_tail_bound_from_values(values, pi, delta)
    best_tail = min(markov_tail, cantelli_tail, quantile_tail)
    pi_min = float(np.min(pi))
    pml_markov = pml_bits_from_chi2_bound(markov_tail, pi_min)
    pml_cantelli = pml_bits_from_chi2_bound(cantelli_tail, pi_min)
    pml_quantile = pml_bits_from_chi2_bound(quantile_tail, pi_min)
    maxl_markov = maxl_bits_from_tail_chi2_bound(markov_tail, pi_min, delta)
    maxl_cantelli = maxl_bits_from_tail_chi2_bound(cantelli_tail, pi_min, delta)
    maxl_quantile = maxl_bits_from_tail_chi2_bound(quantile_tail, pi_min, delta)
    pointwise_maxl_from_quantile_bound = maxl_bits_from_tail_chi2_bound(quantile_tail, pi_min, 0.0)
    return {
        "source": "Markov/Cantelli/evaluator quantile give high-probability chi^2 envelopes; PML uses the good-event cap, while MaxL must include the delta failure-mass fallback unless the bound is pointwise.",
        "t": t,
        "delta": delta,
        "expected_chi2": expected,
        "variance_chi2_over_delegates": variance,
        "delegate_chi2_values": values.tolist(),
        "delegate_odds_inflation_factors": odds_factors.tolist(),
        "exact_channel_maxl_bits": exact_channel_maxl,
        "markov_chi2_tail_bound": markov_tail,
        "cantelli_chi2_tail_bound": cantelli_tail,
        "exact_weighted_quantile_chi2_bound": quantile_tail,
        "best_certified_tail_bound": best_tail,
        "cantelli_tighter_than_markov": bool(cantelli_tail < markov_tail),
        "quantile_tighter_than_cantelli": bool(quantile_tail < cantelli_tail),
        "markov_to_cantelli_ratio": float(markov_tail / cantelli_tail),
        "markov_to_quantile_ratio": float(markov_tail / quantile_tail),
        "pi_min": pi_min,
        "pml_bits_markov_good_event": pml_markov,
        "pml_bits_cantelli_good_event": pml_cantelli,
        "pml_bits_exact_quantile_good_event": pml_quantile,
        "maxl_bits_markov_with_failure_fallback": maxl_markov,
        "maxl_bits_cantelli_with_failure_fallback": maxl_cantelli,
        "maxl_bits_exact_quantile_with_failure_fallback": maxl_quantile,
        "maxl_bits_if_quantile_bound_were_pointwise": pointwise_maxl_from_quantile_bound,
        "pml_bits_if_expectation_were_misused": pml_bits_from_chi2_bound(expected, pi_min),
        "tail_bound_not_raw_expectation": bool(best_tail > expected),
        "tail_maxl_includes_failure_mass": bool(maxl_quantile > pml_quantile),
        "exact_channel_maxl_within_quantile_tail_cap": bool(exact_channel_maxl <= maxl_quantile + 1e-12),
    }


def lazy_cycle_kernel(n: int) -> np.ndarray:
    P = np.zeros((n, n), dtype=float)
    for x in range(n):
        P[x, x] += 0.5
        P[x, (x - 1) % n] += 0.25
        P[x, (x + 1) % n] += 0.25
    return P


def lazy_debruijn_kernel(bits: int) -> np.ndarray:
    n = 2 ** bits
    P = np.zeros((n, n), dtype=float)
    mask = n - 1
    for x in range(n):
        P[x, x] += 0.5
        P[x, ((x << 1) & mask) | 0] += 0.25
        P[x, ((x << 1) & mask) | 1] += 0.25
    return P


def nonlazy_debruijn_kernel(bits: int) -> np.ndarray:
    """Directed B(2,bits) shift-register walk, uniform stationary."""
    n = 2 ** bits
    P = np.zeros((n, n), dtype=float)
    mask = n - 1
    for x in range(n):
        P[x, ((x << 1) & mask) | 0] += 0.5
        P[x, ((x << 1) & mask) | 1] += 0.5
    return P


def nonlazy_cycle_kernel(n: int) -> np.ndarray:
    """Nearest-neighbor non-lazy walk on an n-cycle."""
    P = np.zeros((n, n), dtype=float)
    for x in range(n):
        P[x, (x - 1) % n] += 0.5
        P[x, (x + 1) % n] += 0.5
    return P


def block_diag_kernels(*kernels: np.ndarray) -> np.ndarray:
    """Small local block-diagonal helper; avoids scipy dependency."""
    sizes = [np.asarray(K).shape[0] for K in kernels]
    out = np.zeros((sum(sizes), sum(sizes)), dtype=float)
    offset = 0
    for K, size in zip(kernels, sizes):
        out[offset:offset + size, offset:offset + size] = np.asarray(K, dtype=float)
        offset += size
    return out


def identity_sanity() -> dict:
    """Small dense sanity check showing where shortcuts are and are not legal."""
    P_rev = lazy_cycle_kernel(8)
    pi_rev = np.full(8, 1 / 8)
    t_rev = 3
    P_dir = lazy_debruijn_kernel(4)
    pi_dir = np.full(16, 1 / 16)
    t_dir = 4
    D_dir = discriminant(P_dir, pi_dir)
    one_step_dir = np.linalg.svd(D_dir, compute_uv=False)
    bad_shortcut = float(np.sum(one_step_dir[1:] ** (2 * t_dir)))
    forbidden_trace_power = float(np.trace(np.linalg.matrix_power(D_dir.T @ D_dir, t_dir)) - 1.0)
    exact_rev = exact_expected_chi2(P_rev, pi_rev, t_rev)
    exact_dir = exact_expected_chi2(P_dir, pi_dir, t_dir)
    direct_rev = posterior_expected_chi2_direct(P_rev, pi_rev, t_rev)
    direct_dir = posterior_expected_chi2_direct(P_dir, pi_dir, t_dir)

    P_inh_1 = lazy_cycle_kernel(8)
    P_inh_2 = lazy_debruijn_kernel(3)
    pi_inh = np.full(8, 1 / 8)
    exact_inh = exact_expected_chi2_sequence([P_inh_1, P_inh_2], pi_inh)
    direct_inh = posterior_expected_chi2_direct_sequence([P_inh_1, P_inh_2], pi_inh)
    reverse_order_inh = exact_expected_chi2_sequence([P_inh_2, P_inh_1], pi_inh)
    product_commutes = bool(np.allclose(P_inh_1 @ P_inh_2, P_inh_2 @ P_inh_1))

    return {
        "reversible_cycle": {
            "t": t_rev,
            "exact_t_step_frobenius": exact_rev,
            "direct_bayes_sum": direct_rev,
            "normal_shortcut": normal_shortcut_chi2(P_rev, pi_rev, t_rev),
            "frobenius_matches_direct": bool(np.isclose(exact_rev, direct_rev)),
            "shortcut_matches": bool(np.isclose(exact_rev, normal_shortcut_chi2(P_rev, pi_rev, t_rev))),
        },
        "directed_lazy_debruijn": {
            "t": t_dir,
            "exact_t_step_frobenius": exact_dir,
            "direct_bayes_sum": direct_dir,
            "one_step_singular_power_sum_without_certificate": bad_shortcut,
            "forbidden_trace_DtD_power_minus_one": forbidden_trace_power,
            "shortcut_error": bad_shortcut - exact_dir,
            "frobenius_matches_direct": bool(np.isclose(exact_dir, direct_dir)),
            "is_normal": bool(np.allclose(D_dir @ D_dir.T, D_dir.T @ D_dir)),
        },
        "inhomogeneous_common_stationary": {
            "length": 2,
            "exact_ordered_product_frobenius": exact_inh,
            "direct_bayes_sum": direct_inh,
            "reverse_order_product_frobenius": reverse_order_inh,
            "ordered_product_matches_direct": bool(np.isclose(exact_inh, direct_inh)),
            "reverse_order_differs": bool(not np.isclose(exact_inh, reverse_order_inh)),
            "product_commutes": product_commutes,
        },
        "ergodicity_floor_sanity": ergodicity_floor_sanity(),
        "random_length_sanity": random_length_sanity(),
        "truncation_tail_sanity": truncation_tail_sanity(),
        "empirical_mixture_law_sanity": empirical_mixture_law_sanity(),
        "observation_channel_sanity": observation_channel_sanity(),
        "postprocessing_sanity": postprocessing_sanity(),
        "tail_postprocessing_sanity": tail_postprocess_sanity(),
        "support_trimming_sanity": support_trimming_sanity(),
        "selector_visibility_sanity": selector_visibility_sanity(),
        "separation_ratio_sanity": separation_ratio_sanity(),
        "pairwise_session_support_sanity": pairwise_session_support_sanity(),
        "prior_mismatch_sanity": prior_mismatch_sanity(),
        "prior_composition_sanity": prior_composition_sanity(),
        "stop_time_visibility_sanity": stop_time_visibility_sanity(),
    }



def ergodicity_floor_sanity() -> dict:
    """Show floor cases, and separate them from non-normal one-step sigma2=1."""
    P4 = lazy_cycle_kernel(4)
    reducible = block_diag_kernels(P4, P4)
    pi8 = np.full(8, 1 / 8)
    red_s = np.linalg.svd(discriminant(reducible, pi8), compute_uv=False)
    red_t1 = exact_expected_chi2(reducible, pi8, 1)
    red_t32 = exact_expected_chi2(reducible, pi8, 32)

    periodic = nonlazy_cycle_kernel(6)
    pi6 = np.full(6, 1 / 6)
    per_s = np.linalg.svd(discriminant(periodic, pi6), compute_uv=False)
    per_t32 = exact_expected_chi2(periodic, pi6, 32)

    debruijn = nonlazy_debruijn_kernel(4)
    pi16 = np.full(16, 1 / 16)
    deb_s = np.linalg.svd(discriminant(debruijn, pi16), compute_uv=False)
    deb_tm = exact_expected_chi2(debruijn, pi16, 4)
    deb_direct = posterior_expected_chi2_direct(debruijn, pi16, 4)
    return {
        "reducible_two_lazy_4_cycles": {
            "sigma1": float(red_s[0]),
            "sigma2": float(red_s[1]),
            "expected_chi2_t1": red_t1,
            "expected_chi2_t32_floor": red_t32,
            "floor_is_nonzero": bool(red_t32 > 0.999999),
        },
        "periodic_nonlazy_6_cycle": {
            "sigma1": float(per_s[0]),
            "sigma2": float(per_s[1]),
            "expected_chi2_t32_floor": per_t32,
            "floor_is_nonzero": bool(per_t32 > 0.999999),
        },
        "ergodic_nonnormal_nonlazy_debruijn_bits4": {
            "sigma1": float(deb_s[0]),
            "sigma2": float(deb_s[1]),
            "expected_chi2_at_exact_mixing_time": deb_tm,
            "direct_bayes_sum": deb_direct,
            "one_step_sigma2_one_but_no_floor": bool(np.isclose(deb_s[1], 1.0) and np.isclose(deb_tm, 0.0)),
        },
    }


def prior_mismatch_sanity() -> dict:
    """Show that stationary-prior spectral witnesses must not be reused for a mismatched prior."""
    P = lazy_debruijn_kernel(3)
    pi = np.full(8, 1 / 8)
    rho = np.asarray([0.30, 0.20, 0.15, 0.10, 0.08, 0.07, 0.06, 0.04], dtype=float)
    rho = rho / float(np.sum(rho))
    t = 3
    prior_frob = prior_expected_chi2_frobenius(P, rho, t)
    prior_direct = posterior_expected_chi2_direct_prior(P, rho, t)
    stationary_shortcut = exact_expected_chi2(P, pi, t)
    delegate_marginal = prior_delegate_marginal(P, rho, t)
    return {
        "lazy_debruijn_n8_biased_prior": {
            "t": t,
            "rho": rho.tolist(),
            "delegate_marginal": delegate_marginal.tolist(),
            "prior_aware_frobenius_chi2": prior_frob,
            "direct_bayes_sum": prior_direct,
            "stationary_prior_shortcut_chi2": stationary_shortcut,
            "prior_identity_matches_direct": bool(np.isclose(prior_frob, prior_direct)),
            "stationary_shortcut_differs": bool(not np.isclose(prior_frob, stationary_shortcut)),
        }
    }


def prior_composition_sanity() -> dict:
    """Check arbitrary-prior witnesses for schedules and hidden-length mixtures."""
    n = 8
    pi = np.full(n, 1 / n)
    rho = np.asarray([0.30, 0.20, 0.15, 0.10, 0.08, 0.07, 0.06, 0.04], dtype=float)
    rho = rho / float(np.sum(rho))

    kernels = [lazy_cycle_kernel(n), lazy_debruijn_kernel(3), lazy_cycle_kernel(n)]
    K_sched = kernel_product(kernels)
    sched_prior = prior_expected_chi2_kernel_frobenius(K_sched, rho)
    sched_direct = posterior_expected_chi2_direct_kernel(K_sched, rho)
    sched_stationary = exact_expected_chi2_sequence(kernels, pi)

    P = lazy_debruijn_kernel(3)
    weights = {1: 0.20, 2: 0.30, 4: 0.50}
    K_rand = random_length_kernel(P, weights)
    rand_prior = prior_expected_chi2_kernel_frobenius(K_rand, rho)
    rand_direct = posterior_expected_chi2_direct_kernel(K_rand, rho)
    rand_stationary = exact_expected_chi2_random_length(P, pi, weights)

    return {
        "biased_prior_common_stationary_schedule": {
            "steps": len(kernels),
            "rho": rho.tolist(),
            "prior_aware_kernel_frobenius_chi2": sched_prior,
            "direct_bayes_sum": sched_direct,
            "stationary_ordered_product_chi2": sched_stationary,
            "prior_identity_matches_direct": bool(np.isclose(sched_prior, sched_direct)),
            "stationary_shortcut_differs": bool(not np.isclose(sched_prior, sched_stationary)),
        },
        "biased_prior_hidden_length_mixture": {
            "weights": {str(t): prob for t, prob in _length_weight_items(weights)},
            "rho": rho.tolist(),
            "prior_aware_kernel_frobenius_chi2": rand_prior,
            "direct_bayes_sum": rand_direct,
            "stationary_hidden_length_chi2": rand_stationary,
            "prior_identity_matches_direct": bool(np.isclose(rand_prior, rand_direct)),
            "stationary_shortcut_differs": bool(not np.isclose(rand_prior, rand_stationary)),
        },
    }


def stop_time_visibility_sanity() -> dict:
    """Show that an SST can make D perfect while observed stopping time T leaks S."""
    P = np.full((2, 2), 0.5)
    prior = np.full(2, 0.5)
    # Stopping rule: T=1 from start 0, T=2 from start 1.  For each fixed start,
    # X_T is uniform, but T itself is a deterministic start tag.
    e0 = np.asarray([1.0, 0.0])
    e1 = np.asarray([0.0, 1.0])
    d_given_s = np.vstack([e0 @ np.linalg.matrix_power(P, 1), e1 @ np.linalg.matrix_power(P, 2)])
    delegate_channel = d_given_s
    visible_channel = np.asarray([
        [0.5, 0.5, 0.0, 0.0],  # start 0: T=1 and D uniform
        [0.0, 0.0, 0.5, 0.5],  # start 1: T=2 and D uniform
    ])
    delegate_chi2 = observation_channel_expected_chi2(delegate_channel, prior)
    visible_chi2 = observation_channel_expected_chi2(visible_channel, prior)
    t_values = {"0": 1, "1": 2}
    return {
        "two_state_refresh_chain_start_dependent_sst": {
            "P": P.tolist(),
            "prior": prior.tolist(),
            "stopping_rule_T_by_start": t_values,
            "delegate_law_given_start": d_given_s.tolist(),
            "delegate_independent_of_start": bool(np.allclose(d_given_s[0], d_given_s[1]) and np.allclose(d_given_s[0], prior)),
            "observed_T_identifies_start": True,
            "delegate_only_expected_chi2": delegate_chi2,
            "visible_stop_time_expected_chi2": visible_chi2,
            "delegate_only_perfect_but_hopcount_not": bool(np.isclose(delegate_chi2, 0.0) and visible_chi2 > 0.999999),
        }
    }


PAPER_TABLE_ANCHOR_LINES = [
    'Cycle $C_n$ & 2 & 0.999991 & 196657 & 0.1000 & 0.3129 & 539201 \\\\',
    '2D torus ($32\\times 32$) & 4 & 0.995196 & 438 & 0.1000 & 0.4264 & 1054 \\\\',
    'Hypercube $Q_{10}$ & 10 & 0.900000 & 25 & 0.0904 & 0.5634 & 49 \\\\',
    'Chord ring+fingers & 10 & 0.900000 & 18 & 0.0989 & 0.7633 & 49 \\\\',
    'Random 8-regular & 8 & 0.826246 & 15 & 0.0905 & 0.3325 & 27 \\\\',
    'Directed de Bruijn $B(2,10)$ & 2 & 0.988831 & 24 & 0.0769 & 0.1537 & 452 \\\\',
    '0.01 & 0.135986 & 0.046782 & 0.002159 & 0.118898 & 0.041077 & 0.002449 \\\\',
    '0.05 & 0.526431 & 0.263719 & 0.007143 & 0.486559 & 0.237269 & 0.008565 \\\\',
    '0.10 & 0.779561 & 0.587120 & 0.013865 & 0.742507 & 0.534519 & 0.017125 \\\\',
    '0.20 & 0.958342 & 1.365357 & 0.029827 & 0.930654 & 1.236780 & 0.036783 \\\\',
]


def paper_anchor_check() -> dict:
    paper = Path(__file__).resolve().parents[1] / "paper.tex"
    text = paper.read_text(encoding="utf-8")
    missing = [line for line in PAPER_TABLE_ANCHOR_LINES if line not in text]
    return {
        "status": "pass" if not missing else "fail",
        "missing_count": len(missing),
        "checked_lines": len(PAPER_TABLE_ANCHOR_LINES),
        "missing": missing,
    }



def joint_observation_channel(W1: np.ndarray, W2: np.ndarray) -> np.ndarray:
    """Return W(s,(y,z))=W1(s,y)W2(s,z) for conditionally independent observations.

    This is the finite-channel product visible to an observer who sees both
    observations.  It is not a post-processing of either component alone, so a
    receipt for W1 or W2 by itself cannot be promoted to the joint observer.
    """
    W1 = np.asarray(W1, dtype=float)
    W2 = np.asarray(W2, dtype=float)
    if W1.ndim != 2 or W2.ndim != 2 or W1.shape[0] != W2.shape[0]:
        raise ValueError("channels must be two-dimensional with the same initiator rows")
    validate_observation_channel(W1)
    validate_observation_channel(W2, n_starts=W1.shape[0])
    n, m1 = W1.shape
    m2 = W2.shape[1]
    W = np.zeros((n, m1 * m2), dtype=float)
    for s in range(n):
        W[s, :] = np.outer(W1[s, :], W2[s, :]).reshape(-1)
    validate_observation_channel(W, n_starts=n)
    return W


def joint_observation_sanity() -> dict:
    """Show that separately certified observations do not compose by reuse.

    Two conditionally independent noisy side channels, each with modest expected
    posterior chi-squared leakage under the same prior, have a larger joint
    observation-channel leakage when both are visible.  The correct receipt object
    is the product channel (or an evaluator-certified composition), not the max of
    individual certificate values and not a delegate-only certificate promoted to
    a richer transcript.
    """
    rho = np.asarray([0.5, 0.5], dtype=float)
    p1 = 0.60
    p2 = 0.65
    W1 = np.asarray([[p1, 1.0 - p1], [1.0 - p1, p1]], dtype=float)
    W2 = np.asarray([[p2, 1.0 - p2], [1.0 - p2, p2]], dtype=float)
    W_joint = joint_observation_channel(W1, W2)
    leak1 = observation_channel_expected_chi2(W1, rho)
    leak2 = observation_channel_expected_chi2(W2, rho)
    joint = observation_channel_expected_chi2(W_joint, rho)
    direct_joint = posterior_expected_chi2_direct_observation(W_joint, rho)
    return {
        "conditionally_independent_two_channel_composition": {
            "rho": rho.tolist(),
            "channel_1": W1.tolist(),
            "channel_2": W2.tolist(),
            "joint_channel_shape": list(W_joint.shape),
            "expected_chi2_channel_1": leak1,
            "expected_chi2_channel_2": leak2,
            "max_individual_expected_chi2": max(leak1, leak2),
            "sum_individual_expected_chi2": leak1 + leak2,
            "joint_expected_chi2": joint,
            "direct_bayes_joint_expected_chi2": direct_joint,
            "joint_matches_direct": bool(np.isclose(joint, direct_joint)),
            "joint_exceeds_each_individual": bool(joint > max(leak1, leak2) + 1e-12),
            "max_individual_reuse_is_unsafe": bool(max(leak1, leak2) + 1e-12 < joint),
            "joint_not_postprocessing_of_component": True,
            "receipt_rule": "When multiple initiator-dependent observations are jointly visible, materialize the joint observation channel or carry an evaluator-certified composition bound; do not promote an individual or delegate-only witness to the richer joint observer.",
        }
    }


def adaptive_transcript_sanity() -> dict:
    """Show that marginal or per-round witnesses do not certify an adaptive transcript.

    The first observation Y1 is an independent fair bit.  The second channel is
    chosen as a function of the visible history y1 and emits Y2 = S xor y1.  Each
    marginal observation Y1 and Y2 is independent of S under the declared prior,
    so marginal expected chi-squared witnesses are zero.  The transcript
    (Y1,Y2), however, reveals S exactly.  Therefore receipt-side composition for
    history-visible or policy-adaptive rounds must materialize the full transcript
    channel or carry a certified adaptive-composition rule; it cannot reuse
    marginal/initial-prior certificates round by round.
    """
    rho = np.asarray([0.5, 0.5], dtype=float)
    W_y1 = np.asarray([[0.5, 0.5], [0.5, 0.5]], dtype=float)
    W_y2_marginal = np.asarray([[0.5, 0.5], [0.5, 0.5]], dtype=float)
    W_transcript = np.zeros((2, 4), dtype=float)
    for s in range(2):
        for y1 in range(2):
            y2 = s ^ y1
            W_transcript[s, 2 * y1 + y2] += 0.5
    validate_observation_channel(W_transcript, n_starts=2)
    leak_y1 = observation_channel_expected_chi2(W_y1, rho)
    leak_y2_marginal = observation_channel_expected_chi2(W_y2_marginal, rho)
    leak_transcript = observation_channel_expected_chi2(W_transcript, rho)
    direct_transcript = posterior_expected_chi2_direct_observation(W_transcript, rho)
    history_conditioned_round2_leaks = []
    for y1 in range(2):
        W_round2_given_history = np.zeros((2, 2), dtype=float)
        for s in range(2):
            W_round2_given_history[s, s ^ y1] = 1.0
        history_conditioned_round2_leaks.append(observation_channel_expected_chi2(W_round2_given_history, rho))
    return {
        "xor_history_adaptive_transcript": {
            "rho": rho.tolist(),
            "round1_channel": W_y1.tolist(),
            "round2_marginal_channel": W_y2_marginal.tolist(),
            "transcript_columns": ["y1=0,y2=0", "y1=0,y2=1", "y1=1,y2=0", "y1=1,y2=1"],
            "transcript_channel": W_transcript.tolist(),
            "round1_expected_chi2": leak_y1,
            "round2_marginal_expected_chi2": leak_y2_marginal,
            "history_conditioned_round2_expected_chi2": history_conditioned_round2_leaks,
            "transcript_expected_chi2": leak_transcript,
            "direct_bayes_transcript_expected_chi2": direct_transcript,
            "marginals_look_private": bool(np.isclose(leak_y1, 0.0) and np.isclose(leak_y2_marginal, 0.0)),
            "transcript_reveals_start": bool(np.isclose(leak_transcript, 1.0)),
            "transcript_matches_direct": bool(np.isclose(leak_transcript, direct_transcript)),
            "marginal_reuse_is_unsafe": bool(leak_transcript > leak_y1 + leak_y2_marginal + 1e-12),
            "receipt_rule": "History-visible or policy-adaptive multi-round observations must be certified as a full transcript channel, or with a uniform history-conditioned adaptive-composition certificate; marginal/initial-prior per-round witnesses are not enough.",
        }
    }


def hutchinson_trace_estimate(P: np.ndarray, pi: np.ndarray, t: int, samples: int, seed: int = 0) -> dict:
    """Return a compact Hutchinson estimate for ||D^t||_F^2-1.

    This helper intentionally reports an estimate rather than a certificate.  A
    receipt-side upper bound needs a deterministic inequality or a one-sided
    confidence/UCB policy on top of such samples.
    """
    if samples <= 0:
        raise ValueError("samples must be positive")
    D = discriminant(P, pi)
    A = np.linalg.matrix_power(D, t)
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(samples):
        z = rng.choice(np.asarray([-1.0, 1.0]), size=A.shape[1])
        y = A @ z
        values.append(float(np.dot(y, y)))
    values_arr = np.asarray(values, dtype=float)
    estimate = float(np.mean(values_arr) - 1.0)
    sample_sd = float(np.std(values_arr - 1.0, ddof=1)) if samples > 1 else 0.0
    return {
        "samples": samples,
        "seed": seed,
        "values_minus_stationary": (values_arr - 1.0).tolist(),
        "point_estimate_chi2": estimate,
        "sample_standard_deviation": sample_sd,
    }


def estimator_certification_sanity() -> dict:
    """Show that stochastic trace/SVD point estimates are not upper-bound certificates."""
    P = lazy_debruijn_kernel(4)
    pi = np.full(16, 1 / 16)
    t = 4
    exact = exact_expected_chi2(P, pi, t)
    estimate = hutchinson_trace_estimate(P, pi, t=t, samples=16, seed=0)
    point = float(estimate["point_estimate_chi2"])
    markov_tail_if_point_misused = chi2_tail_bound_from_expectation(point, 0.05)
    markov_tail_exact = chi2_tail_bound_from_expectation(exact, 0.05)
    return {
        "hutchinson_point_estimate_not_certificate": {
            "kernel": "lazy_debruijn_bits4",
            "t": t,
            "exact_expected_chi2": exact,
            "hutchinson_samples": estimate["samples"],
            "hutchinson_seed": estimate["seed"],
            "hutchinson_values_minus_stationary": estimate["values_minus_stationary"],
            "hutchinson_point_estimate_chi2": point,
            "sample_standard_deviation": estimate["sample_standard_deviation"],
            "point_estimate_understates_exact": bool(point + 1e-12 < exact),
            "unsafe_markov_tail_if_point_estimate_used": markov_tail_if_point_misused,
            "markov_tail_from_exact_expected_value": markov_tail_exact,
            "unsafe_tail_understates_certified_tail": bool(markov_tail_if_point_misused + 1e-12 < markov_tail_exact),
            "receipt_rule": "Randomized SVD/Hutchinson outputs are estimates. A chi2-general receipt may use them only with a deterministic upper bound or an explicit one-sided confidence/UCB policy, including estimator kind, sample count, seed/replicate policy, confidence, and upper-bound margin; a raw point estimate is estimate-only.",
        }
    }


def estimator_confidence_accounting_sanity() -> dict:
    """Separate estimator confidence from privacy-tail failure probability.

    A one-sided stochastic upper bound is a confidence-qualified statement about
    the evaluator's computation.  A Markov/Cantelli/quantile tail parameter is a
    statement about the observation draw under the declared channel.  Receipts
    should serialize both parameters; collapsing them into the privacy delta makes
    a confidence-qualified estimate look like a deterministic channel certificate.
    """
    P = lazy_debruijn_kernel(4)
    pi = np.full(16, 1 / 16)
    t = 12
    exact = exact_expected_chi2(P, pi, t)
    # Imagine an evaluator has produced a valid one-sided UCB at confidence 1-alpha.
    estimator_alpha = 0.01
    privacy_delta = 0.05
    certified_expected_upper = 1.10 * exact
    reference_min = float(np.min(pi))
    tail_bound = chi2_tail_bound_from_expectation(certified_expected_upper, privacy_delta)
    pml_bits = pml_bits_from_chi2_bound(tail_bound, reference_min)
    maxl_privacy_only = maxl_bits_from_tail_chi2_bound(tail_bound, reference_min, privacy_delta)
    combined_delta_union = min(estimator_alpha + privacy_delta, 1.0 - 1e-15)
    maxl_with_union_budget = maxl_bits_from_tail_chi2_bound(tail_bound, reference_min, combined_delta_union)
    return {
        "hutchinson_ucb_confidence_vs_privacy_delta": {
            "kernel": "lazy_debruijn_bits4",
            "t": t,
            "exact_expected_chi2": exact,
            "certified_expected_upper": certified_expected_upper,
            "estimator_alpha": estimator_alpha,
            "estimator_confidence": 1.0 - estimator_alpha,
            "privacy_tail_delta": privacy_delta,
            "combined_bad_event_union_bound": combined_delta_union,
            "tail_bound_from_certified_upper": tail_bound,
            "reference_min": reference_min,
            "pml_bits_on_privacy_good_event": pml_bits,
            "maxl_bits_if_estimator_bound_were_deterministic": maxl_privacy_only,
            "maxl_bits_with_estimator_union_budget": maxl_with_union_budget,
            "combined_failure_budget_exceeds_privacy_delta": bool(combined_delta_union > privacy_delta),
            "privacy_only_maxl_understates_combined_envelope": bool(maxl_privacy_only + 1e-12 < maxl_with_union_budget),
            "receipt_rule": "Serialize estimator_alpha/confidence separately from privacy_tail_delta. A confidence-qualified stochastic UCB is not an unconditional chi2_bound; either keep the receipt confidence-qualified or union-bound estimator failure with the privacy-tail failure before advertising a single failure-mass endpoint.",
        }
    }



def estimator_multiplicity_sanity() -> dict:
    """Account for model-selection / many-candidate stochastic certificates.

    If an evaluator computes confidence-qualified UCBs for many candidate
    horizons, schedules, trace estimators, or transcript scopes and then chooses
    a candidate after seeing the stochastic outputs, the selected bound is valid
    only on the event that the relevant family of UCBs is simultaneously valid
    (or under an equivalent always-valid/evaluator-certified selection rule).
    A per-candidate estimator_alpha is therefore not the advertised family-level
    alpha unless the receipt records the candidate family and alpha-spending rule.
    """
    candidate_count = 24
    per_candidate_alpha = 0.01
    advertised_family_alpha = 0.01
    privacy_delta = 0.05
    # Independent-failure calculation is illustrative; the safe distribution-free
    # receipt rule is the union bound or a stronger evaluator certificate.
    independent_any_failure = 1.0 - (1.0 - per_candidate_alpha) ** candidate_count
    union_bound_any_failure = min(1.0, candidate_count * per_candidate_alpha)
    bonferroni_alpha_per_candidate = advertised_family_alpha / candidate_count
    sidak_alpha_per_candidate = 1.0 - (1.0 - advertised_family_alpha) ** (1.0 / candidate_count)
    combined_if_misread = min(1.0 - 1e-15, per_candidate_alpha + privacy_delta)
    combined_family_union = min(1.0 - 1e-15, union_bound_any_failure + privacy_delta)
    combined_family_bonferroni = min(1.0 - 1e-15, advertised_family_alpha + privacy_delta)
    return {
        "many_candidate_estimator_selection": {
            "candidate_examples": ["t", "schedule", "random_seed", "trace_estimator", "transcript_scope"],
            "candidate_count": candidate_count,
            "per_candidate_estimator_alpha": per_candidate_alpha,
            "advertised_family_alpha": advertised_family_alpha,
            "privacy_tail_delta": privacy_delta,
            "independent_any_estimator_failure_probability": independent_any_failure,
            "union_bound_any_estimator_failure_probability": union_bound_any_failure,
            "bonferroni_alpha_per_candidate_for_advertised_family_alpha": bonferroni_alpha_per_candidate,
            "sidak_alpha_per_candidate_for_independent_failures": sidak_alpha_per_candidate,
            "combined_failure_if_per_candidate_alpha_misread_as_family_alpha": combined_if_misread,
            "combined_failure_with_family_union_bound": combined_family_union,
            "combined_failure_after_bonferroni_spending": combined_family_bonferroni,
            "unadjusted_per_candidate_alpha_understates_family_failure": bool(independent_any_failure > per_candidate_alpha and union_bound_any_failure > per_candidate_alpha),
            "family_union_exceeds_advertised_alpha": bool(union_bound_any_failure > advertised_family_alpha),
            "bonferroni_spending_recovers_advertised_family_alpha": bool(candidate_count * bonferroni_alpha_per_candidate <= advertised_family_alpha + 1e-15),
            "receipt_rule": "If a stochastic receipt chooses among multiple candidate horizons/schedules/scopes/estimators after seeing estimates, serialize candidate_family, selection_rule, and alpha_spending/family_confidence. A selected UCB is a receipt bound only under simultaneous-validity, Bonferroni/Sidak/always-valid, or evaluator-certified selection evidence; do not treat a per-candidate estimator_alpha as a family-level alpha.",
        }
    }

def condition_observation_channel_on_event(W: np.ndarray, rho: np.ndarray, event_indices: list[int] | tuple[int, ...] | np.ndarray, atol: float = 1e-12) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Condition an observation channel on a visible/post-selected event.

    Given W(s,y), prior rho, and an event C in the observation alphabet, return
    the conditional channel W_C(s,y)=W(s,y)/Pr[C|S=s] for y in C, the conditioned
    reference prior rho_C(s) proportional to rho(s)Pr[C|S=s], the row event
    probabilities, and the prior event probability.  This is the object receipts
    need for success-only logs, abort-filtered transcripts, and retry-censored
    traces.  If some start has zero probability of C, conditioning loses support
    and the caller must fail closed or explicitly restrict the reference prior.
    """
    W = np.asarray(W, dtype=float)
    rho = np.asarray(rho, dtype=float)
    validate_observation_channel(W, n_starts=rho.shape[0] if rho.ndim == 1 else None, atol=atol)
    validate_distribution(rho, W.shape[0], name="rho", atol=atol)
    event = np.asarray(sorted({int(i) for i in event_indices}), dtype=int)
    if event.size == 0:
        raise ValueError("conditioning event must contain at least one observation")
    if np.any(event < 0) or np.any(event >= W.shape[1]):
        raise ValueError("conditioning event index out of range")
    row_prob = np.sum(W[:, event], axis=1)
    if np.any(row_prob <= atol):
        raise ValueError("conditioning event has zero probability for at least one start; restrict support explicitly")
    event_prob = float(np.dot(rho, row_prob))
    if event_prob <= atol:
        raise ValueError("conditioning event has zero prior probability")
    conditioned_prior = rho * row_prob / event_prob
    conditioned_channel = W[:, event] / row_prob[:, None]
    validate_distribution(conditioned_prior, W.shape[0], name="conditioned_prior", atol=atol)
    validate_observation_channel(conditioned_channel, n_starts=W.shape[0], atol=atol)
    return conditioned_channel, conditioned_prior, row_prob, event_prob


def censoring_conditioning_sanity() -> dict:
    """Show why success-only/post-selected transcripts need their own scope.

    Success status is itself an observation channel.  If only successful traces
    are retained, the reference prior changes from rho to rho|success; using the
    unconditional prior minimum or ignoring the success/abort status can silently
    understate receipt-side odds envelopes.
    """
    rho = np.asarray([0.5, 0.5], dtype=float)
    # Columns are [success, abort].  The emitted success-only transcript carries
    # no extra content, but the success event is highly start-dependent.
    status_channel = np.asarray([
        [0.99, 0.01],
        [0.01, 0.99],
    ], dtype=float)
    validate_observation_channel(status_channel, n_starts=2)
    full_status_expected = observation_channel_expected_chi2(status_channel, rho)
    success_channel, success_prior, success_probs, success_prob = condition_observation_channel_on_event(status_channel, rho, [0])
    success_only_expected = observation_channel_expected_chi2(success_channel, success_prior)
    success_posterior_shift = float(np.sum(success_prior * success_prior / rho) - 1.0)
    original_min = float(np.min(rho))
    conditioned_min = float(np.min(success_prior))
    test_bound = 1.0
    pml_with_original_min = pml_bits_from_chi2_bound(test_bound, original_min)
    pml_with_conditioned_min = pml_bits_from_chi2_bound(test_bound, conditioned_min)
    return {
        "success_abort_postselection": {
            "rho": rho.tolist(),
            "status_channel_columns": ["success", "abort"],
            "status_channel": status_channel.tolist(),
            "success_probability_by_start": success_probs.tolist(),
            "success_probability_under_rho": success_prob,
            "conditioned_prior_given_success": success_prior.tolist(),
            "success_only_conditional_channel": success_channel.tolist(),
            "full_status_expected_chi2": full_status_expected,
            "success_only_expected_chi2_wrt_conditioned_prior": success_only_expected,
            "success_event_posterior_shift_chi2_wrt_original_prior": success_posterior_shift,
            "status_channel_captures_selection_leakage": bool(np.isclose(full_status_expected, success_posterior_shift)),
            "success_only_channel_looks_safe_only_after_prior_is_changed": bool(np.isclose(success_only_expected, 0.0) and success_posterior_shift > 0.9),
            "original_prior_min": original_min,
            "conditioned_prior_min": conditioned_min,
            "pml_bits_for_test_bound_using_original_min": pml_with_original_min,
            "pml_bits_for_test_bound_using_conditioned_min": pml_with_conditioned_min,
            "original_min_understates_conditioned_scope": bool(pml_with_original_min + 1e-12 < pml_with_conditioned_min),
            "receipt_rule": "Success-only, abort-filtered, retry-censored, or post-selected traces must declare conditioning_scope/censoring_policy. Include the success/abort status as an observation, or recompute the conditional channel and reference prior rho|C; do not reuse the unconditional witness or prior_min.",
        }
    }

def raw_schema_value_check(raw: dict) -> dict:
    """Check stable raw-anchor values and basic monotonicity/range constraints."""
    findings = []

    def record(name: str, ok: bool, details: str) -> None:
        findings.append({"name": name, "status": "pass" if ok else "fail", "details": details})

    family = raw.get("family_comparison_n1024_lazy", [])
    expected_families = [
        "Cycle C_n",
        "2D torus 32x32",
        "Hypercube Q_10",
        "Chord ring+fingers",
        "Random 8-regular",
        "Directed de Bruijn B(2,10)",
    ]
    record("family_names_order", [r.get("family") for r in family] == expected_families, str([r.get("family") for r in family]))
    record("family_tv_thresholds", all(0 <= float(r.get("tv_at_t", -1)) <= 0.1001 for r in family), "all TV@t values should be at or below 0.1 anchors")
    record("family_predictions_conservative", all(int(r.get("pred_t_0_1", 0)) >= int(r.get("measured_t_0_1", 10**9)) for r in family), "predicted t_0.1 should be no smaller than measured anchors")

    chord = raw.get("chord_scaling_lazy", [])
    record("chord_sizes_order", [r.get("n") for r in chord] == [256, 512, 1024, 2048], str([r.get("n") for r in chord]))
    record("chord_measured_nondec", [r.get("measured_t_0_1") for r in chord] == sorted(r.get("measured_t_0_1") for r in chord), str([r.get("measured_t_0_1") for r in chord]))

    first_hit = raw.get("first_hit_time_hidden_reference", {}).get("rows", [])
    fracs = [r.get("compromised_fraction") for r in first_hit]
    record("first_hit_fraction_grid", fracs == [0.01, 0.05, 0.1, 0.2], str(fracs))
    for prefix in ["chord", "random8"]:
        hits = [float(r[f"{prefix}_hit_le_30"]) for r in first_hit]
        mi = [float(r[f"{prefix}_I_hid_bits"]) for r in first_hit]
        mp = [float(r[f"{prefix}_MAP_hid"]) for r in first_hit]
        record(f"{prefix}_hit_monotone", hits == sorted(hits), str(hits))
        record(f"{prefix}_mi_monotone", mi == sorted(mi), str(mi))
        record(f"{prefix}_map_monotone", mp == sorted(mp), str(mp))

    tv = raw.get("tv_cliff_coordinates", {})
    cycle = tv.get("cycle_C1024_lazy", [])
    debruijn = tv.get("debruijn_B2_10_nonlazy_clipped", [])
    record("cycle_tv_decreasing", all(cycle[i][1] >= cycle[i+1][1] for i in range(len(cycle)-1)), f"points={len(cycle)}")
    record("debruijn_cliff_terminal", debruijn[-3:] == [[10, 0.0001], [11, 0.0001], [12, 0.0001]], str(debruijn[-3:] if debruijn else []))

    trunc = raw.get("truncation_tail_sanity", {}).get("hidden_selector_truncated_tail", {})
    record("truncation_tail_guard", bool(trunc.get("silent_truncation_understates")) and bool(trunc.get("convexity_cap_covers_full")) and bool(trunc.get("tail_mass_requires_remainder_certificate")), json.dumps(trunc, sort_keys=True))

    failed = [f for f in findings if f["status"] != "pass"]
    return {"status": "pass" if not failed else "fail", "checks": findings}

def load_raw_outputs() -> dict:
    return json.loads((Path(__file__).with_name("spectral_sanity_outputs.json")).read_text(encoding="utf-8"))


def check_raw_outputs() -> dict:
    """Validate the compact raw-anchor file without regenerating long logs."""
    raw = load_raw_outputs()
    required = {
        "version",
        "owner",
        "purpose",
        "identity_repair",
        "family_comparison_n1024_lazy",
        "chord_scaling_lazy",
        "first_hit_time_hidden_reference",
        "tv_cliff_coordinates",
        "ergodicity_floor_sanity",
        "random_length_chi2_sanity",
        "truncation_tail_sanity",
        "empirical_mixture_law_sanity",
        "kernel_model_uncertainty_sanity",
        "numeric_serialization_sanity",
        "observation_channel_sanity",
        "postprocessing_sanity",
        "selector_visibility_sanity",
        "adaptive_selector_sanity",
        "separation_ratio_sanity",
        "tail_postprocessing_sanity",
        "support_trimming_sanity",
        "pairwise_session_support_sanity",
        "expected_to_tail_chi2_sanity",
        "prior_baseline_min_sanity",
        "joint_observation_sanity",
        "adaptive_transcript_sanity",
        "estimator_certification_sanity",
        "estimator_confidence_accounting_sanity",
        "estimator_multiplicity_sanity",
        "censoring_conditioning_sanity",
        "prior_mismatch_sanity",
        "prior_composition_sanity",
        "stop_time_visibility_sanity",
    }
    missing = sorted(required - raw.keys())
    family_rows = raw.get("family_comparison_n1024_lazy", [])
    chord_rows = raw.get("chord_scaling_lazy", [])
    first_hit_rows = raw.get("first_hit_time_hidden_reference", {}).get("rows", [])
    tv = raw.get("tv_cliff_coordinates", {})
    findings = []
    findings.append({"name": "required_keys", "status": "pass" if not missing else "fail", "details": "missing=none" if not missing else f"missing={missing}"})
    findings.append({"name": "family_row_count", "status": "pass" if len(family_rows) == 6 else "fail", "details": f"rows={len(family_rows)} expected=6"})
    findings.append({"name": "chord_row_count", "status": "pass" if len(chord_rows) == 4 else "fail", "details": f"rows={len(chord_rows)} expected=4"})
    findings.append({"name": "first_hit_row_count", "status": "pass" if len(first_hit_rows) == 4 else "fail", "details": f"rows={len(first_hit_rows)} expected=4"})
    tv_lengths = {k: len(v) for k, v in tv.items()}
    expected_tv = {"cycle_C1024_lazy", "debruijn_B2_10_nonlazy_clipped"}
    findings.append({"name": "tv_coordinate_sets", "status": "pass" if set(tv) == expected_tv else "fail", "details": json.dumps(tv_lengths, sort_keys=True)})
    identity = identity_sanity()
    sanity_ok = identity["reversible_cycle"]["frobenius_matches_direct"] and identity["directed_lazy_debruijn"]["frobenius_matches_direct"] and not identity["directed_lazy_debruijn"]["is_normal"]
    findings.append({"name": "identity_sanity", "status": "pass" if sanity_ok else "fail", "details": json.dumps(identity, sort_keys=True)})
    schedule = schedule_sanity()
    sched_payload = schedule["shared_stationary_schedule"]
    sched_ok = sched_payload["frobenius_matches_direct"] and sched_payload["bound_is_conservative"]
    findings.append({"name": "schedule_sanity", "status": "pass" if sched_ok else "fail", "details": json.dumps(schedule, sort_keys=True)})
    floor = ergodicity_floor_sanity()
    raw_floor = raw.get("ergodicity_floor_sanity", {})
    floor_ok = floor["reducible_two_lazy_4_cycles"]["floor_is_nonzero"] and floor["periodic_nonlazy_6_cycle"]["floor_is_nonzero"] and floor["ergodic_nonnormal_nonlazy_debruijn_bits4"]["one_step_sigma2_one_but_no_floor"]
    floor_raw_ok = (
        raw_floor.get("reducible_two_lazy_4_cycles", {}).get("floor_is_nonzero") is True
        and raw_floor.get("periodic_nonlazy_6_cycle", {}).get("floor_is_nonzero") is True
        and raw_floor.get("ergodic_nonnormal_nonlazy_debruijn_bits4", {}).get("one_step_sigma2_one_but_no_floor") is True
    )
    findings.append({"name": "ergodicity_floor_sanity", "status": "pass" if floor_ok and floor_raw_ok else "fail", "details": json.dumps({"computed": floor, "raw": raw_floor}, sort_keys=True)})
    randlen = random_length_sanity()
    raw_rand = raw.get("random_length_chi2_sanity", {})
    rand_payload = randlen["lazy_debruijn_n8_uniform_T_1_to_4"]
    raw_rand_payload = raw_rand.get("lazy_debruijn_n8_uniform_T_1_to_4", {})
    zero_payload = randlen["zero_length_atom_warning"]
    raw_zero_payload = raw_rand.get("zero_length_atom_warning", {})
    rand_ok = (
        rand_payload["mixture_matches_direct"]
        and rand_payload["hidden_channel_matches_mixture"]
        and rand_payload["visible_matches_revealed_average"]
        and rand_payload["hidden_no_more_than_revealed_average"]
        and zero_payload["visible_matches_revealed_average"]
        and zero_payload["zero_atom_retains_short_walk_leakage"]
    )
    rand_raw_ok = (
        bool(raw_rand_payload.get("mixture_matches_direct"))
        and bool(raw_rand_payload.get("hidden_channel_matches_mixture"))
        and bool(raw_rand_payload.get("visible_matches_revealed_average"))
        and bool(raw_rand_payload.get("hidden_no_more_than_revealed_average"))
        and bool(raw_zero_payload.get("visible_matches_revealed_average"))
        and bool(raw_zero_payload.get("zero_atom_retains_short_walk_leakage"))
    )
    findings.append({"name": "random_length_sanity", "status": "pass" if rand_ok and rand_raw_ok else "fail", "details": json.dumps({"computed": randlen, "raw": raw_rand}, sort_keys=True)})
    trunc = truncation_tail_sanity()
    raw_trunc = raw.get("truncation_tail_sanity", {})
    trunc_payload = trunc["hidden_selector_truncated_tail"]
    raw_trunc_payload = raw_trunc.get("hidden_selector_truncated_tail", {})
    trunc_ok = (
        trunc_payload["silent_truncation_understates"]
        and trunc_payload["convexity_cap_covers_full"]
        and trunc_payload["tail_mass_requires_remainder_certificate"]
        and np.isclose(trunc_payload["full_hidden_mixture_expected_chi2"], trunc_payload["direct_bayes_sum_full_mixture"])
    )
    trunc_raw_ok = (
        bool(raw_trunc_payload.get("silent_truncation_understates"))
        and bool(raw_trunc_payload.get("convexity_cap_covers_full"))
        and bool(raw_trunc_payload.get("tail_mass_requires_remainder_certificate"))
        and float(raw_trunc_payload.get("truncation_tail_mass", -1.0)) > 0.0
    )
    findings.append({"name": "truncation_tail_sanity", "status": "pass" if trunc_ok and trunc_raw_ok else "fail", "details": json.dumps({"computed": trunc, "raw": raw_trunc}, sort_keys=True)})
    empirical = empirical_mixture_law_sanity()
    raw_empirical = raw.get("empirical_mixture_law_sanity", {})
    emp_payload = empirical["empirical_hidden_selector_weight_uncertainty"]
    raw_emp_payload = raw_empirical.get("empirical_hidden_selector_weight_uncertainty", {})
    emp_ok = (
        emp_payload["plug_in_understates_true"]
        and emp_payload["zero_count_event_plausible_under_true_weight"]
        and emp_payload["weight_ucb_covers_true_weight"]
        and emp_payload["ucb_exact_cap_covers_true_chi2"]
        and emp_payload["linear_cap_covers_true_chi2"]
        and np.isclose(emp_payload["true_expected_chi2"], emp_payload["direct_bayes_sum_true_channel"])
    )
    emp_raw_ok = (
        bool(raw_emp_payload.get("plug_in_understates_true"))
        and bool(raw_emp_payload.get("zero_count_event_plausible_under_true_weight"))
        and bool(raw_emp_payload.get("weight_ucb_covers_true_weight"))
        and bool(raw_emp_payload.get("ucb_exact_cap_covers_true_chi2"))
        and bool(raw_emp_payload.get("linear_cap_covers_true_chi2"))
        and "plug-in" in raw_emp_payload.get("receipt_rule", "")
    )
    findings.append({"name": "empirical_mixture_law_sanity", "status": "pass" if emp_ok and emp_raw_ok else "fail", "details": json.dumps({"computed": empirical, "raw": raw_empirical}, sort_keys=True)})
    kernel_model = kernel_model_uncertainty_sanity()
    raw_kernel_model = raw.get("kernel_model_uncertainty_sanity", {})
    kernel_payload = kernel_model["plug_in_kernel_snapshot_vs_live_channel"]
    raw_kernel_payload = raw_kernel_model.get("plug_in_kernel_snapshot_vs_live_channel", {})
    kernel_ok = (
        kernel_payload["plug_in_understates_live"]
        and kernel_payload["live_matches_direct"]
        and kernel_payload["robust_cap_covers_live"]
        and kernel_payload["model_uncertainty_required"]
    )
    kernel_raw_ok = (
        bool(raw_kernel_payload.get("plug_in_understates_live"))
        and bool(raw_kernel_payload.get("live_matches_direct"))
        and bool(raw_kernel_payload.get("robust_cap_covers_live"))
        and bool(raw_kernel_payload.get("model_uncertainty_required"))
        and "kernel_source" in raw_kernel_payload.get("receipt_rule", "")
        and "plug-in" in raw_kernel_payload.get("receipt_rule", "")
    )
    findings.append({"name": "kernel_model_uncertainty_sanity", "status": "pass" if kernel_ok and kernel_raw_ok else "fail", "details": json.dumps({"computed": kernel_model, "raw": raw_kernel_model}, sort_keys=True)})
    numeric = numeric_serialization_sanity()
    raw_numeric = raw.get("numeric_serialization_sanity", {})
    numeric_payload = numeric["decimal_chi2_serialization"]
    raw_numeric_payload = raw_numeric.get("decimal_chi2_serialization", {})
    numeric_ok = (
        numeric_payload["rounding_down_understates"]
        and numeric_payload["upward_rounding_covers"]
        and numeric_payload["margin_cap_covers"]
        and numeric_payload["pml_understated_by_rounding_down"]
    )
    numeric_raw_ok = (
        bool(raw_numeric_payload.get("rounding_down_understates"))
        and bool(raw_numeric_payload.get("upward_rounding_covers"))
        and bool(raw_numeric_payload.get("margin_cap_covers"))
        and bool(raw_numeric_payload.get("pml_understated_by_rounding_down"))
        and "numeric_error_policy" in raw_numeric_payload.get("receipt_rule", "")
        and "rounding_direction" in raw_numeric_payload.get("receipt_rule", "")
    )
    findings.append({"name": "numeric_serialization_sanity", "status": "pass" if numeric_ok and numeric_raw_ok else "fail", "details": json.dumps({"computed": numeric, "raw": raw_numeric}, sort_keys=True)})
    obs = observation_channel_sanity()
    raw_obs = raw.get("observation_channel_sanity", {})
    obs_stat = obs["visible_vs_hidden_hopcount_stationary"]
    obs_prior = obs["visible_vs_hidden_hopcount_biased_prior"]
    raw_obs_stat = raw_obs.get("visible_vs_hidden_hopcount_stationary", {})
    raw_obs_prior = raw_obs.get("visible_vs_hidden_hopcount_biased_prior", {})
    obs_ok = (
        obs_stat["visible_matches_revealed_average"]
        and obs_stat["hidden_no_more_than_visible"]
        and obs_prior["visible_identity_matches_direct"]
        and obs_prior["hidden_identity_matches_direct"]
        and obs_prior["hidden_no_more_than_visible"]
    )
    obs_raw_ok = (
        bool(raw_obs_stat.get("visible_matches_revealed_average"))
        and bool(raw_obs_stat.get("hidden_no_more_than_visible"))
        and bool(raw_obs_prior.get("visible_identity_matches_direct"))
        and bool(raw_obs_prior.get("hidden_identity_matches_direct"))
        and bool(raw_obs_prior.get("hidden_no_more_than_visible"))
    )
    findings.append({"name": "observation_channel_sanity", "status": "pass" if obs_ok and obs_raw_ok else "fail", "details": json.dumps({"computed": obs, "raw": raw_obs}, sort_keys=True)})
    post = postprocessing_sanity()
    raw_post = raw.get("postprocessing_sanity", {})
    post_payload = post["drop_hopcount_postprocessing"]
    raw_post_payload = raw_post.get("drop_hopcount_postprocessing", {})
    post_ok = (
        post_payload["coarsened_channel_matches_hidden_length_kernel"]
        and post_payload["stationary_data_processing_holds"]
        and post_payload["stationary_reverse_reuse_forbidden"]
        and post_payload["biased_prior_data_processing_holds"]
        and post_payload["biased_prior_reverse_reuse_forbidden"]
    )
    post_raw_ok = (
        bool(raw_post_payload.get("coarsened_channel_matches_hidden_length_kernel"))
        and bool(raw_post_payload.get("stationary_data_processing_holds"))
        and bool(raw_post_payload.get("stationary_reverse_reuse_forbidden"))
        and bool(raw_post_payload.get("biased_prior_data_processing_holds"))
        and bool(raw_post_payload.get("biased_prior_reverse_reuse_forbidden"))
    )
    findings.append({"name": "postprocessing_sanity", "status": "pass" if post_ok and post_raw_ok else "fail", "details": json.dumps({"computed": post, "raw": raw_post}, sort_keys=True)})
    tail_post = tail_postprocess_sanity()
    raw_tail_post = raw.get("tail_postprocessing_sanity", {})
    tail_post_ok = (
        tail_post["expected_data_processing_holds"]
        and tail_post["rich_tail_valid_at_B"]
        and tail_post["same_B_not_valid_for_coarse_tail"]
        and tail_post["pointwise_cap_transfers"]
        and tail_post["markov_from_rich_expectation_remains_valid_for_coarse"]
        and tail_post["channel_maxl_data_processing_holds"]
    )
    tail_post_raw_ok = (
        bool(raw_tail_post.get("expected_data_processing_holds"))
        and bool(raw_tail_post.get("rich_tail_valid_at_B"))
        and bool(raw_tail_post.get("same_B_not_valid_for_coarse_tail"))
        and bool(raw_tail_post.get("pointwise_cap_transfers"))
        and bool(raw_tail_post.get("markov_from_rich_expectation_remains_valid_for_coarse"))
        and bool(raw_tail_post.get("channel_maxl_data_processing_holds"))
    )
    findings.append({"name": "tail_postprocessing_sanity", "status": "pass" if tail_post_ok and tail_post_raw_ok else "fail", "details": json.dumps({"computed": tail_post, "raw": raw_tail_post}, sort_keys=True)})
    support_trim = support_trimming_sanity()
    raw_support_trim = raw.get("support_trimming_sanity", {})
    support_payload = support_trim["zero_marginal_observation_support"]
    raw_support_payload = raw_support_trim.get("zero_marginal_observation_support", {})
    support_ok = (
        support_payload["zero_marginal_column_count"] == 1
        and support_payload["zero_column_does_not_change_value"]
        and support_payload["frobenius_matches_direct_after_support_trim"]
    )
    support_raw_ok = (
        int(raw_support_payload.get("zero_marginal_column_count", -1)) == 1
        and bool(raw_support_payload.get("zero_column_does_not_change_value"))
        and bool(raw_support_payload.get("frobenius_matches_direct_after_support_trim"))
    )
    findings.append({"name": "support_trimming_sanity", "status": "pass" if support_ok and support_raw_ok else "fail", "details": json.dumps({"computed": support_trim, "raw": raw_support_trim}, sort_keys=True)})
    selector = selector_visibility_sanity()
    raw_selector = raw.get("selector_visibility_sanity", {})
    selector_payload = selector["two_schedule_branch_selector"]
    raw_selector_payload = raw_selector.get("two_schedule_branch_selector", {})
    selector_ok = (
        selector_payload["coarsened_channel_matches_hidden_selector"]
        and selector_payload["visible_matches_revealed_average"]
        and selector_payload["hidden_no_more_than_visible"]
        and selector_payload["reverse_reuse_forbidden"]
        and selector_payload["biased_prior_visible_matches_revealed_average"]
        and selector_payload["biased_prior_hidden_no_more_than_visible"]
    )
    selector_raw_ok = (
        bool(raw_selector_payload.get("coarsened_channel_matches_hidden_selector"))
        and bool(raw_selector_payload.get("visible_matches_revealed_average"))
        and bool(raw_selector_payload.get("hidden_no_more_than_visible"))
        and bool(raw_selector_payload.get("reverse_reuse_forbidden"))
        and bool(raw_selector_payload.get("biased_prior_visible_matches_revealed_average"))
        and bool(raw_selector_payload.get("biased_prior_hidden_no_more_than_visible"))
    )
    findings.append({"name": "selector_visibility_sanity", "status": "pass" if selector_ok and selector_raw_ok else "fail", "details": json.dumps({"computed": selector, "raw": raw_selector}, sort_keys=True)})
    adaptive = adaptive_selector_sanity()
    raw_adaptive = raw.get("adaptive_selector_sanity", {})
    adaptive_payload = adaptive["initiator_correlated_selector"]
    raw_adaptive_payload = raw_adaptive.get("initiator_correlated_selector", {})
    adaptive_ok = (
        adaptive_payload["naive_mixture_understates_leakage"]
        and adaptive_payload["true_hidden_reveals_start"]
        and adaptive_payload["visible_matches_hidden_here"]
    )
    adaptive_raw_ok = (
        bool(raw_adaptive_payload.get("naive_mixture_understates_leakage"))
        and bool(raw_adaptive_payload.get("true_hidden_reveals_start"))
        and bool(raw_adaptive_payload.get("visible_matches_hidden_here"))
    )
    findings.append({"name": "adaptive_selector_sanity", "status": "pass" if adaptive_ok and adaptive_raw_ok else "fail", "details": json.dumps({"computed": adaptive, "raw": raw_adaptive}, sort_keys=True)})
    ratio = separation_ratio_sanity()
    raw_ratio = raw.get("separation_ratio_sanity", {})
    ratio_payload = ratio["sticky_teleport_kernel"]
    raw_ratio_payload = raw_ratio.get("sticky_teleport_kernel", {})
    ratio_ok = (
        ratio_payload["separation_small"]
        and ratio_payload["max_ratio_nontrivial"]
        and ratio_payload["maxl_bits_nontrivial"]
        and ratio_payload["separation_not_upper_ratio_cap"]
    )
    ratio_raw_ok = (
        bool(raw_ratio_payload.get("separation_small"))
        and bool(raw_ratio_payload.get("max_ratio_nontrivial"))
        and bool(raw_ratio_payload.get("maxl_bits_nontrivial"))
        and bool(raw_ratio_payload.get("separation_not_upper_ratio_cap"))
    )
    findings.append({"name": "separation_ratio_sanity", "status": "pass" if ratio_ok and ratio_raw_ok else "fail", "details": json.dumps({"computed": ratio, "raw": raw_ratio}, sort_keys=True)})
    pairwise = pairwise_session_support_sanity()
    raw_pairwise = raw.get("pairwise_session_support_sanity", {})
    pairwise_payload = pairwise["rare_marker_support_mismatch"]
    raw_pairwise_payload = raw_pairwise.get("rare_marker_support_mismatch", {})
    pairwise_ok = (
        pairwise_payload["average_identity_matches_direct"]
        and pairwise_payload["average_chi2_below_0_02"]
        and pairwise_payload["pairwise_kl_infinite_due_to_support"]
        and pairwise_payload["linked_tv_exceeds_0_5"]
    )
    pairwise_raw_ok = (
        bool(raw_pairwise_payload.get("average_identity_matches_direct"))
        and bool(raw_pairwise_payload.get("average_chi2_below_0_02"))
        and bool(raw_pairwise_payload.get("pairwise_kl_infinite_due_to_support"))
        and bool(raw_pairwise_payload.get("linked_tv_exceeds_0_5"))
    )
    findings.append({"name": "pairwise_session_support_sanity", "status": "pass" if pairwise_ok and pairwise_raw_ok else "fail", "details": json.dumps({"computed": pairwise, "raw": raw_pairwise}, sort_keys=True)})
    tail = tail_translation_sanity()
    raw_tail = raw.get("expected_to_tail_chi2_sanity", {})
    tail_ok = (
        tail["tail_bound_not_raw_expectation"]
        and tail["cantelli_tighter_than_markov"]
        and tail["quantile_tighter_than_cantelli"]
        and tail["tail_maxl_includes_failure_mass"]
        and tail["exact_channel_maxl_within_quantile_tail_cap"]
        and tail["pml_bits_exact_quantile_good_event"] < tail["pml_bits_cantelli_good_event"] <= tail["pml_bits_markov_good_event"]
        and tail["maxl_bits_exact_quantile_with_failure_fallback"] < tail["maxl_bits_cantelli_with_failure_fallback"] <= tail["maxl_bits_markov_with_failure_fallback"]
        and tail["maxl_bits_exact_quantile_with_failure_fallback"] > tail["pml_bits_exact_quantile_good_event"]
    )
    tail_raw_ok = (
        bool(raw_tail.get("tail_bound_not_raw_expectation"))
        and bool(raw_tail.get("cantelli_tighter_than_markov"))
        and bool(raw_tail.get("quantile_tighter_than_cantelli"))
        and bool(raw_tail.get("tail_maxl_includes_failure_mass"))
        and bool(raw_tail.get("exact_channel_maxl_within_quantile_tail_cap"))
        and raw_tail.get("pml_bits_exact_quantile_good_event", 999) < raw_tail.get("pml_bits_cantelli_good_event", 999) <= raw_tail.get("pml_bits_markov_good_event", -1)
        and raw_tail.get("maxl_bits_exact_quantile_with_failure_fallback", 999) < raw_tail.get("maxl_bits_cantelli_with_failure_fallback", 999) <= raw_tail.get("maxl_bits_markov_with_failure_fallback", -1)
        and raw_tail.get("maxl_bits_exact_quantile_with_failure_fallback", -1) > raw_tail.get("pml_bits_exact_quantile_good_event", 999)
    )
    findings.append({"name": "tail_translation_sanity", "status": "pass" if tail_ok and tail_raw_ok else "fail", "details": json.dumps({"computed": tail, "raw": raw_tail}, sort_keys=True)})
    baseline = prior_baseline_min_sanity()
    raw_baseline = raw.get("prior_baseline_min_sanity", {})
    baseline_payload = baseline["biased_prior_reference_minimum"]
    raw_baseline_payload = raw_baseline.get("biased_prior_reference_minimum", {})
    baseline_ok = (
        baseline_payload["rho_min_cap_covers_actual_factor"]
        and baseline_payload["unrelated_pi_min_cap_is_unsafe"]
    )
    baseline_raw_ok = (
        bool(raw_baseline_payload.get("rho_min_cap_covers_actual_factor"))
        and bool(raw_baseline_payload.get("unrelated_pi_min_cap_is_unsafe"))
    )
    findings.append({"name": "prior_baseline_min_sanity", "status": "pass" if baseline_ok and baseline_raw_ok else "fail", "details": json.dumps({"computed": baseline, "raw": raw_baseline}, sort_keys=True)})
    joint_obs = joint_observation_sanity()
    raw_joint_obs = raw.get("joint_observation_sanity", {})
    joint_payload = joint_obs["conditionally_independent_two_channel_composition"]
    raw_joint_payload = raw_joint_obs.get("conditionally_independent_two_channel_composition", {})
    joint_ok = (
        joint_payload["joint_matches_direct"]
        and joint_payload["joint_exceeds_each_individual"]
        and joint_payload["max_individual_reuse_is_unsafe"]
    )
    joint_raw_ok = (
        bool(raw_joint_payload.get("joint_matches_direct"))
        and bool(raw_joint_payload.get("joint_exceeds_each_individual"))
        and bool(raw_joint_payload.get("max_individual_reuse_is_unsafe"))
    )
    findings.append({"name": "joint_observation_sanity", "status": "pass" if joint_ok and joint_raw_ok else "fail", "details": json.dumps({"computed": joint_obs, "raw": raw_joint_obs}, sort_keys=True)})
    adaptive_transcript = adaptive_transcript_sanity()
    raw_adaptive_transcript = raw.get("adaptive_transcript_sanity", {})
    transcript_payload = adaptive_transcript["xor_history_adaptive_transcript"]
    raw_transcript_payload = raw_adaptive_transcript.get("xor_history_adaptive_transcript", {})
    transcript_ok = (
        transcript_payload["marginals_look_private"]
        and transcript_payload["transcript_reveals_start"]
        and transcript_payload["transcript_matches_direct"]
        and transcript_payload["marginal_reuse_is_unsafe"]
    )
    transcript_raw_ok = (
        bool(raw_transcript_payload.get("marginals_look_private"))
        and bool(raw_transcript_payload.get("transcript_reveals_start"))
        and bool(raw_transcript_payload.get("transcript_matches_direct"))
        and bool(raw_transcript_payload.get("marginal_reuse_is_unsafe"))
    )
    findings.append({"name": "adaptive_transcript_sanity", "status": "pass" if transcript_ok and transcript_raw_ok else "fail", "details": json.dumps({"computed": adaptive_transcript, "raw": raw_adaptive_transcript}, sort_keys=True)})
    estimator = estimator_certification_sanity()
    raw_estimator = raw.get("estimator_certification_sanity", {})
    estimator_payload = estimator["hutchinson_point_estimate_not_certificate"]
    raw_estimator_payload = raw_estimator.get("hutchinson_point_estimate_not_certificate", {})
    estimator_ok = (
        estimator_payload["point_estimate_understates_exact"]
        and estimator_payload["unsafe_tail_understates_certified_tail"]
    )
    estimator_raw_ok = (
        bool(raw_estimator_payload.get("point_estimate_understates_exact"))
        and bool(raw_estimator_payload.get("unsafe_tail_understates_certified_tail"))
    )
    findings.append({"name": "estimator_certification_sanity", "status": "pass" if estimator_ok and estimator_raw_ok else "fail", "details": json.dumps({"computed": estimator, "raw": raw_estimator}, sort_keys=True)})
    estimator_conf = estimator_confidence_accounting_sanity()
    raw_estimator_conf = raw.get("estimator_confidence_accounting_sanity", {})
    estimator_conf_payload = estimator_conf["hutchinson_ucb_confidence_vs_privacy_delta"]
    raw_estimator_conf_payload = raw_estimator_conf.get("hutchinson_ucb_confidence_vs_privacy_delta", {})
    estimator_conf_ok = (
        estimator_conf_payload["combined_failure_budget_exceeds_privacy_delta"]
        and estimator_conf_payload["privacy_only_maxl_understates_combined_envelope"]
    )
    estimator_conf_raw_ok = (
        bool(raw_estimator_conf_payload.get("combined_failure_budget_exceeds_privacy_delta"))
        and bool(raw_estimator_conf_payload.get("privacy_only_maxl_understates_combined_envelope"))
    )
    findings.append({"name": "estimator_confidence_accounting_sanity", "status": "pass" if estimator_conf_ok and estimator_conf_raw_ok else "fail", "details": json.dumps({"computed": estimator_conf, "raw": raw_estimator_conf}, sort_keys=True)})
    multiplicity = estimator_multiplicity_sanity()
    raw_multiplicity = raw.get("estimator_multiplicity_sanity", {})
    multiplicity_payload = multiplicity["many_candidate_estimator_selection"]
    raw_multiplicity_payload = raw_multiplicity.get("many_candidate_estimator_selection", {})
    multiplicity_ok = (
        multiplicity_payload["unadjusted_per_candidate_alpha_understates_family_failure"]
        and multiplicity_payload["family_union_exceeds_advertised_alpha"]
        and multiplicity_payload["bonferroni_spending_recovers_advertised_family_alpha"]
    )
    multiplicity_raw_ok = (
        bool(raw_multiplicity_payload.get("unadjusted_per_candidate_alpha_understates_family_failure"))
        and bool(raw_multiplicity_payload.get("family_union_exceeds_advertised_alpha"))
        and bool(raw_multiplicity_payload.get("bonferroni_spending_recovers_advertised_family_alpha"))
    )
    findings.append({"name": "estimator_multiplicity_sanity", "status": "pass" if multiplicity_ok and multiplicity_raw_ok else "fail", "details": json.dumps({"computed": multiplicity, "raw": raw_multiplicity}, sort_keys=True)})
    censoring = censoring_conditioning_sanity()
    raw_censoring = raw.get("censoring_conditioning_sanity", {})
    censor_payload = censoring["success_abort_postselection"]
    raw_censor_payload = raw_censoring.get("success_abort_postselection", {})
    censor_ok = (
        censor_payload["status_channel_captures_selection_leakage"]
        and censor_payload["success_only_channel_looks_safe_only_after_prior_is_changed"]
        and censor_payload["original_min_understates_conditioned_scope"]
    )
    censor_raw_ok = (
        bool(raw_censor_payload.get("status_channel_captures_selection_leakage"))
        and bool(raw_censor_payload.get("success_only_channel_looks_safe_only_after_prior_is_changed"))
        and bool(raw_censor_payload.get("original_min_understates_conditioned_scope"))
    )
    findings.append({"name": "censoring_conditioning_sanity", "status": "pass" if censor_ok and censor_raw_ok else "fail", "details": json.dumps({"computed": censoring, "raw": raw_censoring}, sort_keys=True)})
    prior = prior_mismatch_sanity()
    raw_prior = raw.get("prior_mismatch_sanity", {})
    prior_payload = prior["lazy_debruijn_n8_biased_prior"]
    raw_prior_payload = raw_prior.get("lazy_debruijn_n8_biased_prior", {})
    prior_ok = prior_payload["prior_identity_matches_direct"] and prior_payload["stationary_shortcut_differs"]
    prior_raw_ok = bool(raw_prior_payload.get("prior_identity_matches_direct")) and bool(raw_prior_payload.get("stationary_shortcut_differs"))
    findings.append({"name": "prior_mismatch_sanity", "status": "pass" if prior_ok and prior_raw_ok else "fail", "details": json.dumps({"computed": prior, "raw": raw_prior}, sort_keys=True)})
    prior_comp = prior_composition_sanity()
    raw_prior_comp = raw.get("prior_composition_sanity", {})
    sched_payload = prior_comp["biased_prior_common_stationary_schedule"]
    rand_payload = prior_comp["biased_prior_hidden_length_mixture"]
    raw_sched_payload = raw_prior_comp.get("biased_prior_common_stationary_schedule", {})
    raw_rand_payload = raw_prior_comp.get("biased_prior_hidden_length_mixture", {})
    prior_comp_ok = (
        sched_payload["prior_identity_matches_direct"]
        and sched_payload["stationary_shortcut_differs"]
        and rand_payload["prior_identity_matches_direct"]
        and rand_payload["stationary_shortcut_differs"]
    )
    prior_comp_raw_ok = (
        bool(raw_sched_payload.get("prior_identity_matches_direct"))
        and bool(raw_sched_payload.get("stationary_shortcut_differs"))
        and bool(raw_rand_payload.get("prior_identity_matches_direct"))
        and bool(raw_rand_payload.get("stationary_shortcut_differs"))
    )
    findings.append({"name": "prior_composition_sanity", "status": "pass" if prior_comp_ok and prior_comp_raw_ok else "fail", "details": json.dumps({"computed": prior_comp, "raw": raw_prior_comp}, sort_keys=True)})
    stop = stop_time_visibility_sanity()
    raw_stop = raw.get("stop_time_visibility_sanity", {})
    stop_payload = stop["two_state_refresh_chain_start_dependent_sst"]
    raw_stop_payload = raw_stop.get("two_state_refresh_chain_start_dependent_sst", {})
    stop_ok = (
        stop_payload["delegate_independent_of_start"]
        and stop_payload["observed_T_identifies_start"]
        and np.isclose(stop_payload["delegate_only_expected_chi2"], 0.0)
        and stop_payload["visible_stop_time_expected_chi2"] > 0.999999
    )
    stop_raw_ok = (
        bool(raw_stop_payload.get("delegate_independent_of_start"))
        and bool(raw_stop_payload.get("observed_T_identifies_start"))
        and np.isclose(float(raw_stop_payload.get("delegate_only_expected_chi2", -1.0)), 0.0)
        and float(raw_stop_payload.get("visible_stop_time_expected_chi2", 0.0)) > 0.999999
    )
    findings.append({"name": "stop_time_visibility_sanity", "status": "pass" if stop_ok and stop_raw_ok else "fail", "details": json.dumps({"computed": stop, "raw": raw_stop}, sort_keys=True)})
    paper = paper_anchor_check()
    findings.append({"name": "paper_table_anchor_lines", "status": paper["status"], "details": json.dumps(paper, sort_keys=True)})
    value_check = raw_schema_value_check(raw)
    findings.append({"name": "raw_value_constraints", "status": value_check["status"], "details": json.dumps(value_check, sort_keys=True)})
    failed = [f for f in findings if f["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "checks": findings,
        "summary": {"checks_passed": len(findings) - len(failed), "checks_failed": len(failed)},
        "fail_closed_rule": "If this check fails, use the theorem/proof text but do not trust the shipped raw sanity anchors until repaired.",
    }


def archive_guard() -> dict:
    """Validate repaired spectral prose/witness guardrails across compact archive surfaces."""
    root = Path(__file__).resolve().parents[3]
    targets = {
        "spectral_paper": root / "published/2026-01-23_spectral_anonymity/paper.tex",
        "paperD": root / "series/anonymity_series/paperD_spectral_delegation_certificates/paper.tex",
        "synthesis24": root / "series/synthesis/paper24_math_backbone_crosswalk/paper.tex",
        "synthesis21": root / "series/synthesis/paper21_conditional_budget_certificates/paper.tex",
        "context_pack": root / "CONTEXT_PACK.json",
        "start_here": root / "START_HERE.md",
    }
    texts = {name: path.read_text(encoding="utf-8") for name, path in targets.items() if path.exists()}
    findings: list[dict] = []

    def record(name: str, ok: bool, details: str) -> None:
        findings.append({"name": name, "status": "pass" if ok else "fail", "details": details})

    spectral = texts.get("spectral_paper", "")
    record("spectral_no_literal_tabs", "\t" not in spectral, "literal tab count=" + str(spectral.count("\t")))
    record("spectral_fixed_kernel_identity", "\\|\\cD^t\\|_F^2-1" in spectral and "\\sum_{i=2}^n \\tau_i(t)^2" in spectral, "requires t-step Frobenius and tau-spectrum identity")
    record("spectral_schedule_identity", "\\cM_t=\\cD_1\\cD_2\\cdots\\cD_t" in spectral and "\\prod_{i=1}^t\\sigma_{2,i}^{2}" in spectral, "requires ordered-product schedule identity and conservative product bound")
    record("spectral_artifact_guard_claim", "--archive-guard" in spectral and "--check-raw" in spectral, "artifact availability should name both supplement checks")
    record("spectral_tail_conversion_guard", "tail/pointwise" in spectral and "Markov" in spectral and "Cantelli" in spectral, "expected chi2 must not be reused as a receipt chi2_bound without conversion")
    record("spectral_ergodicity_floor_guard", "Ergodicity convention and leakage floors" in spectral and "one-step claim $\\sigma_2(\\cD)<1$" in spectral, "decay interpretation must distinguish ergodicity from one-step sigma2 simplicity")
    record("spectral_random_length_chi2_guard", "Visible versus hidden randomized-length chi-squared leakage" in spectral and "mixture discriminant" in spectral, "randomized length should distinguish visible and hidden hopcount witnesses")
    record("spectral_truncation_tail_guard", "truncation_tail_mass" in spectral and "remainder_chi2_cap" in spectral and "renormalized prefix" in spectral, "finite truncations should serialize tail mass and a remainder cap rather than silently dropping support")
    record("spectral_empirical_mixture_law_guard", "Empirical mixture-law uncertainty" in spectral and "mixture_law_source" in spectral and "weight_confidence" in spectral and "plug-in" in spectral, "empirically estimated hidden-mixture weights should carry law-source/confidence information rather than plug-in frequencies")
    record("spectral_kernel_model_uncertainty_guard", "Kernel/model uncertainty" in spectral and "kernel_source" in spectral and "model_uncertainty_policy" in spectral and "plug-in kernel" in spectral, "estimated/stale kernels or observation models should carry source/confidence/uncertainty-set evidence rather than plug-in reuse")
    record("spectral_numeric_serialization_guard", "Numeric/serialization precision" in spectral and "numeric_error_policy" in spectral and "rounding_direction" in spectral and "interval upper" in spectral, "deterministic numeric or serialization outputs should use conservative rounding/error-policy evidence before becoming upper-bound receipt fields")
    record("spectral_tensorization_guard", "Pinsker" in spectral and "average posterior" in spectral and "pairwise law bound" in spectral and "absolute continuity" in spectral, "repeated-query amplification should expose KL/Pinsker, support conditions, and avoid average-posterior misuse")
    record("spectral_prior_mismatch_guard", "Arbitrary-prior observation-channel identity" in spectral and "stationary-prior shortcut" in spectral, "non-stationary initiator priors and side information should use the declared observation channel rather than stationary spectral shortcut")
    record("spectral_support_trim_guard", "positive-marginal" in spectral and "zero-marginal" in spectral and "m_+" in spectral, "observation-channel identities should trim zero-marginal columns before using m^{-1/2}")
    record("spectral_observation_channel_guard", "observation-channel $\\chi^2$" in spectral and "visible-hopcount observation channel" in spectral and "hidden-hopcount" in spectral, "observation scope should cover visible hopcount and side information")
    record("spectral_joint_observation_guard", "Joint observations compose as a new channel" in spectral and "joint observation channel" in spectral and "not the maximum of individual certificates" in spectral, "jointly visible side channels should require a product/full observation channel or composition certificate")
    record("spectral_adaptive_transcript_guard", "Adaptive transcripts are one observation channel" in spectral and "history-conditioned" in spectral and "marginal" in spectral and "full transcript channel" in spectral, "adaptive/history-visible transcripts should require full transcript or uniform history-conditioned composition evidence")
    record("spectral_estimator_certificate_guard", "Stochastic estimators are not certificates" in spectral and "one-sided" in spectral and "Hutchinson" in spectral and "estimate-only" in spectral, "randomized trace/SVD point estimates should not be accepted as upper-bound certificates")
    record("spectral_estimator_confidence_guard", "estimator confidence" in spectral and "privacy-tail" in spectral and "union" in spectral and "confidence-qualified" in spectral, "estimator confidence should be separate from privacy-tail failure probability")
    record("spectral_estimator_multiplicity_guard", "Estimator/model-selection multiplicity" in spectral and "candidate_family" in spectral and "alpha_spending" in spectral and "selection_rule" in spectral, "many-candidate stochastic estimator/model selection should record family-wise confidence or alpha spending")
    record("spectral_censoring_conditioning_guard", "Censoring and success-only conditioning" in spectral and ("conditioning_scope" in spectral or "conditioning\\_scope" in spectral) and ("censoring_policy" in spectral or "censoring\\_policy" in spectral) and "\\rho\\mid C" in spectral, "success-only / abort-filtered traces should declare conditioning scope and recompute the conditional channel/prior")
    record("spectral_postprocessing_guard", "Observation coarsening / post-processing monotonicity" in spectral and "coarsened" in spectral and "not conversely" in spectral, "post-processing direction should permit richer-to-coarser reuse but fail closed in reverse")
    record("spectral_tail_postprocessing_guard", "Tail endpoints under coarsening" in spectral and "copied unchanged" in spectral and "high-probability tail/quantile" in spectral, "tail/quantile PML endpoints should not be copied unchanged across coarsening")
    record("spectral_selector_visibility_guard", "Independent selector visibility" in spectral and "selector\\_scope" in spectral and "hidden-selector" in spectral and "visible selector" in spectral, "selector identity / schedule-branch visibility should be scoped and fail closed from hidden to visible")
    record("spectral_pairwise_session_guard", "Pairwise/session support guard" in spectral and "support mismatch" in spectral and "average posterior" in spectral and "linked repetitions" in spectral, "pairwise/session claims should require support-aware pairwise laws and linkage model")
    record("spectral_sst_visibility_guard", "Stop-time visibility guard" in spectral and ("T itself may leak" in spectral or "$T$ itself may leak" in spectral), "SST section should distinguish delegate-only perfection from observed stop-time leakage")
    record("spectral_quantile_tail_guard", "exact weighted quantile" in spectral and "enumerated" in spectral and "delegate-level values" in spectral, "tail conversion should mention exact evaluator quantile when delegate values are enumerated")
    record("spectral_pml_maxl_tail_guard", "failure-mass fallback" in spectral and "PML" in spectral and "channel-level MaxL" in spectral, "high-probability PML envelopes must be separated from channel-level MaxL budgets")
    record("spectral_debruijn_suffix_guard", "delegate's first $m-t$ symbols" in spectral and "initiator's last $m-t$ symbols" in spectral and "$\\sigma_2(\\cD)=1$" in spectral, "de Bruijn suffix and non-lazy sigma2 contrast should be explicit")

    raw_report = check_raw_outputs()
    record("raw_check_embedded", raw_report["status"] == "pass", json.dumps(raw_report["summary"], sort_keys=True))

    paper_d = texts.get("paperD", "")
    record("paperD_chi2_general_guard", "tail/pointwise" in paper_d and "normal/reversible side condition" in paper_d and "prior-aware" in paper_d and "observation_scope" in paper_d and "visible-hopcount" in paper_d, "Paper D must fail closed on one-step-power, raw-expectation, mismatched-prior, or mismatched-observation chi2-general witnesses")
    record("paperD_postprocessing_guard", "post-processing" in paper_d and "coarser" in paper_d and "richer" in paper_d, "Paper D should allow richer-to-coarser observation reuse only with a declared postprocessor")
    record("paperD_tail_postprocessing_guard", "tail/quantile PML" in paper_d and "recomputed" in paper_d and "copied unchanged" in paper_d and ("prior_min" in paper_d or "prior\\_min" in paper_d), "Paper D should separate coarsening endpoint kinds and use prior_min for prior-scoped receipts")
    record("paperD_support_policy_guard", "support_policy" in paper_d and "positive-marginal" in paper_d, "Paper D should serialize positive-marginal support policy")
    record("paperD_selector_guard", "selector_scope" in paper_d and "hidden selector" in paper_d and "visible selector" in paper_d, "Paper D should serialize selector visibility scope")
    record("paperD_pairwise_session_guard", "pairwise/session" in paper_d and "support" in paper_d and "average posterior" in paper_d, "Paper D should not export average posterior chi2 as a pairwise/session support certificate")
    record("paperD_schedule_digest_guard", "time-varying schedule digest" in paper_d and "t-step Frobenius/schedule witness" in paper_d, "Paper D should route schedules to schedule witnesses")
    record("paperD_expected_to_tail_guard", ("tail_source=markov" in paper_d or "tail\\_source=markov" in paper_d) and "raw expected-Frobenius" in paper_d, "Paper D should serialize only converted/evaluator-certified chi2_bound values")
    record("paperD_pml_maxl_tail_guard", "derived_pml_bits" in paper_d and "derived_maxl_bits" in paper_d and "failure-mass fallback" in paper_d and "PML envelope" in paper_d and "channel-level MaxL" in paper_d, "Paper D should distinguish high-probability PML envelopes from channel-level MaxL budgets")
    record("paperD_joint_observation_guard", "joint_observation_scope" in paper_d and "joint observation" in paper_d and "product/full observation channel" in paper_d, "Paper D should fail closed when separate witnesses are promoted to jointly visible observations")
    record("paperD_adaptive_transcript_guard", "transcript_scope" in paper_d and "adaptive_composition" in paper_d and "history-conditioned" in paper_d and "marginal" in paper_d, "Paper D should serialize adaptive transcript scope and forbid marginal per-round witness reuse")
    record("paperD_estimator_certificate_guard", "estimator_certification" in paper_d and "one-sided" in paper_d and "estimate-only" in paper_d, "Paper D should distinguish stochastic estimates from upper-bound certificates")
    record("paperD_estimator_confidence_guard", "estimator_confidence" in paper_d and "estimator_alpha" in paper_d and "privacy_delta" in paper_d and "union" in paper_d, "Paper D should preserve estimator confidence separately from privacy-tail delta")
    record("paperD_estimator_multiplicity_guard", "candidate_family" in paper_d and "selection_rule" in paper_d and "alpha_spending" in paper_d, "Paper D should serialize many-candidate estimator/model-selection confidence accounting")
    record("paperD_censoring_conditioning_guard", ("conditioning_scope" in paper_d or "conditioning\\_scope" in paper_d) and ("censoring_policy" in paper_d or "censoring\\_policy" in paper_d) and "success/abort" in paper_d and "conditioned prior" in paper_d, "Paper D should serialize post-selection/censoring scope and conditioned reference prior")
    record("paperD_truncation_tail_guard", "truncation_tail_mass" in paper_d and "remainder_chi2_cap" in paper_d and "renormalized prefix" in paper_d, "Paper D should serialize finite-support truncation tail accounting")
    record("paperD_empirical_mixture_law_guard", "mixture_law_source" in paper_d and "weight_confidence" in paper_d and "plug-in" in paper_d, "Paper D should serialize empirical mixture-law certification for estimated hidden selector/hopcount weights")
    record("paperD_kernel_model_uncertainty_guard", "kernel_source" in paper_d and "model_confidence" in paper_d and "model_uncertainty_policy" in paper_d and "plug-in kernel" in paper_d, "Paper D should serialize kernel/model uncertainty certification for estimated or stale kernels/channels")

    synthesis24 = texts.get("synthesis24", "")
    record("synthesis24_crosswalk_guard", "t-step Frobenius identity" in synthesis24 and "normal/reversible shortcut" in synthesis24, "Synthesis 24 should preserve theorem-root routing semantics")
    record("synthesis24_tail_route_guard", "tail/pointwise" in synthesis24 and "Markov" in synthesis24 and "prior-aware" in synthesis24 and "observation-channel-aware" in synthesis24 and "visible-hopcount" in synthesis24, "Synthesis 24 should preserve expected-to-receipt tail conversion plus prior/observation-scope semantics")
    record("synthesis24_postprocessing_guard", "post-processing" in synthesis24 and "coarser" in synthesis24 and "richer" in synthesis24, "Synthesis 24 should preserve observation coarsening direction")
    record("synthesis24_tail_postprocessing_guard", "tail/quantile PML" in synthesis24 and "recomputed" in synthesis24 and "copied unchanged" in synthesis24, "Synthesis 24 should preserve tail/quantile endpoint-kind semantics under coarsening")
    record("synthesis24_support_trim_guard", "positive-marginal" in synthesis24 and "zero-marginal" in synthesis24, "Synthesis 24 should preserve positive-support observation-channel semantics")
    record("synthesis24_selector_guard", "selector" in synthesis24 and "hidden" in synthesis24 and "visible" in synthesis24, "Synthesis 24 should preserve selector visibility scope")
    record("synthesis24_adaptive_selector_guard", "adaptive" in synthesis24 and "initiator-correlated" in synthesis24 and "full observation channel" in synthesis24, "Synthesis 24 should preserve adaptive selector fail-closed semantics")
    record("synthesis24_prior_min_guard", "prior_min" in synthesis24 and "reference-prior" in synthesis24, "Synthesis 24 should preserve declared reference-prior minimum semantics")
    record("synthesis24_pairwise_session_guard", "pairwise/session" in synthesis24 and "average posterior" in synthesis24 and "support" in synthesis24, "Synthesis 24 should preserve pairwise/session support semantics")
    record("synthesis24_pml_maxl_tail_guard", "PML" in synthesis24 and "failure-mass" in synthesis24 and "channel-level MaxL" in synthesis24 and "PML / realized odds-inflation" in synthesis24, "Synthesis 24 should preserve the PML-vs-MaxL tail boundary")
    record("synthesis24_joint_observation_guard", "joint observation" in synthesis24 and "product/full observation channel" in synthesis24 and "individual" in synthesis24, "Synthesis 24 should preserve joint-observation composition semantics")
    record("synthesis24_adaptive_transcript_guard", "adaptive transcript" in synthesis24 and "history-conditioned" in synthesis24 and "marginal" in synthesis24 and "full transcript channel" in synthesis24, "Synthesis 24 should preserve adaptive transcript composition semantics")
    record("synthesis24_estimator_certificate_guard", "stochastic" in synthesis24 and "one-sided" in synthesis24 and "estimate-only" in synthesis24, "Synthesis 24 should preserve estimator-certification semantics")
    record("synthesis24_estimator_confidence_guard", "estimator confidence" in synthesis24 and "privacy_delta" in synthesis24 and "union" in synthesis24, "Synthesis 24 should preserve estimator-confidence vs privacy-tail semantics")
    record("synthesis24_estimator_multiplicity_guard", "candidate_family" in synthesis24 and "selection_rule" in synthesis24 and "alpha_spending" in synthesis24, "Synthesis 24 should preserve many-candidate estimator/model-selection confidence accounting")
    record("synthesis24_censoring_conditioning_guard", ("conditioning_scope" in synthesis24 or "conditioning\\_scope" in synthesis24) and ("censoring_policy" in synthesis24 or "censoring\\_policy" in synthesis24) and ("success-only" in synthesis24.lower()) and "conditioned prior" in synthesis24, "Synthesis 24 should preserve post-selection/censoring scope semantics")
    record("synthesis24_truncation_tail_guard", "truncation_tail_mass" in synthesis24 and "remainder_chi2_cap" in synthesis24 and "renormalized prefix" in synthesis24, "Synthesis 24 should preserve finite-support truncation tail accounting")
    record("synthesis24_kernel_model_uncertainty_guard", "kernel_source" in synthesis24 and "model_uncertainty_policy" in synthesis24 and "plug-in kernel" in synthesis24, "Synthesis 24 should preserve kernel/model uncertainty semantics")
    record("synthesis24_numeric_serialization_guard", "numeric_error_policy" in synthesis24 and "rounding_direction" in synthesis24 and "certified upper" in synthesis24, "Synthesis 24 should preserve numeric/serialization precision semantics")

    synthesis21 = texts.get("synthesis21", "")
    record("synthesis21_reopen_route_guard", "one-step singular-power shortcut" in synthesis21 and "Anonymity~D" in synthesis21, "Synthesis 21 should route stale spectral evidence to Anonymity D")

    context = texts.get("context_pack", "") + "\n" + texts.get("start_here", "")
    record("operator_surfaces_name_spectral_checks", "spectral_reconstruction.py --check-raw" in context and "chi2-general" in context, "wake-up surfaces should include raw check and chi2-general warning")
    record("operator_surfaces_tail_warning", "tail/pointwise" in context and "expected" in context and "prior-aware" in context, "wake-up surfaces should warn against raw expected chi2 and mismatched priors as receipt bounds")
    record("operator_surfaces_observation_warning", "observation-channel" in context and "visible-hopcount" in context and "prior-aware" in context, "wake-up surfaces should preserve observation and prior scope for visible/hiddden-hopcount witnesses")
    record("operator_surfaces_postprocessing_warning", "post-processing" in context and "coarser" in context and "richer" in context, "wake-up surfaces should preserve coarsening direction for observation-scope reuse")
    record("operator_surfaces_tail_postprocessing_warning", "tail/quantile" in context and "recompute" in context and "coarsened" in context, "wake-up surfaces should warn that tail/quantile PML endpoints are not copied unchanged across coarsening")
    record("operator_surfaces_support_trim_warning", "positive-marginal" in context and "zero-marginal" in context, "wake-up surfaces should warn that observation-channel certificates trim zero-marginal observations")
    record("operator_surfaces_selector_warning", "selector" in context and "hidden" in context and "visible" in context, "wake-up surfaces should preserve selector visibility scope")
    record("operator_surfaces_adaptive_selector_warning", "initiator-correlated" in context and "selector_independence" in context, "wake-up surfaces should warn about adaptive/initiator-correlated selectors")
    record("operator_surfaces_prior_min_warning", "prior_min" in context and "reference prior" in context, "wake-up surfaces should warn about reference-prior minimum for PML/MaxL conversion")
    record("operator_surfaces_pairwise_session_warning", "pairwise/session" in context and "average posterior" in context and "support" in context, "wake-up surfaces should warn that average posterior chi2 is not pairwise/session support evidence")
    record("operator_surfaces_pml_maxl_warning", "failure-mass" in context and "PML" in context and "MaxL" in context, "wake-up surfaces should distinguish high-probability PML envelopes from MaxL budgets")
    record("operator_surfaces_joint_observation_warning", "joint observation" in context and "product/full observation channel" in context, "wake-up surfaces should warn against promoting individual witnesses to jointly visible observations")
    record("operator_surfaces_adaptive_transcript_warning", "adaptive transcript" in context and "history-conditioned" in context and "marginal" in context, "wake-up surfaces should warn against marginal witness reuse for adaptive/history-visible transcripts")
    record("operator_surfaces_estimator_certificate_warning", "one-sided" in context and "estimate-only" in context and "stochastic" in context, "wake-up surfaces should warn that stochastic estimates are not upper-bound certificates")
    record("operator_surfaces_estimator_confidence_warning", "estimator_alpha" in context and "privacy_delta" in context and "confidence-qualified" in context, "wake-up surfaces should separate estimator confidence from privacy-tail failure probability")
    record("operator_surfaces_estimator_multiplicity_warning", "candidate_family" in context and "selection_rule" in context and "alpha_spending" in context, "wake-up surfaces should warn that many-candidate stochastic estimator selection needs family-wise confidence accounting")
    record("operator_surfaces_censoring_conditioning_warning", ("conditioning_scope" in context or "conditioning\\_scope" in context) and ("censoring_policy" in context or "censoring\\_policy" in context) and "success-only" in context.lower(), "wake-up surfaces should warn that post-selected/success-only traces need conditional-channel witnesses")
    record("operator_surfaces_truncation_tail_warning", "truncation_tail_mass" in context and "remainder_chi2_cap" in context and "renormalized prefix" in context, "wake-up surfaces should warn that truncated hidden-support witnesses need remainder accounting")
    record("operator_surfaces_empirical_mixture_law_warning", "mixture_law_source" in context and "weight_confidence" in context and "plug-in" in context, "wake-up surfaces should warn that empirical hidden-mixture weights need law-certification rather than plug-in frequencies")
    record("operator_surfaces_kernel_model_uncertainty_warning", "kernel_source" in context and "model_uncertainty_policy" in context and "plug-in kernel" in context, "wake-up surfaces should warn that estimated/stale kernels need model uncertainty certification")
    record("operator_surfaces_numeric_serialization_warning", "numeric_error_policy" in context and "rounding_direction" in context and "safety_margin" in context, "wake-up surfaces should warn that serialized upper-bound numbers require conservative numeric/rounding policy")

    failed = [f for f in findings if f["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "checks": findings,
        "summary": {"checks_passed": len(findings) - len(failed), "checks_failed": len(failed)},
        "fail_closed_rule": "If this guard fails, do not trust exact chi2-general or schedule witness prose until the named surface is repaired.",
    }


def emit_plot(path: Path) -> None:
    """Render the TV-cliff figure from raw coordinates when matplotlib is available."""
    import matplotlib.pyplot as plt

    raw = load_raw_outputs()["tv_cliff_coordinates"]
    for key, coords in raw.items():
        arr = np.asarray(coords, dtype=float)
        plt.plot(arr[:, 0], arr[:, 1], label=key)
    plt.yscale("log")
    plt.xlabel("walk length t")
    plt.ylabel("total variation")
    plt.legend()
    plt.grid(True)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, bbox_inches="tight")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity-sanity", action="store_true", help="print small exact-vs-shortcut sanity checks")
    ap.add_argument("--schedule-sanity", action="store_true", help="print shared-stationary schedule sanity checks")
    ap.add_argument("--tail-sanity", action="store_true", help="print expected-chi2 to tail-bound translation sanity check")
    ap.add_argument("--random-length-sanity", action="store_true", help="print hidden randomized-length chi2 mixture sanity check")
    ap.add_argument("--truncation-sanity", action="store_true", help="print finite-support truncation-tail accounting sanity check")
    ap.add_argument("--empirical-law-sanity", action="store_true", help="print empirical hidden-mixture law uncertainty sanity check")
    ap.add_argument("--kernel-model-sanity", action="store_true", help="print kernel/model uncertainty sanity check")
    ap.add_argument("--numeric-serialization-sanity", action="store_true", help="print numeric/serialization precision sanity check")
    ap.add_argument("--observation-channel-sanity", action="store_true", help="print visible-hopcount and observation-channel sanity checks")
    ap.add_argument("--postprocess-sanity", action="store_true", help="print observation-channel post-processing/coarsening sanity checks")
    ap.add_argument("--tail-postprocess-sanity", action="store_true", help="print tail/quantile behavior under observation coarsening")
    ap.add_argument("--support-sanity", action="store_true", help="print positive-marginal observation support trimming sanity check")
    ap.add_argument("--selector-sanity", action="store_true", help="print hidden-vs-visible independent selector sanity check")
    ap.add_argument("--adaptive-selector-sanity", action="store_true", help="print adaptive/initiator-correlated selector sanity check")
    ap.add_argument("--joint-observation-sanity", action="store_true", help="print joint-observation composition sanity check")
    ap.add_argument("--adaptive-transcript-sanity", action="store_true", help="print adaptive/history-visible transcript composition sanity check")
    ap.add_argument("--estimator-certification-sanity", action="store_true", help="print stochastic-estimator certification sanity check")
    ap.add_argument("--estimator-confidence-sanity", action="store_true", help="print estimator-confidence versus privacy-tail accounting sanity check")
    ap.add_argument("--estimator-multiplicity-sanity", action="store_true", help="print many-candidate estimator/model-selection confidence accounting sanity check")
    ap.add_argument("--censoring-sanity", action="store_true", help="print success-only/post-selection conditioning sanity check")
    ap.add_argument("--ratio-separation-sanity", action="store_true", help="print separation-vs-upper-relative-density sanity checks")
    ap.add_argument("--pairwise-session-sanity", action="store_true", help="print pairwise/session support mismatch sanity check")
    ap.add_argument("--ergodicity-floor-sanity", action="store_true", help="print reducible/periodic floor and non-normal sigma2 sanity checks")
    ap.add_argument("--prior-sanity", action="store_true", help="print arbitrary-prior mismatch sanity check")
    ap.add_argument("--prior-baseline-min-sanity", action="store_true", help="print declared reference-prior minimum sanity check")
    ap.add_argument("--prior-composition-sanity", action="store_true", help="print prior-aware schedule and hidden-length mixture sanity checks")
    ap.add_argument("--stop-time-sanity", action="store_true", help="print stop-time visibility sanity check")
    ap.add_argument("--raw", action="store_true", help="print the shipped raw table anchors")
    ap.add_argument("--check-raw", action="store_true", help="validate the shipped raw sanity-anchor JSON")
    ap.add_argument("--archive-guard", action="store_true", help="validate repaired spectral guardrails across compact archive surfaces")
    ap.add_argument("--plot", type=Path, default=None, help="optional path for a regenerated TV-cliff plot")
    args = ap.parse_args()

    status = 0
    if args.identity_sanity:
        print(json.dumps(identity_sanity(), indent=2))
    if args.schedule_sanity:
        print(json.dumps(schedule_sanity(), indent=2))
    if args.tail_sanity:
        print(json.dumps(tail_translation_sanity(), indent=2))
    if args.random_length_sanity:
        print(json.dumps(random_length_sanity(), indent=2))
    if args.truncation_sanity:
        print(json.dumps(truncation_tail_sanity(), indent=2))
    if args.empirical_law_sanity:
        print(json.dumps(empirical_mixture_law_sanity(), indent=2))
    if args.kernel_model_sanity:
        print(json.dumps(kernel_model_uncertainty_sanity(), indent=2))
    if args.numeric_serialization_sanity:
        print(json.dumps(numeric_serialization_sanity(), indent=2))
    if args.observation_channel_sanity:
        print(json.dumps(observation_channel_sanity(), indent=2))
    if args.postprocess_sanity:
        print(json.dumps(postprocessing_sanity(), indent=2))
    if args.tail_postprocess_sanity:
        print(json.dumps(tail_postprocess_sanity(), indent=2))
    if args.support_sanity:
        print(json.dumps(support_trimming_sanity(), indent=2))
    if args.selector_sanity:
        print(json.dumps(selector_visibility_sanity(), indent=2))
    if args.adaptive_selector_sanity:
        print(json.dumps(adaptive_selector_sanity(), indent=2))
    if args.joint_observation_sanity:
        print(json.dumps(joint_observation_sanity(), indent=2))
    if args.adaptive_transcript_sanity:
        print(json.dumps(adaptive_transcript_sanity(), indent=2))
    if args.estimator_certification_sanity:
        print(json.dumps(estimator_certification_sanity(), indent=2))
    if args.estimator_confidence_sanity:
        print(json.dumps(estimator_confidence_accounting_sanity(), indent=2))
    if args.estimator_multiplicity_sanity:
        print(json.dumps(estimator_multiplicity_sanity(), indent=2))
    if args.censoring_sanity:
        print(json.dumps(censoring_conditioning_sanity(), indent=2))
    if args.ratio_separation_sanity:
        print(json.dumps(separation_ratio_sanity(), indent=2))
    if args.pairwise_session_sanity:
        print(json.dumps(pairwise_session_support_sanity(), indent=2))
    if args.ergodicity_floor_sanity:
        print(json.dumps(ergodicity_floor_sanity(), indent=2))
    if args.prior_sanity:
        print(json.dumps(prior_mismatch_sanity(), indent=2))
    if args.prior_baseline_min_sanity:
        print(json.dumps(prior_baseline_min_sanity(), indent=2))
    if args.prior_composition_sanity:
        print(json.dumps(prior_composition_sanity(), indent=2))
    if args.stop_time_sanity:
        print(json.dumps(stop_time_visibility_sanity(), indent=2))
    if args.raw:
        print(json.dumps(load_raw_outputs(), indent=2))
    if args.check_raw:
        report = check_raw_outputs()
        print(json.dumps(report, indent=2))
        status = 0 if report["status"] == "pass" else 1
    if args.archive_guard:
        report = archive_guard()
        print(json.dumps(report, indent=2))
        status = 0 if status == 0 and report["status"] == "pass" else 1
    if args.plot is not None:
        emit_plot(args.plot)
        print(json.dumps({"wrote_plot": str(args.plot)}, indent=2))
    if not (args.identity_sanity or args.schedule_sanity or args.tail_sanity or args.random_length_sanity or args.truncation_sanity or args.empirical_law_sanity or args.kernel_model_sanity or args.numeric_serialization_sanity or args.observation_channel_sanity or args.postprocess_sanity or args.tail_postprocess_sanity or args.support_sanity or args.selector_sanity or args.adaptive_selector_sanity or args.joint_observation_sanity or args.adaptive_transcript_sanity or args.estimator_certification_sanity or args.estimator_confidence_sanity or args.estimator_multiplicity_sanity or args.censoring_sanity or args.ratio_separation_sanity or args.pairwise_session_sanity or args.ergodicity_floor_sanity or args.prior_sanity or args.prior_baseline_min_sanity or args.prior_composition_sanity or args.stop_time_sanity or args.raw or args.check_raw or args.archive_guard or args.plot):
        print(json.dumps({"usage": "pass --identity-sanity, --schedule-sanity, --tail-sanity, --random-length-sanity, --truncation-sanity, --empirical-law-sanity, --kernel-model-sanity, --numeric-serialization-sanity, --observation-channel-sanity, --postprocess-sanity, --tail-postprocess-sanity, --support-sanity, --selector-sanity, --adaptive-selector-sanity, --joint-observation-sanity, --adaptive-transcript-sanity, --estimator-certification-sanity, --estimator-confidence-sanity, --estimator-multiplicity-sanity, --censoring-sanity, --ratio-separation-sanity, --pairwise-session-sanity, --ergodicity-floor-sanity, --prior-sanity, --prior-baseline-min-sanity, --prior-composition-sanity, --stop-time-sanity, --check-raw, --archive-guard, --raw, or --plot PATH"}, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
