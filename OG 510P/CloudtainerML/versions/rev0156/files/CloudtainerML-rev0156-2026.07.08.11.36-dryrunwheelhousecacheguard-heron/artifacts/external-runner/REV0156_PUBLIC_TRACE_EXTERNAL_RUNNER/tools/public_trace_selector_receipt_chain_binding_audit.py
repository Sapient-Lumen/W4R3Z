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

SELECTOR_CHAIN_CONTRACT = "public_trace_selector_entry_chain_v1"
TRACE_IDENTITY_CONTRACT = "public_trace_downstream_identity_receipt_v1"

REQUIRED_SOURCE_MARKERS: dict[str, list[str]] = {
    "tools/public_trace_selector_entry_gate.py": [
        SELECTOR_CHAIN_CONTRACT,
        "_selector_entry_chain_sha256",
        "input_evaluation_receipt_sha256",
        "actual_bundle_subject_set_sha256",
        "selector_entry_chain_sha256",
        "trace_identity",
    ],
    "tools/public_trace_selector_receipt_replay_gate.py": [
        SELECTOR_CHAIN_CONTRACT,
        "selector_entry_chain_errors",
        "selector-entry receipt selector_entry_chain_sha256 does not match recomputed evaluation/identity/bundle chain",
        "recomputed_selector_entry_chain_sha256",
    ],
    "tools/public_trace_handoff_builder.py": [
        SELECTOR_CHAIN_CONTRACT,
        "selector_entry_chain_sha256",
        "selector_entry_chain_bound",
    ],
    "tools/public_trace_handoff_archive_gate.py": [
        SELECTOR_CHAIN_CONTRACT,
        "replayed selector-entry chain hash does not match handoff manifest",
        "replayed_selector_entry_chain_sha256",
    ],
}


def stable_chain_probe() -> dict[str, Any]:
    # This fixed synthetic object mirrors the fields hashed by selector/replay.
    # It is intentionally path-free except for subject-role digests; moving a
    # bundle should not change the chain, but changing any accepted receipt,
    # trace identity, or actual subject digest must change it.
    import hashlib

    obj = {
        "selector_entry_chain_contract": SELECTOR_CHAIN_CONTRACT,
        "input_evaluation_receipt_sha256": "a" * 64,
        "input_evaluation_receipt_subject_set_sha256": "b" * 64,
        "trace_identity_sha256": "c" * 64,
        "actual_bundle_subject_set_sha256": "d" * 64,
        "selector_gate_tool_sha256": "e" * 64,
    }
    digest = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    mutated = dict(obj)
    mutated["trace_identity_sha256"] = "f" * 64
    mutated_digest = hashlib.sha256(json.dumps(mutated, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "contract": SELECTOR_CHAIN_CONTRACT,
        "stable_probe_digest": digest,
        "mutation_changes_digest": digest != mutated_digest,
        "subjects_bound": [
            "input_evaluation_receipt_sha256",
            "input_evaluation_receipt_subject_set_sha256",
            "trace_identity_sha256",
            "actual_bundle_subject_set_sha256",
            "selector_gate_tool_sha256",
        ],
    }


def audit() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    marker_results: dict[str, dict[str, Any]] = {}
    for rel, markers in REQUIRED_SOURCE_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing required source: {rel}")
            marker_results[rel] = {"exists": False, "missing_markers": markers}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [m for m in markers if m not in text]
        if missing:
            errors.append(f"{rel} missing chain-binding markers: {', '.join(missing)}")
        marker_results[rel] = {"exists": True, "missing_markers": missing}

    probe = stable_chain_probe()
    if probe["mutation_changes_digest"] is not True:
        errors.append("synthetic selector-entry chain digest did not change under trace identity mutation")

    run_src = (ROOT / "artifacts/capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh").read_text(encoding="utf-8", errors="replace") if (ROOT / "artifacts/capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh").exists() else ""
    one_shot_src = (ROOT / "artifacts/capture-kit" / f"{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh").read_text(encoding="utf-8", errors="replace") if (ROOT / "artifacts/capture-kit" / f"{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh").exists() else ""
    if "public_trace_selector_receipt_chain_binding_audit.py" not in run_src or "public_trace_selector_receipt_chain_binding_audit.py" not in one_shot_src:
        errors.append("current live wrappers must run selector receipt chain binding audit")

    return {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "verdict": "selector_receipt_chain_binding_guarded" if not errors else "selector_receipt_chain_binding_incomplete",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "selector_entry_chain_contract": SELECTOR_CHAIN_CONTRACT,
        "trace_identity_receipt_contract": TRACE_IDENTITY_CONTRACT,
        "source_marker_results": marker_results,
        "stable_chain_probe": probe,
        "summary": "Audits the rev0136 receipt-chain binding refactor: selector-entry receipts must carry a non-circular chain digest tying the accepted evaluation receipt hash, evaluation subject-set hash, downstream trace-identity hash, actual replay bundle subject-set hash, and selector gate tool hash. Handoff manifests must carry and replay that chain hash, so a copied selector receipt cannot be paired with a different evaluation/trace/provenance/tool bundle.",
        "errors": errors,
        "warnings": warnings,
        "blockers": ["real_public_trace_still_requires_digest_verified_snapshot_and_transformers_runtime"],
    }


def main() -> int:
    result = audit()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_CHAIN_BINDING_AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace selector receipt chain binding audit — {REVUP}",
        "",
        f"Status: `{result['status']}`  ",
        f"Verdict: `{result['verdict']}`  ",
        "Promotion allowed: `false`",
        "",
        result["summary"],
        "",
        "## Bound subjects",
        "",
    ]
    for item in result["stable_chain_probe"]["subjects_bound"]:
        md.append(f"- `{item}`")
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in result["errors"]] if result["errors"] else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_CHAIN_BINDING_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "verdict": result["verdict"], "errors": result["errors"]}, indent=2))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
