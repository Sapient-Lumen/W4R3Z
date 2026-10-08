#!/usr/bin/env python3
"""rev0065 deployable selector/layout overhead benchmark over local Q/K/V traces.

rev0064 proved an important layout fact with oracle side inputs: selected-index and
prepacked value layouts can make sparse value accumulation faster than a dense
value sweep on the local learned trace.  The next risky question is whether a
non-oracle selector can produce those layouts cheaply enough.

This probe therefore pays selector and layout construction inside the timed native
loop.  Selectors are score-only: they may use Q/K-derived scores and softmax
probabilities, but not V vectors, dense outputs, labels, or oracle support lists.

Compared paths:
  * dense QK online attention.
  * histogram mass selector + selected-index gather.
  * histogram mass selector + per-query packed selected values.
  * exact-sort Top-p selector + selected-index gather.
  * exact-sort Top-p selector + per-query packed selected values.

All paths still compute all QK scores, so this cannot be a score-path sparse win.
It is also not public/pretrained evidence and not GPU/fused-kernel timing.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0065"}
REV = META.get("revision", "rev0065")
REVUP = REV.upper()
STAMP = "2026-06-18T12:26:00-04:00"

OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_deployable_selector_layout"
CPP = ROOT / "experiments" / "trace_packet_deployable_selector_layout" / "trace_packet_deployable_selector_layout.cpp"
EXE = BUILD_DIR / "trace_packet_deployable_selector_layout"
REPEATS = int(os.environ.get("CTML_DEPLOY_SELECTOR_LAYOUT_REPEATS", "6000"))
TARGET_MASS = float(os.environ.get("CTML_DEPLOY_SELECTOR_TARGET_MASS", "0.96"))
HIST_BINS = int(os.environ.get("CTML_DEPLOY_SELECTOR_HIST_BINS", "32"))
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
        f.write(b"CTMLTR65")
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
    accounting = native.get("accounting", {})
    hist = all_rows.get("hist_index", {})
    sort = all_rows.get("exact_sort_index", {})
    hist_packed = all_rows.get("hist_packed", {})
    sort_packed = all_rows.get("exact_sort_packed", {})

    hist_index_speedup = speedup(timing, "hist_index_qk_included_ms")
    hist_packed_speedup = speedup(timing, "hist_packed_qk_included_ms")
    exact_sort_index_speedup = speedup(timing, "exact_sort_index_qk_included_ms")
    exact_sort_packed_speedup = speedup(timing, "exact_sort_packed_qk_included_ms")
    qk_only_fraction = None
    if timing.get("qk_only_ms") and timing.get("dense_qk_online_ms"):
        qk_only_fraction = float(timing["qk_only_ms"]) / float(timing["dense_qk_online_ms"])

    deployable_paths = {
        "hist_index": {
            "quality_rate": hist.get("quality_rate"),
            "mean_selected_fraction": hist.get("mean_selected_fraction"),
            "speedup_vs_dense": hist_index_speedup,
            "selector_layout_cost_paid": True,
        },
        "hist_packed": {
            "quality_rate": hist_packed.get("quality_rate"),
            "mean_selected_fraction": hist_packed.get("mean_selected_fraction"),
            "speedup_vs_dense": hist_packed_speedup,
            "selector_layout_cost_paid": True,
        },
        "exact_sort_index": {
            "quality_rate": sort.get("quality_rate"),
            "mean_selected_fraction": sort.get("mean_selected_fraction"),
            "speedup_vs_dense": exact_sort_index_speedup,
            "selector_layout_cost_paid": True,
        },
        "exact_sort_packed": {
            "quality_rate": sort_packed.get("quality_rate"),
            "mean_selected_fraction": sort_packed.get("mean_selected_fraction"),
            "speedup_vs_dense": exact_sort_packed_speedup,
            "selector_layout_cost_paid": True,
        },
    }
    promotable = []
    for name, row in deployable_paths.items():
        if float(row.get("quality_rate") or 0.0) >= 0.99 and float(row.get("speedup_vs_dense") or 0.0) > 1.05 and accounting.get("qk_dot_fraction_deployable_sparse") < 1.0:
            promotable.append(name)

    if hist_index_speedup and hist_index_speedup > 1.0 and hist.get("quality_rate", 0) >= 0.99:
        interpretation = "deployable score-only histogram index path clears dense on this local CPU trace, but it still computes every QK score and is not a fused/GPU/public-trace claim"
    elif exact_sort_packed_speedup and exact_sort_packed_speedup > 1.0 and sort_packed.get("quality_rate", 0) >= 0.99:
        interpretation = "exact-sort Top-p packed path clears dense despite paying selector/layout cost, but histogram did not; selector quality/overhead remains the bottleneck"
    else:
        interpretation = "selector and layout overhead consume the rev0064 oracle value-layout headroom on this local CPU trace; sparse value layout is not enough without a cheaper selector or score-path savings"

    summary = {
        "trace_packet_rows": prep["rows"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "selector_layout_overhead_paid_in_timed_loop": True,
        "selectors_use_values_or_dense_outputs": False,
        "qk_score_computation_measured": True,
        "qk_dot_fraction_deployable_sparse": accounting.get("qk_dot_fraction_deployable_sparse"),
        "qk_only_fraction_of_dense_time": qk_only_fraction,
        "hist_index_quality_rate": hist.get("quality_rate"),
        "hist_index_mean_selected_fraction": hist.get("mean_selected_fraction"),
        "hist_index_speedup_vs_dense": hist_index_speedup,
        "hist_packed_quality_rate": hist_packed.get("quality_rate"),
        "hist_packed_mean_selected_fraction": hist_packed.get("mean_selected_fraction"),
        "hist_packed_speedup_vs_dense": hist_packed_speedup,
        "exact_sort_index_quality_rate": sort.get("quality_rate"),
        "exact_sort_index_mean_selected_fraction": sort.get("mean_selected_fraction"),
        "exact_sort_index_speedup_vs_dense": exact_sort_index_speedup,
        "exact_sort_packed_quality_rate": sort_packed.get("quality_rate"),
        "exact_sort_packed_mean_selected_fraction": sort_packed.get("mean_selected_fraction"),
        "exact_sort_packed_speedup_vs_dense": exact_sort_packed_speedup,
        "best_deployable_speedup_vs_dense": max(float(x.get("speedup_vs_dense") or 0.0) for x in deployable_paths.values()),
        "deployable_promoted_paths": promotable,
        "promotion_allowed": False,
        "selector_layout_interpretation": interpretation,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "all_deployable_selector_layout_paths_still_compute_all_qk_scores",
            "materialized_or_row_local_score_prob_storage_required_for_selector",
            "no_score_path_sparse_win_measured",
            "fused_kernel_layout_generation_not_measured",
        ],
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_DEPLOYABLE_SELECTOR_LAYOUT_OVERHEAD",
        "created_at": STAMP,
        "measurement_scope": "native CPU deployable score-only selector/layout replay over a local tiny-trained Q/K/V packet; selector and selected-index/packed layout construction are paid in the timed loop; not public/pretrained; not GPU; not fused; not score-path sparse because all QK dots are still computed",
        "trace_packet": prep["trace_packet"],
        "trace_packet_sha256": prep["trace_packet_sha256"],
        "trace_packet_manifest": prep["trace_packet_manifest"],
        "input_bin": prep["input_bin"],
        "input_bin_sha256": prep["input_bin_sha256"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "promotion_allowed": False,
        "target_mass": TARGET_MASS,
        "histogram_bins": HIST_BINS,
        "trace_summary": {"regime_counts": prep["regime_counts"]},
        "native_result": native,
        "deployable_paths": deployable_paths,
        "summary": summary,
        "claim_boundary": "This is the first non-oracle selected-layout replay: support is generated from Q/K scores in the timed loop and uses no V/dense-output oracle. It still computes all QK scores and is local CPU evidence only, so even a speedup here would not be a fused sparse-attention promotion.",
    }


def write_manifest(artifact: dict[str, Any]) -> None:
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "python_source": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "python_source_sha256": sha256_file(Path(__file__).resolve()),
        "source": CPP.relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(CPP),
        "native_input": BIN_INPUT.relative_to(ROOT).as_posix(),
        "native_input_sha256": sha256_file(BIN_INPUT),
        "trace_packet": artifact["trace_packet"],
        "trace_packet_sha256": artifact["trace_packet_sha256"],
        "command": f"{sys.executable} experiments/trace_packet_deployable_selector_layout/trace_packet_deployable_selector_layout.py",
        "created_at": STAMP,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "native_repeats": REPEATS,
            "histogram_bins": HIST_BINS,
            "target_mass": TARGET_MASS,
        },
        "claim_boundary": "selector and selected-layout construction are paid in-loop; selectors use Q/K scores/probabilities only; not public/pretrained, not GPU, not fused, not score-path sparse",
        "promotion_allowed": False,
    }
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    packet = find_qk_packet()
    prep = prepare_input(packet)
    native = run_native()
    artifact = build_artifact(prep, native)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    write_manifest(artifact)
    s = artifact["summary"]
    print(json.dumps({
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "hist_index_speedup": s["hist_index_speedup_vs_dense"],
        "hist_index_quality": s["hist_index_quality_rate"],
        "exact_sort_packed_speedup": s["exact_sort_packed_speedup_vs_dense"],
        "promotion_allowed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
