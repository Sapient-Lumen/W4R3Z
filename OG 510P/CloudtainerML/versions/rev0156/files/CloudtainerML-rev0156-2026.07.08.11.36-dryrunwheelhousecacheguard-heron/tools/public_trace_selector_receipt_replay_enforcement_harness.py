#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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
REVNO = int(str(META.get("revision_number") or REV.replace("rev", "") or 0))
OUT = ROOT / "artifacts" / "audit"
HARNESS_CONTRACT = "selector_receipt_replay_tamper_enforcement_v1"
TRACE_IDENTITY_RECEIPT_CONTRACT = "public_trace_downstream_identity_receipt_v1"
EVALUATION_RECEIPT_CONTRACT = "public_trace_evaluation_receipt_v2"
SELECTOR_RECEIPT_CONTRACT = "public_trace_selector_entry_receipt_v1"
PINNED_TINYLLAMA_SHA256 = "52f1c88d9e086b8b1e3f8a596052c594d3242d21cb7e6c5b1a45a9a579d8a5db"
VERIFIER_REL = "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py"
EVALUATOR_REL = "tools/public_trace_evaluation_verdict_audit.py"
SELECTOR_REL = "tools/public_trace_selector_entry_gate.py"
REPLAY_REL = "tools/public_trace_selector_receipt_replay_gate.py"


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_module(rel: str, name: str) -> Any:
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {rel}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def make_trace_identity(trace_sha: str) -> dict[str, Any]:
    manifest_identity = {
        "trace_claim_version": "public_trace_claim_v1",
        "public_pretrained_trace": True,
        "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "model_revision": "fe8a4ea1ffedaf415f4da2f062534de366a451e6",
        "tokenizer_revision": "fe8a4ea1ffedaf415f4da2f062534de366a451e6",
        "source_type": "public_huggingface_snapshot",
        "schema": "hf_attention_trace_capture_v1",
        "trace_npz_sha256": trace_sha,
        "model_load_source": "/synthetic/digest-verified/TinyLlama",
        "model_load_source_is_local_path": True,
        "snapshot_digest_authenticity_contract": "tinyllama_model_safetensors_sha256_v1",
        "snapshot_digest_authenticity_required": True,
        "snapshot_digest_authenticity_verified": True,
        "loader_snapshot_binding_contract": "model_loader_uses_selected_digest_verified_local_snapshot_v1",
        "loader_snapshot_binding_required": True,
        "loader_snapshot_binding_verified": True,
        "model_load_source_resolved_path": "/synthetic/digest-verified/TinyLlama",
        "verified_snapshot_path": "/synthetic/digest-verified/TinyLlama",
        "model_safetensors_sha256": PINNED_TINYLLAMA_SHA256,
        "expected_model_safetensors_sha256": PINNED_TINYLLAMA_SHA256,
        "model_safetensors_sha256_matches_expected": True,
        "prompt_manifest_contract": "prompt_text_tokenizer_call_manifest_v1",
        "prompt_manifest_sha256": "1" * 64,
        "prompt_count": 2,
        "tokenization_settings_sha256": "2" * 64,
        "token_provenance_contract": "prompt_input_ids_attention_mask_digest_v2",
        "token_provenance_verified": True,
        "generation_config_sha256": "3" * 64,
        "generation_determinism_contract": "greedy_exact_new_tokens_v1",
        "generation_determinism_verified": True,
        "cache_implementation_contract": "hf_generate_dynamic_cache_v1",
        "generation_cache_implementation": "dynamic",
        "generation_cache_implementation_source": "explicit_generate_argument",
        "generation_token_contract": "exact_min_max_new_tokens_v1",
        "generation_token_provenance_verified": True,
        "generated_new_token_count_min": 2,
        "generated_new_token_count_max": 2,
        "capture_phase_contract": "prefill_cached_decode_trace_v1",
        "prefill_phase_present": True,
        "decode_phase_present": True,
        "cache_decode_verified": True,
        "runtime_provenance_contract": "trace_runtime_device_dtype_timing_v1",
        "runtime_provenance_verified": True,
    }
    npz_identity = dict(manifest_identity)
    trace_identity = {
        "trace_identity_receipt_contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "verified_for_downstream_selector_entry": True,
        "verifier_accepted": True,
        "provenance_verifier_status": "pass",
        "loader_snapshot_binding_verified": True,
        "snapshot_digest_authenticity_verified": True,
        "prompt_manifest_sha256": manifest_identity["prompt_manifest_sha256"],
        "generation_config_sha256": manifest_identity["generation_config_sha256"],
        "tokenization_settings_sha256": manifest_identity["tokenization_settings_sha256"],
        "trace_npz_sha256": trace_sha,
        "model_id": manifest_identity["model_id"],
        "model_revision": manifest_identity["model_revision"],
        "tokenizer_revision": manifest_identity["tokenizer_revision"],
        "model_load_source_resolved_path": manifest_identity["model_load_source_resolved_path"],
        "verified_snapshot_path": manifest_identity["verified_snapshot_path"],
        "model_safetensors_sha256": PINNED_TINYLLAMA_SHA256,
        "expected_model_safetensors_sha256": PINNED_TINYLLAMA_SHA256,
        "model_safetensors_sha256_matches_expected": True,
        "cache_implementation_contract": "hf_generate_dynamic_cache_v1",
        "generation_cache_implementation": "dynamic",
        "generation_determinism_contract": manifest_identity["generation_determinism_contract"],
        "generation_token_contract": manifest_identity["generation_token_contract"],
        "token_provenance_contract": manifest_identity["token_provenance_contract"],
        "manifest_identity": manifest_identity,
        "npz_identity": npz_identity,
        "errors": [],
        "warnings": [],
    }
    identity_sha = stable_sha256({
        "contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "manifest_identity": manifest_identity,
        "npz_identity": npz_identity,
    })
    trace_identity["trace_identity_sha256"] = identity_sha
    return trace_identity


