#!/usr/bin/env python3
"""Offline Hugging Face attention-trace capture helper.

rev0076 makes the capture boundary fail closed on *semantic* fidelity, not just
file provenance. Projection hooks are useful diagnostics, but they are not
assumed to be the tensors actually scored by attention. In particular,
Llama/Mistral/Gemma-style q_proj/k_proj hooks fire before rotary (and possibly
other architecture-specific) Q/K transforms. Such captures are written as
non-public diagnostics and cannot self-promote.

A verified adapter may set attention_score_inputs_verified and
dense_reference_verified only after it captures post-transform Q/K, preserves the
backend's attention-mask formatter, records runtime RoPE position_ids, exercises
at least one causal-mask challenge row, records cached-decode coverage, and checks
reconstructed dense attention against the model's own eager reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (  # noqa: E402
    EXPECTED_MODEL_SAFETENSORS_SHA256,
    inspect_snapshot,
    snapshot_candidate_paths,
)
CAPTURE_TOOL_REL = "experiments/public_trace_capture/hf_attention_trace_capture.py"
PUBLIC_SCORE_INPUT_STAGE = "post_model_qk_transforms"
PUBLIC_TRACE_CLAIM_VERSION = "public_trace_claim_v14"
PUBLIC_ACTIVE_KEY_CONTRACT = "mask_derived_active_prefix_v1"
PUBLIC_POSITION_CONTRACT = "absolute_active_key_position_v2"
PUBLIC_KV_GROUP_CONTRACT = "query_to_kv_head_group_map_v1"
PUBLIC_PROBABILITY_CONTRACT = "float32_softmax_no_dropout_v1"
PUBLIC_ROTARY_POSITION_CONTRACT = "runtime_rope_position_ids_v1"
PUBLIC_TOKEN_PROVENANCE_CONTRACT = "prompt_input_ids_attention_mask_digest_v2"
PUBLIC_PROMPT_MANIFEST_CONTRACT = "prompt_text_tokenizer_call_manifest_v1"
PUBLIC_GENERATION_TOKEN_CONTRACT = "generated_sequence_digest_exact_length_v2"
PUBLIC_GENERATION_DETERMINISM_CONTRACT = "greedy_exact_length_cached_decode_generation_config_v3"
PUBLIC_CACHE_IMPLEMENTATION_CONTRACT = "hf_generate_dynamic_cache_v1"
PUBLIC_REQUIRED_CACHE_IMPLEMENTATION = "dynamic"
PUBLIC_RUNTIME_PROVENANCE_CONTRACT = "trace_runtime_device_dtype_timing_v1"
PUBLIC_CAPTURE_OFFLINE_QUARANTINE_CONTRACT = "hf_transformers_offline_env_before_runtime_import_v1"
PUBLIC_TIMING_CLOCK_CONTRACT = "synchronized_perf_counter_or_cuda_event_v1"
PUBLIC_ATTENTION_PROBABILITY_DTYPE = "float32"
PUBLIC_MASK_SENTINEL = -1.0e30
PUBLIC_QKV_SCHEMA = "qkv_npz_v2"
PUBLIC_SCORE_TRANSFORM = "scaled_dot_product_plus_bias"
PUBLIC_DENSE_PARITY_MAX_ABS_ERROR = 1e-5
PUBLIC_CAPTURE_PHASE_CONTRACT = "prefill_and_cached_decode_v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(data: Any) -> str:
    blob = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_int_array(value: Any) -> str:
    arr = np.asarray(value, dtype=np.int64).tolist()
    return sha256_json(arr)


def _json_canonical_text(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _tokenization_settings(tokenizer: Any) -> dict[str, Any]:
    """Canonical tokenizer-call settings for public prompt replay.

    Public traces should not depend on tokenizer defaults that can differ across
    slow/fast implementations or chat-template wrappers.  The capture helper
    therefore records both the requested call knobs and the observed tokenizer
    surface that turns prompt text into input_ids/attention_mask.
    """
    return {
        "contract": PUBLIC_PROMPT_MANIFEST_CONTRACT,
        "call": {
            "add_special_tokens": True,
            "padding": False,
            "truncation": False,
            "return_attention_mask": True,
            "return_tensors": "pt",
            "chat_template_applied": False,
        },
        "observed_tokenizer": {
            "class": tokenizer.__class__.__name__,
            "is_fast": bool(getattr(tokenizer, "is_fast", False)),
            "padding_side": str(getattr(tokenizer, "padding_side", "unknown")),
            "truncation_side": str(getattr(tokenizer, "truncation_side", "unknown")),
            "model_max_length": str(getattr(tokenizer, "model_max_length", "unknown")),
            "bos_token_id_sha256": _token_id_digest(getattr(tokenizer, "bos_token_id", None)),
            "eos_token_id_sha256": _token_id_digest(getattr(tokenizer, "eos_token_id", None)),
            "pad_token_id_sha256": _token_id_digest(getattr(tokenizer, "pad_token_id", None)),
        },
    }


def _prompt_manifest(prompts: list[str], tokenizer: Any, token_records: list[dict[str, Any]]) -> dict[str, Any]:
    settings = _tokenization_settings(tokenizer)
    records_by_index = {int(r.get("prompt_index", -1)): r for r in token_records}
    return {
        "contract": PUBLIC_PROMPT_MANIFEST_CONTRACT,
        "tokenization_settings": settings,
        "prompt_count": len(prompts),
        "prompts": [
            {
                "prompt_index": i,
                "text": str(prompt),
                "text_sha256": sha256_text(str(prompt)),
                "input_ids_sha256": str(records_by_index.get(i, {}).get("input_ids_sha256", "")),
                "attention_mask_sha256": str(records_by_index.get(i, {}).get("attention_mask_sha256", "")),
                "token_count": int(records_by_index.get(i, {}).get("token_count", 0)),
                "attention_mask_sum": int(records_by_index.get(i, {}).get("attention_mask_sum", 0)),
            }
            for i, prompt in enumerate(prompts)
        ],
    }


def _token_id_digest(value: Any) -> str:
    if value is None:
        return sha256_json(None)
    if isinstance(value, np.ndarray):
        return sha256_json(np.asarray(value, dtype=np.int64).tolist())
    if isinstance(value, (list, tuple)):
        return sha256_json([int(x) for x in value])
    return sha256_json(int(value))


def _resolve_torch_dtype_arg(torch: Any, requested: str) -> Any:
    """Resolve the explicit load dtype knob used by from_pretrained.

    Public traces must not inherit a dtype accidentally from model defaults,
    hardware autocast, or an operator's shell history.  The string is recorded
    in provenance and the resolved value is passed into HF loading when possible.
    """
    value = str(requested or "float32").strip().lower()
    if value == "auto":
        return "auto"
    table = {
        "float32": getattr(torch, "float32"),
        "float16": getattr(torch, "float16"),
        "bfloat16": getattr(torch, "bfloat16"),
    }
    if value not in table:
        raise SystemExit(f"unsupported --torch-dtype {requested!r}; expected auto, float32, float16, or bfloat16")
    return table[value]


def _runtime_device_dtype_summary(torch: Any, model: Any, *, requested_torch_dtype: str, requested_device_policy: str, actual_device: str, synchronized_before_after_timing: bool, capture_elapsed_seconds: float) -> dict[str, Any]:
    dtypes: set[str] = set()
    devices: set[str] = set()
    first_dtype = "unknown"
    first_device = str(actual_device)
    param_count = 0
    try:
        for param in model.parameters():
            param_count += 1
            dtype_s = str(getattr(param, "dtype", "unknown"))
            device_s = str(getattr(param, "device", "unknown"))
            dtypes.add(dtype_s)
            devices.add(device_s)
            if param_count == 1:
                first_dtype = dtype_s
                first_device = device_s
    except Exception:
        pass
    cuda_available = bool(getattr(torch, "cuda", None) is not None and torch.cuda.is_available())
    cuda_name = "not_available"
    cuda_capability = "not_available"
    cuda_count = 0
    if cuda_available:
        try:
            cuda_count = int(torch.cuda.device_count())
            cuda_name = str(torch.cuda.get_device_name(0))
            cap = torch.cuda.get_device_capability(0)
            cuda_capability = f"{int(cap[0])}.{int(cap[1])}"
        except Exception as exc:
            cuda_name = f"unresolved:{exc!r}"
            cuda_capability = "unresolved"
    if not dtypes:
        dtypes.add(first_dtype)
    if not devices:
        devices.add(first_device)
    return {
        "runtime_provenance_contract": PUBLIC_RUNTIME_PROVENANCE_CONTRACT,
        "requested_torch_dtype": str(requested_torch_dtype),
        "resolved_torch_dtype": str(first_dtype),
        "requested_device_policy": str(requested_device_policy),
        "actual_primary_device": str(first_device),
        "model_parameter_dtype_set": sorted(dtypes),
        "model_device_set": sorted(devices),
        "model_parameter_tensor_count": int(param_count),
        "cuda_available": bool(cuda_available),
        "cuda_device_count": int(cuda_count),
        "cuda_device_name": cuda_name,
        "cuda_device_capability": cuda_capability,
        "timing_clock_contract": PUBLIC_TIMING_CLOCK_CONTRACT,
        "timing_cpu_perf_counter_recorded": True,
        "timing_cuda_synchronized": bool(synchronized_before_after_timing),
        "timing_cuda_event_recorded": False,
        "capture_elapsed_seconds": float(capture_elapsed_seconds),
        "named_hardware_timing_measured": False,
    }


def _runtime_provenance_semantics_verified(summary: dict[str, Any]) -> bool:
    try:
        return bool(
            summary.get("runtime_provenance_contract") == PUBLIC_RUNTIME_PROVENANCE_CONTRACT
            and str(summary.get("requested_torch_dtype")) in {"auto", "float32", "float16", "bfloat16"}
            and str(summary.get("resolved_torch_dtype", "")).strip()
            and str(summary.get("requested_device_policy")) in {"auto", "cpu", "cuda"}
            and str(summary.get("actual_primary_device", "")).strip()
            and isinstance(summary.get("model_parameter_dtype_set"), list)
            and len(summary.get("model_parameter_dtype_set") or []) >= 1
            and isinstance(summary.get("model_device_set"), list)
            and len(summary.get("model_device_set") or []) >= 1
            and summary.get("timing_clock_contract") == PUBLIC_TIMING_CLOCK_CONTRACT
            and summary.get("timing_cpu_perf_counter_recorded") is True
            and float(summary.get("capture_elapsed_seconds", 0.0)) >= 0.0
            and summary.get("named_hardware_timing_measured") is False
        )
    except Exception:
        return False


def _deterministic_generation_settings(tokenizer: Any, decode_steps: int, position_policy: str, cache_implementation: str = PUBLIC_REQUIRED_CACHE_IMPLEMENTATION) -> dict[str, Any]:
    """Canonical public replay settings for cached decode.

    HF generation treats `do_sample=False, num_beams=1` as greedy decoding and
    `do_sample=False, num_beams>1` as beam search.  Public cached-decode traces
    are intentionally restricted to single-sequence greedy replay so inherited
    model generation_config values cannot silently alter the token path.
    """
    eos_id = getattr(tokenizer, "eos_token_id", None)
    pad_id = getattr(tokenizer, "pad_token_id", None)
    effective_pad_id = eos_id if pad_id is None and eos_id is not None else pad_id
    cache_impl = str(cache_implementation or PUBLIC_REQUIRED_CACHE_IMPLEMENTATION)
    return {
        "contract": PUBLIC_GENERATION_DETERMINISM_CONTRACT,
        "cache_implementation_contract": PUBLIC_CACHE_IMPLEMENTATION_CONTRACT,
        "cache_implementation": cache_impl,
        "cache_implementation_source": "explicit_generate_argument",
        "cache_config": None,
        "strategy": "greedy",
        "do_sample": False,
        "num_beams": 1,
        "num_return_sequences": 1,
        "max_new_tokens": int(decode_steps),
        "min_new_tokens": int(decode_steps),
        "use_cache": bool(int(decode_steps) > 0),
        "sampling_disabled": True,
        "exact_new_token_count_required": True,
        "beam_search_disabled": True,
        "temperature_effective": "ignored_do_sample_false",
        "top_k_effective": "ignored_do_sample_false",
        "top_p_effective": "ignored_do_sample_false",
        "position_policy": str(position_policy),
        "pad_token_id": (None if effective_pad_id is None else int(effective_pad_id)),
        "eos_token_id_sha256": _token_id_digest(eos_id),
    }


def _generation_determinism_semantics_verified(settings: Any, decode_steps: int) -> bool:
    try:
        cfg = dict(settings)
        return bool(
            cfg.get("contract") == PUBLIC_GENERATION_DETERMINISM_CONTRACT
            and cfg.get("strategy") == "greedy"
            and cfg.get("do_sample") is False
            and int(cfg.get("num_beams")) == 1
            and int(cfg.get("num_return_sequences")) == 1
            and int(cfg.get("max_new_tokens")) == int(decode_steps)
            and int(cfg.get("min_new_tokens")) == int(decode_steps)
            and int(cfg.get("max_new_tokens")) > 0
            and cfg.get("use_cache") is True
            and cfg.get("cache_implementation_contract") == PUBLIC_CACHE_IMPLEMENTATION_CONTRACT
            and cfg.get("cache_implementation") == PUBLIC_REQUIRED_CACHE_IMPLEMENTATION
            and cfg.get("cache_implementation_source") == "explicit_generate_argument"
            and cfg.get("cache_config") is None
            and cfg.get("sampling_disabled") is True
            and cfg.get("beam_search_disabled") is True
            and cfg.get("exact_new_token_count_required") is True
        )
    except Exception:
        return False


def _is_hex_sha256_text(value: object) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(c in "0123456789abcdefABCDEF" for c in text)


def _token_provenance_semantics_verified(
    *,
    prompt_ids: Any,
    positions: Any,
    phases: Any,
    prompt_token_count: Any,
    prompt_input_ids_sha256: Any,
    prompt_attention_mask_sha256: Any,
    prompt_text_sha256: Any,
    decode_steps_requested: int,
) -> bool:
    """Verify row coordinates are replayable against exact tokenized prompts.

    Dense Q/K/V parity is not enough for a public trace.  A verifier also needs
    to know the exact tokenizer output that produced each prefill/decode row,
    without storing the prompt text itself in the NPZ.  This contract records
    SHA-256 digests of input_ids, attention_mask, and prompt text per prompt and
    verifies row positions sit on the correct side of the prompt/decode boundary.
    """
    try:
        pid = np.asarray(prompt_ids, dtype=np.int64).reshape(-1)
        pos = np.asarray(positions, dtype=np.int64).reshape(-1)
        phase_arr = np.asarray(phases).reshape(-1)
        counts = np.asarray(prompt_token_count, dtype=np.int64).reshape(-1)
        id_hashes = np.asarray(prompt_input_ids_sha256).astype(str).reshape(-1)
        mask_hashes = np.asarray(prompt_attention_mask_sha256).astype(str).reshape(-1)
        text_hashes = np.asarray(prompt_text_sha256).astype(str).reshape(-1)
        decode_steps = int(decode_steps_requested)
    except Exception:
        return False
    if not (pid.shape == pos.shape == phase_arr.shape):
        return False
    prompt_count = int(counts.size)
    if prompt_count <= 0 or id_hashes.size != prompt_count or mask_hashes.size != prompt_count or text_hashes.size != prompt_count:
        return False
    if np.any(counts <= 0):
        return False
    if not all(_is_hex_sha256_text(x) for x in list(id_hashes) + list(mask_hashes) + list(text_hashes)):
        return False
    seen_prefill = False
    seen_decode = False
    for row_prompt, row_pos, row_phase in zip(pid, pos, phase_arr):
        p_i, pos_i = int(row_prompt), int(row_pos)
        if p_i < 0 or p_i >= prompt_count or pos_i < 0:
            return False
        prompt_len = int(counts[p_i])
        phase_text = str(row_phase)
        if phase_text == "prefill":
            seen_prefill = True
            if pos_i >= prompt_len:
                return False
        elif phase_text == "decode_cached":
            seen_decode = True
            if decode_steps <= 0 or pos_i < prompt_len or pos_i >= prompt_len + decode_steps:
                return False
        else:
            return False
    return bool(seen_prefill and seen_decode)


def _generation_token_semantics_verified(
    *,
    prompt_ids: Any,
    positions: Any,
    phases: Any,
    prompt_token_count: Any,
    generated_sequence_sha256: Any,
    generated_new_token_ids_sha256: Any,
    generated_new_token_count: Any,
    generated_sequence_token_count: Any,
    generation_prompt_prefix_verified: Any,
    decode_steps_requested: int,
) -> bool:
    """Verify cached-decode rows are bound to the generated token stream.

    rev0088 bound rows to the prompt tokenizer output.  That still leaves a
    cached-decode false-green: after the first generated token, the KV cache is
    fed by model-selected token IDs, not only by the original prompt.  Dense
    Q/K/V parity can pass while the generated continuation is unrecorded.  This
    contract records per-prompt hashes of the full generated sequence and the
    new-token suffix, verifies the generated sequence preserves the prompt
    prefix, and checks decode rows lie inside the actually generated suffix.
    """
    try:
        pid = np.asarray(prompt_ids, dtype=np.int64).reshape(-1)
        pos = np.asarray(positions, dtype=np.int64).reshape(-1)
        phase_arr = np.asarray(phases).reshape(-1)
        prompt_counts = np.asarray(prompt_token_count, dtype=np.int64).reshape(-1)
        seq_hashes = np.asarray(generated_sequence_sha256).astype(str).reshape(-1)
        new_hashes = np.asarray(generated_new_token_ids_sha256).astype(str).reshape(-1)
        new_counts = np.asarray(generated_new_token_count, dtype=np.int64).reshape(-1)
        seq_counts = np.asarray(generated_sequence_token_count, dtype=np.int64).reshape(-1)
        prefix_ok = np.asarray(generation_prompt_prefix_verified, dtype=bool).reshape(-1)
        decode_steps = int(decode_steps_requested)
    except Exception:
        return False
    if not (pid.shape == pos.shape == phase_arr.shape):
        return False
    prompt_count = int(prompt_counts.size)
    if prompt_count <= 0:
        return False
    if not (seq_hashes.shape == new_hashes.shape == new_counts.shape == seq_counts.shape == prefix_ok.shape == (prompt_count,)):
        return False
    if decode_steps <= 0 or np.any(prompt_counts <= 0) or np.any(new_counts <= 0):
        return False
    if np.any(new_counts != decode_steps):
        return False
    if np.any(seq_counts != prompt_counts + new_counts):
        return False
    if not bool(np.all(prefix_ok)):
        return False
    if not all(_is_hex_sha256_text(x) for x in list(seq_hashes) + list(new_hashes)):
        return False
    seen_decode = False
    for row_prompt, row_pos, row_phase in zip(pid, pos, phase_arr):
        p_i, pos_i = int(row_prompt), int(row_pos)
        if p_i < 0 or p_i >= prompt_count or pos_i < 0:
            return False
        prompt_len = int(prompt_counts[p_i])
        gen_len = int(new_counts[p_i])
        phase_text = str(row_phase)
        if phase_text == "prefill":
            if pos_i >= prompt_len:
                return False
        elif phase_text == "decode_cached":
            seen_decode = True
            if pos_i < prompt_len or pos_i >= prompt_len + gen_len:
                return False
        else:
            return False
    return bool(seen_decode)



def _enforce_capture_network_quarantine(*, local_only: bool) -> dict[str, Any]:
    """Set evidence-capture offline controls before importing HF runtime.

    The public runner deliberately separates snapshot materialization (where
    downloads can be enabled after source/license review) from evidence capture
    (which must load the exact digest-verified local snapshot path). Hugging Face
    environment variables are read at import time, so this must run before
    importing transformers/huggingface_hub through _import_runtime().
    """
    controls = {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
        "HF_HUB_DISABLE_UPDATE_CHECK": "1",
    }
    already_imported = [name for name in ["huggingface_hub", "transformers"] if name in sys.modules]
    applied: dict[str, str] = {}
    if local_only:
        for key, value in controls.items():
            os.environ[key] = value
            applied[key] = value
    return {
        "contract": PUBLIC_CAPTURE_OFFLINE_QUARANTINE_CONTRACT,
        "local_only_capture": bool(local_only),
        "applied": applied,
        "controls": controls,
        "set_before_runtime_import": not already_imported,
        "hf_modules_already_imported_before_quarantine": already_imported,
        "boundary": "downloads belong to snapshot preparation; evidence capture loads the selected digest-verified local snapshot with local_files_only=True",
    }

def _import_runtime():
    try:
        import torch  # type: ignore
        import transformers  # type: ignore
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    except Exception as exc:  # pragma: no cover - optional runtime
        raise SystemExit(
            "Missing optional dependencies. Install torch and transformers, or run in an environment with a cached model. "
            f"Original import error: {exc}"
        )
    return torch, transformers, AutoModelForCausalLM, AutoTokenizer


def _get_config_int(config: Any, *names: str, default: int | None = None) -> int:
    for name in names:
        if hasattr(config, name):
            value = getattr(config, name)
            if value is not None:
                return int(value)
    if default is not None:
        return int(default)
    raise ValueError(f"model config missing one of {names}")


def _to_numpy(torch, tensor) -> np.ndarray:
    """Cast before NumPy conversion so BF16/FP8-like hook outputs do not fail."""
    return tensor.detach().to(dtype=torch.float32).cpu().numpy()


def _reshape_heads(x: np.ndarray, heads: int) -> np.ndarray:
    # x: [batch, seq, hidden]
    b, s, h = x.shape
    if h % heads != 0:
        raise ValueError(f"hidden size {h} not divisible by heads {heads}")
    return x.reshape(b, s, heads, h // heads)


def _capture_gpt2_style(torch, model, tokenizer, prompt: str, max_rows: int) -> dict[str, Any] | None:
    n_heads = _get_config_int(model.config, "n_head", "num_attention_heads")
    captured: dict[str, np.ndarray] = {}
    handles = []

    def make_hook(name: str):
        def hook(_module, _inp, out):
            captured[name] = _to_numpy(torch, out)
        return hook

    modules = [(name, mod) for name, mod in model.named_modules() if name.endswith("attn.c_attn")]
    if not modules:
        return None
    for name, mod in modules:
        handles.append(mod.register_forward_hook(make_hook(name)))
    try:
        toks = tokenizer(prompt, return_tensors="pt")
        toks = {k: v.to(model.device) for k, v in toks.items()}
        with torch.no_grad():
            model(**toks, use_cache=False)
    finally:
        for handle in handles:
            handle.remove()

    q_rows: list[np.ndarray] = []
    k_rows: list[np.ndarray] = []
    v_rows: list[np.ndarray] = []
    layers: list[int] = []
    heads: list[int] = []
    positions: list[int] = []
    regimes: list[str] = []
    kv_head_ids: list[int] = []
    for name, qkv in sorted(captured.items()):
        parts = np.split(qkv, 3, axis=-1)
        qh = _reshape_heads(parts[0], n_heads)[0]
        kh = _reshape_heads(parts[1], n_heads)[0]
        vh = _reshape_heads(parts[2], n_heads)[0]
        try:
            layer_id = int(name.split(".")[2]) if name.startswith("transformer.h.") else int([x for x in name.split(".") if x.isdigit()][-1])
        except Exception:
            layer_id = len(set(layers))
        pos = qh.shape[0] - 1
        for head_id in range(n_heads):
            q_rows.append(qh[pos, head_id].astype(np.float64))
            k_rows.append(kh[: pos + 1, head_id].astype(np.float64))
            v_rows.append(vh[: pos + 1, head_id].astype(np.float64))
            layers.append(layer_id)
            heads.append(head_id)
            kv_head_ids.append(head_id)
            positions.append(pos)
            regimes.append("hf_gpt2_projection_last_token")
            if len(q_rows) >= max_rows:
                break
        if len(q_rows) >= max_rows:
            break
    return {
        "rows": (q_rows, k_rows, v_rows, regimes, layers, heads, positions),
        "kv_head": np.asarray(kv_head_ids, dtype=np.int64),
        "num_attention_heads": np.full((len(q_rows),), int(n_heads), dtype=np.int64),
        "num_key_value_heads": np.full((len(q_rows),), int(n_heads), dtype=np.int64),
        "num_key_value_groups": np.ones((len(q_rows),), dtype=np.int64),
        "kv_group_map_contract": PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": _kv_group_semantics_verified(heads, kv_head_ids, n_heads, n_heads, 1),
        "gqa_grouped_rows_present": False,
        "adapter": "gpt2_fused_c_attn_projection_hook",
        "attention_score_input_stage": "projection_output_architecture_assumed_score_inputs",
        "attention_score_inputs_verified": False,
        "score_transform": PUBLIC_SCORE_TRANSFORM,
        "attention_scale_verified": False,
        "score_bias_verified": False,
        "dense_reference_verified": False,
        "dense_reference_max_abs_error": None,
        "fidelity_note": "Projection output was captured, but no model-output parity test was run. It remains diagnostic until a verified adapter compares post-transform Q/K attention against the model reference.",
    }


def _capture_qkv_projection_style(torch, model, tokenizer, prompt: str, max_rows: int) -> dict[str, Any] | None:
    n_heads = _get_config_int(model.config, "num_attention_heads", "n_head")
    n_kv_heads = _get_config_int(model.config, "num_key_value_heads", default=n_heads)
    stores: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    handles = []

    def hook_for(layer_name: str, kind: str):
        def hook(_module, _inp, out):
            stores[layer_name][kind] = _to_numpy(torch, out)
        return hook

    for name, mod in model.named_modules():
        if name.endswith("self_attn.q_proj"):
            base = name[: -len(".q_proj")]
            handles.append(mod.register_forward_hook(hook_for(base, "q")))
        elif name.endswith("self_attn.k_proj"):
            base = name[: -len(".k_proj")]
            handles.append(mod.register_forward_hook(hook_for(base, "k")))
        elif name.endswith("self_attn.v_proj"):
            base = name[: -len(".v_proj")]
            handles.append(mod.register_forward_hook(hook_for(base, "v")))
    if not handles:
        return None
    try:
        toks = tokenizer(prompt, return_tensors="pt")
        toks = {k: v.to(model.device) for k, v in toks.items()}
        with torch.no_grad():
            model(**toks, use_cache=False)
    finally:
        for handle in handles:
            handle.remove()

    q_rows: list[np.ndarray] = []
    k_rows: list[np.ndarray] = []
    v_rows: list[np.ndarray] = []
    layers: list[int] = []
    heads: list[int] = []
    positions: list[int] = []
    regimes: list[str] = []
    kv_head_ids: list[int] = []
    kv_groups = max(1, int(n_heads // max(1, n_kv_heads)))
    for base, parts in sorted(stores.items()):
        if not {"q", "k", "v"}.issubset(parts):
            continue
        qh = _reshape_heads(parts["q"], n_heads)[0]
        kh = _reshape_heads(parts["k"], n_kv_heads)[0]
        vh = _reshape_heads(parts["v"], n_kv_heads)[0]
        pos = qh.shape[0] - 1
        try:
            layer_id = int([x for x in base.split(".") if x.isdigit()][-1])
        except Exception:
            layer_id = len(set(layers))
        for head_id in range(n_heads):
            kv_head = min(n_kv_heads - 1, int(head_id // max(1, kv_groups)))
            q_rows.append(qh[pos, head_id].astype(np.float64))
            k_rows.append(kh[: pos + 1, kv_head].astype(np.float64))
            v_rows.append(vh[: pos + 1, kv_head].astype(np.float64))
            layers.append(layer_id)
            heads.append(head_id)
            kv_head_ids.append(kv_head)
            positions.append(pos)
            regimes.append("hf_raw_qkv_projection_last_token")
            if len(q_rows) >= max_rows:
                break
        if len(q_rows) >= max_rows:
            break
    return {
        "rows": (q_rows, k_rows, v_rows, regimes, layers, heads, positions),
        "kv_head": np.asarray(kv_head_ids, dtype=np.int64),
        "num_attention_heads": np.full((len(q_rows),), int(n_heads), dtype=np.int64),
        "num_key_value_heads": np.full((len(q_rows),), int(n_kv_heads), dtype=np.int64),
        "num_key_value_groups": np.full((len(q_rows),), int(kv_groups), dtype=np.int64),
        "kv_group_map_contract": PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": _kv_group_semantics_verified(heads, kv_head_ids, n_heads, n_kv_heads, kv_groups),
        "gqa_grouped_rows_present": bool(kv_groups > 1 and len(q_rows) > 0),
        "adapter": "qkv_projection_modules_raw",
        "attention_score_input_stage": "raw_projection_pre_attention_transforms",
        "attention_score_inputs_verified": False,
        "score_transform": PUBLIC_SCORE_TRANSFORM,
        "attention_scale_verified": False,
        "score_bias_verified": False,
        "dense_reference_verified": False,
        "dense_reference_max_abs_error": None,
        "fidelity_note": "q_proj/k_proj/v_proj hooks fire before architecture-specific Q/K transforms such as rotary embeddings. This adapter is diagnostic and is never self-attested as public score-input evidence.",
    }


def _softmax_np(scores: np.ndarray) -> np.ndarray:
    """Mirror the public Llama eager probability path: float32 softmax, no dropout.

    Current Transformers Llama eager attention computes probabilities with
    ``nn.functional.softmax(..., dtype=torch.float32)`` and then applies
    dropout.  The capture path runs ``model.eval()``, so dropout must be zero
    and this replay deliberately uses float32 probability normalization rather
    than an accidental float64 NumPy replay.
    """
    scores32 = np.asarray(scores, dtype=np.float32)
    shifted = scores32 - np.max(scores32)
    weights = np.exp(shifted).astype(np.float32)
    denom = np.sum(weights, dtype=np.float32)
    if not math.isfinite(float(denom)) or float(denom) <= 0.0:
        raise ValueError("invalid softmax denominator while reconstructing dense reference")
    return (weights / denom).astype(np.float64)


def _select_query_positions(q_len: int, policy: str) -> list[int]:
    if q_len <= 0:
        return []
    if policy == "last_token_only":
        return [q_len - 1]
    if policy == "last_and_mid":
        return sorted({max(0, q_len // 2), q_len - 1})
    if policy == "all_tokens":
        return list(range(q_len))
    raise ValueError(f"unknown position policy: {policy}")


def _attention_bias_row(mask: np.ndarray | None, *, batch: int, head: int, query_pos: int, key_len: int) -> tuple[np.ndarray, bool, bool]:
    """Extract one additive attention-bias row from HF mask layouts.

    Public traces need the exact score rule, not just Q/K/V.  HF causal masks are
    usually [batch, 1|heads, q_len, kv_len], but this helper also accepts common
    2-D/3-D variants so the capture helper fails less often.  Negative infinity
    is a normal causal-mask representation, so rev0081 converts it to a finite
    sentinel that is numerically equivalent under softmax in float64.  NaN and
    positive infinity still fail the mask verification contract.
    """
    if mask is None:
        return np.zeros((key_len,), dtype=np.float64), True, False
    arr = np.asarray(mask, dtype=np.float64)
    if arr.ndim == 4:
        b = min(batch, arr.shape[0] - 1)
        h = 0 if arr.shape[1] == 1 else min(head, arr.shape[1] - 1)
        q = min(query_pos, arr.shape[2] - 1)
        row = arr[b, h, q, :key_len]
    elif arr.ndim == 3:
        b = min(batch, arr.shape[0] - 1)
        q = min(query_pos, arr.shape[1] - 1)
        row = arr[b, q, :key_len]
    elif arr.ndim == 2:
        if arr.shape[0] == 1:
            row = arr[0, :key_len]
        elif arr.shape[0] > query_pos and arr.shape[1] >= key_len:
            row = arr[query_pos, :key_len]
        else:
            row = arr[min(batch, arr.shape[0] - 1), :key_len]
    elif arr.ndim == 1:
        row = arr[:key_len]
    else:
        raise ValueError(f"unsupported attention mask rank {arr.ndim}")
    if row.shape[0] != key_len:
        padded = np.zeros((key_len,), dtype=np.float64)
        padded[: min(key_len, row.shape[0])] = row[:key_len]
        row = padded
    row = np.asarray(row, dtype=np.float64)
    invalid = bool(np.any(np.isnan(row)) or np.any(np.isposinf(row)))
    had_negative_infinity = bool(np.any(np.isneginf(row)))
    if had_negative_infinity:
        row = np.where(np.isneginf(row), PUBLIC_MASK_SENTINEL, row)
    serializable = bool((not invalid) and np.all(np.isfinite(row)))
    masked_bias_seen = bool(np.any(row < -1.0e20) or np.any(np.abs(row) > 0.0))
    return row.astype(np.float64), serializable, masked_bias_seen


def _rows_from_attention_capture(
    *,
    q: np.ndarray,
    k: np.ndarray,
    v: np.ndarray,
    out: np.ndarray,
    attention_mask: np.ndarray | None,
    scaling: float,
    layer_id: int,
    prompt_index: int,
    position_policy: str,
    max_remaining: int,
    num_key_value_groups: int,
    capture_phase: str = "prefill",
    query_start_position: int | None = None,
    attention_dropout_p: float = 0.0,
    attention_training_state: bool = False,
    attention_probability_dtype: str = PUBLIC_ATTENTION_PROBABILITY_DTYPE,
    rotary_position_ids: Any | None = None,
    rotary_position_out: list[int] | None = None,
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray], list[np.ndarray], list[np.ndarray], list[np.ndarray], list[str], list[int], list[int], list[int], list[int], list[str], list[int], list[int], bool, bool, float]:
    """Convert one eager-attention call into trace rows.

    rev0082 keeps the fixed-context NPZ surface but no longer forces every row
    to have the same live KV length.  Prefill and cached-decode calls are both
    admissible: the writer pads shorter K/V rows and masks their padded tail
    with PUBLIC_MASK_SENTINEL.  The returned per-row valid_key_len is the
    physical exported KV width, and active_key_len is later derived from the
    runtime mask as the contiguous prefix that actually participates in the
    score.  This distinction matters because current cache implementations may
    preallocate or retain masked tokens that dense parity should ignore.
    """
    if q.ndim != 4 or k.ndim != 4 or v.ndim != 4 or out.ndim != 4:
        raise ValueError(f"expected q/k/v/out ranks [B,H,Q,D]/[B,Q,H,Dv], got q={q.shape} k={k.shape} v={v.shape} out={out.shape}")
    batch, n_heads, q_len, d_head = q.shape
    if k.shape[0] != batch or v.shape[0] != batch or out.shape[0] != batch or out.shape[1] != q_len or out.shape[2] != n_heads:
        raise ValueError(f"attention capture shape mismatch: q={q.shape} k={k.shape} v={v.shape} out={out.shape}")
    if not math.isfinite(float(scaling)) or float(scaling) <= 0.0:
        raise ValueError(f"attention scaling must be finite positive, got {scaling}")
    if str(attention_probability_dtype) != PUBLIC_ATTENTION_PROBABILITY_DTYPE:
        raise ValueError(f"unsupported attention probability dtype {attention_probability_dtype!r}; expected {PUBLIC_ATTENTION_PROBABILITY_DTYPE}")
    if bool(attention_training_state) or abs(float(attention_dropout_p or 0.0)) > 1e-12:
        raise ValueError("public trace capture requires eval-mode attention with zero dropout")
    kv_heads = k.shape[1]
    if kv_heads <= 0 or n_heads <= 0:
        raise ValueError("attention capture has no heads")
    groups = max(1, int(num_key_value_groups) or max(1, n_heads // kv_heads))
    q_rows: list[np.ndarray] = []
    k_rows: list[np.ndarray] = []
    v_rows: list[np.ndarray] = []
    scales: list[np.ndarray] = []
    biases: list[np.ndarray] = []
    refs: list[np.ndarray] = []
    regimes: list[str] = []
    layers: list[int] = []
    heads: list[int] = []
    positions: list[int] = []
    prompt_ids: list[int] = []
    phases: list[str] = []
    valid_key_lens: list[int] = []
    query_lens: list[int] = []
    kv_head_ids: list[int] = []
    num_attention_heads_rows: list[int] = []
    num_key_value_heads_rows: list[int] = []
    num_key_value_groups_rows: list[int] = []
    rotary_position_rows: list[int] = []
    all_bias_serializable = True
    mask_challenge_seen = False
    max_err = 0.0
    key_len = int(k.shape[2])
    phase = str(capture_phase or "prefill")
    if query_start_position is None:
        query_start_position = max(0, key_len - q_len) if phase == "decode_cached" else 0
    query_start_position = int(query_start_position)
    if query_start_position < 0:
        raise ValueError(f"query_start_position must be non-negative, got {query_start_position}")
    rotary_ids_arr = None
    if rotary_position_ids is not None:
        rotary_ids_arr = np.asarray(rotary_position_ids, dtype=np.int64)
        if rotary_ids_arr.ndim == 1:
            if rotary_ids_arr.shape[0] != q_len:
                raise ValueError(f"rotary_position_ids rank-1 length {rotary_ids_arr.shape[0]} does not match q_len {q_len}")
            rotary_ids_arr = np.broadcast_to(rotary_ids_arr.reshape(1, q_len), (batch, q_len))
        elif rotary_ids_arr.ndim == 2:
            if rotary_ids_arr.shape[1] != q_len:
                raise ValueError(f"rotary_position_ids rank-2 shape {rotary_ids_arr.shape} does not match q_len {q_len}")
            if rotary_ids_arr.shape[0] == 1 and batch > 1:
                rotary_ids_arr = np.broadcast_to(rotary_ids_arr, (batch, q_len))
            elif rotary_ids_arr.shape[0] != batch:
                raise ValueError(f"rotary_position_ids batch {rotary_ids_arr.shape[0]} does not match batch {batch}")
        else:
            raise ValueError(f"rotary_position_ids must be rank 1 or 2, got {rotary_ids_arr.shape}")
    for b in range(batch):
        for pos in _select_query_positions(q_len, position_policy):
            for head_id in range(n_heads):
                if len(q_rows) >= max_remaining:
                    return q_rows, k_rows, v_rows, scales, biases, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, all_bias_serializable, mask_challenge_seen, max_err
                kv_head = min(kv_heads - 1, head_id // groups)
                q_row = q[b, head_id, pos].astype(np.float64)
                k_row = k[b, kv_head, :key_len].astype(np.float64)
                v_row = v[b, kv_head, :key_len].astype(np.float64)
                bias_row, bias_serializable, masked_bias_seen = _attention_bias_row(attention_mask, batch=b, head=head_id, query_pos=pos, key_len=key_len)
                all_bias_serializable = all_bias_serializable and bias_serializable
                mask_challenge_seen = mask_challenge_seen or masked_bias_seen
                scores = (k_row @ q_row) * float(scaling) + bias_row
                probs = _softmax_np(scores)
                reconstructed = probs @ v_row
                model_reference = out[b, pos, head_id].astype(np.float64)
                row_err = float(np.max(np.abs(reconstructed - model_reference)))
                max_err = max(max_err, row_err)
                q_rows.append(q_row)
                k_rows.append(k_row)
                v_rows.append(v_row)
                scales.append(np.asarray([float(scaling)], dtype=np.float64))
                biases.append(bias_row)
                refs.append(model_reference)
                active_len = int(_active_key_lengths_from_bias(bias_row.reshape(1, -1), np.asarray([key_len], dtype=np.int64))[0])
                if phase == "decode_cached":
                    absolute_position = int(active_len - q_len + pos)
                else:
                    absolute_position = int(query_start_position + pos)
                if absolute_position < 0 or absolute_position >= max(1, active_len):
                    raise ValueError(f"absolute position {absolute_position} outside active KV length {active_len} for phase={phase}")
                regimes.append(f"hf_llama_eager_{phase}_post_transform_attention_row")
                layers.append(int(layer_id))
                heads.append(int(head_id))
                positions.append(absolute_position)
                if rotary_position_out is not None:
                    if rotary_ids_arr is not None:
                        rotary_position_out.append(int(rotary_ids_arr[b, pos]))
                    else:
                        rotary_position_out.append(int(query_start_position + pos))
                prompt_ids.append(int(prompt_index))
                phases.append(phase)
                valid_key_lens.append(int(key_len))
                query_lens.append(int(q_len))
    return q_rows, k_rows, v_rows, scales, biases, refs, regimes, layers, heads, positions, prompt_ids, phases, valid_key_lens, query_lens, all_bias_serializable, mask_challenge_seen, max_err


def _pad_2d_rows(rows: list[np.ndarray], *, width: int, fill: float = 0.0) -> np.ndarray:
    if not rows:
        return np.zeros((0, width), dtype=np.float64)
    out = np.full((len(rows), width), fill, dtype=np.float64)
    for i, row in enumerate(rows):
        arr = np.asarray(row, dtype=np.float64).reshape(-1)
        if arr.shape[0] > width:
            raise ValueError(f"row {i} length {arr.shape[0]} exceeds target width {width}")
        out[i, : arr.shape[0]] = arr
    return out


def _pad_3d_rows(rows: list[np.ndarray], *, width: int) -> np.ndarray:
    if not rows:
        return np.zeros((0, width, 0), dtype=np.float64)
    d = int(np.asarray(rows[0]).shape[-1])
    out = np.zeros((len(rows), width, d), dtype=np.float64)
    for i, row in enumerate(rows):
        arr = np.asarray(row, dtype=np.float64)
        if arr.ndim != 2:
            raise ValueError(f"row {i} expected rank-2 [n,d], got {arr.shape}")
        if arr.shape[1] != d:
            raise ValueError(f"row {i} dimension {arr.shape[1]} does not match first dimension {d}")
        if arr.shape[0] > width:
            raise ValueError(f"row {i} length {arr.shape[0]} exceeds target width {width}")
        out[i, : arr.shape[0], :] = arr
    return out


def _valid_key_lengths_from_rows(k_rows: list[np.ndarray]) -> np.ndarray:
    return np.asarray([int(np.asarray(row).shape[0]) for row in k_rows], dtype=np.int64)


def _valid_key_len_padding_verified(score_bias: np.ndarray, valid_key_len: np.ndarray) -> bool:
    if score_bias.ndim != 2 or valid_key_len.ndim != 1 or score_bias.shape[0] != valid_key_len.shape[0]:
        return False
    n = int(score_bias.shape[1])
    for i, live in enumerate(valid_key_len.astype(np.int64)):
        if live <= 0 or live > n:
            return False
        if live < n and not np.all(score_bias[i, int(live):] < -1.0e20):
            return False
    return bool(np.all(np.isfinite(score_bias)))


def _active_key_lengths_from_bias(score_bias: np.ndarray, valid_key_len: np.ndarray) -> np.ndarray:
    """Infer the scored KV prefix from the serialized additive mask.

    Dense parity alone cannot distinguish active cache tokens from masked static
    or causal-tail storage.  Public trace rows therefore carry active_key_len as
    the contiguous prefix that is not masked by the finite negative sentinel.
    Non-prefix masks are represented by the first masked index and rejected by
    _active_key_len_semantics_verified; this keeps the accepted public schema
    conservative and cost-accountable.
    """
    bias = np.asarray(score_bias, dtype=np.float64)
    live = np.asarray(valid_key_len, dtype=np.int64).reshape(-1)
    if bias.ndim != 2 or live.shape != (bias.shape[0],):
        raise ValueError("score_bias must be [rows,n] and valid_key_len must be [rows]")
    active = np.zeros((bias.shape[0],), dtype=np.int64)
    for i, live_i in enumerate(live):
        li = int(live_i)
        if li <= 0 or li > bias.shape[1]:
            active[i] = 0
            continue
        masked = bias[i, :li] < -1.0e20
        if np.any(masked):
            active[i] = int(np.argmax(masked))
        else:
            active[i] = li
    return active


def _active_key_len_semantics_verified(score_bias: np.ndarray, valid_key_len: np.ndarray, active_key_len: np.ndarray) -> bool:
    bias = np.asarray(score_bias, dtype=np.float64)
    live = np.asarray(valid_key_len, dtype=np.int64).reshape(-1)
    active = np.asarray(active_key_len, dtype=np.int64).reshape(-1)
    if bias.ndim != 2 or not (live.shape == active.shape == (bias.shape[0],)):
        return False
    if not np.all(np.isfinite(bias)):
        return False
    n = int(bias.shape[1])
    masked_row_seen = False
    for i, (live_i, active_i) in enumerate(zip(live, active)):
        li, ai = int(live_i), int(active_i)
        if li <= 0 or li > n or ai <= 0 or ai > li:
            return False
        if ai < li:
            masked_row_seen = True
            if not np.all(bias[i, ai:li] < -1.0e20):
                return False
        if li < n and not np.all(bias[i, li:] < -1.0e20):
            return False
    return bool(masked_row_seen)


def _absolute_position_semantics_verified(
    positions: np.ndarray,
    valid_key_len: np.ndarray,
    query_len: np.ndarray,
    phases: list[str] | np.ndarray,
    active_key_len: np.ndarray | None = None,
) -> bool:
    positions = np.asarray(positions, dtype=np.int64).reshape(-1)
    valid_key_len = np.asarray(valid_key_len, dtype=np.int64).reshape(-1)
    query_len = np.asarray(query_len, dtype=np.int64).reshape(-1)
    active = valid_key_len if active_key_len is None else np.asarray(active_key_len, dtype=np.int64).reshape(-1)
    phase_arr = np.asarray(phases).reshape(-1)
    if not (positions.shape == valid_key_len.shape == query_len.shape == active.shape == phase_arr.shape):
        return False
    if positions.size == 0:
        return False
    for pos, live, q_len, active_len, phase in zip(positions, valid_key_len, query_len, active, phase_arr):
        pos_i, live_i, q_i, active_i = int(pos), int(live), int(q_len), int(active_len)
        if live_i <= 0 or active_i <= 0 or active_i > live_i or q_i <= 0 or pos_i < 0 or pos_i >= active_i:
            return False
        phase_text = str(phase)
        if phase_text == "decode_cached":
            # For generation decode rows, the exported query position must be the
            # absolute position inside the active scored KV prefix, not the
            # local q_len=1 index and not the physical static-cache width.
            if q_i != 1 or pos_i != active_i - 1:
                return False
        elif phase_text == "prefill":
            # In a causal prefill row with prefix masks, active tokens are the
            # exact prefix through the selected query position.
            if pos_i >= q_i or active_i != pos_i + 1 or live_i < q_i:
                return False
        else:
            return False
    return True




def _rotary_position_semantics_verified(
    rotary_position_id: np.ndarray,
    active_position: np.ndarray,
    query_len: np.ndarray,
    phases: list[str] | np.ndarray,
) -> bool:
    """Verify that runtime RoPE position_ids are not confused with local row ids.

    The public selector/cost trace keeps `position` as the active-cache row
    position.  Hugging Face Llama applies RoPE from runtime `position_ids`,
    which can be a larger global decode position when a cache/window is already
    populated.  Dense parity can still pass if a bundle relabels this as local
    position 0, so public rows carry both fields.
    """
    rope = np.asarray(rotary_position_id, dtype=np.int64).reshape(-1)
    active = np.asarray(active_position, dtype=np.int64).reshape(-1)
    q_len_arr = np.asarray(query_len, dtype=np.int64).reshape(-1)
    phase_arr = np.asarray(phases).reshape(-1)
    if not (rope.shape == active.shape == q_len_arr.shape == phase_arr.shape):
        return False
    if rope.size == 0:
        return False
    decode_rows = 0
    prefill_rows = 0
    for rid, pos, q_len, phase in zip(rope, active, q_len_arr, phase_arr):
        rid_i, pos_i, q_i = int(rid), int(pos), int(q_len)
        if rid_i < 0 or pos_i < 0 or q_i <= 0:
            return False
        phase_text = str(phase)
        if phase_text == "prefill":
            prefill_rows += 1
            # Default Llama forward derives prefill position_ids as arange from
            # zero when no cache is present.  This fixture/capture lane does not
            # accept custom shifted prefill ids for public claims.
            if rid_i != pos_i:
                return False
        elif phase_text == "decode_cached":
            decode_rows += 1
            # In decode, q_len is one and RoPE position_ids must be the global
            # runtime token position, never the local q_len=1 index.  It may be
            # equal to the active-cache position for ordinary dynamic cache, or
            # larger for sliding/static cache windows.
            if q_i != 1 or rid_i < pos_i:
                return False
        else:
            return False
    return bool(prefill_rows > 0 and decode_rows > 0)


def _broadcast_int_rows(value: Any, rows: int, *, default: int | None = None) -> np.ndarray:
    if value is None:
        if default is None:
            raise ValueError("missing integer row metadata")
        return np.full((rows,), int(default), dtype=np.int64)
    arr = np.asarray(value, dtype=np.int64).reshape(-1)
    if arr.size == 1:
        return np.repeat(arr, rows).astype(np.int64)
    if arr.size != rows:
        raise ValueError(f"expected scalar or {rows} integer metadata values, got {arr.size}")
    return arr.astype(np.int64)


def _kv_group_semantics_verified(
    heads: Any,
    kv_heads: Any,
    num_attention_heads: Any,
    num_key_value_heads: Any,
    num_key_value_groups: Any,
) -> bool:
    """Verify query-head to KV-head ownership for MHA/GQA/MQA rows.

    Llama-family eager attention receives K/V in compact KV-head form and
    expands or logically broadcasts them to query heads at score time.  Dense
    parity can pass even when a trace forgets this sharing relation, which then
    corrupts cache-cost accounting by treating repeated KV rows as independent
    storage.  Public rows therefore need an explicit, checkable query->KV map.
    """
    try:
        head_arr = np.asarray(heads, dtype=np.int64).reshape(-1)
        rows = int(head_arr.size)
        if rows <= 0:
            return False
        kv_arr = _broadcast_int_rows(kv_heads, rows)
        qh_arr = _broadcast_int_rows(num_attention_heads, rows)
        kvh_arr = _broadcast_int_rows(num_key_value_heads, rows)
        group_arr = _broadcast_int_rows(num_key_value_groups, rows)
    except Exception:
        return False
    for head, kv_head, q_heads, kv_count, groups in zip(head_arr, kv_arr, qh_arr, kvh_arr, group_arr):
        h, kh, qn, kvn, g = int(head), int(kv_head), int(q_heads), int(kv_count), int(groups)
        if qn <= 0 or kvn <= 0 or g <= 0:
            return False
        if qn != kvn * g:
            return False
        if h < 0 or h >= qn or kh < 0 or kh >= kvn:
            return False
        if kh != h // g:
            return False
    return True


def _gqa_grouped_rows_present(num_key_value_groups: Any, rows: int) -> bool:
    try:
        group_arr = _broadcast_int_rows(num_key_value_groups, rows)
        return bool(np.any(group_arr > 1))
    except Exception:
        return False


def _set_model_attn_impl(model: Any, value: object) -> None:
    if not hasattr(model, "config"):
        return
    try:
        if value is None:
            return
        model.config._attn_implementation = value
    except Exception:
        return


def _registry_lookup(registry: Any, key: str, missing: Any) -> Any:
    for getter in (
        lambda: registry[key],
        lambda: getattr(registry, "_global_mapping", {}).get(key, missing),
        lambda: getattr(registry, "_local_mapping", {}).get(key, missing),
    ):
        try:
            value = getter()
            if value is not missing:
                return value
        except Exception:
            pass
    return missing


def _registry_set(registry: Any, key: str, value: Any) -> bool:
    for setter in (
        lambda: registry.register(key, value),
        lambda: registry.__setitem__(key, value),
    ):
        try:
            setter()
            return True
        except Exception:
            pass
    for attr in ("_global_mapping", "_local_mapping"):
        mapping = getattr(registry, attr, None)
        if isinstance(mapping, dict):
            mapping[key] = value
            return True
    return False


def _registry_restore(registry: Any, key: str, previous: Any, missing: Any) -> None:
    if previous is missing:
        for deleter in (
            lambda: registry.__delitem__(key),
            lambda: getattr(registry, "_global_mapping", {}).pop(key, None),
            lambda: getattr(registry, "_local_mapping", {}).pop(key, None),
        ):
            try:
                deleter()
            except Exception:
                pass
        return
    _registry_set(registry, key, previous)


def _install_llama_attention_capture_wrapper(llama_mod: Any, model: Any, wrapped_eager: Any) -> tuple[Any, dict[str, Any]]:
    """Install a capture wrapper without dropping the active attention mask.

    Hugging Face's current Llama path calls
    `ALL_ATTENTION_FUNCTIONS.get_interface(config._attn_implementation,
    eager_attention_forward)` after RoPE.  rev0080 used a new registry key, but
    Transformers documents that custom attention backends must also be registered
    with AttentionMaskInterface or mask creation can be skipped.  rev0081 avoids
    that failure mode by temporarily overriding the existing `eager` registry key
    and setting the model to `eager`, preserving the built-in eager mask backend.
    The module-level eager fallback is still patched for older releases.
    """
    backend_name = "eager"
    missing = object()
    original_eager = getattr(llama_mod, "eager_attention_forward", None)
    original_impl = getattr(getattr(model, "config", None), "_attn_implementation", None)
    registry = getattr(llama_mod, "ALL_ATTENTION_FUNCTIONS", None)
    previous_backend = _registry_lookup(registry, backend_name, missing) if registry is not None else missing
    registry_installed = False
    registry_error = None
    try:
        llama_mod.eager_attention_forward = wrapped_eager
    except Exception as exc:
        registry_error = f"module_patch_failed:{exc!r}"
    if registry is not None:
        try:
            registry_installed = _registry_set(registry, backend_name, wrapped_eager)
        except Exception as exc:
            registry_installed = False
            registry_error = f"eager_registry_override_failed:{exc!r}"
    _set_model_attn_impl(model, backend_name)

    def restore() -> None:
        if registry is not None and registry_installed:
            _registry_restore(registry, backend_name, previous_backend, missing)
        if original_eager is not None:
            try:
                llama_mod.eager_attention_forward = original_eager
            except Exception:
                pass
        if original_impl is not None:
            _set_model_attn_impl(model, original_impl)

    return restore, {
        "backend_name": backend_name,
        "registry_present": bool(registry is not None),
        "eager_registry_overridden": bool(registry_installed),
        "attention_mask_backend_preserved": True,
        "custom_attention_backend_used": False,
        "module_patch_installed": bool(getattr(llama_mod, "eager_attention_forward", None) is wrapped_eager),
        "previous_attention_implementation": str(original_impl),
        "install_error": registry_error,
    }


def _capture_llama_eager_post_transform_style(torch, model, tokenizer, prompts: list[str], max_rows: int, position_policy: str, decode_steps: int = 0, cache_implementation: str = PUBLIC_REQUIRED_CACHE_IMPLEMENTATION) -> dict[str, Any] | None:
    """Capture verified post-RoPE Llama-family attention rows via eager attention.

    rev0082 moves this from a prefill-only diagnostic bridge to a phase-aware
    capture path.  With --decode-steps > 0 it executes the HF generation path
    with `use_cache=True`, so the trace includes both prompt prefill rows and
    q_len=1 cached-decode rows.  Public self-attestation now requires that
    cached-decode phase coverage and the fixed-context padding/mask semantics
    survive the gate.
    """
    try:  # optional dependency path; import lazily for offline environments
        from transformers.models.llama import modeling_llama as llama_mod  # type: ignore
    except Exception:
        return None
    if not any(mod.__class__.__name__ == "LlamaAttention" for _name, mod in model.named_modules()):
        return None
    original_eager = getattr(llama_mod, "eager_attention_forward", None)
    if original_eager is None:
        return None

    captures: list[dict[str, Any]] = []
    token_records: list[dict[str, Any]] = []
    generation_records: list[dict[str, Any]] = []
    generation_settings = _deterministic_generation_settings(tokenizer, int(decode_steps), position_policy, cache_implementation)
    generation_config_json = _json_canonical_text(generation_settings)
    generation_config_sha256 = sha256_text(generation_config_json)
    generation_determinism_verified = _generation_determinism_semantics_verified(generation_settings, int(decode_steps))
    tokenization_settings = _tokenization_settings(tokenizer)
    tokenization_settings_json = _json_canonical_text(tokenization_settings)
    tokenization_settings_sha256 = sha256_text(tokenization_settings_json)
    current_prompt = {"index": 0}

    def wrapped_eager(module, query, key, value, attention_mask, scaling, dropout=0.0, **kwargs):
        attn_output, attn_weights = original_eager(module, query, key, value, attention_mask, scaling, dropout=dropout, **kwargs)
        q_len = int(query.shape[-2])
        key_len = int(key.shape[-2])
        phase = "decode_cached" if int(decode_steps) > 0 and q_len == 1 and key_len > 1 else "prefill"
        position_ids = kwargs.get("position_ids")
        rotary_position_ids = None
        query_start_position = None
        if position_ids is not None:
            try:
                pos_np = _to_numpy(torch, position_ids).astype(np.int64)
                if pos_np.ndim == 1:
                    pos_np = pos_np.reshape(1, -1)
                if pos_np.size:
                    rotary_position_ids = pos_np
                    query_start_position = int(pos_np.reshape(-1)[0])
            except Exception:
                rotary_position_ids = None
                query_start_position = None
        cache_position = kwargs.get("cache_position")
        if query_start_position is None and cache_position is not None:
            try:
                cache_pos_np = _to_numpy(torch, cache_position).reshape(-1)
                if cache_pos_np.size:
                    query_start_position = int(cache_pos_np[0])
            except Exception:
                query_start_position = None
        if query_start_position is None:
            query_start_position = max(0, key_len - q_len) if phase == "decode_cached" else 0
        captures.append({
            "prompt_index": int(current_prompt["index"]),
            "layer_idx": int(getattr(module, "layer_idx", -1)),
            "num_key_value_groups": int(getattr(module, "num_key_value_groups", 1)),
            "query": _to_numpy(torch, query),
            "key": _to_numpy(torch, key),
            "value": _to_numpy(torch, value),
            "attention_mask": (_to_numpy(torch, attention_mask) if attention_mask is not None else None),
            "attention_mask_present": bool(attention_mask is not None),
            "scaling": float(scaling),
            "dropout": float(dropout or 0.0),
            "attention_training_state": bool(getattr(module, "training", False)),
            "attention_probability_dtype": PUBLIC_ATTENTION_PROBABILITY_DTYPE,
            "dropout_applied": bool(getattr(module, "training", False) and float(dropout or 0.0) > 0.0),
            "attn_output": _to_numpy(torch, attn_output),
            "q_len": q_len,
            "key_len": key_len,
            "query_start_position": int(query_start_position),
            "rotary_position_ids": rotary_position_ids,
            "rotary_position_ids_present": bool(rotary_position_ids is not None),
            "capture_phase": phase,
        })
        return attn_output, attn_weights

    restore_attention, install_status = _install_llama_attention_capture_wrapper(llama_mod, model, wrapped_eager)
    try:
        for prompt_index, prompt in enumerate(prompts):
            current_prompt["index"] = prompt_index
            raw_toks = tokenizer(prompt, return_tensors="pt", add_special_tokens=True, padding=False, truncation=False, return_attention_mask=True)
            if "input_ids" not in raw_toks:
                raise ValueError("tokenizer did not return input_ids; cannot record public token provenance")
            input_ids_np = _to_numpy(torch, raw_toks["input_ids"]).astype(np.int64)
            mask_supplied = "attention_mask" in raw_toks
            if mask_supplied:
                attention_mask_np = _to_numpy(torch, raw_toks["attention_mask"]).astype(np.int64)
            else:
                attention_mask_np = np.ones_like(input_ids_np, dtype=np.int64)
            token_records.append({
                "prompt_index": int(prompt_index),
                "prompt_text_sha256": sha256_text(str(prompt)),
                "input_ids_sha256": sha256_int_array(input_ids_np),
                "attention_mask_sha256": sha256_int_array(attention_mask_np),
                "token_count": int(input_ids_np.shape[-1]),
                "attention_mask_sum": int(np.sum(attention_mask_np)),
                "attention_mask_supplied_by_tokenizer": bool(mask_supplied),
            })
            toks = {k: v.to(model.device) for k, v in raw_toks.items()}
            with torch.no_grad():
                if int(decode_steps) > 0:
                    generate_kwargs: dict[str, Any] = dict(toks)
                    eos_id = getattr(tokenizer, "eos_token_id", None)
                    pad_id = getattr(tokenizer, "pad_token_id", None)
                    if generation_settings.get("pad_token_id") is not None:
                        generate_kwargs["pad_token_id"] = int(generation_settings["pad_token_id"])
                    elif pad_id is None and eos_id is not None:
                        generate_kwargs["pad_token_id"] = eos_id
                    generated = model.generate(
                        **generate_kwargs,
                        do_sample=False,
                        num_beams=1,
                        num_return_sequences=1,
                        max_new_tokens=int(decode_steps),
                        min_new_tokens=int(decode_steps),
                        use_cache=True,
                        cache_implementation=str(generation_settings["cache_implementation"]),
                    )
                    sequences = getattr(generated, "sequences", generated)
                    sequence_np = _to_numpy(torch, sequences).astype(np.int64)
                    prompt_len = int(input_ids_np.shape[-1])
                    if sequence_np.ndim == 1:
                        sequence_np = sequence_np.reshape(1, -1)
                    prefix_ok = bool(sequence_np.shape[-1] >= prompt_len and np.array_equal(sequence_np[:, :prompt_len], input_ids_np))
                    generated_new = sequence_np[:, prompt_len:] if sequence_np.shape[-1] >= prompt_len else np.zeros((sequence_np.shape[0], 0), dtype=np.int64)
                    generation_records.append({
                        "prompt_index": int(prompt_index),
                        "generated_sequence_sha256": sha256_int_array(sequence_np),
                        "generated_new_token_ids_sha256": sha256_int_array(generated_new),
                        "generated_new_token_count": int(generated_new.shape[-1]),
                        "generated_sequence_token_count": int(sequence_np.shape[-1]),
                        "generation_prompt_prefix_verified": prefix_ok,
                    })
                else:
                    model(**toks, use_cache=False)
    finally:
        restore_attention()

    if not captures:
        return None

    q_rows: list[np.ndarray] = []
    k_rows: list[np.ndarray] = []
    v_rows: list[np.ndarray] = []
    scale_rows: list[np.ndarray] = []
    bias_rows: list[np.ndarray] = []
    dense_refs: list[np.ndarray] = []
    regimes: list[str] = []
    layers: list[int] = []
    heads: list[int] = []
    positions: list[int] = []
    prompt_ids: list[int] = []
    phases: list[str] = []
    valid_key_lens: list[int] = []
    query_lens: list[int] = []
    kv_head_ids: list[int] = []
    num_attention_heads_rows: list[int] = []
    num_key_value_heads_rows: list[int] = []
    num_key_value_groups_rows: list[int] = []
    rotary_position_rows: list[int] = []
    all_bias_serializable = True
    mask_challenge_exercised = False
    attention_mask_present_call_count = sum(1 for c in captures if c.get("attention_mask_present"))
    attention_mask_absent_call_count = len(captures) - attention_mask_present_call_count
    rotary_position_ids_present_call_count = sum(1 for c in captures if c.get("rotary_position_ids_present"))
    dropout_values = [float(c.get("dropout", 0.0) or 0.0) for c in captures]
    training_states = [bool(c.get("attention_training_state", False)) for c in captures]
    probability_dtypes = {str(c.get("attention_probability_dtype", "unknown")) for c in captures}
    dropout_applied = any(bool(c.get("dropout_applied", False)) for c in captures)
    probability_semantics_verified = bool(
        probability_dtypes == {PUBLIC_ATTENTION_PROBABILITY_DTYPE}
        and all(abs(x) <= 1e-12 for x in dropout_values)
        and not any(training_states)
        and not dropout_applied
    )
    dense_max_err = 0.0
    for cap in captures:
        remaining = max_rows - len(q_rows)
        if remaining <= 0:
            break
        rows = _rows_from_attention_capture(
            q=cap["query"],
            k=cap["key"],
            v=cap["value"],
            out=cap["attn_output"],
            attention_mask=cap["attention_mask"],
            scaling=cap["scaling"],
            layer_id=cap["layer_idx"],
            prompt_index=cap["prompt_index"],
            position_policy=position_policy,
            max_remaining=remaining,
            num_key_value_groups=cap["num_key_value_groups"],
            capture_phase=cap.get("capture_phase", "prefill"),
            query_start_position=int(cap.get("query_start_position", 0)),
            attention_dropout_p=float(cap.get("dropout", 0.0)),
            attention_training_state=bool(cap.get("attention_training_state", False)),
            attention_probability_dtype=str(cap.get("attention_probability_dtype", PUBLIC_ATTENTION_PROBABILITY_DTYPE)),
            rotary_position_ids=cap.get("rotary_position_ids"),
            rotary_position_out=rotary_position_rows,
        )
        rq, rk, rv, rs, rb, rr, rg, rl, rh, rp, rpid, rphase, rvkl, rql, bias_serializable, mask_seen, err = rows
        q_rows.extend(rq); k_rows.extend(rk); v_rows.extend(rv)
        scale_rows.extend(rs); bias_rows.extend(rb); dense_refs.extend(rr)
        regimes.extend(rg); layers.extend(rl); heads.extend(rh); positions.extend(rp); prompt_ids.extend(rpid)
        phases.extend(rphase); valid_key_lens.extend(rvkl); query_lens.extend(rql)
        cap_num_attention_heads = int(cap["query"].shape[1])
        cap_num_key_value_heads = int(cap["key"].shape[1])
        cap_num_key_value_groups = int(cap["num_key_value_groups"])
        kv_head_ids.extend([min(cap_num_key_value_heads - 1, int(h) // max(1, cap_num_key_value_groups)) for h in rh])
        num_attention_heads_rows.extend([cap_num_attention_heads] * len(rh))
        num_key_value_heads_rows.extend([cap_num_key_value_heads] * len(rh))
        num_key_value_groups_rows.extend([cap_num_key_value_groups] * len(rh))
        all_bias_serializable = all_bias_serializable and bias_serializable
        mask_challenge_exercised = mask_challenge_exercised or mask_seen
        dense_max_err = max(dense_max_err, err)
    if not q_rows:
        return None

    valid_key_len_arr = np.asarray(valid_key_lens, dtype=np.int64)
    query_len_arr = np.asarray(query_lens, dtype=np.int64)
    position_arr = np.asarray(positions, dtype=np.int64)
    if len(rotary_position_rows) == len(positions):
        rotary_position_id_arr = np.asarray(rotary_position_rows, dtype=np.int64)
    else:
        rotary_position_id_arr = position_arr.copy()
    max_key_len = int(np.max(valid_key_len_arr))
    padded_bias = _pad_2d_rows(bias_rows, width=max_key_len, fill=PUBLIC_MASK_SENTINEL)
    valid_key_len_semantics_verified = _valid_key_len_padding_verified(padded_bias, valid_key_len_arr)
    active_key_len_arr = _active_key_lengths_from_bias(padded_bias, valid_key_len_arr)
    active_key_len_semantics_verified = _active_key_len_semantics_verified(padded_bias, valid_key_len_arr, active_key_len_arr)
    absolute_position_verified = _absolute_position_semantics_verified(position_arr, valid_key_len_arr, query_len_arr, phases, active_key_len_arr)
    rotary_position_ids_verified = _rotary_position_semantics_verified(rotary_position_id_arr, position_arr, query_len_arr, phases)
    kv_head_arr = np.asarray(kv_head_ids, dtype=np.int64)
    num_attention_heads_arr = np.asarray(num_attention_heads_rows, dtype=np.int64)
    num_key_value_heads_arr = np.asarray(num_key_value_heads_rows, dtype=np.int64)
    num_key_value_groups_arr = np.asarray(num_key_value_groups_rows, dtype=np.int64)
    kv_group_map_verified = _kv_group_semantics_verified(position_arr * 0 + np.asarray(heads, dtype=np.int64), kv_head_arr, num_attention_heads_arr, num_key_value_heads_arr, num_key_value_groups_arr)
    gqa_grouped_rows_present = _gqa_grouped_rows_present(num_key_value_groups_arr, len(q_rows))
    prefill_phase_present = any(p == "prefill" for p in phases)
    decode_phase_present = any(p == "decode_cached" for p in phases)
    cache_decode_verified = bool(int(decode_steps) > 0 and decode_phase_present and any(q_len == 1 and live > 1 for q_len, live in zip(query_lens, valid_key_lens)))
    phase_contract = PUBLIC_CAPTURE_PHASE_CONTRACT if cache_decode_verified and prefill_phase_present else "prefill_only_v1"
    token_records_sorted = sorted(token_records, key=lambda r: int(r.get("prompt_index", 0)))
    prompt_token_count_arr = np.asarray([int(r.get("token_count", 0)) for r in token_records_sorted], dtype=np.int64)
    prompt_attention_mask_sum_arr = np.asarray([int(r.get("attention_mask_sum", 0)) for r in token_records_sorted], dtype=np.int64)
    prompt_input_ids_sha256_arr = np.asarray([str(r.get("input_ids_sha256", "")) for r in token_records_sorted])
    prompt_attention_mask_sha256_arr = np.asarray([str(r.get("attention_mask_sha256", "")) for r in token_records_sorted])
    prompt_text_sha256_arr = np.asarray([str(r.get("prompt_text_sha256", "")) for r in token_records_sorted])
    attention_mask_supplied_by_tokenizer_arr = np.asarray([bool(r.get("attention_mask_supplied_by_tokenizer", False)) for r in token_records_sorted])
    generation_records_sorted = sorted(generation_records, key=lambda r: int(r.get("prompt_index", 0)))
    generated_sequence_sha256_arr = np.asarray([str(r.get("generated_sequence_sha256", "")) for r in generation_records_sorted])
    generated_new_token_ids_sha256_arr = np.asarray([str(r.get("generated_new_token_ids_sha256", "")) for r in generation_records_sorted])
    generated_new_token_count_arr = np.asarray([int(r.get("generated_new_token_count", 0)) for r in generation_records_sorted], dtype=np.int64)
    generated_sequence_token_count_arr = np.asarray([int(r.get("generated_sequence_token_count", 0)) for r in generation_records_sorted], dtype=np.int64)
    generation_prompt_prefix_verified_arr = np.asarray([bool(r.get("generation_prompt_prefix_verified", False)) for r in generation_records_sorted])
    generation_token_provenance_verified = bool(
        len(generation_records_sorted) == len(prompts)
        and _generation_token_semantics_verified(
            prompt_ids=prompt_ids,
            positions=position_arr,
            phases=phases,
            prompt_token_count=prompt_token_count_arr,
            generated_sequence_sha256=generated_sequence_sha256_arr,
            generated_new_token_ids_sha256=generated_new_token_ids_sha256_arr,
            generated_new_token_count=generated_new_token_count_arr,
            generated_sequence_token_count=generated_sequence_token_count_arr,
            generation_prompt_prefix_verified=generation_prompt_prefix_verified_arr,
            decode_steps_requested=int(decode_steps),
        )
    )
    token_provenance_verified = bool(
        len(token_records_sorted) == len(prompts)
        and bool(np.all(attention_mask_supplied_by_tokenizer_arr))
        and _token_provenance_semantics_verified(
            prompt_ids=prompt_ids,
            positions=position_arr,
            phases=phases,
            prompt_token_count=prompt_token_count_arr,
            prompt_input_ids_sha256=prompt_input_ids_sha256_arr,
            prompt_attention_mask_sha256=prompt_attention_mask_sha256_arr,
            prompt_text_sha256=prompt_text_sha256_arr,
            decode_steps_requested=int(decode_steps),
        )
    )
    verified = bool(
        all_bias_serializable
        and mask_challenge_exercised
        and valid_key_len_semantics_verified
        and active_key_len_semantics_verified
        and absolute_position_verified
        and rotary_position_ids_verified
        and token_provenance_verified
        and generation_token_provenance_verified
        and generation_determinism_verified
        and kv_group_map_verified
        and probability_semantics_verified
        and phase_contract == PUBLIC_CAPTURE_PHASE_CONTRACT
        and dense_max_err <= PUBLIC_DENSE_PARITY_MAX_ABS_ERROR
    )
    return {
        "rows": (q_rows, k_rows, v_rows, regimes, layers, heads, positions),
        "prompt_ids": prompt_ids,
        "capture_phase": phases,
        "valid_key_len": valid_key_len_arr,
        "active_key_len": active_key_len_arr,
        "query_len": query_len_arr,
        "kv_head": kv_head_arr,
        "num_attention_heads": num_attention_heads_arr,
        "num_key_value_heads": num_key_value_heads_arr,
        "num_key_value_groups": num_key_value_groups_arr,
        "kv_group_map_contract": PUBLIC_KV_GROUP_CONTRACT,
        "kv_group_map_verified": bool(kv_group_map_verified),
        "gqa_grouped_rows_present": bool(gqa_grouped_rows_present),
        "adapter": "hf_llama_eager_post_transform_attention_forward",
        "attention_interface_backend": install_status.get("backend_name"),
        "attention_interface_registry_wrapper_installed": bool(install_status.get("eager_registry_overridden")),
        "attention_mask_backend_preserved": bool(install_status.get("attention_mask_backend_preserved")),
        "custom_attention_backend_used": bool(install_status.get("custom_attention_backend_used", False)),
        "attention_interface_install_status": install_status,
        "attention_score_input_stage": PUBLIC_SCORE_INPUT_STAGE,
        "attention_score_inputs_verified": verified,
        "score_transform": PUBLIC_SCORE_TRANSFORM,
        "probability_contract": PUBLIC_PROBABILITY_CONTRACT,
        "probability_semantics_verified": bool(probability_semantics_verified),
        "attention_probability_dtype": PUBLIC_ATTENTION_PROBABILITY_DTYPE,
        "attention_dropout_p": float(max(dropout_values) if dropout_values else 0.0),
        "attention_training_state": bool(any(training_states)),
        "dropout_applied": bool(dropout_applied),
        "attention_scale": np.concatenate(scale_rows).astype(np.float64),
        "score_bias": padded_bias.astype(np.float64),
        "attention_scale_verified": True,
        "score_bias_verified": bool(all_bias_serializable and valid_key_len_semantics_verified),
        "mask_challenge_exercised": bool(mask_challenge_exercised),
        "attention_mask_present_call_count": int(attention_mask_present_call_count),
        "attention_mask_absent_call_count": int(attention_mask_absent_call_count),
        "dense_reference_output": np.stack(dense_refs).astype(np.float64),
        "dense_reference_verified": verified,
        "dense_reference_max_abs_error": float(dense_max_err),
        "prompt_count": int(len(prompts)),
        "position_policy": position_policy,
        "rotary_position_id": rotary_position_id_arr,
        "rotary_position_contract": PUBLIC_ROTARY_POSITION_CONTRACT,
        "rotary_position_ids_verified": bool(rotary_position_ids_verified),
        "rotary_position_ids_present_call_count": int(rotary_position_ids_present_call_count),
        "decode_steps_requested": int(decode_steps),
        "active_key_len_contract": PUBLIC_ACTIVE_KEY_CONTRACT,
        "active_key_len_semantics_verified": bool(active_key_len_semantics_verified),
        "position_contract": PUBLIC_POSITION_CONTRACT,
        "absolute_position_verified": bool(absolute_position_verified),
        "capture_phase_contract": phase_contract,
        "prefill_phase_present": bool(prefill_phase_present),
        "decode_phase_present": bool(decode_phase_present),
        "cache_decode_verified": bool(cache_decode_verified),
        "valid_key_len_semantics_verified": bool(valid_key_len_semantics_verified),
        "token_provenance_contract": PUBLIC_TOKEN_PROVENANCE_CONTRACT,
        "token_provenance_verified": bool(token_provenance_verified),
        "prompt_token_count": prompt_token_count_arr,
        "prompt_attention_mask_sum": prompt_attention_mask_sum_arr,
        "prompt_input_ids_sha256": prompt_input_ids_sha256_arr,
        "prompt_attention_mask_sha256": prompt_attention_mask_sha256_arr,
        "prompt_text_sha256": prompt_text_sha256_arr,
        "attention_mask_supplied_by_tokenizer": attention_mask_supplied_by_tokenizer_arr,
        "generation_config_json": generation_config_json,
        "generation_config_sha256": generation_config_sha256,
        "generation_determinism_contract": PUBLIC_GENERATION_DETERMINISM_CONTRACT,
        "generation_determinism_verified": bool(generation_determinism_verified),
        "generation_strategy": str(generation_settings["strategy"]),
        "generation_do_sample": bool(generation_settings["do_sample"]),
        "generation_use_cache": bool(generation_settings["use_cache"]),
        "cache_implementation_contract": PUBLIC_CACHE_IMPLEMENTATION_CONTRACT,
        "generation_cache_implementation": str(generation_settings["cache_implementation"]),
        "generation_cache_implementation_source": str(generation_settings["cache_implementation_source"]),
        "generation_cache_config_present": bool(generation_settings["cache_config"] is not None),
        "generation_num_beams": int(generation_settings["num_beams"]),
        "generation_num_return_sequences": int(generation_settings["num_return_sequences"]),
        "generation_max_new_tokens": int(generation_settings["max_new_tokens"]),
        "generation_min_new_tokens": int(generation_settings["min_new_tokens"]),
        "generation_sampling_disabled": bool(generation_settings["sampling_disabled"]),
        "generation_exact_new_tokens_required": bool(generation_settings["exact_new_token_count_required"]),
        "generated_new_token_exact_count_verified": bool(
            generation_token_provenance_verified
            and generated_new_token_count_arr.size == len(prompts)
            and bool(np.all(generated_new_token_count_arr == int(decode_steps)))
        ),
        "generation_token_contract": PUBLIC_GENERATION_TOKEN_CONTRACT,
        "generation_token_provenance_verified": bool(generation_token_provenance_verified),
        "generated_sequence_sha256": generated_sequence_sha256_arr,
        "generated_new_token_ids_sha256": generated_new_token_ids_sha256_arr,
        "generated_new_token_count": generated_new_token_count_arr,
        "generated_sequence_token_count": generated_sequence_token_count_arr,
        "generation_prompt_prefix_verified": generation_prompt_prefix_verified_arr,
        "fidelity_note": "Captured from HF Llama eager_attention_forward after RoPE and before score computation, with the built-in eager mask backend preserved. Dense output was recomputed from exported Q/K/V, scale, additive score bias, float32 softmax/no-dropout probability semantics, mask-derived active_key_len, absolute active-key positions, valid_key_len padding masks, explicit prompt/token digests, exact generated-token sequence digests, greedy single-beam generation determinism contract with explicit dynamic KV cache, explicit device/dtype/timing provenance, and explicit query-head to KV-head group mapping against the runtime attention output before o_proj. Public self-attestation requires cached-decode phase coverage with exact prompt manifest plus tokenizer input_ids/attention_mask digests, generated continuation token digests, greedy single-beam exact-length decode settings, absolute decode row positions, active-key mask semantics, probability dtype/dropout semantics, and KV-sharing semantics, not prefill-only, physical-cache-width labels, unreplayable prompt or generated-token streams, hidden dtype/device placement, float64 replay accidents, or duplicated KV rows with no ownership map.",
    }


def _is_immutable_revision(value: object) -> bool:
    text = str(value or "").strip()
    if text.startswith("sha256:"):
        digest = text.split(":", 1)[1]
        return len(digest) == 64 and all(c in "0123456789abcdefABCDEF" for c in digest)
    return len(text) in {40, 64} and all(c in "0123456789abcdefABCDEF" for c in text)


def _resolved_commit(obj: Any, requested: str | None) -> str:
    candidates = [
        getattr(getattr(obj, "config", None), "_commit_hash", None),
        getattr(obj, "_commit_hash", None),
        getattr(obj, "init_kwargs", {}).get("_commit_hash") if isinstance(getattr(obj, "init_kwargs", None), dict) else None,
        requested,
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return "unresolved"


def _snapshot_digest_authenticity_proof(
    *,
    model_load_source: str,
    public_model_id: str,
    requested_revision: str | None,
    require_hash: bool,
) -> dict[str, Any]:
    """Verify that the local model.safetensors bytes match the pinned public weight digest.

    Public trace identity used to stop at immutable revision + source URL.  That is
    necessary but not sufficient for a mounted/local snapshot path: a structurally
    plausible directory could contain the wrong or truncated weights.  This helper
    reuses the shared snapshot integrity contract and promotes only when the
    expected TinyLlama model.safetensors SHA-256 is observed.
    """
    revision = str(requested_revision or "")
    candidates: list[Path] = []
    load_path = Path(model_load_source).expanduser()
    if load_path.exists():
        candidates.append(load_path.resolve())
    candidates.extend(snapshot_candidate_paths(public_model_id, revision))
    deduped: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key not in seen:
            seen.add(key)
            deduped.append(path)

    checks: list[dict[str, Any]] = []
    for path in deduped:
        try:
            checks.append(inspect_snapshot(path, model_id=public_model_id, revision=revision, include_hashes=require_hash))
        except Exception as exc:
            checks.append({
                "path": str(path),
                "complete_required_snapshot": False,
                "blockers": ["snapshot_digest_inspection_exception"],
                "error": type(exc).__name__ + ": " + repr(exc),
            })

    load_source_resolved_path = str(load_path.resolve()) if load_path.exists() else str(load_path)
    load_source_is_local_directory = bool(load_path.exists() and load_path.is_dir())
    load_source_check: dict[str, Any] | None = None
    for check in checks:
        if str(check.get("path", "")) == load_source_resolved_path:
            load_source_check = check
            break

    verified_check: dict[str, Any] | None = None
    for check in checks:
        safe = check.get("model_safetensors", {}) if isinstance(check, dict) else {}
        if check.get("complete_required_snapshot") and safe.get("sha256_matches_expected") is True:
            verified_check = check
            break

    load_source_safe = load_source_check.get("model_safetensors", {}) if isinstance(load_source_check, dict) else {}
    loader_snapshot_binding_verified = bool(
        load_source_is_local_directory
        and load_source_check is not None
        and load_source_check.get("complete_required_snapshot")
        and load_source_safe.get("sha256_matches_expected") is True
    )

    observed_sha = ""
    observed_path = ""
    matches = False
    for check in checks:
        safe = check.get("model_safetensors", {}) if isinstance(check, dict) else {}
        if safe.get("sha256"):
            observed_sha = str(safe.get("sha256"))
            observed_path = str(check.get("path", ""))
            matches = bool(safe.get("sha256_matches_expected"))
            break
    if verified_check is not None:
        safe = verified_check.get("model_safetensors", {})
        observed_sha = str(safe.get("sha256", observed_sha))
        observed_path = str(verified_check.get("path", observed_path))
        matches = True

    blockers: list[str] = []
    if require_hash and verified_check is None:
        blockers.append("model_safetensors_digest_not_verified_against_expected_sha256")
    if require_hash and not checks:
        blockers.append("no_snapshot_candidate_available_for_digest_verification")
    if require_hash and checks and not any((c.get("model_safetensors", {}) if isinstance(c, dict) else {}).get("sha256") for c in checks):
        blockers.append("snapshot_candidates_lacked_hashable_model_safetensors")
    if require_hash and not load_source_is_local_directory:
        blockers.append("model_load_source_not_local_snapshot_directory")
    if require_hash and not loader_snapshot_binding_verified:
        blockers.append("model_load_source_not_digest_verified_snapshot_path")

    return {
        "contract": "model_safetensors_digest_authenticity_v1",
        "required": bool(require_hash),
        "expected_model_safetensors_sha256": EXPECTED_MODEL_SAFETENSORS_SHA256,
        "observed_model_safetensors_sha256": observed_sha,
        "observed_snapshot_path": observed_path,
        "sha256_matches_expected": bool(matches),
        "verified": bool(verified_check is not None),
        "candidate_count": len(checks),
        "candidate_paths": [str(p) for p in deduped],
        "model_load_source_resolved_path": load_source_resolved_path,
        "model_load_source_is_local_directory": bool(load_source_is_local_directory),
        "model_load_source_complete_required_snapshot": bool(load_source_check.get("complete_required_snapshot") if isinstance(load_source_check, dict) else False),
        "model_load_source_sha256_matches_expected": bool(load_source_safe.get("sha256_matches_expected") is True),
        "loader_snapshot_binding_contract": "model_loader_uses_selected_digest_verified_local_snapshot_v1",
        "loader_snapshot_binding_verified": bool(loader_snapshot_binding_verified),
        "verified_snapshot_path": str(verified_check.get("path", "")) if verified_check else "",
        "candidate_summaries": [
            {
                "path": str(c.get("path", "")),
                "exists": bool(c.get("exists", False)),
                "complete_required_snapshot": bool(c.get("complete_required_snapshot", False)),
                "sha256_checked": bool((c.get("model_safetensors", {}) if isinstance(c, dict) else {}).get("sha256")),
                "sha256_matches_expected": bool((c.get("model_safetensors", {}) if isinstance(c, dict) else {}).get("sha256_matches_expected", False)),
                "blockers": list(c.get("blockers", []))[:12],
            }
            for c in checks
        ],
        "blockers": sorted(set(blockers)),
    }


def _resolve_prompts(args: argparse.Namespace) -> list[str]:
    prompts: list[str] = []
    if args.prompt:
        prompts.extend([p for p in args.prompt if str(p).strip()])
    if args.prompts_file is not None:
        text = args.prompts_file.read_text(encoding="utf-8")
        stripped = text.strip()
        if stripped.startswith("["):
            loaded = json.loads(stripped)
            if not isinstance(loaded, list):
                raise SystemExit("--prompts-file JSON must be a list of strings")
            prompts.extend([str(x) for x in loaded if str(x).strip()])
        else:
            prompts.extend([line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")])
    if not prompts:
        prompts = ["The quick brown fox jumps over the lazy dog."]
    return prompts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Hugging Face model id or local snapshot path used by from_pretrained")
    parser.add_argument("--public-model-id", default=None, help="canonical public model id to write into provenance when --model is a local snapshot path")
    parser.add_argument("--model-revision", default=None, help="model revision; a full immutable commit/content hash is required for public claims")
    parser.add_argument("--tokenizer-revision", default=None, help="tokenizer revision; defaults to --model-revision and must resolve to an immutable hash for public claims")
    parser.add_argument("--code-revision", default=None, help="immutable remote-code revision; required when --trust-remote-code is used for a public claim")
    parser.add_argument("--prompt", action="append", default=None, help="prompt to trace; may be passed more than once")
    parser.add_argument("--prompts-file", type=Path, default=None, help="optional UTF-8 text file with one prompt per line, or a JSON list of prompts")
    parser.add_argument("--position-policy", choices=["last_token_only", "last_and_mid", "all_tokens"], default="last_and_mid")
    parser.add_argument("--decode-steps", type=int, default=0, help="when >0, use model.generate(..., use_cache=True) to capture prefill plus cached-decode rows")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-rows", type=int, default=128)
    parser.add_argument("--allow-download", action="store_true", help="allow Hugging Face downloads; default is local-files-only")
    parser.add_argument("--trust-remote-code", action="store_true", help="pass trust_remote_code=True; review code before use")
    parser.add_argument("--attention-implementation", default="eager", help="requested Transformers attention implementation")
    parser.add_argument("--cache-implementation", default=PUBLIC_REQUIRED_CACHE_IMPLEMENTATION, help="requested Transformers generation cache implementation; public traces must use dynamic")
    parser.add_argument("--torch-dtype", default="float32", choices=["auto", "float32", "float16", "bfloat16"], help="explicit dtype passed to from_pretrained and recorded in public runtime provenance")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"], help="explicit capture device policy; auto chooses cuda when available, else cpu")
    parser.add_argument("--provenance-out", type=Path, default=None)
    parser.add_argument("--public-pretrained-trace", action="store_true", help="request a public/pretrained claim; refused unless semantic fidelity and immutable provenance are verified")
    parser.add_argument("--require-model-safetensors-sha256", action="store_true", help="require an observed local model.safetensors SHA-256 matching the pinned public weight digest before public promotion")
    parser.add_argument("--require-loader-snapshot-bind", action="store_true", help="require --model itself to be the digest-verified local snapshot path, not merely any cached candidate")
    parser.add_argument("--source-type", default="public_pretrained_hf")
    parser.add_argument("--weights-source", default="")
    parser.add_argument("--license", default="")
    parser.add_argument("--provenance-reviewed", action="store_true")
    parser.add_argument("--uses-random-weights", action="store_true")
    parser.add_argument("--generated-from-local-tiny-model", action="store_true")
    args = parser.parse_args()

    if args.max_rows <= 0:
        raise SystemExit("--max-rows must be positive")
    if args.decode_steps < 0:
        raise SystemExit("--decode-steps must be non-negative")
    if args.public_pretrained_trace and str(args.cache_implementation) != PUBLIC_REQUIRED_CACHE_IMPLEMENTATION:
        raise SystemExit("public pretrained cached-decode traces must use --cache-implementation dynamic; other caches are timing/baseline lanes")
    prompts = _resolve_prompts(args)
    public_model_id = str(args.public_model_id or args.model).strip()
    if not public_model_id:
        raise SystemExit("--public-model-id resolved empty")
    snapshot_digest_proof = _snapshot_digest_authenticity_proof(
        model_load_source=args.model,
        public_model_id=public_model_id,
        requested_revision=args.model_revision,
        require_hash=bool(args.require_model_safetensors_sha256),
    )
    if args.public_pretrained_trace and args.require_model_safetensors_sha256 and not snapshot_digest_proof.get("verified"):
        raise SystemExit(
            "public pretrained trace requires verified model.safetensors SHA-256; "
            + ",".join(snapshot_digest_proof.get("blockers", []))
        )
    if args.public_pretrained_trace and args.require_loader_snapshot_bind and not snapshot_digest_proof.get("loader_snapshot_binding_verified"):
        raise SystemExit(
            "public pretrained trace requires --model to be the selected digest-verified local snapshot path; "
            + ",".join(snapshot_digest_proof.get("blockers", []))
        )

    local_only = not args.allow_download
    capture_network_quarantine = _enforce_capture_network_quarantine(local_only=local_only)
    if args.public_pretrained_trace and not capture_network_quarantine.get("set_before_runtime_import"):
        raise SystemExit("public pretrained capture requires offline quarantine before importing Hugging Face runtime")
    torch, transformers, AutoModelForCausalLM, AutoTokenizer = _import_runtime()
    model_load_path = Path(args.model).expanduser()
    model_load_source_is_local_path = model_load_path.exists()
    tokenizer_revision = args.tokenizer_revision or args.model_revision
    load_tokenizer_revision = None if model_load_source_is_local_path else tokenizer_revision
    load_model_revision = None if model_load_source_is_local_path else args.model_revision
    tokenizer = AutoTokenizer.from_pretrained(
        args.model,
        revision=load_tokenizer_revision,
        local_files_only=local_only,
        trust_remote_code=args.trust_remote_code,
    )
    model_kwargs: dict[str, Any] = {
        "revision": load_model_revision,
        "local_files_only": local_only,
        "trust_remote_code": args.trust_remote_code,
        "attn_implementation": args.attention_implementation,
    }
    model_kwargs["torch_dtype"] = _resolve_torch_dtype_arg(torch, args.torch_dtype)
    if args.code_revision is not None:
        model_kwargs["code_revision"] = args.code_revision
    model = AutoModelForCausalLM.from_pretrained(args.model, **model_kwargs)
    model.eval()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requested but torch.cuda.is_available() is false")
    device = "cuda" if (args.device == "auto" and torch.cuda.is_available()) else ("cpu" if args.device == "auto" else args.device)
    model.to(device)

    synchronized_timing = bool(device == "cuda" and torch.cuda.is_available())
    if synchronized_timing:
        torch.cuda.synchronize()
    capture_start = time.perf_counter()
    capture = _capture_llama_eager_post_transform_style(torch, model, tokenizer, prompts, args.max_rows, args.position_policy, args.decode_steps, args.cache_implementation)
    if capture is None:
        # Legacy diagnostic adapters intentionally use only the first prompt and
        # cannot self-attest as public/pretrained score-input evidence.
        capture = _capture_gpt2_style(torch, model, tokenizer, prompts[0], args.max_rows)
    if capture is None:
        capture = _capture_qkv_projection_style(torch, model, tokenizer, prompts[0], args.max_rows)
    if capture is None:
        raise SystemExit("Unsupported model adapter: no verified Llama eager path, GPT-2 c_attn, or q_proj/k_proj/v_proj path found")
    if synchronized_timing:
        torch.cuda.synchronize()
    capture_elapsed_seconds = time.perf_counter() - capture_start
    runtime_summary = _runtime_device_dtype_summary(
        torch, model,
        requested_torch_dtype=args.torch_dtype,
        requested_device_policy=args.device,
        actual_device=device,
        synchronized_before_after_timing=synchronized_timing,
        capture_elapsed_seconds=capture_elapsed_seconds,
    )
    runtime_provenance_verified = _runtime_provenance_semantics_verified(runtime_summary)

    q_rows, k_rows, v_rows, regimes, layers, heads, positions = capture["rows"]
    if not q_rows:
        raise SystemExit("No trace rows captured")
    valid_key_len = np.asarray(capture.get("valid_key_len", _valid_key_lengths_from_rows(k_rows)), dtype=np.int64).reshape(-1)
    if valid_key_len.shape[0] != len(k_rows):
        raise SystemExit(f"internal capture error: valid_key_len length {valid_key_len.shape[0]} does not match row count {len(k_rows)}")
    max_key_len = int(np.max(valid_key_len))
    q = np.stack(q_rows).astype(np.float64)
    k = _pad_3d_rows(k_rows, width=max_key_len).astype(np.float64)
    v = _pad_3d_rows(v_rows, width=max_key_len).astype(np.float64)
    row_count = int(q.shape[0])
    default_num_attention_heads = max(1, int(max(heads) + 1)) if heads else 1
    kv_head = _broadcast_int_rows(capture.get("kv_head"), row_count, default=0)
    num_attention_heads = _broadcast_int_rows(capture.get("num_attention_heads"), row_count, default=default_num_attention_heads)
    default_num_key_value_heads = max(1, int(np.max(kv_head)) + 1)
    num_key_value_heads = _broadcast_int_rows(capture.get("num_key_value_heads"), row_count, default=default_num_key_value_heads)
    default_num_key_value_groups = max(1, int(num_attention_heads[0]) // max(1, int(num_key_value_heads[0])))
    num_key_value_groups = _broadcast_int_rows(capture.get("num_key_value_groups"), row_count, default=default_num_key_value_groups)
    kv_group_map_verified = bool(
        capture.get("kv_group_map_verified", False)
        and capture.get("kv_group_map_contract") == PUBLIC_KV_GROUP_CONTRACT
        and _kv_group_semantics_verified(heads, kv_head, num_attention_heads, num_key_value_heads, num_key_value_groups)
    )
    gqa_grouped_rows_present = bool(capture.get("gqa_grouped_rows_present", False) or _gqa_grouped_rows_present(num_key_value_groups, row_count))

    model_revision = _resolved_commit(model, args.model_revision)
    resolved_tokenizer_revision = _resolved_commit(tokenizer, tokenizer_revision)
    config_dict = model.config.to_dict() if hasattr(model.config, "to_dict") else vars(model.config)
    config_sha256 = sha256_json(config_dict)
    capture_tool_sha = sha256_file(Path(__file__).resolve())
    prompt_sha = sha256_json(prompts)
    code_revision = args.code_revision or ("unresolved" if args.trust_remote_code else "not_applicable")
    dense_error = capture["dense_reference_max_abs_error"]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    dense_error_value = float(capture["dense_reference_max_abs_error"]) if capture["dense_reference_max_abs_error"] is not None else np.nan
    # Diagnostic projection adapters do not know the model's exact score rule.
    # We still serialize an explicit baseline rule for deterministic local replay,
    # while the verification booleans remain false so it can never self-promote.
    attention_scale = np.asarray(capture.get("attention_scale", [1.0 / math.sqrt(int(q.shape[-1]))]), dtype=np.float64).reshape(-1)
    if attention_scale.size == 1:
        attention_scale = np.repeat(attention_scale, q.shape[0])
    raw_score_bias = capture.get("score_bias")
    if raw_score_bias is None:
        score_bias = np.zeros((q.shape[0], k.shape[1]), dtype=np.float64)
        for i, live in enumerate(valid_key_len):
            if int(live) < k.shape[1]:
                score_bias[i, int(live):] = PUBLIC_MASK_SENTINEL
    elif isinstance(raw_score_bias, list):
        score_bias = _pad_2d_rows(raw_score_bias, width=k.shape[1], fill=PUBLIC_MASK_SENTINEL)
    else:
        score_bias = np.asarray(raw_score_bias, dtype=np.float64)
        if score_bias.ndim == 1:
            score_bias = score_bias.reshape(1, -1)
        if score_bias.shape[1] != k.shape[1] and score_bias.shape[0] == q.shape[0]:
            score_bias = _pad_2d_rows([score_bias[i, : int(valid_key_len[i])] for i in range(score_bias.shape[0])], width=k.shape[1], fill=PUBLIC_MASK_SENTINEL)
    if score_bias.shape != (q.shape[0], k.shape[1]):
        raise SystemExit(f"internal capture error: score_bias shape {score_bias.shape} does not match {(q.shape[0], k.shape[1])}")
    valid_key_len_semantics_verified = _valid_key_len_padding_verified(score_bias, valid_key_len)
    active_key_len = np.asarray(capture.get("active_key_len", _active_key_lengths_from_bias(score_bias, valid_key_len)), dtype=np.int64).reshape(-1)
    if active_key_len.shape[0] != q.shape[0]:
        raise SystemExit(f"internal capture error: active_key_len length {active_key_len.shape[0]} does not match row count {q.shape[0]}")
    active_key_len_semantics_verified = _active_key_len_semantics_verified(score_bias, valid_key_len, active_key_len)
    rotary_position_id = _broadcast_int_rows(capture.get("rotary_position_id"), row_count, default=0)
    rotary_position_ids_verified = bool(
        capture.get("rotary_position_contract") == PUBLIC_ROTARY_POSITION_CONTRACT
        and capture.get("rotary_position_ids_verified") is True
        and _rotary_position_semantics_verified(
            rotary_position_id,
            np.asarray(positions, dtype=np.int64),
            np.asarray(capture.get("query_len", np.ones(q.shape[0], dtype=np.int64) * k.shape[1]), dtype=np.int64),
            capture.get("capture_phase", ["prefill"] * q.shape[0]),
        )
    )
    phase_contract_verified = bool(
        capture.get("capture_phase_contract") == PUBLIC_CAPTURE_PHASE_CONTRACT
        and capture.get("prefill_phase_present") is True
        and capture.get("decode_phase_present") is True
        and capture.get("cache_decode_verified") is True
        and valid_key_len_semantics_verified is True
        and capture.get("active_key_len_contract") == PUBLIC_ACTIVE_KEY_CONTRACT
        and capture.get("active_key_len_semantics_verified") is True
        and capture.get("position_contract") == PUBLIC_POSITION_CONTRACT
        and capture.get("absolute_position_verified") is True
        and rotary_position_ids_verified is True
        and int(capture.get("rotary_position_ids_present_call_count", 0)) > 0
        and capture.get("kv_group_map_contract") == PUBLIC_KV_GROUP_CONTRACT
        and kv_group_map_verified is True
    )
    score_path_fidelity_verified = bool(
        capture["attention_score_input_stage"] == PUBLIC_SCORE_INPUT_STAGE
        and capture["attention_score_inputs_verified"] is True
        and capture["attention_scale_verified"] is True
        and capture["score_bias_verified"] is True
        and capture.get("probability_contract") == PUBLIC_PROBABILITY_CONTRACT
        and capture.get("probability_semantics_verified") is True
        and capture.get("attention_probability_dtype") == PUBLIC_ATTENTION_PROBABILITY_DTYPE
        and float(capture.get("attention_dropout_p", 1.0)) == 0.0
        and capture.get("attention_training_state") is False
        and capture.get("dropout_applied") is False
        and active_key_len_semantics_verified is True
        and rotary_position_ids_verified is True
        and int(capture.get("rotary_position_ids_present_call_count", 0)) > 0
        and kv_group_map_verified is True
        and capture["score_transform"] == PUBLIC_SCORE_TRANSFORM
        and capture["dense_reference_verified"] is True
        and capture.get("attention_mask_backend_preserved") is True
        and capture.get("custom_attention_backend_used") is not True
        and capture.get("mask_challenge_exercised") is True
        and phase_contract_verified is True
        and dense_error is not None
        and math.isfinite(float(dense_error))
        and float(dense_error) <= PUBLIC_DENSE_PARITY_MAX_ABS_ERROR
        and capture.get("dense_reference_output") is not None
    )
    dense_reference_output = capture.get("dense_reference_output")
    if dense_reference_output is not None:
        dense_reference_output = np.asarray(dense_reference_output, dtype=np.float64)
        if dense_reference_output.shape != (q.shape[0], v.shape[2]):
            raise SystemExit(f"internal capture error: dense_reference_output shape {dense_reference_output.shape} does not match {(q.shape[0], v.shape[2])}")
    else:
        dense_reference_output = np.zeros((q.shape[0], v.shape[2]), dtype=np.float64)
    prompt_ids = np.asarray(capture.get("prompt_ids", [0] * q.shape[0]), dtype=np.int64).reshape(-1)
    if prompt_ids.shape != (q.shape[0],):
        raise SystemExit(f"internal capture error: prompt_id shape {prompt_ids.shape} does not match rows {q.shape[0]}")
    prompt_token_count = np.asarray(capture.get("prompt_token_count", [0]), dtype=np.int64).reshape(-1)
    prompt_attention_mask_sum = np.asarray(capture.get("prompt_attention_mask_sum", [0]), dtype=np.int64).reshape(-1)
    prompt_input_ids_sha256 = np.asarray(capture.get("prompt_input_ids_sha256", [""])).astype(str).reshape(-1)
    prompt_attention_mask_sha256 = np.asarray(capture.get("prompt_attention_mask_sha256", [""])).astype(str).reshape(-1)
    prompt_text_sha256 = np.asarray(capture.get("prompt_text_sha256", [""])).astype(str).reshape(-1)
    token_provenance_verified = bool(
        capture.get("token_provenance_contract") == PUBLIC_TOKEN_PROVENANCE_CONTRACT
        and capture.get("token_provenance_verified") is True
        and _token_provenance_semantics_verified(
            prompt_ids=prompt_ids,
            positions=np.asarray(positions, dtype=np.int64),
            phases=capture.get("capture_phase", ["prefill"] * q.shape[0]),
            prompt_token_count=prompt_token_count,
            prompt_input_ids_sha256=prompt_input_ids_sha256,
            prompt_attention_mask_sha256=prompt_attention_mask_sha256,
            prompt_text_sha256=prompt_text_sha256,
            decode_steps_requested=int(capture.get("decode_steps_requested", args.decode_steps)),
        )
    )
    generation_config_json = str(capture.get("generation_config_json", "{}"))
    generation_config_sha256 = str(capture.get("generation_config_sha256", "missing_generation_config_sha256"))
    generation_determinism_contract = str(capture.get("generation_determinism_contract", "missing_generation_determinism_contract"))
    generation_determinism_verified = bool(capture.get("generation_determinism_verified", False))
    generation_strategy = str(capture.get("generation_strategy", "unknown"))
    generation_num_beams = int(capture.get("generation_num_beams", 0))
    cache_implementation_contract = str(capture.get("cache_implementation_contract", "missing_cache_implementation_contract"))
    generation_cache_implementation = str(capture.get("generation_cache_implementation", "missing_cache_implementation"))
    generation_cache_implementation_source = str(capture.get("generation_cache_implementation_source", "missing_cache_implementation_source"))
    generation_cache_config_present = bool(capture.get("generation_cache_config_present", True))
    generation_num_return_sequences = int(capture.get("generation_num_return_sequences", 0))
    generation_max_new_tokens = int(capture.get("generation_max_new_tokens", 0))
    generation_min_new_tokens = int(capture.get("generation_min_new_tokens", 0))
    generation_sampling_disabled = bool(capture.get("generation_sampling_disabled", False))
    generation_exact_new_tokens_required = bool(capture.get("generation_exact_new_tokens_required", False))
    generated_new_token_exact_count_verified = bool(capture.get("generated_new_token_exact_count_verified", False))
    generated_sequence_sha256 = np.asarray(capture.get("generated_sequence_sha256", [""])).astype(str).reshape(-1)
    generated_new_token_ids_sha256 = np.asarray(capture.get("generated_new_token_ids_sha256", [""])).astype(str).reshape(-1)
    generated_new_token_count = np.asarray(capture.get("generated_new_token_count", [0]), dtype=np.int64).reshape(-1)
    generated_sequence_token_count = np.asarray(capture.get("generated_sequence_token_count", [0]), dtype=np.int64).reshape(-1)
    generation_prompt_prefix_verified = np.asarray(capture.get("generation_prompt_prefix_verified", [False]), dtype=bool).reshape(-1)
    generation_token_provenance_verified = bool(
        capture.get("generation_token_contract") == PUBLIC_GENERATION_TOKEN_CONTRACT
        and capture.get("generation_token_provenance_verified") is True
        and _generation_token_semantics_verified(
            prompt_ids=prompt_ids,
            positions=np.asarray(positions, dtype=np.int64),
            phases=capture.get("capture_phase", ["prefill"] * q.shape[0]),
            prompt_token_count=prompt_token_count,
            generated_sequence_sha256=generated_sequence_sha256,
            generated_new_token_ids_sha256=generated_new_token_ids_sha256,
            generated_new_token_count=generated_new_token_count,
            generated_sequence_token_count=generated_sequence_token_count,
            generation_prompt_prefix_verified=generation_prompt_prefix_verified,
            decode_steps_requested=int(capture.get("decode_steps_requested", args.decode_steps)),
        )
    )
    generation_determinism_gate_verified = bool(
        generation_determinism_contract == PUBLIC_GENERATION_DETERMINISM_CONTRACT
        and generation_determinism_verified is True
        and generation_strategy == "greedy"
        and generation_num_beams == 1
        and cache_implementation_contract == PUBLIC_CACHE_IMPLEMENTATION_CONTRACT
        and generation_cache_implementation == PUBLIC_REQUIRED_CACHE_IMPLEMENTATION
        and generation_cache_implementation_source == "explicit_generate_argument"
        and generation_cache_config_present is False
        and generation_num_return_sequences == 1
        and generation_max_new_tokens == int(capture.get("decode_steps_requested", args.decode_steps))
        and generation_min_new_tokens == int(capture.get("decode_steps_requested", args.decode_steps))
        and generation_sampling_disabled is True
        and generation_exact_new_tokens_required is True
        and generated_new_token_exact_count_verified is True
    )
    snapshot_digest_verified = bool((not args.require_model_safetensors_sha256) or snapshot_digest_proof.get("verified") is True)
    loader_snapshot_binding_verified = bool((not args.require_loader_snapshot_bind) or snapshot_digest_proof.get("loader_snapshot_binding_verified") is True)
    provenance_complete = bool(
        _is_immutable_revision(model_revision)
        and _is_immutable_revision(resolved_tokenizer_revision)
        and (not args.trust_remote_code or _is_immutable_revision(code_revision))
        and args.weights_source.strip()
        and args.license.strip()
        and args.provenance_reviewed
        and snapshot_digest_verified
        and loader_snapshot_binding_verified
        and not args.uses_random_weights
        and not args.generated_from_local_tiny_model
    )
    fidelity_verified = bool(score_path_fidelity_verified and token_provenance_verified and generation_token_provenance_verified and generation_determinism_gate_verified)
    effective_public = bool(args.public_pretrained_trace and fidelity_verified and provenance_complete and runtime_provenance_verified)
    effective_source_type = args.source_type if effective_public else "hf_projection_capture_unverified"
    np.savez_compressed(
        args.out,
        q=q,
        k=k,
        v=v,
        regime=np.asarray(regimes),
        layer=np.asarray(layers, dtype=np.int64),
        head=np.asarray(heads, dtype=np.int64),
        position=np.asarray(positions, dtype=np.int64),
        rotary_position_id=rotary_position_id.astype(np.int64),
        d_head=np.asarray([int(q.shape[-1])], dtype=np.int64),
        model_id=np.asarray([public_model_id]),
        model_load_source=np.asarray([args.model]),
        model_load_source_is_local_path=np.asarray([bool(model_load_source_is_local_path)]),
        runtime_provenance_contract=np.asarray([str(runtime_summary["runtime_provenance_contract"])]),
        requested_torch_dtype=np.asarray([str(runtime_summary["requested_torch_dtype"])]),
        resolved_torch_dtype=np.asarray([str(runtime_summary["resolved_torch_dtype"])]),
        requested_device_policy=np.asarray([str(runtime_summary["requested_device_policy"])]),
        actual_primary_device=np.asarray([str(runtime_summary["actual_primary_device"])]),
        model_parameter_dtype_set=np.asarray([json.dumps(runtime_summary["model_parameter_dtype_set"], sort_keys=True)]),
        model_device_set=np.asarray([json.dumps(runtime_summary["model_device_set"], sort_keys=True)]),
        model_parameter_tensor_count=np.asarray([int(runtime_summary["model_parameter_tensor_count"])], dtype=np.int64),
        cuda_available=np.asarray([bool(runtime_summary["cuda_available"])]),
        cuda_device_count=np.asarray([int(runtime_summary["cuda_device_count"])], dtype=np.int64),
        cuda_device_name=np.asarray([str(runtime_summary["cuda_device_name"])]),
        cuda_device_capability=np.asarray([str(runtime_summary["cuda_device_capability"])]),
        timing_clock_contract=np.asarray([str(runtime_summary["timing_clock_contract"])]),
        timing_cpu_perf_counter_recorded=np.asarray([bool(runtime_summary["timing_cpu_perf_counter_recorded"])]),
        timing_cuda_synchronized=np.asarray([bool(runtime_summary["timing_cuda_synchronized"])]),
        timing_cuda_event_recorded=np.asarray([bool(runtime_summary["timing_cuda_event_recorded"])]),
        capture_elapsed_seconds=np.asarray([float(runtime_summary["capture_elapsed_seconds"])], dtype=np.float64),
        named_hardware_timing_measured=np.asarray([bool(runtime_summary["named_hardware_timing_measured"])]),
        runtime_provenance_verified=np.asarray([bool(runtime_provenance_verified)]),
        capture_offline_quarantine_contract=np.asarray([str(capture_network_quarantine.get("contract", ""))]),
        capture_offline_quarantine_set_before_runtime_import=np.asarray([bool(capture_network_quarantine.get("set_before_runtime_import"))]),
        capture_offline_quarantine_applied_json=np.asarray([_json_canonical_text(capture_network_quarantine.get("applied", {}))]),
        model_revision=np.asarray([model_revision]),
        tokenizer_revision=np.asarray([resolved_tokenizer_revision]),
        snapshot_digest_authenticity_contract=np.asarray([str(snapshot_digest_proof.get("contract", "missing"))]),
        snapshot_digest_authenticity_required=np.asarray([bool(snapshot_digest_proof.get("required", False))]),
        snapshot_digest_authenticity_verified=np.asarray([bool(snapshot_digest_proof.get("verified", False))]),
        loader_snapshot_binding_contract=np.asarray([str(snapshot_digest_proof.get("loader_snapshot_binding_contract", "missing"))]),
        loader_snapshot_binding_required=np.asarray([bool(args.require_loader_snapshot_bind)]),
        loader_snapshot_binding_verified=np.asarray([bool(snapshot_digest_proof.get("loader_snapshot_binding_verified", False))]),
        model_load_source_resolved_path=np.asarray([str(snapshot_digest_proof.get("model_load_source_resolved_path", ""))]),
        verified_snapshot_path=np.asarray([str(snapshot_digest_proof.get("verified_snapshot_path", ""))]),
        model_safetensors_sha256=np.asarray([str(snapshot_digest_proof.get("observed_model_safetensors_sha256", ""))]),
        expected_model_safetensors_sha256=np.asarray([str(snapshot_digest_proof.get("expected_model_safetensors_sha256", ""))]),
        model_safetensors_sha256_matches_expected=np.asarray([bool(snapshot_digest_proof.get("sha256_matches_expected", False))]),
        code_revision=np.asarray([code_revision]),
        trust_remote_code=np.asarray([bool(args.trust_remote_code)]),
        config_sha256=np.asarray([config_sha256]),
        adapter=np.asarray([capture["adapter"]]),
        attention_interface_backend=np.asarray([str(capture.get("attention_interface_backend", "not_applicable"))]),
        attention_interface_registry_wrapper_installed=np.asarray([bool(capture.get("attention_interface_registry_wrapper_installed", False))]),
        attention_mask_backend_preserved=np.asarray([bool(capture.get("attention_mask_backend_preserved", False))]),
        custom_attention_backend_used=np.asarray([bool(capture.get("custom_attention_backend_used", False))]),
        mask_challenge_exercised=np.asarray([bool(capture.get("mask_challenge_exercised", False))]),
        attention_mask_present_call_count=np.asarray([int(capture.get("attention_mask_present_call_count", 0))], dtype=np.int64),
        attention_mask_absent_call_count=np.asarray([int(capture.get("attention_mask_absent_call_count", 0))], dtype=np.int64),
        prompt_sha256=np.asarray([prompt_sha]),
        prompt_count=np.asarray([int(capture.get("prompt_count", len(prompts)))], dtype=np.int64),
        prompt_id=prompt_ids,
        token_provenance_contract=np.asarray([str(capture.get("token_provenance_contract", "missing_token_provenance_contract"))]),
        token_provenance_verified=np.asarray([bool(token_provenance_verified)]),
        prompt_token_count=prompt_token_count.astype(np.int64),
        prompt_attention_mask_sum=prompt_attention_mask_sum.astype(np.int64),
        prompt_input_ids_sha256=prompt_input_ids_sha256,
        prompt_attention_mask_sha256=prompt_attention_mask_sha256,
        prompt_text_sha256=prompt_text_sha256,
        prompt_token_count_min=np.asarray([int(np.min(prompt_token_count)) if prompt_token_count.size else 0], dtype=np.int64),
        prompt_token_count_max=np.asarray([int(np.max(prompt_token_count)) if prompt_token_count.size else 0], dtype=np.int64),
        generation_config_json=np.asarray([generation_config_json]),
        generation_config_sha256=np.asarray([generation_config_sha256]),
        generation_determinism_contract=np.asarray([generation_determinism_contract]),
        generation_determinism_verified=np.asarray([bool(generation_determinism_gate_verified)]),
        generation_strategy=np.asarray([generation_strategy]),
        generation_do_sample=np.asarray([bool(capture.get("generation_do_sample", False))]),
        generation_use_cache=np.asarray([bool(capture.get("generation_use_cache", int(args.decode_steps) > 0))]),
        cache_implementation_contract=np.asarray([cache_implementation_contract]),
        generation_cache_implementation=np.asarray([generation_cache_implementation]),
        generation_cache_implementation_source=np.asarray([generation_cache_implementation_source]),
        generation_cache_config_present=np.asarray([bool(generation_cache_config_present)]),
        generation_num_beams=np.asarray([generation_num_beams], dtype=np.int64),
        generation_num_return_sequences=np.asarray([generation_num_return_sequences], dtype=np.int64),
        generation_max_new_tokens=np.asarray([generation_max_new_tokens], dtype=np.int64),
        generation_min_new_tokens=np.asarray([generation_min_new_tokens], dtype=np.int64),
        generation_sampling_disabled=np.asarray([bool(generation_sampling_disabled)]),
        generation_exact_new_tokens_required=np.asarray([bool(generation_exact_new_tokens_required)]),
        generation_token_contract=np.asarray([str(capture.get("generation_token_contract", "missing_generation_token_contract"))]),
        generation_token_provenance_verified=np.asarray([bool(generation_token_provenance_verified)]),
        generated_sequence_sha256=generated_sequence_sha256,
        generated_new_token_ids_sha256=generated_new_token_ids_sha256,
        generated_new_token_count=generated_new_token_count.astype(np.int64),
        generated_new_token_count_min=np.asarray([int(np.min(generated_new_token_count)) if generated_new_token_count.size else 0], dtype=np.int64),
        generated_new_token_count_max=np.asarray([int(np.max(generated_new_token_count)) if generated_new_token_count.size else 0], dtype=np.int64),
        generated_new_token_exact_count_verified=np.asarray([bool(generated_new_token_exact_count_verified)]),
        generated_sequence_token_count=generated_sequence_token_count.astype(np.int64),
        generation_prompt_prefix_verified=generation_prompt_prefix_verified.astype(bool),
        position_policy=np.asarray([str(capture.get("position_policy", args.position_policy))]),
        position_contract=np.asarray([str(capture.get("position_contract", "local_query_position_v0"))]),
        absolute_position_verified=np.asarray([bool(capture.get("absolute_position_verified", False))]),
        rotary_position_contract=np.asarray([str(capture.get("rotary_position_contract", "missing_rotary_position_contract"))]),
        rotary_position_ids_verified=np.asarray([bool(rotary_position_ids_verified)]),
        rotary_position_ids_present_call_count=np.asarray([int(capture.get("rotary_position_ids_present_call_count", 0))], dtype=np.int64),
        decode_steps_requested=np.asarray([int(capture.get("decode_steps_requested", args.decode_steps))], dtype=np.int64),
        capture_phase=np.asarray(capture.get("capture_phase", ["prefill"] * q.shape[0])),
        valid_key_len=valid_key_len.astype(np.int64),
        query_len=np.asarray(capture.get("query_len", np.ones(q.shape[0], dtype=np.int64) * k.shape[1]), dtype=np.int64),
        active_key_len=active_key_len.astype(np.int64),
        kv_head=kv_head.astype(np.int64),
        num_attention_heads=num_attention_heads.astype(np.int64),
        num_key_value_heads=num_key_value_heads.astype(np.int64),
        num_key_value_groups=num_key_value_groups.astype(np.int64),
        kv_group_map_contract=np.asarray([str(capture.get("kv_group_map_contract", PUBLIC_KV_GROUP_CONTRACT))]),
        kv_group_map_verified=np.asarray([bool(kv_group_map_verified)]),
        gqa_grouped_rows_present=np.asarray([bool(gqa_grouped_rows_present)]),
        active_key_len_contract=np.asarray([str(capture.get("active_key_len_contract", PUBLIC_ACTIVE_KEY_CONTRACT))]),
        active_key_len_semantics_verified=np.asarray([bool(active_key_len_semantics_verified)]),
        capture_phase_contract=np.asarray([str(capture.get("capture_phase_contract", "prefill_only_v1"))]),
        prefill_phase_present=np.asarray([bool(capture.get("prefill_phase_present", True))]),
        decode_phase_present=np.asarray([bool(capture.get("decode_phase_present", False))]),
        cache_decode_verified=np.asarray([bool(capture.get("cache_decode_verified", False))]),
        valid_key_len_semantics_verified=np.asarray([bool(valid_key_len_semantics_verified)]),
        trace_claim_version=np.asarray([PUBLIC_TRACE_CLAIM_VERSION]),
        public_pretrained_trace_requested=np.asarray([bool(args.public_pretrained_trace)]),
        public_pretrained_trace=np.asarray([effective_public]),
        source_type=np.asarray([effective_source_type]),
        weights_source=np.asarray([args.weights_source]),
        license=np.asarray([args.license]),
        schema=np.asarray([PUBLIC_QKV_SCHEMA]),
        capture_tool=np.asarray([CAPTURE_TOOL_REL]),
        capture_tool_sha256=np.asarray([capture_tool_sha]),
        generated_from_local_tiny_model=np.asarray([bool(args.generated_from_local_tiny_model)]),
        uses_random_weights=np.asarray([bool(args.uses_random_weights)]),
        provenance_reviewed=np.asarray([bool(args.provenance_reviewed)]),
        attention_backend=np.asarray([args.attention_implementation]),
        attention_score_input_stage=np.asarray([capture["attention_score_input_stage"]]),
        attention_score_inputs_verified=np.asarray([bool(capture["attention_score_inputs_verified"])]),
        score_transform=np.asarray([capture["score_transform"]]),
        probability_contract=np.asarray([str(capture.get("probability_contract", PUBLIC_PROBABILITY_CONTRACT))]),
        probability_semantics_verified=np.asarray([bool(capture.get("probability_semantics_verified", False))]),
        attention_probability_dtype=np.asarray([str(capture.get("attention_probability_dtype", PUBLIC_ATTENTION_PROBABILITY_DTYPE))]),
        attention_dropout_p=np.asarray([float(capture.get("attention_dropout_p", 0.0))], dtype=np.float64),
        attention_training_state=np.asarray([bool(capture.get("attention_training_state", False))]),
        dropout_applied=np.asarray([bool(capture.get("dropout_applied", False))]),
        attention_scale=attention_scale,
        score_bias=score_bias,
        dense_reference_output=dense_reference_output,
        attention_scale_verified=np.asarray([bool(capture["attention_scale_verified"])]),
        score_bias_verified=np.asarray([bool(capture["score_bias_verified"])]),
        dense_reference_verified=np.asarray([bool(capture["dense_reference_verified"])]),
        dense_reference_max_abs_error=np.asarray([dense_error_value], dtype=np.float64),
    )
    trace_sha = sha256_file(args.out)

    provenance = {
        "trace_claim_version": PUBLIC_TRACE_CLAIM_VERSION,
        "public_pretrained_trace_requested": bool(args.public_pretrained_trace),
        "public_pretrained_trace": effective_public,
        "source_type": effective_source_type,
        "model_id": public_model_id,
        "model_load_source": args.model,
        "model_load_source_is_local_path": bool(model_load_source_is_local_path),
        "runtime_provenance_contract": runtime_summary["runtime_provenance_contract"],
        "requested_torch_dtype": runtime_summary["requested_torch_dtype"],
        "resolved_torch_dtype": runtime_summary["resolved_torch_dtype"],
        "requested_device_policy": runtime_summary["requested_device_policy"],
        "actual_primary_device": runtime_summary["actual_primary_device"],
        "model_parameter_dtype_set": runtime_summary["model_parameter_dtype_set"],
        "model_device_set": runtime_summary["model_device_set"],
        "model_parameter_tensor_count": runtime_summary["model_parameter_tensor_count"],
        "cuda_available": runtime_summary["cuda_available"],
        "cuda_device_count": runtime_summary["cuda_device_count"],
        "cuda_device_name": runtime_summary["cuda_device_name"],
        "cuda_device_capability": runtime_summary["cuda_device_capability"],
        "timing_clock_contract": runtime_summary["timing_clock_contract"],
        "timing_cpu_perf_counter_recorded": runtime_summary["timing_cpu_perf_counter_recorded"],
        "timing_cuda_synchronized": runtime_summary["timing_cuda_synchronized"],
        "timing_cuda_event_recorded": runtime_summary["timing_cuda_event_recorded"],
        "capture_elapsed_seconds": runtime_summary["capture_elapsed_seconds"],
        "named_hardware_timing_measured": runtime_summary["named_hardware_timing_measured"],
        "runtime_provenance_verified": bool(runtime_provenance_verified),
        "model_revision": model_revision,
        "tokenizer_revision": resolved_tokenizer_revision,
        "code_revision": code_revision,
        "trust_remote_code": bool(args.trust_remote_code),
        "snapshot_digest_authenticity_contract": str(snapshot_digest_proof.get("contract", "missing")),
        "snapshot_digest_authenticity_required": bool(snapshot_digest_proof.get("required", False)),
        "snapshot_digest_authenticity_verified": bool(snapshot_digest_proof.get("verified", False)),
        "loader_snapshot_binding_contract": str(snapshot_digest_proof.get("loader_snapshot_binding_contract", "missing")),
        "loader_snapshot_binding_required": bool(args.require_loader_snapshot_bind),
        "loader_snapshot_binding_verified": bool(snapshot_digest_proof.get("loader_snapshot_binding_verified", False)),
        "model_load_source_resolved_path": str(snapshot_digest_proof.get("model_load_source_resolved_path", "")),
        "verified_snapshot_path": str(snapshot_digest_proof.get("verified_snapshot_path", "")),
        "model_safetensors_sha256": str(snapshot_digest_proof.get("observed_model_safetensors_sha256", "")),
        "expected_model_safetensors_sha256": str(snapshot_digest_proof.get("expected_model_safetensors_sha256", "")),
        "model_safetensors_sha256_matches_expected": bool(snapshot_digest_proof.get("sha256_matches_expected", False)),
        "snapshot_digest_proof": snapshot_digest_proof,
        "weights_source": args.weights_source,
        "license": args.license,
        "trace_npz_sha256": trace_sha,
        "schema": PUBLIC_QKV_SCHEMA,
        "d_head": int(q.shape[-1]),
        "capture_tool": CAPTURE_TOOL_REL,
        "capture_tool_sha256": capture_tool_sha,
        "config_sha256": config_sha256,
        "generated_from_local_tiny_model": bool(args.generated_from_local_tiny_model),
        "uses_random_weights": bool(args.uses_random_weights),
        "provenance_reviewed": bool(args.provenance_reviewed),
        "adapter": capture["adapter"],
        "attention_interface_backend": capture.get("attention_interface_backend", "not_applicable"),
        "attention_interface_registry_wrapper_installed": bool(capture.get("attention_interface_registry_wrapper_installed", False)),
        "attention_mask_backend_preserved": bool(capture.get("attention_mask_backend_preserved", False)),
        "custom_attention_backend_used": bool(capture.get("custom_attention_backend_used", False)),
        "mask_challenge_exercised": bool(capture.get("mask_challenge_exercised", False)),
        "attention_mask_present_call_count": int(capture.get("attention_mask_present_call_count", 0)),
        "attention_mask_absent_call_count": int(capture.get("attention_mask_absent_call_count", 0)),
        "attention_interface_install_status": capture.get("attention_interface_install_status"),
        "attention_backend": args.attention_implementation,
        "attention_score_input_stage": capture["attention_score_input_stage"],
        "attention_score_inputs_verified": bool(capture["attention_score_inputs_verified"]),
        "score_transform": capture["score_transform"],
        "probability_contract": str(capture.get("probability_contract", PUBLIC_PROBABILITY_CONTRACT)),
        "probability_semantics_verified": bool(capture.get("probability_semantics_verified", False)),
        "attention_probability_dtype": str(capture.get("attention_probability_dtype", PUBLIC_ATTENTION_PROBABILITY_DTYPE)),
        "attention_dropout_p": float(capture.get("attention_dropout_p", 0.0)),
        "attention_training_state": bool(capture.get("attention_training_state", False)),
        "dropout_applied": bool(capture.get("dropout_applied", False)),
        "attention_scale_verified": bool(capture["attention_scale_verified"]),
        "score_bias_verified": bool(capture["score_bias_verified"]),
        "dense_reference_verified": bool(capture["dense_reference_verified"]),
        "dense_reference_max_abs_error": capture["dense_reference_max_abs_error"],
        "fidelity_note": capture["fidelity_note"],
        "prompt_sha256": prompt_sha,
        "prompt_count": int(capture.get("prompt_count", len(prompts))),
        "prompt_manifest_contract": str(capture.get("prompt_manifest_contract", PUBLIC_PROMPT_MANIFEST_CONTRACT)),
        "prompt_manifest_json": str(capture.get("prompt_manifest_json", "")),
        "prompt_manifest_sha256": str(capture.get("prompt_manifest_sha256", "")),
        "tokenization_settings_json": str(capture.get("tokenization_settings_json", "")),
        "tokenization_settings_sha256": str(capture.get("tokenization_settings_sha256", "")),
        "tokenization_add_special_tokens": bool(capture.get("tokenization_add_special_tokens", True)),
        "tokenization_padding": str(capture.get("tokenization_padding", "false")),
        "tokenization_truncation": str(capture.get("tokenization_truncation", "false")),
        "tokenization_return_attention_mask": bool(capture.get("tokenization_return_attention_mask", True)),
        "tokenization_return_tensors": str(capture.get("tokenization_return_tensors", "pt")),
        "chat_template_applied": bool(capture.get("chat_template_applied", False)),
        "tokenizer_class": str(capture.get("tokenizer_class", "unknown")),
        "tokenizer_is_fast": bool(capture.get("tokenizer_is_fast", False)),
        "tokenizer_padding_side": str(capture.get("tokenizer_padding_side", "unknown")),
        "tokenizer_truncation_side": str(capture.get("tokenizer_truncation_side", "unknown")),
        "token_provenance_contract": str(capture.get("token_provenance_contract", "missing_token_provenance_contract")),
        "token_provenance_verified": bool(token_provenance_verified),
        "prompt_token_count": [int(x) for x in prompt_token_count.tolist()],
        "prompt_token_count_min": int(np.min(prompt_token_count)) if prompt_token_count.size else 0,
        "prompt_token_count_max": int(np.max(prompt_token_count)) if prompt_token_count.size else 0,
        "prompt_attention_mask_sum": [int(x) for x in prompt_attention_mask_sum.tolist()],
        "prompt_input_ids_sha256": [str(x) for x in prompt_input_ids_sha256.tolist()],
        "prompt_attention_mask_sha256": [str(x) for x in prompt_attention_mask_sha256.tolist()],
        "prompt_text_sha256": [str(x) for x in prompt_text_sha256.tolist()],
        "generation_config_json": generation_config_json,
        "generation_config_sha256": generation_config_sha256,
        "generation_determinism_contract": generation_determinism_contract,
        "generation_determinism_verified": bool(generation_determinism_gate_verified),
        "generation_strategy": generation_strategy,
        "generation_do_sample": bool(capture.get("generation_do_sample", False)),
        "generation_use_cache": bool(capture.get("generation_use_cache", int(args.decode_steps) > 0)),
        "cache_implementation_contract": cache_implementation_contract,
        "generation_cache_implementation": generation_cache_implementation,
        "generation_cache_implementation_source": generation_cache_implementation_source,
        "generation_cache_config_present": bool(generation_cache_config_present),
        "generation_num_beams": int(generation_num_beams),
        "generation_num_return_sequences": int(generation_num_return_sequences),
        "generation_max_new_tokens": int(generation_max_new_tokens),
        "generation_min_new_tokens": int(generation_min_new_tokens),
        "generation_sampling_disabled": bool(generation_sampling_disabled),
        "generation_exact_new_tokens_required": bool(generation_exact_new_tokens_required),
        "generation_token_contract": str(capture.get("generation_token_contract", "missing_generation_token_contract")),
        "generation_token_provenance_verified": bool(generation_token_provenance_verified),
        "generated_sequence_sha256": [str(x) for x in generated_sequence_sha256.tolist()],
        "generated_new_token_ids_sha256": [str(x) for x in generated_new_token_ids_sha256.tolist()],
        "generated_new_token_count": [int(x) for x in generated_new_token_count.tolist()],
        "generated_new_token_count_min": int(np.min(generated_new_token_count)) if generated_new_token_count.size else 0,
        "generated_new_token_count_max": int(np.max(generated_new_token_count)) if generated_new_token_count.size else 0,
        "generated_new_token_exact_count_verified": bool(generated_new_token_exact_count_verified),
        "generated_sequence_token_count": [int(x) for x in generated_sequence_token_count.tolist()],
        "generation_prompt_prefix_verified": [bool(x) for x in generation_prompt_prefix_verified.tolist()],
        "position_policy": str(capture.get("position_policy", args.position_policy)),
        "active_key_len_contract": str(capture.get("active_key_len_contract", PUBLIC_ACTIVE_KEY_CONTRACT)),
        "active_key_len_semantics_verified": bool(active_key_len_semantics_verified),
        "kv_group_map_contract": str(capture.get("kv_group_map_contract", PUBLIC_KV_GROUP_CONTRACT)),
        "kv_group_map_verified": bool(kv_group_map_verified),
        "gqa_grouped_rows_present": bool(gqa_grouped_rows_present),
        "num_attention_heads_min": int(np.min(num_attention_heads)),
        "num_attention_heads_max": int(np.max(num_attention_heads)),
        "num_key_value_heads_min": int(np.min(num_key_value_heads)),
        "num_key_value_heads_max": int(np.max(num_key_value_heads)),
        "num_key_value_groups_min": int(np.min(num_key_value_groups)),
        "num_key_value_groups_max": int(np.max(num_key_value_groups)),
        "position_contract": str(capture.get("position_contract", "local_query_position_v0")),
        "absolute_position_verified": bool(capture.get("absolute_position_verified", False)),
        "rotary_position_contract": str(capture.get("rotary_position_contract", "missing_rotary_position_contract")),
        "rotary_position_ids_verified": bool(rotary_position_ids_verified),
        "rotary_position_ids_present_call_count": int(capture.get("rotary_position_ids_present_call_count", 0)),
        "decode_steps_requested": int(capture.get("decode_steps_requested", args.decode_steps)),
        "capture_phase_contract": str(capture.get("capture_phase_contract", "prefill_only_v1")),
        "prefill_phase_present": bool(capture.get("prefill_phase_present", True)),
        "decode_phase_present": bool(capture.get("decode_phase_present", False)),
        "cache_decode_verified": bool(capture.get("cache_decode_verified", False)),
        "valid_key_len_semantics_verified": bool(valid_key_len_semantics_verified),
        "valid_key_len_min": int(np.min(valid_key_len)),
        "valid_key_len_max": int(np.max(valid_key_len)),
        "active_key_len_min": int(np.min(active_key_len)),
        "active_key_len_max": int(np.max(active_key_len)),
        "local_files_only": local_only,
        "capture_offline_quarantine_contract": capture_network_quarantine.get("contract"),
        "capture_offline_quarantine_applied": capture_network_quarantine.get("applied"),
        "capture_offline_quarantine_set_before_runtime_import": bool(capture_network_quarantine.get("set_before_runtime_import")),
        "capture_offline_quarantine_modules_already_imported": capture_network_quarantine.get("hf_modules_already_imported_before_quarantine", []),
        "device": device,
        "python_version": platform.python_version(),
        "torch_version": getattr(torch, "__version__", "unknown"),
        "transformers_version": getattr(transformers, "__version__", "unknown"),
        "public_claim_refusal_reasons": [
            reason
            for reason, failed in [
                ("score_inputs_scale_bias_mask_challenge_dense_output_or_parity_not_verified", not fidelity_verified),
                ("float32_softmax_no_dropout_probability_contract_not_verified", capture.get("probability_semantics_verified") is not True),
                ("prefill_plus_cached_decode_phase_active_key_kv_group_or_rope_position_contract_not_verified", not phase_contract_verified),
                ("prompt_token_input_ids_attention_mask_provenance_not_verified", not token_provenance_verified),
                ("generated_token_sequence_exact_length_provenance_not_verified", not generation_token_provenance_verified),
                ("immutable_model_tokenizer_or_code_provenance_incomplete", not provenance_complete),
                ("model_safetensors_digest_authenticity_not_verified", not snapshot_digest_verified),
                ("loader_snapshot_binding_not_verified", not loader_snapshot_binding_verified),
                ("runtime_device_dtype_timing_provenance_not_verified", not runtime_provenance_verified),
            ]
            if args.public_pretrained_trace and failed
        ],
        "warning": "Projection-hook captures are diagnostic. The public gate requires post-model Q/K transforms, verified scale/bias/mask score semantics, an exercised causal-mask challenge row, explicit runtime RoPE position_ids, exact prompt manifest plus tokenizer input_ids/attention_mask digests, generated-token sequence digests, query-head to KV-head mapping, immutable model/tokenizer/code identity, and recomputed dense-reference parity.",
    }
    if args.provenance_out is not None:
        args.provenance_out.parent.mkdir(parents=True, exist_ok=True)
        args.provenance_out.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "captured_public_claim_ready" if effective_public else (
        "captured_diagnostic_public_claim_refused" if args.public_pretrained_trace else "captured_diagnostic_nonpublic"
    )
    print(json.dumps({
        "status": status,
        "adapter": capture["adapter"],
        "attention_interface_backend": capture.get("attention_interface_backend", "not_applicable"),
        "attention_interface_registry_wrapper_installed": bool(capture.get("attention_interface_registry_wrapper_installed", False)),
        "attention_score_input_stage": capture["attention_score_input_stage"],
        "attention_score_inputs_verified": capture["attention_score_inputs_verified"],
        "attention_scale_verified": capture["attention_scale_verified"],
        "score_bias_verified": capture["score_bias_verified"],
        "score_transform": capture["score_transform"],
        "probability_contract": str(capture.get("probability_contract", PUBLIC_PROBABILITY_CONTRACT)),
        "probability_semantics_verified": bool(capture.get("probability_semantics_verified", False)),
        "attention_probability_dtype": str(capture.get("attention_probability_dtype", PUBLIC_ATTENTION_PROBABILITY_DTYPE)),
        "attention_dropout_p": float(capture.get("attention_dropout_p", 0.0)),
        "dense_reference_verified": capture["dense_reference_verified"],
        "capture_phase_contract": capture.get("capture_phase_contract", "prefill_only_v1"),
        "decode_phase_present": bool(capture.get("decode_phase_present", False)),
        "cache_decode_verified": bool(capture.get("cache_decode_verified", False)),
        "valid_key_len_semantics_verified": bool(valid_key_len_semantics_verified),
        "active_key_len_semantics_verified": bool(active_key_len_semantics_verified),
        "kv_group_map_contract": str(capture.get("kv_group_map_contract", PUBLIC_KV_GROUP_CONTRACT)),
        "kv_group_map_verified": bool(kv_group_map_verified),
        "gqa_grouped_rows_present": bool(gqa_grouped_rows_present),
        "position_contract": str(capture.get("position_contract", "local_query_position_v0")),
        "absolute_position_verified": bool(capture.get("absolute_position_verified", False)),
        "rotary_position_contract": str(capture.get("rotary_position_contract", "missing_rotary_position_contract")),
        "rotary_position_ids_verified": bool(rotary_position_ids_verified),
        "rotary_position_ids_present_call_count": int(capture.get("rotary_position_ids_present_call_count", 0)),
        "model": args.model,
        "public_model_id": public_model_id,
        "model_load_source_is_local_path": bool(model_load_source_is_local_path),
        "runtime_provenance_contract": runtime_summary["runtime_provenance_contract"],
        "requested_torch_dtype": runtime_summary["requested_torch_dtype"],
        "resolved_torch_dtype": runtime_summary["resolved_torch_dtype"],
        "requested_device_policy": runtime_summary["requested_device_policy"],
        "actual_primary_device": runtime_summary["actual_primary_device"],
        "runtime_provenance_verified": bool(runtime_provenance_verified),
        "capture_elapsed_seconds": float(runtime_summary["capture_elapsed_seconds"]),
        "model_revision": model_revision,
        "out": args.out.as_posix(),
        "provenance_out": args.provenance_out.as_posix() if args.provenance_out else None,
        "rows": int(q.shape[0]),
        "n": int(k.shape[1]),
        "d": int(q.shape[-1]),
        "dv": int(v.shape[-1]),
        "device": device,
        "public_pretrained_trace_requested": bool(args.public_pretrained_trace),
        "public_pretrained_trace_written": effective_public,
        "trace_npz_sha256": trace_sha,
        "next_step": "Use --decode-steps > 0 with an immutable public checkpoint, then pass the gate with prefill_plus_cached_decode phase coverage, mask-derived active_key_len, absolute active-key decode positions, float32/no-dropout probability semantics, runtime RoPE position_ids, exact prompt manifest plus tokenizer input_ids/attention_mask digests, generated-token sequence digests, and query-head to KV-head group mapping before requesting public/pretrained acceptance.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
