#!/usr/bin/env python3
"""Synthetic ballot-accounting reconciliation for the Example County CDF fixture.

The v895/v896 CDF lane proved that exported CVR totals could be replayed and
checked by a second implementation.  That is still not enough for the election
mission: result totals must be reconciled against ballot accounting and reporting
unit completeness before anyone treats the closeout as operational evidence.

This tool checks a deliberately small, deterministic projection:
- ballot definition reporting units, ballot styles, contests, and limits;
- CVR record counts and selections by reporting unit/contest;
- a synthetic ballot-accounting ledger with expected CVR counts, eligible ballot
  counts, selection slots, undervote slots, and overvote-record counts.

It is not a live custody record, not full NIST CDF conformance, not a voting
system test, and not outcome proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
CDF_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
DEFAULT_BD = CDF_DIR / "ballot-definition-minimal.json"
DEFAULT_CVR = CDF_DIR / "cast-vote-records-minimal.json"
DEFAULT_ACCOUNTING = CDF_DIR / "ballot-accounting-minimal.json"
REPORT = ROOT / "artifacts" / "reports" / f"ballot-accounting-reconciliation-rev{REV}.json"
PUBLIC = CDF_DIR / "public-ballot-accounting-reconciliation.md"
SCHEMA_FAMILY = "TES-CDF-MINIMAL-PROJECTION-v1"
ACCOUNTING_FAMILY = "TES-BALLOT-ACCOUNTING-MINIMAL-v1"
BOUNDARY = (
    "Synthetic ballot-accounting reconciliation only; not live custody evidence, "
    "not a full NIST CDF conformance result, not the NIST CDF Test Method, not certification, "
    "not outcome proof, not current voter instruction, and not legal advice."
)
PASS_DECISION = "SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE"
FAIL_DECISION = "FAIL_BALLOT_ACCOUNTING_RECONCILIATION"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def digest_json(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(dump_bytes(obj)).hexdigest()


def sid(value: Any) -> str:
    return str(value or "").strip()


def list_field(obj: dict[str, Any], field: str, errors: list[str], code: str) -> list[Any]:
    value = obj.get(field)
    if not isinstance(value, list):
        errors.append(f"{code}_{field.upper()}_NOT_ARRAY")
        return []
    return value


def duplicate_ids(values: list[str]) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if not value:
            continue
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)


def index_bd(bd: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    if bd.get("schema_family") != SCHEMA_FAMILY:
        errors.append("BD_SCHEMA_FAMILY_UNSUPPORTED")
    gp_units: dict[str, dict[str, Any]] = {}
    for row in list_field(bd, "gp_units", errors, "BD"):
        if not isinstance(row, dict):
            errors.append("BD_GP_UNIT_NOT_OBJECT")
            continue
        gid = sid(row.get("id"))
        if not gid:
            errors.append("BD_GP_UNIT_MISSING_ID")
            continue
        gp_units[gid] = row
    styles: dict[str, dict[str, Any]] = {}
    for row in list_field(bd, "ballot_styles", errors, "BD"):
        if not isinstance(row, dict):
            errors.append("BD_BALLOT_STYLE_NOT_OBJECT")
            continue
        style_id = sid(row.get("id"))
        if not style_id:
            errors.append("BD_BALLOT_STYLE_MISSING_ID")
            continue
        styles[style_id] = row
    contests_raw: list[dict[str, Any]] = []
    for row in list_field(bd, "contests", errors, "BD"):
        if not isinstance(row, dict):
            errors.append("BD_CONTEST_NOT_OBJECT")
            continue
        contests_raw.append(row)
    for label, values in [
        ("BD_DUPLICATE_GP_UNIT", list(gp_units)),
        ("BD_DUPLICATE_BALLOT_STYLE", list(styles)),
        ("BD_DUPLICATE_CONTEST", [sid(c.get("id")) for c in contests_raw]),
    ]:
        for dup in duplicate_ids(values):
            errors.append(f"{label}:{dup}")
    contests: dict[str, dict[str, Any]] = {}
    contest_limits: dict[str, int] = {}
    contest_options: dict[str, set[str]] = {}
    for contest in contests_raw:
        cid = sid(contest.get("id"))
        if not cid:
            errors.append("BD_CONTEST_MISSING_ID")
            continue
        contests[cid] = contest
        try:
            limit = int(contest.get("selection_limit"))
        except Exception:
            limit = 0
        if limit <= 0:
            errors.append(f"BD_INVALID_SELECTION_LIMIT:{cid}")
        contest_limits[cid] = limit
        options: list[str] = []
        for opt in contest.get("options") or []:
            if not isinstance(opt, dict):
                errors.append(f"BD_OPTION_NOT_OBJECT:{cid}")
                continue
            oid = sid(opt.get("id"))
            if not oid:
                errors.append(f"BD_OPTION_MISSING_ID:{cid}")
                continue
            options.append(oid)
        for dup in duplicate_ids(options):
            errors.append(f"BD_DUPLICATE_OPTION:{cid}:{dup}")
        contest_options[cid] = set(options)
    for style_id, style in styles.items():
        for unit_id in style.get("gp_unit_ids") or []:
            if sid(unit_id) not in gp_units:
                errors.append(f"BD_BALLOT_STYLE_UNKNOWN_GP_UNIT:{style_id}:{unit_id}")
        for contest_id in style.get("contest_ids") or []:
            if sid(contest_id) not in contests:
                errors.append(f"BD_BALLOT_STYLE_UNKNOWN_CONTEST:{style_id}:{contest_id}")
    return {"gp_units": gp_units, "styles": styles, "contests": contests, "contest_limits": contest_limits, "contest_options": contest_options}


def compute_cvr_accounting(cvr: dict[str, Any], idx: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    if cvr.get("schema_family") != SCHEMA_FAMILY:
        errors.append("CVR_SCHEMA_FAMILY_UNSUPPORTED")
    records: list[dict[str, Any]] = []
    for row in list_field(cvr, "records", errors, "CVR"):
        if not isinstance(row, dict):
            errors.append("CVR_RECORD_NOT_OBJECT")
            continue
        records.append(row)
    for dup in duplicate_ids([sid(r.get("id")) for r in records]):
        errors.append(f"CVR_DUPLICATE_RECORD:{dup}")

    units: dict[str, dict[str, Any]] = defaultdict(lambda: {"cvr_record_count": 0, "contest_records": defaultdict(list)})  # type: ignore[assignment]
    for record in records:
        rid = sid(record.get("id")) or "<missing-record-id>"
        unit_id = sid(record.get("reporting_unit_id"))
        style_id = sid(record.get("ballot_style_id"))
        if not unit_id:
            errors.append(f"CVR_MISSING_REPORTING_UNIT:{rid}")
            continue
        if unit_id not in idx["gp_units"]:
            errors.append(f"CVR_UNKNOWN_REPORTING_UNIT:{rid}:{unit_id}")
        units[unit_id]["cvr_record_count"] += 1
        style = idx["styles"].get(style_id)
        if style is None:
            errors.append(f"CVR_UNKNOWN_BALLOT_STYLE:{rid}:{style_id}")
            allowed_contests: set[str] = set()
        else:
            allowed_contests = {sid(x) for x in style.get("contest_ids") or [] if sid(x)}
        seen_vote_rows: dict[str, dict[str, Any]] = {}
        for contest_vote in record.get("contests") or []:
            if not isinstance(contest_vote, dict):
                errors.append(f"CVR_CONTEST_NOT_OBJECT:{rid}")
                continue
            cid = sid(contest_vote.get("contest_id"))
            if not cid:
                errors.append(f"CVR_CONTEST_MISSING_ID:{rid}")
                continue
            if cid in seen_vote_rows:
                errors.append(f"CVR_DUPLICATE_CONTEST_IN_RECORD:{rid}:{cid}")
            seen_vote_rows[cid] = contest_vote
        for cid in allowed_contests:
            vote = seen_vote_rows.get(cid, {"selected_option_ids": []})
            selected = [sid(x) for x in (vote.get("selected_option_ids") or [])]
            limit = int(idx["contest_limits"].get(cid) or 0)
            unknown = [oid for oid in selected if oid not in idx["contest_options"].get(cid, set())]
            for oid in unknown:
                errors.append(f"CVR_UNKNOWN_OPTION:{rid}:{cid}:{oid}")
            if len(selected) > limit:
                errors.append(f"CVR_SELECTION_LIMIT_EXCEEDED:{rid}:{cid}:selected={len(selected)}:limit={limit}")
                overvote = 1
            else:
                overvote = 0
            units[unit_id]["contest_records"][cid].append({
                "record_id": rid,
                "selection_count": len([oid for oid in selected if oid not in unknown]),
                "overvote": overvote,
            })
        for cid in seen_vote_rows:
            if allowed_contests and cid not in allowed_contests:
                errors.append(f"CVR_CONTEST_NOT_IN_BALLOT_STYLE:{rid}:{style_id}:{cid}")
    out_units: dict[str, dict[str, Any]] = {}
    for unit_id, urow in units.items():
        contest_out: dict[str, dict[str, int]] = {}
        for cid, rows in urow["contest_records"].items():
            limit = int(idx["contest_limits"].get(cid) or 0)
            eligible = len(rows)
            selection_count = sum(int(r["selection_count"]) for r in rows)
            overvote_records = sum(int(r["overvote"]) for r in rows)
            slots = eligible * limit
            contest_out[cid] = {
                "eligible_ballot_count": eligible,
                "selection_limit": limit,
                "expected_selection_slots": slots,
                "cvr_selection_count": selection_count,
                "undervote_slots": max(0, slots - selection_count),
                "overvote_record_count": overvote_records,
            }
        out_units[unit_id] = {"cvr_record_count": int(urow["cvr_record_count"]), "contests": contest_out}
    return out_units


def int_or_error(row: dict[str, Any], field: str, errors: list[str], code: str) -> int:
    try:
        return int(row.get(field))
    except Exception:
        errors.append(f"{code}_{field.upper()}_NOT_INTEGER")
        return -1


def expected_rows(accounting: dict[str, Any], idx: dict[str, Any], errors: list[str]) -> dict[tuple[str, str], dict[str, int]]:
    if accounting.get("schema_family") != ACCOUNTING_FAMILY:
        errors.append("ACCOUNTING_SCHEMA_FAMILY_UNSUPPORTED")
    out: dict[tuple[str, str], dict[str, int]] = {}
    seen_units: set[str] = set()
    for unit in list_field(accounting, "reporting_units", errors, "ACCOUNTING"):
        if not isinstance(unit, dict):
            errors.append("ACCOUNTING_REPORTING_UNIT_NOT_OBJECT")
            continue
        unit_id = sid(unit.get("reporting_unit_id"))
        if not unit_id:
            errors.append("ACCOUNTING_REPORTING_UNIT_MISSING_ID")
            continue
        if unit_id in seen_units:
            errors.append(f"ACCOUNTING_DUPLICATE_REPORTING_UNIT:{unit_id}")
        seen_units.add(unit_id)
        if unit_id not in idx["gp_units"]:
            errors.append(f"ACCOUNTING_UNKNOWN_REPORTING_UNIT:{unit_id}")
        cvr_count = int_or_error(unit, "cvr_record_count", errors, "ACCOUNTING")
        ballots_cast = int_or_error(unit, "ballots_cast", errors, "ACCOUNTING")
        if ballots_cast != cvr_count:
            errors.append(f"ACCOUNTING_BALLOTS_CAST_CVR_COUNT_MISMATCH:{unit_id}:ballots_cast={ballots_cast}:cvr_record_count={cvr_count}")
        for contest in unit.get("contest_accounting") or []:
            if not isinstance(contest, dict):
                errors.append(f"ACCOUNTING_CONTEST_ROW_NOT_OBJECT:{unit_id}")
                continue
            cid = sid(contest.get("contest_id"))
            if not cid:
                errors.append(f"ACCOUNTING_CONTEST_MISSING_ID:{unit_id}")
                continue
            if cid not in idx["contests"]:
                errors.append(f"ACCOUNTING_UNKNOWN_CONTEST:{unit_id}:{cid}")
            key = (unit_id, cid)
            if key in out:
                errors.append(f"ACCOUNTING_DUPLICATE_CONTEST_ROW:{unit_id}:{cid}")
            row = {
                "cvr_record_count": cvr_count,
                "ballots_cast": ballots_cast,
                "eligible_ballot_count": int_or_error(contest, "eligible_ballot_count", errors, "ACCOUNTING"),
                "selection_limit": int_or_error(contest, "selection_limit", errors, "ACCOUNTING"),
                "expected_selection_slots": int_or_error(contest, "expected_selection_slots", errors, "ACCOUNTING"),
                "cvr_selection_count": int_or_error(contest, "cvr_selection_count", errors, "ACCOUNTING"),
                "undervote_slots": int_or_error(contest, "undervote_slots", errors, "ACCOUNTING"),
                "overvote_record_count": int_or_error(contest, "overvote_record_count", errors, "ACCOUNTING"),
            }
            out[key] = row
    return out


def build_report(bd_path: Path, cvr_path: Path, accounting_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    bd = load_json(bd_path)
    cvr = load_json(cvr_path)
    accounting = load_json(accounting_path)
    for label, obj in [("CVR", cvr), ("ACCOUNTING", accounting)]:
        if isinstance(obj, dict) and obj.get("election_id") != bd.get("election_id"):
            errors.append(f"{label}_ELECTION_ID_MISMATCH:{obj.get('election_id')}!={bd.get('election_id')}")
        if isinstance(obj, dict) and obj.get("jurisdiction") != bd.get("jurisdiction"):
            errors.append(f"{label}_JURISDICTION_MISMATCH:{obj.get('jurisdiction')}!={bd.get('jurisdiction')}")
    idx = index_bd(bd, errors)
    computed = compute_cvr_accounting(cvr, idx, errors)
    expected = expected_rows(accounting, idx, errors)
    rows: list[dict[str, Any]] = []
    for key in sorted(set(expected) | {(unit_id, cid) for unit_id, unit in computed.items() for cid in unit.get("contests", {})}):
        unit_id, cid = key
        observed_unit = computed.get(unit_id, {})
        observed_contest = (observed_unit.get("contests") or {}).get(cid, {})
        expected_row = expected.get(key)
        if expected_row is None:
            errors.append(f"ACCOUNTING_MISSING_CONTEST_ROW:{unit_id}:{cid}")
            expected_row = {}
        if not observed_contest:
            errors.append(f"ACCOUNTING_NO_CVR_CONTEST_OBSERVATION:{unit_id}:{cid}")
        observed = {
            "cvr_record_count": int(observed_unit.get("cvr_record_count") or 0),
            "eligible_ballot_count": int(observed_contest.get("eligible_ballot_count") or 0),
            "selection_limit": int(observed_contest.get("selection_limit") or 0),
            "expected_selection_slots": int(observed_contest.get("expected_selection_slots") or 0),
            "cvr_selection_count": int(observed_contest.get("cvr_selection_count") or 0),
            "undervote_slots": int(observed_contest.get("undervote_slots") or 0),
            "overvote_record_count": int(observed_contest.get("overvote_record_count") or 0),
        }
        comparisons: dict[str, bool] = {}
        for field in ["cvr_record_count", "eligible_ballot_count", "selection_limit", "expected_selection_slots", "cvr_selection_count", "undervote_slots", "overvote_record_count"]:
            if field in expected_row:
                comparisons[field] = int(expected_row.get(field) or 0) == observed[field]
                if not comparisons[field]:
                    errors.append(f"ACCOUNTING_FIELD_MISMATCH:{unit_id}:{cid}:{field}:expected={expected_row.get(field)}:observed={observed[field]}")
        rows.append({
            "reporting_unit_id": unit_id,
            "contest_id": cid,
            "expected": expected_row,
            "observed": observed,
            "comparisons": comparisons,
            "match": bool(comparisons) and all(comparisons.values()),
        })

    if not rows:
        errors.append("ACCOUNTING_NO_RECONCILIATION_ROWS")
    decision = PASS_DECISION if not errors and all(r.get("match") is True for r in rows) else FAIL_DECISION
    report = {
        "report_id": f"BALLOT-ACCOUNTING-RECONCILIATION-rev{REV}",
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "generated_at": release_date(ROOT) + "T00:00:00Z",
        "decision": decision,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_live_custody_claim": True,
        "no_full_nist_conformance_claim": True,
        "no_outcome_proof_claim": True,
        "boundary": BOUNDARY,
        "inputs": [
            {"role": "ballot_definition", "path": rel(bd_path), "sha256": digest_file(bd_path)},
            {"role": "cast_vote_records", "path": rel(cvr_path), "sha256": digest_file(cvr_path)},
            {"role": "ballot_accounting", "path": rel(accounting_path), "sha256": digest_file(accounting_path)},
        ],
        "counts": {
            "reporting_unit_count": len({r["reporting_unit_id"] for r in rows}),
            "contest_accounting_row_count": len(rows),
            "cvr_record_count": sum(int(u.get("cvr_record_count") or 0) for u in computed.values()),
            "matched_reconciliation_row_count": sum(1 for r in rows if r.get("match") is True),
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "reconciliation_rows": rows,
        "errors": errors,
        "warnings": warnings,
        "accounting_hash": digest_json(accounting),
        "adapter_scope": "Minimal synthetic ballot-accounting projection reconciled against BD/CVR identifiers and selection limits; not a live custody/admissibility record.",
        "risk_burndown": {
            "burned_down": "K02/K03 seam where replayed result totals could match while ballot-accounting completeness remained unchecked.",
            "still_missing": "Authorized local ballot-accounting exports, seal/transfer logs, exception records, disposition records, and external reviewer execution.",
            "negative_controls": [
                "artifacts/test-vectors/ballot-accounting/ballot-accounting-cvr-count-mismatch.json",
                "artifacts/test-vectors/ballot-accounting/ballot-accounting-undervote-mismatch.json",
                "artifacts/test-vectors/ballot-accounting/ballot-accounting-unknown-unit.json",
            ],
        },
    }
    return report


def public_summary(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Synthetic ballot-accounting reconciliation",
        "",
        f"Archive version: `{report['archive_version']}`  ",
        f"Report: `artifacts/reports/ballot-accounting-reconciliation-rev{REV}.json`  ",
        "",
        "This is a synthetic reconciliation of the Example County minimal BD/CVR fixture against a minimal ballot-accounting ledger.",
        "",
        "## Result",
        "",
        f"- Decision: `{report['decision']}`.",
        f"- Reporting units checked: `{counts['reporting_unit_count']}`.",
        f"- Contest accounting rows checked: `{counts['contest_accounting_row_count']}`.",
        f"- Synthetic CVR records counted: `{counts['cvr_record_count']}`.",
        f"- Errors: `{counts['error_count']}`.",
        "",
        "## What this catches",
        "",
        "- CVR record count drift against ballot-accounting totals.",
        "- Contest eligible-ballot, selection-slot, selection-count, undervote-slot, and overvote-record mismatches.",
        "- Unknown reporting units or contests in the accounting ledger.",
        "",
        "## Boundary",
        "",
        "This is not live custody evidence, not a full NIST CDF conformance result, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.",
        "It does not authorize live pilot use and does not replace ballot accounting, custody transfer/seal records, audit, recount, canvass, certification, retention, public-records review, or counsel review.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Reconcile synthetic ballot accounting against BD/CVR fixture")
    ap.add_argument("--bd", type=Path, default=DEFAULT_BD)
    ap.add_argument("--cvr", type=Path, default=DEFAULT_CVR)
    ap.add_argument("--accounting", type=Path, default=DEFAULT_ACCOUNTING)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = build_report(args.bd, args.cvr, args.accounting)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        PUBLIC.write_text(public_summary(report), encoding="utf-8")
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        print(f"{report['decision']}: rows={report['counts']['contest_accounting_row_count']} errors={report['counts']['error_count']}")
    return 0 if report["decision"] == PASS_DECISION else 2


if __name__ == "__main__":
    raise SystemExit(main())
