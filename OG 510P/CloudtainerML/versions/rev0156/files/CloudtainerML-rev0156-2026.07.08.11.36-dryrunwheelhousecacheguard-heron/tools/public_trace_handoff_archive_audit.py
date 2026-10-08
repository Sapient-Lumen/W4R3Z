#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(REV.replace("rev", ""))
OUT = ROOT / "artifacts" / "audit"
FIX = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_HANDOFF_ARCHIVE_FIXTURES"
OUT.mkdir(parents=True, exist_ok=True)
FIX.mkdir(parents=True, exist_ok=True)
TOOLCHAIN_SUBJECTS = {
    "public_trace_selector_receipt_replay_gate": "tools/public_trace_selector_receipt_replay_gate.py",
    "public_trace_selector_entry_gate": "tools/public_trace_selector_entry_gate.py",
    "public_trace_evaluation_verdict_audit": "tools/public_trace_evaluation_verdict_audit.py",
    "public_trace_gate_surrogate_verifier": "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
    "public_trace_handoff_archive_gate": "tools/public_trace_handoff_archive_gate.py",
    "public_trace_cold_reviewer_verify_wrapper": "VERIFY_HANDOFF.py",
}


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


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_sha256(obj: Any) -> str:
    import hashlib
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def normalized(subjects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"name": s.get("name"), "path": s.get("path"), "digest": s.get("digest", {})} for s in subjects]


def subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    return stable_sha256({"handoff_contract": "public_trace_handoff_archive_v1", "subjects": normalized(subjects)})


def toolpack_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    tool_subjects = [s for s in subjects if s.get("name") in TOOLCHAIN_SUBJECTS]
    return stable_sha256({"toolpack_contract": "public_trace_handoff_toolpack_v1", "subjects": normalized(tool_subjects)})


def copy_tool_into_handoff(handoff_dir: Path, relpath: str) -> Path:
    src = ROOT / relpath
    dst = handoff_dir / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def write_handoff_manifest(handoff_dir: Path, *, trace: Path, prov: Path, eval_receipt: Path, selector_receipt: Path) -> Path:
    subjects = [
        {"name": "public_trace_npz", "path": trace.relative_to(handoff_dir).as_posix(), "digest": {"sha256": sha256_file(trace)}},
        {"name": "public_trace_provenance_json", "path": prov.relative_to(handoff_dir).as_posix(), "digest": {"sha256": sha256_file(prov)}},
        {"name": "public_trace_evaluation_receipt", "path": eval_receipt.relative_to(handoff_dir).as_posix(), "digest": {"sha256": sha256_file(eval_receipt)}},
        {"name": "public_trace_selector_entry_receipt", "path": selector_receipt.relative_to(handoff_dir).as_posix(), "digest": {"sha256": sha256_file(selector_receipt)}},
    ]
    for name, relpath in TOOLCHAIN_SUBJECTS.items():
        copied = copy_tool_into_handoff(handoff_dir, relpath)
        subjects.append({"name": name, "path": relpath, "digest": {"sha256": sha256_file(copied)}})
    manifest = {
        "handoff_contract": "public_trace_handoff_archive_v1",
        "toolpack_contract": "public_trace_handoff_toolpack_v1",
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": True,
        "gpu_fused_kernel_measured": False,
        "selector_entry_receipt_contract": "public_trace_selector_entry_receipt_v1",
        "evaluation_receipt_contract": "public_trace_evaluation_receipt_v2",
        "paths_relative_to_manifest_dir": True,
        "subjects": subjects,
        "handoff_subject_set_sha256": subject_set_sha256(subjects),
        "toolpack_subject_set_sha256": toolpack_subject_set_sha256(subjects),
        "summary": "Portable handoff manifest for replaying an accepted evaluation receipt and selector-entry receipt by digest after archive extraction. It carries a self-contained verifier/evaluator/selector toolpack by hash. Fixture only in audit; not promotion evidence.",
    }
    manifest_path = handoff_dir / "PUBLIC_TRACE_HANDOFF_MANIFEST.json"
    write_json(manifest_path, manifest)
    return manifest_path


