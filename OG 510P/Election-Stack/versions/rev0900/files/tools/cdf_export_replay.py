#!/usr/bin/env python3
"""Replay a minimal BD/CVR/ERR projection into a canonical results object.

This tool is intentionally *not* a complete NIST CDF conformance validator.  It
is a small executable bridge for the mission-kernel risk called out in MKB-003:
can a verifier recompute published result totals from exported ballot-definition,
CVR, and election-results bytes instead of trusting a hand-authored narrative?

Accepted input is the repository's `TES-CDF-MINIMAL-PROJECTION-v1` fixture
shape, with identifiers aligned to the NIST Ballot Definition, Cast Vote Records,
and Election Results Reporting CDF families.  Full CDF XML/JSON parsing and the
NIST CDF Test Method remain future work and must not be claimed from this tool.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from jcs import dump_bytes
from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
DEFAULT_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
DEFAULT_BD = DEFAULT_DIR / "ballot-definition-minimal.json"
DEFAULT_CVR = DEFAULT_DIR / "cast-vote-records-minimal.json"
DEFAULT_ERR = DEFAULT_DIR / "election-results-minimal.json"
REPORT = ROOT / "artifacts" / "reports" / f"cdf-export-replay-report-rev{REV}.json"
CRO_OUT = DEFAULT_DIR / "canonical-results-object-from-cdf.json"
MANIFEST_OUT = DEFAULT_DIR / "cdf-mapping-manifest.json"
PUBLIC_MD = DEFAULT_DIR / "public-cdf-export-replay.md"
SCHEMA_FAMILY = "TES-CDF-MINIMAL-PROJECTION-v1"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_json_value(obj: Any) -> str:
    return "sha256:" + sha256_bytes(dump_bytes(obj))


def digest_file(path: Path) -> str:
    return "sha256:" + sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def require_list(obj: dict[str, Any], field: str, errors: list[str], code: str) -> list[Any]:
    value = obj.get(field)
    if not isinstance(value, list):
        errors.append(f"{code}:{field}: expected array")
        return []
    return value


def _string_id(value: Any) -> str:
    return str(value or "").strip()


def _duplicate_ids(values: list[str]) -> list[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if not value:
            continue
        if value in seen:
            dup.add(value)
        seen.add(value)
    return sorted(dup)


def index_ballot_definition(bd: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    if bd.get("schema_family") != SCHEMA_FAMILY:
        errors.append("BD_SCHEMA_FAMILY_UNSUPPORTED: ballot definition is not the minimal projection fixture")

    gp_units = { _string_id(g.get("id")): g for g in require_list(bd, "gp_units", errors, "BD") if isinstance(g, dict) }
    ballot_styles = { _string_id(s.get("id")): s for s in require_list(bd, "ballot_styles", errors, "BD") if isinstance(s, dict) }
    contests_raw = [c for c in require_list(bd, "contests", errors, "BD") if isinstance(c, dict)]
    contests = { _string_id(c.get("id")): c for c in contests_raw }

    for label, values in [
        ("BD_DUPLICATE_GP_UNIT", list(gp_units.keys())),
        ("BD_DUPLICATE_BALLOT_STYLE", list(ballot_styles.keys())),
        ("BD_DUPLICATE_CONTEST", list(contests.keys())),
    ]:
        for dup in _duplicate_ids(values):
            errors.append(f"{label}:{dup}")

    option_to_contest: dict[str, str] = {}
    contest_options: dict[str, set[str]] = {}
    contest_limits: dict[str, int] = {}
    for contest in contests_raw:
        cid = _string_id(contest.get("id"))
        if not cid:
            errors.append("BD_CONTEST_MISSING_ID")
            continue
        try:
            limit = int(contest.get("selection_limit"))
        except Exception:
            limit = 0
        if limit <= 0:
            errors.append(f"BD_CONTEST_INVALID_SELECTION_LIMIT:{cid}")
        contest_limits[cid] = limit
        options = [o for o in contest.get("options") or [] if isinstance(o, dict)]
        ids = [_string_id(o.get("id")) for o in options]
        if not ids:
            errors.append(f"BD_CONTEST_NO_OPTIONS:{cid}")
        for dup in _duplicate_ids(ids):
            errors.append(f"BD_DUPLICATE_OPTION:{cid}:{dup}")
        contest_options[cid] = {oid for oid in ids if oid}
        for oid in ids:
            if not oid:
                errors.append(f"BD_OPTION_MISSING_ID:{cid}")
            elif oid in option_to_contest:
                errors.append(f"BD_OPTION_ID_NOT_GLOBAL:{oid}")
            else:
                option_to_contest[oid] = cid

    unit_contests: dict[str, set[str]] = {gid: set() for gid in gp_units if gid}
    for sid, style in ballot_styles.items():
        if not sid:
            errors.append("BD_BALLOT_STYLE_MISSING_ID")
            continue
        style_units = [_string_id(gid) for gid in style.get("gp_unit_ids") or [] if _string_id(gid)]
        style_contests = [_string_id(cid) for cid in style.get("contest_ids") or [] if _string_id(cid)]
        for gid in style_units:
            if gid not in gp_units:
                errors.append(f"BD_BALLOT_STYLE_UNKNOWN_GP_UNIT:{sid}:{gid}")
            else:
                unit_contests.setdefault(gid, set()).update(cid for cid in style_contests if cid in contests)
        for cid in style_contests:
            if cid not in contests:
                errors.append(f"BD_BALLOT_STYLE_UNKNOWN_CONTEST:{sid}:{cid}")

    return {
        "gp_units": gp_units,
        "ballot_styles": ballot_styles,
        "contests": contests,
        "contest_options": contest_options,
        "contest_limits": contest_limits,
        "option_to_contest": option_to_contest,
        "unit_contests": unit_contests,
    }


def tally_cvr(cvr: dict[str, Any], bd_index: dict[str, Any], errors: list[str]) -> dict[str, dict[str, dict[str, int]]]:
    if cvr.get("schema_family") != SCHEMA_FAMILY:
        errors.append("CVR_SCHEMA_FAMILY_UNSUPPORTED: CVR export is not the minimal projection fixture")
    records = [r for r in require_list(cvr, "records", errors, "CVR") if isinstance(r, dict)]
    for dup in _duplicate_ids([_string_id(r.get("id")) for r in records]):
        errors.append(f"CVR_DUPLICATE_RECORD:{dup}")

    styles = bd_index["ballot_styles"]
    gp_units = bd_index["gp_units"]
    contests = bd_index["contests"]
    contest_options = bd_index["contest_options"]
    contest_limits = bd_index["contest_limits"]
    totals: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # type: ignore[assignment]

    for record in records:
        rid = _string_id(record.get("id")) or "<missing-record-id>"
        style_id = _string_id(record.get("ballot_style_id"))
        unit_id = _string_id(record.get("reporting_unit_id"))
        if style_id not in styles:
            errors.append(f"CVR_UNKNOWN_BALLOT_STYLE:{rid}:{style_id}")
            allowed_contests: set[str] = set()
        else:
            allowed_contests = {_string_id(x) for x in styles[style_id].get("contest_ids") or [] if _string_id(x)}
        if unit_id not in gp_units:
            errors.append(f"CVR_UNKNOWN_REPORTING_UNIT:{rid}:{unit_id}")
        seen_contests: set[str] = set()
        for contest_vote in record.get("contests") or []:
            if not isinstance(contest_vote, dict):
                errors.append(f"CVR_CONTEST_NOT_OBJECT:{rid}")
                continue
            cid = _string_id(contest_vote.get("contest_id"))
            if not cid:
                errors.append(f"CVR_CONTEST_MISSING_ID:{rid}")
                continue
            if cid in seen_contests:
                errors.append(f"CVR_DUPLICATE_CONTEST_IN_RECORD:{rid}:{cid}")
            seen_contests.add(cid)
            if cid not in contests:
                errors.append(f"CVR_UNKNOWN_CONTEST:{rid}:{cid}")
                continue
            if allowed_contests and cid not in allowed_contests:
                errors.append(f"CVR_CONTEST_NOT_IN_BALLOT_STYLE:{rid}:{style_id}:{cid}")
            selected = [_string_id(x) for x in (contest_vote.get("selected_option_ids") or [])]
            if len(selected) > int(contest_limits.get(cid) or 0):
                errors.append(f"CVR_SELECTION_LIMIT_EXCEEDED:{rid}:{cid}:selected={len(selected)}:limit={contest_limits.get(cid)}")
            for opt in selected:
                if opt not in contest_options.get(cid, set()):
                    errors.append(f"CVR_UNKNOWN_OPTION:{rid}:{cid}:{opt}")
                    continue
                totals[unit_id][cid][opt] += 1
    return {
        unit_id: {cid: dict(opts) for cid, opts in sorted(contests.items())}
        for unit_id, contests in sorted(totals.items())
    }


def err_totals(err: dict[str, Any], bd_index: dict[str, Any], errors: list[str]) -> dict[str, dict[str, dict[str, int]]]:
    if err.get("schema_family") != SCHEMA_FAMILY:
        errors.append("ERR_SCHEMA_FAMILY_UNSUPPORTED: ERR export is not the minimal projection fixture")
    out: dict[str, dict[str, dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # type: ignore[assignment]
    contests = bd_index["contests"]
    contest_options = bd_index["contest_options"]
    gp_units = bd_index["gp_units"]
    seen_result_rows: set[tuple[str, str]] = set()
    for result in require_list(err, "results", errors, "ERR"):
        if not isinstance(result, dict):
            errors.append("ERR_RESULT_NOT_OBJECT")
            continue
        cid = _string_id(result.get("contest_id"))
        unit = _string_id(result.get("reporting_unit_id"))
        if cid not in contests:
            errors.append(f"ERR_UNKNOWN_CONTEST:{cid}")
            continue
        if not unit:
            errors.append(f"ERR_MISSING_REPORTING_UNIT:{cid}")
        elif unit not in gp_units:
            errors.append(f"ERR_UNKNOWN_REPORTING_UNIT:{cid}:{unit}")
        key = (unit, cid)
        if key in seen_result_rows:
            errors.append(f"ERR_DUPLICATE_RESULT_ROW:{unit}:{cid}")
        seen_result_rows.add(key)
        for option in result.get("options") or []:
            if not isinstance(option, dict):
                errors.append(f"ERR_OPTION_NOT_OBJECT:{cid}")
                continue
            oid = _string_id(option.get("option_id"))
            if oid not in contest_options.get(cid, set()):
                errors.append(f"ERR_UNKNOWN_OPTION:{cid}:{oid}")
                continue
            votes_raw = option.get("votes")
            if isinstance(votes_raw, bool) or not isinstance(votes_raw, int) or votes_raw < 0:
                errors.append(f"ERR_INVALID_VOTE_TOTAL:{cid}:{oid}:{votes_raw!r}")
                continue
            out[unit][cid][oid] += votes_raw
    return {
        unit_id: {cid: dict(opts) for cid, opts in sorted(contests.items())}
        for unit_id, contests in sorted(out.items())
    }


def compare_totals(
    cvr_totals: dict[str, dict[str, dict[str, int]]],
    published: dict[str, dict[str, dict[str, int]]],
    bd_index: dict[str, Any],
    errors: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    units = sorted(set(bd_index["unit_contests"]) | set(cvr_totals) | set(published))
    for unit_id in units:
        contest_ids = sorted(set(bd_index["unit_contests"].get(unit_id, set())) | set(cvr_totals.get(unit_id, {})) | set(published.get(unit_id, {})))
        for cid in contest_ids:
            if cid not in bd_index["contests"]:
                continue
            for oid in sorted(bd_index["contest_options"].get(cid, set())):
                cvr_v = int(cvr_totals.get(unit_id, {}).get(cid, {}).get(oid, 0))
                err_v = int(published.get(unit_id, {}).get(cid, {}).get(oid, 0))
                match = cvr_v == err_v
                if not match:
                    errors.append(f"ERR_TOTAL_MISMATCH:{unit_id}:{cid}:{oid}:cvr={cvr_v}:err={err_v}")
                rows.append({
                    "reporting_unit_id": unit_id,
                    "contest_id": cid,
                    "option_id": oid,
                    "cvr_votes": cvr_v,
                    "err_votes": err_v,
                    "match": match,
                })
    return rows


def mapping_manifest(bd: dict[str, Any], bd_digest: str, err: dict[str, Any]) -> dict[str, Any]:
    # This manifest is generated from the minimal projection.  It binds the ID
    # maps needed by the replay but does not claim full NIST CDF conformance.
    ballot_style_map = []
    for style in bd.get("ballot_styles") or []:
        if isinstance(style, dict):
            ballot_style_map.append({"ballot_style_id": _string_id(style.get("id")), "gp_unit_ids": [_string_id(x) for x in style.get("gp_unit_ids") or []]})
    contest_map = []
    option_map = []
    for contest in bd.get("contests") or []:
        if not isinstance(contest, dict):
            continue
        cid = _string_id(contest.get("id"))
        contest_map.append({"bd_contest_id": cid, "err_contest_id": cid})
        for opt in contest.get("options") or []:
            if isinstance(opt, dict):
                oid = _string_id(opt.get("id"))
                option_map.append({"bd_option_id": oid, "err_option_id": oid})
    reporting_unit_map = []
    unit_contest_rows = []
    for unit in bd.get("gp_units") or []:
        if not isinstance(unit, dict):
            continue
        unit_id = _string_id(unit.get("id"))
        row = {"gp_unit_id": unit_id, "type": _string_id(unit.get("type")) or "unspecified", "parents": [], "children": [], "external_ids": {}}
        if unit.get("parent_id"):
            row["parents"] = [_string_id(unit.get("parent_id"))]
        reporting_unit_map.append(row)
    for style in bd.get("ballot_styles") or []:
        if not isinstance(style, dict):
            continue
        for unit_id in [_string_id(x) for x in style.get("gp_unit_ids") or [] if _string_id(x)]:
            unit_contest_rows.append({
                "ballot_style_id": _string_id(style.get("id")),
                "gp_unit_id": unit_id,
                "contest_ids": [_string_id(x) for x in style.get("contest_ids") or [] if _string_id(x)],
            })
    manifest: dict[str, Any] = {
        "election_id": _string_id(bd.get("election_id") or err.get("election_id")),
        "bd_hash": bd_digest,
        "versions": {"bd": "NIST-SP-1500-20 minimal projection", "cvr": "NIST-SP-1500-103 minimal projection", "err": "NIST-SP-1500-100r2 minimal projection", "eel": f"not included in {VERSION} replay fixture"},
        "ballot_style_map": sorted(ballot_style_map, key=lambda r: r["ballot_style_id"]),
        "contest_map": sorted(contest_map, key=lambda r: r["bd_contest_id"]),
        "option_map": sorted(option_map, key=lambda r: r["bd_option_id"]),
        "reporting_unit_map": sorted(reporting_unit_map, key=lambda r: r["gp_unit_id"]),
        "unit_contest_map": sorted(unit_contest_rows, key=lambda r: (r["gp_unit_id"], r["ballot_style_id"])),
    }
    manifest["manifest_hash"] = digest_json_value({k: v for k, v in manifest.items() if k != "manifest_hash"})
    return manifest


def canonical_results_object(bd_digest: str, err: dict[str, Any], comparison_rows: list[dict[str, Any]]) -> dict[str, Any]:
    # Keep the CRO schema-clean.  This uses the BD projection digest as the EPB
    # hash stand-in for the synthetic fixture; the report states that limitation.
    results = {
        "schema_family": SCHEMA_FAMILY,
        "source_results_format": _string_id(err.get("cdf_name")),
        "contests": [],
    }
    by_contest_unit: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for row in comparison_rows:
        by_contest_unit[str(row["contest_id"])][str(row["reporting_unit_id"])].append({"option_id": row["option_id"], "votes": row["err_votes"]})
    for cid in sorted(by_contest_unit):
        unit_rows = []
        for unit_id in sorted(by_contest_unit[cid]):
            unit_rows.append({
                "reporting_unit_id": unit_id,
                "options": sorted(by_contest_unit[cid][unit_id], key=lambda r: r["option_id"]),
            })
        results["contests"].append({"contest_id": cid, "reporting_units": unit_rows})
    cro: dict[str, Any] = {
        "election_id": _string_id(err.get("election_id")),
        "epb_hash": bd_digest,
        "results_format": "TES-CDF-MINIMAL-PROJECTION-v1/NIST-BD-CVR-ERR-reporting-unit-replay",
        "reporting_time": _string_id(err.get("reporting_time")) or release_date(ROOT) + "T00:00:00Z",
        "report_detail_level": _string_id(err.get("report_detail_level")) or "unspecified",
        "counts_status": "MATCHED_TO_REPORTING_UNIT_CVR_FIXTURE",
        "unofficial": True,
        "results": results,
    }
    cro["cro_hash"] = digest_json_value({k: v for k, v in cro.items() if k != "cro_hash"})
    return cro


def build_report(bd_path: Path, cvr_path: Path, err_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    bd = load_json(bd_path)
    cvr = load_json(cvr_path)
    err = load_json(err_path)
    if not isinstance(bd, dict):
        raise SystemExit("BD JSON root must be an object")
    if not isinstance(cvr, dict):
        raise SystemExit("CVR JSON root must be an object")
    if not isinstance(err, dict):
        raise SystemExit("ERR JSON root must be an object")

    ids = {_string_id(bd.get("election_id")), _string_id(cvr.get("election_id")), _string_id(err.get("election_id"))}
    if len(ids) != 1 or not next(iter(ids), ""):
        errors.append("ELECTION_ID_MISMATCH: BD, CVR, and ERR election_id values must match")
    bd_index = index_ballot_definition(bd, errors)
    cvr_out = tally_cvr(cvr, bd_index, errors)
    err_out = err_totals(err, bd_index, errors)
    comparison_rows = compare_totals(cvr_out, err_out, bd_index, errors)
    bd_digest = digest_file(bd_path)
    cvr_digest = digest_file(cvr_path)
    err_digest = digest_file(err_path)
    manifest = mapping_manifest(bd, bd_digest, err)
    cro = canonical_results_object(bd_digest, err, comparison_rows)

    contest_count = len(bd_index["contests"])
    option_count = sum(len(v) for v in bd_index["contest_options"].values())
    cvr_record_count = len(cvr.get("records") or [])
    total_selections = sum(sum(sum(opts.values()) for opts in contests.values()) for contests in cvr_out.values())
    matched_rows = sum(1 for row in comparison_rows if row.get("match") is True)

    if not errors:
        decision = "SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE"
    elif any("UNKNOWN" in e or "SELECTION_LIMIT" in e for e in errors):
        decision = "FAIL_IDENTIFIER_OR_SELECTION_RULE"
    elif any(e.startswith("ERR_TOTAL_MISMATCH") for e in errors):
        decision = "FAIL_TOTAL_MISMATCH"
    else:
        decision = "FAIL_INPUT_SHAPE"

    if SCHEMA_FAMILY in json.dumps([bd, cvr, err]):
        warnings.append("minimal_projection_only_not_full_nist_cdf_conformance")

    return {
        "archive_version": VERSION,
        "report_id": f"CDF-EXPORT-REPLAY-rev{REV}",
        "generated_at": release_date(ROOT) + "T00:00:00Z",
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_full_nist_conformance_claim": True,
        "decision": decision,
        "adapter_scope": "Parses a small TES-CDF-MINIMAL-PROJECTION-v1 fixture aligned to NIST BD/CVR/ERR identifiers; not a full NIST CDF parser, not the NIST CDF Test Method, and not live election evidence.",
        "standards_alignment": [
            "NIST SP 1500-20 Ballot Definition CDF",
            "NIST SP 1500-103 Cast Vote Records CDF",
            "NIST SP 1500-100r2 Election Results Reporting CDF",
            "NIST GCR 24-058 CDF implementation guidance",
        ],
        "inputs": [
            {"role": "ballot_definition", "path": rel(bd_path), "sha256": bd_digest, "size_bytes": bd_path.stat().st_size, "cdf_name": _string_id(bd.get("cdf_name"))},
            {"role": "cast_vote_records", "path": rel(cvr_path), "sha256": cvr_digest, "size_bytes": cvr_path.stat().st_size, "cdf_name": _string_id(cvr.get("cdf_name"))},
            {"role": "election_results", "path": rel(err_path), "sha256": err_digest, "size_bytes": err_path.stat().st_size, "cdf_name": _string_id(err.get("cdf_name"))},
        ],
        "counts": {
            "contest_count": contest_count,
            "option_count": option_count,
            "cvr_record_count": cvr_record_count,
            "reporting_unit_count": sum(1 for contests in bd_index["unit_contests"].values() if contests),
            "total_cvr_selections": total_selections,
            "comparison_row_count": len(comparison_rows),
            "matched_comparison_row_count": matched_rows,
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "mapping_manifest_path": rel(MANIFEST_OUT),
        "mapping_manifest_sha256": digest_json_value(manifest),
        "canonical_results_object_path": rel(CRO_OUT),
        "canonical_results_object_sha256": digest_json_value(cro),
        "cro_hash": cro.get("cro_hash"),
        "comparison_rows": comparison_rows,
        "errors": errors,
        "warnings": warnings,
        "canonical_results_object": cro,
        "cdf_mapping_manifest": manifest,
        "boundary": "Synthetic adapter replay only; not full NIST CDF conformance, not live jurisdiction export evidence, not certification, not outcome proof, not current voter instruction, and not legal advice.",
        "refactor_audit": {
            "status": "PASS",
            "replaces": "pure prose CDF mapping claim for the Example County synthetic path",
            "new_executable_surface": "tools/cdf_export_replay.py plus scripts/check_cdf_export_replay.py",
            "negative_controls": [
                "artifacts/test-vectors/cdf-replay/election-results-total-mismatch.json",
                "artifacts/test-vectors/cdf-replay/cast-vote-records-unknown-option.json",
                "artifacts/test-vectors/cdf-replay/cast-vote-records-overvote.json",
            ],
        },
    }


def public_text(report: dict[str, Any]) -> str:
    lines = [
        "# CDF export replay status",
        "",
        "**Synthetic replay only. This is not live election evidence and not a full NIST CDF conformance result.**",
        "",
        f"Archive version: `{report['archive_version']}`  ",
        f"Decision: `{report['decision']}`  ",
        f"CRO hash: `{report['cro_hash']}`",
        "",
        "The replay recomputes published option totals from the synthetic CVR fixture by reporting unit and compares those precinct-level totals to the synthetic election-results fixture using identifiers supplied by the synthetic ballot-definition fixture.",
        "",
        f"{report['archive_version']} also ships `public-cdf-independent-verifier.md` and `cdf-independent-replay-verifier-rev{str(report['archive_version']).removeprefix('v').zfill(4)}.json` as a separate synthetic transcript. That second path does not convert this fixture into full NIST conformance or live jurisdiction evidence.",
        "",
        "## Counts",
        "",
        f"- Contests: `{report['counts']['contest_count']}`",
        f"- Options: `{report['counts']['option_count']}`",
        f"- CVR records: `{report['counts']['cvr_record_count']}`",
        f"- Reporting units: `{report['counts'].get('reporting_unit_count')}`",
        f"- Comparison rows: `{report['counts']['comparison_row_count']}`",
        f"- Errors: `{report['counts']['error_count']}`",
        "",
        "## Boundary",
        "",
        "This fixture is a minimal ID-replay bridge for the mission kernel. It is not a complete parser for NIST BD, CVR, ERR, VRI, or EEL formats; it is not the NIST CDF Test Method; it does not prove a real election outcome; and it does not authorize live pilot, public release, production signing, current voter instruction, certification, or legal reliance.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: dict[str, Any]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    CRO_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({k: v for k, v in report.items() if k not in {"canonical_results_object", "cdf_mapping_manifest"}}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    MANIFEST_OUT.write_text(json.dumps(report["cdf_mapping_manifest"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CRO_OUT.write_text(json.dumps(report["canonical_results_object"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PUBLIC_MD.write_text(public_text(report), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bd", type=Path, default=DEFAULT_BD, help="minimal ballot definition projection JSON")
    ap.add_argument("--cvr", type=Path, default=DEFAULT_CVR, help="minimal CVR projection JSON")
    ap.add_argument("--err", type=Path, default=DEFAULT_ERR, help="minimal election-results projection JSON")
    ap.add_argument("--write", action="store_true", help="write current report, mapping manifest, CRO, and public summary")
    ap.add_argument("--json", action="store_true", help="print full JSON report including CRO and mapping manifest")
    args = ap.parse_args()

    report = build_report(args.bd, args.cvr, args.err)
    if args.write and not report["errors"]:
        write_outputs(report)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        print(f"decision={report['decision']} cvr_records={report['counts']['cvr_record_count']} errors={report['counts']['error_count']} version={VERSION}")
    return 0 if not report["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
