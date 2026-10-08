#!/usr/bin/env python3
"""rev0056 router cost-frontier stress.

rev0055 showed that bucket-robust routing prevents a low-support-calibrated
router from becoming slower than dense on high-support rows.  The remaining risk
is subtler: the row-adaptive router can look attractive only under an assumed
QK/value cost ratio.  If that assumption is unmeasured or shifts by platform,
router claims can be promoted too early.

This probe recalibrates the bound-gate router for a grid of qk_weight/value_weight
cost models and evaluates it against the simple dense-score mass histogram.  It
uses the same tiny learned Q/K/V trace generator as rev0055, keeps public/GPU
claims false, and forbids V/dense-output/heldout-quality leakage in selection.

The purpose is not to find a new winner; it is to make proxy-cost dependency an
explicit veto surface.
"""
from __future__ import annotations

import hashlib
import json
import platform
import statistics
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0056"}
REV = META.get("revision", "rev0056")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_ROUTER_COST_FRONTIER.json"
MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_ROUTER_COST_FRONTIER_RUN_MANIFEST.json"

from experiments.row_adaptive_attention_router.row_adaptive_attention_router import (  # noqa: E402
    D_HEAD,
    QUALITY_FLOOR,
    SEQ,
    CandidateConfig,
    collect_trace_rows,
    make_cases,
    route_bound_gate,
    train_model,
)

