#!/usr/bin/env python3
"""Build a mission-kernel evidence submission from operator-supplied records.

This tool is deliberately narrow: it hashes records that live outside the
published synthetic archive and emits a submission JSON for
``mission_kernel_live_evidence_intake.py --submission``. It does not validate
that a jurisdiction is authorized, does not publish the source records, and does
not turn a drill into live election evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from example_county_common import ROOT
from mission_kernel_common import (
    ALLOWED_SOURCE_MODES,
    BOUNDARY,
    DRILL_EVIDENCE_SOURCE_MODE,
    LIVE_EVIDENCE_SOURCE_MODE,
    PUBLIC_BOUNDARY_VALUES,
    REDACTION_STATUS_VALUES,
    is_governed_synthetic_locator,
    source_mode_is_external_record,
)
from mission_kernel_live_workqueue import build_workqueue
from release_context import archive_version, release_date

VERSION = archive_version(ROOT)
REV = VERSION.removeprefix("v").zfill(4)


def fingerprint_file(path: Path) -> tuple[str, int]:
    """Hash one stable regular-file snapshot and return (digest, byte_count).

    Digesting and sizing through one open descriptor closes the prior stat/hash
    race.  A before/after fstat check fails closed if the source changes while it
    is being read.
    """

    with path.open("rb") as f:
        before = os.fstat(f.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"file_path is not a regular file: {path}")
        h = hashlib.sha256()
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
        after = os.fstat(f.fileno())
    stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable_fields):
        raise ValueError(f"file_path changed while being hashed: {path}")
    return "sha256:" + h.hexdigest(), int(after.st_size)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def ensure_external_file(raw: Any) -> Path:
    if not raw:
        raise ValueError("evidence object missing file_path")
    path = Path(str(raw)).expanduser()
    if not path.is_absolute():
        path = path.resolve()
    else:
        path = path.resolve()
    root = ROOT.resolve()
    if _is_relative_to(path, root):
        raise ValueError(f"file_path is inside governed synthetic archive and cannot satisfy operator evidence: {path}")
    if not path.is_file():
        raise ValueError(f"file_path does not exist or is not a file: {path}")
    return path


def _parse_utc_timestamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        return None
    return parsed


def clean_locator(obj: dict[str, Any], digest: str) -> str:
    locator = str(obj.get("record_locator") or obj.get("local_path_or_record_locator") or "").strip()
    if not locator:
        # Content-address the default locator; basenames collide and can leak
        # operator naming conventions.
        locator = f"external-record:{digest}"
    normalized = locator.replace("\\", "/")
    lower = normalized.lower()
    if normalized.startswith(("/", "~/", "../", "./")) or (len(normalized) >= 3 and normalized[1:3] in {":/", ":\\"}):
        raise ValueError("record_locator must be an opaque external locator, not a local filesystem path")
    if lower.startswith(("file:", "path:")) or ":" not in normalized:
        raise ValueError("record_locator must use an explicit non-file scheme")
    if is_governed_synthetic_locator(normalized):
        raise ValueError(f"record_locator points into governed synthetic archive: {locator}")
    return locator


def default_common_fields(plan: dict[str, Any]) -> dict[str, str]:
    supplied = plan.get("common_fields") if isinstance(plan.get("common_fields"), dict) else {}
    fields = {
        "jurisdiction_name": "",
        "election_id": "",
        "election_date": "",
        "local_authority_contact_role": "",
        "authority_scope_record_sha256": "",
        "evidence_capture_datetime_utc": "",
        "redaction_review_status": "",
        "public_release_approval_status": "",
        "records_retention_rule_ref": "",
    }
    for k in fields:
        fields[k] = str(supplied.get(k) or "")
    return fields


def normalize_source_mode(raw: Any, fallback: str) -> str:
    mode = str(raw or fallback).strip()
    if mode not in ALLOWED_SOURCE_MODES:
        raise ValueError(f"source_mode {mode!r} is not allowed")
    if not source_mode_is_external_record(mode):
        raise ValueError(f"source_mode {mode!r} is not an operator-supplied record mode for this submitter")
    return mode


def validate_review_fields(obj: dict[str, Any], *, work_item_id: str) -> None:
    redaction = str(obj.get("redaction_status") or "").strip()
    boundary = str(obj.get("public_private_boundary") or "").strip()
    approving_role = str(obj.get("approving_role") or "").strip()
    retention_ref = str(obj.get("records_retention_rule_ref") or "").strip()
    captured_at = str(obj.get("captured_at_utc") or "").strip()
    if not approving_role:
        raise ValueError(f"{work_item_id}: evidence object missing approving_role")
    if redaction not in REDACTION_STATUS_VALUES or redaction in {"", "NOT_REVIEWED"}:
        raise ValueError(f"{work_item_id}: redaction_status must be a completed allowed value")
    if boundary not in PUBLIC_BOUNDARY_VALUES or not boundary:
        raise ValueError(f"{work_item_id}: public_private_boundary must be an allowed non-empty value")
    allowed_pairs = {
        "APPROVED_PUBLIC": {"PUBLIC_RELEASED", "REDACTED_PUBLIC_DERIVATIVE"},
        "APPROVED_PRIVATE": {"PRIVATE_SOURCE_RECORD"},
        "WITHHELD": {"WITHHELD_LEGAL_OR_PRIVACY"},
    }
    if boundary not in allowed_pairs.get(redaction, set()):
        raise ValueError(f"{work_item_id}: redaction_status {redaction!r} conflicts with public_private_boundary {boundary!r}")
    if not retention_ref:
        raise ValueError(f"{work_item_id}: evidence object missing records_retention_rule_ref")
    if _parse_utc_timestamp(captured_at) is None:
        raise ValueError(f"{work_item_id}: captured_at_utc must be an explicit UTC RFC3339 timestamp")


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def _validate_live_common_fields(common: dict[str, str]) -> None:
    required = [
        "jurisdiction_name",
        "election_id",
        "election_date",
        "local_authority_contact_role",
        "authority_scope_record_sha256",
        "evidence_capture_datetime_utc",
        "redaction_review_status",
        "public_release_approval_status",
        "records_retention_rule_ref",
    ]
    missing = [field for field in required if not str(common.get(field) or "").strip()]
    if missing:
        raise ValueError("live submission common_fields missing: " + ", ".join(missing))
    digest = str(common.get("authority_scope_record_sha256") or "").strip().lower()
    if not (digest.startswith("sha256:") and len(digest) == 71 and all(ch in "0123456789abcdef" for ch in digest[7:])):
        raise ValueError("live submission authority_scope_record_sha256 must be sha256:<64hex>")
    if _parse_utc_timestamp(common.get("evidence_capture_datetime_utc")) is None:
        raise ValueError("live submission evidence_capture_datetime_utc must be an explicit UTC RFC3339 timestamp")


def build_submission(plan: dict[str, Any]) -> dict[str, Any]:
    workqueue = build_workqueue()
    rows_by_id = {str(r.get("work_item_id")): r for r in workqueue.get("rows") or [] if isinstance(r, dict)}
    default_mode = normalize_source_mode(plan.get("source_mode"), DRILL_EVIDENCE_SOURCE_MODE)
    submission_id = str(plan.get("submission_id") or f"MK-EVIDENCE-SUBMISSION-rev{REV}-{default_mode}").strip()
    if not submission_id:
        raise ValueError("submission_id must not be empty")

    input_items = plan.get("work_items") or []
    if not isinstance(input_items, list) or not input_items:
        raise ValueError("plan must contain at least one work_items entry")
    if not all(isinstance(item, dict) for item in input_items):
        raise ValueError("each work_items entry must be an object")
    work_item_ids = [str(item.get("work_item_id") or "").strip() for item in input_items]
    duplicate_ids = _duplicates(work_item_ids)
    if duplicate_ids:
        raise ValueError("plan contains duplicate work_item_id values: " + ", ".join(duplicate_ids))

    common_fields = default_common_fields(plan)
    if default_mode == LIVE_EVIDENCE_SOURCE_MODE:
        _validate_live_common_fields(common_fields)

    out_items: list[dict[str, Any]] = []
    for item in input_items:
        work_item_id = str(item.get("work_item_id") or "").strip()
        if work_item_id not in rows_by_id:
            raise ValueError(f"unknown work_item_id {work_item_id!r}")
        row = rows_by_id[work_item_id]
        required = {str(x) for x in row.get("minimum_evidence_classes") or []}
        evidence_objects = item.get("evidence_objects") or []
        if not isinstance(evidence_objects, list) or not evidence_objects:
            raise ValueError(f"{work_item_id}: evidence_objects must contain at least one object")
        if not all(isinstance(obj, dict) for obj in evidence_objects):
            raise ValueError(f"{work_item_id}: evidence object must be an object")
        classes = [str(obj.get("evidence_class") or "").strip() for obj in evidence_objects]
        duplicate_classes = _duplicates(classes)
        if duplicate_classes:
            raise ValueError(f"{work_item_id}: duplicate evidence_class values: {duplicate_classes}")

        out_objects: list[dict[str, Any]] = []
        for obj in evidence_objects:
            cls = str(obj.get("evidence_class") or "").strip()
            if cls not in required:
                raise ValueError(f"{work_item_id}: evidence_class {cls!r} is not required for this item")
            mode = normalize_source_mode(obj.get("source_mode"), default_mode)
            if mode != default_mode:
                raise ValueError(
                    f"{work_item_id}: evidence object source_mode {mode!r} does not match submission source_mode {default_mode!r}"
                )
            path = ensure_external_file(obj.get("file_path"))
            validate_review_fields(obj, work_item_id=work_item_id)
            digest, byte_count = fingerprint_file(path)
            out_obj = {
                "evidence_class": cls,
                "source_mode": mode,
                "record_locator": clean_locator(obj, digest),
                "sha256": digest,
                "byte_count": byte_count,
                "approving_role": str(obj.get("approving_role") or "").strip(),
                "redaction_status": str(obj.get("redaction_status") or "").strip(),
                "public_private_boundary": str(obj.get("public_private_boundary") or "").strip(),
                "records_retention_rule_ref": str(obj.get("records_retention_rule_ref") or "").strip(),
                "captured_at_utc": str(obj.get("captured_at_utc") or "").strip(),
                "notes": str(obj.get("notes") or "").strip(),
            }
            if mode == DRILL_EVIDENCE_SOURCE_MODE:
                out_obj["drill_scope"] = str(
                    obj.get("drill_scope") or "non-production operator drill; not live election evidence"
                ).strip()
            out_objects.append(out_obj)
        out_items.append({
            "work_item_id": work_item_id,
            "blocker_id": row.get("blocker_id"),
            "owner_role": row.get("owner_role"),
            "minimum_evidence_classes": row.get("minimum_evidence_classes") or [],
            "submission_status": "OPERATOR_RECORDS_HASHED_PENDING_INTAKE_VALIDATION",
            "evidence_objects": out_objects,
        })

    synthetic_only = bool(plan.get("synthetic_only", False))
    if default_mode == LIVE_EVIDENCE_SOURCE_MODE and synthetic_only:
        raise ValueError("live source_mode submission must not be marked synthetic_only=true")

    authentication_state = (
        "UNAUTHENTICATED_CANDIDATE_REQUIRES_SIGNED_EVIDENCE_ENVELOPE"
        if default_mode == LIVE_EVIDENCE_SOURCE_MODE
        else "NOT_APPLICABLE_NONPRODUCTION_DRILL"
    )
    decision = (
        "OPERATOR_CANDIDATE_HASHED_AUTHENTICATION_REQUIRED"
        if default_mode == LIVE_EVIDENCE_SOURCE_MODE
        else "OPERATOR_SUBMISSION_HASHED_PENDING_INTAKE_VALIDATION"
    )
    return {
        "archive_version": VERSION,
        "submission_id": submission_id,
        "scenario_id": str(plan.get("scenario_id") or workqueue.get("scenario_id") or ""),
        "workqueue_id": str(plan.get("workqueue_id") or workqueue.get("workqueue_id") or ""),
        "source_mode": default_mode,
        "synthetic_only": synthetic_only,
        "non_production_drill": default_mode == DRILL_EVIDENCE_SOURCE_MODE,
        "no_live_deployment_claim": True,
        "decision": decision,
        "authentication_state": authentication_state,
        "release_date": release_date(ROOT),
        "boundary": BOUNDARY,
        "common_fields": common_fields,
        "work_items": out_items,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Hash external mission-kernel records into an evidence submission JSON")
    ap.add_argument("--plan", type=Path, required=True, help="operator plan JSON with work_items/evidence_objects/file_path entries")
    ap.add_argument("--out", type=Path, help="write submission JSON to this path")
    ap.add_argument("--json", action="store_true", help="print canonical submission JSON to stdout")
    args = ap.parse_args()
    try:
        submission = build_submission(load_json(args.plan))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(submission, sort_keys=True, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    if args.json or not args.out:
        sys.stdout.write(payload)
    else:
        print(f"wrote {args.out} work_items={len(submission['work_items'])} source_mode={submission['source_mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
