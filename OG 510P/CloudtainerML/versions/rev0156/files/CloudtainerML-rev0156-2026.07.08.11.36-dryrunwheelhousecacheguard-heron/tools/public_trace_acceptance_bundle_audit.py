#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0105"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

CAPTURE = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
GATE = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
README_FILES = ["START_HERE.md", "START_HERE_SLIM.md", "README.md", "PRIORITY-LIST.md", "MISSION-KERNEL.md"]

# Fields needed for an accepted public trace to be evaluation-ready, not merely captured.
# These are deliberately repeated here instead of imported from the gate so the audit can
# catch drift in the gate itself.
FIELD_GROUPS: dict[str, list[str]] = {
    "core_qkv_and_rows": [
        "q", "k", "v", "schema", "trace_claim_version", "public_pretrained_trace",
        "source_type", "layer", "head", "position", "d_head",
    ],
    "public_source_identity": [
        "model_id", "model_load_source", "model_load_source_is_local_path",
        "model_revision", "tokenizer_revision", "code_revision", "trust_remote_code",
        "weights_source", "license", "config_sha256", "capture_tool", "capture_tool_sha256",
        "generated_from_local_tiny_model", "uses_random_weights", "provenance_reviewed",
    ],
    "runtime_device_dtype_timing": [
        "runtime_provenance_contract", "requested_torch_dtype", "resolved_torch_dtype",
        "requested_device_policy", "actual_primary_device", "model_parameter_dtype_set",
        "model_device_set", "model_parameter_tensor_count", "cuda_available", "cuda_device_count",
        "cuda_device_name", "cuda_device_capability", "timing_clock_contract",
        "timing_cpu_perf_counter_recorded", "timing_cuda_synchronized", "timing_cuda_event_recorded",
        "capture_elapsed_seconds", "named_hardware_timing_measured", "runtime_provenance_verified",
    ],
    "prompt_and_tokenizer_replay": [
        "prompt_manifest_contract", "prompt_manifest_json", "prompt_manifest_sha256",
        "tokenization_settings_json", "tokenization_settings_sha256", "tokenization_add_special_tokens",
        "tokenization_padding", "tokenization_truncation", "tokenization_return_attention_mask",
        "tokenization_return_tensors", "chat_template_applied", "token_provenance_contract",
        "token_provenance_verified", "prompt_id", "prompt_count", "prompt_token_count",
        "prompt_token_count_min", "prompt_token_count_max", "prompt_input_ids_sha256",
        "prompt_attention_mask_sha256", "prompt_text_sha256",
    ],
    "generation_cache_replay": [
        "generation_config_json", "generation_config_sha256", "generation_determinism_contract",
        "generation_determinism_verified", "generation_strategy", "generation_do_sample",
        "generation_use_cache", "cache_implementation_contract", "generation_cache_implementation",
        "generation_cache_implementation_source", "generation_cache_config_present",
        "generation_num_beams", "generation_num_return_sequences", "generation_max_new_tokens",
        "generation_min_new_tokens", "generation_sampling_disabled", "generation_exact_new_tokens_required",
        "generation_token_contract", "generation_token_provenance_verified", "generated_sequence_sha256",
        "generated_new_token_ids_sha256", "generated_new_token_count", "generated_new_token_count_min",
        "generated_new_token_count_max", "generated_new_token_exact_count_verified",
        "generated_sequence_token_count", "generation_prompt_prefix_verified",
    ],
    "phase_mask_position_kv": [
        "capture_phase_contract", "capture_phase", "prefill_phase_present", "decode_phase_present",
        "decode_steps_requested", "cache_decode_verified", "valid_key_len", "valid_key_len_semantics_verified",
        "active_key_len", "active_key_len_contract", "active_key_len_semantics_verified",
        "position_contract", "absolute_position_verified", "rotary_position_contract", "rotary_position_id",
        "rotary_position_ids_verified", "rotary_position_ids_present_call_count", "kv_head",
        "num_attention_heads", "num_key_value_heads", "num_key_value_groups", "kv_group_map_contract",
        "kv_group_map_verified", "gqa_grouped_rows_present",
    ],
    "score_fidelity_and_dense_reference": [
        "attention_backend", "attention_score_input_stage", "attention_score_inputs_verified",
        "score_transform", "probability_contract", "probability_semantics_verified",
        "attention_probability_dtype", "attention_dropout_p", "attention_training_state", "dropout_applied",
        "attention_scale", "score_bias", "attention_scale_verified", "score_bias_verified",
        "dense_reference_output", "dense_reference_verified", "dense_reference_max_abs_error",
        "attention_mask_backend_preserved", "custom_attention_backend_used", "mask_challenge_exercised",
    ],
}

# Full provenance JSON has a few manifest-only fields that should not be required
# inside the NPZ before it can be hashed.
MANIFEST_ONLY = {"trace_npz_sha256", "trace_claim_version"}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def fields() -> list[str]:
    out: list[str] = []
    for group in FIELD_GROUPS.values():
        for item in group:
            if item not in out:
                out.append(item)
    return out


def extract_list_block(src: str, marker: str) -> set[str]:
    idx = src.find(marker)
    if idx < 0:
        return set()
    start = src.find("[", idx)
    if start < 0:
        return set()
    depth = 0
    for end in range(start, len(src)):
        ch = src[end]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                block = src[start:end + 1]
                return set(re.findall(r'"([A-Za-z0-9_]+)"', block))
    return set()


