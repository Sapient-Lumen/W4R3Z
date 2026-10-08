#!/usr/bin/env python3
"""Release-gate the independent synthetic CDF replay verifier.

v895 closed the first CDF replay gap with a primary adapter.  The next risk is
single-implementation self-confirmation: K03 asks for an independent verifier
transcript.  This check requires a second parser/tally path that does not import
or execute the primary adapter, agrees with the shipped primary report/CRO, and
fails closed on bad exports or deliberate primary-output disagreement.
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cdf_replay_independent_verifier as independent_replay  # noqa: E402
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
TOOL = ROOT / "tools" / "cdf_replay_independent_verifier.py"
PRIMARY_TOOL = ROOT / "tools" / "cdf_export_replay.py"
CDF_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
BD = CDF_DIR / "ballot-definition-minimal.json"
CVR = CDF_DIR / "cast-vote-records-minimal.json"
ERR = CDF_DIR / "election-results-minimal.json"
PRIMARY_REPORT = ROOT / "artifacts" / "reports" / f"cdf-export-replay-report-rev{REV}.json"
CRO = CDF_DIR / "canonical-results-object-from-cdf.json"
REPORT = ROOT / "artifacts" / "reports" / f"cdf-independent-replay-verifier-rev{REV}.json"
PUBLIC = CDF_DIR / "public-cdf-independent-verifier.md"
VECTORS = ROOT / "artifacts" / "test-vectors" / "cdf-replay"
REQUIRED = [TOOL, PRIMARY_TOOL, BD, CVR, ERR, PRIMARY_REPORT, CRO, REPORT, PUBLIC]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_tool(*, bd: Path = BD, cvr: Path = CVR, err: Path = ERR, primary_report: Path = PRIMARY_REPORT, cro: Path = CRO) -> tuple[int, dict[str, Any], str]:
    """Run the independent verifier in-process inside this release-gate child.

    This checker still audits the verifier source to ensure it does not import
    or execute the primary adapter. Avoiding nested subprocesses materially
    reduces full-gate runtime while preserving the independence property being
    tested.
    """

    obj = independent_replay.build_report(bd, cvr, err, primary_report, cro)
    code = 0 if obj.get("decision") == "INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE" else 2
    return code, obj, ""


def ensure_independent_source(errors: list[str]) -> None:
    text = TOOL.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(TOOL))
    forbidden = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "cdf_export_replay":
                    forbidden.append("import cdf_export_replay")
        elif isinstance(node, ast.ImportFrom):
            if node.module == "cdf_export_replay":
                forbidden.append("from cdf_export_replay import ...")
    for literal in ["cdf_export_replay.py", "tools/cdf_export_replay.py"]:
        if literal in text:
            forbidden.append(f"literal reference {literal!r}")
    if "subprocess" in text:
        errors.append("independent verifier must not use subprocess")
    if forbidden:
        errors.append("independent verifier is coupled to the primary adapter: " + ", ".join(sorted(set(forbidden))))


def require_problem(label: str, *, want_prefix: str, want_code_nonzero: bool = True, **paths: Path) -> None:
    code, obj, stderr = run_tool(**paths)
    local_errors = globals().setdefault("_NEGATIVE_ERRORS", [])
    if want_code_nonzero and code == 0:
        local_errors.append(f"{label}: expected nonzero exit")
    if obj.get("decision") != "FAIL_INDEPENDENT_CDF_REPLAY_DISAGREEMENT":
        local_errors.append(f"{label}: unexpected decision {obj.get('decision')!r}; stderr={stderr!r}")
    problems = [str(x) for x in obj.get("errors") or []]
    if not any(p.startswith(want_prefix) for p in problems):
        local_errors.append(f"{label}: missing problem prefix {want_prefix!r}; got {problems!r}")


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2

    ensure_independent_source(errors)

    try:
        code, generated, stderr = run_tool()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2
    if code != 0:
        errors.append(f"independent verifier failed on default fixture rc={code}: {stderr}")

    shipped = load_json(REPORT)
    if shipped != generated:
        errors.append("cdf-independent-replay-verifier report is stale; run tools/cdf_replay_independent_verifier.py --write")
    if shipped.get("archive_version") != VERSION:
        errors.append("independent verifier archive_version mismatch")
    if shipped.get("decision") != "INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE":
        errors.append("independent verifier must agree only as synthetic non-conformance replay")
    if shipped.get("synthetic_only") is not True or shipped.get("no_live_deployment_claim") is not True:
        errors.append("independent verifier missing synthetic/no-live flags")
    if shipped.get("no_full_nist_conformance_claim") is not True:
        errors.append("independent verifier must explicitly deny full NIST conformance claim")
    counts = shipped.get("counts") or {}
    if (
        counts.get("contest_count") != 2
        or counts.get("option_count") != 6
        or counts.get("cvr_record_count") != 6
        or counts.get("reporting_unit_count") != 2
        or counts.get("comparison_row_count") != 12
    ):
        errors.append(f"unexpected independent verifier fixture counts: {counts!r}")
    if counts.get("error_count") != 0 or counts.get("matched_comparison_row_count") != counts.get("comparison_row_count"):
        errors.append("independent verifier default fixture must have zero errors and all rows matched")
    if shipped.get("primary_cro_hash") != shipped.get("cro_hash"):
        errors.append("independent verifier primary cro hash does not match CRO file hash field")
    if shipped.get("comparison_rows") != load_json(PRIMARY_REPORT).get("comparison_rows"):
        errors.append("independent verifier rows do not match primary report rows")

    public = PUBLIC.read_text(encoding="utf-8", errors="replace").lower()
    for phrase in [
        "not live election evidence",
        "not a full nist cdf conformance result",
        "without importing or executing the primary replay adapter",
        "not the nist cdf test method",
        "not certification",
        "not outcome proof",
        "by reporting unit",
    ]:
        if phrase not in public:
            errors.append(f"public independent verifier summary missing boundary phrase {phrase!r}")
    for phrase in ["full nist conformance pass", "is live jurisdiction export evidence", "certifies", "proves the outcome"]:
        if phrase in public:
            errors.append(f"public independent verifier summary contains prohibited overclaim {phrase!r}")

    globals()["_NEGATIVE_ERRORS"] = []
    require_problem("total-mismatch", err=VECTORS / "election-results-total-mismatch.json", want_prefix="ERR_TOTAL_MISMATCH:")
    require_problem("unit-swap-total-preserving", err=VECTORS / "election-results-unit-swap-total-preserving.json", want_prefix="ERR_TOTAL_MISMATCH:P-")
    require_problem("unknown-option", cvr=VECTORS / "cast-vote-records-unknown-option.json", want_prefix="CVR_UNKNOWN_OPTION:")
    require_problem("overvote", cvr=VECTORS / "cast-vote-records-overvote.json", want_prefix="CVR_SELECTION_LIMIT_EXCEEDED:")
    errors.extend(globals().get("_NEGATIVE_ERRORS", []))

    with tempfile.TemporaryDirectory(prefix="tes_cdf_independent_negative_") as td:
        tmp = Path(td)
        primary_bad = tmp / "primary-bad.json"
        primary = load_json(PRIMARY_REPORT)
        primary["comparison_rows"][0]["err_votes"] += 1
        primary_bad.write_text(json.dumps(primary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        code, obj, _stderr = run_tool(primary_report=primary_bad)
        if code == 0 or "PRIMARY_REPLAY_COMPARISON_ROWS_DISAGREE" not in (obj.get("errors") or []):
            errors.append("independent verifier must fail on altered primary comparison rows")

        cro_bad = tmp / "cro-bad.json"
        cro = load_json(CRO)
        cro["results"]["contests"][0]["reporting_units"][0]["options"][0]["votes"] += 1
        cro_bad.write_text(json.dumps(cro, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        code, obj, _stderr = run_tool(cro=cro_bad)
        if code == 0 or "PRIMARY_CRO_VOTE_ROWS_DISAGREE" not in (obj.get("errors") or []):
            errors.append("independent verifier must fail on altered CRO vote rows")

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 2
    print(f"PASS: independent CDF replay verifier ({VERSION}, rows={counts.get('comparison_row_count')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
