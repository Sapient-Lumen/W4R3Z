#!/usr/bin/env python3
from __future__ import annotations

import importlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = META.get("revision", "rev0091")
REVUP = REV.upper()
OUT_AUDIT = ROOT / "artifacts" / "audit"
OUT_CAPTURE = ROOT / "artifacts" / "capture-kit"
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
OUT_CAPTURE.mkdir(parents=True, exist_ok=True)
CAPTURE = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"


def optional_dep(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)
    out: dict[str, Any] = {"available": bool(spec), "origin": getattr(spec, "origin", None) if spec else None}
    if not spec:
        return out
    try:
        module = importlib.import_module(name)
        out["version"] = getattr(module, "__version__", "unknown")
    except Exception as exc:
        out["available"] = False
        out["import_error"] = repr(exc)
    return out


def torch_runtime() -> dict[str, Any]:
    info = optional_dep("torch")
    if not info.get("available"):
        return info
    try:
        import torch  # type: ignore
        info.update({
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
            "cuda_device_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else [],
        })
    except Exception as exc:
        info["runtime_error"] = repr(exc)
    return info


def cache_roots() -> list[Path]:
    roots: list[Path] = []
    env = os.environ.get("HF_HOME")
    if env:
        roots.append(Path(env) / "hub")
    env_cache = os.environ.get("HUGGINGFACE_HUB_CACHE")
    if env_cache:
        roots.append(Path(env_cache))
    roots.extend([
        Path.home() / ".cache" / "huggingface" / "hub",
        Path("/root/.cache/huggingface/hub"),
        Path("/mnt/data/.cache/huggingface/hub"),
    ])
    dedup: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = root.as_posix()
        if key not in seen:
            seen.add(key)
            dedup.append(root)
    return dedup


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def snapshot_model_id(repo_dir_name: str) -> str:
    # Hugging Face cache dirs look like models--org--repo.
    text = repo_dir_name
    if text.startswith("models--"):
        text = text[len("models--"):]
    return text.replace("--", "/")


def scan_cached_snapshots() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for root in cache_roots():
        if not root.exists():
            continue
        for repo in sorted(root.glob("models--*")):
            snaps = repo / "snapshots"
            if not snaps.exists():
                continue
            for snap in sorted(snaps.iterdir()):
                if not snap.is_dir():
                    continue
                cfg_path = snap / "config.json"
                cfg = read_json(cfg_path)
                if cfg is None:
                    continue
                arch = cfg.get("architectures") or []
                arch_text = " ".join(str(x) for x in (arch if isinstance(arch, list) else [arch])).lower()
                model_type = str(cfg.get("model_type", "")).lower()
                is_llama_like = bool(model_type in {"llama", "mllama"} or "llama" in arch_text)
                weights = sorted([p.name for p in snap.glob("*.safetensors")]) + sorted([p.name for p in snap.glob("pytorch_model*.bin")])
                tokenizer_files = [name for name in ["tokenizer.json", "tokenizer.model", "tokenizer_config.json", "special_tokens_map.json"] if (snap / name).exists()]
                license_files = [p.name for p in snap.iterdir() if p.name.lower() in {"license", "license.md", "copying"}]
                candidates.append({
                    "model_id": snapshot_model_id(repo.name),
                    "snapshot_path": snap.as_posix(),
                    "revision": snap.name,
                    "revision_looks_immutable": len(snap.name) in {40, 64} and all(c in "0123456789abcdefABCDEF" for c in snap.name),
                    "model_type": model_type,
                    "architectures": arch,
                    "is_llama_like": is_llama_like,
                    "has_config": True,
                    "weight_file_count": len(weights),
                    "weight_files_sample": weights[:5],
                    "tokenizer_file_count": len(tokenizer_files),
                    "tokenizer_files": tokenizer_files,
                    "license_files": license_files,
                    "ready_for_capture_attempt": bool(is_llama_like and weights and tokenizer_files),
                })
    return candidates


