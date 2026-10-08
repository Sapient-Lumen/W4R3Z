#!/usr/bin/env python3
"""Shared sparse-attention evaluation utilities for CloudtainerML.

This module intentionally separates *selection* from *evaluation*.
Selection helpers may inspect QK scores and derived score-only quantities
(max score, exp score mass, histograms, block-local order), but they must not
inspect V vectors or dense attention outputs.  Evaluation helpers may compute
softmax(QK) @ V after the selector has returned its index set.

The core is still Python/numpy diagnostic code; it is not a kernel and does not
make speed claims.  Its purpose is to keep output metrics and cost accounting
identical across synthetic-row and model-trace probes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

QUALITY_MASS = 0.95
QUALITY_COSINE = 0.995
QUALITY_REL_L2 = 0.18
DEFAULT_DELTAS = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0, 12.0, math.inf)


def stable_softmax(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    y = x - float(np.max(x))
    e = np.exp(np.clip(y, -80.0, 80.0))
    z = float(np.sum(e))
    if not np.isfinite(z) or z <= 0:
        return np.full_like(x, 1.0 / len(x), dtype=np.float64)
    return e / z


def topk_indices(scores: np.ndarray, k: int) -> np.ndarray:
    scores = np.asarray(scores)
    k = min(int(k), len(scores))
    if k <= 0:
        return np.array([], dtype=np.int64)
    if k >= len(scores):
        return np.argsort(-scores).astype(np.int64)
    part = np.argpartition(-scores, k - 1)[:k]
    return part[np.argsort(-scores[part])].astype(np.int64)


def topp_indices_from_probs(scores: np.ndarray, probs: np.ndarray, p: float) -> np.ndarray:
    order = np.argsort(-np.asarray(scores))
    mass = 0.0
    keep: list[int] = []
    for i in order:
        keep.append(int(i))
        mass += float(probs[i])
        if mass >= p:
            break
    return np.array(keep, dtype=np.int64)


def min_k_for_mass(probs: np.ndarray, target: float) -> int:
    order = np.argsort(-np.asarray(probs))
    mass = 0.0
    for rank, i in enumerate(order, start=1):
        mass += float(probs[i])
        if mass >= target:
            return rank
    return len(probs)


def effective_support(probs: np.ndarray) -> float:
    probs = np.asarray(probs, dtype=np.float64)
    ent = -float(np.sum(probs * np.log(np.maximum(probs, 1e-30))))
    return float(math.exp(ent))


def sparse_attention_output(scores: np.ndarray, values: np.ndarray, selected: Iterable[int]) -> tuple[np.ndarray, float, int]:
    sel = np.unique(np.fromiter((int(i) for i in selected), dtype=np.int64))
    if len(sel) == 0:
        return np.zeros(values.shape[-1], dtype=np.float64), 0.0, 0
    probs = stable_softmax(scores)
    sparse_probs = stable_softmax(scores[sel])
    out = sparse_probs @ values[sel]
    mass = float(np.sum(probs[sel]))
    return out, mass, int(len(sel))


def output_metrics(scores: np.ndarray, values: np.ndarray, selected: Iterable[int]) -> dict[str, float | int | bool]:
    dense_probs = stable_softmax(scores)
    dense_out = dense_probs @ values
    sparse_out, mass, count = sparse_attention_output(scores, values, selected)
    dense_norm = float(np.linalg.norm(dense_out))
    err = float(np.linalg.norm(sparse_out - dense_out))
    rel = err / max(1e-9, dense_norm)
    denom = max(1e-12, float(np.linalg.norm(sparse_out)) * dense_norm)
    cosine = float(np.dot(sparse_out, dense_out) / denom) if denom > 0 else 0.0
    cosine = max(-1.0, min(1.0, cosine))
    return {
        "selected_count": int(count),
        "mass_retained": float(mass),
        "attention_l2_error": err,
        "attention_rel_l2_error": rel,
        "output_cosine": cosine,
        "dense_attention_output_norm": dense_norm,
        "effective_support": effective_support(dense_probs),
    }


def passes_attention_quality_bar(metrics: dict[str, float | int | bool], target_mass: float = QUALITY_MASS) -> bool:
    return bool(
        float(metrics["output_cosine"]) >= QUALITY_COSINE
        and float(metrics["mass_retained"]) >= target_mass
        and float(metrics["attention_rel_l2_error"]) <= QUALITY_REL_L2
    )


def bytes_touched_est(qk_dot_products: int, score_reads: int, value_reads: int, d_head: int, d_value: int) -> int:
    return int(4 * (qk_dot_products * d_head + score_reads + value_reads * d_value))


@dataclass(frozen=True)
class SelectionResult:
    selected: np.ndarray
    selector: str
    target_mass: float | None
    mass_certificate: str
    certified_mass_from_scores: float | None
    selector_passes: int
    score_reads: int
    threshold_evals: int
    sort_free: bool
    selection_uses_values: bool = False
    selection_uses_dense_output: bool = False
    selection_uses_value_norms: bool = False
    value_norm_reads: int = 0
    value_error_bound_from_scores_and_norms: float | None = None
    fallback: str | None = None
    details: dict[str, float | int | str | bool | None] | None = None


def _score_only_mass(scores: np.ndarray, selected: Sequence[int] | np.ndarray) -> float:
    probs = stable_softmax(scores)
    sel = np.unique(np.asarray(selected, dtype=np.int64))
    if len(sel) == 0:
        return 0.0
    return float(np.sum(probs[sel]))


def _value_norm_error_bound(scores: np.ndarray, value_norms: np.ndarray, selected: Sequence[int] | np.ndarray) -> dict[str, float]:
    """Conservative score+metadata bound on output error from omitted values.

    This uses probabilities derived from scores and per-token value norms only.
    It does not inspect value directions or dense outputs.  For selected set S,
    sparse output equals E[V | S] and dense output equals mass(S) E[V|S]
    plus the tail expectation.  Therefore

        ||sparse - dense|| <= (1-mass) * E[||V|| | S] + sum_{i notin S} p_i ||V_i||.

    The bound is deliberately conservative, but it catches the exact failure mode
    that rev0045 left open: high-norm low-probability values can matter even
    when 0.95 attention mass is retained.
    """
    probs = stable_softmax(scores)
    norms = np.asarray(value_norms, dtype=np.float64)
    sel = np.unique(np.asarray(selected, dtype=np.int64))
    mask = np.zeros(len(probs), dtype=bool)
    mask[sel] = True
    mass = float(np.sum(probs[mask]))
    omitted_mass = max(0.0, 1.0 - mass)
    if mass > 0.0:
        selected_expected_norm = float(np.sum(probs[mask] * norms[mask]) / mass)
    else:
        selected_expected_norm = 0.0
    omitted_weighted_norm = float(np.sum(probs[~mask] * norms[~mask]))
    bound = omitted_mass * selected_expected_norm + omitted_weighted_norm
    return {
        "value_error_bound_from_scores_and_norms": float(bound),
        "omitted_mass": float(omitted_mass),
        "selected_expected_value_norm_from_metadata": float(selected_expected_norm),
        "omitted_weighted_value_norm_from_metadata": float(omitted_weighted_norm),
    }


def full_dense_selection(scores: np.ndarray) -> SelectionResult:
    n = len(scores)
    sel = np.arange(n, dtype=np.int64)
    return SelectionResult(
        selected=sel,
        selector="full_dense",
        target_mass=1.0,
        mass_certificate="trivial_full_context",
        certified_mass_from_scores=1.0,
        selector_passes=0,
        score_reads=0,
        threshold_evals=0,
        sort_free=True,
        details={"n": int(n)},
    )


def exact_topk_selection(scores: np.ndarray, k: int) -> SelectionResult:
    n = len(scores)
    sel = topk_indices(scores, k)
    return SelectionResult(
        selected=sel,
        selector=f"exact_topk_{min(int(k), n)}",
        target_mass=None,
        mass_certificate="not_mass_certified",
        certified_mass_from_scores=_score_only_mass(scores, sel),
        selector_passes=1,
        score_reads=n,
        threshold_evals=0,
        sort_free=False,
        details={"k": int(min(k, n))},
    )


def ordered_topp_selection(scores: np.ndarray, target_mass: float) -> SelectionResult:
    n = len(scores)
    probs = stable_softmax(scores)
    sel = topp_indices_from_probs(scores, probs, target_mass)
    return SelectionResult(
        selected=sel,
        selector=f"ordered_topp_{str(target_mass).replace('.', 'p')}",
        target_mass=float(target_mass),
        mass_certificate="exact_from_scores_sorted_order_bound",
        certified_mass_from_scores=_score_only_mass(scores, sel),
        selector_passes=1,
        score_reads=n,
        threshold_evals=0,
        sort_free=False,
        details={"target_mass": float(target_mass), "order_statistic": int(len(sel))},
    )


def delta_grid_mass_selection(scores: np.ndarray, target_mass: float = 0.95, deltas: Sequence[float] = DEFAULT_DELTAS) -> SelectionResult:
    """Score-only threshold compiler: select scores within delta of row max.

    The selector can compute the exact mass certificate from scores alone.  It
    does not sort and does not inspect values or dense outputs.  It may overread
    values if the delta grid is coarse; that is the point of the probe.
    """
    scores = np.asarray(scores, dtype=np.float64)
    n = len(scores)
    max_score = float(np.max(scores))
    probs = stable_softmax(scores)
    chosen_delta = math.inf
    chosen_sel = np.arange(n, dtype=np.int64)
    chosen_mass = 1.0
    inspected = 0
    for delta in deltas:
        inspected += 1
        if math.isinf(float(delta)):
            sel = np.arange(n, dtype=np.int64)
        else:
            sel = np.flatnonzero(scores >= max_score - float(delta)).astype(np.int64)
        mass = float(np.sum(probs[sel])) if len(sel) else 0.0
        if mass >= target_mass:
            chosen_delta = float(delta)
            chosen_sel = sel
            chosen_mass = mass
            break
    return SelectionResult(
        selected=chosen_sel,
        selector=f"mass_delta_grid_{str(target_mass).replace('.', 'p')}",
        target_mass=float(target_mass),
        mass_certificate="exact_from_scores_threshold_grid",
        certified_mass_from_scores=float(chosen_mass),
        selector_passes=1,
        score_reads=n,
        threshold_evals=n * inspected,
        sort_free=True,
        fallback="full_context_delta_inf" if math.isinf(chosen_delta) else None,
        details={"chosen_delta": chosen_delta, "deltas_inspected": inspected, "target_mass": float(target_mass)},
    )


def histogram_mass_selection(scores: np.ndarray, target_mass: float = 0.95, bins: int = 32, max_delta: float = 16.0) -> SelectionResult:
    """Sort-free score histogram compiler with an exact post-selection mass certificate.

    Scores are bucketed by distance from the row maximum.  The chosen bucket is
    the first cumulative bucket whose score-only softmax mass reaches target.
    The selector then keeps every token in buckets up to that cutoff.  This is
    deployable as scan + histogram + gather; it avoids full sort/top-p ordering
    but may overselect within the final bucket.
    """
    scores = np.asarray(scores, dtype=np.float64)
    n = len(scores)
    bins = int(max(1, bins))
    max_score = float(np.max(scores))
    rel = np.maximum(0.0, max_score - scores)
    weights = np.exp(np.clip(scores - max_score, -80.0, 0.0))
    z = float(np.sum(weights))
    if not np.isfinite(z) or z <= 0:
        return full_dense_selection(scores)
    width = float(max_delta) / bins
    # bin ids: 0..bins-1 represent [i*width,(i+1)*width); bins is overflow.
    raw_ids = np.floor(rel / max(width, 1e-12)).astype(np.int64)
    bin_ids = np.clip(raw_ids, 0, bins)
    mass_by_bin = np.bincount(bin_ids, weights=weights, minlength=bins + 1) / z
    cum = 0.0
    cutoff_bin = bins
    for bid, mass in enumerate(mass_by_bin):
        cum += float(mass)
        if cum >= target_mass:
            cutoff_bin = bid
            break
    sel = np.flatnonzero(bin_ids <= cutoff_bin).astype(np.int64)
    exact_mass = float(np.sum(stable_softmax(scores)[sel])) if len(sel) else 0.0
    cutoff_delta_hi = math.inf if cutoff_bin >= bins else (cutoff_bin + 1) * width
    return SelectionResult(
        selected=sel,
        selector=f"mass_histogram_{str(target_mass).replace('.', 'p')}_bins{bins}",
        target_mass=float(target_mass),
        mass_certificate="exact_from_scores_histogram_threshold",
        certified_mass_from_scores=exact_mass,
        selector_passes=2,
        score_reads=2 * n,
        threshold_evals=n,
        sort_free=True,
        fallback="overflow_bucket" if cutoff_bin >= bins else None,
        details={
            "bins": bins,
            "max_delta": float(max_delta),
            "cutoff_bin": int(cutoff_bin),
            "cutoff_delta_hi": cutoff_delta_hi,
            "target_mass": float(target_mass),
        },
    )


def block_local_topb_mass_selection(scores: np.ndarray, target_mass: float = 0.95, block: int = 32, b_grid: Sequence[int] = (1, 2, 4, 8, 16, 32, 64, 128)) -> SelectionResult:
    """Block-local widening compiler.

    It keeps the top-b scores from each block and widens b until the exact
    score-only mass certificate reaches the target.  This resembles a simple
    block-sparse gather policy: it is sort-free globally but performs small
    per-block orderings.
    """
    scores = np.asarray(scores, dtype=np.float64)
    n = len(scores)
    block = int(max(1, min(block, n)))
    probs = stable_softmax(scores)
    chosen_b = n
    chosen_sel = np.arange(n, dtype=np.int64)
    chosen_mass = 1.0
    inspected = 0
    for b in b_grid:
        inspected += 1
        parts: list[np.ndarray] = []
        for start in range(0, n, block):
            stop = min(n, start + block)
            kk = min(int(b), stop - start)
            if kk <= 0:
                continue
            local = topk_indices(scores[start:stop], kk) + start
            parts.append(local.astype(np.int64))
        sel = np.unique(np.concatenate(parts)) if parts else np.array([], dtype=np.int64)
        mass = float(np.sum(probs[sel])) if len(sel) else 0.0
        if mass >= target_mass or len(sel) >= n:
            chosen_b = min(int(b), block)
            chosen_sel = sel
            chosen_mass = mass
            break
    return SelectionResult(
        selected=chosen_sel,
        selector=f"block_topb_certified_{str(target_mass).replace('.', 'p')}",
        target_mass=float(target_mass),
        mass_certificate="exact_from_scores_block_local_widening",
        certified_mass_from_scores=float(chosen_mass),
        selector_passes=inspected,
        score_reads=n * inspected,
        threshold_evals=0,
        sort_free=False,
        fallback="full_block_width" if len(chosen_sel) >= n else None,
        details={"block": int(block), "chosen_b_per_block": int(chosen_b), "b_values_inspected": inspected, "target_mass": float(target_mass)},
    )


def value_norm_guarded_histogram_selection(
    scores: np.ndarray,
    value_norms: np.ndarray,
    target_mass: float = 0.95,
    bins: int = 32,
    max_delta: float = 16.0,
    absolute_error_bound: float = 0.15,
) -> SelectionResult:
    """Histogram mass selector widened until a value-norm error bound passes.

    This is not score-only: it reads value-norm metadata.  It still does not read
    value vectors or dense attention outputs.  It is useful as a safety guard for
    rows where a low-probability token has a high-norm value and mass alone is
    an unsafe proxy for output quality.
    """
    scores = np.asarray(scores, dtype=np.float64)
    norms = np.asarray(value_norms, dtype=np.float64)
    n = len(scores)
    bins = int(max(1, bins))
    max_score = float(np.max(scores))
    rel = np.maximum(0.0, max_score - scores)
    weights = np.exp(np.clip(scores - max_score, -80.0, 0.0))
    z = float(np.sum(weights))
    if not np.isfinite(z) or z <= 0:
        return full_dense_selection(scores)
    width = float(max_delta) / bins
    bin_ids = np.clip(np.floor(rel / max(width, 1e-12)).astype(np.int64), 0, bins)
    mass_by_bin = np.bincount(bin_ids, weights=weights, minlength=bins + 1) / z
    chosen_sel = np.arange(n, dtype=np.int64)
    chosen_bin = bins
    chosen_mass = 1.0
    chosen_bound = _value_norm_error_bound(scores, norms, chosen_sel)
    for cutoff_bin in range(bins + 1):
        sel = np.flatnonzero(bin_ids <= cutoff_bin).astype(np.int64)
        mass = float(np.sum(mass_by_bin[: cutoff_bin + 1]))
        bound = _value_norm_error_bound(scores, norms, sel)
        if mass >= target_mass and bound["value_error_bound_from_scores_and_norms"] <= absolute_error_bound:
            chosen_sel = sel
            chosen_bin = cutoff_bin
            chosen_mass = mass
            chosen_bound = bound
            break
    cutoff_delta_hi = math.inf if chosen_bin >= bins else (chosen_bin + 1) * width
    return SelectionResult(
        selected=chosen_sel,
        selector=f"value_norm_guarded_histogram_{str(target_mass).replace('.', 'p')}_bins{bins}",
        target_mass=float(target_mass),
        mass_certificate="exact_from_scores_plus_value_norm_metadata_histogram_threshold",
        certified_mass_from_scores=float(_score_only_mass(scores, chosen_sel)),
        selector_passes=2,
        score_reads=2 * n,
        threshold_evals=n,
        sort_free=True,
        selection_uses_value_norms=True,
        value_norm_reads=n,
        value_error_bound_from_scores_and_norms=chosen_bound["value_error_bound_from_scores_and_norms"],
        fallback="full_context_value_norm_bound" if len(chosen_sel) >= n else None,
        details={
            "bins": bins,
            "max_delta": float(max_delta),
            "cutoff_bin": int(chosen_bin),
            "cutoff_delta_hi": cutoff_delta_hi,
            "target_mass": float(target_mass),
            "absolute_error_bound": float(absolute_error_bound),
            **chosen_bound,
        },
    )


def value_norm_exception_mass_selection(
    scores: np.ndarray,
    value_norms: np.ndarray,
    target_mass: float = 0.95,
    bins: int = 32,
    max_delta: float = 16.0,
    absolute_error_bound: float = 0.15,
    exception_cap: int | None = None,
) -> SelectionResult:
    """Mass histogram plus discontiguous high-risk value-norm exceptions.

    Start with the score-only histogram mass selector, then inspect value-norm
    metadata for omitted tokens and include the largest p_i ||V_i|| risks until
    the conservative bound passes.  This models a deployable metadata sidecar:
    no value vectors or dense outputs are read while selecting, but selection is
    allowed to use cheap precomputed value norms.
    """
    scores = np.asarray(scores, dtype=np.float64)
    norms = np.asarray(value_norms, dtype=np.float64)
    n = len(scores)
    base = histogram_mass_selection(scores, target_mass=target_mass, bins=bins, max_delta=max_delta)
    selected = set(map(int, base.selected))
    probs = stable_softmax(scores)
    cap = n if exception_cap is None else max(0, min(int(exception_cap), n))

    # rev0050 refactor: keep the value-norm certificate aggregates live instead
    # of rescanning all N tokens after every exception.  This preserves the same
    # certificate semantics while making the sidecar path a plausible kernel
    # candidate rather than an O(N * exceptions) diagnostic.
    mask = np.zeros(n, dtype=bool)
    if selected:
        mask[np.fromiter(selected, dtype=np.int64)] = True
    mass = float(np.sum(probs[mask]))
    selected_weighted_norm = float(np.sum(probs[mask] * norms[mask]))
    omitted_weighted_norm = float(np.sum(probs[~mask] * norms[~mask]))

    def current_bound() -> dict[str, float]:
        selected_expected_norm = selected_weighted_norm / mass if mass > 0.0 else 0.0
        omitted_mass = max(0.0, 1.0 - mass)
        return {
            "value_error_bound_from_scores_and_norms": float(omitted_mass * selected_expected_norm + omitted_weighted_norm),
            "omitted_mass": float(omitted_mass),
            "selected_expected_value_norm_from_metadata": float(selected_expected_norm),
            "omitted_weighted_value_norm_from_metadata": float(omitted_weighted_norm),
        }

    bound = current_bound()
    exceptions_added = 0
    risk_order = sorted(
        (i for i in range(n) if i not in selected),
        key=lambda i: float(probs[i] * norms[i]),
        reverse=True,
    )
    while bound["value_error_bound_from_scores_and_norms"] > absolute_error_bound and exceptions_added < cap and risk_order:
        idx = int(risk_order.pop(0))
        selected.add(idx)
        contrib = float(probs[idx] * norms[idx])
        mass += float(probs[idx])
        selected_weighted_norm += contrib
        omitted_weighted_norm = max(0.0, omitted_weighted_norm - contrib)
        exceptions_added += 1
        bound = current_bound()
    sel = np.array(sorted(selected), dtype=np.int64)
    return SelectionResult(
        selected=sel,
        selector=f"value_norm_exception_mass_{str(target_mass).replace('.', 'p')}_bins{bins}",
        target_mass=float(target_mass),
        mass_certificate="exact_from_scores_plus_value_norm_metadata_tail_exceptions",
        certified_mass_from_scores=float(_score_only_mass(scores, sel)),
        selector_passes=int(base.selector_passes + 1),
        score_reads=int(base.score_reads + n),
        threshold_evals=int(base.threshold_evals),
        sort_free=False,
        selection_uses_value_norms=True,
        value_norm_reads=n,
        value_error_bound_from_scores_and_norms=bound["value_error_bound_from_scores_and_norms"],
        fallback="exception_cap_or_full_context" if bound["value_error_bound_from_scores_and_norms"] > absolute_error_bound else None,
        details={
            "bins": int(bins),
            "max_delta": float(max_delta),
            "target_mass": float(target_mass),
            "absolute_error_bound": float(absolute_error_bound),
            "base_selected_count": int(len(base.selected)),
            "exceptions_added": int(exceptions_added),
            "exception_cap": None if exception_cap is None else int(exception_cap),
            "bound_update_mode": "incremental_aggregate",
            **bound,
        },
    )


@dataclass(frozen=True)
class FrontierPoint:
    method: str
    budget_or_target: str
    selected_count: int
    mass_retained: float
    attention_rel_l2_error: float
    output_cosine: float
    value_reads: int
    qk_dot_products: int
    bytes_touched_est: int
    passes_quality_bar: bool


def compiler_points_for_row(scores: np.ndarray, values: np.ndarray, d_head: int, budgets=(8, 16, 32, 64, 128, 256), p_targets=(0.80, 0.90, 0.95, 0.98)) -> list[dict]:
    n = len(scores)
    probs = stable_softmax(scores)
    out: list[dict] = []
    for k in budgets:
        kk = min(int(k), n)
        sel = topk_indices(scores, kk)
        m = output_metrics(scores, values, sel)
        m.update({
            "method": f"topk_{kk}",
            "budget_or_target": str(kk),
            "value_reads": int(m["selected_count"]),
            "qk_dot_products": n,
            "score_reads": n,
            "bytes_touched_est": bytes_touched_est(n, n, int(m["selected_count"]), d_head, values.shape[-1]),
            "passes_quality_bar": passes_attention_quality_bar(m),
        })
        out.append(m)
    for p in p_targets:
        sel = topp_indices_from_probs(scores, probs, float(p))
        m = output_metrics(scores, values, sel)
        m.update({
            "method": f"topp_{str(p).replace('.', 'p')}",
            "budget_or_target": str(p),
            "value_reads": int(m["selected_count"]),
            "qk_dot_products": n,
            "score_reads": n,
            "bytes_touched_est": bytes_touched_est(n, n, int(m["selected_count"]), d_head, values.shape[-1]),
            "passes_quality_bar": passes_attention_quality_bar(m),
        })
        out.append(m)
    return out


def evaluate_selection_result(
    scores: np.ndarray,
    values: np.ndarray,
    selection: SelectionResult,
    d_head: int,
    method_label: str | None = None,
    target_mass: float = 0.95,
) -> dict:
    m = output_metrics(scores, values, selection.selected)
    selected_count = int(m["selected_count"])
    row = dict(m)
    row.update({
        "compiler": method_label or selection.selector,
        "method": method_label or selection.selector,
        "selector": selection.selector,
        "target_mass": selection.target_mass,
        "value_reads": selected_count,
        "qk_dot_products": len(scores),
        "score_reads": int(selection.score_reads),
        "selector_passes": int(selection.selector_passes),
        "threshold_evals": int(selection.threshold_evals),
        "sort_free_selector": bool(selection.sort_free),
        "selection_uses_values": bool(selection.selection_uses_values),
        "selection_uses_dense_output": bool(selection.selection_uses_dense_output),
        "selection_uses_value_norms": bool(selection.selection_uses_value_norms),
        "value_norm_reads": int(selection.value_norm_reads),
        "value_error_bound_from_scores_and_norms": selection.value_error_bound_from_scores_and_norms,
        "mass_certificate": selection.mass_certificate,
        "certified_mass_from_scores": selection.certified_mass_from_scores,
        "certificate_error_abs": abs(float(m["mass_retained"]) - float(selection.certified_mass_from_scores)) if selection.certified_mass_from_scores is not None else None,
        "fallback": selection.fallback,
        "bytes_touched_est": bytes_touched_est(len(scores), int(selection.score_reads), selected_count, d_head, values.shape[-1]),
        "metadata_reads": int(selection.value_norm_reads),
        "passes_value_norm_bound": (selection.value_error_bound_from_scores_and_norms is None or float(selection.value_error_bound_from_scores_and_norms) <= 0.15),
        "passes_quality_bar": passes_attention_quality_bar(m, target_mass=target_mass),
    })
    if selection.details:
        row.update({f"selector_{k}": v for k, v in selection.details.items()})
    return row


def mass_aware_compiler_points_for_row(
    scores: np.ndarray,
    values: np.ndarray,
    d_head: int,
    fixed_k: int,
    target_mass: float = 0.95,
    block: int = 32,
    hist_bins: int = 32,
    hist_max_delta: float = 16.0,
    deltas: Sequence[float] = DEFAULT_DELTAS,
) -> list[dict]:
    selectors = [
        ("full_dense", full_dense_selection(scores)),
        (f"exact_topk_{min(fixed_k, len(scores))}", exact_topk_selection(scores, fixed_k)),
        (f"ordered_topp_{str(target_mass).replace('.', 'p')}_bound", ordered_topp_selection(scores, target_mass)),
        (f"mass_delta_grid_{str(target_mass).replace('.', 'p')}", delta_grid_mass_selection(scores, target_mass, deltas=deltas)),
        (f"mass_histogram_{str(target_mass).replace('.', 'p')}_bins{hist_bins}", histogram_mass_selection(scores, target_mass, bins=hist_bins, max_delta=hist_max_delta)),
        (f"block_topb_certified_{str(target_mass).replace('.', 'p')}", block_local_topb_mass_selection(scores, target_mass, block=block)),
    ]
    rows = []
    truth_topk = set(map(int, topk_indices(scores, fixed_k)))
    for label, sel in selectors:
        r = evaluate_selection_result(scores, values, sel, d_head=d_head, method_label=label, target_mass=target_mass)
        selected_set = set(map(int, sel.selected))
        r["topk_hit_rate"] = float(len(selected_set & truth_topk) / max(1, min(fixed_k, len(scores))))
        r["value_read_fraction"] = float(r["value_reads"] / max(1, len(scores)))
        r["score_read_fraction"] = float(r["score_reads"] / max(1, len(scores)))
        r["mass_certified_without_values"] = bool(
            r["mass_certificate"] in {
                "trivial_full_context",
                "exact_from_scores_sorted_order_bound",
                "exact_from_scores_threshold_grid",
                "exact_from_scores_histogram_threshold",
                "exact_from_scores_block_local_widening",
            }
            and not r["selection_uses_values"]
            and not r["selection_uses_dense_output"]
        )
        rows.append(r)
    return rows


def guarded_mass_aware_compiler_points_for_row(
    scores: np.ndarray,
    values: np.ndarray,
    value_norms: np.ndarray | None,
    d_head: int,
    fixed_k: int,
    target_mass: float = 0.95,
    block: int = 32,
    hist_bins: int = 32,
    hist_max_delta: float = 16.0,
    value_error_bound: float = 0.15,
    include_ordered_topp: bool = True,
) -> list[dict]:
    """Evaluate a common guarded sparse-attention compiler panel for one row.

    This is the rev0048 refactor seam.  Earlier probes each hand-built their
    selector list, which made it easy for a method to disappear or change label
    between benchmarks.  This helper centralizes the contract used by trace
    probes: selectors may use scores; guarded selectors may additionally use
    per-token value-norm metadata; selectors may not inspect value vectors or
    dense outputs before returning indices.
    """
    norms = np.linalg.norm(values, axis=-1) if value_norms is None else np.asarray(value_norms, dtype=np.float64)
    selectors: list[tuple[str, SelectionResult]] = [
        ("full_dense", full_dense_selection(scores)),
        (f"exact_topk_{min(fixed_k, len(scores))}", exact_topk_selection(scores, fixed_k)),
    ]
    if include_ordered_topp:
        selectors.append((f"ordered_topp_{str(target_mass).replace('.', 'p')}_oracle_sort_bound", ordered_topp_selection(scores, target_mass)))
    selectors.extend([
        (f"mass_histogram_{str(target_mass).replace('.', 'p')}_bins{hist_bins}", histogram_mass_selection(scores, target_mass, bins=hist_bins, max_delta=hist_max_delta)),
        (f"block_topb_certified_{str(target_mass).replace('.', 'p')}", block_local_topb_mass_selection(scores, target_mass, block=block)),
        (
            f"value_norm_exception_mass_{str(target_mass).replace('.', 'p')}_bins{hist_bins}",
            value_norm_exception_mass_selection(
                scores,
                norms,
                target_mass=target_mass,
                bins=hist_bins,
                max_delta=hist_max_delta,
                absolute_error_bound=value_error_bound,
            ),
        ),
    ])
    truth_topk = set(map(int, topk_indices(scores, fixed_k)))
    rows: list[dict] = []
    for label, sel in selectors:
        r = evaluate_selection_result(scores, values, sel, d_head=d_head, method_label=label, target_mass=target_mass)
        selected_set = set(map(int, sel.selected))
        r["topk_hit_rate"] = float(len(selected_set & truth_topk) / max(1, min(fixed_k, len(scores))))
        r["value_read_fraction"] = float(r["value_reads"] / max(1, len(scores)))
        r["score_read_fraction"] = float(r["score_reads"] / max(1, len(scores)))
        r["mass_certified_without_value_vectors"] = bool(
            r["mass_certificate"] in {
                "trivial_full_context",
                "exact_from_scores_sorted_order_bound",
                "exact_from_scores_histogram_threshold",
                "exact_from_scores_block_local_widening",
                "exact_from_scores_plus_value_norm_metadata_tail_exceptions",
            }
            and not r["selection_uses_values"]
            and not r["selection_uses_dense_output"]
        )
        rows.append(r)
    return rows
