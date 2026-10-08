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
OUT = ROOT / "artifacts" / "audit"
FIX = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_SELECTOR_ENTRY_RECEIPT_FIXTURES"
OUT.mkdir(parents=True, exist_ok=True)
FIX.mkdir(parents=True, exist_ok=True)


def _load_module(rel: str, name: str) -> Any:
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name + "_" + REVUP, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import " + rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    case_results: dict[str, Any] = {}
    source_checks: dict[str, bool] = {}
    try:
        selector_src = (ROOT / "tools" / "public_trace_selector_entry_gate.py").read_text(encoding="utf-8")
        required_terms = [
            "SELECTOR_ENTRY_RECEIPT_CONTRACT",
            "public_trace_selector_entry_receipt_v1",
            "recomputed_receipt_subject_set_sha256",
            "actual_gate_verifier_sha256",
            "actual_evaluator_tool_sha256",
            "selector_gate_tool_sha256",
            "actual_bundle_subject_set_sha256",
            "evidence_subject_set_sha256 does not match recomputed",
            "actual files match",
            "--selector-entry-receipt-json",
        ]
        source_checks = {term: (term in selector_src) for term in required_terms}
        for term, present in source_checks.items():
            if not present:
                errors.append("selector gate source missing term: " + term)

        verdict_mod = _load_module("tools/public_trace_evaluation_verdict_audit.py", "_selector_receipt_verdict")
        selector_mod = _load_module("tools/public_trace_selector_entry_gate.py", "_selector_receipt_gate")
        if FIX.exists():
            shutil.rmtree(FIX)
        FIX.mkdir(parents=True, exist_ok=True)
        original = FIX / "original"
        relocated = FIX / "relocated"
        tampered = FIX / "tampered"
        for d in [original, relocated, tampered]:
            d.mkdir(parents=True, exist_ok=True)
        trace = original / "trace.npz"
        prov = original / "trace.provenance.json"
        trace.write_bytes(b"rev0109 selector entry trace fixture bytes\n")
        prov.write_text('{"fixture":"rev0109 selector entry provenance"}\n', encoding="utf-8")
        relocated_trace = relocated / "renamed-trace.npz"
        relocated_prov = relocated / "renamed-trace.provenance.json"
        shutil.copy2(trace, relocated_trace)
        shutil.copy2(prov, relocated_prov)
        bad_trace = tampered / "renamed-trace.npz"
        bad_prov = tampered / "renamed-trace.provenance.json"
        bad_trace.write_bytes(b"tampered rev0109 selector entry bytes\n")
        shutil.copy2(prov, bad_prov)

        trace_sha = verdict_mod.sha256_file(trace)
        accepted = verdict_mod._make_receipt(
            trace_npz=trace,
            provenance_json=prov,
            status="pass_with_blockers",
            verdict="accepted_for_selector_evaluation_not_promotion",
            errors=[],
            blockers=["timing"],
            provenance_status={"accepted": True, "trace_npz_sha256_actual": trace_sha, "status": "accepted"},
            strict_require_trace=True,
        )
        receipt_path = FIX / f"{REVUP}_accepted_receipt.json"
        _write_json(receipt_path, accepted)
        selector_receipt_path = FIX / f"{REVUP}_selector_entry_receipt.json"
        accepted_eval = selector_mod.evaluate_receipt(receipt_path=receipt_path, selector_receipt_path=selector_receipt_path, strict=True)
        selector_receipt = json.loads(selector_receipt_path.read_text(encoding="utf-8"))
        case_results["accepted_matching_bundle_opens_selector_entry"] = accepted_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not accepted_eval.get("errors")
        case_results["selector_entry_receipt_emitted"] = selector_receipt_path.exists() and selector_receipt.get("selector_entry_receipt_contract") == "public_trace_selector_entry_receipt_v1"
        case_results["selector_receipt_binds_selector_gate_hash"] = bool(selector_receipt.get("selector_gate_tool_sha256")) and selector_receipt.get("selector_gate_tool_sha256") == accepted_eval.get("selector_gate_tool_sha256")
        case_results["input_subject_set_recomputed"] = accepted_eval.get("receipt_subject_set_verified") is True and accepted_eval.get("recomputed_receipt_subject_set_sha256") == accepted.get("evidence_subject_set_sha256")
        moved_eval = selector_mod.evaluate_receipt(receipt_path=receipt_path, trace_npz_override=relocated_trace, provenance_json_override=relocated_prov, selector_receipt_path=FIX / f"{REVUP}_moved_selector_entry_receipt.json", strict=True)
        case_results["relocated_matching_bundle_still_opens_selector_entry"] = moved_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not moved_eval.get("errors")
        bad_file_eval = selector_mod.evaluate_receipt(receipt_path=receipt_path, trace_npz_override=bad_trace, provenance_json_override=bad_prov, selector_receipt_path=FIX / f"{REVUP}_bad_file_selector_entry_receipt.json", strict=False)
        case_results["tampered_file_blocks_selector_entry"] = bad_file_eval.get("status") == "fail" and any("actual trace_npz hash" in str(e) for e in bad_file_eval.get("errors", []))

        forged_subject = dict(accepted)
        forged_subject["evidence_subject_set_sha256"] = "0" * 64
        forged_subject_path = FIX / f"{REVUP}_forged_subject_set_receipt.json"
        _write_json(forged_subject_path, forged_subject)
        forged_subject_eval = selector_mod.evaluate_receipt(receipt_path=forged_subject_path, selector_receipt_path=FIX / f"{REVUP}_forged_subject_selector_entry_receipt.json", strict=False)
        case_results["forged_subject_set_blocks_selector_entry"] = forged_subject_eval.get("status") == "fail" and any("evidence_subject_set_sha256" in str(e) for e in forged_subject_eval.get("errors", []))

        forged_tool = dict(accepted)
        forged_tool["evaluator_tool_sha256"] = "f" * 64
        # Keep subject list unchanged to ensure the gate catches both subject/top-level mismatch and actual tool mismatch.
        forged_tool_path = FIX / f"{REVUP}_forged_tool_receipt.json"
        _write_json(forged_tool_path, forged_tool)
        forged_tool_eval = selector_mod.evaluate_receipt(receipt_path=forged_tool_path, selector_receipt_path=FIX / f"{REVUP}_forged_tool_selector_entry_receipt.json", strict=False)
        case_results["forged_evaluator_tool_hash_blocks_selector_entry"] = forged_tool_eval.get("status") == "fail" and any("evaluator" in str(e) for e in forged_tool_eval.get("errors", []))

        if not all(case_results.values()):
            errors.append("selector-entry receipt case failed: " + json.dumps(case_results, sort_keys=True))
    except Exception as exc:
        errors.append("selector-entry receipt audit exception: " + repr(exc))
        case_results["exception"] = repr(exc)

    blockers = [
        "real_public_trace_npz_and_provenance_pair_missing",
        "selector_entry_receipt_is_handoff_not_promotion_evidence",
        "named_hardware_timing_still_required_for_promotion",
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
        "summary": "Audits the selector-entry handoff: the gate must recompute the input evaluation receipt subject-set, verify current evaluator/verifier/selector tool hashes, match actual NPZ/provenance file hashes, and emit a selector-entry receipt. This prevents a moved/tampered bundle or modified gate from quietly reinterpreting an old receipt.",
        "source_checks": source_checks,
        "case_results": case_results,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://slsa.dev/spec/v1.0/provenance", "note": "SLSA provenance emphasizes subject artifact digests; rev0109 applies the same digest-binding discipline to selector-entry handoff receipts."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/README.md", "note": "In-toto statements bind predicates to subjects; selector-entry is now a separate predicate over the evaluation receipt and actual files."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md", "note": "Resource descriptors include names and digests; rev0109 verifies semantic subject names, digests, and tool hashes rather than trusting paths."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace selector-entry receipt audit — {REVUP}", "",
        f"Status: `{audit['status']}`  ", "Promotion allowed: `false`", "",
        audit["summary"], "", "## Cases", "",
    ]
    md.extend([f"- `{k}` = `{v}`" for k, v in case_results.items()])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "case_results": case_results, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