def source_checks() -> dict[str, bool]:
    capture = CAPTURE.read_text(encoding="utf-8", errors="replace")
    gate = GATE.read_text(encoding="utf-8", errors="replace")
    return {
        "capture_helper_exists": CAPTURE.exists(),
        "gate_exists": GATE.exists(),
        "eager_registry_override_present": "_install_llama_attention_capture_wrapper" in capture and 'backend_name = "eager"' in capture and "eager_registry_overridden" in capture,
        "custom_attention_backend_not_used": "custom_attention_backend_used" in capture and "cloudtainer_trace_eager" not in capture,
        "module_fallback_patch_present": "llama_mod.eager_attention_forward = wrapped_eager" in capture,
        "capture_reports_attention_interface_backend": "attention_interface_backend" in capture,
        "mask_backend_preservation_exported": "attention_mask_backend_preserved" in capture and "attention_mask_backend_preserved" in gate,
        "mask_challenge_required": "mask_challenge_exercised" in capture and "mask_challenge_exercised" in gate and "score_inputs_scale_bias_mask_challenge" in capture,
        "dense_reference_export_present": "dense_reference_output=dense_reference_output" in capture,
        "public_claim_requires_fidelity_and_provenance": "args.public_pretrained_trace and fidelity_verified and provenance_complete" in capture,
        "projection_fallback_nonpublic": "cannot self-attest as public/pretrained" in capture and "hf_projection_capture_unverified" in capture,
        "gate_recomputes_dense_reference": "verify_qkv_score_contract" in gate and "computed_dense_reference_max_abs_error" in gate,
        "gate_rejects_mutable_revisions": "model_revision must be an immutable" in gate and "tokenizer_revision must be an immutable" in gate,
        "cached_decode_cli_present": "--decode-steps" in capture and "model.generate(" in capture and "use_cache=True" in capture,
        "phase_contract_required": "PUBLIC_CAPTURE_PHASE_CONTRACT" in capture and "capture_phase_contract" in gate and "decode_phase_present" in gate,
        "valid_key_len_required": "valid_key_len" in capture and "valid_key_len" in gate and "valid_key_len_padding_rows" in gate,
        "absolute_position_required": "position_contract" in capture and "absolute_position_verified" in gate and "position_contract_verified" in gate,
        "active_key_len_contract_required": "PUBLIC_ACTIVE_KEY_CONTRACT" in capture and "active_key_len" in capture and "active_key_len_semantics_verified" in gate and "active_key_len_contract_verified" in gate,
        "static_cache_physical_width_not_active": "physical-cache-width" in capture and "active_len - q_len" in capture and "masked causal/static-cache tokens" in gate,
        "decode_position_absolute_not_local": "query_start_position" in capture and "active_i - 1" in gate,
        "kv_group_map_contract_required": "PUBLIC_KV_GROUP_CONTRACT" in capture and "PUBLIC_KV_GROUP_CONTRACT" in gate and "kv_head" in capture and "kv_head/num_attention_heads" in gate,
        "kv_group_map_recomputed_by_gate": "verify_kv_group_map_contract" in gate and "query-head to KV-head group map contract was not verified" in gate,
        "gqa_group_map_audit_present": (ROOT / "tools" / "public_trace_kv_group_audit.py").exists(),
        "probability_contract_required": "PUBLIC_PROBABILITY_CONTRACT" in capture and "PUBLIC_PROBABILITY_CONTRACT" in gate and "probability_semantics_verified" in capture and "probability_semantics_verified" in gate,
        "probability_dtype_float32_required": "attention_probability_dtype" in capture and "attention_probability_dtype" in gate and "float32_softmax_no_dropout_v1" in capture and "float32_softmax_no_dropout_v1" in gate,
        "dropout_zero_eval_required": "attention_dropout_p" in capture and "attention_training_state" in capture and "dropout_applied" in capture and "attention_dropout_p must be zero" in gate,
        "probability_semantics_audit_present": (ROOT / "tools" / "public_trace_probability_semantics_audit.py").exists(),
        "rotary_position_contract_required": "PUBLIC_ROTARY_POSITION_CONTRACT" in capture and "PUBLIC_ROTARY_POSITION_CONTRACT" in gate and "rotary_position_id" in capture and "rotary_position_id" in gate and "rotary_position_ids_verified" in gate,
        "runtime_rope_position_ids_observed": "rotary_position_ids_present_call_count" in capture and "runtime RoPE position_ids were not observed" in gate,
        "rotary_position_audit_present": (ROOT / "tools" / "public_trace_rotary_position_audit.py").exists(),
        "token_provenance_contract_required": "PUBLIC_TOKEN_PROVENANCE_CONTRACT" in capture and "PUBLIC_TOKEN_PROVENANCE_CONTRACT" in gate and "prompt_input_ids_sha256" in capture and "prompt_attention_mask_sha256" in gate and "token_provenance_verified" in gate,
        "prompt_manifest_contract_required": "PUBLIC_PROMPT_MANIFEST_CONTRACT" in capture and "PUBLIC_PROMPT_MANIFEST_CONTRACT" in gate and "prompt_manifest_json" in capture and "verify_prompt_manifest_contract" in gate,
        "tokenizer_call_explicit_no_padding_no_truncation": "add_special_tokens=True" in capture and "padding=False" in capture and "truncation=False" in capture and "return_attention_mask=True" in capture,
        "token_provenance_audit_present": (ROOT / "tools" / "public_trace_token_provenance_audit.py").exists(),
        "generation_token_provenance_contract_required": "PUBLIC_GENERATION_TOKEN_CONTRACT" in capture and "PUBLIC_GENERATION_TOKEN_CONTRACT" in gate and "generated_new_token_ids_sha256" in capture and "generated_new_token_ids_sha256" in gate and "generation_token_provenance_verified" in gate,
        "generation_token_provenance_audit_present": (ROOT / "tools" / "public_trace_generation_token_audit.py").exists(),
        "generation_determinism_contract_required": "PUBLIC_GENERATION_DETERMINISM_CONTRACT" in capture and "PUBLIC_GENERATION_DETERMINISM_CONTRACT" in gate and "generation_num_beams" in capture and "generation_num_beams" in gate and "verify_generation_determinism_contract" in gate,
        "generation_determinism_audit_present": (ROOT / "tools" / "public_trace_generation_determinism_audit.py").exists(),
        "generation_call_forces_greedy_single_beam": "num_beams=1" in capture and "num_return_sequences=1" in capture and "do_sample=False" in capture,
        "generation_call_forces_exact_new_token_count": "min_new_tokens=int(decode_steps)" in capture and "generation_min_new_tokens" in gate and "generated_new_token_count must equal decode_steps_requested" in gate,
        "public_gate_requires_decode_steps": "decode_steps_requested must be positive" in gate or "decode_steps_requested must be a positive integer" in gate,
    }


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    deps = {
        "python": {"version": sys.version.split()[0], "platform": platform.platform()},
        "torch": torch_runtime(),
        "transformers": optional_dep("transformers"),
        "huggingface_hub": optional_dep("huggingface_hub"),
        "safetensors": optional_dep("safetensors"),
    }
    checks = source_checks()
    for name, ok in checks.items():
        if not ok:
            errors.append(f"source check failed: {name}")
    snapshots = scan_cached_snapshots()
    ready_snapshots = [s for s in snapshots if s.get("ready_for_capture_attempt")]
    llama_ready = [s for s in ready_snapshots if s.get("is_llama_like") and s.get("revision_looks_immutable")]
    blockers: list[str] = []
    if not deps["transformers"].get("available"):
        blockers.append("transformers_dependency_absent")
    if not deps["torch"].get("available"):
        blockers.append("torch_dependency_absent")
    if not ready_snapshots:
        blockers.append("no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected")
    if ready_snapshots and not llama_ready:
        blockers.append("cached_snapshots_found_but_no_immutable_llama_like_ready_snapshot")
    if not deps["torch"].get("cuda_available"):
        blockers.append("cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule")

    recommended_commands: list[str] = []
    if llama_ready:
        cand = llama_ready[0]
        recommended_commands = [
            "python tools/public_trace_token_provenance_audit.py",
            "python tools/public_trace_generation_token_audit.py",
            "python tools/public_trace_generation_determinism_audit.py",
            "python tools/public_trace_capture_readiness_audit.py",
            (
                "python experiments/public_trace_capture/hf_attention_trace_capture.py "
                f"--model {cand['model_id']} --model-revision {cand['revision']} --tokenizer-revision {cand['revision']} "
                "--prompt 'The quick brown fox jumps over the lazy dog.' --prompt 'Summarize why sparse attention is risky.' "
                "--position-policy last_and_mid --decode-steps 2 --max-rows 128 --public-pretrained-trace --provenance-reviewed "
                "--weights-source '<reviewed source URL or local snapshot>' --license '<reviewed license/source terms>' "
                f"--out artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz "
                f"--provenance-out artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json"
            ),
            (
                "python experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py "
                f"--trace-npz artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz --public-pretrained-trace "
                f"--provenance-json artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json "
                f"--out artifacts/probe-results/{REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json"
            ),
        ]

    status = "fail" if errors else ("ready_to_run_cached_capture" if llama_ready and deps["transformers"].get("available") else "pass_with_blockers")
    report = {
        "project": "CloudtainerML",
        "revision": REV,
        "report": "public_trace_capture_readiness_audit",
        "generated_at": META.get("generated_at"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "dependency_status": deps,
        "hf_cache_roots_checked": [p.as_posix() for p in cache_roots()],
        "cached_snapshot_count": len(snapshots),
        "ready_cached_snapshot_count": len(ready_snapshots),
        "immutable_llama_like_ready_snapshot_count": len(llama_ready),
        "ready_snapshot_sample": ready_snapshots[:10],
        "source_checks": checks,
        "blockers": blockers,
        "errors": errors,
        "warnings": warnings,
        "recommended_commands": recommended_commands,
        "interpretation": (
            "This is an execution readiness audit for the riskiest trace lane. It hard-fails source regressions, verifies the v13 prompt-plus-generated-token-plus-greedy-exact-length-generation seam, scans the local HF cache for immutable Llama-like snapshots, "
            "and records why the capsule can or cannot run the real public/pretrained post-transform prefill+decode capture now. It requires absolute active-key decode positions, mask-derived active_key_len semantics, explicit query-head to compact-KV-head ownership, float32 softmax/no-dropout probability semantics, observed runtime RoPE position_ids, and exact prompt manifest plus tokenizer input_ids/attention_mask digests and generated-token sequence digests, exact requested new-token counts, and greedy single-beam generation settings so physical cache width, duplicated per-query K/V rows, local cached-decode position labels, training-time dropout, or unreplayable prompt/generated-token streams, early-stop decode truncation, or inherited beam/sampling generation configs cannot masquerade as public runtime evidence. It does not promote any trace."
        ),
    }
    (OUT_AUDIT / f"{REVUP}_PUBLIC_TRACE_CAPTURE_READINESS_AUDIT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        f"# Public trace capture readiness — {REV}",
        "",
        f"**Status:** {status}",
        "",
        report["interpretation"],
        "",
        "## Current blockers",
        "",
    ]
    if blockers:
        lines.extend(f"- `{b}`" for b in blockers)
    else:
        lines.append("- none detected before capture execution")
    lines.extend([
        "",
        "## Runtime/dependency facts",
        "",
        f"- transformers available: `{deps['transformers'].get('available')}`",
        f"- torch available: `{deps['torch'].get('available')}`",
        f"- CUDA available: `{deps['torch'].get('cuda_available')}`",
        f"- cached snapshot count: `{len(snapshots)}`",
        f"- immutable Llama-like ready snapshots: `{len(llama_ready)}`",
        "",
        "## Next command",
        "",
    ])
    if recommended_commands:
        lines.append("```bash")
        lines.extend(recommended_commands)
        lines.append("```")
    else:
        lines.append("Run `python tools/public_trace_token_provenance_audit.py`, `python tools/public_trace_generation_token_audit.py`, and `python tools/public_trace_generation_determinism_audit.py`, then install/provide `transformers` plus an immutable cached public Llama-family snapshot, and rerun `python tools/public_trace_capture_readiness_audit.py`. The real capture command must include `--decode-steps 2` or another positive decode count.")
    (OUT_CAPTURE / f"{REVUP}_PUBLIC_TRACE_CAPTURE_READINESS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    script = f'''#!/usr/bin/env bash
set -euo pipefail

# {REV} minimal execution path. This script intentionally does not download by
# default. Set MODEL_ID/MODEL_REVISION/TOKENIZER_REVISION after provenance review,
# or run the readiness audit first to discover a cached immutable snapshot.
# Public acceptance requires prefill plus cached-decode rows, finite mask/valid
# length semantics, mask-derived active_key_len, absolute active-key position
# labels for q_len=1 decode rows, GQA/MQA query-head to KV-head ownership,
# observed runtime RoPE position_ids, exact tokenizer input_ids/attention_mask
# digests, exact generated-token sequence digests, forced greedy single-beam
# generation settings with min_new_tokens=max_new_tokens=DECODE_STEPS, exact generated-new-token count, and float32 softmax/no-dropout probability semantics.

python tools/public_trace_token_provenance_audit.py
python tools/public_trace_generation_token_audit.py
python tools/public_trace_generation_determinism_audit.py
python tools/public_trace_capture_readiness_audit.py

: "${{MODEL_ID:?set MODEL_ID to a reviewed HF model id or local model path}}"
: "${{MODEL_REVISION:?set MODEL_REVISION to a full immutable commit/content hash}}"
: "${{TOKENIZER_REVISION:=$MODEL_REVISION}}"
: "${{WEIGHTS_SOURCE:?set WEIGHTS_SOURCE to the reviewed source URL or local snapshot description}}"
: "${{LICENSE:?set LICENSE to reviewed license/source terms}}"
: "${{DECODE_STEPS:=2}}"

if [ "$DECODE_STEPS" -le 0 ]; then
  echo "DECODE_STEPS must be positive for {REV} public trace acceptance" >&2
  exit 2
fi

OUT_NPZ="artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz"
OUT_PROV="artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json"
OUT_GATE="artifacts/probe-results/{REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json"

python experiments/public_trace_capture/hf_attention_trace_capture.py \
  --model "$MODEL_ID" \
  --model-revision "$MODEL_REVISION" \
  --tokenizer-revision "$TOKENIZER_REVISION" \
  --prompt "The quick brown fox jumps over the lazy dog." \
  --prompt "Summarize why sparse attention claims need exact score-path, cache, mask, active-key, position, KV-group, RoPE-position, token-provenance, and probability evidence." \
  --position-policy last_and_mid \
  --decode-steps "$DECODE_STEPS" \
  --max-rows 128 \
  --public-pretrained-trace \
  --provenance-reviewed \
  --weights-source "$WEIGHTS_SOURCE" \
  --license "$LICENSE" \
  --out "$OUT_NPZ" \
  --provenance-out "$OUT_PROV"

python experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py \
  --trace-npz "$OUT_NPZ" \
  --public-pretrained-trace \
  --provenance-json "$OUT_PROV" \
  --trace-source-label public_llama_post_transform_prefill_cached_decode_active_key_kv_group_rope_probability_prompt_generation_token_determinism_capture \
  --bundle-model-id "$MODEL_ID" \
  --bundle-license "$LICENSE" \
  --out "$OUT_GATE"
'''
    script_path = OUT_CAPTURE / f"{REVUP}_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh"
    script_path.write_text(script, encoding="utf-8")
    script_path.chmod(0o755)

    print(json.dumps({"status": status, "blockers": blockers, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
