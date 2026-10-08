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
FIX = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_SELECTOR_RECEIPT_REPLAY_FIXTURES"
OUT.mkdir(parents=True, exist_ok=True)
FIX.mkdir(parents=True, exist_ok=True)


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
    try:
        replay_src = (ROOT / "tools" / "public_trace_selector_receipt_replay_gate.py").read_text(encoding="utf-8")
        reloc_src = (ROOT / "tools" / "public_trace_receipt_relocation_audit.py").read_text(encoding="utf-8")
        required_terms = [
            "public_trace_selector_entry_receipt_v1", "actual_bundle_subject_set_sha256",
            "input_receipt_sha256", "path_relocation_supported_with_overrides", "--selector-entry-receipt-json",
            "selector_receipt_replay_verified_selector_entry_not_promotion",
        ]
        source_checks = {term: (term in replay_src) for term in required_terms}
        for term, present in source_checks.items():
            if not present:
                errors.append("selector receipt replay gate source missing term: " + term)
        if "selector_receipt_path=FIX" not in reloc_src:
            errors.append("relocation audit still risks overwriting the default selector-entry receipt")

        verdict_mod = load_module("tools/public_trace_evaluation_verdict_audit.py", "_replay_verdict")
        selector_mod = load_module("tools/public_trace_selector_entry_gate.py", "_replay_selector")
        replay_mod = load_module("tools/public_trace_selector_receipt_replay_gate.py", "_replay_gate")
        if FIX.exists():
            shutil.rmtree(FIX)
        original = FIX / "original"
        relocated = FIX / "relocated"
        tampered = FIX / "tampered"
        for d in [original, relocated, tampered]:
            d.mkdir(parents=True, exist_ok=True)
        trace = original / "trace.npz"
        prov = original / "trace.provenance.json"
        trace.write_bytes(b"rev0110 selector receipt replay trace fixture bytes\n")
        prov.write_text('{"fixture":"rev0110 selector receipt replay provenance"}\n', encoding="utf-8")
        relocated_trace = relocated / "renamed-trace.npz"
        relocated_prov = relocated / "renamed-trace.provenance.json"
        shutil.copy2(trace, relocated_trace)
        shutil.copy2(prov, relocated_prov)
        bad_trace = tampered / "renamed-trace.npz"
        bad_trace.write_bytes(b"tampered rev0110 selector receipt replay bytes\n")

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
        eval_receipt_path = original / f"{REVUP}_accepted_evaluation_receipt.json"
        write_json(eval_receipt_path, accepted)
        selector_receipt_path = original / f"{REVUP}_selector_entry_receipt.json"
        selector_eval = selector_mod.evaluate_receipt(receipt_path=eval_receipt_path, selector_receipt_path=selector_receipt_path, strict=True)
        case_results["selector_gate_fixture_opened"] = selector_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not selector_eval.get("errors")
        replay_original = replay_mod.evaluate_chain(selector_receipt_path=selector_receipt_path, evaluation_receipt_path=eval_receipt_path, strict=True)
        case_results["replay_original_selector_receipt_passes"] = replay_original.get("verdict") == "selector_receipt_replay_verified_selector_entry_not_promotion" and not replay_original.get("errors")

        relocated_eval_receipt = relocated / f"{REVUP}_accepted_evaluation_receipt_RENAMED.json"
        relocated_selector_receipt = relocated / f"{REVUP}_selector_entry_receipt_RENAMED.json"
        shutil.copy2(eval_receipt_path, relocated_eval_receipt)
        shutil.copy2(selector_receipt_path, relocated_selector_receipt)
        replay_moved = replay_mod.evaluate_chain(
            selector_receipt_path=relocated_selector_receipt,
            evaluation_receipt_path=relocated_eval_receipt,
            trace_npz=relocated_trace,
            provenance_json=relocated_prov,
            strict=True,
        )
        case_results["replay_relocated_with_overrides_passes"] = replay_moved.get("verdict") == "selector_receipt_replay_verified_selector_entry_not_promotion" and not replay_moved.get("errors")

        replay_tampered = replay_mod.evaluate_chain(
            selector_receipt_path=relocated_selector_receipt,
            evaluation_receipt_path=relocated_eval_receipt,
            trace_npz=bad_trace,
            provenance_json=relocated_prov,
            strict=False,
        )
        case_results["replay_tampered_trace_blocks"] = replay_tampered.get("status") == "fail" and any("public_trace_npz" in str(e) or "actual_bundle_subject_set" in str(e) for e in replay_tampered.get("errors", []))

        forged_selector = json.loads(selector_receipt_path.read_text(encoding="utf-8"))
        forged_selector["actual_bundle_subject_set_sha256"] = "0" * 64
        forged_selector_path = tampered / f"{REVUP}_forged_selector_subject_set_receipt.json"
        write_json(forged_selector_path, forged_selector)
        replay_forged_subject = replay_mod.evaluate_chain(selector_receipt_path=forged_selector_path, evaluation_receipt_path=eval_receipt_path, strict=False)
        case_results["forged_selector_subject_set_blocks"] = replay_forged_subject.get("status") == "fail" and any("actual_bundle_subject_set" in str(e) for e in replay_forged_subject.get("errors", []))

        forged_tool = json.loads(selector_receipt_path.read_text(encoding="utf-8"))
        forged_tool["selector_gate_tool_sha256"] = "f" * 64
        forged_tool_path = tampered / f"{REVUP}_forged_selector_tool_receipt.json"
        write_json(forged_tool_path, forged_tool)
        replay_forged_tool = replay_mod.evaluate_chain(selector_receipt_path=forged_tool_path, evaluation_receipt_path=eval_receipt_path, strict=False)
        case_results["forged_selector_tool_hash_blocks"] = replay_forged_tool.get("status") == "fail" and any("selector_gate_tool_sha256" in str(e) for e in replay_forged_tool.get("errors", []))

        default_receipt_path = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json"
        default_receipt = json.loads(default_receipt_path.read_text(encoding="utf-8")) if default_receipt_path.exists() else {}
        case_results["default_selector_receipt_not_fixture_overwritten"] = not str(default_receipt.get("input_receipt_json", "")).startswith("artifacts/trace-bundles/")

        if not all(case_results.values()):
            errors.append("selector receipt replay case failed: " + json.dumps(case_results, sort_keys=True))
    except Exception as exc:
        errors.append("selector receipt replay audit exception: " + repr(exc))
        case_results["exception"] = repr(exc)

    blockers = [
        "real_public_trace_npz_and_provenance_pair_missing",
        "selector_receipt_replay_is_handoff_not_promotion_evidence",
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
        "summary": "Audits the final selector-entry handoff replay: a selector-entry receipt may be moved or renamed only if the evaluation receipt, trace NPZ, provenance JSON, verifier, evaluator, and selector gate all replay to the same subject digests. It also prevents fixture negative cases from overwriting the default current selector receipt.",
        "source_checks": source_checks,
        "case_results": case_results,
        "fixture_dir": FIX.relative_to(ROOT).as_posix(),
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://slsa.dev/spec/v1.0/provenance", "note": "SLSA provenance models artifact subjects by digest; rev0110 applies that to selector-entry replay."},
            {"url": "https://slsa.dev/blog/2023/05/in-toto-and-slsa", "note": "In-toto/SLSA statements bind predicates to subjects, which motivates a separate replay gate over selector-entry handoff receipts."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "note": "Hugging Face snapshot workflows distinguish local/cache paths from reviewed model revision identity."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace selector receipt replay audit — {REVUP}", "",
        f"Status: `{audit['status']}`  ", "Promotion allowed: `false`", "",
        audit["summary"], "", "## Cases", "",
    ]
    md.extend([f"- `{k}` = `{v}`" for k, v in case_results.items()])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "case_results": case_results, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