def source_field_presence(src: str, required: list[str], *, required_occurrence: int = 1) -> dict[str, Any]:
    missing: list[str] = []
    counts: dict[str, int] = {}
    for f in required:
        quoted = src.count(f'"{f}"') + src.count(f"'{f}'")
        keyword = len(re.findall(rf"(?m)(?:^|[,(\s]){re.escape(f)}\s*=", src))
        c = quoted + keyword
        counts[f] = c
        if c < required_occurrence:
            missing.append(f)
    return {"missing": missing, "counts": counts}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    capture = read(CAPTURE)
    gate = read(GATE)
    docs = "\n".join(read(ROOT / rel) for rel in README_FILES)
    required = fields()

    # Capture must emit the required arrays/scalars either into the NPZ or into
    # provenance; most should be in both, except manifest-only values such as the
    # NPZ sha that is only knowable after write.
    npz_block = capture[capture.find("np.savez_compressed("):] if "np.savez_compressed(" in capture else ""
    provenance_block = capture[capture.find("provenance = {"):] if "provenance = {" in capture else ""
    npz_only_arrays = {
        "q", "k", "v", "layer", "head", "position", "rotary_position_id", "capture_phase",
        "valid_key_len", "active_key_len", "kv_head", "num_attention_heads", "num_key_value_heads",
        "num_key_value_groups", "attention_scale", "score_bias", "dense_reference_output",
        "prompt_id", "generated_sequence_sha256", "generated_new_token_ids_sha256",
        "generated_new_token_count", "generated_sequence_token_count", "generation_prompt_prefix_verified",
    }
    per_prompt_arrays_not_self_attested_as_scalars = {
        "prompt_id", "prompt_token_count", "prompt_input_ids_sha256", "prompt_attention_mask_sha256",
        "prompt_text_sha256", "prompt_manifest_json", "tokenization_settings_json",
        "generated_sequence_sha256", "generated_new_token_ids_sha256", "generated_new_token_count",
        "generated_sequence_token_count", "generation_prompt_prefix_verified",
    }
    required_npz = [f for f in required if f not in {"trace_npz_sha256"}]
    required_manifest = [f for f in required if f not in npz_only_arrays]
    capture_npz = source_field_presence(npz_block, required_npz)
    capture_manifest = source_field_presence(provenance_block, required_manifest)
    if capture_npz["missing"]:
        errors.append("capture NPZ writer missing acceptance fields: " + ", ".join(capture_npz["missing"]))
    if capture_manifest["missing"]:
        errors.append("capture provenance writer missing acceptance fields: " + ", ".join(capture_manifest["missing"]))

    gate_metadata_fields = extract_list_block(gate, "metadata_fields = [")
    gate_required_public = extract_list_block(gate, "required_for_public = [")
    gate_manifest_required = extract_list_block(gate, "required_fields")
    gate_cross_check = extract_list_block(gate, "for key in [")

    required_self_attestation = [f for f in required_manifest if f not in {"trace_npz_sha256"} | per_prompt_arrays_not_self_attested_as_scalars]
    required_manifest_fields = [f for f in required_manifest if f not in {"trace_claim_version"} | per_prompt_arrays_not_self_attested_as_scalars] + ["trace_npz_sha256"]
    for label, present, want in [
        ("gate metadata extraction", gate_metadata_fields, required_self_attestation),
        ("gate public self-attestation requirement", gate_required_public, required_self_attestation),
        ("gate provenance manifest requirement", gate_manifest_required, required_manifest_fields),
        ("gate NPZ/manifest cross-check", gate_cross_check, required_self_attestation),
    ]:
        missing = [f for f in want if f not in present]
        if missing:
            errors.append(f"{label} missing fields: " + ", ".join(missing))

    required_phrases = [
        "verify_runtime_provenance_contract(data)",
        "model_load_source_is_local_path must be boolean",
        "generation_cache_implementation_source must be explicit_generate_argument",
        "named_hardware_timing_measured must remain false",
    ]
    for phrase in required_phrases:
        if phrase not in gate:
            errors.append("gate missing semantic check phrase: " + phrase)

    if "acceptance-bundle" not in docs and "acceptance bundle" not in docs:
        warnings.append("docs do not yet emphasize acceptance-bundle validation wording")

    blockers = [
        "real_public_trace_npz_and_provenance_pair_missing",
        "accepted_trace_bundle_required_before_named_hardware_timing",
    ]
    audit = {
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Audits that a captured public trace is an acceptance bundle: NPZ arrays, provenance JSON, embedded self-attestation, runtime/cache/local-loader identity, and cross-check fields must all be present before evaluation.",
        "field_groups": FIELD_GROUPS,
        "capture_npz_missing": capture_npz["missing"],
        "capture_manifest_missing": capture_manifest["missing"],
        "gate_list_sizes": {
            "metadata_fields": len(gate_metadata_fields),
            "required_for_public": len(gate_required_public),
            "manifest_required": len(gate_manifest_required),
            "cross_check": len(gate_cross_check),
        },
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {
                "url": "https://huggingface.co/docs/transformers/en/kv_cache",
                "note": "Generation cache strategy is an explicit runtime variable; accepted bundles must bind dynamic cache metadata, not inherit defaults.",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/main_classes/model",
                "note": "Model loading can infer dtype from checkpoints; accepted bundles must record requested and resolved dtype/device provenance.",
            },
            {
                "url": "https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html",
                "note": "Timing evidence must identify synchronized timing semantics and must not be conflated with promotion hardware timing.",
            },
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_BUNDLE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    lines = [
        f"# Public trace acceptance-bundle audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        "This audit closes a false-green path where an NPZ/provenance pair could be captured but not complete enough to replay, verify, and evaluate.",
        "",
        "## What is now required",
        "",
    ]
    for group, names in FIELD_GROUPS.items():
        lines.append(f"- `{group}`: {len(names)} fields")
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- `{b}`" for b in blockers)
    lines.extend(["", "## Errors", ""])
    lines.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_ACCEPTANCE_BUNDLE_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "blockers": blockers}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
