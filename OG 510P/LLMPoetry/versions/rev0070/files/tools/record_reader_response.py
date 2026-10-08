#!/usr/bin/env python3
"""Validate and optionally append a real non-identifying reader response.

This tool is intentionally narrow. It helps the cube record local editorial
reader pressure for P0002-D010 without turning that response into admission,
evidence-ready status, or human-subjects/generalizable research proof.

Rev0040 hardens the intake path further: blank responses are rejected,
provenance fields are assigned by the tool rather than accepted from input, a
boundary acknowledgement is required before any append, and duplicate response
content is rejected by fingerprint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONEISH_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
FORBIDDEN_KEYS = {
    "name", "full_name", "first_name", "last_name", "email", "phone", "address",
    "location", "city", "state", "country", "zip", "postal_code", "employer",
    "organization", "school", "age", "birthdate", "gender", "race", "ethnicity",
    "demographic", "bio", "biography", "social_media", "ip", "user_agent"
}
RESERVED_INPUT_KEYS = {
    "response_id", "recorded_at", "recorded_by", "source", "clean_first_response",
    "protocol_deviation_notes", "does_not_create_admission", "does_not_create_evidence_status",
    "local_editorial_pressure_only", "template_only", "not_a_response", "created_at",
    "updated_at", "updated_by_tool", "schema", "status", "response_count", "responses",
    "content_fingerprint", "response_fingerprint", "fingerprint"
}
REQUIRED_FIELDS = {
    "disclosure_seen_before_poem",
    "source_packet_opened_before_first_response",
    "boundary_acknowledged",
    "keep_reject_uncertain",
    "strongest_line_or_phrase",
    "weakest_line_or_phrase",
    "disclosure_delta",
    "body_works_without_source_packet",
    "documentation_doing_poem_work",
    "revision_instruction",
}
TEXT_FIELDS = (
    "strongest_line_or_phrase",
    "weakest_line_or_phrase",
    "documentation_doing_poem_work",
    "revision_instruction",
)
ALLOWED_DECISIONS = {"keep", "reject", "uncertain"}
ALLOWED_DISCLOSURE_DELTA = {"improved", "weakened", "confounded", "merely_explained", "other"}
LOG_PATH = Path("anthology/candidates/P0002-D010_reader_responses.json")
PACKET_PATH = Path("anthology/candidates/P0002-D010_disclosed_reader_packet.json")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def flatten_strings(obj) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return "\n".join(flatten_strings(v) for v in obj.values())
    if isinstance(obj, list):
        return "\n".join(flatten_strings(v) for v in obj)
    return str(obj)


def normalized_text(value) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def validate_response(response: dict) -> tuple[bool, list[str], dict]:
    errors: list[str] = []
    if not isinstance(response, dict):
        return False, ["response must be a JSON object"], {}

    normalized = deepcopy(response)
    keys = set(response)
    missing = sorted(REQUIRED_FIELDS - keys)
    if missing:
        errors.append(f"missing required fields: {missing}")
    bad_keys = sorted(keys & FORBIDDEN_KEYS)
    if bad_keys:
        errors.append(f"forbidden personal-data keys present: {bad_keys}")
    reserved = sorted(keys & RESERVED_INPUT_KEYS)
    if reserved:
        errors.append(f"reserved tool-managed keys present in input: {reserved}")

    dumped = json.dumps(response, ensure_ascii=False)
    dumped_low = dumped.lower()
    if EMAIL_RE.search(dumped):
        errors.append("email-like text detected")
    if PHONEISH_RE.search(dumped):
        errors.append("phone-number-like text detected")
    for forbidden in ("admitted", "evidence-ready", "evidence_candidate", "publishable proof", "human-authored"):
        if forbidden in dumped_low:
            errors.append(f"admission/evidence/deception wording detected: {forbidden}")

    for field in ("disclosure_seen_before_poem", "source_packet_opened_before_first_response", "body_works_without_source_packet", "boundary_acknowledged"):
        if field in response and not isinstance(response[field], bool):
            errors.append(f"{field} must be boolean")
    if response.get("boundary_acknowledged") is not True:
        errors.append("boundary_acknowledged must be true before intake")

    decision = normalized_text(response.get("keep_reject_uncertain", "")).lower()
    if decision not in ALLOWED_DECISIONS:
        errors.append(f"keep_reject_uncertain must be one of {sorted(ALLOWED_DECISIONS)}")
    delta = normalized_text(response.get("disclosure_delta", "")).lower().replace(" ", "_")
    if delta not in ALLOWED_DISCLOSURE_DELTA:
        errors.append(f"disclosure_delta must be one of {sorted(ALLOWED_DISCLOSURE_DELTA)}")

    for field in TEXT_FIELDS:
        if field in response and not isinstance(response[field], str):
            errors.append(f"{field} must be a string")
        elif field in response:
            cleaned = normalized_text(response[field])
            normalized[field] = cleaned
            if len(cleaned) < 2:
                errors.append(f"{field} must not be blank")

    text_blob = flatten_strings(response)
    if len(text_blob) > 6000:
        errors.append("response text is longer than the local editorial cap")

    normalized["keep_reject_uncertain"] = decision
    normalized["disclosure_delta"] = delta
    normalized["clean_first_response"] = bool(
        response.get("disclosure_seen_before_poem") is True
        and response.get("source_packet_opened_before_first_response") is False
        and response.get("boundary_acknowledged") is True
    )
    normalized.setdefault(
        "protocol_deviation_notes",
        "" if normalized["clean_first_response"] else "Disclosure/source-order/boundary deviation; keep as editorial pressure only.",
    )
    normalized.setdefault("quality_claims", [])
    if normalized.get("quality_claims") != []:
        errors.append("quality_claims must be empty")
    return not errors, errors, normalized



def response_fingerprint(response: dict) -> str:
    """Stable fingerprint of reader-supplied response content only."""
    payload = {
        key: response.get(key)
        for key in sorted(REQUIRED_FIELDS | {"quality_claims"})
        if key in response
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def existing_fingerprints(log: dict) -> set[str]:
    fps: set[str] = set()
    for response in log.get("responses", []) if isinstance(log.get("responses"), list) else []:
        if not isinstance(response, dict):
            continue
        fp = response.get("content_fingerprint")
        if isinstance(fp, str) and fp:
            fps.add(fp)
        else:
            # Backward compatibility for any pre-fingerprint response records.
            fps.add(response_fingerprint(response))
    return fps

def next_response_id(log: dict) -> str:
    existing = log.get("responses", []) if isinstance(log.get("responses"), list) else []
    return f"R-P0002-D010-{len(existing) + 1:04d}"


def append_response(root: Path, input_path: Path, dry_run: bool, recorded_at: str | None) -> dict:
    response = load_json(input_path)
    ok, errors, normalized = validate_response(response)
    report = {"ok": ok, "input": str(input_path), "errors": errors, "would_write": not dry_run and ok}
    if not ok:
        return report

    log_path = root / LOG_PATH
    log = load_json(log_path)
    fingerprint = response_fingerprint(normalized)
    if fingerprint in existing_fingerprints(log):
        report["ok"] = False
        report["errors"] = ["duplicate response content fingerprint already exists in log"]
        report["would_write"] = False
        report["content_fingerprint"] = fingerprint
        return report

    normalized["response_id"] = next_response_id(log)
    normalized["recorded_at"] = recorded_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    normalized["source"] = "real_reader_response_nonidentifying_local_editorial_pressure"
    normalized["content_fingerprint"] = fingerprint
    normalized["does_not_create_admission"] = True
    normalized["does_not_create_evidence_status"] = True
    normalized["local_editorial_pressure_only"] = True

    if not dry_run:
        responses = log.setdefault("responses", [])
        responses.append(normalized)
        log["response_count"] = len(responses)
        log["status"] = "real_nonidentifying_responses_recorded_not_evidence" if responses else log.get("status")
        log["updated_at"] = normalized["recorded_at"]
        log["updated_by_tool"] = "tools/record_reader_response.py"
        log.setdefault("quality_claims", [])
        dump_json(log_path, log)
        packet_path = root / PACKET_PATH
        packet = load_json(packet_path)
        packet["responses_recorded"] = log["response_count"]
        packet["status"] = "calibrated_disclosed_reader_packet_responses_logged_not_admitted_not_evidence"
        packet.setdefault("quality_claims", [])
        dump_json(packet_path, packet)
    report["normalized_response"] = normalized
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate and optionally append a P0002-D010 reader response")
    ap.add_argument("--root", default=".")
    ap.add_argument("--input", required=True, help="Path to a JSON response object")
    ap.add_argument("--dry-run", action="store_true", help="Validate only; do not append to the response log")
    ap.add_argument("--recorded-at", help="Explicit ISO timestamp for deterministic archival use")
    args = ap.parse_args()
    report = append_response(Path(args.root), Path(args.input), args.dry_run, args.recorded_at)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
