#!/usr/bin/env python3
"""Audit the rev0083 public-trace mask-fidelity and cached-decode seam.

This tool is deliberately small and execution-biased. It verifies the concrete
failure mode found after rev0080: a capture can pass dense parity while silently
losing causal/padding mask semantics if the AttentionInterface seam is patched
with a custom backend. The audit therefore checks two things:

1. the capture row builder serializes causal -inf mask entries as a finite
   sentinel while preserving the dense attention result; and
2. the public gate accepts only traces that self-attest mask challenge exercise,
   built-in mask-backend preservation, no custom attention backend, and cached
   decode phase coverage.

It creates temporary public-like bundles only to exercise the gate. They are not
stored as evidence and never promote a project claim.
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
REV = META.get("revision", "rev0083")
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
CAPTURE_PATH = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE_PATH = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def softmax(scores: np.ndarray) -> np.ndarray:
    shifted = scores - np.max(scores)
    exps = np.exp(shifted)
    return exps / np.sum(exps)


def make_masked_attention_case() -> dict[str, Any]:
    rng = np.random.default_rng(81081)
    batch, heads, kv_heads, q_len, key_len, d_head, d_value = 1, 2, 1, 4, 4, 4, 3
    q = rng.normal(0.0, 0.4, size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(0.0, 0.4, size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(0.0, 0.4, size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scaling = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    for pos in range(q_len):
        if pos + 1 < key_len:
            mask[:, :, pos, pos + 1 :] = -np.inf
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    for b in range(batch):
        for pos in range(q_len):
            for h in range(heads):
                scores = (k[b, 0] @ q[b, h, pos]) * scaling + np.where(np.isneginf(mask[b, 0, pos]), -1.0e30, mask[b, 0, pos])
                out[b, pos, h] = softmax(scores) @ v[b, 0]
    return {"q": q, "k": k, "v": v, "out": out, "mask": mask, "scaling": scaling}


def make_cached_decode_case() -> dict[str, Any]:
    rng = np.random.default_rng(82082)
    batch, heads, kv_heads, q_len, key_len, d_head, d_value = 1, 2, 1, 1, 5, 4, 3
    q = rng.normal(0.0, 0.4, size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(0.0, 0.4, size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(0.0, 0.4, size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scaling = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    for b in range(batch):
        for pos in range(q_len):
            for h in range(heads):
                scores = (k[b, 0] @ q[b, h, pos]) * scaling + mask[b, 0, pos]
                out[b, pos, h] = softmax(scores) @ v[b, 0]
    return {"q": q, "k": k, "v": v, "out": out, "mask": mask, "scaling": scaling}


def merge_rows(a: tuple, b: tuple) -> tuple:
    # First fourteen return slots are row/label lists; final slots are finite,
    # mask-seen, and max-error.
    return tuple(a[i] + b[i] for i in range(14)) + (bool(a[14] and b[14]), bool(a[15] or b[15]), max(float(a[16]), float(b[16])))


def scalar(value: Any) -> np.ndarray:
    return np.asarray([value])


def kv_group_fields(gate, heads: list[int] | np.ndarray) -> dict[str, Any]:
    """Return row-level GQA ownership metadata for synthetic Llama fixtures.

    The existing fixture calls _rows_from_attention_capture with
    num_key_value_groups=2, so both query heads share one compact K/V head.
    Public trace validation must carry this ownership explicitly; otherwise
    downstream cost/cache analysis can count duplicated per-query K/V rows as
    independent KV-cache storage.
    """
    head_arr = np.asarray(heads, dtype=np.int64).reshape(-1)
    row_count = int(head_arr.shape[0])
    num_attention_heads_value = int(max(1, int(np.max(head_arr)) + 1)) if row_count else 1
    num_key_value_heads_value = 1
    num_key_value_groups_value = max(1, num_attention_heads_value // num_key_value_heads_value)
    num_attention_heads = np.full((row_count,), num_attention_heads_value, dtype=np.int64)
    num_key_value_heads = np.full((row_count,), num_key_value_heads_value, dtype=np.int64)
    num_key_value_groups = np.full((row_count,), num_key_value_groups_value, dtype=np.int64)
    kv_head = (head_arr // num_key_value_groups_value).astype(np.int64)
    verification = gate.verify_kv_group_map_contract(
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
        "kv_group_map_verified": bool(verification.get("kv_group_map_verified")),
        "gqa_grouped_rows_present": bool(int(verification.get("gqa_grouped_rows", 0)) > 0),
    }


def write_bundle(path: Path, rows: tuple, *, mask_challenge: bool, cap, gate) -> dict[str, Any]:
    q_rows, k_rows, v_rows, scale_rows, bias_rows, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, _bias_ok, _mask_seen, max_err = rows
    valid_key_len = np.asarray(valid_key_lens, dtype=np.int64)
    max_key_len = int(np.max(valid_key_len))
    q = np.stack(q_rows).astype(np.float64)
    k = cap._pad_3d_rows(k_rows, width=max_key_len).astype(np.float64)
    v = cap._pad_3d_rows(v_rows, width=max_key_len).astype(np.float64)
    scale = np.concatenate(scale_rows).astype(np.float64)
    bias = cap._pad_2d_rows(bias_rows, width=max_key_len, fill=cap.PUBLIC_MASK_SENTINEL).astype(np.float64)
    active_key_len = cap._active_key_lengths_from_bias(bias, valid_key_len)
    active_key_len_ok = cap._active_key_len_semantics_verified(bias, valid_key_len, active_key_len)
    ref = np.stack(refs).astype(np.float64)
    decode_present = any(str(p) == "decode_cached" for p in phases)
    prefill_present = any(str(p) == "prefill" for p in phases)
    valid_key_len_ok = cap._valid_key_len_padding_verified(bias, valid_key_len)
    absolute_position_ok = cap._absolute_position_semantics_verified(np.asarray(positions, dtype=np.int64), valid_key_len, np.asarray(query_lens, dtype=np.int64), phases, active_key_len)
    kv = kv_group_fields(gate, heads)
    meta = {
        "trace_claim_version": gate.PUBLIC_TRACE_CLAIM_VERSION,
        "public_pretrained_trace": True,
        "source_type": "public_pretrained_hf",
        "model_id": "org/model-public-placeholder",
        "model_revision": "a" * 40,
        "tokenizer_revision": "b" * 40,
        "code_revision": "not_applicable",
        "trust_remote_code": False,
        "weights_source": "reviewed-source-url-placeholder",
        "license": "reviewed-source-terms-placeholder",
        "schema": gate.PUBLIC_QKV_SCHEMA,
        "capture_tool": "experiments/public_trace_capture/hf_attention_trace_capture.py",
        "capture_tool_sha256": sha256_file(CAPTURE_PATH),
        "config_sha256": "c" * 64,
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
        "mask_challenge_exercised": bool(mask_challenge),
        "attention_mask_backend_preserved": True,
        "custom_attention_backend_used": False,
        "capture_phase_contract": gate.PUBLIC_CAPTURE_PHASE_CONTRACT,
        "prefill_phase_present": bool(prefill_present),
        "decode_phase_present": bool(decode_present),
        "cache_decode_verified": bool(decode_present and any(int(q) == 1 and int(vkl) > 1 for q, vkl in zip(query_lens, valid_key_lens))),
        "valid_key_len_semantics_verified": bool(valid_key_len_ok),
        "active_key_len_contract": gate.PUBLIC_ACTIVE_KEY_CONTRACT,
        "active_key_len_semantics_verified": bool(active_key_len_ok),
        "kv_group_map_contract": gate.PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": bool(kv["kv_group_map_verified"]),
        "gqa_grouped_rows_present": bool(kv["gqa_grouped_rows_present"]),
        "position_contract": gate.PUBLIC_POSITION_CONTRACT if bool(absolute_position_ok) else "local_query_position_v0",
        "absolute_position_verified": bool(absolute_position_ok),
        "decode_steps_requested": 1,
        "dense_reference_verified": True,
        "dense_reference_max_abs_error": float(max_err),
    }
    np.savez_compressed(
        path,
        q=q,
        k=k,
        v=v,
        regime=np.asarray(regimes),
        layer=np.asarray(layers, dtype=np.int64),
        head=np.asarray(heads, dtype=np.int64),
        kv_head=kv["kv_head"],
        num_attention_heads=kv["num_attention_heads"],
        num_key_value_heads=kv["num_key_value_heads"],
        num_key_value_groups=kv["num_key_value_groups"],
        position=np.asarray(positions, dtype=np.int64),
        prompt_id=np.asarray(prompt_ids, dtype=np.int64),
        capture_phase=np.asarray(phases),
        valid_key_len=valid_key_len,
        active_key_len=active_key_len.astype(np.int64),
        query_len=np.asarray(query_lens, dtype=np.int64),
        d_head=np.asarray([int(q.shape[-1])], dtype=np.int64),
        attention_scale=scale,
        score_bias=bias,
        dense_reference_output=ref,
        **{name: scalar(value) for name, value in meta.items()},
    )
    prov = dict(meta)
    prov["trace_npz_sha256"] = sha256_file(path)
    prov["d_head"] = int(q.shape[-1])
    prov["adapter"] = "hf_llama_eager_post_transform_attention_forward"
    return prov


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    cap = load_module(CAPTURE_PATH, "cloudtainer_capture_rev0083")
    gate = load_module(GATE_PATH, "cloudtainer_gate_rev0083")

    case = make_masked_attention_case()
    prefill_rows = cap._rows_from_attention_capture(
        q=case["q"],
        k=case["k"],
        v=case["v"],
        out=case["out"],
        attention_mask=case["mask"],
        scaling=case["scaling"],
        layer_id=0,
        prompt_index=0,
        position_policy="last_and_mid",
        max_remaining=64,
        num_key_value_groups=2,
        capture_phase="prefill",
    )
    decode_case = make_cached_decode_case()
    decode_rows = cap._rows_from_attention_capture(
        q=decode_case["q"],
        k=decode_case["k"],
        v=decode_case["v"],
        out=decode_case["out"],
        attention_mask=decode_case["mask"],
        scaling=decode_case["scaling"],
        layer_id=0,
        prompt_index=0,
        position_policy="all_tokens",
        max_remaining=64,
        num_key_value_groups=2,
        capture_phase="decode_cached",
    )
    rows = merge_rows(prefill_rows, decode_rows)
    q_rows, k_rows, v_rows, scale_rows, bias_rows, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, bias_ok, mask_seen, max_err = rows
    if len(q_rows) != 6:
        errors.append(f"expected six audited rows from prefill mask plus cached decode fixture, got {len(q_rows)}")
    if not bias_ok:
        errors.append("mask/bias rows were not serializable after finite sentinel conversion")
    if not mask_seen:
        errors.append("mask_challenge_exercised was not detected")
    if not any(np.any(np.asarray(row) < -1.0e20) for row in bias_rows):
        errors.append("no finite negative sentinel appeared in captured score_bias rows")
    if not math.isfinite(float(max_err)) or float(max_err) > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
        errors.append(f"dense reconstruction exceeded tight fixture tolerance: {max_err}")

    gate_results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="ctml_mask_audit_") as tmp:
        tmpdir = Path(tmp)
        good_npz = tmpdir / "good.npz"
        good_prov = tmpdir / "good.provenance.json"
        good_manifest = write_bundle(good_npz, rows, mask_challenge=True, cap=cap, gate=gate)
        good_prov.write_text(json.dumps(good_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        good_validation = gate.validate_public_trace_provenance(good_prov, good_npz)
        gate_results["masked_public_like_bundle"] = {
            "accepted": bool(good_validation.get("accepted")),
            "status": good_validation.get("status"),
            "errors": good_validation.get("errors", []),
            "score_contract_max_abs_error": (good_validation.get("score_contract_verification") or {}).get("computed_dense_reference_max_abs_error"),
        }
        if good_validation.get("accepted") is not True:
            errors.append("gate did not accept a well-formed masked qkv_npz_v2 bundle in the temporary audit harness")

        bad_npz = tmpdir / "bad.npz"
        bad_prov = tmpdir / "bad.provenance.json"
        bad_manifest = write_bundle(bad_npz, rows, mask_challenge=False, cap=cap, gate=gate)
        bad_prov.write_text(json.dumps(bad_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bad_validation = gate.validate_public_trace_provenance(bad_prov, bad_npz)
        bad_errors = bad_validation.get("errors", [])
        gate_results["missing_mask_challenge_bundle"] = {
            "accepted": bool(bad_validation.get("accepted")),
            "status": bad_validation.get("status"),
            "errors": bad_errors,
        }
        if bad_validation.get("accepted") is True:
            errors.append("gate accepted a bundle with mask_challenge_exercised=false")
        if not any("mask" in str(e).lower() for e in bad_errors):
            errors.append("gate rejection for missing mask challenge did not mention mask fidelity")

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_mask_fidelity_audit",
        "generated_at": META.get("generated_at"),
        "status": "fail" if errors else "pass_with_blockers",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": {
            "rows_checked": int(len(q_rows)),
            "bias_serializable": bool(bias_ok),
            "mask_challenge_exercised": bool(mask_seen),
            "finite_negative_mask_sentinel_seen": bool(any(np.any(np.asarray(row) < -1.0e20) for row in bias_rows)),
            "dense_reconstruction_max_abs_error": float(max_err),
            "decode_phase_present": bool(any(str(p) == "decode_cached" for p in phases)),
            "valid_key_len_padding_exercised": bool(max(valid_key_lens) > min(valid_key_lens)),
            "temporary_masked_bundle_accepted_by_gate": bool(gate_results.get("masked_public_like_bundle", {}).get("accepted")),
            "temporary_missing_mask_bundle_rejected_by_gate": not bool(gate_results.get("missing_mask_challenge_bundle", {}).get("accepted")),
        },
        "gate_results": gate_results,
        "research_sources": [
            {
                "url": "https://huggingface.co/docs/transformers/en/attention_interface",
                "finding": "Custom attention backends need matching attention-mask registration; otherwise attention_mask can be None and constraints can be dropped.",
            },
            {
                "url": "https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py",
                "finding": "Current Llama eager attention receives post-RoPE query/key/value tensors, scaling, and attention_mask before score computation.",
            },
            {
                "url": "https://github.com/huggingface/transformers/issues/40362",
                "finding": "A public issue reports changed Llama computation when registering a custom AttentionInterface backend, reinforcing the need for a safer seam.",
            },
        ],
        "blockers": [
            "actual_public_pretrained_post_transform_qkv_bundle_missing",
            "verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule",
            "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
        ],
        "errors": errors,
        "warnings": warnings,
        "interpretation": (
            "rev0083 keeps the mask-fidelity contract executable and extends its fixture to mixed prefill plus cached-decode rows: a public claim must prove that a masked score row was captured, "
            "the built-in eager mask backend was preserved, no custom attention backend was used, dense attention recomputes from exported q/k/v/scale/bias, and valid_key_len padding semantics survived the mixed phase bundle. "
            "The accepted temporary bundle in this audit is only a gate harness sanity check; it is not public model evidence."
        ),
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_MASK_FIDELITY_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        f"# Public trace mask-fidelity audit — {REV}",
        "",
        f"**Status:** {report['status']}",
        "",
        report["interpretation"],
        "",
        "## What was exercised",
        "",
        f"- rows checked: `{len(q_rows)}`",
        f"- finite negative mask sentinel seen: `{report['summary']['finite_negative_mask_sentinel_seen']}`",
        f"- dense reconstruction max abs error: `{report['summary']['dense_reconstruction_max_abs_error']}`",
        f"- decode phase present: `{report['summary']['decode_phase_present']}`",
        f"- valid_key_len padding exercised: `{report['summary']['valid_key_len_padding_exercised']}`",
        f"- gate accepts temporary masked bundle: `{report['summary']['temporary_masked_bundle_accepted_by_gate']}`",
        f"- gate rejects missing-mask-challenge bundle: `{report['summary']['temporary_missing_mask_bundle_rejected_by_gate']}`",
        "",
        "## Remaining blockers",
        "",
    ]
    lines.extend(f"- `{b}`" for b in report["blockers"])
    lines.extend([
        "",
        "## Research inputs",
        "",
        "- Hugging Face AttentionInterface / AttentionMaskInterface documentation",
        "- Hugging Face Transformers Llama eager attention source",
        "- Hugging Face Transformers issue #40362 on custom AttentionInterface behavior",
        "",
    ])
    (OUT / f"{REVUP}_PUBLIC_TRACE_MASK_FIDELITY_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
