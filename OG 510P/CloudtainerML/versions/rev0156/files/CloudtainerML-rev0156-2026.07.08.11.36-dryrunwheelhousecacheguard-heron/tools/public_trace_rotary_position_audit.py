#!/usr/bin/env python3
"""Audit runtime RoPE position_id semantics in public cached-decode traces.

rev0087 fixes a trace-fidelity blind spot left after absolute active-position
and active-key gates.  In current Llama-style runtime code, RoPE is driven by
runtime ``position_ids``.  During cached decode, the query's global RoPE
position can differ from the row's active-cache position used for selector and
cost analysis.  Dense Q/K/V parity can still pass if a trace stores the correct
post-RoPE tensors but labels that decode row as local position 0; this audit
proves the public gate rejects that false-green bundle.
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
REV = META.get("revision", "rev0087")
REVUP = str(REV).upper()
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


def make_case(*, q_len: int, key_len: int, seed: int, causal: bool, active_len: int | None = None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    batch, heads, kv_heads, d_head, d_value = 1, 2, 1, 4, 3
    groups = heads // kv_heads
    q = rng.normal(0.0, 0.35, size=(batch, heads, q_len, d_head)).astype(np.float64)
    k = rng.normal(0.0, 0.35, size=(batch, kv_heads, key_len, d_head)).astype(np.float64)
    v = rng.normal(0.0, 0.35, size=(batch, kv_heads, key_len, d_value)).astype(np.float64)
    scaling = 1.0 / math.sqrt(d_head)
    mask = np.zeros((batch, 1, q_len, key_len), dtype=np.float64)
    if causal:
        for pos in range(q_len):
            if pos + 1 < key_len:
                mask[:, :, pos, pos + 1 :] = -np.inf
    if active_len is not None:
        if active_len <= 0 or active_len > key_len:
            raise ValueError("active_len must be within physical key width")
        mask[:, :, :, active_len:] = -np.inf
    out = np.zeros((batch, q_len, heads, d_value), dtype=np.float64)
    for b in range(batch):
        for pos in range(q_len):
            additive = np.where(np.isneginf(mask[b, 0, pos]), -1.0e30, mask[b, 0, pos])
            for h in range(heads):
                kv_head = h // groups
                scores = (k[b, kv_head] @ q[b, h, pos]) * scaling + additive
                out[b, pos, h] = softmax(scores) @ v[b, kv_head]
    return {"q": q, "k": k, "v": v, "out": out, "mask": mask, "scaling": scaling, "groups": groups}


def rows_for(cap, case: dict[str, Any], *, phase: str, policy: str, rotary_ids: np.ndarray, query_start_position: int | None = None) -> tuple[tuple, list[int]]:
    rotary_out: list[int] = []
    rows = cap._rows_from_attention_capture(
        q=case["q"],
        k=case["k"],
        v=case["v"],
        out=case["out"],
        attention_mask=case["mask"],
        scaling=case["scaling"],
        layer_id=0,
        prompt_index=0,
        position_policy=policy,
        max_remaining=128,
        num_key_value_groups=case["groups"],
        capture_phase=phase,
        query_start_position=query_start_position,
        rotary_position_ids=rotary_ids,
        rotary_position_out=rotary_out,
    )
    return rows, rotary_out


def merge_rows(*row_sets: tuple) -> tuple:
    out = list(row_sets[0])
    for rows in row_sets[1:]:
        for i in range(14):
            out[i] = out[i] + rows[i]
        out[14] = bool(out[14] and rows[14])
        out[15] = bool(out[15] or rows[15])
        out[16] = max(float(out[16]), float(rows[16]))
    return tuple(out)


def scalar(value: Any) -> np.ndarray:
    return np.asarray([value])


def kv_group_fields(gate, heads: list[int] | np.ndarray) -> dict[str, Any]:
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


def write_bundle(path: Path, rows: tuple, rotary_ids: list[int], *, cap, gate, forge_local_decode_rope_id: bool) -> dict[str, Any]:
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
    ref = np.stack(refs).astype(np.float64)
    valid_key_len_ok = cap._valid_key_len_padding_verified(bias, valid_key_len)
    absolute_position_ok = cap._absolute_position_semantics_verified(positions_arr, valid_key_len, query_len, phases, active_key_len)
    rotary_position = np.asarray(rotary_ids, dtype=np.int64)
    real_rotary_position = rotary_position.copy()
    if forge_local_decode_rope_id:
        rotary_position = rotary_position.copy()
        for i, phase in enumerate(phases):
            if str(phase) == "decode_cached":
                rotary_position[i] = 0
    rotary_check = gate.verify_rotary_position_contract(
        rotary_position_id=rotary_position,
        active_position=positions_arr,
        query_len=query_len,
        capture_phase=np.asarray(phases),
    )
    decode_present = any(str(p) == "decode_cached" for p in phases)
    prefill_present = any(str(p) == "prefill" for p in phases)
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
        "mask_challenge_exercised": bool(any(np.any(np.asarray(row) < -1.0e20) for row in bias_rows)),
        "attention_mask_backend_preserved": True,
        "custom_attention_backend_used": False,
        "capture_phase_contract": gate.PUBLIC_CAPTURE_PHASE_CONTRACT,
        "prefill_phase_present": bool(prefill_present),
        "decode_phase_present": bool(decode_present),
        "cache_decode_verified": bool(decode_present and any(int(q_len) == 1 and int(vkl) > 1 for q_len, vkl in zip(query_lens, valid_key_lens))),
        "valid_key_len_semantics_verified": bool(valid_key_len_ok),
        "active_key_len_contract": gate.PUBLIC_ACTIVE_KEY_CONTRACT,
        "active_key_len_semantics_verified": bool(active_key_len_ok),
        "kv_group_map_contract": gate.PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": bool(kv["kv_group_map_verified"]),
        "gqa_grouped_rows_present": bool(kv["gqa_grouped_rows_present"]),
        "position_contract": gate.PUBLIC_POSITION_CONTRACT,
        "absolute_position_verified": bool(absolute_position_ok),
        "rotary_position_contract": gate.PUBLIC_ROTARY_POSITION_CONTRACT,
        "rotary_position_ids_verified": bool(rotary_check.get("rotary_position_verified")),
        "rotary_position_ids_present_call_count": 2,
        "decode_steps_requested": 2,
        "dense_reference_verified": True,
        "dense_reference_max_abs_error": float(max_err),
    }
    if forge_local_decode_rope_id:
        # Same dense Q/K/V/reference tensors, but a false self-attestation that
        # cached decode used local q_len index 0 as the RoPE/global position.
        # The gate must recompute and reject this.
        meta["rotary_position_ids_verified"] = True
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
        position=positions_arr,
        rotary_position_id=rotary_position.astype(np.int64),
        prompt_id=np.asarray(prompt_ids, dtype=np.int64),
        capture_phase=np.asarray(phases),
        valid_key_len=valid_key_len,
        active_key_len=active_key_len.astype(np.int64),
        query_len=query_len,
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
    prov["real_rotary_position_id_min"] = int(np.min(real_rotary_position))
    prov["real_rotary_position_id_max"] = int(np.max(real_rotary_position))
    prov["serialized_rotary_position_id_min"] = int(np.min(rotary_position))
    prov["serialized_rotary_position_id_max"] = int(np.max(rotary_position))
    prov["decode_rotary_global_offset_rows"] = int(rotary_check.get("decode_rotary_global_offset_rows", 0))
    return prov


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    cap = load_module(CAPTURE_PATH, "cloudtainer_capture_rotary_position")
    gate = load_module(GATE_PATH, "cloudtainer_gate_rotary_position")

    prefill_case = make_case(q_len=4, key_len=4, seed=870871, causal=True)
    decode_case = make_case(q_len=1, key_len=8, seed=870872, causal=False, active_len=5)
    prefill, prefill_rope = rows_for(
        cap,
        prefill_case,
        phase="prefill",
        policy="last_and_mid",
        rotary_ids=np.asarray([[0, 1, 2, 3]], dtype=np.int64),
        query_start_position=0,
    )
    decode, decode_rope = rows_for(
        cap,
        decode_case,
        phase="decode_cached",
        policy="all_tokens",
        rotary_ids=np.asarray([[7]], dtype=np.int64),
        query_start_position=7,
    )
    rows = merge_rows(prefill, decode)
    rotary_ids = prefill_rope + decode_rope
    q_rows, _k_rows, _v_rows, _scale_rows, bias_rows, _refs, _regimes, _layers, _heads, positions, _prompt_ids, phases, valid_key_lens, query_lens, bias_ok, mask_seen, max_err = rows
    valid_key_len_arr = np.asarray(valid_key_lens, dtype=np.int64)
    query_len_arr = np.asarray(query_lens, dtype=np.int64)
    positions_arr = np.asarray(positions, dtype=np.int64)
    bias = cap._pad_2d_rows(bias_rows, width=int(np.max(valid_key_len_arr)), fill=cap.PUBLIC_MASK_SENTINEL)
    active_key_len_arr = cap._active_key_lengths_from_bias(bias, valid_key_len_arr)
    rotary_check = gate.verify_rotary_position_contract(
        rotary_position_id=np.asarray(rotary_ids, dtype=np.int64),
        active_position=positions_arr,
        query_len=query_len_arr,
        capture_phase=np.asarray(phases),
    )
    global_decode_rows = [
        {"active_position": int(pos), "rotary_position_id": int(rid), "query_len": int(q_len), "active_key_len": int(active)}
        for pos, rid, q_len, active, phase in zip(positions_arr, rotary_ids, query_len_arr, active_key_len_arr, phases)
        if str(phase) == "decode_cached" and int(rid) > int(pos)
    ]
    if not bias_ok or not mask_seen:
        errors.append("rotary fixture lost finite mask challenge")
    if float(max_err) > getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5):
        errors.append(f"dense parity too large in rotary fixture: {max_err}")
    if rotary_check.get("rotary_position_verified") is not True:
        errors.append("runtime RoPE position_id fixture did not satisfy rotary contract")
    if not global_decode_rows:
        errors.append("fixture did not exercise cached decode where rotary_position_id exceeds active row position")

    gate_results: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="ctml_rotary_position_audit_") as tmp:
        tmpdir = Path(tmp)
        good_npz = tmpdir / "rotary_position_good.npz"
        good_prov = tmpdir / "rotary_position_good.provenance.json"
        good_manifest = write_bundle(good_npz, rows, rotary_ids, cap=cap, gate=gate, forge_local_decode_rope_id=False)
        good_prov.write_text(json.dumps(good_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        good_validation = gate.validate_public_trace_provenance(good_prov, good_npz)
        good_score = good_validation.get("score_contract_verification") or {}
        gate_results["rotary_position_bundle"] = {
            "accepted": bool(good_validation.get("accepted")),
            "status": good_validation.get("status"),
            "errors": good_validation.get("errors", []),
            "rotary_position_contract_verified": good_score.get("rotary_position_contract_verified"),
            "rotary_position_global_offset_rows": good_score.get("rotary_position_global_offset_rows"),
        }
        if good_validation.get("accepted") is not True:
            errors.append("gate did not accept the runtime RoPE position bundle")

        bad_npz = tmpdir / "rotary_position_local_index_bad.npz"
        bad_prov = tmpdir / "rotary_position_local_index_bad.provenance.json"
        bad_manifest = write_bundle(bad_npz, rows, rotary_ids, cap=cap, gate=gate, forge_local_decode_rope_id=True)
        bad_prov.write_text(json.dumps(bad_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bad_validation = gate.validate_public_trace_provenance(bad_prov, bad_npz)
        bad_errors = bad_validation.get("errors", [])
        bad_score = bad_validation.get("score_contract_verification") or {}
        gate_results["local_rope_id_forged_bundle"] = {
            "accepted": bool(bad_validation.get("accepted")),
            "status": bad_validation.get("status"),
            "errors": bad_errors,
            "dense_reference_max_abs_error": bad_score.get("computed_dense_reference_max_abs_error", float(max_err)),
            "dense_reference_same_as_good_fixture": float(max_err) <= getattr(gate, "PUBLIC_DENSE_PARITY_MAX_ABS_ERROR", 1e-5),
            "rotary_position_contract_verified": bad_score.get("rotary_position_contract_verified"),
            "rotary_position_global_offset_rows": bad_score.get("rotary_position_global_offset_rows"),
        }
        if bad_validation.get("accepted") is True:
            errors.append("gate accepted a cached-decode bundle forged to local rotary_position_id 0")
        if not any("rope" in str(e).lower() or "rotary" in str(e).lower() for e in bad_errors):
            errors.append("local rotary_position_id rejection did not mention RoPE/rotary semantics")

    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_rotary_position_audit",
        "generated_at": META.get("generated_at"),
        "status": "fail" if errors else "pass_with_blockers",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": {
            "mixed_rows_checked": int(len(q_rows)),
            "rotary_position_contract_verified": bool(rotary_check.get("rotary_position_verified")),
            "decode_rotary_global_offset_rows": int(rotary_check.get("decode_rotary_global_offset_rows", 0)),
            "global_decode_rows": global_decode_rows,
            "temporary_rotary_position_bundle_accepted_by_gate": bool(gate_results.get("rotary_position_bundle", {}).get("accepted")),
            "temporary_local_rope_id_bundle_rejected_by_gate": not bool(gate_results.get("local_rope_id_forged_bundle", {}).get("accepted")),
            "dense_math_same_but_local_rope_id_rejected": bool(
                not gate_results.get("local_rope_id_forged_bundle", {}).get("accepted")
                and gate_results.get("local_rope_id_forged_bundle", {}).get("dense_reference_same_as_good_fixture") is True
            ),
        },
        "gate_results": gate_results,
        "research_sources": [
            {
                "url": "https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py",
                "finding": "LlamaModel builds position_ids from past_key_values.get_seq_length during cached use and passes position_embeddings/position_ids through the decoder layer into attention.",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/internal/rope_utils",
                "finding": "RoPE behavior is model/config-dependent, so trace evidence should carry the runtime position_ids that produced the rotated Q/K tensors.",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/kv_cache",
                "finding": "Cache strategy affects physical key storage, making global RoPE positions and active scored key positions distinct pieces of evidence.",
            },
        ],
        "blockers": [
            "actual_public_pretrained_prefill_plus_cached_decode_bundle_missing",
            "verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule",
            "named_hardware_end_to_end_sparse_vs_dense_measurement_missing",
        ],
        "errors": errors,
        "warnings": warnings,
        "interpretation": (
            "rev0087 prevents a cached-decode false green: a trace can contain correct post-RoPE Q/K/V rows and still mislabel the runtime RoPE position_id as local q_len position 0. "
            "The public gate now requires row-level rotary_position_id evidence and rejects a same-math forged bundle whose decode RoPE id no longer matches the runtime/global position semantics. "
            "This remains trace-fidelity hardening; it is not a substitute for a real public checkpoint capture."
        ),
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_ROTARY_POSITION_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        f"# Public trace runtime RoPE position audit — {REV}",
        "",
        f"**Status:** {report['status']}",
        "",
        report["interpretation"],
        "",
        "## What was exercised",
        "",
        f"- mixed rows checked: `{report['summary']['mixed_rows_checked']}`",
        f"- rotary position contract verified: `{report['summary']['rotary_position_contract_verified']}`",
        f"- cached-decode rows with global RoPE offset: `{report['summary']['decode_rotary_global_offset_rows']}`",
        f"- gate accepts temporary runtime-RoPE bundle: `{report['summary']['temporary_rotary_position_bundle_accepted_by_gate']}`",
        f"- gate rejects local q_len RoPE-id forgery: `{report['summary']['temporary_local_rope_id_bundle_rejected_by_gate']}`",
        f"- dense math same but local RoPE label rejected: `{report['summary']['dense_math_same_but_local_rope_id_rejected']}`",
        "",
        "## Global decode RoPE rows",
        "",
    ]
    lines.extend(f"- active position `{r['active_position']}`, rotary_position_id `{r['rotary_position_id']}`, active_key_len `{r['active_key_len']}`" for r in global_decode_rows)
    lines.extend([
        "",
        "## Remaining blockers",
        "",
    ])
    lines.extend(f"- `{b}`" for b in report["blockers"])
    lines.extend([
        "",
        "## Research inputs",
        "",
        "- Hugging Face current Llama modeling source",
        "- Hugging Face RoPE utilities documentation",
        "- Hugging Face KV cache documentation",
        "",
    ])
    (OUT / f"{REVUP}_PUBLIC_TRACE_ROTARY_POSITION_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": report["status"], "errors": len(errors), "warnings": len(warnings)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