def zip_dir(src: Path, dest: Path) -> None:
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, arcname=p.relative_to(src).as_posix())


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    case_results: dict[str, Any] = {}
    source_checks: dict[str, bool] = {}
    try:
        gate_src = (ROOT / "tools" / "public_trace_handoff_archive_gate.py").read_text(encoding="utf-8")
        required_terms = [
            "public_trace_handoff_archive_v1",
            "public_trace_handoff_toolpack_v1",
            "paths_relative_to_manifest_dir",
            "handoff_subject_set_sha256",
            "toolpack_subject_set_sha256",
            "selector_receipt_replay_verified_selector_entry_not_promotion",
            "must be relative, not absolute",
            "escapes handoff directory",
            "public_trace_selector_receipt_replay_gate",
            "public_trace_selector_entry_gate",
            "public_trace_evaluation_verdict_audit",
            "public_trace_gate_surrogate_verifier",
            "public_trace_cold_reviewer_verify_wrapper",
            "PUBLIC_TRACE_HANDOFF_MANIFEST.json",
        ]
        source_checks = {term: (term in gate_src) for term in required_terms}
        for term, present in source_checks.items():
            if not present:
                errors.append("handoff archive gate source missing term: " + term)

        verdict_mod = load_module("tools/public_trace_evaluation_verdict_audit.py", "_handoff_verdict")
        selector_mod = load_module("tools/public_trace_selector_entry_gate.py", "_handoff_selector")
        gate_mod = load_module("tools/public_trace_handoff_archive_gate.py", "_handoff_gate")
        if FIX.exists():
            shutil.rmtree(FIX)
        build = FIX / "build" / "handoff"
        extracted = FIX / "extracted" / "handoff"
        tampered = FIX / "tampered" / "handoff"
        tampered_tool = FIX / "tampered_tool" / "handoff"
        build.mkdir(parents=True, exist_ok=True)
        (build / "evidence").mkdir(parents=True, exist_ok=True)
        (build / "receipts").mkdir(parents=True, exist_ok=True)
        trace = build / "evidence" / "trace.npz"
        prov = build / "evidence" / "trace.provenance.json"
        trace.write_bytes((REV + " handoff archive trace fixture bytes\n").encode("utf-8"))
        prov.write_text(json.dumps({"fixture": REV + " handoff archive provenance"}) + "\n", encoding="utf-8")
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
        eval_receipt = build / "receipts" / "evaluation_receipt.json"
        write_json(eval_receipt, accepted)
        selector_receipt = build / "receipts" / "selector_entry_receipt.json"
        selector_eval = selector_mod.evaluate_receipt(receipt_path=eval_receipt, selector_receipt_path=selector_receipt, strict=True)
        case_results["selector_entry_fixture_opened"] = selector_eval.get("verdict") == "selector_entry_allowed_not_promotion" and not selector_eval.get("errors")
        manifest = write_handoff_manifest(build, trace=trace, prov=prov, eval_receipt=eval_receipt, selector_receipt=selector_receipt)
        direct_gate = gate_mod.evaluate_handoff(handoff_dir=build, manifest_path=manifest, strict=True)
        case_results["direct_toolpacked_handoff_gate_passes"] = direct_gate.get("verdict") == "handoff_archive_replay_verified_not_promotion" and not direct_gate.get("errors")
        case_results["toolpack_subject_set_verified"] = bool(direct_gate.get("toolpack_subject_set_sha256")) and direct_gate.get("toolpack_subject_set_sha256") == direct_gate.get("actual_toolpack_subject_set_sha256")

        archive = FIX / f"{REVUP}_portable_handoff_fixture.zip"
        zip_dir(build, archive)
        extracted.parent.mkdir(parents=True, exist_ok=True)
        if extracted.exists():
            shutil.rmtree(extracted)
        with zipfile.ZipFile(archive) as z:
            z.extractall(extracted)
        extracted_manifest = extracted / "PUBLIC_TRACE_HANDOFF_MANIFEST.json"
        extracted_gate = gate_mod.evaluate_handoff(handoff_dir=extracted, manifest_path=extracted_manifest, strict=True)
        case_results["extracted_archive_gate_passes"] = extracted_gate.get("verdict") == "handoff_archive_replay_verified_not_promotion" and not extracted_gate.get("errors")
        case_results["archive_movement_preserves_subject_sets"] = direct_gate.get("actual_handoff_subject_set_sha256") == extracted_gate.get("actual_handoff_subject_set_sha256") and direct_gate.get("actual_toolpack_subject_set_sha256") == extracted_gate.get("actual_toolpack_subject_set_sha256")

        if tampered.exists():
            shutil.rmtree(tampered)
        shutil.copytree(extracted, tampered)
        (tampered / "evidence" / "trace.npz").write_bytes(("tampered " + REV + " handoff archive trace bytes\n").encode("utf-8"))
        tampered_gate = gate_mod.evaluate_handoff(handoff_dir=tampered, manifest_path=tampered / "PUBLIC_TRACE_HANDOFF_MANIFEST.json", strict=False)
        case_results["tampered_extracted_trace_blocks"] = tampered_gate.get("status") == "fail" and any("public_trace_npz" in str(e) or "handoff_subject_set_sha256" in str(e) for e in tampered_gate.get("errors", []))

        manifest_obj = json.loads(extracted_manifest.read_text(encoding="utf-8"))
        for sub in manifest_obj["subjects"]:
            if sub.get("name") == "public_trace_npz":
                sub["path"] = "../outside.npz"
        escape_manifest = tampered / "PUBLIC_TRACE_HANDOFF_MANIFEST_ESCAPE.json"
        write_json(escape_manifest, manifest_obj)
        escape_gate = gate_mod.evaluate_handoff(handoff_dir=tampered, manifest_path=escape_manifest, strict=False)
        case_results["path_escape_manifest_blocks"] = escape_gate.get("status") == "fail" and any("escapes handoff directory" in str(e) for e in escape_gate.get("errors", []))

        manifest_obj = json.loads(extracted_manifest.read_text(encoding="utf-8"))
        manifest_obj["handoff_subject_set_sha256"] = "0" * 64
        forged_manifest = tampered / "PUBLIC_TRACE_HANDOFF_MANIFEST_FORGED_SUBJECT_SET.json"
        write_json(forged_manifest, manifest_obj)
        forged_gate = gate_mod.evaluate_handoff(handoff_dir=tampered, manifest_path=forged_manifest, strict=False)
        case_results["forged_handoff_subject_set_blocks"] = forged_gate.get("status") == "fail" and any("handoff_subject_set_sha256" in str(e) for e in forged_gate.get("errors", []))

        manifest_obj = json.loads(extracted_manifest.read_text(encoding="utf-8"))
        manifest_obj["toolpack_subject_set_sha256"] = "1" * 64
        forged_toolpack_manifest = tampered / "PUBLIC_TRACE_HANDOFF_MANIFEST_FORGED_TOOLPACK.json"
        write_json(forged_toolpack_manifest, manifest_obj)
        forged_toolpack_gate = gate_mod.evaluate_handoff(handoff_dir=tampered, manifest_path=forged_toolpack_manifest, strict=False)
        case_results["forged_toolpack_subject_set_blocks"] = forged_toolpack_gate.get("status") == "fail" and any("toolpack_subject_set_sha256" in str(e) for e in forged_toolpack_gate.get("errors", []))

        manifest_obj = json.loads(extracted_manifest.read_text(encoding="utf-8"))
        manifest_obj["subjects"] = [s for s in manifest_obj["subjects"] if s.get("name") != "public_trace_evaluation_verdict_audit"]
        missing_tool_manifest = tampered / "PUBLIC_TRACE_HANDOFF_MANIFEST_MISSING_TOOL.json"
        write_json(missing_tool_manifest, manifest_obj)
        missing_tool_gate = gate_mod.evaluate_handoff(handoff_dir=tampered, manifest_path=missing_tool_manifest, strict=False)
        case_results["missing_toolpack_subject_blocks"] = missing_tool_gate.get("status") == "fail" and any("public_trace_evaluation_verdict_audit" in str(e) for e in missing_tool_gate.get("errors", []))

        if tampered_tool.exists():
            shutil.rmtree(tampered_tool)
        shutil.copytree(extracted, tampered_tool)
        tool_path = tampered_tool / "tools" / "public_trace_evaluation_verdict_audit.py"
        tool_path.write_text(tool_path.read_text(encoding="utf-8") + "\n# tamper\n", encoding="utf-8")
        tampered_tool_gate = gate_mod.evaluate_handoff(handoff_dir=tampered_tool, manifest_path=tampered_tool / "PUBLIC_TRACE_HANDOFF_MANIFEST.json", strict=False)
        case_results["tampered_toolpack_tool_blocks"] = tampered_tool_gate.get("status") == "fail" and any("public_trace_evaluation_verdict_audit" in str(e) or "toolpack_subject_set_sha256" in str(e) for e in tampered_tool_gate.get("errors", []))

        if not all(case_results.values()):
            errors.append("handoff archive audit case failed: " + json.dumps(case_results, sort_keys=True))
    except Exception as exc:
        errors.append("handoff archive audit exception: " + repr(exc))
        case_results["exception"] = repr(exc)

    blockers = [
        "real_public_trace_handoff_archive_missing",
        "portable_handoff_archive_is_selector_entry_not_promotion_evidence",
        "named_hardware_timing_still_required_for_promotion",
    ]
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Audits a self-contained public-trace handoff archive: an accepted evaluation receipt plus selector-entry receipt can be zipped, extracted, moved, and replayed by relative paths and SHA-256 subject digests, while the archive also carries the verifier/evaluator/selector/replay toolpack and cold-reviewer wrapper by digest. Tampered files, missing tools, tool tampering, path escapes, and forged subject-set hashes stay blocked.",
        "fixture_dir": FIX.relative_to(ROOT).as_posix(),
        "source_checks": source_checks,
        "case_results": case_results,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://slsa.dev/spec/v1.2/verifying-artifacts", "note": "SLSA verification stresses that provenance only helps if someone inspects it; rev0112 makes the handoff inspect both subjects and verification tools."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md", "note": "In-toto Statements bind predicates to subject names/digests; rev0112 applies that pattern to both trace subjects and tool subjects."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "note": "HF snapshot downloads require explicit revisions for immutable identity; the handoff archive is similarly digest-first rather than path-label-first."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_HANDOFF_ARCHIVE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace handoff archive audit — {REVUP}", "",
        f"Status: `{audit['status']}`  ", "Promotion allowed: `false`", "",
        audit["summary"], "", "## Cases", "",
    ]
    md.extend([f"- `{k}` = `{v}`" for k, v in case_results.items()])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_HANDOFF_ARCHIVE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "case_results": case_results, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
