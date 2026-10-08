#!/usr/bin/env python3
"""Independent synthetic CDF replay verifier for the Example County fixture.

This verifier deliberately does **not** import or shell out to
the primary replay adapter.  It re-parses the minimal BD/CVR/ERR projection,
recomputes CVR-derived option totals, compares them with the published ERR
projection, then cross-checks the shipped primary adapter report and CRO.  The
scope is narrow by design: this is not full NIST CDF conformance and not live
jurisdiction evidence.
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
DEFAULT_ERR = CDF_DIR / "election-results-minimal.json"
DEFAULT_PRIMARY_REPORT = ROOT / "artifacts" / "reports" / f"cdf-export-replay-report-rev{REV}.json"
DEFAULT_CRO = CDF_DIR / "canonical-results-object-from-cdf.json"
REPORT = ROOT / "artifacts" / "reports" / f"cdf-independent-replay-verifier-rev{REV}.json"
PUBLIC = CDF_DIR / "public-cdf-independent-verifier.md"
SCHEMA_FAMILY = "TES-CDF-MINIMAL-PROJECTION-v1"
BOUNDARY = (
    "Independent synthetic replay transcript only; not full NIST CDF conformance, "
    "not the NIST CDF Test Method, not live jurisdiction export evidence, not certification, "
    "not outcome proof, not current voter instruction, and not legal advice."
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    # The fixture contains only simple JSON values.  This local encoder is used
    # to avoid depending on the primary adapter's canonicalization helper.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_json(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()


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
        gp_units[sid(row.get("id"))] = row

    styles: dict[str, dict[str, Any]] = {}
    for row in list_field(bd, "ballot_styles", errors, "BD"):
        if not isinstance(row, dict):
            errors.append("BD_BALLOT_STYLE_NOT_OBJECT")
            continue
        styles[sid(row.get("id"))] = row

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
    contest_options: dict[str, set[str]] = {}
    contest_limits: dict[str, int] = {}
    option_owner: dict[str, str] = {}
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
        opts = []
        for option in contest.get("options") or []:
            if not isinstance(option, dict):
                errors.append(f"BD_OPTION_NOT_OBJECT:{cid}")
                continue
            oid = sid(option.get("id"))
            opts.append(oid)
            if not oid:
                errors.append(f"BD_OPTION_MISSING_ID:{cid}")
                continue
            if oid in option_owner:
                errors.append(f"BD_OPTION_ID_REUSED:{oid}")
            option_owner[oid] = cid
        for dup in duplicate_ids(opts):
            errors.append(f"BD_DUPLICATE_OPTION:{cid}:{dup}")
        contest_options[cid] = {o for o in opts if o}

    unit_contests: dict[str, set[str]] = {gid: set() for gid in gp_units if gid}
    for style_id, style in styles.items():
        if not style_id:
            errors.append("BD_BALLOT_STYLE_MISSING_ID")
        style_units = [sid(unit_id) for unit_id in style.get("gp_unit_ids") or [] if sid(unit_id)]
        style_contests = [sid(contest_id) for contest_id in style.get("contest_ids") or [] if sid(contest_id)]
        for unit_id in style_units:
            if unit_id not in gp_units:
                errors.append(f"BD_BALLOT_STYLE_UNKNOWN_GP_UNIT:{style_id}:{unit_id}")
            else:
                unit_contests.setdefault(unit_id, set()).update(contest_id for contest_id in style_contests if contest_id in contests)
        for contest_id in style_contests:
            if contest_id not in contests:
                errors.append(f"BD_BALLOT_STYLE_UNKNOWN_CONTEST:{style_id}:{contest_id}")

    return {
        "gp_units": gp_units,
        "styles": styles,
        "contests": contests,
        "contest_options": contest_options,
        "contest_limits": contest_limits,
        "option_owner": option_owner,
        "unit_contests": unit_contests,
    }


def tally_cvr(cvr: dict[str, Any], idx: dict[str, Any], errors: list[str]) -> dict[str, dict[str, dict[str, int]]]:
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

    totals: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # type: ignore[assignment]
    for record in records:
        rid = sid(record.get("id")) or "<missing-record-id>"
        style_id = sid(record.get("ballot_style_id"))
        unit_id = sid(record.get("reporting_unit_id"))
        style = idx["styles"].get(style_id)
        if style is None:
            errors.append(f"CVR_UNKNOWN_BALLOT_STYLE:{rid}:{style_id}")
            allowed_contests: set[str] = set()
        else:
            allowed_contests = {sid(x) for x in style.get("contest_ids") or [] if sid(x)}
        if unit_id not in idx["gp_units"]:
            errors.append(f"CVR_UNKNOWN_REPORTING_UNIT:{rid}:{unit_id}")

        seen_contests: set[str] = set()
        for contest_vote in record.get("contests") or []:
            if not isinstance(contest_vote, dict):
                errors.append(f"CVR_CONTEST_NOT_OBJECT:{rid}")
                continue
            cid = sid(contest_vote.get("contest_id"))
            if not cid:
                errors.append(f"CVR_CONTEST_MISSING_ID:{rid}")
                continue
            if cid in seen_contests:
                errors.append(f"CVR_DUPLICATE_CONTEST_IN_RECORD:{rid}:{cid}")
            seen_contests.add(cid)
            if cid not in idx["contests"]:
                errors.append(f"CVR_UNKNOWN_CONTEST:{rid}:{cid}")
                continue
            if allowed_contests and cid not in allowed_contests:
                errors.append(f"CVR_CONTEST_NOT_IN_BALLOT_STYLE:{rid}:{style_id}:{cid}")
            selected = [sid(x) for x in contest_vote.get("selected_option_ids") or []]
            limit = int(idx["contest_limits"].get(cid) or 0)
            if len(selected) > limit:
                errors.append(f"CVR_SELECTION_LIMIT_EXCEEDED:{rid}:{cid}:selected={len(selected)}:limit={limit}")
            for oid in selected:
                if oid not in idx["contest_options"].get(cid, set()):
                    errors.append(f"CVR_UNKNOWN_OPTION:{rid}:{cid}:{oid}")
                    continue
                totals[unit_id][cid][oid] += 1
    return {
        unit_id: {cid: dict(options) for cid, options in sorted(contests.items())}
        for unit_id, contests in sorted(totals.items())
    }


def tally_err(err: dict[str, Any], idx: dict[str, Any], errors: list[str]) -> dict[str, dict[str, dict[str, int]]]:
    if err.get("schema_family") != SCHEMA_FAMILY:
        errors.append("ERR_SCHEMA_FAMILY_UNSUPPORTED")
    totals: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # type: ignore[assignment]
    seen_rows: set[tuple[str, str]] = set()
    for row in list_field(err, "results", errors, "ERR"):
        if not isinstance(row, dict):
            errors.append("ERR_RESULT_NOT_OBJECT")
            continue
        cid = sid(row.get("contest_id"))
        unit_id = sid(row.get("reporting_unit_id"))
        if cid not in idx["contests"]:
            errors.append(f"ERR_UNKNOWN_CONTEST:{cid}")
            continue
        if not unit_id:
            errors.append(f"ERR_MISSING_REPORTING_UNIT:{cid}")
        elif unit_id not in idx["gp_units"]:
            errors.append(f"ERR_UNKNOWN_REPORTING_UNIT:{cid}:{unit_id}")
        key = (unit_id, cid)
        if key in seen_rows:
            errors.append(f"ERR_DUPLICATE_RESULT_ROW:{unit_id}:{cid}")
        seen_rows.add(key)
        for option in row.get("options") or []:
            if not isinstance(option, dict):
                errors.append(f"ERR_OPTION_NOT_OBJECT:{cid}")
                continue
            oid = sid(option.get("option_id"))
            if oid not in idx["contest_options"].get(cid, set()):
                errors.append(f"ERR_UNKNOWN_OPTION:{cid}:{oid}")
                continue
            votes = option.get("votes")
            if isinstance(votes, bool) or not isinstance(votes, int) or votes < 0:
                errors.append(f"ERR_INVALID_VOTES:{cid}:{oid}:{votes!r}")
                continue
            totals[unit_id][cid][oid] += votes
    return {
        unit_id: {cid: dict(options) for cid, options in sorted(contests.items())}
        for unit_id, contests in sorted(totals.items())
    }


def comparison_rows(
    idx: dict[str, Any],
    cvr_totals: dict[str, dict[str, dict[str, int]]],
    err_totals: dict[str, dict[str, dict[str, int]]],
    errors: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    units = sorted(set(idx["unit_contests"]) | set(cvr_totals) | set(err_totals))
    for unit_id in units:
        contest_ids = sorted(set(idx["unit_contests"].get(unit_id, set())) | set(cvr_totals.get(unit_id, {})) | set(err_totals.get(unit_id, {})))
        for cid in contest_ids:
            if cid not in idx["contests"]:
                continue
            for oid in sorted(idx["contest_options"].get(cid, set())):
                cvr_votes = int(cvr_totals.get(unit_id, {}).get(cid, {}).get(oid, 0))
                err_votes = int(err_totals.get(unit_id, {}).get(cid, {}).get(oid, 0))
                match = cvr_votes == err_votes
                if not match:
                    errors.append(f"ERR_TOTAL_MISMATCH:{unit_id}:{cid}:{oid}:cvr={cvr_votes}:err={err_votes}")
                rows.append({
                    "reporting_unit_id": unit_id,
                    "contest_id": cid,
                    "option_id": oid,
                    "cvr_votes": cvr_votes,
                    "err_votes": err_votes,
                    "match": match,
                })
    return rows


def cro_rows(cro: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    results = cro.get("results") if isinstance(cro, dict) else {}
    for contest in (results or {}).get("contests") or []:
        if not isinstance(contest, dict):
            continue
        cid = sid(contest.get("contest_id"))
        for unit in contest.get("reporting_units") or []:
            if not isinstance(unit, dict):
                continue
            unit_id = sid(unit.get("reporting_unit_id"))
            for option in unit.get("options") or []:
                if not isinstance(option, dict):
                    continue
                rows.append({"reporting_unit_id": unit_id, "contest_id": cid, "option_id": sid(option.get("option_id")), "votes": option.get("votes")})
    return sorted(rows, key=lambda r: (r["reporting_unit_id"], r["contest_id"], r["option_id"]))


def build_report(bd_path: Path, cvr_path: Path, err_path: Path, primary_report_path: Path, cro_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings = ["minimal_projection_only_not_full_nist_cdf_conformance"]

    bd = load_json(bd_path)
    cvr = load_json(cvr_path)
    err = load_json(err_path)
    primary = load_json(primary_report_path) if primary_report_path.exists() else {}
    cro = load_json(cro_path) if cro_path.exists() else {}

    if not isinstance(bd, dict):
        raise SystemExit("BD JSON root must be an object")
    if not isinstance(cvr, dict):
        raise SystemExit("CVR JSON root must be an object")
    if not isinstance(err, dict):
        raise SystemExit("ERR JSON root must be an object")

    election_ids = {sid(bd.get("election_id")), sid(cvr.get("election_id")), sid(err.get("election_id"))}
    if len(election_ids) != 1 or not next(iter(election_ids), ""):
        errors.append("ELECTION_ID_MISMATCH")

    idx = index_bd(bd, errors)
    cvr_totals = tally_cvr(cvr, idx, errors)
    published_totals = tally_err(err, idx, errors)
    rows = comparison_rows(idx, cvr_totals, published_totals, errors)

    primary_rows = primary.get("comparison_rows") if isinstance(primary, dict) else None
    primary_decision = primary.get("decision") if isinstance(primary, dict) else None
    primary_cro_hash = primary.get("cro_hash") if isinstance(primary, dict) else None
    cro_hash = cro.get("cro_hash") if isinstance(cro, dict) else None
    cro_vote_rows = cro_rows(cro) if isinstance(cro, dict) else []
    independent_cro_vote_rows = sorted(
        [{"reporting_unit_id": r["reporting_unit_id"], "contest_id": r["contest_id"], "option_id": r["option_id"], "votes": r["err_votes"]} for r in rows],
        key=lambda r: (r["reporting_unit_id"], r["contest_id"], r["option_id"]),
    )

    primary_decision_expected = primary_decision == "SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE"
    primary_report_agrees = primary_rows == rows
    cro_agrees = cro_vote_rows == independent_cro_vote_rows
    cro_hash_agrees = primary_cro_hash == cro_hash

    if not primary_decision_expected:
        errors.append(f"PRIMARY_REPLAY_UNEXPECTED_DECISION:{primary_decision}")
    if not primary_report_agrees:
        errors.append("PRIMARY_REPLAY_COMPARISON_ROWS_DISAGREE")
    if not cro_agrees:
        errors.append("PRIMARY_CRO_VOTE_ROWS_DISAGREE")
    if not cro_hash_agrees:
        errors.append("PRIMARY_CRO_HASH_DISAGREES_WITH_CRO_FILE")

    agreement = not errors
    decision = "INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE" if agreement else "FAIL_INDEPENDENT_CDF_REPLAY_DISAGREEMENT"
    counts = {
        "contest_count": len(idx["contests"]),
        "option_count": sum(len(v) for v in idx["contest_options"].values()),
        "cvr_record_count": len(cvr.get("records") or []),
        "reporting_unit_count": sum(1 for contests in idx["unit_contests"].values() if contests),
        "comparison_row_count": len(rows),
        "matched_comparison_row_count": sum(1 for r in rows if r.get("match") is True),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "primary_comparison_row_count": len(primary_rows or []),
        "primary_cro_vote_row_count": len(cro_vote_rows),
    }

    return {
        "archive_version": VERSION,
        "report_id": f"CDF-INDEPENDENT-REPLAY-VERIFIER-rev{REV}",
        "generated_at": release_date(ROOT) + "T00:00:00Z",
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_full_nist_conformance_claim": True,
        "decision": decision,
        "boundary": BOUNDARY,
        "independence_claim": "Separate stdlib parser/tally path; does not import or execute the primary replay adapter; cross-checks shipped primary report and CRO bytes.",
        "inputs": [
            {"role": "ballot_definition", "path": rel(bd_path), "sha256": sha256_file(bd_path)},
            {"role": "cast_vote_records", "path": rel(cvr_path), "sha256": sha256_file(cvr_path)},
            {"role": "election_results", "path": rel(err_path), "sha256": sha256_file(err_path)},
            {"role": "primary_replay_report", "path": rel(primary_report_path), "sha256": sha256_file(primary_report_path) if primary_report_path.exists() else None},
            {"role": "primary_canonical_results_object", "path": rel(cro_path), "sha256": sha256_file(cro_path) if cro_path.exists() else None},
        ],
        "primary_report_digest": sha256_file(primary_report_path) if primary_report_path.exists() else None,
        "primary_cro_digest": sha256_file(cro_path) if cro_path.exists() else None,
        "primary_report_agrees": primary_report_agrees,
        "primary_decision_expected": primary_decision_expected,
        "cro_agrees": cro_agrees,
        "cro_hash_agrees": cro_hash_agrees,
        "primary_cro_hash": primary_cro_hash,
        "cro_hash": cro_hash,
        "cvr_totals": cvr_totals,
        "published_totals": published_totals,
        "comparison_rows": rows,
        "cro_vote_rows": cro_vote_rows,
        "counts": counts,
        "errors": errors,
        "warnings": warnings,
        "refactor_audit": {
            "status": "PASS" if agreement else "FAIL",
            "risk_closed": "K03 now has an independent synthetic verifier transcript in addition to the primary adapter report.",
            "avoids": "single-implementation replay success being mistaken for independent reproducibility",
            "not_closed": "live jurisdiction exports, full NIST CDF parser/conformance, external reviewer execution, and legal/certification reliance remain no-go",
        },
    }


def public_text(report: dict[str, Any]) -> str:
    counts = report.get("counts") or {}
    return "\n".join([
        "# Independent CDF replay verifier status",
        "",
        "**Synthetic independent transcript only. This is not live election evidence and not a full NIST CDF conformance result.**",
        "",
        f"Archive version: `{report['archive_version']}`  ",
        f"Decision: `{report['decision']}`  ",
        f"Primary CRO hash: `{report.get('cro_hash')}`",
        "",
        "This verifier re-parses the synthetic Ballot Definition, Cast Vote Records, and Election Results minimal projection without importing or executing the primary replay adapter. It recomputes option totals by reporting unit and compares both the primary adapter rows and the shipped CRO vote rows.",
        "",
        "## Counts",
        "",
        f"- Contests: `{counts.get('contest_count')}`",
        f"- Options: `{counts.get('option_count')}`",
        f"- CVR records: `{counts.get('cvr_record_count')}`",
        f"- Reporting units: `{counts.get('reporting_unit_count')}`",
        f"- Comparison rows: `{counts.get('comparison_row_count')}`",
        f"- Errors: `{counts.get('error_count')}`",
        "",
        "## Boundary",
        "",
        "This is an independent synthetic replay transcript, not live jurisdiction export evidence, not a complete parser for NIST BD, CVR, ERR, VRI, or EEL formats, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.",
        "",
    ])


def write_outputs(report: dict[str, Any]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    CDF_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    PUBLIC.write_text(public_text(report), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bd", type=Path, default=DEFAULT_BD)
    ap.add_argument("--cvr", type=Path, default=DEFAULT_CVR)
    ap.add_argument("--err", type=Path, default=DEFAULT_ERR)
    ap.add_argument("--primary-report", type=Path, default=DEFAULT_PRIMARY_REPORT)
    ap.add_argument("--cro", type=Path, default=DEFAULT_CRO)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = build_report(args.bd, args.cvr, args.err, args.primary_report, args.cro)
    if args.write and not report["errors"]:
        write_outputs(report)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        print(f"decision={report['decision']} rows={report['counts']['comparison_row_count']} errors={report['counts']['error_count']} version={VERSION}")
    return 0 if not report["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
