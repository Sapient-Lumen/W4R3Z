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
FIX = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_RECEIPT_RELOCATION_FIXTURES"
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


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    case_results: dict[str, Any] = {}
    try:
        verdict_mod = _load_module("tools/public_trace_evaluation_verdict_audit.py", "_reloc_verdict")
        selector_mod = _load_module("tools/public_trace_selector_entry_gate.py", "_reloc_selector")
        src = FIX / "original"
        dst = FIX / "relocated"
        tampered = FIX / "tampered"
        for d in [src, dst, tampered]:
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)
        src_trace = src / "trace-capture-original.npz"
        src_prov = src / "trace-capture-original.provenance.json"
        src_trace.write_bytes(b"rev0110 relocation trace fixture bytes\n")
        src_prov.write_text('{"fixture":"rev0110 relocation provenance"}\n', encoding="utf-8")
        dst_trace = dst / "renamed-evidence.npz"
        dst_prov = dst / "renamed-evidence.provenance.json"
        shutil.copy2(src_trace, dst_trace)
        shutil.copy2(src_prov, dst_prov)
        bad_trace = tampered / "renamed-evidence.npz"
        bad_prov = tampered / "renamed-evidence.provenance.json"
        bad_trace.write_bytes(b"tampered trace bytes\n")
        shutil.copy2(src_prov, bad_prov)
        trace_sha = verdict_mod.sha256_file(src_trace)
        receipt = verdict_mod._make_receipt(
            trace_npz=src_trace,
            provenance_json=src_prov,
            status="pass_with_blockers",
            verdict="accepted_for_selector_evaluation_not_promotion",
            errors=[],
            blockers=["timing"],
            provenance_status={"accepted": True, "trace_npz_sha256_actual": trace_sha, "status": "accepted"},
            strict_require_trace=True,
        )
        receipt_path = FIX / f"{REVUP}_accepted_receipt.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        relocated_receipt = verdict_mod._make_receipt(
            trace_npz=dst_trace,
            provenance_json=dst_prov,
            status="pass_with_blockers",
            verdict="accepted_for_selector_evaluation_not_promotion",
            errors=[],
            blockers=["timing"],
            provenance_status={"accepted": True, "trace_npz_sha256_actual": trace_sha, "status": "accepted"},
            strict_require_trace=True,
        )
        case_results["subject_set_stable_after_rename"] = receipt.get("evidence_subject_set_sha256") == relocated_receipt.get("evidence_subject_set_sha256")
        case_results["paths_differ_but_hashes_match"] = receipt.get("trace_npz") != relocated_receipt.get("trace_npz") and receipt.get("trace_npz_sha256") == relocated_receipt.get("trace_npz_sha256")
        default_eval = selector_mod.evaluate_receipt(receipt_path=receipt_path, selector_receipt_path=FIX / f"{REVUP}_original_selector_entry_receipt.json", strict=True)
        moved_eval = selector_mod.evaluate_receipt(receipt_path=receipt_path, trace_npz_override=dst_trace, provenance_json_override=dst_prov, selector_receipt_path=FIX / f"{REVUP}_relocated_selector_entry_receipt.json", strict=True)
        bad_eval = selector_mod.evaluate_receipt(receipt_path=receipt_path, trace_npz_override=bad_trace, provenance_json_override=bad_prov, selector_receipt_path=FIX / f"{REVUP}_tampered_selector_entry_receipt.json", strict=True)
        case_results["selector_allows_original_matching_files"] = default_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not default_eval.get("errors")
        case_results["selector_allows_relocated_matching_files"] = moved_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not moved_eval.get("errors")
        case_results["selector_blocks_tampered_relocated_trace"] = bad_eval.get("status") == "fail" and any("actual trace_npz hash" in str(e) for e in bad_eval.get("errors", []))
        forged_v1 = dict(receipt)
        forged_v1["receipt_contract"] = "public_trace_evaluation_receipt_v1"
        forged_v1.pop("evidence_subject_set_sha256", None)
        forged_path = FIX / f"{REVUP}_forged_v1_receipt.json"
        forged_path.write_text(json.dumps(forged_v1, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        forged_eval = selector_mod.evaluate_receipt(receipt_path=forged_path, trace_npz_override=dst_trace, provenance_json_override=dst_prov, selector_receipt_path=FIX / f"{REVUP}_forged_v1_selector_entry_receipt.json", strict=True)
        case_results["selector_blocks_v1_or_missing_subject_set"] = forged_eval.get("status") == "fail" and forged_eval.get("verdict") == "selector_entry_blocked_wrong_receipt_contract"
        if not all(case_results.values()):
            errors.append("relocation receipt case failed: " + json.dumps(case_results, sort_keys=True))
    except Exception as exc:
        errors.append("relocation audit exception: " + repr(exc))
        case_results["exception"] = repr(exc)

    blockers = [
        "real_public_trace_bundle_still_missing",
        "receipt_relocation_contract_only_opens_evaluation_for_matching_actual_files",
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
        "summary": "Tests that v2 evaluation receipts are content-addressed: moving or renaming an accepted trace/provenance pair preserves the subject-set digest and selector entry if actual file hashes still match; tampered relocated files and old v1 receipts stay blocked.",
        "fixture_dir": FIX.relative_to(ROOT).as_posix(),
        "case_results": case_results,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://slsa.dev/spec/v1.0/provenance", "note": "Digest-bound subjects are the right primitive for artifact movement and provenance handoff."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md", "note": "ResourceDescriptors include names and digests; semantic names plus SHA-256 digest checks avoid path-only identity."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_RECEIPT_RELOCATION_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace receipt relocation audit — {REVUP}", "",
        f"Status: `{audit['status']}`  ", "Promotion allowed: `false`", "",
        audit["summary"], "", "## Cases", "",
    ]
    md.extend([f"- `{k}` = `{v}`" for k, v in case_results.items()])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_RECEIPT_RELOCATION_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "case_results": case_results, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
