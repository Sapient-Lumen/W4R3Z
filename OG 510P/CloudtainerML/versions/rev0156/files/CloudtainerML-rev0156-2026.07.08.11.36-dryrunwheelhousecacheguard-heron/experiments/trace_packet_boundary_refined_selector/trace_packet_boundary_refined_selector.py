#!/usr/bin/env python3
"""rev0068 boundary-refined selector-layout benchmark over local Q/K/V traces.

rev0065 showed that a deployable coarse histogram mass selector preserved output
quality but over-selected many values; exact-sort Top-p selected fewer values but
its selector cost was too high.  rev0068 tests the narrow, risky middle ground:
coarse histogram plus a boundary-bin refinement that sorts only the threshold bin.

This is still a local tiny-trained CPU trace replay.  It is not public/pretrained
evidence, not GPU/fused-kernel timing, and not a score-path sparse win because all
QK scores are computed before selection.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0068"}
REV = META.get("revision", "rev0068")
REVUP = REV.upper()
STAMP = "2026-06-18T14:06:00-04:00"
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_BOUNDARY_REFINED_SELECTOR_LAYOUT.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_BOUNDARY_REFINED_SELECTOR_LAYOUT_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_BOUNDARY_REFINED_SELECTOR_LAYOUT_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_boundary_refined_selector"
CPP = ROOT / "experiments" / "trace_packet_boundary_refined_selector" / "trace_packet_boundary_refined_selector.cpp"
EXE = BUILD_DIR / "trace_packet_boundary_refined_selector"
REPEATS = int(os.environ.get("CTML_BOUNDARY_REFINED_REPEATS", "6000"))
TARGET_MASS = float(os.environ.get("CTML_BOUNDARY_REFINED_TARGET_MASS", "0.96"))
HIST_BINS = int(os.environ.get("CTML_BOUNDARY_REFINED_HIST_BINS", "32"))
REGIME_IDS = {"low_support_lt12": 0, "mid_support_12_28": 1, "high_support_ge28": 2}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_qk_packet() -> Path:
    candidates = sorted((ROOT / "artifacts" / "trace-bundles").glob("REV*_TINY_TRAINED_QK_TRACE_PACKET.npz"), reverse=True)
    preferred = [p for p in candidates if p.name.startswith("REV0062") or p.name.startswith(REVUP)]
    if preferred:
        return preferred[0]
    if candidates:
        return candidates[0]
    raise FileNotFoundError("no Q/K/V trace packet found")


def prepare_input(packet_path: Path) -> dict[str, Any]:
    z = np.load(packet_path)
    queries = np.asarray(z["queries"], dtype=np.float64)
    keys = np.asarray(z["keys"], dtype=np.float64)
    values = np.asarray(z["values"], dtype=np.float64)
    regimes_raw = z["regime"] if "regime" in z.files else np.array(["unknown"] * queries.shape[0])
    rows, n_tokens, d_key = keys.shape
    d_value = values.shape[2]
    if queries.shape != (rows, d_key) or values.shape != (rows, n_tokens, d_value):
        raise ValueError(f"bad Q/K/V shapes q={queries.shape} k={keys.shape} v={values.shape}")
    regime_ids = np.array([REGIME_IDS.get(str(r), -1) for r in regimes_raw], dtype=np.int32)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    with BIN_INPUT.open("wb") as f:
        f.write(b"CTMLTR68")
        f.write(struct.pack("QQQQ", int(rows), int(n_tokens), int(d_key), int(d_value)))
        f.write(np.ascontiguousarray(queries, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(keys, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(values, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(regime_ids, dtype=np.int32).tobytes(order="C"))
    packet_manifest_path = packet_path.with_name(packet_path.stem + "_MANIFEST.json")
    packet_manifest = json.loads(packet_manifest_path.read_text(encoding="utf-8")) if packet_manifest_path.exists() else {}
    return {
        "trace_packet": packet_path.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(packet_path),
        "trace_packet_manifest": packet_manifest,
        "rows": int(rows),
        "n_tokens": int(n_tokens),
        "d_key": int(d_key),
        "d_value": int(d_value),
        "regime_counts": {str(k): int(v) for k, v in zip(*np.unique(regimes_raw.astype(str), return_counts=True))},
        "input_bin": BIN_INPUT.relative_to(ROOT).as_posix(),
        "input_bin_sha256": sha256_file(BIN_INPUT),
    }


def compile_native() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        raise RuntimeError("no C++ compiler found")
    cmd = [compiler, "-O3", "-std=c++17", "-march=native", str(CPP), "-o", str(EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)


def run_native() -> dict[str, Any]:
    compile_native()
    proc = subprocess.run([str(EXE), str(BIN_INPUT), str(REPEATS), str(TARGET_MASS), str(HIST_BINS)], cwd=ROOT, check=True, text=True, capture_output=True)
    return json.loads(proc.stdout)


def speedup(timing: dict[str, Any], key: str) -> float | None:
    base = timing.get("dense_qk_online_ms")
    val = timing.get(key)
    if not base or not val:
        return None
    return float(base) / float(val)


def build_artifact(prep: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    timing = native.get("timing", {})
    all_rows = native.get("all_rows", {})
    coarse = all_rows.get("coarse_hist_index", {})
    refined = all_rows.get("refined_hist_index", {})
    refined_packed = all_rows.get("refined_hist_packed", {})
    exact = all_rows.get("exact_sort_index", {})
    overshoot = native.get("overshoot", {})
    refined_selected_delta = float(overshoot.get("refined_minus_exact_mean_selected_count", 0.0))
    coarse_selected_delta = float(overshoot.get("coarse_minus_exact_mean_selected_count", 0.0))
    refined_reduces_overshoot = refined_selected_delta < max(0.0, coarse_selected_delta) * 0.35
    refined_index_speedup = speedup(timing, "refined_hist_index_qk_included_ms")
    refined_packed_speedup = speedup(timing, "refined_hist_packed_qk_included_ms")
    coarse_speedup = speedup(timing, "coarse_hist_index_qk_included_ms")
    exact_speedup = speedup(timing, "exact_sort_index_qk_included_ms")
    maybe_fast = max([x or 0.0 for x in [refined_index_speedup, refined_packed_speedup, coarse_speedup]]) > 1.05
    summary = {
        "trace_packet_rows": prep["rows"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "selector_layout_overhead_paid_in_timed_loop": True,
        "selectors_use_values_or_dense_outputs": False,
        "qk_score_computation_measured": True,
        "qk_dot_fraction_deployable_sparse": native.get("accounting", {}).get("qk_dot_fraction_deployable_sparse"),
        "row_local_score_prob_storage_required": True,
        "boundary_bucket_sort_paid": True,
        "coarse_hist_quality_rate": coarse.get("quality_rate"),
        "coarse_hist_mean_selected_fraction": coarse.get("mean_selected_fraction"),
        "coarse_hist_speedup_vs_dense": coarse_speedup,
        "refined_hist_quality_rate": refined.get("quality_rate"),
        "refined_hist_mean_selected_fraction": refined.get("mean_selected_fraction"),
        "refined_hist_speedup_vs_dense": refined_index_speedup,
        "refined_hist_packed_quality_rate": refined_packed.get("quality_rate"),
        "refined_hist_packed_mean_selected_fraction": refined_packed.get("mean_selected_fraction"),
        "refined_hist_packed_speedup_vs_dense": refined_packed_speedup,
        "exact_sort_quality_rate": exact.get("quality_rate"),
        "exact_sort_mean_selected_fraction": exact.get("mean_selected_fraction"),
        "exact_sort_speedup_vs_dense": exact_speedup,
        "coarse_minus_exact_mean_selected_count": coarse_selected_delta,
        "refined_minus_exact_mean_selected_count": refined_selected_delta,
        "refined_reduces_histogram_overshoot": refined_reduces_overshoot,
        "refined_boundary_candidate_fraction": refined.get("mean_boundary_candidate_fraction"),
        "promotion_allowed": False,
        "deployable_promoted_paths": [],
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "all_deployable_selectors_still_compute_full_qk_scores",
            "row_local_score_storage_or_prob_storage_still_required",
            "boundary_refinement_overhead_not_a_fused_kernel_win",
            "no_deployable_score_path_sparse_win_measured",
        ],
    }
    if refined_reduces_overshoot and float(refined.get("quality_rate", 0.0)) >= 0.99:
        interpretation = "boundary-bin refinement repairs much of the coarse histogram over-selection, but it still pays full QK/row-local probability storage and remains non-promotional without a score-path or fused-kernel win"
    else:
        interpretation = "boundary-bin refinement did not repair the selector bottleneck enough to change the sparse-attention decision; promotion remains blocked"
    if maybe_fast:
        interpretation += "; any local CPU speedup is fenced because all QK scores are still materialized before selection"
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_BOUNDARY_REFINED_SELECTOR_LAYOUT",
        "generated_at": STAMP,
        "measurement_scope": "local tiny-trained Q/K/V trace; native CPU timing; selector/layout overhead paid; boundary bucket sort paid; all deployable paths compute full QK scores; row-local score/probability storage required; not public/pretrained; not GPU; not fused; no promotion",
        "trace_input": prep,
        "native_result": native,
        "summary": summary,
        "interpretation": interpretation,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "promotion_allowed": False,
    }


def write_manifest(artifact: dict[str, Any]) -> None:
    sources = [
        "experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.py",
        "experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.cpp",
        artifact["trace_input"]["trace_packet"],
    ]
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "generated_at": STAMP,
        "command": "python experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.py",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "parameters": {"repeats": REPEATS, "target_mass": TARGET_MASS, "hist_bins": HIST_BINS},
        "sources": [{"path": s, "sha256": sha256_file(ROOT / s)} for s in sources if (ROOT / s).exists()],
        "native_binary": EXE.relative_to(ROOT).as_posix() if EXE.exists() else None,
        "native_binary_sha256": sha256_file(EXE) if EXE.exists() else None,
        "promotion_allowed": False,
    }
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    prep = prepare_input(find_qk_packet())
    native = run_native()
    artifact = build_artifact(prep, native)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    write_manifest(artifact)
    print(json.dumps({"status": "pass", "artifact": OUT.relative_to(ROOT).as_posix(), "refined_selected_fraction": artifact["summary"].get("refined_hist_mean_selected_fraction"), "refined_speedup": artifact["summary"].get("refined_hist_speedup_vs_dense")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
