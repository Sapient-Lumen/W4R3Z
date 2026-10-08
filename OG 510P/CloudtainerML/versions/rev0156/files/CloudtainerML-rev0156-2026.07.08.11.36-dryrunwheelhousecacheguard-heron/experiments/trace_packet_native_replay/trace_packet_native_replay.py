#!/usr/bin/env python3
"""rev0061 native replay of the learned trace packet.

rev0060 replayed dispatch rules over a learned trace packet using proxy work
units.  That was enough to close the *schema/replay* gap, but it left a risky
claim boundary: score-storage-allowed sparse rows could look promotable without
any native loop actually consuming the same scores and values.

This probe exports the rev0060 trace packet to a deterministic native binary
format and runs a C++ score-consumption/value-accumulation benchmark.  The scope
is deliberately narrow:

* materialized scores are already present;
* QK score computation is not timed;
* no global-score-storage-free/fused-kernel claim is allowed;
* the packet is local tiny-transformer evidence, not public/pretrained evidence.
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
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0061"}
REV = META.get("revision", "rev0061")
REVUP = REV.upper()
STAMP = "2026-06-18T09:22:00-04:00"
TRACE_PACKET = ROOT / "artifacts" / "trace-bundles" / "REV0060_TINY_TRAINED_TRACE_PACKET.npz"
TRACE_MANIFEST = ROOT / "artifacts" / "trace-bundles" / "REV0060_TINY_TRAINED_TRACE_PACKET_MANIFEST.json"
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_PACKET_NATIVE_REPLAY.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TRACE_PACKET_NATIVE_REPLAY_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_TRACE_PACKET_NATIVE_REPLAY_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_native_replay"
CPP = ROOT / "experiments" / "trace_packet_native_replay" / "trace_packet_native_replay.cpp"
EXE = BUILD_DIR / "trace_packet_native_replay"
REPEATS = int(os.environ.get("CTML_NATIVE_TRACE_REPEATS", "1200"))
TARGET_MASS = 0.95
QUALITY_MIN_RATE = 0.999

REGIME_IDS = {
    "low_support_lt12": 0,
    "mid_support_12_28": 1,
    "high_support_ge28": 2,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs):
    vals = [float(x) for x in xs]
    return float(sum(vals) / len(vals)) if vals else None


def export_native_input() -> dict[str, Any]:
    if not TRACE_PACKET.exists():
        raise FileNotFoundError(f"missing trace packet: {TRACE_PACKET}")
    z = np.load(TRACE_PACKET, allow_pickle=False)
    scores = np.asarray(z["scores"], dtype=np.float64)
    values = np.asarray(z["values"], dtype=np.float64)
    regimes_raw = np.asarray(z["regime"]).astype(str)
    if scores.ndim != 2 or values.ndim != 3:
        raise ValueError("expected scores[rows,n] and values[rows,n,dv]")
    if scores.shape[:2] != values.shape[:2]:
        raise ValueError("scores/values row-token dimensions disagree")
    regime_ids = np.asarray([REGIME_IDS.get(str(r), -1) for r in regimes_raw], dtype=np.int32)
    if np.any(regime_ids < 0):
        raise ValueError("unknown regime label in trace packet")
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    rows, n = scores.shape
    dv = values.shape[2]
    with BIN_INPUT.open("wb") as f:
        f.write(b"CTMLTR61")
        f.write(struct.pack("<QQQ", rows, n, dv))
        f.write(np.ascontiguousarray(scores).tobytes(order="C"))
        f.write(np.ascontiguousarray(values).tobytes(order="C"))
        f.write(np.ascontiguousarray(regime_ids).tobytes(order="C"))
    return {
        "rows": int(rows),
        "n_tokens": int(n),
        "d_value": int(dv),
        "regime_counts": {r: int(np.sum(regimes_raw == r)) for r in sorted(REGIME_IDS)},
        "input_bin": BIN_INPUT.relative_to(ROOT).as_posix(),
        "input_bin_sha256": sha256_file(BIN_INPUT),
        "trace_packet_sha256": sha256_file(TRACE_PACKET),
    }


def compile_native() -> dict[str, Any]:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("c++")
    if not compiler:
        raise RuntimeError("no C++ compiler available")
    cmd = [compiler, "-O3", "-std=c++17", str(CPP), "-o", str(EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return {"compiler": compiler, "compile_command": " ".join(cmd), "native_exe": EXE.relative_to(ROOT).as_posix(), "cpp_sha256": sha256_file(CPP)}


def run_native() -> dict[str, Any]:
    cmd = [str(EXE), str(BIN_INPUT), str(REPEATS)]
    proc = subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"native benchmark did not emit JSON: {proc.stdout[:2000]} {proc.stderr[:2000]}") from e


def load_prev_proxy() -> dict[str, Any]:
    p = ROOT / "artifacts" / "probe-results" / "REV0060_TRACE_PACKET_DISPATCH_REPLAY.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    exported = export_native_input()
    compiled = compile_native()
    native = run_native()
    previous = load_prev_proxy()
    prev_summary = previous.get("summary", {}) if previous else {}
    native_speedup = float(native["timing"]["mass_histogram_speedup_vs_dense_score_consumption"])
    quality_rate = float(native["all_rows"]["quality_rate"])
    selected_fraction = float(native["all_rows"]["mean_selected_fraction"])
    prev_proxy_speedup = prev_summary.get("score_storage_allowed_aggregate_speedup_vs_dense_cost_proxy")
    speedup_delta_vs_proxy = None
    if prev_proxy_speedup is not None:
        speedup_delta_vs_proxy = float(native_speedup - float(prev_proxy_speedup))
    materialized_path_native_measured = True
    fused_or_qk_blocker_closed = False
    promotion_allowed = False
    summary = {
        "trace_packet_rows": int(exported["rows"]),
        "native_replay_rows": int(native["rows"]),
        "native_mass_histogram_speedup_vs_dense_score_consumption": native_speedup,
        "native_mass_histogram_quality_rate": quality_rate,
        "native_mass_histogram_mean_selected_fraction": selected_fraction,
        "rev0060_proxy_speedup_vs_dense_cost_proxy": prev_proxy_speedup,
        "native_minus_proxy_speedup": speedup_delta_vs_proxy,
        "materialized_path_native_measured": materialized_path_native_measured,
        "score_storage_required": True,
        "qk_score_computation_measured": False,
        "gpu_fused_kernel_measured": False,
        "public_pretrained_trace_loaded": False,
        "strict_materialization_free_sparse_promoted": False,
        "fused_or_qk_blocker_closed": fused_or_qk_blocker_closed,
        "promotion_allowed": promotion_allowed,
        "native_quality_bar_passed": quality_rate >= QUALITY_MIN_RATE,
        "native_score_consumption_speed_bar_passed": native_speedup > 1.0,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "qk_score_computation_not_measured_for_trace_packet",
            "gpu_fused_attention_kernel_timing_missing",
            "strict_materialization_free_sparse_schedule_has_no_learned_trace_speed_win",
            "materialized_sparse_cpu_path_requires_global_score_storage",
        ],
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_TRACE_PACKET_NATIVE_REPLAY",
        "generated_at": STAMP,
        "status": "native_score_consumption_measured_promotion_blocked",
        "promotion_allowed": promotion_allowed,
        "measurement_scope": "native C++ CPU materialized-score replay over a local tiny-trained trace packet; not QK computation, not GPU, not fused kernel, not public/pretrained evidence",
        "public_pretrained_trace_loaded": False,
        "gpu_kernel_claim": False,
        "gpu_fused_kernel_measured": False,
        "qk_score_computation_measured": False,
        "score_storage_required": True,
        "score_materialization_assumed_available": True,
        "target_mass": TARGET_MASS,
        "quality_bar": {"mass_min": 0.95, "cosine_min": 0.995, "rel_l2_max": 0.18, "quality_rate_min": QUALITY_MIN_RATE},
        "input": exported,
        "native_build": compiled,
        "native_result": native,
        "previous_proxy_dispatch_replay": {
            "artifact": "REV0060_TRACE_PACKET_DISPATCH_REPLAY.json" if previous else None,
            "score_storage_allowed_sparse_row_rate": prev_summary.get("score_storage_allowed_sparse_row_rate"),
            "score_storage_allowed_aggregate_speedup_vs_dense_cost_proxy": prev_proxy_speedup,
            "strict_materialization_free_sparse_row_count": prev_summary.get("strict_materialization_free_sparse_row_count"),
        },
        "summary": summary,
        "interpretation": (
            "The learned trace packet now has native CPU evidence for the materialized-score mass-histogram path. "
            "This can validate or veto proxy dispatch arithmetic, but it cannot close the QK-score, public/pretrained, or fused-kernel blockers because scores are pre-materialized inputs."
        ),
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    run_manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "source": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(Path(__file__).resolve()),
        "native_source": CPP.relative_to(ROOT).as_posix(),
        "native_source_sha256": sha256_file(CPP),
        "trace_packet": TRACE_PACKET.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(TRACE_PACKET),
        "input_bin": BIN_INPUT.relative_to(ROOT).as_posix(),
        "input_bin_sha256": sha256_file(BIN_INPUT),
        "command": "python experiments/trace_packet_native_replay/trace_packet_native_replay.py",
        "native_command": f"{EXE.relative_to(ROOT).as_posix()} {BIN_INPUT.relative_to(ROOT).as_posix()} {REPEATS}",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "generated_at": STAMP,
    }
    RUN_MANIFEST.write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "native_speedup": native_speedup, "quality_rate": quality_rate, "promotion_allowed": promotion_allowed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
