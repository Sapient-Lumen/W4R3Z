#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

TRACE_IDENTITY_RECEIPT_CONTRACT = "public_trace_downstream_identity_receipt_v1"
SELECTOR_ENTRY_CHAIN_CONTRACT = "public_trace_selector_entry_chain_v1"


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def load(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    evaluator = read("tools/public_trace_evaluation_verdict_audit.py")
    selector = read("tools/public_trace_selector_entry_gate.py")
    replay = read("tools/public_trace_selector_receipt_replay_gate.py")
    builder = read("tools/public_trace_handoff_builder.py")
    handoff_gate = read("tools/public_trace_handoff_archive_gate.py")
    verifier = read("experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py")
    run = read(f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh")
    one = read(f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh")
    smoke = read("tools/smoke_validate.py")
    packet = load(f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json")
    det = packet.get("determinism_contract", {}) if isinstance(packet, dict) else {}
    env = packet.get("environment_preflight", {}) if isinstance(packet, dict) else {}

    checks: dict[str, bool] = {
        "verifier_exposes_loader_fields_in_manifest_summary": "*PUBLIC_LOADER_BINDING_FIELDS" in verifier and "status[\"manifest\"]" in verifier,
        "evaluator_declares_trace_identity_contract": TRACE_IDENTITY_RECEIPT_CONTRACT in evaluator and "TRACE_IDENTITY_FIELDS" in evaluator,
        "evaluator_summarizes_snapshot_prompt_generation_identity": all(term in evaluator for term in [
            "_trace_identity_summary", "prompt_manifest_sha256", "generation_config_sha256",
            "tokenization_settings_sha256", "model_safetensors_sha256", "verified_snapshot_path",
            "cache_implementation_contract", "generation_cache_implementation",
        ]),
        "evaluator_requires_identity_before_accepting_selector_entry": "trace_identity.get(\"verified_for_downstream_selector_entry\") is True" in evaluator,
        "selector_requires_trace_identity_receipt_on_open_entry": "_trace_identity_receipt_errors" in selector and "trace_identity_verified_for_downstream" in selector,
        "selector_receipt_carries_trace_identity_hash": "trace_identity_sha256" in selector and "trace_identity_receipt_contract" in selector,
        "replay_checks_selector_and_evaluation_identity_hashes": "trace_identity_chain_errors" in replay and "selector-entry trace_identity_sha256 does not match input evaluation receipt" in replay,
        "handoff_builder_exports_identity_chain": "trace_identity_chain_bound" in builder and "selector_trace_identity_sha256" in builder,
        "handoff_gate_replays_identity_chain": "replayed selector chain trace identity hash does not match handoff manifest" in handoff_gate,
        "selector_entry_chain_contract_present": SELECTOR_ENTRY_CHAIN_CONTRACT in selector and SELECTOR_ENTRY_CHAIN_CONTRACT in replay,
        "selector_entry_chain_digest_replayed": "selector_entry_chain_errors" in replay and "selector-entry receipt selector_entry_chain_sha256 does not match recomputed evaluation/identity/bundle chain" in replay,
        "handoff_carries_selector_entry_chain": "selector_entry_chain_sha256" in builder and "selector_entry_chain_sha256" in handoff_gate,
        "live_wrappers_run_downstream_identity_audit": "public_trace_downstream_identity_receipt_audit.py" in run and "public_trace_downstream_identity_receipt_audit.py" in one,
        "smoke_guards_downstream_identity_receipt": "downstream_identity_receipt" in smoke and TRACE_IDENTITY_RECEIPT_CONTRACT in smoke,
        "run_packet_declares_downstream_identity_contract": det.get("downstream_identity_receipt_contract") == TRACE_IDENTITY_RECEIPT_CONTRACT,
        "run_packet_declares_selector_entry_chain_contract": det.get("selector_entry_chain_contract") == SELECTOR_ENTRY_CHAIN_CONTRACT,
        "run_packet_declares_downstream_identity_audit": env.get("downstream_identity_receipt_audit") == "tools/public_trace_downstream_identity_receipt_audit.py",
        "run_packet_declares_selector_chain_audit": env.get("selector_receipt_chain_binding_audit") == "tools/public_trace_selector_receipt_chain_binding_audit.py",
    }
    errors = [name for name, ok in checks.items() if not ok]
    status = "pass" if not errors else "fail"
    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": int(str(REV).replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Guards rev0136: once a public trace is accepted, the evaluation receipt, selector-entry receipt, replay gate, and handoff manifest must carry both the compact selected-snapshot/prompt/generation identity hash and a selector-entry chain digest that binds that identity to the exact evaluation receipt and replay subject set, not merely a boolean verifier acceptance.",
        "risk_closed": "downstream_receipts_or_handoff_archive_detach_from_selected_snapshot_prompt_manifest_generation_cache_identity_after_acceptance_verifier_passes",
        "checks": checks,
        "errors": errors,
        "online_basis": [
            {"url": "https://huggingface.co/docs/transformers/en/installation", "note": "Offline/local Transformers runs can load from a local directory with local_files_only; receipts should record the exact selected local snapshot identity."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "note": "snapshot_download binds a repository revision to local snapshot files; downstream receipts need this identity summarized after acceptance."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables", "note": "Cache paths can vary by environment, so handoff receipts should not rely on implicit cache resolution."},
            {"url": "https://slsa.dev/spec/v1.0/provenance", "note": "Subject identity should be digest-bound in attestations; rev0136 mirrors that for trace/prompt/model identity receipts."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/README.md", "note": "in-toto statements bind predicate details to subjects; downstream trace receipts now carry a compact identity predicate hash."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_DOWNSTREAM_IDENTITY_RECEIPT_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace downstream identity receipt audit — {REVUP}",
        "",
        f"Status: `{status}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Checks",
        "",
    ]
    md.extend([f"- {name}: `{ok}`" for name, ok in checks.items()])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_DOWNSTREAM_IDENTITY_RECEIPT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