def evidence_subject_set_sha256(receipt: dict[str, Any]) -> str:
    normalized = []
    for item in receipt.get("evidence_subjects", []):
        normalized.append({
            "name": item.get("name"),
            "digest": item.get("digest", {}),
            "reported_by_verifier_sha256": item.get("reported_by_verifier_sha256"),
        })
    return stable_sha256({"receipt_contract": receipt.get("receipt_contract"), "subjects": normalized})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def build_evaluation_receipt(work: Path) -> tuple[Path, Path, Path]:
    trace = work / "synthetic_public_trace.npz"
    prov = work / "synthetic_public_trace.provenance.json"
    trace.write_bytes(b"synthetic trace bytes for selector replay enforcement\n")
    prov.write_text(json.dumps({"synthetic": True, "contract": HARNESS_CONTRACT}, sort_keys=True) + "\n", encoding="utf-8")
    trace_sha = sha256_file(trace)
    prov_sha = sha256_file(prov)
    verifier_sha = sha256_file(ROOT / VERIFIER_REL)
    evaluator_sha = sha256_file(ROOT / EVALUATOR_REL)
    trace_identity = make_trace_identity(str(trace_sha))
    receipt = {
        "receipt_contract": EVALUATION_RECEIPT_CONTRACT,
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers",
        "verdict": "accepted_for_selector_evaluation_not_promotion",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": True,
        "gpu_fused_kernel_measured": False,
        "accepted_for_selector_evaluation": True,
        "selector_evaluation_entry_allowed": True,
        "provenance_verifier_accepted": True,
        "trace_npz": rel(trace),
        "trace_npz_sha256": trace_sha,
        "trace_npz_sha256_reported_by_verifier": trace_sha,
        "provenance_json": rel(prov),
        "provenance_json_sha256": prov_sha,
        "gate_verifier": VERIFIER_REL,
        "gate_verifier_sha256": verifier_sha,
        "evaluator_tool": EVALUATOR_REL,
        "evaluator_tool_sha256": evaluator_sha,
        "trace_identity_receipt_contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "trace_identity_sha256": trace_identity["trace_identity_sha256"],
        "trace_identity": trace_identity,
        "trace_identity_verified_for_downstream": True,
        "receipt_identity_errors": [],
        "evidence_subjects": [
            {"name": "public_trace_npz", "digest": {"sha256": trace_sha}, "reported_by_verifier_sha256": trace_sha},
            {"name": "public_trace_provenance_json", "digest": {"sha256": prov_sha}, "reported_by_verifier_sha256": prov_sha},
            {"name": "public_trace_verifier_tool", "digest": {"sha256": verifier_sha}, "reported_by_verifier_sha256": verifier_sha},
            {"name": "public_trace_evaluator_tool", "digest": {"sha256": evaluator_sha}, "reported_by_verifier_sha256": evaluator_sha},
        ],
        "summary": "Synthetic accepted evaluation receipt used only to prove selector receipt replay enforcement catches digest tampering.",
        "errors": [],
        "warnings": [],
        "blockers": ["synthetic_harness_not_real_public_trace"],
    }
    receipt["evidence_subject_set_sha256"] = evidence_subject_set_sha256(receipt)
    eval_path = work / "synthetic_evaluation_receipt.json"
    write_json(eval_path, receipt)
    return trace, prov, eval_path


def verdict_ok(result: dict[str, Any]) -> bool:
    return result.get("verdict") == "selector_receipt_replay_verified_selector_entry_not_promotion" and not result.get("errors")


