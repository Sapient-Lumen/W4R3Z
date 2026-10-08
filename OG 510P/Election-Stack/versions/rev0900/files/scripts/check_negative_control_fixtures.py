#!/usr/bin/env python3
"""Validate synthetic Example County negative-control verifier fixtures.

The happy-path scorecard should not be the only verifier rehearsal. This gate
ensures expected-failure fixtures are cataloged, generated outputs are current,
and every temporary mutation is rejected with the expected public problem code.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REG = ROOT / "artifacts" / "registries" / "negative-control-fixtures.csv"
OUTDIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
PROBLEM_CODES = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"
REQUIRED_HEADER = [
    "fixture_id",
    "track",
    "source_packet",
    "mutation",
    "expected_status",
    "expected_problem_codes",
    "runner",
    "generated_output_refs",
    "public_interpretation",
    "non_claims",
]
REQUIRED_IDS = {f"ECF-{i:03d}" for i in range(1, 9)}
ALLOWED_MUTATIONS = {
    "append_payload_object",
    "tamper_payload_pointer_digest",
    "tamper_payload_digest",
    "tamper_tbs_digest",
    "tamper_manifest_digest",
    "remove_manifest",
    "unsupported_envelope_version",
    "missing_payload_object",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def split_cell(cell: str) -> list[str]:
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def known_problem_codes() -> set[str]:
    if not PROBLEM_CODES.exists():
        return set()
    return {r.get("code", "") for r in read_csv(PROBLEM_CODES) if r.get("code")}


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print("ERROR: missing artifacts/registries/negative-control-fixtures.csv", file=sys.stderr)
        return 2
    with REG.open("r", encoding="utf-8", newline="") as f:
        raw = list(csv.reader(f))
    if not raw:
        print("ERROR: negative-control-fixtures.csv is empty", file=sys.stderr)
        return 2
    header = [h.strip() for h in raw[0]]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header!r} want {REQUIRED_HEADER!r}")

    rows = read_csv(REG)
    known = known_problem_codes()
    seen: set[str] = set()
    for idx, row in enumerate(rows, start=2):
        fid = row.get("fixture_id", "")
        if not re.fullmatch(r"ECF-\d{3}", fid):
            errors.append(f"L{idx}: invalid fixture_id {fid!r}")
            continue
        if fid in seen:
            errors.append(f"L{idx}: duplicate fixture_id {fid}")
        seen.add(fid)
        if row.get("track") != "A":
            errors.append(f"L{idx}: {fid} must be Track A")
        if row.get("mutation") not in ALLOWED_MUTATIONS:
            errors.append(f"L{idx}: {fid} unknown mutation {row.get('mutation')!r}")
        if row.get("expected_status") != "FAIL":
            errors.append(f"L{idx}: {fid} expected_status must be FAIL")
        source = row.get("source_packet", "")
        if not source.startswith("artifacts/examples/") or not (ROOT / source).exists():
            errors.append(f"L{idx}: {fid} missing source packet {source!r}")
        runner = row.get("runner", "")
        if runner != "tools/example_county_negative_control_runner.py" or not (ROOT / runner).exists():
            errors.append(f"L{idx}: {fid} runner mismatch or missing: {runner!r}")
        codes = split_cell(row.get("expected_problem_codes", ""))
        if not codes:
            errors.append(f"L{idx}: {fid} missing expected_problem_codes")
        for code in codes:
            if code not in known:
                errors.append(f"L{idx}: {fid} unknown expected problem code {code!r}")
        for ref in split_cell(row.get("generated_output_refs", "")):
            if not ref.startswith("artifacts/examples/example_county_2026_municipal_pilot/"):
                errors.append(f"L{idx}: {fid} generated output ref outside Example County output dir: {ref!r}")
            elif not (ROOT / ref).exists():
                errors.append(f"L{idx}: {fid} missing generated output ref: {ref}")
        if "not live election evidence" not in row.get("non_claims", "").lower() and "not live deployment evidence" not in row.get("non_claims", "").lower():
            errors.append(f"L{idx}: {fid} non_claims must include live-evidence boundary")
        if "intent" not in row.get("non_claims", "").lower() and "certification" not in row.get("non_claims", "").lower() and "outcome" not in row.get("non_claims", "").lower():
            errors.append(f"L{idx}: {fid} non_claims should block at least one common overclaim")

    missing = sorted(REQUIRED_IDS - seen)
    if missing:
        errors.append("missing required fixture ids: " + ", ".join(missing))

    report_path = OUTDIR / "negative-control-report.json"
    csv_path = OUTDIR / "negative-control-results.csv"
    md_path = OUTDIR / "public-negative-control-summary.md"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        report = {}
        errors.append(f"negative-control-report.json parse failed: {exc}")
    if report:
        if report.get("archive_version") != VERSION:
            errors.append(f"negative-control-report.json archive_version drift: {report.get('archive_version')!r} vs {VERSION!r}")
        if report.get("synthetic_only") is not True:
            errors.append("negative-control-report.json missing synthetic_only=true")
        if report.get("no_live_deployment_claim") is not True:
            errors.append("negative-control-report.json missing no_live_deployment_claim=true")
        if report.get("status") != "PASS":
            errors.append("negative-control-report.json status must be PASS")
        results = report.get("results")
        if not isinstance(results, list) or len(results) != len(rows):
            errors.append("negative-control-report.json result count mismatch")
            results = []
        by_id = {r.get("fixture_id"): r for r in results if isinstance(r, dict)}
        for row in rows:
            fid = row.get("fixture_id")
            res = by_id.get(fid)
            if not res:
                errors.append(f"negative-control-report.json missing fixture result {fid}")
                continue
            if res.get("expectation_status") != "PASS":
                errors.append(f"{fid} expectation_status must be PASS")
            if res.get("observed_status") != row.get("expected_status"):
                errors.append(f"{fid} observed_status {res.get('observed_status')!r} != expected {row.get('expected_status')!r}")
            observed = set(str(x) for x in (res.get("observed_problem_codes") or []))
            for code in split_cell(row.get("expected_problem_codes", "")):
                if code not in observed:
                    errors.append(f"{fid} missing expected observed code {code}")
            if res.get("missing_expected_codes"):
                errors.append(f"{fid} records missing expected codes: {res.get('missing_expected_codes')!r}")

    try:
        result_rows = read_csv(csv_path)
    except Exception as exc:
        result_rows = []
        errors.append(f"negative-control-results.csv read failed: {exc}")
    if len(result_rows) != len(rows):
        errors.append("negative-control-results.csv row count mismatch")
    if result_rows and not all(r.get("expectation_status") == "PASS" and r.get("non_claims") for r in result_rows):
        errors.append("negative-control-results.csv rows must PASS and carry non_claims")

    try:
        head = "\n".join(md_path.read_text(encoding="utf-8", errors="replace").splitlines()[:10]).lower()
        full = md_path.read_text(encoding="utf-8", errors="replace").lower()
    except Exception as exc:
        head = full = ""
        errors.append(f"public-negative-control-summary.md read failed: {exc}")
    for phrase in ["synthetic example only", "not live election evidence"]:
        if phrase not in head:
            errors.append(f"public-negative-control-summary.md missing early boundary phrase {phrase!r}")
    for phrase in ["expected-failure", "does not certify", "does not prove intent or fraud"]:
        if phrase not in full:
            errors.append(f"public-negative-control-summary.md missing phrase {phrase!r}")
    if "certifies" in full or "proves fraud" in full:
        errors.append("public-negative-control-summary.md contains prohibited overclaim language")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(f"PASS: negative-control fixtures ({len(rows)} fixture(s), {VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
