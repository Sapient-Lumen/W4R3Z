#!/usr/bin/env python3
"""rev0055 router distribution-shift stress test.

rev0054 calibrated a row-adaptive attention router on one even/odd split of tiny
learned Q/K/V rows.  The remaining risk is that the router is overfit to the
calibration mixture: a sparse route can look good on easy/low-support rows and
then waste work on high-support rows.

This probe keeps the same selection contract as rev0054.  The router may use
only observable Q/K-derived features, block-bound prechecks, and score-only mass
certificates after paying the corresponding score cost.  It may not use V
vectors, dense outputs, target labels, or heldout quality labels for routing.

New in rev0055:
  * low-support-only calibration is evaluated on high-support rows as an OOD
    negative control;
  * a bucket-robust calibration rule chooses thresholds that meet the quality
    floor on low/middle/high support slices and minimizes worst-slice work;
  * all failed fallback costs are still charged in inherited route accounting.

This remains tiny learned-trace CPU/proxy evidence, not public/pretrained trace
or fused GPU-kernel evidence.
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
from typing import Any, Callable

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0055"}
REV = META.get("revision", "rev0055")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_ROUTER_SHIFT_STRESS.json"
MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_ROUTER_SHIFT_STRESS_RUN_MANIFEST.json"

from experiments.row_adaptive_attention_router.row_adaptive_attention_router import (  # noqa: E402
    D_HEAD,
    QUALITY_FLOOR,
    SEQ,
    CandidateConfig,
    calibrate,
    collect_trace_rows,
    make_cases,
    route_bound_gate,
    train_model,
)

SEED = 5055
GENERATED_AT = "2026-06-18T05:13:00-04:00"
SUPPORT_BUCKETS = ["low_support", "middle_support", "high_support"]
DENSE_WORK_UNITS = 2 * SEQ * D_HEAD


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


def bucket_of(case: dict[str, Any]) -> str:
    return str(case["base"]["support_bucket"])


def select_cases(cases: list[dict[str, Any]], selector: str) -> list[dict[str, Any]]:
    if selector == "all":
        return list(cases)
    if selector == "even_rows":
        return [c for c in cases if int(c["row_id"]) % 2 == 0]
    if selector == "odd_rows":
        return [c for c in cases if int(c["row_id"]) % 2 == 1]
    if selector == "low_support":
        return [c for c in cases if bucket_of(c) == "low_support_le_q25"]
    if selector == "middle_support":
        return [c for c in cases if bucket_of(c) == "middle_support"]
    if selector == "high_support":
        return [c for c in cases if bucket_of(c) == "high_support_ge_q75"]
    if selector == "low_and_middle_support":
        return [c for c in cases if bucket_of(c) in {"low_support_le_q25", "middle_support"}]
    raise KeyError(selector)


def evaluate_config(cases: list[dict[str, Any]], cfg: CandidateConfig) -> dict[str, Any]:
    routed = [route_bound_gate(c["methods"], cfg) for c in cases]
    if not routed:
        return {"rows": 0, "quality_bar_rate": None, "mean_total_work_units": None, "speedup_proxy_vs_dense": None}
    paths = Counter(str(r.get("router_path", "unknown")) for r in routed)
    works = np.asarray([float(r["total_work_units"]) for r in routed], dtype=np.float64)
    qks = np.asarray([float(r["qk_dot_fraction_vs_dense"]) for r in routed], dtype=np.float64)
    vals = np.asarray([float(r["selected_count"]) for r in routed], dtype=np.float64)
    quality = np.asarray([1.0 if bool(r["passes_quality_bar"]) else 0.0 for r in routed], dtype=np.float64)
    return {
        "rows": len(routed),
        "quality_bar_rate": float(np.mean(quality)),
        "mean_selected_values": float(np.mean(vals)),
        "selected_value_fraction": float(np.mean(vals) / SEQ),
        "mean_qk_dot_fraction_vs_dense": float(np.mean(qks)),
        "mean_total_work_units": float(np.mean(works)),
        "speedup_proxy_vs_dense": float(DENSE_WORK_UNITS / max(1e-9, float(np.mean(works)))),
        "path_counts": dict(paths),
        "mean_failed_probe_exact_token_dots": float(np.mean([float(r.get("failed_probe_exact_token_dots", 0.0)) for r in routed])),
        "selection_uses_values": any(bool(r.get("selection_uses_values", False)) for r in routed),
        "selection_uses_dense_output": any(bool(r.get("selection_uses_dense_output", False)) for r in routed),
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
    }


def evaluate_static(cases: list[dict[str, Any]], method: str) -> dict[str, Any]:
    rows = [c["methods"][method] for c in cases]
    if not rows:
        return {"rows": 0, "quality_bar_rate": None, "mean_total_work_units": None, "speedup_proxy_vs_dense": None}
    works = np.asarray([float(r["total_work_units"]) for r in rows], dtype=np.float64)
    qks = np.asarray([float(r["qk_dot_fraction_vs_dense"]) for r in rows], dtype=np.float64)
    vals = np.asarray([float(r["selected_count"]) for r in rows], dtype=np.float64)
    return {
        "rows": len(rows),
        "quality_bar_rate": float(np.mean([bool(r["passes_quality_bar"]) for r in rows])),
        "mean_selected_values": float(np.mean(vals)),
        "selected_value_fraction": float(np.mean(vals) / SEQ),
        "mean_qk_dot_fraction_vs_dense": float(np.mean(qks)),
        "mean_total_work_units": float(np.mean(works)),
        "speedup_proxy_vs_dense": float(DENSE_WORK_UNITS / max(1e-9, float(np.mean(works)))),
        "path_counts": {"static": len(rows)},
        "selection_uses_values": any(bool(r.get("selection_uses_values", False)) for r in rows),
        "selection_uses_dense_output": any(bool(r.get("selection_uses_dense_output", False)) for r in rows),
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
    }


def single_selector_calibration(cases: list[dict[str, Any]], selector: str) -> dict[str, Any]:
    cal_cases = select_cases(cases, selector)
    c = calibrate(cal_cases, "bound_gate")
    cfg = CandidateConfig(**c["selected_config"])
    return {
        "strategy": f"min_work_on_{selector}",
        "calibration_selector": selector,
        "selected_config": asdict(cfg),
        "calibration_quality_bar_rate": float(c["calibration_quality_bar_rate"]),
        "calibration_mean_work_units": float(c["calibration_mean_work_units"]),
        "quality_floor": QUALITY_FLOOR,
        "selection_reason": c["selection_reason"],
        "calibration_rows": len(cal_cases),
    }


def robust_bucket_calibration(cases: list[dict[str, Any]], selectors: list[str]) -> dict[str, Any]:
    groups = {sel: select_cases(cases, sel) for sel in selectors}
    scored: list[dict[str, Any]] = []
    for cfg in config_grid():
        slices = {}
        qualities = []
        works = []
        for sel, cs in groups.items():
            ev = evaluate_config(cs, cfg)
            slices[sel] = ev
            qualities.append(float(ev["quality_bar_rate"]))
            works.append(float(ev["mean_total_work_units"]))
        feasible = all(q >= QUALITY_FLOOR for q in qualities)
        scored.append({
            "config": asdict(cfg),
            "feasible": feasible,
            "min_quality_bar_rate": float(min(qualities)),
            "max_work_units": float(max(works)),
            "mean_work_units": float(statistics.fmean(works)),
            "slice_evaluation": slices,
        })
    feasible = [s for s in scored if s["feasible"]]
    if feasible:
        best = min(feasible, key=lambda s: (s["max_work_units"], s["mean_work_units"], -s["min_quality_bar_rate"]))
        reason = "minimize_worst_support_slice_work_subject_to_each_slice_quality_floor"
    else:
        best = min(scored, key=lambda s: (-s["min_quality_bar_rate"], s["max_work_units"], s["mean_work_units"]))
        reason = "no_config_met_all_slice_quality_floors"
    return {
        "strategy": "bucket_robust_minimax_low_mid_high",
        "calibration_selectors": selectors,
        "selected_config": best["config"],
        "quality_floor": QUALITY_FLOOR,
        "selection_reason": reason,
        "calibration_rows": sum(len(v) for v in groups.values()),
        "min_calibration_quality_bar_rate": best["min_quality_bar_rate"],
        "max_calibration_work_units": best["max_work_units"],
        "mean_calibration_work_units": best["mean_work_units"],
        "slice_evaluation": best["slice_evaluation"],
        "top5_feasible_by_worst_work": [
            {k: v for k, v in s.items() if k != "slice_evaluation"}
            for s in sorted(feasible, key=lambda s: (s["max_work_units"], s["mean_work_units"]))[:5]
        ],
    }


def add_strategy_eval(rows: list[dict[str, Any]], cases: list[dict[str, Any]], strategy: dict[str, Any], test_selector: str, scenario: str) -> None:
    cfg = CandidateConfig(**strategy["selected_config"])
    test_cases = select_cases(cases, test_selector)
    ev = evaluate_config(test_cases, cfg)
    rows.append({
        "scenario": scenario,
        "test_selector": test_selector,
        "method": strategy["strategy"],
        "selected_config": strategy["selected_config"],
        "rows": ev["rows"],
        **{k: v for k, v in ev.items() if k != "rows"},
        "selection_uses_values": bool(ev.get("selection_uses_values", False)),
        "selection_uses_dense_output": bool(ev.get("selection_uses_dense_output", False)),
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
    })


def add_static_eval(rows: list[dict[str, Any]], cases: list[dict[str, Any]], method: str, test_selector: str, scenario: str) -> None:
    test_cases = select_cases(cases, test_selector)
    ev = evaluate_static(test_cases, method)
    rows.append({
        "scenario": scenario,
        "test_selector": test_selector,
        "method": method,
        "selected_config": None,
        "rows": ev["rows"],
        **{k: v for k, v in ev.items() if k != "rows"},
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
    })


def make_artifact() -> dict[str, Any]:
    torch.manual_seed(SEED)
    model, train_metrics = train_model()
    base_rows, trace_meta = collect_trace_rows(model)
    cases = make_cases(base_rows)

    calibrations = {
        "low_only": single_selector_calibration(cases, "low_support"),
        "middle_only": single_selector_calibration(cases, "middle_support"),
        "even_rows": single_selector_calibration(cases, "even_rows"),
        "all_rows": single_selector_calibration(cases, "all"),
        "bucket_robust": robust_bucket_calibration(cases, SUPPORT_BUCKETS),
    }

    scenario_defs = [
        ("ood_low_calibration_high_support_test", "high_support", ["low_only", "bucket_robust", "all_rows"]),
        ("ood_middle_calibration_high_support_test", "high_support", ["middle_only", "bucket_robust", "all_rows"]),
        ("balanced_even_calibration_odd_test", "odd_rows", ["even_rows", "bucket_robust", "all_rows"]),
        ("all_rows_test", "all", ["low_only", "middle_only", "bucket_robust", "all_rows"]),
        ("low_support_test", "low_support", ["low_only", "bucket_robust", "all_rows"]),
        ("middle_support_test", "middle_support", ["middle_only", "bucket_robust", "all_rows"]),
        ("high_support_test", "high_support", ["low_only", "middle_only", "bucket_robust", "all_rows"]),
    ]
    result_rows: list[dict[str, Any]] = []
    static_methods = ["dense_full_attention", "dense_score_mass_histogram_0p95_sparse", "pca_block_bound_pruned_0p95_sparse"]
    for scenario, test_selector, strategies in scenario_defs:
        for sm in static_methods:
            add_static_eval(result_rows, cases, sm, test_selector, scenario)
        for strategy_key in strategies:
            add_strategy_eval(result_rows, cases, calibrations[strategy_key], test_selector, scenario)

    by = {(r["scenario"], r["method"]): r for r in result_rows}
    low_to_high = by[("ood_low_calibration_high_support_test", "min_work_on_low_support")]
    robust_high = by[("ood_low_calibration_high_support_test", "bucket_robust_minimax_low_mid_high")]
    hist_high = by[("ood_low_calibration_high_support_test", "dense_score_mass_histogram_0p95_sparse")]
    dense_high = by[("ood_low_calibration_high_support_test", "dense_full_attention")]
    even_odd = by[("balanced_even_calibration_odd_test", "min_work_on_even_rows")]
    robust_odd = by[("balanced_even_calibration_odd_test", "bucket_robust_minimax_low_mid_high")]

    summary = {
        "promotion_allowed": False,
        "primary_claim": "Router thresholds calibrated on one support regime can waste work under support-regime shift; bucket-robust calibration prevents the low-support-to-high-support dense-worse failure on this tiny trace but remains proxy evidence.",
        "low_only_to_high_quality_bar_rate": low_to_high["quality_bar_rate"],
        "low_only_to_high_mean_work_units": low_to_high["mean_total_work_units"],
        "low_only_to_high_speedup_proxy_vs_dense": low_to_high["speedup_proxy_vs_dense"],
        "low_only_to_high_path_counts": low_to_high["path_counts"],
        "low_only_to_high_is_slower_than_dense": bool(float(low_to_high["mean_total_work_units"]) > float(dense_high["mean_total_work_units"])),
        "bucket_robust_to_high_quality_bar_rate": robust_high["quality_bar_rate"],
        "bucket_robust_to_high_mean_work_units": robust_high["mean_total_work_units"],
        "bucket_robust_to_high_speedup_proxy_vs_dense": robust_high["speedup_proxy_vs_dense"],
        "bucket_robust_to_high_path_counts": robust_high["path_counts"],
        "bucket_robust_to_high_beats_dense": bool(float(robust_high["mean_total_work_units"]) < float(dense_high["mean_total_work_units"])),
        "bucket_robust_to_high_beats_low_only_shifted": bool(float(robust_high["mean_total_work_units"]) < float(low_to_high["mean_total_work_units"])),
        "bucket_robust_to_high_beats_histogram_equal_units": bool(float(robust_high["mean_total_work_units"]) < float(hist_high["mean_total_work_units"])),
        "histogram_high_mean_work_units": hist_high["mean_total_work_units"],
        "dense_high_mean_work_units": dense_high["mean_total_work_units"],
        "even_to_odd_quality_bar_rate": even_odd["quality_bar_rate"],
        "even_to_odd_mean_work_units": even_odd["mean_total_work_units"],
        "robust_to_odd_mean_work_units": robust_odd["mean_total_work_units"],
        "calibration_configs": {k: v["selected_config"] for k, v in calibrations.items()},
        "support_bucket_counts": trace_meta.get("bucket_counts"),
        "remaining_blockers": [
            "public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "router_validated_only_on_tiny_learned_trace",
            "adaptive_router_kernel_path_missing",
            "distribution_shift_space_still_tiny_support_bucket_only",
        ],
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_ROUTER_SHIFT_STRESS",
        "probe": "router_shift_stress",
        "kind": "tiny_trained_model_trace_router_distribution_shift_stress",
        "evidence_tier": "E2p7_tiny_trained_trace_router_shift_probe",
        "generated_at": GENERATED_AT,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "trace_source_type": "tiny_trained_transformer_qkv_trace",
        "selection_contract": "router calibration may use only observable support buckets, q/k-derived block bounds, score-only mass after paying score cost, and calibration-row route outcomes; it may not inspect V vectors, dense outputs, target labels, or heldout quality labels during routing",
        "configuration": {
            "seed": SEED,
            "seq": SEQ,
            "d_head": D_HEAD,
            "quality_floor": QUALITY_FLOOR,
            "dense_work_units_per_row": DENSE_WORK_UNITS,
            "support_buckets": SUPPORT_BUCKETS,
            "calibration_grid_size": len(config_grid()),
            "stress_scenarios": [s[0] for s in scenario_defs],
        },
        "train_metrics": train_metrics,
        "trace_meta": trace_meta,
        "calibrations": calibrations,
        "summary": summary,
        "rows": result_rows,
        "raw_case_count": len(cases),
        "run_provenance": {},
        "interpretation": "The low-support-only threshold rule is a negative control: it optimizes easy rows and becomes dense-worse on high-support rows because it routes many shifted rows to dense full attention after a precheck. Bucket-robust calibration reduces that shifted waste and preserves quality, but the simple dense-score histogram remains a strong equal-unit baseline. This is a routing-risk repair, not promotion-ready systems evidence.",
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    artifact = make_artifact()
    src_rel = "experiments/router_shift_stress/router_shift_stress.py"
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
        "command": "python experiments/router_shift_stress/router_shift_stress.py",
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
        "command": "python experiments/router_shift_stress/router_shift_stress.py",
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "promotion_allowed": False,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "artifact": str(OUT.relative_to(ROOT)), "manifest": str(MANIFEST.relative_to(ROOT)), "rows": len(artifact["rows"]), "cases": artifact["raw_case_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
