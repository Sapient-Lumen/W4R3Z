#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value) if value else default


def defaults() -> dict[str, Path]:
    return {
        "trace_npz": _env_path("OUT_NPZ", ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz"),
        "provenance_json": _env_path("OUT_PROV", ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json"),
        "gate_json": _env_path("OUT_GATE", ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json"),
        "evaluation_receipt": _env_path("OUT_RECEIPT", ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT.json"),
        "selector_receipt": _env_path("OUT_SELECTOR", ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT.json"),
        "handoff_dir": _env_path("OUT_HANDOFF_DIR", ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_TRACE_HANDOFF"),
        "handoff_zip": _env_path("OUT_HANDOFF_ZIP", ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_TRACE_HANDOFF.zip"),
    }


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_missing": True}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc)}


def zip_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    out: dict[str, Any] = {"exists": True, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            out["valid_zip"] = bad is None
            out["bad_member"] = bad
            out["member_count"] = len(zf.infolist())
    except Exception as exc:
        out["valid_zip"] = False
        out["error"] = repr(exc)
    return out


def evaluate(paths: dict[str, Path], *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []

    trace_sha = sha256_file(paths["trace_npz"])
    prov_sha = sha256_file(paths["provenance_json"])
    gate = load_json(paths["gate_json"])
    receipt = load_json(paths["evaluation_receipt"])
    selector = load_json(paths["selector_receipt"])
    handoff_manifest = load_json(paths["handoff_dir"] / "PUBLIC_TRACE_HANDOFF_MANIFEST.json")
    handoff_zip_status = zip_status(paths["handoff_zip"])

    missing = [name for name in ["trace_npz", "provenance_json", "gate_json", "evaluation_receipt", "selector_receipt"] if not paths[name].exists()]
    if not paths["handoff_dir"].is_dir():
        missing.append("handoff_dir")
    if not paths["handoff_zip"].is_file():
        missing.append("handoff_zip")
    if missing:
        blockers.append("live_trace_lane_outputs_missing:" + ",".join(missing))

    if gate.get("_load_error"):
        errors.append("gate json malformed: " + str(gate.get("_load_error")))
    elif gate and not gate.get("_missing"):
        if gate.get("public_pretrained_trace_loaded") is not True:
            errors.append("gate did not load accepted public pretrained trace")
        if gate.get("trace_gate_status") != "external_public_pretrained_npz_loaded_provenance_manifest_accepted":
            errors.append("gate trace status is not accepted public-pretrained")

    if receipt.get("_load_error"):
        errors.append("evaluation receipt malformed: " + str(receipt.get("_load_error")))
    elif receipt and not receipt.get("_missing"):
        if receipt.get("receipt_contract") != "public_trace_evaluation_receipt_v2":
            errors.append("evaluation receipt contract mismatch")
        if receipt.get("accepted_for_selector_evaluation") is not True:
            errors.append("evaluation receipt does not open selector evaluation")
        if receipt.get("trace_npz_sha256") != trace_sha:
            errors.append("evaluation receipt trace hash mismatch")
        if receipt.get("provenance_json_sha256") != prov_sha:
            errors.append("evaluation receipt provenance hash mismatch")
        if receipt.get("promotion_allowed") is not False:
            errors.append("evaluation receipt overclaims promotion")

    if selector.get("_load_error"):
        errors.append("selector receipt malformed: " + str(selector.get("_load_error")))
    elif selector and not selector.get("_missing"):
        if selector.get("selector_entry_receipt_contract") != "public_trace_selector_entry_receipt_v1":
            errors.append("selector receipt contract mismatch")
        if selector.get("selector_entry_allowed") is not True:
            errors.append("selector receipt does not open selector entry")
        if selector.get("promotion_allowed") is not False:
            errors.append("selector receipt overclaims promotion")

    if handoff_manifest.get("_load_error"):
        errors.append("handoff manifest malformed: " + str(handoff_manifest.get("_load_error")))
    elif handoff_manifest and not handoff_manifest.get("_missing"):
        if handoff_manifest.get("handoff_contract") != "public_trace_handoff_archive_v1":
            errors.append("handoff manifest contract mismatch")
        if handoff_manifest.get("promotion_allowed") is not False:
            errors.append("handoff manifest overclaims promotion")
        names = {str(s.get("name")) for s in handoff_manifest.get("subjects", []) if isinstance(s, dict)}
        for required in ["public_trace_npz", "public_trace_provenance_json", "public_trace_evaluation_receipt", "public_trace_selector_entry_receipt"]:
            if required not in names:
                errors.append("handoff manifest missing subject: " + required)

    if handoff_zip_status.get("exists") and not handoff_zip_status.get("valid_zip"):
        errors.append("handoff zip is not a valid zip archive")

    all_outputs_present = not missing
    accepted_chain = bool(
        all_outputs_present
        and not errors
        and gate.get("public_pretrained_trace_loaded") is True
        and receipt.get("accepted_for_selector_evaluation") is True
        and selector.get("selector_entry_allowed") is True
        and handoff_manifest.get("handoff_contract") == "public_trace_handoff_archive_v1"
        and handoff_zip_status.get("valid_zip") is True
    )

    if accepted_chain:
        status = "pass_with_blockers"
        verdict = "real_trace_lane_packaged_not_promotion"
        blockers.append("named_hardware_timing_still_required_for_promotion")
    else:
        status = "pass_with_blockers" if not errors else "fail"
        verdict = "real_trace_lane_incomplete"
        if not blockers:
            blockers.append("real_trace_lane_not_fully_packaged")

    if strict and not accepted_chain:
        status = "fail"
        errors.append("strict current trace lane audit requested but accepted trace/receipt/handoff chain is incomplete")

    return {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": accepted_chain,
        "gpu_fused_kernel_measured": False,
        "named_hardware_timing_measured": False,
        "summary": "End-of-lane audit for the live public trace command. It verifies that capture, provenance, gate output, evaluation receipt, selector-entry receipt, and portable handoff archive exist as one digest-consistent chain. Passing this audit is still non-promotional until named-hardware timing exists.",
        "paths": {name: rel(path) for name, path in paths.items()},
        "trace_npz_sha256": trace_sha,
        "provenance_json_sha256": prov_sha,
        "gate_status": gate.get("trace_gate_status"),
        "evaluation_receipt_accepted": receipt.get("accepted_for_selector_evaluation"),
        "selector_entry_allowed": selector.get("selector_entry_allowed"),
        "handoff_manifest_contract": handoff_manifest.get("handoff_contract"),
        "handoff_zip_status": handoff_zip_status,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
    }


def write_audit(audit: dict[str, Any]) -> None:
    (OUT / f"{REVUP}_PUBLIC_TRACE_CURRENT_TRACE_LANE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace current trace lane audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        f"Verdict: `{audit.get('verdict')}`  ",
        "Promotion allowed: `false`",
        "",
        audit.get("summary", ""),
        "",
        "## Outputs",
        "",
    ]
    for name, path in audit.get("paths", {}).items():
        md.append(f"- {name}: `{path}`")
    md.extend(["", "## Blockers", ""])
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] if audit.get("blockers") else ["- none"])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in audit.get("errors", [])] if audit.get("errors") else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_CURRENT_TRACE_LANE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify the whole live public trace lane after capture, receipt, replay, and handoff packaging.")
    ap.add_argument("--trace-npz", type=Path, default=None)
    ap.add_argument("--provenance-json", type=Path, default=None)
    ap.add_argument("--gate-json", type=Path, default=None)
    ap.add_argument("--evaluation-receipt-json", type=Path, default=None)
    ap.add_argument("--selector-entry-receipt-json", type=Path, default=None)
    ap.add_argument("--handoff-dir", type=Path, default=None)
    ap.add_argument("--handoff-zip", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    paths = defaults()
    overrides = {
        "trace_npz": args.trace_npz,
        "provenance_json": args.provenance_json,
        "gate_json": args.gate_json,
        "evaluation_receipt": args.evaluation_receipt_json,
        "selector_receipt": args.selector_entry_receipt_json,
        "handoff_dir": args.handoff_dir,
        "handoff_zip": args.handoff_zip,
    }
    for key, value in overrides.items():
        if value is not None:
            paths[key] = value
    audit = evaluate(paths, strict=args.strict)
    write_audit(audit)
    print(json.dumps({"status": audit["status"], "verdict": audit.get("verdict"), "errors": audit.get("errors", []), "blockers": audit.get("blockers", [])}, indent=2))
    return 0 if not audit.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
