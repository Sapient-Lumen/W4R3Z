#!/usr/bin/env python3
"""rev0063 sparse speed envelope over the local learned Q/K/V trace packet.

rev0062 measured native dense QK attention versus an executable materialized
histogram selector.  This probe asks a sharper engineering question before
spending more effort on selector cleverness:

    If exact Top-p support were supplied for free as an oracle mask, would sparse
    value accumulation have enough native CPU headroom to beat dense once QK
    score construction is still included?

The oracle mask is a deliberately non-promotional upper bound.  It uses the full
QK score row to choose exact Top-p 0.96 support outside the timed selector.  The
point is not to propose an algorithm; the point is to locate whether the next
bottleneck is selector overhead, QK score construction, or value accumulation.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8")) if (ROOT / "CUBE-META.json").exists() else {"revision": "rev0063"}
REV = META.get("revision", "rev0063")
REVUP = REV.upper()
STAMP = "2026-06-18T10:47:00-04:00"

OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_PACKET_SPEED_ENVELOPE.json"
RUN_MANIFEST = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TRACE_PACKET_SPEED_ENVELOPE_RUN_MANIFEST.json"
BIN_DIR = ROOT / "artifacts" / "native-inputs"
BIN_INPUT = BIN_DIR / f"{REVUP}_TRACE_PACKET_SPEED_ENVELOPE_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "trace_packet_speed_envelope"
CPP = ROOT / "experiments" / "trace_packet_speed_envelope" / "trace_packet_speed_envelope.cpp"
EXE = BUILD_DIR / "trace_packet_speed_envelope"
REPEATS = int(os.environ.get("CTML_SPEED_ENVELOPE_REPEATS", "3000"))
TARGET_MASS = 0.96
QUALITY_MIN_RATE = 0.99
REGIME_IDS = {"low_support_lt12": 0, "mid_support_12_28": 1, "high_support_ge28": 2}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmean(xs: Iterable[float]) -> float | None:
    vals = [float(x) for x in xs]
    return float(statistics.fmean(vals)) if vals else None


def pctl(xs: Iterable[float], q: float) -> float | None:
    vals = sorted(float(x) for x in xs)
    if not vals:
        return None
    return float(vals[int(q * (len(vals) - 1))])


def find_qk_packet() -> Path:
    candidates = sorted((ROOT / "artifacts" / "trace-bundles").glob("REV*_TINY_TRAINED_QK_TRACE_PACKET.npz"), reverse=True)
    for p in candidates:
        if p.name.startswith("REV0062") or p.name.startswith(REVUP):
            return p
    if candidates:
        return candidates[0]
    raise FileNotFoundError("no Q/K/V trace packet found")


def stable_softmax(scores: np.ndarray) -> np.ndarray:
    x = scores.astype(np.float64)
    x = x - np.max(x)
    w = np.exp(np.clip(x, -80.0, 0.0))
    return w / np.sum(w)


def exact_topp_mask(probs: np.ndarray, target: float = TARGET_MASS) -> np.ndarray:
    order = np.argsort(-probs)
    mask = np.zeros_like(probs, dtype=np.uint8)
    total = 0.0
    for idx in order:
        mask[int(idx)] = 1
        total += float(probs[int(idx)])
        if total >= target:
            break
    return mask


def prepare_input(packet_path: Path) -> dict[str, Any]:
    z = np.load(packet_path)
    queries = np.asarray(z["queries"], dtype=np.float64)
    keys = np.asarray(z["keys"], dtype=np.float64)
    values = np.asarray(z["values"], dtype=np.float64)
    scores_packet = np.asarray(z["scores"], dtype=np.float64) if "scores" in z.files else None
    regimes_raw = z["regime"] if "regime" in z.files else np.array(["unknown"] * queries.shape[0])
    rows, n, dk = keys.shape
    dv = values.shape[2]
    if queries.shape != (rows, dk) or values.shape[:2] != (rows, n):
        raise ValueError(f"bad packet shapes queries={queries.shape} keys={keys.shape} values={values.shape}")
    probs = np.zeros((rows, n), dtype=np.float64)
    masks = np.zeros((rows, n), dtype=np.uint8)
    selected_counts: list[int] = []
    masses: list[float] = []
    max_diff = 0.0
    eff_supports: list[float] = []
    for r in range(rows):
        scores = keys[r] @ queries[r] / math.sqrt(float(dk))
        if scores_packet is not None:
            max_diff = max(max_diff, float(np.max(np.abs(scores - scores_packet[r]))))
        pr = stable_softmax(scores)
        probs[r] = pr
        masks[r] = exact_topp_mask(pr, TARGET_MASS)
        selected_counts.append(int(np.sum(masks[r])))
        masses.append(float(np.sum(pr[masks[r].astype(bool)])))
        eff_supports.append(float(math.exp(-float(np.sum(pr * np.log(np.maximum(pr, 1e-30)))))))
    regime_ids = np.array([REGIME_IDS.get(str(r), -1) for r in regimes_raw], dtype=np.int32)
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    with BIN_INPUT.open("wb") as f:
        f.write(b"CTMLTR63")
        f.write(struct.pack("QQQQ", int(rows), int(n), int(dk), int(dv)))
        f.write(np.ascontiguousarray(queries, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(keys, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(values, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(probs, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(masks, dtype=np.uint8).tobytes(order="C"))
        f.write(np.ascontiguousarray(regime_ids, dtype=np.int32).tobytes(order="C"))
    packet_manifest_path = packet_path.with_name(packet_path.stem + "_MANIFEST.json")
    packet_manifest = json.loads(packet_manifest_path.read_text(encoding="utf-8")) if packet_manifest_path.exists() else {}
    return {
        "trace_packet": packet_path.relative_to(ROOT).as_posix(),
        "trace_packet_sha256": sha256_file(packet_path),
        "trace_packet_manifest": packet_manifest,
        "rows": int(rows),
        "n_tokens": int(n),
        "d_key": int(dk),
        "d_value": int(dv),
        "input_bin": BIN_INPUT.relative_to(ROOT).as_posix(),
        "input_bin_sha256": sha256_file(BIN_INPUT),
        "oracle_topp96_mask": {
            "target_mass": TARGET_MASS,
            "mask_is_oracle_upper_bound": True,
            "mask_is_promotional": False,
            "mean_selected_count": fmean(selected_counts),
            "mean_selected_fraction": fmean(c / n for c in selected_counts),
            "p90_selected_count": pctl(selected_counts, 0.90),
            "mean_exact_mass": fmean(masses),
            "min_exact_mass": float(min(masses)) if masses else None,
        },
        "trace_summary": {
            "mean_effective_support": fmean(eff_supports),
            "p90_effective_support": pctl(eff_supports, 0.90),
            "regime_counts": {str(k): int(v) for k, v in zip(*np.unique(regimes_raw.astype(str), return_counts=True))},
            "max_qk_score_packet_abs_diff": max_diff,
        },
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
    proc = subprocess.run([str(EXE), str(BIN_INPUT), str(REPEATS)], cwd=ROOT, check=True, text=True, capture_output=True)
    return json.loads(proc.stdout)


def build_artifact(prep: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    timing = native.get("timing", {})
    all_rows = native.get("all_rows", {})
    qk_speedup = float(timing.get("oracle_topp96_qk_included_speedup_vs_dense", 0.0))
    value_speedup = float(timing.get("oracle_topp96_value_only_speedup_vs_dense_value_only", 0.0))
    summary = {
        "trace_packet_rows": prep["rows"],
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "qk_score_computation_measured": True,
        "oracle_selector_upper_bound_measured": True,
        "oracle_topp96_mask_is_promotional": False,
        "oracle_topp96_mean_selected_fraction": prep["oracle_topp96_mask"]["mean_selected_fraction"],
        "oracle_topp96_quality_rate": all_rows.get("quality_rate"),
        "oracle_topp96_mean_rel_l2": all_rows.get("mean_rel_l2"),
        "oracle_topp96_mean_cosine": all_rows.get("mean_cosine"),
        "oracle_topp96_qk_included_speedup_vs_dense": qk_speedup,
        "oracle_topp96_value_only_speedup_vs_dense_value_only": value_speedup,
        "qk_scores_only_fraction_of_dense_online_time": timing.get("qk_scores_only_fraction_of_dense_online_time"),
        "speed_envelope_interpretation": (
            "strong negative envelope: even the oracle/free-selector Top-p path is slower than dense with QK included, and sparse value-only accumulation is also slower on this CPU trace"
            if qk_speedup < 1.0 and value_speedup <= 1.0 else
            "sparse value reads have a value-only win, but the qk-included free-selector upper bound does not clear dense on this CPU trace"
            if qk_speedup < 1.0 and value_speedup > 1.0 else
            "free-selector upper bound clears dense; selector/schedule overhead becomes the next bottleneck, not promotion evidence"
            if qk_speedup >= 1.0 else
            "speed envelope is inconclusive"
        ),
        "promotion_allowed": False,
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing",
            "gpu_fused_attention_kernel_timing_missing",
            "oracle_topp96_mask_is_not_deployable_selector",
            "materialized_sparse_paths_still_compute_all_qk_scores",
            "strict_materialization_free_sparse_schedule_has_no_measured_speed_win",
        ],
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "generated_at": STAMP,
        "experiment": "trace_packet_speed_envelope",
        "measurement_scope": "native CPU speed envelope over local tiny-trained Q/K/V traces; QK score computation is measured; exact Top-p mask is an oracle upper bound; not public/pretrained; not GPU; not fused; not deployable sparse selector evidence",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "trace_packet": prep["trace_packet"],
        "trace_packet_sha256": prep["trace_packet_sha256"],
        "trace_packet_manifest": prep["trace_packet_manifest"],
        "native_input": {"path": prep["input_bin"], "sha256": prep["input_bin_sha256"]},
        "oracle_topp96_mask": prep["oracle_topp96_mask"],
        "trace_summary": prep["trace_summary"],
        "native_result": native,
        "summary": summary,
        "risk_closed": "local learned-trace sparse speedups now have an oracle/free-selector upper bound with QK included; this prevents chasing selector refinements when QK/value math leaves no measured headroom",
        "next_best_substantive_work": [
            "run the same envelope over a public/pretrained trace packet once captured",
            "repeat on GPU/fused kernels where QK/value memory economics differ",
            "only then revisit deployable selector optimization if the envelope shows headroom",
        ],
    }
    return artifact


def write_run_manifest(artifact: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "generated_at": STAMP,
        "run_kind": "trace_packet_speed_envelope_native_cpu",
        "command": "python experiments/trace_packet_speed_envelope/trace_packet_speed_envelope.py",
        "source": CPP.relative_to(ROOT).as_posix(),
        "source_sha256": sha256_file(CPP),
        "python_source": Path(__file__).relative_to(ROOT).as_posix(),
        "python_source_sha256": sha256_file(Path(__file__)),
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "native_input": BIN_INPUT.relative_to(ROOT).as_posix(),
        "native_input_sha256": sha256_file(BIN_INPUT),
        "trace_packet": artifact["trace_packet"],
        "trace_packet_sha256": artifact["trace_packet_sha256"],
        "platform": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "numpy": np.__version__,
        },
        "repeats": REPEATS,
        "claim_boundary": "oracle exact-Top-p support is used only to bound native speed headroom; it is not a deployable selector and cannot promote the mechanism",
    }
    RUN_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    # Update artifact with run-manifest hash after manifest is written.
    artifact["run_manifest"] = RUN_MANIFEST.relative_to(ROOT).as_posix()
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    manifest["artifact_sha256"] = sha256_file(OUT)
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    packet = find_qk_packet()
    prep = prepare_input(packet)
    native = run_native()
    artifact = build_artifact(prep, native)
    write_run_manifest(artifact)
    print(json.dumps({
        "status": "ok",
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "oracle_qk_speedup": artifact["summary"]["oracle_topp96_qk_included_speedup_vs_dense"],
        "value_only_speedup": artifact["summary"]["oracle_topp96_value_only_speedup_vs_dense_value_only"],
        "quality_rate": artifact["summary"]["oracle_topp96_quality_rate"],
        "selected_fraction": artifact["summary"]["oracle_topp96_mean_selected_fraction"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
