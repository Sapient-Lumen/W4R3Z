#!/usr/bin/env python3
"""Executable post-transform trace contract harness for CloudtainerML rev0077.

This is not public-model evidence. It is a deterministic adapter wind-tunnel that
turns the riskiest missing semantic boundary into runnable code:

* create raw projection Q/K/V states for a Llama-like decoder attention path;
* apply a RoPE-like post-projection transform to Q/K before scores are formed;
* record fixed-width causal/padding score bias, explicit attention scale, and
  dense reference output;
* prove the post-transform bundle replays exactly while the raw-projection
  bundle cannot reproduce the same model reference;
* pass the bundle through the existing public-trace gate as non-public evidence;
* prove a forged public claim is rejected because the origin is synthetic.

The output is a contract fixture and a reusable failure mode, not a model result.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0077")
REVUP = REV.upper()
STAMP = META.get("generated_at") or META.get("created_at") or "unknown"
OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT.json"
MAN = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT_RUN_MANIFEST.json"
BUNDLE_DIR = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_POST_TRANSFORM_CONTRACT"
GATE_SCRIPT = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
THIS = Path(__file__).resolve()

TRACE_CLAIM_VERSION = "public_trace_claim_v3"
QKV_SCHEMA = "qkv_npz_v2"
SCORE_TRANSFORM = "scaled_dot_product_plus_bias"
SCORE_STAGE_POST = "post_model_qk_transforms"
SCORE_STAGE_RAW = "raw_projection_pre_attention_transforms"
PUBLIC_DENSE_TOL = 1e-5
NEGATIVE_MASK_BIAS = -1.0e9


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scalar(value: Any) -> np.ndarray:
    return np.asarray([value])


def stable_softmax(scores: np.ndarray) -> np.ndarray:
    s = scores - np.max(scores, axis=1, keepdims=True)
    p = np.exp(s)
    p /= np.sum(p, axis=1, keepdims=True)
    return p


def dense_attention(q: np.ndarray, k: np.ndarray, v: np.ndarray, scale: np.ndarray, bias: np.ndarray) -> np.ndarray:
    scale_vec = np.asarray(scale, dtype=np.float64).reshape(-1)
    if scale_vec.size == 1:
        scale_vec = np.repeat(scale_vec, q.shape[0])
    scores = np.einsum("rd,rnd->rn", q, k) * scale_vec[:, None] + bias
    return np.einsum("rn,rnd->rd", stable_softmax(scores), v)


def rotate_half(x: np.ndarray) -> np.ndarray:
    if x.shape[-1] % 2 != 0:
        raise ValueError("RoPE contract fixture requires even head dimension")
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    out = np.empty_like(x)
    out[..., 0::2] = -x_odd
    out[..., 1::2] = x_even
    return out


def rope_angles(max_position: int, d_head: int, *, base: float = 10000.0) -> tuple[np.ndarray, np.ndarray]:
    half = d_head // 2
    inv_freq = 1.0 / (base ** (np.arange(half, dtype=np.float64) / max(1, half)))
    positions = np.arange(max_position, dtype=np.float64)[:, None]
    freqs = positions * inv_freq[None, :]
    cos_half = np.cos(freqs)
    sin_half = np.sin(freqs)
    cos = np.empty((max_position, d_head), dtype=np.float64)
    sin = np.empty((max_position, d_head), dtype=np.float64)
    cos[:, 0::2] = cos_half
    cos[:, 1::2] = cos_half
    sin[:, 0::2] = sin_half
    sin[:, 1::2] = sin_half
    return cos, sin


def apply_rope(x: np.ndarray, positions: np.ndarray, cos: np.ndarray, sin: np.ndarray) -> np.ndarray:
    # x [..., d], positions matching leading shape without d.
    c = cos[positions]
    s = sin[positions]
    return x * c + rotate_half(x) * s


def unit_row_norm(x: np.ndarray) -> np.ndarray:
    return x / np.maximum(1e-9, np.linalg.norm(x, axis=-1, keepdims=True))


def make_rows(seed: int = 77077) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    prompt_lengths = [8, 13, 21]
    positions_by_prompt = {
        0: [0, 3, 7],
        1: [2, 8, 12],
        2: [4, 10, 20],
    }
    layers = [0, 1, 3]
    heads = [0, 2]
    max_len = max(prompt_lengths)
    d_model = 48
    n_heads = 4
    d_head = 16
    d_value = 16
    if d_model != n_heads * d_head // (d_head // 16):
        # Kept explicit so edits do not silently change the fixture geometry.
        d_model = 48
    cos, sin = rope_angles(max_len, d_head)

    # Layer/head specific projections. Value dimension intentionally equals d_head
    # in this fixture so the dense reference shape is simple, while the contract
    # still records d_value separately through V.
    Wq = rng.normal(0, 0.16, size=(len(layers), len(heads), d_model, d_head))
    Wk = rng.normal(0, 0.16, size=(len(layers), len(heads), d_model, d_head))
    Wv = rng.normal(0, 0.12, size=(len(layers), len(heads), d_model, d_value))

    q_raw_rows: list[np.ndarray] = []
    k_raw_rows: list[np.ndarray] = []
    q_post_rows: list[np.ndarray] = []
    k_post_rows: list[np.ndarray] = []
    v_rows: list[np.ndarray] = []
    bias_rows: list[np.ndarray] = []
    layer_rows: list[int] = []
    head_rows: list[int] = []
    position_rows: list[int] = []
    prompt_rows: list[int] = []
    active_rows: list[int] = []
    regime_rows: list[str] = []

    prompt_states: list[np.ndarray] = []
    for prompt_id, length in enumerate(prompt_lengths):
        # Deterministic prompt-specific hidden states with weak local correlation.
        base = rng.normal(0, 1.0, size=(length, d_model))
        ramp = np.linspace(-0.5, 0.5, length)[:, None]
        state = base + 0.15 * np.roll(base, shift=1, axis=0) + ramp * rng.normal(0, 0.5, size=(1, d_model))
        prompt_states.append(unit_row_norm(state))

    for p_id, states in enumerate(prompt_states):
        length = states.shape[0]
        token_positions = np.arange(max_len)
        padded = np.zeros((max_len, d_model), dtype=np.float64)
        padded[:length] = states
        for li, layer in enumerate(layers):
            # Lightweight layer variation, not a model claim.
            layer_states = unit_row_norm(padded + 0.04 * (li + 1) * np.tanh(padded))
            for hi, head in enumerate(heads):
                q_all = layer_states @ Wq[li, hi]
                k_all = layer_states @ Wk[li, hi]
                v_all = layer_states @ Wv[li, hi]
                q_all = q_all + 0.02 * (head + 1)
                k_all = k_all - 0.015 * (layer + 1)
                q_post_all = apply_rope(q_all, token_positions, cos, sin)
                k_post_all = apply_rope(k_all, token_positions, cos, sin)
                for pos in positions_by_prompt[p_id]:
                    q_raw_rows.append(q_all[pos].astype(np.float64))
                    k_raw_rows.append(k_all.astype(np.float64))
                    q_post_rows.append(q_post_all[pos].astype(np.float64))
                    k_post_rows.append(k_post_all.astype(np.float64))
                    v_rows.append(v_all.astype(np.float64))
                    bias = np.full(max_len, NEGATIVE_MASK_BIAS, dtype=np.float64)
                    # Active prefix: real prompt tokens up through the causal position.
                    bias[: pos + 1] = 0.0
                    # Add a tiny finite ALiBi-like preference so this tests bias, not
                    # just masking. It remains tiny versus NEGATIVE_MASK_BIAS.
                    bias[: pos + 1] += np.linspace(0.02, -0.02, pos + 1, dtype=np.float64)
                    bias_rows.append(bias)
                    layer_rows.append(layer)
                    head_rows.append(head)
                    position_rows.append(pos)
                    prompt_rows.append(p_id)
                    active_rows.append(pos + 1)
                    regime_rows.append(f"rope_causal_prompt{p_id}_len{length}")

    q_raw = np.stack(q_raw_rows)
    k_raw = np.stack(k_raw_rows)
    q_post = np.stack(q_post_rows)
    k_post = np.stack(k_post_rows)
    v = np.stack(v_rows)
    score_bias = np.stack(bias_rows)
    scale = np.asarray([1.0 / math.sqrt(q_post.shape[-1])], dtype=np.float64)
    dense_post = dense_attention(q_post, k_post, v, scale, score_bias)
    dense_raw_against_post_reference = dense_attention(q_raw, k_raw, v, scale, score_bias)
    raw_reference_error = np.max(np.abs(dense_raw_against_post_reference - dense_post), axis=1)
    return {
        "q_raw": q_raw,
        "k_raw": k_raw,
        "q_post": q_post,
        "k_post": k_post,
        "v": v,
        "score_bias": score_bias,
        "attention_scale": scale,
        "dense_post": dense_post,
        "raw_reference_error": raw_reference_error,
        "layer": np.asarray(layer_rows, dtype=np.int64),
        "head": np.asarray(head_rows, dtype=np.int64),
        "position": np.asarray(position_rows, dtype=np.int64),
        "prompt_id": np.asarray(prompt_rows, dtype=np.int64),
        "active_tokens": np.asarray(active_rows, dtype=np.int64),
        "regime": np.asarray(regime_rows),
    }


def base_metadata(*, public: bool, source_type: str, stage: str, verified: bool, dense_error: float) -> dict[str, np.ndarray]:
    synthetic_config = {
        "architecture": "deterministic_rope_decoder_attention_contract_fixture",
        "claim": "post-transform Q/K adapter replay semantics only; not public/pretrained evidence",
        "revision": REV,
    }
    config_sha = hashlib.sha256(json.dumps(synthetic_config, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "trace_claim_version": scalar(TRACE_CLAIM_VERSION),
        "public_pretrained_trace": scalar(bool(public)),
        "source_type": scalar(source_type),
        "model_id": scalar("synthetic_rope_contract_fixture_not_public"),
        "model_revision": scalar("sha256:" + "7" * 64),
        "tokenizer_revision": scalar("sha256:" + "8" * 64),
        "code_revision": scalar("not_applicable"),
        "trust_remote_code": scalar(False),
        "weights_source": scalar("deterministic seeded synthetic adapter harness; no pretrained weights"),
        "license": scalar("synthetic fixture generated inside capsule; no model license"),
        "schema": scalar(QKV_SCHEMA),
        "capture_tool": scalar("experiments/post_transform_trace_contract/post_transform_trace_contract.py"),
        "capture_tool_sha256": scalar(sha256_file(THIS)),
        "config_sha256": scalar(config_sha),
        "generated_from_local_tiny_model": scalar(True),
        "uses_random_weights": scalar(False),
        "provenance_reviewed": scalar(True),
        "attention_backend": scalar("deterministic_numpy_eager_reference"),
        "attention_score_input_stage": scalar(stage),
        "attention_score_inputs_verified": scalar(bool(verified)),
        "score_transform": scalar(SCORE_TRANSFORM),
        "attention_scale_verified": scalar(bool(verified)),
        "score_bias_verified": scalar(bool(verified)),
        "dense_reference_verified": scalar(bool(verified)),
        "dense_reference_max_abs_error": scalar(float(dense_error)),
        "contract_fixture": scalar(True),
        "preflight_fixture": scalar(False),
    }


def write_bundle(path: Path, rows: dict[str, np.ndarray], *, post: bool) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    q = rows["q_post"] if post else rows["q_raw"]
    k = rows["k_post"] if post else rows["k_raw"]
    stage = SCORE_STAGE_POST if post else SCORE_STAGE_RAW
    verified = bool(post)
    # Raw bundle deliberately carries the model/runtime post-transform reference,
    # so score-contract recomputation must expose semantic mismatch.
    reference = rows["dense_post"]
    direct = dense_attention(q, k, rows["v"], rows["attention_scale"], rows["score_bias"])
    dense_error = float(np.max(np.abs(direct - reference)))
    metadata = base_metadata(
        public=False,
        source_type="synthetic_post_transform_adapter_contract" if post else "synthetic_raw_projection_negative_control",
        stage=stage,
        verified=verified,
        dense_error=(dense_error if post else 0.0),  # raw case understates on purpose; direct verifier catches it.
    )
    np.savez_compressed(
        path,
        q=q,
        k=k,
        v=rows["v"],
        value_norms=np.linalg.norm(rows["v"], axis=-1),
        d_head=scalar(int(q.shape[-1])),
        attention_scale=rows["attention_scale"],
        score_bias=rows["score_bias"],
        dense_reference_output=reference,
        layer=rows["layer"],
        head=rows["head"],
        position=rows["position"],
        prompt_id=rows["prompt_id"],
        active_tokens=rows["active_tokens"],
        regime=rows["regime"],
        **metadata,
    )
    return path


def npz_scalar(data, key: str) -> Any:
    arr = np.asarray(data[key])
    val = arr.reshape(-1)[0]
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    if isinstance(val, np.generic):
        return val.item()
    return val


def manifest_from_npz(path: Path, trace_npz: Path, *, overrides: dict[str, Any] | None = None) -> Path:
    fields = [
        "trace_claim_version", "public_pretrained_trace", "source_type", "model_id", "model_revision",
        "tokenizer_revision", "code_revision", "trust_remote_code", "weights_source", "license", "schema",
        "capture_tool", "capture_tool_sha256", "config_sha256", "generated_from_local_tiny_model",
        "uses_random_weights", "provenance_reviewed", "attention_backend", "attention_score_input_stage",
        "attention_score_inputs_verified", "score_transform", "attention_scale_verified", "score_bias_verified",
        "dense_reference_verified", "dense_reference_max_abs_error",
    ]
    with np.load(trace_npz, allow_pickle=False) as z:
        data = {key: npz_scalar(z, key) for key in fields if key in z.files}
    data["trace_npz_sha256"] = sha256_file(trace_npz)
    data["contract_fixture_manifest"] = True
    if overrides:
        data.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_gate_module():
    spec = importlib.util.spec_from_file_location(f"public_trace_gate_surrogate_{REV}", GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import public trace gate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def compact_gate(payload: dict[str, Any] | None, error: str | None = None) -> dict[str, Any]:
    if payload is None:
        return {
            "gate_exception": error,
            "external_trace_loaded": False,
            "public_pretrained_trace_loaded": False,
            "accepted_as_public_pretrained_trace": False,
        }
    decl = payload.get("external_trace_declaration", {})
    provenance = decl.get("provenance_status", {})
    return {
        "trace_gate_status": payload.get("trace_gate_status"),
        "external_trace_loaded": payload.get("external_trace_loaded"),
        "public_pretrained_trace_loaded": payload.get("public_pretrained_trace_loaded"),
        "accepted_as_public_pretrained_trace": decl.get("accepted_as_public_pretrained_trace"),
        "provenance_status": provenance.get("status"),
        "provenance_errors": provenance.get("errors", [])[:30],
        "trace_row_count": payload.get("summary", {}).get("trace_row_count"),
        "result_row_count": payload.get("summary", {}).get("result_row_count"),
        "oracle_leakage_rows": payload.get("summary", {}).get("oracle_leakage_rows"),
        "evaluated_d_heads": sorted({int(row["D"]) for row in payload.get("rows", []) if "D" in row}),
        "positions": sorted({int(row["position"]) for row in payload.get("rows", []) if "position" in row}),
        "layers": sorted({int(row["layer"]) for row in payload.get("rows", []) if "layer" in row}),
        "heads": sorted({int(row["head"]) for row in payload.get("rows", []) if "head" in row}),
        "score_semantics_verified_rate": float(np.mean([bool(row.get("score_semantics_verified")) for row in payload.get("rows", [])])) if payload.get("rows") else None,
    }


def direct_contract(gate, path: Path) -> dict[str, Any]:
    try:
        result = gate.verify_qkv_score_contract(path)
        return {"computed": True, "within_public_tolerance": float(result["computed_dense_reference_max_abs_error"]) <= PUBLIC_DENSE_TOL, **result}
    except Exception as exc:
        return {"computed": False, "within_public_tolerance": False, "error": str(exc)}


def main() -> int:
    gate = load_gate_module()
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    rows = make_rows()
    post_npz = write_bundle(BUNDLE_DIR / f"{REVUP}_SYNTH_POST_TRANSFORM_QKV_V2.npz", rows, post=True)
    raw_npz = write_bundle(BUNDLE_DIR / f"{REVUP}_SYNTH_RAW_PROJECTION_NEGATIVE_QKV_V2.npz", rows, post=False)
    forged_public_manifest = manifest_from_npz(
        BUNDLE_DIR / f"{REVUP}_SYNTH_POST_TRANSFORM_FORGED_PUBLIC_MANIFEST.json",
        post_npz,
        overrides={
            "public_pretrained_trace": True,
            "source_type": "public_pretrained_manual_export",
            "model_id": "org/pretend-public-model",
            "generated_from_local_tiny_model": False,
            "weights_source": "forged manual export manifest should not override embedded synthetic metadata",
            "license": "forged public terms",
        },
    )

    post_contract = direct_contract(gate, post_npz)
    raw_contract = direct_contract(gate, raw_npz)
    post_gate_payload = gate.run(
        post_npz,
        public_pretrained_trace=False,
        trace_source_label=f"{REV}_synthetic_post_transform_contract",
        bundle_model_id=None,
        bundle_license=None,
        provenance_json=None,
    )
    try:
        public_attempt_payload = gate.run(
            post_npz,
            public_pretrained_trace=True,
            trace_source_label=f"{REV}_synthetic_post_transform_public_attempt",
            bundle_model_id="org/pretend-public-model",
            bundle_license="forged public terms",
            provenance_json=forged_public_manifest,
        )
        public_attempt = compact_gate(public_attempt_payload)
    except Exception as exc:
        public_attempt = compact_gate(None, repr(exc))

    row_count = int(rows["q_post"].shape[0])
    unique_positions = sorted(int(x) for x in np.unique(rows["position"]))
    unique_layers = sorted(int(x) for x in np.unique(rows["layer"]))
    unique_heads = sorted(int(x) for x in np.unique(rows["head"]))
    unique_prompts = sorted(int(x) for x in np.unique(rows["prompt_id"]))
    active_token_counts = sorted(int(x) for x in np.unique(rows["active_tokens"]))
    raw_err = rows["raw_reference_error"]
    summary = {
        "row_count": row_count,
        "prompt_count": len(unique_prompts),
        "positions_covered": unique_positions,
        "position_count": len(unique_positions),
        "layers_covered": unique_layers,
        "layer_count": len(unique_layers),
        "heads_covered": unique_heads,
        "head_count": len(unique_heads),
        "active_token_counts": active_token_counts,
        "d_head": int(rows["q_post"].shape[-1]),
        "d_value": int(rows["v"].shape[-1]),
        "tokens_padded_width": int(rows["k_post"].shape[1]),
        "post_transform_dense_reference_max_abs_error": float(post_contract.get("computed_dense_reference_max_abs_error", math.inf)),
        "post_transform_contract_within_tolerance": bool(post_contract.get("within_public_tolerance") is True),
        "raw_projection_against_post_reference_max_abs_error": float(np.max(raw_err)),
        "raw_projection_against_post_reference_mean_row_error": float(np.mean(raw_err)),
        "raw_projection_contract_rejected_or_out_of_tolerance": bool(raw_contract.get("within_public_tolerance") is not True),
        "causal_padding_bias_min": float(np.min(rows["score_bias"])),
        "finite_score_bias": bool(np.all(np.isfinite(rows["score_bias"]))),
        "nonzero_finite_bias_exercised": bool(np.any((rows["score_bias"] > -1.0) & (np.abs(rows["score_bias"]) > 0))),
        "gate_external_nonpublic_loaded": compact_gate(post_gate_payload).get("external_trace_loaded") is True,
        "gate_public_pretrained_trace_loaded": compact_gate(post_gate_payload).get("public_pretrained_trace_loaded") is True,
        "gate_actual_d_head_propagated": compact_gate(post_gate_payload).get("evaluated_d_heads") == [int(rows["q_post"].shape[-1])],
        "gate_result_row_count_positive": int(compact_gate(post_gate_payload).get("result_row_count") or 0) > 0,
        "synthetic_public_claim_rejected": public_attempt.get("public_pretrained_trace_loaded") is not True and public_attempt.get("accepted_as_public_pretrained_trace") is not True,
        "public_attempt_error_mentions_npz_self_attestation": any("NPZ" in str(e) or "self-attestation" in str(e) or "red-flag" in str(e) for e in public_attempt.get("provenance_errors", [])),
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
    }
    status = "pass_post_transform_contract_harness_no_public_evidence" if all([
        summary["post_transform_contract_within_tolerance"],
        summary["raw_projection_contract_rejected_or_out_of_tolerance"],
        summary["finite_score_bias"],
        summary["nonzero_finite_bias_exercised"],
        summary["gate_external_nonpublic_loaded"],
        summary["gate_actual_d_head_propagated"],
        summary["gate_result_row_count_positive"],
        summary["synthetic_public_claim_rejected"],
        row_count >= 50,
        len(unique_prompts) >= 3,
        len(unique_positions) >= 6,
        len(unique_layers) >= 3,
        len(unique_heads) >= 2,
    ]) else "fail"

    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_POST_TRANSFORM_TRACE_CONTRACT",
        "generated_at": STAMP,
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "measurement_scope": "deterministic architecture-aware post-transform Q/K contract harness with RoPE-like Q/K transforms, finite causal score bias, multiple prompts/positions/layers/heads, gate replay, and raw-projection negative control; synthetic only, not public model evidence",
        "bundles": {
            "post_transform_qkv": {"path": post_npz.relative_to(ROOT).as_posix(), "sha256": sha256_file(post_npz)},
            "raw_projection_negative_control": {"path": raw_npz.relative_to(ROOT).as_posix(), "sha256": sha256_file(raw_npz)},
            "forged_public_manifest": {"path": forged_public_manifest.relative_to(ROOT).as_posix(), "sha256": sha256_file(forged_public_manifest)},
        },
        "summary": summary,
        "post_transform_direct_score_contract": post_contract,
        "raw_projection_direct_score_contract": raw_contract,
        "gate_nonpublic_replay": compact_gate(post_gate_payload),
        "forged_public_claim_attempt": public_attempt,
        "interpretation": (
            "rev0077 turns the missing post-transform adapter into executable semantics: replay from post-RoPE Q/K/V plus explicit scale and finite causal bias is exact, "
            "while raw projection Q/K cannot reproduce the same dense reference. The existing gate loads the bundle as external non-public trace evidence and refuses a forged public claim. "
            "This reduces adapter risk but does not supply public pretrained traces or named-hardware kernel measurements."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    run_manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "generated_at": STAMP,
        "command": "python experiments/post_transform_trace_contract/post_transform_trace_contract.py",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "source_files": {
            THIS.relative_to(ROOT).as_posix(): sha256_file(THIS),
            GATE_SCRIPT.relative_to(ROOT).as_posix(): sha256_file(GATE_SCRIPT),
        },
        "bundle_files": {v["path"]: v["sha256"] for v in artifact["bundles"].values()},
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
    }
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "summary": summary}, indent=2))
    return 0 if status.startswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
