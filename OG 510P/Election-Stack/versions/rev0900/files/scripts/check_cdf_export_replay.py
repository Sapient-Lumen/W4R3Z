#!/usr/bin/env python3
"""Release-gated CDF export replay bridge for mission-kernel blocker MKB-003.

This check keeps the v895 forward motion concrete: the archive must ship a small
executable replay that recomputes result totals from exported CVR-like bytes and
fails on mismatched totals, unknown identifiers, and selection-limit violations.
It also prevents the fixture from being described as full NIST CDF conformance or
live jurisdictional evidence.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from jcs import dump_bytes  # noqa: E402
import cdf_export_replay as replay  # noqa: E402

VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
TOOL = ROOT / "tools" / "cdf_export_replay.py"
CDF_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
BD = CDF_DIR / "ballot-definition-minimal.json"
CVR = CDF_DIR / "cast-vote-records-minimal.json"
ERR = CDF_DIR / "election-results-minimal.json"
REPORT = ROOT / "artifacts" / "reports" / f"cdf-export-replay-report-rev{REV}.json"
CRO = CDF_DIR / "canonical-results-object-from-cdf.json"
MANIFEST = CDF_DIR / "cdf-mapping-manifest.json"
PUBLIC = CDF_DIR / "public-cdf-export-replay.md"
CRO_SCHEMA = ROOT / "schemas" / "CanonicalResultsObject.json"
MANIFEST_SCHEMA = ROOT / "schemas" / "CDFMappingManifest.json"
VECTORS = ROOT / "artifacts" / "test-vectors" / "cdf-replay"
REQUIRED = [TOOL, BD, CVR, ERR, REPORT, CRO, MANIFEST, PUBLIC, CRO_SCHEMA, MANIFEST_SCHEMA]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_sha256(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(dump_bytes(obj)).hexdigest()


def run_tool(*, bd: Path = BD, cvr: Path = CVR, err: Path = ERR) -> tuple[int, dict[str, Any], str]:
    """Run the replay logic in-process for release-gate speed.

    The release gate already isolates this checker in its own subprocess. Older
    revisions spawned five additional Python interpreters from inside the child
    check to exercise the positive path and negative controls. That made the
    one-command gate fragile in the cloudtainer without adding meaningful
    isolation. Directly invoking the stdlib replay function keeps the same
    failure semantics while removing redundant interpreter startup.
    """

    obj = replay.build_report(bd, cvr, err)
    code = 0 if obj.get("decision") == "SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE" else 2
    return code, obj, ""


def stripped_report(obj: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in obj.items() if k not in {"canonical_results_object", "cdf_mapping_manifest"}}


def require_negative(label: str, *, bd: Path = BD, cvr: Path = CVR, err: Path = ERR, want_decision: str, want_problem_prefix: str, errors: list[str]) -> None:
    try:
        code, obj, stderr = run_tool(bd=bd, cvr=cvr, err=err)
    except Exception as exc:
        errors.append(f"{label}: tool invocation failed: {exc}")
        return
    if code == 0:
        errors.append(f"{label}: negative control exited 0")
    if obj.get("decision") != want_decision:
        errors.append(f"{label}: decision {obj.get('decision')!r} != {want_decision!r}")
    problems = [str(e) for e in obj.get("errors") or []]
    if not any(p.startswith(want_problem_prefix) for p in problems):
        errors.append(f"{label}: missing problem prefix {want_problem_prefix!r}; got {problems!r}; stderr={stderr!r}")


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2

    try:
        code, generated, stderr = run_tool()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    if code != 0:
        errors.append(f"default CDF replay failed rc={code}: {stderr}")

    shipped_report = load_json(REPORT)
    shipped_cro = load_json(CRO)
    shipped_manifest = load_json(MANIFEST)
    if shipped_report != stripped_report(generated):
        errors.append("cdf-export-replay report is stale; run tools/cdf_export_replay.py --write")
    if shipped_cro != generated.get("canonical_results_object"):
        errors.append("canonical-results-object-from-cdf.json is stale")
    if shipped_manifest != generated.get("cdf_mapping_manifest"):
        errors.append("cdf-mapping-manifest.json is stale")

    if shipped_report.get("archive_version") != VERSION:
        errors.append("CDF replay report archive_version mismatch")
    if shipped_report.get("decision") != "SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE":
        errors.append("CDF replay must pass only as synthetic non-conformance replay")
    if shipped_report.get("synthetic_only") is not True or shipped_report.get("no_live_deployment_claim") is not True:
        errors.append("CDF replay report missing synthetic/no-live flags")
    if shipped_report.get("no_full_nist_conformance_claim") is not True:
        errors.append("CDF replay report must explicitly deny full NIST conformance claim")
    counts = shipped_report.get("counts") or {}
    if (
        counts.get("contest_count") != 2
        or counts.get("option_count") != 6
        or counts.get("cvr_record_count") != 6
        or counts.get("reporting_unit_count") != 2
        or counts.get("comparison_row_count") != 12
    ):
        errors.append(f"unexpected CDF replay fixture counts: {counts!r}")
    if counts.get("error_count") != 0 or counts.get("matched_comparison_row_count") != counts.get("comparison_row_count"):
        errors.append("default CDF replay must have zero errors and all rows matched")
    if shipped_report.get("canonical_results_object_sha256") != canonical_json_sha256(shipped_cro):
        errors.append("CRO canonical sha256 in report does not match shipped CRO object")
    if shipped_report.get("mapping_manifest_sha256") != canonical_json_sha256(shipped_manifest):
        errors.append("mapping manifest canonical sha256 in report does not match shipped manifest object")
    if shipped_report.get("cro_hash") != shipped_cro.get("cro_hash"):
        errors.append("report cro_hash does not match shipped CRO")

    # Optional schema validation in richer environments; parse-only remains stdlib friendly.
    try:
        import jsonschema  # type: ignore
        from jsonschema import FormatChecker  # type: ignore
        jsonschema.Draft202012Validator(load_json(CRO_SCHEMA), format_checker=FormatChecker()).validate(shipped_cro)
        jsonschema.Draft202012Validator(load_json(MANIFEST_SCHEMA), format_checker=FormatChecker()).validate(shipped_manifest)
    except ImportError:
        pass
    except Exception as exc:
        errors.append(f"CDF replay outputs fail schema validation: {exc}")

    public = PUBLIC.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in ["not live election evidence", "not a full nist cdf conformance result", "does not prove a real election outcome", "does not authorize live pilot", "not the nist cdf test method", "by reporting unit"]:
        if phrase not in public:
            errors.append(f"public CDF replay summary missing boundary phrase {phrase!r}")
    prohibited = ["full nist conformance pass", "live jurisdiction export evidence", "certifies", "proves the outcome"]
    for phrase in prohibited:
        if phrase in public:
            errors.append(f"public CDF replay summary contains prohibited overclaim {phrase!r}")

    require_negative(
        "total-mismatch",
        err=VECTORS / "election-results-total-mismatch.json",
        want_decision="FAIL_TOTAL_MISMATCH",
        want_problem_prefix="ERR_TOTAL_MISMATCH:",
        errors=errors,
    )
    require_negative(
        "unit-swap-total-preserving",
        err=VECTORS / "election-results-unit-swap-total-preserving.json",
        want_decision="FAIL_TOTAL_MISMATCH",
        want_problem_prefix="ERR_TOTAL_MISMATCH:P-",
        errors=errors,
    )
    require_negative(
        "unknown-option",
        cvr=VECTORS / "cast-vote-records-unknown-option.json",
        want_decision="FAIL_IDENTIFIER_OR_SELECTION_RULE",
        want_problem_prefix="CVR_UNKNOWN_OPTION:",
        errors=errors,
    )
    require_negative(
        "overvote",
        cvr=VECTORS / "cast-vote-records-overvote.json",
        want_decision="FAIL_IDENTIFIER_OR_SELECTION_RULE",
        want_problem_prefix="CVR_SELECTION_LIMIT_EXCEEDED:",
        errors=errors,
    )

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2
    print(f"PASS: CDF export replay bridge ({VERSION}, rows={counts.get('comparison_row_count')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
