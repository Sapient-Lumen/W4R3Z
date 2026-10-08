#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
PROBE_OUT = ROOT / "artifacts" / "probe-results"
OUT.mkdir(parents=True, exist_ok=True)
PROBE_OUT.mkdir(parents=True, exist_ok=True)
RECEIPT_CONTRACT = "public_trace_evaluation_receipt_v2"
SELECTOR_ENTRY_RECEIPT_CONTRACT = "public_trace_selector_entry_receipt_v1"
SELECTOR_TOOL_REL = "tools/public_trace_selector_entry_gate.py"
REQUIRED_RECEIPT_SUBJECTS = {
    "public_trace_npz": "trace_npz_sha256",
    "public_trace_provenance_json": "provenance_json_sha256",
    "public_trace_verifier_tool": "gate_verifier_sha256",
    "public_trace_evaluator_tool": "evaluator_tool_sha256",
}


def _default_receipt() -> Path:
    return ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT.json"


def _default_selector_receipt() -> Path:
    return ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json"


def load_receipt(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": True}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc)}


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _stable_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _resolve_receipt_path(value: Any) -> Path | None:
    if not value:
        return None
    p = Path(str(value))
    return p if p.is_absolute() else ROOT / p


def _resolve_tool_path(value: Any, errors: list[str], *, field_name: str) -> Path | None:
    if not value:
        errors.append(f"receipt missing {field_name}")
        return None
    p = Path(str(value))
    if p.is_absolute():
        try:
            p.resolve().relative_to(ROOT.resolve())
        except Exception:
            errors.append(f"{field_name} must not point outside the cube")
            return None
        return p
    return ROOT / p


def _rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _normalized_receipt_subjects(subjects: Any) -> list[dict[str, Any]]:
    if not isinstance(subjects, list):
        return []
    out: list[dict[str, Any]] = []
    for item in subjects:
        if not isinstance(item, dict):
            continue
        out.append({
            "name": item.get("name"),
            "digest": item.get("digest", {}),
            "reported_by_verifier_sha256": item.get("reported_by_verifier_sha256"),
        })
    return out


def _receipt_subject_set_sha256(receipt: dict[str, Any]) -> str | None:
    subjects = _normalized_receipt_subjects(receipt.get("evidence_subjects"))
    if not subjects:
        return None
    return _stable_sha256({"receipt_contract": receipt.get("receipt_contract"), "subjects": subjects})


def _subject_digest_map(receipt: dict[str, Any], errors: list[str]) -> dict[str, str | None]:
    subjects = receipt.get("evidence_subjects")
    if not isinstance(subjects, list):
        errors.append("receipt missing evidence_subjects list")
        return {}
    names_seen: set[str] = set()
    out: dict[str, str | None] = {}
    for item in subjects:
        if not isinstance(item, dict):
            errors.append("receipt evidence_subjects contains non-object entry")
            continue
        name = str(item.get("name"))
        if name in names_seen:
            errors.append("duplicate receipt evidence subject name: " + name)
        names_seen.add(name)
        digest = item.get("digest")
        sha = digest.get("sha256") if isinstance(digest, dict) else None
        out[name] = sha
    for required in REQUIRED_RECEIPT_SUBJECTS:
        if required not in out:
            errors.append("receipt missing required evidence subject: " + required)
    return out


def _actual_bundle_subjects(*, trace_sha: str | None, prov_sha: str | None, verifier_sha: str | None, evaluator_sha: str | None, selector_sha: str | None, receipt_sha: str | None) -> list[dict[str, Any]]:
    return [
        {"name": "public_trace_npz", "digest": {"sha256": trace_sha}},
        {"name": "public_trace_provenance_json", "digest": {"sha256": prov_sha}},
        {"name": "public_trace_verifier_tool", "digest": {"sha256": verifier_sha}},
        {"name": "public_trace_evaluator_tool", "digest": {"sha256": evaluator_sha}},
        {"name": "public_trace_selector_entry_gate", "digest": {"sha256": selector_sha}},
        {"name": "public_trace_evaluation_receipt", "digest": {"sha256": receipt_sha}},
    ]


def _actual_bundle_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    normalized = [{"name": s.get("name"), "digest": s.get("digest", {})} for s in subjects]
    return _stable_sha256({"selector_entry_receipt_contract": SELECTOR_ENTRY_RECEIPT_CONTRACT, "subjects": normalized})


def _write_selector_entry_receipt(path: Path, receipt: dict[str, Any], audit: dict[str, Any], actual_subjects: list[dict[str, Any]], input_receipt_sha: str | None) -> str | None:
    selector_receipt = {
        "selector_entry_receipt_contract": SELECTOR_ENTRY_RECEIPT_CONTRACT,
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": audit.get("status"),
        "verdict": audit.get("verdict"),
        "selector_entry_allowed": audit.get("verdict") == "selector_entry_allowed_not_promotion",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": audit.get("verdict") == "selector_entry_allowed_not_promotion",
        "named_hardware_timing_still_required_for_promotion": True,
        "input_receipt_json": audit.get("receipt_json"),
        "input_receipt_sha256": input_receipt_sha,
        "input_receipt_contract": receipt.get("receipt_contract"),
        "input_receipt_subject_set_sha256": receipt.get("evidence_subject_set_sha256"),
        "recomputed_input_receipt_subject_set_sha256": audit.get("recomputed_receipt_subject_set_sha256"),
        "input_receipt_subject_set_verified": audit.get("receipt_subject_set_verified") is True,
        "selector_gate_tool": SELECTOR_TOOL_REL,
        "selector_gate_tool_sha256": audit.get("selector_gate_tool_sha256"),
        "actual_bundle_subjects": actual_subjects,
        "actual_bundle_subject_set_sha256": _actual_bundle_subject_set_sha256(actual_subjects),
        "actual_bundle_subject_set_verified": audit.get("actual_bundle_subjects_verified") is True,
        "errors": audit.get("errors", []),
        "blockers": audit.get("blockers", []),
        "summary": "Selector-entry receipt emitted after the narrow selector gate checked the accepted evaluation receipt, recomputed the receipt subject-set digest, verified current evaluator/verifier/selector tool hashes, and matched actual NPZ/provenance file hashes. It is a handoff receipt for selector/cost evaluation, not promotion evidence.",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(selector_receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return sha256_file(path)


def evaluate_receipt(*, receipt_path: Path, trace_npz_override: Path | None = None, provenance_json_override: Path | None = None, selector_receipt_path: Path | None = None, strict: bool = False) -> dict[str, Any]:
    receipt = load_receipt(receipt_path)
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    actual_trace_path = trace_npz_override
    actual_prov_path = provenance_json_override
    actual_trace_sha = None
    actual_prov_sha = None
    actual_verifier_sha = None
    actual_evaluator_sha = None
    selector_sha = sha256_file(ROOT / SELECTOR_TOOL_REL)
    receipt_sha = sha256_file(receipt_path)
    recomputed_subject_set = None
    receipt_subject_set_verified = False
    actual_bundle_subjects_verified = False

    if receipt.get("_missing"):
        status = "pass_with_blockers"
        verdict = "selector_entry_blocked_no_receipt"
        blockers.append("evaluation_receipt_missing")
    elif receipt.get("_load_error"):
        status = "fail"
        verdict = "selector_entry_blocked_malformed_receipt"
        errors.append("could not load receipt: " + str(receipt.get("_load_error")))
    elif receipt.get("receipt_contract") != RECEIPT_CONTRACT:
        status = "fail"
        verdict = "selector_entry_blocked_wrong_receipt_contract"
        errors.append("receipt_contract must be " + RECEIPT_CONTRACT)
    else:
        if actual_trace_path is None:
            actual_trace_path = _resolve_receipt_path(receipt.get("trace_npz"))
        if actual_prov_path is None:
            actual_prov_path = _resolve_receipt_path(receipt.get("provenance_json"))
        if actual_trace_path is not None:
            actual_trace_sha = sha256_file(actual_trace_path)
        if actual_prov_path is not None:
            actual_prov_sha = sha256_file(actual_prov_path)

        recomputed_subject_set = _receipt_subject_set_sha256(receipt)
        if not receipt.get("evidence_subject_set_sha256"):
            errors.append("receipt missing evidence_subject_set_sha256")
        elif recomputed_subject_set != receipt.get("evidence_subject_set_sha256"):
            errors.append("receipt evidence_subject_set_sha256 does not match recomputed evidence_subjects digest")
        else:
            receipt_subject_set_verified = True

        subject_map = _subject_digest_map(receipt, errors)
        for subject_name, top_key in REQUIRED_RECEIPT_SUBJECTS.items():
            if subject_name in subject_map and subject_map.get(subject_name) != receipt.get(top_key):
                errors.append(f"receipt subject {subject_name} digest does not match top-level {top_key}")

        verifier_path = _resolve_tool_path(receipt.get("gate_verifier"), errors, field_name="gate_verifier")
        evaluator_path = _resolve_tool_path(receipt.get("evaluator_tool"), errors, field_name="evaluator_tool")
        actual_verifier_sha = sha256_file(verifier_path) if verifier_path else None
        actual_evaluator_sha = sha256_file(evaluator_path) if evaluator_path else None
        if actual_verifier_sha != receipt.get("gate_verifier_sha256"):
            errors.append("actual gate_verifier hash does not match receipt gate_verifier_sha256")
        if actual_evaluator_sha != receipt.get("evaluator_tool_sha256"):
            errors.append("actual evaluator_tool hash does not match receipt evaluator_tool_sha256")

        if receipt.get("promotion_allowed") is not False:
            errors.append("receipt must not permit promotion")
        if receipt.get("receipt_identity_errors"):
            errors.append("receipt_identity_errors present: " + json.dumps(receipt.get("receipt_identity_errors"), sort_keys=True))
        if receipt.get("trace_npz_sha256_reported_by_verifier") and receipt.get("trace_npz_sha256") and receipt.get("trace_npz_sha256_reported_by_verifier") != receipt.get("trace_npz_sha256"):
            errors.append("receipt trace hash does not match verifier-reported trace hash")

        base_accept = bool(
            receipt.get("selector_evaluation_entry_allowed") is True
            and receipt.get("accepted_for_selector_evaluation") is True
            and receipt.get("provenance_verifier_accepted") is True
            and receipt.get("trace_npz_sha256")
            and receipt.get("provenance_json_sha256")
            and receipt.get("gate_verifier_sha256")
            and receipt.get("evaluator_tool_sha256")
            and receipt_subject_set_verified
            and actual_verifier_sha == receipt.get("gate_verifier_sha256")
            and actual_evaluator_sha == receipt.get("evaluator_tool_sha256")
            and selector_sha
        )
        if not base_accept:
            status = "pass_with_blockers" if not errors else "fail"
            verdict = "selector_entry_blocked_until_accepted_receipt"
            blockers.append("evaluation_receipt_not_accepted_for_selector_entry")
        else:
            if actual_trace_sha is None:
                errors.append("accepted receipt has no readable trace_npz at receipt path or override")
            elif actual_trace_sha != receipt.get("trace_npz_sha256"):
                errors.append("actual trace_npz hash does not match receipt trace_npz_sha256")
            if actual_prov_sha is None:
                errors.append("accepted receipt has no readable provenance_json at receipt path or override")
            elif actual_prov_sha != receipt.get("provenance_json_sha256"):
                errors.append("actual provenance_json hash does not match receipt provenance_json_sha256")
            if errors:
                status = "fail"
                verdict = "selector_entry_blocked_receipt_file_mismatch"
            else:
                status = "pass_with_blockers"
                verdict = "selector_entry_allowed_not_promotion"
                actual_bundle_subjects_verified = True
                blockers.append("named_hardware_timing_still_required_for_promotion")

    if strict and verdict != "selector_entry_allowed_not_promotion":
        errors.append("strict selector entry requested but accepted receipt plus matching files are absent")
        status = "fail"

    actual_subjects = _actual_bundle_subjects(
        trace_sha=actual_trace_sha,
        prov_sha=actual_prov_sha,
        verifier_sha=actual_verifier_sha,
        evaluator_sha=actual_evaluator_sha,
        selector_sha=selector_sha,
        receipt_sha=receipt_sha,
    )
    selector_receipt_path = selector_receipt_path or _default_selector_receipt()
    audit = {
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": verdict == "selector_entry_allowed_not_promotion",
        "gpu_fused_kernel_measured": False,
        "receipt_json": _rel(receipt_path),
        "receipt_json_sha256": receipt_sha,
        "receipt_contract": receipt.get("receipt_contract"),
        "receipt_trace_npz_sha256": receipt.get("trace_npz_sha256"),
        "receipt_provenance_json_sha256": receipt.get("provenance_json_sha256"),
        "receipt_subject_set_sha256": receipt.get("evidence_subject_set_sha256"),
        "recomputed_receipt_subject_set_sha256": recomputed_subject_set,
        "receipt_subject_set_verified": receipt_subject_set_verified,
        "actual_trace_npz": _rel(actual_trace_path),
        "actual_trace_npz_sha256": actual_trace_sha,
        "actual_provenance_json": _rel(actual_prov_path),
        "actual_provenance_json_sha256": actual_prov_sha,
        "actual_gate_verifier_sha256": actual_verifier_sha,
        "actual_evaluator_tool_sha256": actual_evaluator_sha,
        "selector_gate_tool": SELECTOR_TOOL_REL,
        "selector_gate_tool_sha256": selector_sha,
        "selector_entry_receipt_json": _rel(selector_receipt_path),
        "selector_entry_receipt_contract": SELECTOR_ENTRY_RECEIPT_CONTRACT,
        "actual_bundle_subjects": actual_subjects,
        "actual_bundle_subject_set_sha256": _actual_bundle_subject_set_sha256(actual_subjects),
        "actual_bundle_subjects_verified": actual_bundle_subjects_verified,
        "path_override_supported": True,
        "summary": "A narrow selector-entry gate: a public trace may proceed into selector/cost evaluation only when a v2 evaluation receipt binds an accepted verifier verdict to exact NPZ/provenance/tool digests, the receipt subject-set hash recomputes cleanly, the current evaluator/verifier/selector tools match the receipt or emitted selector receipt, and the actual files match. Renaming or moving the files is safe only with matching hashes; copying or editing a receipt without matching files/tool hashes remains blocked. Promotion still requires named hardware timing.",
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
    }
    selector_receipt_sha = _write_selector_entry_receipt(selector_receipt_path, receipt, audit, actual_subjects, receipt_sha)
    audit["selector_entry_receipt_sha256"] = selector_receipt_sha
    return audit


def main() -> int:
    ap = argparse.ArgumentParser(description="Block selector/cost evaluation unless a public trace evaluation receipt explicitly opens that entry gate and the actual files match the receipt digests.")
    ap.add_argument("--receipt-json", type=Path, default=None)
    ap.add_argument("--trace-npz", type=Path, default=None, help="optional relocated trace NPZ path to check against the receipt digest")
    ap.add_argument("--provenance-json", type=Path, default=None, help="optional relocated provenance JSON path to check against the receipt digest")
    ap.add_argument("--selector-entry-receipt-json", type=Path, default=None, help="where to write the selector-entry handoff receipt")
    ap.add_argument("--strict", action="store_true", help="exit nonzero unless selector entry is allowed")
    args = ap.parse_args()

    receipt_path = args.receipt_json or _default_receipt()
    audit = evaluate_receipt(
        receipt_path=receipt_path,
        trace_npz_override=args.trace_npz,
        provenance_json_override=args.provenance_json,
        selector_receipt_path=args.selector_entry_receipt_json,
        strict=args.strict,
    )
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_GATE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace selector-entry gate — {REVUP}", "",
        f"Status: `{audit['status']}`  ", f"Verdict: `{audit['verdict']}`  ", "Promotion allowed: `false`", "",
        audit["summary"], "", "## Checked files", "",
        f"- actual trace NPZ: `{audit.get('actual_trace_npz') or 'missing'}`",
        f"- actual provenance JSON: `{audit.get('actual_provenance_json') or 'missing'}`",
        f"- selector-entry receipt: `{audit.get('selector_entry_receipt_json') or 'missing'}`",
        "", "## Blockers", "",
    ]
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] if audit.get("blockers") else ["- none"])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in audit.get("errors", [])] if audit.get("errors") else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_GATE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "verdict": audit["verdict"], "selector_entry_receipt": audit.get("selector_entry_receipt_json"), "errors": audit["errors"], "blockers": audit["blockers"]}, indent=2))
    return 0 if not audit["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
