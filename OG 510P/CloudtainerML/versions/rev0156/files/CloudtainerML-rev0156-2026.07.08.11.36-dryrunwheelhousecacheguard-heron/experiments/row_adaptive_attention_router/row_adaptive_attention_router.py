#!/usr/bin/env python3
"""rev0054 learned-trace row-adaptive attention router.

rev0053 showed that observable block bounds sometimes skip QK score work on
learned tiny-model traces, but high-support rows erase the advantage.  The next
risk is a global sparse mechanism being applied where it should route to a
fallback.  This probe trains the same tiny trace model, splits captured Q/K/V
rows into calibration and heldout partitions, learns a tiny rule from observable
row features, and evaluates whether an adaptive router can avoid the worst waste.

Selection contract:
  * The router may use q, k, block centroids/radii built from k, block upper
    bounds, exact scores for opened blocks, and full dense scores only after it
    explicitly pays for a dense-score fallback.
  * The router may not inspect V vectors, dense outputs, target labels, or
    heldout quality labels when deciding a row path.
  * If a row first probes block bounds and then falls back, the failed probe
    cost is counted in the final row cost.

This remains tiny CPU/model-trace evidence, not public/pretrained or GPU fused
kernel evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0054"}
REV = META.get("revision", "rev0054")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_ROW_ADAPTIVE_ATTENTION_ROUTER.json"
MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_ROW_ADAPTIVE_ATTENTION_ROUTER_RUN_MANIFEST.json"

from experiments.attention_compiler_core.attention_core import (  # noqa: E402
    output_metrics,
    passes_attention_quality_bar,
    stable_softmax,
)
from experiments.learned_trace_block_bounds.learned_trace_block_bounds import (  # noqa: E402
    BLOCK_SIZE,
    D_HEAD,
    SEQ,
    SQRT_D,
    TARGET_MASS,
    build_index,
    collect_trace_rows,
    contiguous_blocks,
    dense_hist_selection,
    full_dense_selection,
    pca_sorted_blocks,
    train_model,
)

SEED = 5054
QUALITY_FLOOR = 0.985
REUSE_QUERIES = 32


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class CandidateConfig:
    bound_support_threshold: float
    hist_selected_fraction_threshold: float
    name: str


def dense_scores(q: np.ndarray, k: np.ndarray) -> np.ndarray:
    return (k @ q) / SQRT_D


def block_upper_bounds(q: np.ndarray, index: Any) -> np.ndarray:
    qnorm = float(np.linalg.norm(q))
    return (index.centroids @ q) / SQRT_D + qnorm * index.radii / SQRT_D


def effective_support_from_weights(xs: np.ndarray) -> float:
    p = stable_softmax(xs)
    return float(1.0 / max(1e-300, np.sum(p * p)))


def block_select_with_cached_bounds(q: np.ndarray, k: np.ndarray, index: Any, ubs: np.ndarray) -> dict[str, Any]:
    """Open blocks by cached upper bounds and certify a lower mass bound.

    This is a copy of the rev0053 block selector with a crucial accounting
    change: block-bound dots are assumed already paid by the router precheck,
    so the returned exact_token_score_dots only counts opened-token QK work.
    """
    order = np.argsort(-ubs)
    opened: list[int] = []
    opened_mask = np.zeros(len(index.groups), dtype=bool)
    exact_scores: dict[int, float] = {}
    cert = 0.0
    opened_blocks = 0
    for bi in order:
        bi = int(bi)
        opened_mask[bi] = True
        opened_blocks += 1
        for t in index.groups[bi]:
            t = int(t)
            opened.append(t)
            exact_scores[t] = float((k[t] @ q) / SQRT_D)
        opened_vals = np.fromiter(exact_scores.values(), dtype=np.float64)
        upper_unopened = ubs[~opened_mask]
        m = float(np.max(opened_vals)) if len(opened_vals) else -np.inf
        if len(upper_unopened):
            m = max(m, float(np.max(upper_unopened)))
        opened_w = float(np.sum(np.exp(np.clip(opened_vals - m, -80.0, 80.0)))) if len(opened_vals) else 0.0
        unopened_w = 0.0
        for j, ub in enumerate(ubs):
            if not opened_mask[j]:
                unopened_w += len(index.groups[j]) * float(math.exp(max(-80.0, min(80.0, float(ub - m)))))
        cert = opened_w / max(1e-300, opened_w + unopened_w)
        if cert >= TARGET_MASS:
            break
    selected = np.unique(np.asarray(opened, dtype=np.int64))
    return {
        "selected": selected,
        "exact_token_score_dots": int(len(selected)),
        "opened_blocks": int(opened_blocks),
        "asserted_lower_bound_mass_certificate": float(cert),
    }


def row_static_methods(base_row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    q = base_row["q"]
    k = base_row["k"]
    v = base_row["v"]
    scores = base_row["scores"]
    n = len(scores)
    groups_pca = pca_sorted_blocks(k, BLOCK_SIZE)
    idx = build_index("pca_sorted_mean_radius_block_pruned_0p95_sparse", k, groups_pca, False)
    ubs = block_upper_bounds(q, idx)
    bound_support = effective_support_from_weights(ubs)
    bound_gap = float(np.max(ubs) - np.partition(ubs, -2)[-2]) if len(ubs) > 1 else float("inf")
    block = block_select_with_cached_bounds(q, k, idx, ubs)
    hist_sel = dense_hist_selection(scores)
    dense_sel = full_dense_selection(scores)

    methods: dict[str, dict[str, Any]] = {}
    for method_name, selected, qk_dots, exact_dots, block_dots, opened_blocks, cert, dense_scores_required, block_pruned in [
        (
            "dense_full_attention",
            dense_sel.selected,
            n,
            n,
            0,
            0,
            1.0,
            True,
            False,
        ),
        (
            "dense_score_mass_histogram_0p95_sparse",
            hist_sel.selected,
            n,
            n,
            0,
            0,
            float(hist_sel.asserted_lower_bound_mass_certificate),
            True,
            False,
        ),
        (
            "pca_block_bound_pruned_0p95_sparse",
            block["selected"],
            len(idx.groups) + block["exact_token_score_dots"],
            block["exact_token_score_dots"],
            len(idx.groups),
            block["opened_blocks"],
            block["asserted_lower_bound_mass_certificate"],
            False,
            True,
        ),
    ]:
        metrics = output_metrics(scores, v, selected)
        methods[method_name] = {
            "method": method_name,
            "selected": selected,
            "selected_count": int(metrics["selected_count"]),
            "selected_fraction": float(metrics["selected_count"] / n),
            "value_reads": int(metrics["selected_count"]),
            "mass_retained": float(metrics["mass_retained"]),
            "attention_rel_l2_error": float(metrics["attention_rel_l2_error"]),
            "output_cosine": float(metrics["output_cosine"]),
            "passes_quality_bar": bool(passes_attention_quality_bar(metrics, TARGET_MASS)),
            "qk_dot_products": int(qk_dots),
            "qk_dot_fraction_vs_dense": float(qk_dots / n),
            "exact_token_score_dots": int(exact_dots),
            "block_bound_dots": int(block_dots),
            "opened_blocks": int(opened_blocks),
            "asserted_lower_bound_mass_certificate": float(cert),
            "exact_dense_scores_required": bool(dense_scores_required),
            "computes_all_qk_scores_before_selection": bool(dense_scores_required),
            "block_upper_bound_pruning": bool(block_pruned),
            "observable_index_from_key_cache": bool(block_pruned),
            "selection_uses_values": False,
            "selection_uses_dense_output": False,
        }
    for payload in methods.values():
        payload["score_work_units"] = int(payload["qk_dot_products"] * D_HEAD)
        payload["value_work_units"] = int(payload["value_reads"] * D_HEAD)
        payload["total_work_units"] = int(payload["score_work_units"] + payload["value_work_units"])
        payload["speedup_proxy_vs_dense"] = float((2 * n * D_HEAD) / max(1, payload["total_work_units"]))
    methods["features"] = {
        "bound_support": float(bound_support),
        "bound_gap": float(bound_gap),
        "n_blocks": int(len(idx.groups)),
        "pca_block_selected_fraction": float(methods["pca_block_bound_pruned_0p95_sparse"]["selected_fraction"]),
        "pca_block_qk_fraction": float(methods["pca_block_bound_pruned_0p95_sparse"]["qk_dot_fraction_vs_dense"]),
        "hist_selected_fraction": float(methods["dense_score_mass_histogram_0p95_sparse"]["selected_fraction"]),
        "index_build_ns": int(idx.build_ns),
    }
    return methods


def route_bound_gate(methods: dict[str, dict[str, Any]], cfg: CandidateConfig) -> dict[str, Any]:
    """Bound-precheck router with honest failed-route accounting.

    Every row pays one PCA block-bound precheck before choosing a path.  If the
    upper-bound softmax is concentrated enough, the row uses block pruning and
    pays opened-token exact scores.  Otherwise it pays dense QK scores and then
    either uses histogram sparse values or full dense values.
    """
    n = SEQ
    precheck_block_dots = int(methods["features"]["n_blocks"])
    bound_support = float(methods["features"]["bound_support"])
    hist_fraction = float(methods["features"]["hist_selected_fraction"])
    if bound_support <= cfg.bound_support_threshold:
        chosen = methods["pca_block_bound_pruned_0p95_sparse"]
        path = "block_pruned_after_bound_precheck"
        qk_dots = int(chosen["qk_dot_products"])
        failed_probe_exact_dots = 0
        fallback_dense_score_dots = 0
    else:
        if hist_fraction <= cfg.hist_selected_fraction_threshold:
            chosen = methods["dense_score_mass_histogram_0p95_sparse"]
            path = "dense_score_mass_histogram_after_bound_precheck"
        else:
            chosen = methods["dense_full_attention"]
            path = "dense_full_after_bound_precheck"
        qk_dots = precheck_block_dots + n
        failed_probe_exact_dots = 0
        fallback_dense_score_dots = n
    selected_count = int(chosen["selected_count"])
    total_units = int((qk_dots + selected_count) * D_HEAD)
    return {
        **{k: v for k, v in chosen.items() if k != "selected"},
        "method": "adaptive_bound_gate_router_calibrated",
        "router_path": path,
        "router_config": cfg.__dict__,
        "qk_dot_products": int(qk_dots),
        "qk_dot_fraction_vs_dense": float(qk_dots / n),
        "block_bound_precheck_dots": precheck_block_dots,
        "failed_probe_exact_token_dots": failed_probe_exact_dots,
        "fallback_dense_score_dots": fallback_dense_score_dots,
        "score_work_units": int(qk_dots * D_HEAD),
        "value_work_units": int(selected_count * D_HEAD),
        "total_work_units": total_units,
        "speedup_proxy_vs_dense": float((2 * n * D_HEAD) / max(1, total_units)),
        "exact_dense_scores_required": path != "block_pruned_after_bound_precheck",
        "computes_all_qk_scores_before_selection": path != "block_pruned_after_bound_precheck",
        "block_upper_bound_pruning": path == "block_pruned_after_bound_precheck",
        "observable_index_from_key_cache": True,
        "selection_uses_values": False,
        "selection_uses_dense_output": False,
    }


def route_block_attempt_then_fallback(methods: dict[str, dict[str, Any]], cfg: CandidateConfig) -> dict[str, Any]:
    """More aggressive router that may waste exact block-open work before fallback."""
    n = SEQ
    pca = methods["pca_block_bound_pruned_0p95_sparse"]
    hist = methods["dense_score_mass_histogram_0p95_sparse"]
    if float(pca["qk_dot_fraction_vs_dense"]) <= 0.75 and float(pca["selected_fraction"]) <= 0.75:
        chosen = pca
        path = "block_pruned_after_full_attempt"
        qk_dots = int(pca["qk_dot_products"])
        failed_probe_exact_dots = 0
        fallback_dense_score_dots = 0
    else:
        if float(hist["selected_fraction"]) <= cfg.hist_selected_fraction_threshold:
            chosen = hist
            path = "histogram_fallback_after_failed_block_attempt"
        else:
            chosen = methods["dense_full_attention"]
            path = "dense_fallback_after_failed_block_attempt"
        qk_dots = int(pca["qk_dot_products"] + n)
        failed_probe_exact_dots = int(pca["exact_token_score_dots"])
        fallback_dense_score_dots = n
    selected_count = int(chosen["selected_count"])
    total_units = int((qk_dots + selected_count) * D_HEAD)
    return {
        **{k: v for k, v in chosen.items() if k != "selected"},
        "method": "adaptive_block_attempt_then_fallback_router_calibrated",
        "router_path": path,
        "router_config": cfg.__dict__,
        "qk_dot_products": int(qk_dots),
        "qk_dot_fraction_vs_dense": float(qk_dots / n),
        "block_bound_precheck_dots": int(methods["features"]["n_blocks"]),
        "failed_probe_exact_token_dots": failed_probe_exact_dots,
        "fallback_dense_score_dots": fallback_dense_score_dots,
        "score_work_units": int(qk_dots * D_HEAD),
        "value_work_units": int(selected_count * D_HEAD),
        "total_work_units": total_units,
        "speedup_proxy_vs_dense": float((2 * n * D_HEAD) / max(1, total_units)),
        "exact_dense_scores_required": path != "block_pruned_after_full_attempt",
        "computes_all_qk_scores_before_selection": path != "block_pruned_after_full_attempt",
        "block_upper_bound_pruning": path == "block_pruned_after_full_attempt",
        "observable_index_from_key_cache": True,
        "selection_uses_values": False,
        "selection_uses_dense_output": False,
    }


def summarize(rows: list[dict[str, Any]], partition: str, method: str) -> dict[str, Any]:
    rs = [r for r in rows if r["partition"] == partition and r["method"] == method]
    if not rs:
        return {"partition": partition, "method": method, "rows": 0}
    paths: dict[str, int] = {}
    for r in rs:
        paths[str(r.get("router_path", "static"))] = paths.get(str(r.get("router_path", "static")), 0) + 1
    dense_work = 2 * SEQ * D_HEAD
    mean_total_work = float(np.mean([r["total_work_units"] for r in rs]))
    return {
        "partition": partition,
        "method": method,
        "rows": len(rs),
        "quality_bar_rate": float(np.mean([bool(r["passes_quality_bar"]) for r in rs])),
        "mean_selected_values": float(np.mean([r["selected_count"] for r in rs])),
        "selected_value_fraction": float(np.mean([r["selected_fraction"] for r in rs])),
        "mean_true_mass_retained": float(np.mean([r["mass_retained"] for r in rs])),
        "mean_attention_rel_l2_error": float(np.mean([r["attention_rel_l2_error"] for r in rs])),
        "mean_output_cosine": float(np.mean([r["output_cosine"] for r in rs])),
        "mean_qk_dot_products": float(np.mean([r["qk_dot_products"] for r in rs])),
        "qk_dot_fraction_vs_dense": float(np.mean([r["qk_dot_fraction_vs_dense"] for r in rs])),
        "mean_total_work_units": mean_total_work,
        "speedup_proxy_vs_dense": float(dense_work / max(1e-9, mean_total_work)),
        "mean_row_speedup_proxy_vs_dense": float(np.mean([r["speedup_proxy_vs_dense"] for r in rs])),
        "mean_failed_probe_exact_token_dots": float(np.mean([r.get("failed_probe_exact_token_dots", 0) for r in rs])),
        "path_counts": paths,
        "selection_uses_values": any(bool(r.get("selection_uses_values", False)) for r in rs),
        "selection_uses_dense_output": any(bool(r.get("selection_uses_dense_output", False)) for r in rs),
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
    }


def evaluate_config(cases: list[dict[str, Any]], cfg: CandidateConfig, router: str) -> tuple[float, float]:
    routed = []
    for c in cases:
        if router == "bound_gate":
            routed.append(route_bound_gate(c["methods"], cfg))
        elif router == "block_attempt":
            routed.append(route_block_attempt_then_fallback(c["methods"], cfg))
        else:
            raise KeyError(router)
    quality = float(np.mean([bool(r["passes_quality_bar"]) for r in routed]))
    mean_work = float(np.mean([float(r["total_work_units"]) for r in routed]))
    return quality, mean_work


def calibrate(cases: list[dict[str, Any]], router: str) -> dict[str, Any]:
    configs = []
    for bs in [1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]:
        for hs in [0.25, 0.40, 0.55, 0.70, 0.85, 1.00]:
            configs.append(CandidateConfig(bound_support_threshold=bs, hist_selected_fraction_threshold=hs, name=f"bs{bs}_hs{hs}"))
    scored = []
    for cfg in configs:
        q, work = evaluate_config(cases, cfg, router)
        scored.append({"config": cfg, "quality": q, "mean_work_units": work})
    feasible = [s for s in scored if s["quality"] >= QUALITY_FLOOR]
    if feasible:
        best = min(feasible, key=lambda x: (x["mean_work_units"], -x["quality"]))
        reason = f"min_work_among_configs_with_quality_ge_{QUALITY_FLOOR}"
    else:
        best = min(scored, key=lambda x: (-x["quality"], x["mean_work_units"]))
        reason = "no_config_met_quality_floor_choose_highest_quality_then_min_work"
    return {
        "router": router,
        "selected_config": best["config"].__dict__,
        "calibration_quality_bar_rate": best["quality"],
        "calibration_mean_work_units": best["mean_work_units"],
        "quality_floor": QUALITY_FLOOR,
        "selection_reason": reason,
        "grid_size": len(scored),
        "top5_by_work_feasible": [
            {"config": s["config"].__dict__, "quality": s["quality"], "mean_work_units": s["mean_work_units"]}
            for s in sorted(feasible, key=lambda x: x["mean_work_units"])[:5]
        ],
    }


def make_cases(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases = []
    for i, row in enumerate(base_rows):
        methods = row_static_methods(row)
        partition = "calibration" if (i % 2 == 0) else "heldout"
        cases.append({"row_id": i, "partition": partition, "base": row, "methods": methods})
    return cases


def make_artifact() -> dict[str, Any]:
    torch.manual_seed(SEED)
    model, train_metrics = train_model()
    base_rows, trace_meta = collect_trace_rows(model)
    cases = make_cases(base_rows)
    calibration_cases = [c for c in cases if c["partition"] == "calibration"]
    bound_gate_cal = calibrate(calibration_cases, "bound_gate")
    block_attempt_cal = calibrate(calibration_cases, "block_attempt")
    bound_cfg = CandidateConfig(**bound_gate_cal["selected_config"])
    attempt_cfg = CandidateConfig(**block_attempt_cal["selected_config"])

    row_results: list[dict[str, Any]] = []
    for c in cases:
        base = c["base"]
        common = {
            "row_id": c["row_id"],
            "partition": c["partition"],
            "trace_source_type": "tiny_trained_transformer_qkv_trace",
            "trace_public_pretrained": False,
            "layer": int(base["layer"]),
            "head": int(base["head"]),
            "support_bucket": str(base["support_bucket"]),
            "effective_support": float(base["effective_support"]),
            "max_probability": float(base["max_probability"]),
            "bound_support": float(c["methods"]["features"]["bound_support"]),
            "hist_selected_fraction_feature": float(c["methods"]["features"]["hist_selected_fraction"]),
            "pca_block_qk_fraction_feature": float(c["methods"]["features"]["pca_block_qk_fraction"]),
            "target_mass": TARGET_MASS,
            "N": SEQ,
            "D": D_HEAD,
            "block_size": BLOCK_SIZE,
        }
        for static_name in [
            "dense_full_attention",
            "dense_score_mass_histogram_0p95_sparse",
            "pca_block_bound_pruned_0p95_sparse",
        ]:
            payload = {k: v for k, v in c["methods"][static_name].items() if k != "selected"}
            row_results.append({**common, **payload, "router_path": "static"})
        row_results.append({**common, **route_bound_gate(c["methods"], bound_cfg)})
        row_results.append({**common, **route_block_attempt_then_fallback(c["methods"], attempt_cfg)})

    methods = sorted(set(r["method"] for r in row_results))
    summary_rows = []
    for part in ["calibration", "heldout", "all"]:
        if part == "all":
            # Duplicate temporary partition so summarize can reuse one path.
            all_rows = [{**r, "partition": "all"} for r in row_results]
            for m in methods:
                summary_rows.append(summarize(all_rows, "all", m))
        else:
            for m in methods:
                summary_rows.append(summarize(row_results, part, m))

    heldout_by_method = {r["method"]: r for r in summary_rows if r["partition"] == "heldout"}
    dense = heldout_by_method["dense_full_attention"]
    router = heldout_by_method["adaptive_bound_gate_router_calibrated"]
    attempt = heldout_by_method["adaptive_block_attempt_then_fallback_router_calibrated"]
    pca = heldout_by_method["pca_block_bound_pruned_0p95_sparse"]
    hist = heldout_by_method["dense_score_mass_histogram_0p95_sparse"]
    heldout_methods = [dense, hist, pca, router, attempt]
    sensitivity = []
    for qk_weight in [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]:
        weighted = []
        dense_cost = qk_weight * dense["mean_qk_dot_products"] + dense["mean_selected_values"]
        for m in heldout_methods:
            cost = qk_weight * m["mean_qk_dot_products"] + m["mean_selected_values"]
            weighted.append({
                "method": m["method"],
                "qk_weight": qk_weight,
                "mean_weighted_cost": float(cost),
                "speedup_vs_dense_weighted": float(dense_cost / max(1e-9, cost)),
                "quality_bar_rate": m["quality_bar_rate"],
            })
        sensitivity.append({
            "qk_weight": qk_weight,
            "best_method_by_weighted_cost": min(weighted, key=lambda x: x["mean_weighted_cost"])["method"],
            "weighted_rows": sorted(weighted, key=lambda x: x["mean_weighted_cost"]),
        })
    denom = float(hist["mean_qk_dot_products"] - router["mean_qk_dot_products"])
    if abs(denom) > 1e-9:
        breakeven = float((router["mean_selected_values"] - hist["mean_selected_values"]) / denom)
    else:
        breakeven = None
    summary = {
        "promotion_allowed": False,
        "primary_claim": "A row-adaptive learned-trace router is calibrated only on calibration rows and evaluated on heldout rows; failed sparse probes are charged to the final path.",
        "heldout_dense_quality_rate": dense["quality_bar_rate"],
        "heldout_hist_quality_rate": hist["quality_bar_rate"],
        "heldout_pca_quality_rate": pca["quality_bar_rate"],
        "heldout_adaptive_bound_gate_quality_rate": router["quality_bar_rate"],
        "heldout_adaptive_bound_gate_speedup_proxy_vs_dense": router["speedup_proxy_vs_dense"],
        "heldout_adaptive_bound_gate_qk_fraction": router["qk_dot_fraction_vs_dense"],
        "heldout_adaptive_bound_gate_path_counts": router["path_counts"],
        "heldout_block_attempt_quality_rate": attempt["quality_bar_rate"],
        "heldout_block_attempt_speedup_proxy_vs_dense": attempt["speedup_proxy_vs_dense"],
        "heldout_block_attempt_mean_failed_probe_exact_token_dots": attempt["mean_failed_probe_exact_token_dots"],
        "equal_unit_best_heldout_method": min(heldout_methods, key=lambda m: m["mean_total_work_units"])["method"],
        "adaptive_bound_gate_beats_dense_proxy_on_heldout": bool(router["speedup_proxy_vs_dense"] > 1.0 and router["quality_bar_rate"] >= QUALITY_FLOOR),
        "adaptive_bound_gate_beats_dense_score_histogram_equal_units": bool(router["mean_total_work_units"] < hist["mean_total_work_units"]),
        "qk_weight_break_even_adaptive_bound_gate_vs_histogram": breakeven,
        "block_attempt_overhead_exposed": bool(attempt["mean_failed_probe_exact_token_dots"] > 0 or attempt["speedup_proxy_vs_dense"] < router["speedup_proxy_vs_dense"]),
        "cost_model_sensitivity": sensitivity,
        "remaining_blockers": [
            "public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "adaptive_router_kernel_path_missing",
            "row_router_calibrated_only_on_tiny_trace_distribution",
        ],
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_ROW_ADAPTIVE_ATTENTION_ROUTER",
        "probe": "row_adaptive_attention_router",
        "kind": "tiny_trained_model_trace_row_adaptive_sparse_attention_router",
        "evidence_tier": "E2p6_tiny_trained_trace_adaptive_router_probe",
        "generated_at": "2026-06-18T04:31:00-04:00",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "selection_contract": "router may use q/k-derived block bounds and score-only mass after paying score costs; router may not inspect V vectors, dense outputs, target labels, or heldout quality labels during selection",
        "configuration": {
            "seq": SEQ,
            "d_head": D_HEAD,
            "block_size": BLOCK_SIZE,
            "target_mass": TARGET_MASS,
            "quality_floor": QUALITY_FLOOR,
            "reuse_queries": REUSE_QUERIES,
            "seed": SEED,
            "partition_rule": "even row_id calibration, odd row_id heldout",
            "dense_work_units_per_row": 2 * SEQ * D_HEAD,
        },
        "train_metrics": train_metrics,
        "trace_meta": trace_meta,
        "calibration": {
            "bound_gate_router": bound_gate_cal,
            "block_attempt_router": block_attempt_cal,
        },
        "summary": summary,
        "rows": summary_rows,
        "raw_row_count": len(row_results),
        "raw_rows_sample": row_results[:30],
        "run_provenance": {},
        "interpretation": "This revision tests a narrow but important systems decision: do not deploy one sparse path globally. A bound-precheck router can avoid some score work on easy learned rows while falling back honestly; an aggressive block-attempt fallback is included to expose wasted failed-route cost. This remains proxy work-unit evidence, not GPU timing or public/pretrained trace evidence.",
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    artifact = make_artifact()
    src_rel = "experiments/row_adaptive_attention_router/row_adaptive_attention_router.py"
    core_rel = "experiments/attention_compiler_core/attention_core.py"
    learned_rel = "experiments/learned_trace_block_bounds/learned_trace_block_bounds.py"
    artifact["run_provenance"] = {
        "script": src_rel,
        "source_path": src_rel,
        "source_sha256": sha256_file(ROOT / src_rel),
        "core_source_path": core_rel,
        "core_source_sha256": sha256_file(ROOT / core_rel),
        "learned_trace_source_path": learned_rel,
        "learned_trace_source_sha256": sha256_file(ROOT / learned_rel),
        "command": "python experiments/row_adaptive_attention_router/row_adaptive_attention_router.py",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "torch": torch.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "seed_policy": artifact["configuration"],
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "source": src_rel,
        "source_sha256": sha256_file(ROOT / src_rel),
        "core_source": core_rel,
        "core_source_sha256": sha256_file(ROOT / core_rel),
        "learned_trace_source": learned_rel,
        "learned_trace_source_sha256": sha256_file(ROOT / learned_rel),
        "command": "python experiments/row_adaptive_attention_router/row_adaptive_attention_router.py",
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "promotion_allowed": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "artifact": str(OUT.relative_to(ROOT)), "manifest": str(MANIFEST.relative_to(ROOT)), "rows": len(artifact["rows"]), "raw_rows": artifact["raw_row_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
