#!/usr/bin/env python3
"""Audit probability semantics for public Llama eager trace bundles.

rev0086 closes a dense-parity blind spot left after the mask/phase/position/
active-key/KV-group gates: a bundle could describe QK score construction while
remaining silent about the probability path.  Current HF Llama eager attention
uses float32 softmax probabilities and applies dropout only in training.  Public
trace acceptance therefore has to attest and gate-check float32 softmax with no
dropout, not a silent float64 NumPy replay or train-mode/dropout path.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0086")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
CAPTURE_PATH = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE_PATH = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scalar(value: Any) -> np.ndarray:
    return np.asarray([value])


def softmax32(cap, scores: np.ndarray) -> np.ndarray:
    # Use the capture helper's public replay softmax; this binds the fixture to
    # the same float32 probability semantics that the gate now requires.
    return cap._softmax_np(scores)


def make_case(cap, *, phase: str, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    batch, heads, kv_heads, d_head, d_value = 1, 2, 1, 4, 3
    if phase == "prefill":
        q_len, key_len = 3, 3
    else:
        q_len, key_len = 1, 5
    q = rng.normal(0.0, 0.4, size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(0.0, 0.4, size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(0.0, 0.4, size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scale = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    if phase == "prefill":
        for pos in range(q_len):
            if pos + 1 < key_len:
                mask[:, :, pos, pos + 1 :] = -np.inf
        query_start_position = 0
    else:
        # Simulate a static/sliding cache tail: five physical slots, four active
        # keys, and one masked padding/stale slot.  The decode row is the last
        # active key, not local position zero.
        mask[:, :, 0, 4:] = -np.inf
        query_start_position = 3
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    groups = heads // kv_heads
    for b in range(batch):
        for pos in range(q_len):
            for h in range(heads):
                kv_head = h // groups
                scores = (k[b, kv_head] @ q[b, h, pos]) * scale + mask[b, 0, pos]
                out[b, pos, h] = softmax32(cap, scores) @ v[b, kv_head]
    return {
        "q": q,
        "k": k,
        "v": v,
        "out": out,
        "mask": mask,
        "scale": scale,
        "groups": groups,
        "capture_phase": "decode_cached" if phase == "decode" else "prefill",
        "query_start_position": query_start_position,
    }


def combine_rows(a: tuple, b: tuple) -> tuple:
    combined = []
    for i, (x, y) in enumerate(zip(a, b)):
        if isinstance(x, list):
            combined.append(x + y)
        elif isinstance(x, bool):
            combined.append(bool(x and y) if i == 14 else bool(x or y))
        else:
            combined.append(max(float(x), float(y)))
    return tuple(combined)


def kv_group_arrays(gate, heads: list[int]) -> dict[str, np.ndarray | bool]:
    head_arr = np.asarray(heads, dtype=np.int64)
    num_attention_heads = np.full((len(head_arr),), 2, dtype=np.int64)
    num_key_value_heads = np.ones((len(head_arr),), dtype=np.int64)
    num_key_value_groups = np.full((len(head_arr),), 2, dtype=np.int64)
    kv_head = np.zeros((len(head_arr),), dtype=np.int64)
    verified = gate.verify_kv_group_map_contract(
        heads=head_arr,
        kv_head=kv_head,
        num_attention_heads=num_attention_heads,
        num_key_value_heads=num_key_value_heads,
        num_key_value_groups=num_key_value_groups,
    )
    return {
        "kv_head": kv_head,
        "num_attention_heads": num_attention_heads,
        "num_key_value_heads": num_key_value_heads,
        "num_key_value_groups": num_key_value_groups,
        "kv_group_map_verified": bool(verified.get("kv_group_map_verified")),
        "gqa_grouped_rows_present": bool(int(verified.get("gqa_grouped_rows", 0)) > 0),
    }


def build_rows(cap) -> tuple:
    pre = make_case(cap, phase="prefill", seed=86001)
    dec = make_case(cap, phase="decode", seed=86002)
    pre_rows = cap._rows_from_attention_capture(
        q=pre["q"], k=pre["k"], v=pre["v"], out=pre["out"], attention_mask=pre["mask"], scaling=pre["scale"],
        layer_id=0, prompt_index=0, position_policy="all_tokens", max_remaining=64,
        num_key_value_groups=pre["groups"], capture_phase=pre["capture_phase"], query_start_position=pre["query_start_position"],
        attention_dropout_p=0.0, attention_training_state=False, attention_probability_dtype=cap.PUBLIC_ATTENTION_PROBABILITY_DTYPE,
    )
    dec_rows = cap._rows_from_attention_capture(
        q=dec["q"], k=dec["k"], v=dec["v"], out=dec["out"], attention_mask=dec["mask"], scaling=dec["scale"],
        layer_id=0, prompt_index=0, position_policy="all_tokens", max_remaining=64,
        num_key_value_groups=dec["groups"], capture_phase=dec["capture_phase"], query_start_position=dec["query_start_position"],
        attention_dropout_p=0.0, attention_training_state=False, attention_probability_dtype=cap.PUBLIC_ATTENTION_PROBABILITY_DTYPE,
    )
    return combine_rows(pre_rows, dec_rows)


def write_bundle(path: Path, rows: tuple, *, cap, gate, mutation: str | None = None) -> dict[str, Any]:
    q_rows, k_rows, v_rows, scale_rows, bias_rows, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, _bias_ok, _mask_seen, max_err = rows
    valid_key_len = np.asarray(valid_key_lens, dtype=np.int64)
    query_len = np.asarray(query_lens, dtype=np.int64)
    max_key_len = int(np.max(valid_key_len))
    q = np.stack(q_rows).astype(np.float64)
    k = cap._pad_3d_rows(k_rows, width=max_key_len).astype(np.float64)
    v = cap._pad_3d_rows(v_rows, width=max_key_len).astype(np.float64)
    scale = np.concatenate(scale_rows).astype(np.float64)
    bias = cap._pad_2d_rows(bias_rows, width=max_key_len, fill=cap.PUBLIC_MASK_SENTINEL).astype(np.float64)
    active_key_len = cap._active_key_lengths_from_bias(bias, valid_key_len)
    active_key_len_ok = cap._active_key_len_semantics_verified(bias, valid_key_len, active_key_len)
    positions_arr = np.asarray(positions, dtype=np.int64)
    valid_key_len_ok = cap._valid_key_len_padding_verified(bias, valid_key_len)
    absolute_position_ok = cap._absolute_position_semantics_verified(positions_arr, valid_key_len, query_len, phases, active_key_len)
    kv = kv_group_arrays(gate, heads)
    decode_present = any(str(p) == "decode_cached" for p in phases)
    prefill_present = any(str(p) == "prefill" for p in phases)
    meta = {
        "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
        "public_pretrained_trace": True,
        "source_type": "public_pretrained_hf",
        "model_id": "org/model-public-placeholder",
        "model_revision": "8" * 40,
        "tokenizer_revision": "9" * 40,
        "code_revision": "not_applicable",
        "trust_remote_code": False,
        "weights_source": "reviewed-source-url-placeholder",
        "license": "reviewed-source-terms-placeholder",
        "schema": gate.PUBLIC_QKV_SCHEMA,
        "capture_tool": "experiments/public_trace_capture/hf_attention_trace_capture.py",
        "capture_tool_sha256": sha256_file(CAPTURE_PATH),
        "config_sha256": "a" * 64,
        "generated_from_local_tiny_model": False,
        "uses_random_weights": False,
        "provenance_reviewed": True,
        "attention_backend": "eager",
        "attention_score_input_stage": gate.PUBLIC_SCORE_INPUT_STAGE,
        "attention_score_inputs_verified": True,
        "score_transform": gate.PUBLIC_SCORE_TRANSFORM,
        "probability_contract": gate.PUBLIC_PROBABILITY_CONTRACT,
        "probability_semantics_verified": True,
        "attention_probability_dtype": gate.PUBLIC_ATTENTION_PROBABILITY_DTYPE,
        "attention_dropout_p": 0.0,
        "attention_training_state": False,
        "dropout_applied": False,
        "attention_scale_verified": True,
        "score_bias_verified": True,
        "mask_challenge_exercised": True,
        "attention_mask_backend_preserved": True,
        "custom_attention_backend_used": False,
        "capture_phase_contract": gate.PUBLIC_CAPTURE_PHASE_CONTRACT,
        "prefill_phase_present": bool(prefill_present),
        "decode_phase_present": bool(decode_present),
        "cache_decode_verified": bool(decode_present),
        "valid_key_len_semantics_verified": bool(valid_key_len_ok),
        "active_key_len_contract": gate.PUBLIC_ACTIVE_KEY_CONTRACT,
        "active_key_len_semantics_verified": bool(active_key_len_ok),
        "kv_group_map_contract": gate.PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": bool(kv["kv_group_map_verified"]),
        "gqa_grouped_rows_present": bool(kv["gqa_grouped_rows_present"]),
        "position_contract": gate.PUBLIC_POSITION_CONTRACT,
        "absolute_position_verified": bool(absolute_position_ok),
        "decode_steps_requested": 1,
        "dense_reference_verified": True,
        "dense_reference_max_abs_error": float(max_err),
    }
    if mutation == "missing_probability_contract":
        meta.pop("probability_contract", None)
    elif mutation == "float64_probability_dtype":
        meta["attention_probability_dtype"] = "float64"
    elif mutation == "dropout_enabled":
        meta["attention_dropout_p"] = 0.10
        meta["dropout_applied"] = True
    np.savez_compressed(
        path,
        q=q, k=k, v=v,
        regime=np.asarray(regimes), layer=np.asarray(layers, dtype=np.int64), head=np.asarray(heads, dtype=np.int64),
        kv_head=kv["kv_head"], num_attention_heads=kv["num_attention_heads"], num_key_value_heads=kv["num_key_value_heads"], num_key_value_groups=kv["num_key_value_groups"],
        position=positions_arr, prompt_id=np.asarray(prompt_ids, dtype=np.int64), capture_phase=np.asarray(phases),
        valid_key_len=valid_key_len, active_key_len=active_key_len.astype(np.int64), query_len=query_len,
        d_head=np.asarray([int(q.shape[-1])], dtype=np.int64), attention_scale=scale, score_bias=bias,
        dense_reference_output=np.stack(refs).astype(np.float64),
        **{name: scalar(value) for name, value in meta.items()},
    )
    prov = dict(meta)
    prov["trace_npz_sha256"] = sha256_file(path)
    prov["d_head"] = int(q.shape[-1])
    prov["adapter"] = "hf_llama_eager_post_transform_attention_forward"
    prov["mutation"] = mutation or "none"
    return prov


def check_gate(gate, path: Path) -> dict[str, Any]:
    try:
        score = gate.verify_qkv_score_contract(path)
        return {"accepted": True, **score}
    except Exception as exc:
        return {"accepted": False, "error": str(exc)}


def main() -> int:
    errors: list[str] = []
    cap = load_module(CAPTURE_PATH, "cloudtainer_capture_probability_semantics")
    gate = load_module(GATE_PATH, "cloudtainer_gate_probability_semantics")
    rows = build_rows(cap)
    q_rows, _k_rows, _v_rows, _scale_rows, _bias_rows, _refs, _regimes, _layers, _heads, _positions, _prompt_ids, phases, valid_key_lens, _query_lens, bias_ok, mask_seen, max_err = rows
    if len(q_rows) <= 0:
        errors.append("fixture produced no rows")
    if float(max_err) > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
        errors.append(f"probability fixture dense parity too large: {max_err}")
    if not bias_ok or not mask_seen:
        errors.append("fixture did not exercise finite mask sentinel semantics")
    if not ({"prefill", "decode_cached"}.issubset({str(x) for x in phases})):
        errors.append("fixture did not include both prefill and cached decode rows")

    gate_results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        good = td_path / "good_probability_contract.npz"
        good_prov = write_bundle(good, rows, cap=cap, gate=gate)
        gate_results["good_probability_contract"] = check_gate(gate, good)
        for mutation in ["missing_probability_contract", "float64_probability_dtype", "dropout_enabled"]:
            bad = td_path / f"bad_{mutation}.npz"
            write_bundle(bad, rows, cap=cap, gate=gate, mutation=mutation)
            gate_results[mutation] = check_gate(gate, bad)

    if gate_results["good_probability_contract"].get("accepted") is not True:
        errors.append("good probability semantics bundle was rejected")
    good_err = gate_results["good_probability_contract"].get("computed_dense_reference_max_abs_error")
    if good_err is None or float(good_err) > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
        errors.append("good probability bundle failed dense parity")
    for mutation in ["missing_probability_contract", "float64_probability_dtype", "dropout_enabled"]:
        if gate_results[mutation].get("accepted") is not False:
            errors.append(f"{mutation} negative control was accepted")

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_probability_semantics_audit",
        "generated_at": META.get("generated_at"),
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "probability_contract": gate.PUBLIC_PROBABILITY_CONTRACT,
        "attention_probability_dtype": gate.PUBLIC_ATTENTION_PROBABILITY_DTYPE,
        "fixture": {
            "row_count": len(q_rows),
            "phases": sorted({str(x) for x in phases}),
            "valid_key_len_min": int(min(valid_key_lens)),
            "valid_key_len_max": int(max(valid_key_lens)),
            "dense_reference_max_abs_error": float(max_err),
            "good_trace_sha256": good_prov.get("trace_npz_sha256"),
        },
        "gate_results": gate_results,
        "summary": {
            "good_probability_contract_accepted": bool(gate_results["good_probability_contract"].get("accepted")),
            "missing_probability_contract_rejected": not bool(gate_results["missing_probability_contract"].get("accepted")),
            "float64_probability_dtype_rejected": not bool(gate_results["float64_probability_dtype"].get("accepted")),
            "dropout_enabled_rejected": not bool(gate_results["dropout_enabled"].get("accepted")),
            "dense_math_same_but_probability_label_rejected": all(not bool(gate_results[m].get("accepted")) for m in ["missing_probability_contract", "float64_probability_dtype", "dropout_enabled"]),
            "current_public_blocker": "actual_public_pretrained_prefill_plus_cached_decode_probability_active_key_kv_group_trace_missing",
        },
        "errors": errors,
        "interpretation": "The public trace gate now requires the Llama eager probability path itself: float32 softmax, eval mode, zero dropout, and explicit attestation in both NPZ metadata and the provenance manifest. This prevents a dense-parity-compatible bundle from silently substituting float64 replay or train-mode/dropout semantics for the runtime probability path.",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_PROBABILITY_SEMANTICS_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        f"# Public trace probability semantics audit — {REV}",
        "",
        f"**Status:** `{report['status']}`",
        "",
        f"- probability contract: `{report['probability_contract']}`",
        f"- attention probability dtype: `{report['attention_probability_dtype']}`",
        f"- fixture rows: `{report['fixture']['row_count']}`",
        f"- good bundle max dense error: `{report['fixture']['dense_reference_max_abs_error']}`",
        "",
        "## Negative controls",
        "",
    ]
    for mutation in ["missing_probability_contract", "float64_probability_dtype", "dropout_enabled"]:
        md.append(f"- `{mutation}` rejected: `{not bool(gate_results[mutation].get('accepted'))}` — {gate_results[mutation].get('error', '')}")
    md += ["", "## Interpretation", "", report["interpretation"]]
    if errors:
        md += ["", "## Errors", *[f"- {e}" for e in errors]]
    (OUT / f"{REVUP}_PUBLIC_TRACE_PROBABILITY_SEMANTICS_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "summary": report["summary"]}, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
