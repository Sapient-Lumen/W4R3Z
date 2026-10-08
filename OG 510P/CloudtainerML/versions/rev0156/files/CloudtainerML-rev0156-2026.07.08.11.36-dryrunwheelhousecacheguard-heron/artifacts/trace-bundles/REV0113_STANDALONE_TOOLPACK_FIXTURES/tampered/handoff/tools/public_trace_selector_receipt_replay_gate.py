#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_meta(root: Path) -> dict[str, Any]:
    cube_meta = root / "CUBE-META.json"
    if cube_meta.exists():
        return json.loads(cube_meta.read_text(encoding="utf-8"))
    handoff_manifest = root / "PUBLIC_TRACE_HANDOFF_MANIFEST.json"
    if handoff_manifest.exists():
        try:
            manifest = json.loads(handoff_manifest.read_text(encoding="utf-8"))
            return {
                "revision": manifest.get("revision", "rev0000"),
                "revision_number": manifest.get("revision_number"),
                "package_name": manifest.get("package_name"),
                "archive_name": manifest.get("archive_name"),
                "revision_kind": "standalone_selector_receipt_replay",
            }
        except Exception:
            pass
    return {
        "revision": "rev0000",
        "revision_number": 0,
        "package_name": root.name,
        "archive_name": None,
        "revision_kind": "standalone_selector_receipt_replay_unknown",
    }


META = _load_meta(ROOT)
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
SELECTOR_RECEIPT_CONTRACT = "public_trace_selector_entry_receipt_v1"
EVALUATION_RECEIPT_CONTRACT = "public_trace_evaluation_receipt_v2"
SELECTOR_TOOL_REL = "tools/public_trace_selector_entry_gate.py"
EVALUATOR_TOOL_REL = "tools/public_trace_evaluation_verdict_audit.py"
VERIFIER_TOOL_REL = "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py"


def default_selector_receipt() -> Path:
    return ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json"


def default_evaluation_receipt() -> Path:
    return ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": True, "_path": path.as_posix()}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": path.as_posix()}


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


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def resolve_path(value: Any) -> Path | None:
    if not value:
        return None
    p = Path(str(value))
    return p if p.is_absolute() else ROOT / p


def subject_map(subjects: Any) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    if not isinstance(subjects, list):
        return out
    for item in subjects:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name"))
        digest = item.get("digest") if isinstance(item.get("digest"), dict) else {}
        out[name] = digest.get("sha256")
    return out


def selector_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    normalized = [{"name": s.get("name"), "digest": s.get("digest", {})} for s in subjects]
    return stable_sha256({"selector_entry_receipt_contract": SELECTOR_RECEIPT_CONTRACT, "subjects": normalized})


def eval_subject_set_sha256(receipt: dict[str, Any]) -> str | None:
    subjects = receipt.get("evidence_subjects")
    if not isinstance(subjects, list):
        return None
    normalized: list[dict[str, Any]] = []
    for item in subjects:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "name": item.get("name"),
            "digest": item.get("digest", {}),
            "reported_by_verifier_sha256": item.get("reported_by_verifier_sha256"),
        })
    if not normalized:
        return None
    return stable_sha256({"receipt_contract": receipt.get("receipt_contract"), "subjects": normalized})


def build_actual_subjects(*, trace_sha: str | None, prov_sha: str | None, verifier_sha: str | None, evaluator_sha: str | None, selector_sha: str | None, eval_receipt_sha: str | None) -> list[dict[str, Any]]:
    return [
        {"name": "public_trace_npz", "digest": {"sha256": trace_sha}},
        {"name": "public_trace_provenance_json", "digest": {"sha256": prov_sha}},
        {"name": "public_trace_verifier_tool", "digest": {"sha256": verifier_sha}},
        {"name": "public_trace_evaluator_tool", "digest": {"sha256": evaluator_sha}},
        {"name": "public_trace_selector_entry_gate", "digest": {"sha256": selector_sha}},
        {"name": "public_trace_evaluation_receipt", "digest": {"sha256": eval_receipt_sha}},
    ]


