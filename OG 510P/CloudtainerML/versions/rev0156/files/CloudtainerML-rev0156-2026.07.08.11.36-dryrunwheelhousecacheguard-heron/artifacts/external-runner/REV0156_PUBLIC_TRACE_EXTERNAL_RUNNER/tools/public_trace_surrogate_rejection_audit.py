#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "experiments" / "public_trace_gate_surrogate"))
try:
    from public_trace_gate_surrogate import validate_public_trace_provenance  # type: ignore
except Exception as exc:  # pragma: no cover
    validate_public_trace_provenance = None  # type: ignore[assignment]
    IMPORT_ERROR = repr(exc)
else:
    IMPORT_ERROR = None


def default_trace() -> Path:
    return ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz"


def default_prov() -> Path:
    return ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json"


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
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc)}


def evaluate(trace_npz: Path, provenance_json: Path, *, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    case_results: dict[str, Any] = {}

    if IMPORT_ERROR:
        errors.append("could not import public trace gate verifier: " + IMPORT_ERROR)
        status = "fail"
        verdict = "surrogate_rejection_unavailable"
    elif not trace_npz.exists() or not provenance_json.exists():
        blockers.append("real_public_trace_npz_or_provenance_missing")
        status = "pass_with_blockers"
        verdict = "surrogate_rejection_blocked_no_real_trace"
        if strict:
            errors.append("strict surrogate-rejection audit requested but trace/provenance is missing")
            status = "fail"
    else:
        assert validate_public_trace_provenance is not None
        baseline = validate_public_trace_provenance(provenance_json, trace_npz)
        case_results["baseline_status"] = baseline.get("status")
        case_results["baseline_accepted"] = bool(baseline.get("accepted"))
        if not baseline.get("accepted"):
            errors.append("baseline trace/provenance was not accepted before tamper-negative case: " + "; ".join(map(str, baseline.get("errors", []))))
        prov_data = load_json(provenance_json)
        if prov_data.get("_load_error"):
            errors.append("could not load provenance for tamper case: " + str(prov_data.get("_load_error")))
        else:
            with tempfile.TemporaryDirectory(prefix=f"{REVUP.lower()}_surrogate_reject_") as td:
                td_path = Path(td)
                tampered_prov = td_path / "tampered.provenance.json"
                # Two independent negative signals: the public claim flag is
                # false and the manifest no longer binds the supplied NPZ hash.
                prov_data["public_pretrained_trace"] = False
                prov_data["source_type"] = "surrogate_fixture"
                prov_data["trace_npz_sha256"] = "0" * 64
                tampered_prov.write_text(json.dumps(prov_data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
                rejected = validate_public_trace_provenance(tampered_prov, trace_npz)
                case_results["tampered_status"] = rejected.get("status")
                case_results["tampered_accepted"] = bool(rejected.get("accepted"))
                case_results["tampered_errors_sample"] = list(rejected.get("errors", []))[:8]
                if rejected.get("accepted"):
                    errors.append("tampered surrogate/nonpublic provenance was accepted")
        if errors:
            status = "fail"
            verdict = "surrogate_rejection_failed"
        else:
            status = "pass_with_blockers"
            verdict = "surrogate_rejection_negative_case_passed_not_promotion"
            blockers.append("named_hardware_timing_still_required_for_promotion")

    audit = {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": verdict == "surrogate_rejection_negative_case_passed_not_promotion",
        "gpu_fused_kernel_measured": False,
        "trace_npz": rel(trace_npz),
        "trace_npz_sha256": sha256_file(trace_npz),
        "provenance_json": rel(provenance_json),
        "provenance_json_sha256": sha256_file(provenance_json),
        "summary": "Negative-control audit for the live public trace lane. Once a real trace/provenance pair exists, the same verifier must accept the untouched pair but reject a tampered nonpublic/surrogate manifest, proving the lane does not silently promote diagnostic or fixture traces.",
        "case_results": case_results,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
    }
    return audit


def write_audit(audit: dict[str, Any]) -> None:
    (OUT / f"{REVUP}_PUBLIC_TRACE_SURROGATE_REJECTION_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace surrogate rejection audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        f"Verdict: `{audit.get('verdict')}`  ",
        "Promotion allowed: `false`",
        "",
        audit.get("summary", ""),
        "",
        "## Trace inputs",
        "",
        f"- trace NPZ: `{audit.get('trace_npz') or 'missing'}`",
        f"- provenance JSON: `{audit.get('provenance_json') or 'missing'}`",
        "",
        "## Blockers",
        "",
    ]
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] if audit.get("blockers") else ["- none"])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in audit.get("errors", [])] if audit.get("errors") else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_SURROGATE_REJECTION_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify that the public-trace gate rejects a tampered surrogate/nonpublic manifest for the current trace pair.")
    ap.add_argument("--trace-npz", type=Path, default=None)
    ap.add_argument("--provenance-json", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    audit = evaluate(args.trace_npz or default_trace(), args.provenance_json or default_prov(), strict=args.strict)
    write_audit(audit)
    print(json.dumps({"status": audit["status"], "verdict": audit.get("verdict"), "errors": audit.get("errors", []), "blockers": audit.get("blockers", [])}, indent=2))
    return 0 if not audit.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
