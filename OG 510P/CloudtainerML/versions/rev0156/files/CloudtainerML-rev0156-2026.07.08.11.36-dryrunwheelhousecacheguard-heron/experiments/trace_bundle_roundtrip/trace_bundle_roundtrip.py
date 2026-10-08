#!/usr/bin/env python3
"""rev0049 NPZ attention-trace bundle roundtrip.

The public trace gate introduced in rev0048 was useful but dangerous in one
specific way: any external NPZ load was surfaced as `public_pretrained` in row
metadata.  rev0049 turns that into an executable claims test.

This probe builds two deterministic external trace bundles:
  1. scores + values schema;
  2. q + k + v schema.

It then imports each bundle through the public trace gate with
`public_pretrained_trace=False`.  A passing run proves the importer is exercised
on actual NPZ files and that arbitrary external bundles are not promoted to
public/pretrained evidence by metadata accident.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "public_trace_gate_surrogate"))
import public_trace_gate_surrogate as gate  # noqa: E402

REV = "rev0049"
REVUP = REV.upper()
GENERATED_AT = "2026-06-18T01:37:00-04:00"
SEED = 49049
N = 96
D = 32
DV = 24
ROWS_PER_REGIME = 10
REGIMES = ("retrieval_peaked", "broad_high_entropy", "value_tail_outlier")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unit(rng: np.random.Generator, d: int) -> np.ndarray:
    x = rng.normal(size=d)
    return x / max(1e-12, float(np.linalg.norm(x)))


def make_scores(rng: np.random.Generator, regime: str) -> np.ndarray:
    if regime == "retrieval_peaked":
        scores = rng.normal(-2.5, 0.22, size=N)
        c = int(rng.integers(0, N))
        scores[c] = rng.uniform(5.8, 7.2)
        near = rng.choice([i for i in range(N) if i != c], size=5, replace=False)
        scores[near] += rng.uniform(1.8, 3.0, size=len(near))
        return scores.astype(np.float64)
    if regime == "broad_high_entropy":
        return rng.normal(0.0, 0.09, size=N).astype(np.float64)
    if regime == "value_tail_outlier":
        scores = rng.normal(-8.0, 0.12, size=N)
        c = int(rng.integers(0, N))
        scores[c] = rng.uniform(0.0, 0.25)
        near = rng.choice([i for i in range(N) if i != c], size=6, replace=False)
        scores[near] = rng.normal(-2.1, 0.15, size=len(near))
        tail = rng.choice([i for i in range(N) if i != c and i not in set(near)], size=4, replace=False)
        scores[tail] = rng.uniform(-4.9, -4.45, size=len(tail))
        return scores.astype(np.float64)
    raise ValueError(regime)


def stable_softmax(scores: np.ndarray) -> np.ndarray:
    y = scores - float(np.max(scores))
    e = np.exp(np.clip(y, -80.0, 80.0))
    return e / float(e.sum())


def make_values(rng: np.random.Generator, scores: np.ndarray, regime: str) -> np.ndarray:
    values = rng.normal(0.0, 0.28, size=(N, DV)).astype(np.float64)
    probs = stable_softmax(scores)
    top = np.argsort(-probs)[:8]
    values[top] += unit(rng, DV) * rng.uniform(0.8, 1.5)
    if regime == "value_tail_outlier":
        low_risk = np.argsort(probs * np.linalg.norm(values, axis=-1))[:4]
        direction = unit(rng, DV)
        for j, idx in enumerate(low_risk):
            values[idx] = direction * (70.0 + 7.0 * j)
            scores[idx] = max(scores) - rng.uniform(4.45, 4.9)
    return values.astype(np.float64)


def make_rows() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    scores_rows: list[np.ndarray] = []
    values_rows: list[np.ndarray] = []
    regimes: list[str] = []
    layers: list[int] = []
    heads: list[int] = []
    positions: list[int] = []
    for layer in range(2):
        for head in range(2):
            for regime in REGIMES:
                for _ in range(ROWS_PER_REGIME // 2):
                    scores = make_scores(rng, regime)
                    values = make_values(rng, scores, regime)
                    scores_rows.append(scores)
                    values_rows.append(values)
                    regimes.append(regime)
                    layers.append(layer)
                    heads.append(head)
                    positions.append(N - 1)
    scores = np.stack(scores_rows).astype(np.float64)
    values = np.stack(values_rows).astype(np.float64)
    norms = np.linalg.norm(values, axis=-1).astype(np.float64)
    return (
        scores,
        values,
        norms,
        np.asarray(regimes),
        np.asarray(layers, dtype=np.int64),
        np.asarray(heads, dtype=np.int64),
        np.asarray(positions, dtype=np.int64),
    )


def write_scores_values_bundle(path: Path) -> dict:
    scores, values, norms, regimes, layers, heads, positions = make_rows()
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        scores=scores,
        values=values,
        value_norms=norms,
        regime=regimes,
        layer=layers,
        head=heads,
        position=positions,
    )
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "rows": int(scores.shape[0]), "n": int(scores.shape[1]), "dv": int(values.shape[-1])}


def write_qkv_bundle(path: Path) -> dict:
    scores, values, _norms, regimes, layers, heads, positions = make_rows()
    row_count = scores.shape[0]
    q = np.zeros((row_count, D), dtype=np.float64)
    q[:, 0] = 1.0
    k = np.zeros((row_count, N, D), dtype=np.float64)
    k[:, :, 0] = scores * math.sqrt(D)
    # Add tiny non-score dimensions so the file exercises multidimensional k.
    rng = np.random.default_rng(SEED + 7)
    k[:, :, 1:] = rng.normal(0.0, 1e-4, size=(row_count, N, D - 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        q=q,
        k=k,
        v=values,
        regime=regimes,
        layer=layers,
        head=heads,
        position=positions,
    )
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "rows": int(row_count), "n": int(N), "d": int(D), "dv": int(DV)}


def write_gate_payload(bundle_path: Path, out_path: Path, label: str) -> dict:
    payload = gate.run(
        bundle_path,
        public_pretrained_trace=False,
        trace_source_label=label,
        bundle_model_id="synthetic_roundtrip_fixture_not_a_model",
        bundle_license="internal synthetic fixture",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    man = ROOT / "artifacts" / "run-manifests" / (out_path.stem + "_RUN_MANIFEST.json")
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_text(json.dumps(payload["run_provenance"], indent=2) + "\n", encoding="utf-8")
    return {
        "path": out_path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(out_path),
        "trace_gate_status": payload.get("trace_gate_status"),
        "external_trace_loaded": payload.get("external_trace_loaded"),
        "public_pretrained_trace_loaded": payload.get("public_pretrained_trace_loaded"),
        "row_public_pretrained_true_count": sum(1 for r in payload.get("rows", []) if r.get("public_pretrained_trace_loaded")),
        "trace_rows": payload.get("summary", {}).get("trace_row_count"),
        "result_rows": payload.get("summary", {}).get("result_row_count"),
        "trace_source_types": payload.get("summary", {}).get("trace_source_types"),
        "risk_surface": payload.get("summary", {}).get("risk_surface"),
    }


def main() -> int:
    bundle_dir = ROOT / "artifacts" / "trace-bundles"
    scores_values_path = bundle_dir / f"{REVUP}_ROUNDTRIP_SCORES_VALUES_TRACE.npz"
    qkv_path = bundle_dir / f"{REVUP}_ROUNDTRIP_QKV_TRACE.npz"
    sv_info = write_scores_values_bundle(scores_values_path)
    qkv_info = write_qkv_bundle(qkv_path)

    gate_dir = ROOT / "artifacts" / "probe-results"
    sv_gate = write_gate_payload(scores_values_path, gate_dir / f"{REVUP}_EXTERNAL_TRACE_ROUNDTRIP_SCORES_VALUES_GATE.json", "roundtrip_scores_values_fixture")
    qkv_gate = write_gate_payload(qkv_path, gate_dir / f"{REVUP}_EXTERNAL_TRACE_ROUNDTRIP_QKV_GATE.json", "roundtrip_qkv_fixture")

    gates = [sv_gate, qkv_gate]
    claims_ok = all(
        g["external_trace_loaded"] is True
        and g["public_pretrained_trace_loaded"] is False
        and g["row_public_pretrained_true_count"] == 0
        and g["trace_gate_status"] == "external_npz_loaded_claims_public_pretrained_false"
        for g in gates
    )
    payload = {
        "project": "CloudtainerML",
        "revision": REV,
        "probe": "trace_bundle_roundtrip",
        "kind": "external_npz_schema_roundtrip_and_claims_guard",
        "generated_at": GENERATED_AT,
        "promotion_allowed": False,
        "primary_metric": {"name": "external_npz_roundtrip_passes_without_public_pretrained_claim", "value": bool(claims_ok)},
        "bundle_artifacts": {"scores_values": sv_info, "qkv": qkv_info},
        "gate_outputs": {"scores_values": sv_gate, "qkv": qkv_gate},
        "claims_invariant": {
            "arbitrary_external_npz_is_not_public_pretrained": bool(claims_ok),
            "reason": "external_trace_loaded is separate from public_pretrained_trace_loaded after rev0049",
        },
        "remaining_blockers": [
            "actual public/pretrained trace bundle still missing",
            "this roundtrip fixture is synthetic and only validates importer semantics",
            "GPU/fused-kernel timing still missing",
        ],
        "run_provenance": {
            "source_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "source_sha256": sha256_file(Path(__file__).resolve()),
            "public_gate_source_sha256": sha256_file(ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"),
            "command": "python experiments/trace_bundle_roundtrip/trace_bundle_roundtrip.py",
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "seed": SEED,
        },
    }
    out = ROOT / "artifacts" / "probe-results" / f"{REVUP}_TRACE_BUNDLE_ROUNDTRIP.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    man = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_TRACE_BUNDLE_ROUNDTRIP_RUN_MANIFEST.json"
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_text(json.dumps(payload["run_provenance"], indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "pass" if claims_ok else "fail",
        "scores_values_gate_status": sv_gate["trace_gate_status"],
        "qkv_gate_status": qkv_gate["trace_gate_status"],
        "claims_ok": claims_ok,
        "outputs": [out.relative_to(ROOT).as_posix(), sv_gate["path"], qkv_gate["path"]],
    }, indent=2))
    return 0 if claims_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