def run_harness(clean: bool = True) -> dict[str, Any]:
    work = OUT / f"{REVUP}_SELECTOR_RECEIPT_REPLAY_ENFORCEMENT_FIXTURE"
    if clean and work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    selector_mod = load_module(SELECTOR_REL, "_selector_entry_gate_harness")
    replay_mod = load_module(REPLAY_REL, "_selector_receipt_replay_gate_harness")
    trace, prov, eval_receipt = build_evaluation_receipt(work)
    selector_receipt = work / "synthetic_selector_entry_receipt.json"
    selector_result = selector_mod.evaluate_receipt(
        receipt_path=eval_receipt,
        trace_npz_override=trace,
        provenance_json_override=prov,
        selector_receipt_path=selector_receipt,
        strict=True,
    )
    replay_good = replay_mod.evaluate_chain(
        selector_receipt_path=selector_receipt,
        evaluation_receipt_path=eval_receipt,
        trace_npz=trace,
        provenance_json=prov,
        strict=True,
    )

    tampered_trace = work / "tampered_trace.npz"
    tampered_trace.write_bytes(b"tampered trace bytes\n")
    replay_tampered_trace = replay_mod.evaluate_chain(
        selector_receipt_path=selector_receipt,
        evaluation_receipt_path=eval_receipt,
        trace_npz=tampered_trace,
        provenance_json=prov,
        strict=True,
    )

    tampered_eval = work / "tampered_evaluation_receipt.json"
    tampered_eval_data = json.loads(eval_receipt.read_text(encoding="utf-8"))
    tampered_eval_data["trace_identity_sha256"] = "0" * 64
    write_json(tampered_eval, tampered_eval_data)
    replay_tampered_eval = replay_mod.evaluate_chain(
        selector_receipt_path=selector_receipt,
        evaluation_receipt_path=tampered_eval,
        trace_npz=trace,
        provenance_json=prov,
        strict=True,
    )

    tampered_selector = work / "tampered_selector_entry_receipt.json"
    tampered_selector_data = json.loads(selector_receipt.read_text(encoding="utf-8"))
    tampered_selector_data["selector_entry_chain_sha256"] = "0" * 64
    write_json(tampered_selector, tampered_selector_data)
    replay_tampered_selector = replay_mod.evaluate_chain(
        selector_receipt_path=tampered_selector,
        evaluation_receipt_path=eval_receipt,
        trace_npz=trace,
        provenance_json=prov,
        strict=True,
    )

    failures_observed = {
        "tampered_trace_rejected": replay_tampered_trace.get("status") == "fail" and any("public_trace_npz" in str(e) or "actual_bundle_subject_set" in str(e) or "selector_entry_chain_sha256" in str(e) for e in replay_tampered_trace.get("errors", [])),
        "tampered_evaluation_receipt_rejected": replay_tampered_eval.get("status") == "fail" and any("trace_identity" in str(e) or "selector_entry_chain_sha256" in str(e) or "evaluation receipt" in str(e) for e in replay_tampered_eval.get("errors", [])),
        "tampered_selector_chain_rejected": replay_tampered_selector.get("status") == "fail" and any("selector_entry_chain_sha256" in str(e) for e in replay_tampered_selector.get("errors", [])),
    }
    errors: list[str] = []
    if selector_result.get("verdict") != "selector_entry_allowed_not_promotion" or selector_result.get("errors"):
        errors.append("synthetic selector-entry gate did not emit an allowed non-promotional receipt")
    if not verdict_ok(replay_good):
        errors.append("known-good synthetic selector receipt did not replay cleanly")
    for key, ok in failures_observed.items():
        if not ok:
            errors.append(key + " was not observed")

    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "fail" if errors else "pass",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "harness_contract": HARNESS_CONTRACT,
        "fixture_dir": rel(work),
        "selector_entry_receipt_contract": SELECTOR_RECEIPT_CONTRACT,
        "known_good_replay_verdict": replay_good.get("verdict"),
        "tamper_checks": failures_observed,
        "selector_entry_chain_sha256": selector_result.get("selector_entry_chain_sha256"),
        "replayed_selector_entry_chain_sha256": replay_good.get("selector_entry_chain_sha256"),
        "summary": "Executable harness builds a synthetic accepted evaluation receipt and selector-entry receipt, verifies the good replay path, then proves trace-byte, evaluation-receipt, and selector-chain tampering are rejected by the replay gate. It prevents the receipt-chain feature from being only a static string contract.",
        "errors": errors,
        "warnings": ["synthetic fixture only; no real public TinyLlama trace or promotion evidence"],
        "blockers": ["real_digest_verified_snapshot_and_transformers_runtime_still_required"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_ENFORCEMENT_HARNESS.json", audit)
    md = [
        f"# Public trace selector receipt replay enforcement harness — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Tamper checks",
        "",
    ]
    md.extend(f"- {k}: `{v}`" for k, v in failures_observed.items())
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_ENFORCEMENT_HARNESS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return audit


def main() -> int:
    ap = argparse.ArgumentParser(description="Executable tamper harness for the public trace selector receipt replay gate.")
    ap.add_argument("--no-clean", action="store_true", help="keep existing fixture files before regenerating")
    args = ap.parse_args()
    audit = run_harness(clean=not args.no_clean)
    print(json.dumps({"status": audit["status"], "tamper_checks": audit["tamper_checks"], "errors": audit["errors"]}, indent=2))
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
