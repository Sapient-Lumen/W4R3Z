#!/usr/bin/env python3
"""rev0066 support-reuse amortization benchmark over local Q/K/V traces.

rev0065 paid selector and selected-layout construction per row and found that
non-oracle score-only selection consumed the rev0064 oracle value-layout headroom.
rev0066 tests the next loophole: amortize support construction across related
rows.  This is a score-path question: reused support can avoid full QK over all
keys for non-anchor rows, but only if the anchor support still preserves the
non-anchor rows' attention output.

The probe is local CPU/native evidence over the tiny-trained trace packet.  It is
not public/pretrained evidence, not a GPU/fused-kernel measurement, and not a
promotion-ready systems claim.
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
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0066"}
REV = META.get("revision", "rev0066")
REVUP = REV.upper()
STAMP = "2026-06-18T13:04:00-04:00"
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_SUPPORT_REUSE_AMORTIZATION.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_SUPPORT_REUSE_AMORTIZATION_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_SUPPORT_REUSE_AMORTIZATION_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_support_reuse"
CPP = ROOT / "experiments" / "trace_packet_support_reuse" / "trace_packet_support_reuse.cpp"
EXE = BUILD_DIR / "trace_packet_support_reuse"
REPEATS = int(os.environ.get("CTML_SUPPORT_REUSE_REPEATS", "5000"))
TARGET_MASS = float(os.environ.get("CTML_SUPPORT_REUSE_TARGET_MASS", "0.96"))
HIST_BINS = int(os.environ.get("CTML_SUPPORT_REUSE_HIST_BINS", "32"))
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
    rows, n_tokens, d_key = keys.shape
    d_value = values.shape[2]
    if queries.shape != (rows, d_key) or values.shape != (rows, n_tokens, d_value):
        raise ValueError(f"bad Q/K/V shapes q={queries.shape} k={keys.shape} v={values.shape}")
    regime_raw = z["regime"] if "regime" in z.files else np.array(["unknown"] * rows)
    regime_ids = np.array([REGIME_IDS.get(str(r), -1) for r in regime_raw], dtype=np.int32)
    example = np.asarray(z["example"] if "example" in z.files else np.arange(rows), dtype=np.int32)
    head = np.asarray(z["head"] if "head" in z.files else np.zeros(rows), dtype=np.int32)
    layer = np.asarray(z["layer"] if "layer" in z.files else np.zeros(rows), dtype=np.int32)
    trace_batch = np.asarray(z["trace_batch"] if "trace_batch" in z.files else np.zeros(rows), dtype=np.int32)
    # Dense integer IDs, stable across packet order.
    ex_keys = [(int(e), int(tb)) for e, tb in zip(example, trace_batch)]
    ex_map = {k: i for i, k in enumerate(sorted(set(ex_keys)))}
    group_example = np.array([ex_map[k] for k in ex_keys], dtype=np.int32)
    exh_keys = [(int(e), int(tb), int(h)) for e, tb, h in zip(example, trace_batch, head)]
    exh_map = {k: i for i, k in enumerate(sorted(set(exh_keys)))}
    group_example_head = np.array([exh_map[k] for k in exh_keys], dtype=np.int32)

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    with BIN_INPUT.open("wb") as f:
        f.write(b"CTMLTR66")
        f.write(struct.pack("QQQQ", int(rows), int(n_tokens), int(d_key), int(d_value)))
        f.write(np.ascontiguousarray(queries, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(keys, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(values, dtype=np.float64).tobytes(order="C"))
        for arr in [regime_ids, example, head, layer, trace_batch, group_example, group_example_head]:
            f.write(np.ascontiguousarray(arr, dtype=np.int32).tobytes(order="C"))

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
        "example_groups": int(len(ex_map)),
        "example_head_groups": int(len(exh_map)),
        "regime_counts": {str(k): int(v) for k, v in zip(*np.unique(regime_raw.astype(str), return_counts=True))},
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


def build_artifact(prep: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    paths = native.get("all_rows", {})
    acct = native.get("accounting", {})
    speedups = native.get("speedups_vs_dense", {})
    fresh = paths.get("fresh_hist_index", {})
    ex = paths.get("reuse_example_anchor_hist", {})
    exh = paths.get("reuse_example_head_anchor_hist", {})
    uni = paths.get("union_example_hist_upper_bound", {})
    deployable_promoted: list[str] = []
    for name, p, qk_key in [
        ("reuse_example_anchor_hist", ex, "reuse_example_anchor_qk_dot_fraction"),
        ("reuse_example_head_anchor_hist", exh, "reuse_example_head_anchor_qk_dot_fraction"),
    ]:
        if float(p.get("quality_rate", 0.0)) >= 0.99 and float(speedups.get(name, 0.0)) > 1.05 and float(acct.get(qk_key, 1.0)) < 0.95:
            deployable_promoted.append(name)
    interpretation = (
        "anchor support reuse reduces QK work but fails output quality on the local learned trace; "
        "the all-row union support upper bound restores quality only by becoming near dense, so support reuse cannot be promoted without a better row-stability certificate"
    )
    summary = {
        "trace_packet_rows": prep["rows"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "support_reuse_overhead_paid_in_timed_loop": True,
        "support_reuse_does_not_use_values_or_dense_outputs": True,
        "qk_score_computation_measured": True,
        "fresh_hist_quality_rate": fresh.get("quality_rate"),
        "fresh_hist_mean_selected_fraction": fresh.get("mean_selected_fraction"),
        "fresh_hist_speedup_vs_dense": speedups.get("fresh_hist_index"),
        "reuse_example_anchor_quality_rate": ex.get("quality_rate"),
        "reuse_example_anchor_mean_selected_fraction": ex.get("mean_selected_fraction"),
        "reuse_example_anchor_qk_dot_fraction": acct.get("reuse_example_anchor_qk_dot_fraction"),
        "reuse_example_anchor_speedup_vs_dense": speedups.get("reuse_example_anchor_hist"),
        "reuse_example_anchor_jaccard_mean": acct.get("reuse_example_anchor_jaccard_mean"),
        "reuse_example_head_anchor_quality_rate": exh.get("quality_rate"),
        "reuse_example_head_anchor_mean_selected_fraction": exh.get("mean_selected_fraction"),
        "reuse_example_head_anchor_qk_dot_fraction": acct.get("reuse_example_head_anchor_qk_dot_fraction"),
        "reuse_example_head_anchor_speedup_vs_dense": speedups.get("reuse_example_head_anchor_hist"),
        "reuse_example_head_anchor_jaccard_mean": acct.get("reuse_example_head_anchor_jaccard_mean"),
        "union_example_hist_quality_rate": uni.get("quality_rate"),
        "union_example_hist_mean_selected_fraction": uni.get("mean_selected_fraction"),
        "union_example_hist_qk_dot_fraction": acct.get("union_example_hist_qk_dot_fraction"),
        "union_example_hist_speedup_vs_dense": speedups.get("union_example_hist_upper_bound"),
        "union_support_non_promotional_upper_bound": True,
        "deployable_promoted_paths": deployable_promoted,
        "promotion_allowed": False,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "support_reuse_anchor_quality_below_bar",
            "support_union_restores_quality_by_becoming_near_dense",
            "row_stability_certificate_missing",
            "no_deployable_score_path_sparse_win_measured",
        ],
    }
    return {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_SUPPORT_REUSE_AMORTIZATION",
        "generated_at": STAMP,
        "measurement_scope": "Native CPU local tiny-trained Q/K/V trace replay. Support construction/reuse overhead is paid in-loop. Anchor reuse is score-only and does not use V or dense outputs. Union support is an all-row upper-bound negative control. Not public/pretrained, not GPU, not fused-kernel, and not promotion evidence.",
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "promotion_allowed": False,
        "input": prep,
        "native_result": native,
        "summary": summary,
        "interpretation": interpretation,
    }


def write_outputs(artifact: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "run_id": f"{REVUP}_SUPPORT_REUSE_AMORTIZATION",
        "generated_at": STAMP,
        "command": f"python experiments/trace_packet_support_reuse/trace_packet_support_reuse.py",
        "native_command": f"{EXE} {BIN_INPUT} {REPEATS} {TARGET_MASS} {HIST_BINS}",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "parameters": {"repeats": REPEATS, "target_mass": TARGET_MASS, "hist_bins": HIST_BINS},
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "python_source": "experiments/trace_packet_support_reuse/trace_packet_support_reuse.py",
        "python_source_sha256": sha256_file(ROOT / "experiments" / "trace_packet_support_reuse" / "trace_packet_support_reuse.py"),
        "source": "experiments/trace_packet_support_reuse/trace_packet_support_reuse.cpp",
        "source_sha256": sha256_file(CPP),
        "native_input": BIN_INPUT.relative_to(ROOT).as_posix(),
        "native_input_sha256": sha256_file(BIN_INPUT),
        "claim_boundary": "Support reuse amortization is paid in-loop and score-only. Anchor support may skip Q/K dots for non-anchor rows, but quality must pass before any promotion. Union support is a non-promotional all-row upper bound. This is local CPU trace replay, not public/pretrained, not GPU, and not fused-kernel evidence.",
    }
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    prep = prepare_input(find_qk_packet())
    native = run_native()
    artifact = build_artifact(prep, native)
    write_outputs(artifact)
    print(json.dumps({"artifact": OUT.relative_to(ROOT).as_posix(), "summary": artifact["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
