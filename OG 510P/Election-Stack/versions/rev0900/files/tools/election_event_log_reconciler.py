#!/usr/bin/env python3
"""Verify the synthetic Example County election-event chain.

The CDF replay and ballot-accounting tools prove that selected exported bytes can
be recomputed.  They do not, by themselves, prove that the generated evidence
objects are chained in time or that a public closeout packet names the exact
artifact bytes it depends on.

This tool builds and verifies a deliberately small Election Event Log style
projection for the synthetic Example County fixture.  It is not a full NIST EEL
parser, not the NIST CDF Test Method, not live custody evidence, not
certification, not outcome proof, not current voter instruction, and not legal
advice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)
CDF_DIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "cdf"
DEFAULT_EVENT_LOG = CDF_DIR / "election-event-log-minimal.json"
REPORT = ROOT / "artifacts" / "reports" / f"election-event-log-reconciliation-rev{REV}.json"
PUBLIC = CDF_DIR / "public-election-event-log-reconciliation.md"
SCHEMA_FAMILY = "TES-ELECTION-EVENT-LOG-MINIMAL-v1"
PASS_DECISION = "SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL"
FAIL_DECISION = "FAIL_EVENT_LOG_CHAIN_RECONCILIATION"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
BOUNDARY = (
    "Synthetic election-event-chain reconciliation only; not live Election Event Log evidence, "
    "not full NIST EEL/CDF conformance, not the NIST CDF Test Method, not certification, "
    "not outcome proof, not current voter instruction, and not legal advice."
)
NON_CLAIMS = [
    "not_live_election_event_log_evidence",
    "not_full_nist_eel_or_cdf_conformance",
    "not_nist_cdf_test_method",
    "not_certification",
    "not_outcome_proof",
    "not_current_voter_instruction",
    "not_legal_advice",
]
REQUIRED_ROLES = [
    "ballot_definition",
    "cast_vote_records",
    "election_results",
    "ballot_accounting",
    "cdf_mapping_manifest",
    "canonical_results_object",
    "cdf_primary_replay_report",
    "cdf_independent_replay_report",
    "ballot_accounting_reconciliation_report",
    "public_replay_boundary",
    "public_independent_boundary",
    "public_accounting_boundary",
]


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest_json(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def event_hash(event: dict[str, Any]) -> str:
    material = {k: v for k, v in event.items() if k != "event_hash"}
    return digest_json(material)


def parse_time(raw: Any, errors: list[str], event_id: str) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        errors.append(f"EVENT_TIME_MISSING:{event_id}")
        return None
    try:
        value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"EVENT_TIME_INVALID:{event_id}:{text}")
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def safe_artifact_path(raw: Any) -> tuple[Path | None, str]:
    rel_path = str(raw or "").strip()
    if not rel_path:
        return None, "missing"
    p = Path(rel_path)
    if p.is_absolute() or ".." in p.parts or any(part in {"", "."} for part in p.parts):
        return None, f"unsafe:{rel_path}"
    return ROOT / rel_path, rel_path


def artifact_specs() -> list[tuple[str, str, str, str]]:
    # (event_type, artifact_role, relative path, synthetic event time)
    return [
        ("BALLOT_DEFINITION_CAPTURED", "ballot_definition", "artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-definition-minimal.json", "2026-11-03T21:00:00Z"),
        ("CVR_EXPORT_CAPTURED", "cast_vote_records", "artifacts/examples/example_county_2026_municipal_pilot/cdf/cast-vote-records-minimal.json", "2026-11-03T23:00:00Z"),
        ("ELECTION_RESULTS_EXPORT_CAPTURED", "election_results", "artifacts/examples/example_county_2026_municipal_pilot/cdf/election-results-minimal.json", "2026-11-03T23:30:00Z"),
        ("BALLOT_ACCOUNTING_LEDGER_CAPTURED", "ballot_accounting", "artifacts/examples/example_county_2026_municipal_pilot/cdf/ballot-accounting-minimal.json", "2026-11-03T23:45:00Z"),
        ("CDF_MAPPING_MANIFEST_EMITTED", "cdf_mapping_manifest", "artifacts/examples/example_county_2026_municipal_pilot/cdf/cdf-mapping-manifest.json", "2026-11-03T23:50:00Z"),
        ("CANONICAL_RESULTS_OBJECT_EMITTED", "canonical_results_object", "artifacts/examples/example_county_2026_municipal_pilot/cdf/canonical-results-object-from-cdf.json", "2026-11-03T23:51:00Z"),
        ("PRIMARY_CDF_REPLAY_REPORT_EMITTED", "cdf_primary_replay_report", f"artifacts/reports/cdf-export-replay-report-rev{REV}.json", "2026-11-03T23:52:00Z"),
        ("INDEPENDENT_CDF_REPLAY_REPORT_EMITTED", "cdf_independent_replay_report", f"artifacts/reports/cdf-independent-replay-verifier-rev{REV}.json", "2026-11-03T23:53:00Z"),
        ("BALLOT_ACCOUNTING_RECONCILIATION_EMITTED", "ballot_accounting_reconciliation_report", f"artifacts/reports/ballot-accounting-reconciliation-rev{REV}.json", "2026-11-03T23:54:00Z"),
        ("PUBLIC_REPLAY_BOUNDARY_PUBLISHED", "public_replay_boundary", "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-cdf-export-replay.md", "2026-11-03T23:55:00Z"),
        ("PUBLIC_INDEPENDENT_BOUNDARY_PUBLISHED", "public_independent_boundary", "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-cdf-independent-verifier.md", "2026-11-03T23:56:00Z"),
        ("PUBLIC_ACCOUNTING_BOUNDARY_PUBLISHED", "public_accounting_boundary", "artifacts/examples/example_county_2026_municipal_pilot/cdf/public-ballot-accounting-reconciliation.md", "2026-11-03T23:57:00Z"),
    ]


def build_event_log() -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    previous = "GENESIS"
    for idx, (event_type, role, path, event_time) in enumerate(artifact_specs(), start=1):
        target = ROOT / path
        if not target.exists():
            raise SystemExit(f"cannot build event log; missing {path}")
        ev = {
            "event_id": f"EEL-{REV}-{idx:03d}",
            "sequence_number": idx,
            "event_time": event_time,
            "event_type": event_type,
            "actor_role": "synthetic release generator",
            "artifact_role": role,
            "artifact_path": path,
            "artifact_sha256": digest_file(target),
            "previous_event_hash": previous,
            "non_claims": NON_CLAIMS,
        }
        ev["event_hash"] = event_hash(ev)
        previous = ev["event_hash"]
        events.append(ev)
    log: dict[str, Any] = {
        "schema_family": SCHEMA_FAMILY,
        "election_id": "example-county-2026-municipal",
        "jurisdiction": "Example County",
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "generated_at": release_date(ROOT) + "T00:00:00Z",
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_full_nist_eel_or_cdf_conformance_claim": True,
        "no_nist_cdf_test_method_claim": True,
        "no_certification_claim": True,
        "no_outcome_proof_claim": True,
        "boundary": BOUNDARY,
        "required_artifact_roles": REQUIRED_ROLES,
        "events": events,
    }
    log["event_log_hash"] = digest_json({k: v for k, v in log.items() if k != "event_log_hash"})
    return log


def build_report(event_log_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        event_log = load_json(event_log_path)
    except Exception as exc:
        event_log = {}
        errors.append(f"EVENT_LOG_JSON_LOAD_FAILED:{exc}")
    if not isinstance(event_log, dict):
        event_log = {}
        errors.append("EVENT_LOG_ROOT_NOT_OBJECT")

    if event_log.get("schema_family") != SCHEMA_FAMILY:
        errors.append("EVENT_LOG_SCHEMA_FAMILY_UNSUPPORTED")
    if event_log.get("archive_version") != VERSION:
        errors.append(f"EVENT_LOG_ARCHIVE_VERSION_MISMATCH:{event_log.get('archive_version')}!={VERSION}")
    for flag in [
        "synthetic_only",
        "no_live_deployment_claim",
        "no_full_nist_eel_or_cdf_conformance_claim",
        "no_nist_cdf_test_method_claim",
        "no_certification_claim",
        "no_outcome_proof_claim",
    ]:
        if event_log.get(flag) is not True:
            errors.append(f"EVENT_LOG_BOUNDARY_FLAG_MISSING:{flag}")

    events_raw = event_log.get("events")
    if not isinstance(events_raw, list):
        events_raw = []
        errors.append("EVENT_LOG_EVENTS_NOT_ARRAY")

    previous_hash = "GENESIS"
    previous_time: datetime | None = None
    seen_ids: set[str] = set()
    seen_roles: set[str] = set()
    rows: list[dict[str, Any]] = []
    digest_match_count = 0
    chain_match_count = 0
    timestamp_ok_count = 0

    for idx, event_any in enumerate(events_raw, start=1):
        if not isinstance(event_any, dict):
            errors.append(f"EVENT_NOT_OBJECT:{idx}")
            continue
        event = event_any
        event_id = str(event.get("event_id") or f"<event-{idx}>")
        role = str(event.get("artifact_role") or "").strip()
        seen_roles.add(role)
        if event_id in seen_ids:
            errors.append(f"EVENT_DUPLICATE_ID:{event_id}")
        seen_ids.add(event_id)
        if int(event.get("sequence_number") or -1) != idx:
            errors.append(f"EVENT_SEQUENCE_MISMATCH:{event_id}:expected={idx}:got={event.get('sequence_number')}")
        expected_previous_hash = previous_hash
        previous_hash_ok = event.get("previous_event_hash") == expected_previous_hash
        if not previous_hash_ok:
            errors.append(f"EVENT_PREVIOUS_HASH_MISMATCH:{event_id}")
        actual_event_hash = event_hash(event)
        event_hash_ok = event.get("event_hash") == actual_event_hash
        if not event_hash_ok:
            errors.append(f"EVENT_HASH_MISMATCH:{event_id}")
        else:
            chain_match_count += 1
        previous_hash = actual_event_hash

        value_time = parse_time(event.get("event_time"), errors, event_id)
        if value_time is not None:
            if previous_time is not None and value_time < previous_time:
                errors.append(f"EVENT_TIMESTAMP_REGRESSION:{event_id}")
            else:
                timestamp_ok_count += 1
            previous_time = value_time

        target, safe_detail = safe_artifact_path(event.get("artifact_path"))
        exists = bool(target and target.exists())
        actual_digest = digest_file(target) if exists and target else ""
        declared = str(event.get("artifact_sha256") or "")
        digest_ok = bool(exists and DIGEST_RE.fullmatch(declared) and declared == actual_digest)
        if not exists:
            errors.append(f"EVENT_ARTIFACT_MISSING:{event_id}:{safe_detail}")
        elif not DIGEST_RE.fullmatch(declared):
            errors.append(f"EVENT_ARTIFACT_DIGEST_SHAPE_INVALID:{event_id}:{declared}")
        elif declared != actual_digest:
            errors.append(f"EVENT_ARTIFACT_DIGEST_MISMATCH:{event_id}:{safe_detail}")
        else:
            digest_match_count += 1
        rows.append({
            "event_id": event_id,
            "sequence_number": idx,
            "event_type": str(event.get("event_type") or ""),
            "artifact_role": role,
            "artifact_path": str(event.get("artifact_path") or ""),
            "declared_sha256": declared,
            "actual_sha256": actual_digest,
            "digest_match": digest_ok,
            "event_hash_match": event_hash_ok,
            "previous_hash_match": previous_hash_ok,
            "computed_event_hash": actual_event_hash,
        })

    missing_roles = sorted(set(REQUIRED_ROLES) - {r for r in seen_roles if r})
    for role in missing_roles:
        errors.append(f"EVENT_REQUIRED_ROLE_MISSING:{role}")

    declared_log_hash = str(event_log.get("event_log_hash") or "")
    computed_log_hash = digest_json({k: v for k, v in event_log.items() if k != "event_log_hash"})
    if declared_log_hash != computed_log_hash:
        errors.append("EVENT_LOG_HASH_MISMATCH")

    if not events_raw:
        errors.append("EVENT_LOG_EMPTY")
    if "not full nist" not in str(event_log.get("boundary") or "").lower():
        warnings.append("boundary_should_explicitly_state_not_full_nist_conformance")

    decision = PASS_DECISION if not errors else FAIL_DECISION
    return {
        "archive_version": VERSION,
        "release_date": release_date(ROOT),
        "generated_at": release_date(ROOT) + "T00:00:00Z",
        "report_id": f"ELECTION-EVENT-LOG-RECONCILIATION-rev{REV}",
        "decision": decision,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_live_election_event_log_claim": True,
        "no_full_nist_eel_or_cdf_conformance_claim": True,
        "no_nist_cdf_test_method_claim": True,
        "no_certification_claim": True,
        "no_outcome_proof_claim": True,
        "boundary": BOUNDARY,
        "inputs": [
            {"role": "election_event_log", "path": rel(event_log_path), "sha256": digest_file(event_log_path) if event_log_path.exists() else "missing"}
        ],
        "counts": {
            "event_count": len(events_raw),
            "required_role_count": len(REQUIRED_ROLES),
            "missing_required_role_count": len(missing_roles),
            "artifact_digest_match_count": digest_match_count,
            "event_hash_match_count": chain_match_count,
            "timestamp_order_ok_count": timestamp_ok_count,
            "error_count": len(errors),
            "warning_count": len(warnings),
        },
        "event_log_hash": declared_log_hash,
        "computed_event_log_hash": computed_log_hash,
        "rows": rows,
        "errors": errors,
        "warnings": warnings,
        "risk_burndown": {
            "burned_down": "K02/K03 synthetic evidence now has a chronological event-chain witness that binds BD/CVR/ERR/accounting inputs to replay, independent-verifier, CRO, and public-boundary outputs by digest.",
            "still_missing": "Jurisdiction-generated EEL/CDF exports, live custody transfer/seal/access records, local authority approval, and outside reviewer transcripts.",
            "negative_controls": [
                "artifacts/test-vectors/election-event-log/election-event-log-broken-prev-hash.json",
                "artifacts/test-vectors/election-event-log/election-event-log-digest-mismatch.json",
                "artifacts/test-vectors/election-event-log/election-event-log-timestamp-regression.json",
                "artifacts/test-vectors/election-event-log/election-event-log-missing-required-role.json",
            ],
        },
    }


def public_summary(report: dict[str, Any]) -> str:
    counts = report.get("counts") or {}
    return "\n".join([
        "# Synthetic election-event log reconciliation",
        "",
        f"Archive version: `{report['archive_version']}`  ",
        f"Report: `artifacts/reports/election-event-log-reconciliation-rev{REV}.json`  ",
        f"Decision: `{report['decision']}`  ",
        "",
        "This synthetic check binds the Example County CDF replay and ballot-accounting outputs into a chronological event chain with per-artifact SHA-256 digests.",
        "",
        "## Counts",
        "",
        f"- Events checked: `{counts.get('event_count')}`.",
        f"- Required artifact roles: `{counts.get('required_role_count')}`.",
        f"- Missing required roles: `{counts.get('missing_required_role_count')}`.",
        f"- Artifact digest matches: `{counts.get('artifact_digest_match_count')}`.",
        f"- Errors: `{counts.get('error_count')}`.",
        "",
        "## Boundary",
        "",
        "This is not live Election Event Log evidence, not full NIST EEL or CDF conformance, not the NIST CDF Test Method, not certification, not outcome proof, not current voter instruction, and not legal advice.",
        "It does not authorize live pilot use and does not replace custody transfer/seal records, access logs, audit, recount, canvass, certification, retention, public-records review, or counsel review.",
        "",
    ])


def write_outputs() -> dict[str, Any]:
    DEFAULT_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    event_log = build_event_log()
    DEFAULT_EVENT_LOG.write_text(json.dumps(event_log, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    report = build_report(DEFAULT_EVENT_LOG)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    PUBLIC.write_text(public_summary(report), encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify synthetic election-event log chain")
    ap.add_argument("--event-log", type=Path, default=DEFAULT_EVENT_LOG)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = write_outputs() if args.write else build_report(args.event_log)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        counts = report.get("counts") or {}
        print(f"{report['decision']}: events={counts.get('event_count')} errors={counts.get('error_count')} version={VERSION}")
    return 0 if report.get("decision") == PASS_DECISION else 2


if __name__ == "__main__":
    raise SystemExit(main())
