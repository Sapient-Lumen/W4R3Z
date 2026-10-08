#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

REQUIRED_RECEIPT_FIELDS = [
    "receipt_contract", "revision", "revision_number", "package_name", "archive_name",
    "status", "verdict", "accepted_for_selector_evaluation", "promotion_allowed",
    "trace_npz", "trace_npz_exists", "trace_npz_sha256",
    "provenance_json", "provenance_json_exists", "provenance_json_sha256",
    "evaluator_tool", "evaluator_tool_sha256", "gate_verifier", "gate_verifier_sha256",
    "trace_npz_sha256_reported_by_verifier", "provenance_verifier_status",
    "provenance_verifier_accepted", "evidence_subjects", "evidence_subject_set_sha256",
    "receipt_identity_errors", "selector_evaluation_entry_allowed",
    "named_hardware_timing_still_required_for_promotion", "path_relocation_policy",
]


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def _load_verdict_module() -> Any:
    path = ROOT / "tools" / "public_trace_evaluation_verdict_audit.py"
    spec = importlib.util.spec_from_file_location("_verdict_receipt_probe_" + REVUP, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import public_trace_evaluation_verdict_audit")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    verdict_tool = read("tools/public_trace_evaluation_verdict_audit.py")
    selector_gate = read("tools/public_trace_selector_entry_gate.py")
    one_shot = read(f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh")
    current = read("artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh")
    readiness = read("tools/public_trace_readiness_gate.py")

    required_terms = [
        "RECEIPT_CONTRACT", "public_trace_evaluation_receipt_v2", "evidence_subject_set_sha256",
        "evidence_subjects", "receipt_identity_errors", "trace_npz_sha256_reported_by_verifier",
        "--receipt-json", "path_relocation_policy",
    ]
    for term in required_terms:
        if term not in verdict_tool:
            errors.append("evaluation verdict tool missing receipt term: " + term)

    for term in ["public_trace_evaluation_receipt_v2", "evidence_subject_set_sha256", "--trace-npz", "--provenance-json", "actual files match", "public_trace_selector_entry_receipt_v1", "selector_gate_tool_sha256", "recomputed_receipt_subject_set_sha256"]:
        if term not in selector_gate:
            errors.append("selector entry gate missing v2 relocation term: " + term)

    for term in ["OUT_RECEIPT", "--receipt-json", "--trace-npz", "--provenance-json", "public_trace_selector_entry_gate.py"]:
        if term not in one_shot:
            errors.append("current one-shot launcher missing v2 receipt/selector handoff term: " + term)
    if f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh" not in current:
        errors.append("RUN_CURRENT_PUBLIC_TRACE.sh does not target the current revision launcher")
    if "receipt_relocation" not in readiness or "selector_entry_receipt" not in readiness or "selector_entry_gate" not in readiness:
        errors.append("readiness gate does not include relocation receipt/selector-entry checks")

    case_results: dict[str, Any] = {}
    try:
        mod = _load_verdict_module()
        fixture = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_RECEIPT_AUDIT_FIXTURE"
        fixture.mkdir(parents=True, exist_ok=True)
        trace = fixture / "trace.npz"
        prov = fixture / "trace.provenance.json"
        trace.write_bytes(b"receipt-audit-trace-content\n")
        prov.write_text('{"kind":"receipt-audit-provenance"}\n', encoding="utf-8")
        trace_sha = mod.sha256_file(trace)
        receipt = mod._make_receipt(
            trace_npz=trace,
            provenance_json=prov,
            status="pass_with_blockers",
            verdict="accepted_for_selector_evaluation_not_promotion",
            errors=[],
            blockers=["timing"],
            provenance_status={"accepted": True, "trace_npz_sha256_actual": trace_sha, "status": "accepted"},
            strict_require_trace=True,
        )
        missing_fields = [f for f in REQUIRED_RECEIPT_FIELDS if f not in receipt]
        if missing_fields:
            errors.append("receipt object missing fields: " + ", ".join(missing_fields))
        case_results["accepted_receipt_has_subject_set"] = bool(receipt.get("evidence_subject_set_sha256") and receipt.get("evidence_subjects"))
        case_results["accepted_receipt_opens_selector_but_not_promotion"] = bool(receipt.get("selector_evaluation_entry_allowed")) and receipt.get("promotion_allowed") is False
        mismatch = mod._make_receipt(
            trace_npz=trace,
            provenance_json=prov,
            status="pass_with_blockers",
            verdict="accepted_for_selector_evaluation_not_promotion",
            errors=[],
            blockers=["timing"],
            provenance_status={"accepted": True, "trace_npz_sha256_actual": "f"*64, "status": "accepted"},
            strict_require_trace=True,
        )
        case_results["hash_mismatch_closes_selector_entry"] = mismatch.get("selector_evaluation_entry_allowed") is False and bool(mismatch.get("receipt_identity_errors"))
        missing = mod._make_receipt(
            trace_npz=ROOT / "artifacts" / "trace-bundles" / "MISSING_RECEIPT_AUDIT.npz",
            provenance_json=ROOT / "artifacts" / "trace-bundles" / "MISSING_RECEIPT_AUDIT.json",
            status="pass_with_blockers",
            verdict="blocked_no_trace_bundle",
            errors=[],
            blockers=["missing"],
            provenance_status={},
            strict_require_trace=False,
        )
        case_results["missing_trace_receipt_blocks_selector_entry"] = missing.get("selector_evaluation_entry_allowed") is False and missing.get("accepted_for_selector_evaluation") is False
        if not all(case_results.values()):
            errors.append("receipt semantic case failed: " + json.dumps(case_results, sort_keys=True))
    except Exception as exc:
        errors.append("could not exercise receipt semantics: " + repr(exc))
        case_results["exception"] = repr(exc)

    blockers = [
        "real_public_trace_npz_and_provenance_pair_missing",
        "receipt_expected_to_block_selector_entry_until_verifier_accepts_bundle_and_actual_files_match_digests",
        "named_hardware_timing_still_required_after_selector_entry",
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
        "receipt_contract": "public_trace_evaluation_receipt_v2",
        "summary": "Audits that the evaluation verdict emits a content-addressed receipt binding selector-entry permission to the exact trace NPZ, provenance JSON, verifier code, evaluator code, and a relocation-stable subject-set hash. The selector gate must verify actual file hashes before opening evaluation.",
        "required_receipt_fields": REQUIRED_RECEIPT_FIELDS,
        "case_results": case_results,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://slsa.dev/spec/v1.0/provenance", "note": "Provenance is an attestation about produced artifacts; selector entry should require artifact digests, not path names."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/README.md", "note": "An attestation statement binds a predicate to subject artifacts."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md", "note": "ResourceDescriptor entries include names and digests; rev0108 uses semantic subject names and SHA-256 digests."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace evaluation receipt audit — {REVUP}", "",
        f"Status: `{audit['status']}`  ", "Promotion allowed: `false`", "",
        audit["summary"], "", "## Semantic cases", "",
    ]
    md.extend([f"- `{k}` = `{v}`" for k, v in case_results.items()])
    md.extend(["", "## Blockers", ""])
    md.extend([f"- `{b}`" for b in blockers])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "case_results": case_results, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