def evaluate_chain(*, selector_receipt_path: Path, evaluation_receipt_path: Path | None = None, trace_npz: Path | None = None, provenance_json: Path | None = None, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    selector_receipt = load_json(selector_receipt_path)

    if selector_receipt.get("_missing"):
        audit = {
            "status": "pass_with_blockers",
            "verdict": "selector_receipt_replay_blocked_no_selector_receipt",
            "errors": [],
            "warnings": [],
            "blockers": ["selector_entry_receipt_missing"],
        }
        if strict:
            audit["status"] = "fail"; audit["errors"] = ["strict replay requested but selector-entry receipt is missing"]
        return audit
    if selector_receipt.get("_load_error"):
        return {"status": "fail", "verdict": "selector_receipt_replay_blocked_malformed_selector_receipt", "errors": ["could not load selector receipt: " + str(selector_receipt.get("_load_error"))], "warnings": [], "blockers": []}
    if selector_receipt.get("selector_entry_receipt_contract") != SELECTOR_RECEIPT_CONTRACT:
        return {"status": "fail", "verdict": "selector_receipt_replay_blocked_wrong_selector_receipt_contract", "errors": ["selector_entry_receipt_contract must be " + SELECTOR_RECEIPT_CONTRACT], "warnings": [], "blockers": []}

    if selector_receipt.get("promotion_allowed") is not False:
        errors.append("selector-entry receipt must not permit promotion")
    if selector_receipt.get("revision") != REV:
        warnings.append("selector-entry receipt revision differs from current cube revision; replay continues by digest identity")

    if evaluation_receipt_path is None:
        evaluation_receipt_path = resolve_path(selector_receipt.get("input_receipt_json")) or default_evaluation_receipt()
    eval_receipt = load_json(evaluation_receipt_path)
    eval_receipt_sha = sha256_file(evaluation_receipt_path)
    selector_receipt_sha = sha256_file(selector_receipt_path)
    selector_sha = sha256_file(ROOT / SELECTOR_TOOL_REL)
    evaluator_sha = sha256_file(ROOT / EVALUATOR_TOOL_REL)
    verifier_sha = sha256_file(ROOT / VERIFIER_TOOL_REL)

    if eval_receipt.get("_missing"):
        errors.append("input evaluation receipt missing at replay path")
    elif eval_receipt.get("_load_error"):
        errors.append("could not load input evaluation receipt: " + str(eval_receipt.get("_load_error")))
    elif eval_receipt.get("receipt_contract") != EVALUATION_RECEIPT_CONTRACT:
        errors.append("input evaluation receipt contract must be " + EVALUATION_RECEIPT_CONTRACT)

    if selector_receipt.get("input_receipt_sha256") and eval_receipt_sha != selector_receipt.get("input_receipt_sha256"):
        errors.append("input evaluation receipt hash does not match selector-entry receipt input_receipt_sha256")
    if selector_receipt.get("input_receipt_subject_set_verified") is True and eval_receipt:
        recomputed_eval = eval_subject_set_sha256(eval_receipt)
        if recomputed_eval != selector_receipt.get("recomputed_input_receipt_subject_set_sha256"):
            errors.append("recomputed evaluation receipt subject set does not match selector-entry receipt")
        if eval_receipt.get("evidence_subject_set_sha256") and recomputed_eval != eval_receipt.get("evidence_subject_set_sha256"):
            errors.append("evaluation receipt evidence_subject_set_sha256 does not match recomputed digest")
    else:
        blockers.append("input_evaluation_receipt_subject_set_not_verified_by_selector_receipt")

    if trace_npz is None and isinstance(eval_receipt, dict):
        trace_npz = resolve_path(eval_receipt.get("trace_npz"))
    if provenance_json is None and isinstance(eval_receipt, dict):
        provenance_json = resolve_path(eval_receipt.get("provenance_json"))
    trace_sha = sha256_file(trace_npz)
    prov_sha = sha256_file(provenance_json)

    actual_subjects = build_actual_subjects(trace_sha=trace_sha, prov_sha=prov_sha, verifier_sha=verifier_sha, evaluator_sha=evaluator_sha, selector_sha=selector_sha, eval_receipt_sha=eval_receipt_sha)
    actual_subject_set = selector_subject_set_sha256(actual_subjects)
    reported_subject_set = selector_receipt.get("actual_bundle_subject_set_sha256")
    if reported_subject_set != actual_subject_set:
        errors.append("selector-entry receipt actual_bundle_subject_set_sha256 does not match replayed files/tools")
    reported_map = subject_map(selector_receipt.get("actual_bundle_subjects"))
    actual_map = subject_map(actual_subjects)
    for name, actual_sha in actual_map.items():
        if reported_map.get(name) != actual_sha:
            errors.append(f"selector-entry receipt subject {name} digest does not match replayed actual digest")

    if selector_receipt.get("selector_gate_tool_sha256") != selector_sha:
        errors.append("selector-entry receipt selector_gate_tool_sha256 does not match local selector gate tool")
    if eval_receipt and eval_receipt.get("gate_verifier_sha256") and eval_receipt.get("gate_verifier_sha256") != verifier_sha:
        errors.append("input evaluation receipt gate_verifier_sha256 does not match local verifier tool")
    if eval_receipt and eval_receipt.get("evaluator_tool_sha256") and eval_receipt.get("evaluator_tool_sha256") != evaluator_sha:
        errors.append("input evaluation receipt evaluator_tool_sha256 does not match local evaluator tool")

    selector_allowed = selector_receipt.get("selector_entry_allowed") is True and selector_receipt.get("verdict") == "selector_entry_allowed_not_promotion"
    if not selector_allowed:
        blockers.append("selector_entry_receipt_does_not_open_selector_entry")
        verdict = "selector_receipt_replay_blocked_until_selector_entry_allowed"
        status = "pass_with_blockers" if not errors else "fail"
    elif errors:
        verdict = "selector_receipt_replay_blocked_digest_or_tool_mismatch"
        status = "fail"
    else:
        verdict = "selector_receipt_replay_verified_selector_entry_not_promotion"
        status = "pass_with_blockers"
        blockers.append("named_hardware_timing_still_required_for_promotion")

    if strict and verdict != "selector_receipt_replay_verified_selector_entry_not_promotion":
        status = "fail"
        errors.append("strict replay requested but verified selector-entry chain is absent")

    return {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": verdict == "selector_receipt_replay_verified_selector_entry_not_promotion",
        "gpu_fused_kernel_measured": False,
        "selector_entry_receipt_json": rel(selector_receipt_path),
        "selector_entry_receipt_sha256": selector_receipt_sha,
        "evaluation_receipt_json": rel(evaluation_receipt_path),
        "evaluation_receipt_sha256": eval_receipt_sha,
        "trace_npz": rel(trace_npz),
        "trace_npz_sha256": trace_sha,
        "provenance_json": rel(provenance_json),
        "provenance_json_sha256": prov_sha,
        "selector_gate_tool_sha256": selector_sha,
        "evaluator_tool_sha256": evaluator_sha,
        "gate_verifier_sha256": verifier_sha,
        "replayed_actual_bundle_subjects": actual_subjects,
        "replayed_actual_bundle_subject_set_sha256": actual_subject_set,
        "selector_entry_receipt_subject_set_sha256": reported_subject_set,
        "path_relocation_supported_with_overrides": True,
        "summary": "Replays a selector-entry receipt after movement/renaming by verifying the selector receipt, input evaluation receipt, trace NPZ, provenance JSON, verifier tool, evaluator tool, and selector gate by SHA-256 subject digests instead of path labels. This is selector/cost-evaluation entry only; promotion still requires named-hardware timing.",
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Replay a public_trace_selector_entry_receipt_v1 against actual files and the local toolpack.")
    ap.add_argument("--selector-entry-receipt-json", type=Path, default=None)
    ap.add_argument("--evaluation-receipt-json", type=Path, default=None)
    ap.add_argument("--trace-npz", type=Path, default=None)
    ap.add_argument("--provenance-json", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    audit = evaluate_chain(
        selector_receipt_path=args.selector_entry_receipt_json or default_selector_receipt(),
        evaluation_receipt_path=args.evaluation_receipt_json,
        trace_npz=args.trace_npz,
        provenance_json=args.provenance_json,
        strict=args.strict,
    )
    if "revision" not in audit:
        audit = {
            "revision": REV,
            "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
            "package_name": META.get("package_name"),
            "archive_name": META.get("archive_name"),
            "promotion_allowed": False,
            "public_pretrained_trace_loaded": False,
            "gpu_fused_kernel_measured": False,
            **audit,
        }
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_GATE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace selector receipt replay gate — {REVUP}", "",
        f"Status: `{audit['status']}`  ", f"Verdict: `{audit.get('verdict')}`  ", "Promotion allowed: `false`", "",
        audit.get("summary", "Replay gate could not reach summary."), "", "## Files", "",
        f"- selector-entry receipt: `{audit.get('selector_entry_receipt_json') or 'missing'}`",
        f"- evaluation receipt: `{audit.get('evaluation_receipt_json') or 'missing'}`",
        f"- trace NPZ: `{audit.get('trace_npz') or 'missing'}`",
        f"- provenance JSON: `{audit.get('provenance_json') or 'missing'}`",
        "", "## Blockers", "",
    ]
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] if audit.get("blockers") else ["- none"])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in audit.get("errors", [])] if audit.get("errors") else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_GATE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "verdict": audit.get("verdict"), "errors": audit.get("errors", []), "blockers": audit.get("blockers", [])}, indent=2))
    return 0 if not audit.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())

# tampered after manifest
