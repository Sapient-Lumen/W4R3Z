#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(META.get("revision_number") or REV.replace("rev", "") or 0)
OUT = ROOT / "artifacts" / "audit"
FIX = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_HANDOFF_BUILDER_FIXTURES"
OUT.mkdir(parents=True, exist_ok=True)


def load_module(rel: str, name: str) -> Any:
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name + "_" + REVUP, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import " + rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    case_results: dict[str, Any] = {}
    source_checks: dict[str, bool] = {}
    if FIX.exists():
        shutil.rmtree(FIX)
    try:
        builder_src = (ROOT / "tools" / "public_trace_handoff_builder.py").read_text(encoding="utf-8")
        source_checks = {
            "handoff_contract_literal": "public_trace_handoff_archive_v1" in builder_src,
            "toolpack_contract_literal": "public_trace_handoff_toolpack_v1" in builder_src,
            "builder_function": "def build_handoff_directory" in builder_src,
            "manifest_filename": "PUBLIC_TRACE_HANDOFF_MANIFEST.json" in builder_src,
            "promotion_never_allowed": "\"promotion_allowed\": False" in builder_src,
            "cold_reviewer_wrapper_included": "public_trace_cold_reviewer_verify_wrapper" in builder_src,
        }
        for key, ok in source_checks.items():
            if not ok:
                errors.append("builder source missing expected term: " + key)

        verdict_mod = load_module("tools/public_trace_evaluation_verdict_audit.py", "_builder_verdict")
        selector_mod = load_module("tools/public_trace_selector_entry_gate.py", "_builder_selector")
        builder_mod = load_module("tools/public_trace_handoff_builder.py", "_builder")
        gate_mod = load_module("tools/public_trace_handoff_archive_gate.py", "_builder_gate")

        src = FIX / "source"
        src.mkdir(parents=True, exist_ok=True)
        trace = src / "trace.npz"
        prov = src / "trace.provenance.json"
        trace.write_bytes((REV + " builder fixture trace bytes\n").encode("utf-8"))
        prov.write_text(json.dumps({"fixture": REV + " handoff builder provenance"}) + "\n", encoding="utf-8")
        trace_sha = verdict_mod.sha256_file(trace)
        fake_sha = "a" * 64
        prompt_sha = "b" * 64
        generation_sha = "c" * 64
        tokenization_sha = "d" * 64
        identity_manifest = {
            "trace_claim_version": "public_trace_fixture_v1",
            "public_pretrained_trace": True,
            "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "model_revision": "fe8a4ea1ffedaf415f4da2f062534de366a451e6",
            "tokenizer_revision": "fe8a4ea1ffedaf415f4da2f062534de366a451e6",
            "source_type": "fixture_downstream_identity_only",
            "schema": "public_trace_fixture_identity_v1",
            "trace_npz_sha256": trace_sha,
            "model_load_source": "/tmp/digest-verified-tinyllama-fixture",
            "model_load_source_is_local_path": True,
            "snapshot_digest_authenticity_contract": "model_safetensors_sha256_pinned_v1",
            "snapshot_digest_authenticity_required": True,
            "snapshot_digest_authenticity_verified": True,
            "loader_snapshot_binding_contract": "model_loader_uses_selected_digest_verified_local_snapshot_v1",
            "loader_snapshot_binding_required": True,
            "loader_snapshot_binding_verified": True,
            "model_load_source_resolved_path": "/tmp/digest-verified-tinyllama-fixture",
            "verified_snapshot_path": "/tmp/digest-verified-tinyllama-fixture",
            "model_safetensors_sha256": fake_sha,
            "expected_model_safetensors_sha256": fake_sha,
            "model_safetensors_sha256_matches_expected": True,
            "prompt_manifest_contract": "prompt_text_tokenizer_call_manifest_v1",
            "prompt_manifest_sha256": prompt_sha,
            "prompt_count": 2,
            "tokenization_settings_sha256": tokenization_sha,
            "token_provenance_contract": "prompt_input_ids_attention_mask_digest_v2",
            "token_provenance_verified": True,
            "generation_config_sha256": generation_sha,
            "generation_determinism_contract": "exact_new_tokens_greedy_v1",
            "generation_determinism_verified": True,
            "cache_implementation_contract": "hf_generate_dynamic_cache_v1",
            "generation_cache_implementation": "dynamic",
            "generation_cache_implementation_source": "explicit_generate_argument",
            "generation_token_contract": "generated_token_trace_v1",
            "generation_token_provenance_verified": True,
            "generated_new_token_count_min": 2,
            "generated_new_token_count_max": 2,
            "capture_phase_contract": "prefill_cached_decode_active_key_trace_v1",
            "prefill_phase_present": True,
            "decode_phase_present": True,
            "cache_decode_verified": True,
            "runtime_provenance_contract": "runtime_backend_identity_v1",
            "runtime_provenance_verified": True,
        }
        accepted = verdict_mod._make_receipt(
            trace_npz=trace,
            provenance_json=prov,
            status="pass_with_blockers",
            verdict="accepted_for_selector_evaluation_not_promotion",
            errors=[],
            blockers=["timing"],
            provenance_status={
                "accepted": True,
                "trace_npz_sha256_actual": trace_sha,
                "status": "accepted",
                "manifest": identity_manifest,
                "npz_metadata_status": {"metadata": dict(identity_manifest)},
                "loader_snapshot_binding_status": {"manifest_errors": [], "npz_errors": []},
            },
            strict_require_trace=True,
        )
        eval_receipt = src / "evaluation_receipt.json"
        write_json(eval_receipt, accepted)
        selector_receipt = src / "selector_entry_receipt.json"
        selector_eval = selector_mod.evaluate_receipt(receipt_path=eval_receipt, selector_receipt_path=selector_receipt, strict=True)
        case_results["selector_fixture_opened"] = selector_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not selector_eval.get("errors")

        handoff_dir = FIX / "handoff"
        zip_path = FIX / f"{REVUP}_portable_handoff_builder_fixture.zip"
        result = builder_mod.build_handoff_directory(
            handoff_dir=handoff_dir,
            trace_npz=trace,
            provenance_json=prov,
            evaluation_receipt_json=eval_receipt,
            selector_entry_receipt_json=selector_receipt,
            clean=True,
        )
        builder_mod.zip_dir(handoff_dir, zip_path)
        manifest = result["manifest_path"]
        gate = gate_mod.evaluate_handoff(handoff_dir=handoff_dir, manifest_path=manifest, strict=True)
        case_results["built_handoff_gate_passes"] = gate.get("verdict") == "handoff_archive_replay_verified_not_promotion" and not gate.get("errors")
        case_results["zip_written"] = zip_path.exists() and zip_path.stat().st_size > 0
        case_results["manifest_toolpack_subject_set_matches"] = gate.get("toolpack_subject_set_sha256") == gate.get("actual_toolpack_subject_set_sha256")
        case_results["manifest_handoff_subject_set_matches"] = gate.get("handoff_subject_set_sha256") == gate.get("actual_handoff_subject_set_sha256")

        tampered = FIX / "tampered"
        shutil.copytree(handoff_dir, tampered)
        (tampered / "tools" / "public_trace_selector_entry_gate.py").write_text("# tampered\n", encoding="utf-8")
        tampered_gate = gate_mod.evaluate_handoff(handoff_dir=tampered, manifest_path=tampered / "PUBLIC_TRACE_HANDOFF_MANIFEST.json", strict=False)
        case_results["tampered_tool_blocks"] = tampered_gate.get("status") == "fail" and any("public_trace_selector_entry_gate" in str(e) or "toolpack_subject_set_sha256" in str(e) for e in tampered_gate.get("errors", []))

        if not all(case_results.values()):
            errors.append("builder audit case failed: " + json.dumps(case_results, sort_keys=True))
    except Exception as exc:
        errors.append("builder audit exception: " + repr(exc))
        case_results["exception"] = repr(exc)

    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Audits the new reusable public-trace handoff builder. The builder closes the prior gap where the fixture audit could create portable handoffs but the real trace path had no dedicated builder command.",
        "source_checks": source_checks,
        "case_results": case_results,
        "fixture_root": FIX.relative_to(ROOT).as_posix(),
        "errors": errors,
        "warnings": warnings,
        "decision": "builder_ready_for_real_trace_after_selector_entry_receipt" if not errors else "repair_builder_before_real_trace_handoff",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_HANDOFF_BUILDER_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace handoff builder audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Case results",
        "",
    ]
    md.extend(f"- `{k}` = `{str(v).lower()}`" for k, v in case_results.items())
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_HANDOFF_BUILDER_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "case_results": case_results}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