SEED = 5056
GENERATED_AT = "2026-06-18T05:56:00-04:00"
VALUE_WEIGHT = 1.0
QK_WEIGHTS = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0]
SUPPORT_SELECTORS = ["low_support", "middle_support", "high_support"]
STATIC_METHODS = [
    "dense_full_attention",
    "dense_score_mass_histogram_0p95_sparse",
    "pca_block_bound_pruned_0p95_sparse",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def config_grid() -> list[CandidateConfig]:
    return [
        CandidateConfig(bound_support_threshold=bs, hist_selected_fraction_threshold=hs, name=f"bs{bs}_hs{hs}")
        for bs in [1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
        for hs in [0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    ]


def select_cases(cases: list[dict[str, Any]], selector: str) -> list[dict[str, Any]]:
    if selector == "all":
        return list(cases)
    if selector == "calibration_even":
        return [c for c in cases if c["partition"] == "calibration"]
    if selector == "heldout_odd":
        return [c for c in cases if c["partition"] == "heldout"]
    if selector == "low_support":
        return [c for c in cases if str(c["base"]["support_bucket"]) == "low_support_le_q25"]
    if selector == "middle_support":
        return [c for c in cases if str(c["base"]["support_bucket"]) == "middle_support"]
    if selector == "high_support":
        return [c for c in cases if str(c["base"]["support_bucket"]) == "high_support_ge_q75"]
    raise KeyError(selector)


def weighted_cost(row: dict[str, Any], qk_weight: float, value_weight: float = VALUE_WEIGHT) -> float:
    return float(D_HEAD * (qk_weight * float(row["qk_dot_products"]) + value_weight * float(row["selected_count"])))


def dense_weighted_cost(qk_weight: float, value_weight: float = VALUE_WEIGHT) -> float:
    return float(D_HEAD * (qk_weight * SEQ + value_weight * SEQ))


def route_rows(cases: list[dict[str, Any]], cfg: CandidateConfig) -> list[dict[str, Any]]:
    return [route_bound_gate(c["methods"], cfg) for c in cases]


def static_rows(cases: list[dict[str, Any]], method: str) -> list[dict[str, Any]]:
    return [c["methods"][method] for c in cases]


def summarize_rows(rows: list[dict[str, Any]], qk_weight: float, method: str, selector: str, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    costs = np.asarray([weighted_cost(r, qk_weight) for r in rows], dtype=np.float64)
    dense_cost = dense_weighted_cost(qk_weight)
    paths = Counter(str(r.get("router_path", "static")) for r in rows)
    qks = np.asarray([float(r["qk_dot_products"]) for r in rows], dtype=np.float64)
    vals = np.asarray([float(r["selected_count"]) for r in rows], dtype=np.float64)
    quality = np.asarray([1.0 if bool(r["passes_quality_bar"]) else 0.0 for r in rows], dtype=np.float64)
    return {
        "selector": selector,
        "method": method,
        "qk_weight": float(qk_weight),
        "value_weight": float(VALUE_WEIGHT),
        "rows": len(rows),
        "quality_bar_rate": float(np.mean(quality)) if len(rows) else None,
        "mean_weighted_cost_units": float(np.mean(costs)) if len(rows) else None,
        "speedup_vs_dense_weighted": float(dense_cost / max(1e-9, float(np.mean(costs)))) if len(rows) else None,
        "mean_qk_dot_products": float(np.mean(qks)) if len(rows) else None,
        "mean_qk_fraction_vs_dense": float(np.mean(qks) / SEQ) if len(rows) else None,
        "mean_selected_values": float(np.mean(vals)) if len(rows) else None,
        "mean_selected_fraction": float(np.mean(vals) / SEQ) if len(rows) else None,
        "path_counts": dict(paths),
        "router_config": cfg,
        "beats_dense": bool(float(np.mean(costs)) < dense_cost and float(np.mean(quality)) >= QUALITY_FLOOR) if len(rows) else False,
        "selection_uses_values": any(bool(r.get("selection_uses_values", False)) for r in rows),
        "selection_uses_dense_output": any(bool(r.get("selection_uses_dense_output", False)) for r in rows),
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
    }


def evaluate_config(cases: list[dict[str, Any]], cfg: CandidateConfig, qk_weight: float) -> dict[str, Any]:
    rows = route_rows(cases, cfg)
    return summarize_rows(rows, qk_weight, "cost_calibrated_adaptive_bound_gate_router", "calibration_slice", asdict(cfg))


def calibrate_cost_model(cases: list[dict[str, Any]], qk_weight: float) -> dict[str, Any]:
    buckets = {sel: select_cases(cases, sel) for sel in SUPPORT_SELECTORS}
    scored: list[dict[str, Any]] = []
    for cfg in config_grid():
        slices: dict[str, Any] = {}
        qualities: list[float] = []
        costs: list[float] = []
        for sel, cs in buckets.items():
            ev = evaluate_config(cs, cfg, qk_weight)
            slices[sel] = ev
            qualities.append(float(ev["quality_bar_rate"]))
            costs.append(float(ev["mean_weighted_cost_units"]))
        feasible = all(q >= QUALITY_FLOOR for q in qualities)
        scored.append({
            "config": asdict(cfg),
            "feasible": feasible,
            "min_quality_bar_rate": float(min(qualities)),
            "max_bucket_weighted_cost_units": float(max(costs)),
            "mean_bucket_weighted_cost_units": float(statistics.fmean(costs)),
            "slice_evaluation": slices,
        })
    feasible = [s for s in scored if s["feasible"]]
    if feasible:
        best = min(feasible, key=lambda s: (s["max_bucket_weighted_cost_units"], s["mean_bucket_weighted_cost_units"], -s["min_quality_bar_rate"]))
        reason = "minimize_worst_support_bucket_weighted_cost_subject_to_each_bucket_quality_floor"
    else:
        best = min(scored, key=lambda s: (-s["min_quality_bar_rate"], s["max_bucket_weighted_cost_units"]))
        reason = "no_config_met_each_bucket_quality_floor"
    return {
        "qk_weight": float(qk_weight),
        "value_weight": float(VALUE_WEIGHT),
        "strategy": "cost_model_specific_bucket_robust_bound_gate",
        "selected_config": best["config"],
        "selection_reason": reason,
        "calibration_rows": sum(len(v) for v in buckets.values()),
        "min_calibration_quality_bar_rate": best["min_quality_bar_rate"],
        "max_bucket_weighted_cost_units": best["max_bucket_weighted_cost_units"],
        "mean_bucket_weighted_cost_units": best["mean_bucket_weighted_cost_units"],
        "top5_feasible_by_worst_cost": [
            {k: v for k, v in s.items() if k != "slice_evaluation"}
            for s in sorted(feasible, key=lambda s: (s["max_bucket_weighted_cost_units"], s["mean_bucket_weighted_cost_units"]))[:5]
        ],
    }


def add_static_and_router_rows(out_rows: list[dict[str, Any]], cases: list[dict[str, Any]], qk_weight: float, calibration: dict[str, Any], selectors: Iterable[str]) -> None:
    cfg = CandidateConfig(**calibration["selected_config"])
    for selector in selectors:
        cs = select_cases(cases, selector)
        for method in STATIC_METHODS:
            out_rows.append(summarize_rows(static_rows(cs, method), qk_weight, method, selector, None))
        out_rows.append(summarize_rows(route_rows(cs, cfg), qk_weight, "cost_calibrated_adaptive_bound_gate_router", selector, calibration["selected_config"]))


def first_weight_for(rows: list[dict[str, Any]], selector: str) -> float | None:
    by: dict[float, dict[str, dict[str, Any]]] = {}
    for r in rows:
        if r["selector"] == selector:
            by.setdefault(float(r["qk_weight"]), {})[r["method"]] = r
    winners: list[float] = []
    for w, m in by.items():
        router = m.get("cost_calibrated_adaptive_bound_gate_router")
        hist = m.get("dense_score_mass_histogram_0p95_sparse")
        if router and hist and float(router["quality_bar_rate"]) >= QUALITY_FLOOR:
            if float(router["mean_weighted_cost_units"]) < float(hist["mean_weighted_cost_units"]):
                winners.append(w)
    return min(winners) if winners else None


def best_methods_by_weight(rows: list[dict[str, Any]], selector: str) -> list[dict[str, Any]]:
    out = []
    for qk_weight in QK_WEIGHTS:
        rs = [r for r in rows if r["selector"] == selector and float(r["qk_weight"]) == float(qk_weight) and float(r["quality_bar_rate"]) >= QUALITY_FLOOR]
        best = min(rs, key=lambda r: float(r["mean_weighted_cost_units"]))
        out.append({
            "selector": selector,
            "qk_weight": float(qk_weight),
            "best_quality_feasible_method": best["method"],
            "best_weighted_cost_units": best["mean_weighted_cost_units"],
            "speedup_vs_dense_weighted": best["speedup_vs_dense_weighted"],
        })
    return out


def make_artifact() -> dict[str, Any]:
    torch.manual_seed(SEED)
    model, train_metrics = train_model()
    base_rows, trace_meta = collect_trace_rows(model)
    cases = make_cases(base_rows)
    calibration_pool = select_cases(cases, "all")

    calibrations = {str(w): calibrate_cost_model(calibration_pool, w) for w in QK_WEIGHTS}
    result_rows: list[dict[str, Any]] = []
    selectors = ["all", "low_support", "middle_support", "high_support", "heldout_odd"]
    for w in QK_WEIGHTS:
        add_static_and_router_rows(result_rows, cases, w, calibrations[str(w)], selectors)

    equal_all = {r["method"]: r for r in result_rows if r["selector"] == "all" and float(r["qk_weight"]) == 1.0}
    equal_high = {r["method"]: r for r in result_rows if r["selector"] == "high_support" and float(r["qk_weight"]) == 1.0}
    router_equal = equal_all["cost_calibrated_adaptive_bound_gate_router"]
    hist_equal = equal_all["dense_score_mass_histogram_0p95_sparse"]
    router_high_equal = equal_high["cost_calibrated_adaptive_bound_gate_router"]
    hist_high_equal = equal_high["dense_score_mass_histogram_0p95_sparse"]
    all_first = first_weight_for(result_rows, "all")
    high_first = first_weight_for(result_rows, "high_support")
    heldout_first = first_weight_for(result_rows, "heldout_odd")

    # Approximate empirical break-even using the equal-unit selected router config on all rows.
    # For row-wise mean costs, router < histogram when w*(qk_r-qk_h) + (v_r-v_h) < 0.
    denom = float(hist_equal["mean_qk_dot_products"] - router_equal["mean_qk_dot_products"])
    if denom > 1e-9:
        continuous_break_even_all = float((router_equal["mean_selected_values"] - hist_equal["mean_selected_values"]) / denom)
    else:
        continuous_break_even_all = None
    summary = {
        "promotion_allowed": False,
        "primary_claim": "Router value depends on the QK/value cost ratio; the cube must not promote adaptive routing when wins require unmeasured proxy weights or disappear on high-support rows.",
        "equal_unit_router_beats_histogram_all": bool(float(router_equal["mean_weighted_cost_units"]) < float(hist_equal["mean_weighted_cost_units"])),
        "equal_unit_router_beats_histogram_high_support": bool(float(router_high_equal["mean_weighted_cost_units"]) < float(hist_high_equal["mean_weighted_cost_units"])),
        "equal_unit_router_all_cost_units": router_equal["mean_weighted_cost_units"],
        "equal_unit_histogram_all_cost_units": hist_equal["mean_weighted_cost_units"],
        "equal_unit_router_high_cost_units": router_high_equal["mean_weighted_cost_units"],
        "equal_unit_histogram_high_cost_units": hist_high_equal["mean_weighted_cost_units"],
        "first_qk_weight_router_beats_histogram_all": all_first,
        "first_qk_weight_router_beats_histogram_high_support": high_first,
        "first_qk_weight_router_beats_histogram_heldout": heldout_first,
        "continuous_break_even_qk_weight_all_using_equal_unit_config": continuous_break_even_all,
        "cost_model_dependency_exposed": bool((all_first is not None and all_first > 1.0) or high_first is None),
        "unmeasured_cost_model_claim_blocked": True,
        "quality_floor": QUALITY_FLOOR,
        "qk_weight_grid": QK_WEIGHTS,
        "best_methods_all": best_methods_by_weight(result_rows, "all"),
        "best_methods_high_support": best_methods_by_weight(result_rows, "high_support"),
        "remaining_blockers": [
            "public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "measured_platform_qk_value_cost_ratio_missing",
            "adaptive_router_kernel_path_missing",
            "router_validated_only_on_tiny_learned_trace",
        ],
    }

    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_ROUTER_COST_FRONTIER",
        "probe": "router_cost_frontier",
        "kind": "tiny_trained_model_trace_router_cost_model_frontier",
        "evidence_tier": "E2p8_tiny_trained_trace_router_cost_frontier_probe",
        "generated_at": GENERATED_AT,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "trace_source_type": "tiny_trained_transformer_qkv_trace",
        "selection_contract": "router calibration may use observable support buckets, q/k-derived block bounds, score-only mass after paying score cost, and calibration-row route outcomes; it may not inspect V vectors, dense outputs, target labels, heldout quality labels, or measured hardware timings during routing",
        "cost_contract": "qk_weight/value_weight is an explicit proxy assumption; any router win that depends on qk_weight > 1 is not a measured systems claim",
        "configuration": {
            "seed": SEED,
            "seq": SEQ,
            "d_head": D_HEAD,
            "quality_floor": QUALITY_FLOOR,
            "value_weight": VALUE_WEIGHT,
            "qk_weight_grid": QK_WEIGHTS,
            "calibration_grid_size": len(config_grid()),
            "support_bucket_count": len(SUPPORT_SELECTORS),
        },
        "train_metrics": train_metrics,
        "trace_meta": trace_meta,
        "calibrations_by_qk_weight": calibrations,
        "summary": summary,
        "rows": result_rows,
        "raw_case_count": len(cases),
        "run_provenance": {},
        "interpretation": "rev0056 converts the router decision into a cost-frontier problem. If the adaptive router only beats the dense-score histogram at high assumed QK/value weights, that is useful guidance for kernel work but not promotion-ready evidence. High-support rows remain the harshest slice and often preserve the histogram baseline.",
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    artifact = make_artifact()
    src_rel = "experiments/router_cost_frontier/router_cost_frontier.py"
    router_rel = "experiments/row_adaptive_attention_router/row_adaptive_attention_router.py"
    learned_rel = "experiments/learned_trace_block_bounds/learned_trace_block_bounds.py"
    core_rel = "experiments/attention_compiler_core/attention_core.py"
    artifact["run_provenance"] = {
        "script": src_rel,
        "source_path": src_rel,
        "source_sha256": sha256_file(ROOT / src_rel),
        "row_router_source_path": router_rel,
        "row_router_source_sha256": sha256_file(ROOT / router_rel),
        "learned_trace_source_path": learned_rel,
        "learned_trace_source_sha256": sha256_file(ROOT / learned_rel),
        "core_source_path": core_rel,
        "core_source_sha256": sha256_file(ROOT / core_rel),
        "command": "python experiments/router_cost_frontier/router_cost_frontier.py",
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
        "row_router_source": router_rel,
        "row_router_source_sha256": sha256_file(ROOT / router_rel),
        "learned_trace_source": learned_rel,
        "learned_trace_source_sha256": sha256_file(ROOT / learned_rel),
        "core_source": core_rel,
        "core_source_sha256": sha256_file(ROOT / core_rel),
        "command": "python experiments/router_cost_frontier/router_cost_frontier.py",
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "promotion_allowed": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "artifact": str(OUT.relative_to(ROOT)),
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "rows": len(artifact["rows"]),
        "cases": artifact["raw_case_count"],
        "equal_unit_router_beats_histogram_all": artifact["summary"]["equal_unit_router_beats_histogram_all"],
        "first_qk_weight_router_beats_histogram_all": artifact["summary"]["first_qk_weight_router_beats_histogram_all"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
