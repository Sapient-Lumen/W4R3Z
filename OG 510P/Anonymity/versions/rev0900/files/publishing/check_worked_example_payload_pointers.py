#!/usr/bin/env python3
"""Verify Paper17 worked-example JSON payload pointers.

This is a concrete hot-path refactor guard: the bulky generated JSON files keep
stable logical paths and SHA-256 values, but their bytes may be stored as
mtime-zero gzip payloads behind small pointer files.  The checker fails closed if
any pointer, payload, support-manifest row, or validator resolver drifts.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys
from typing import Any

WORKED_ROOT = pathlib.Path("series/synthesis/paper17_worked_example_receipt_interlock")
ARTIFACT_ROOT = WORKED_ROOT / "artifacts"
SUPPORT_MANIFEST = ARTIFACT_ROOT / "support_manifest.json"
VALIDATOR = WORKED_ROOT / "tools/validate_example.py"
SUPPORT_CHECKER = pathlib.Path("publishing/check_support_manifest_integrity.py")
POINTER_FORMAT = "worked-example-json-payload-pointer-v1"
REQUIRED_LOGICAL_ARTIFACTS = {
    "example_series_spine.json",
    "example_question_routes.json",
    "example_public_request_response_packet_refresh_response_menus.json",
    "example_public_request_response_packet_refresh_response_packet_closure_verdicts.json",
    "example_public_request_response_packet_refresh_response_packets.json",
    "example_successor_challenge_answer_review_menus.json",
    "example_verifier_report.json",
}
MINIMUM_TOTAL_HOT_PATH_SAVED_BYTES = 7_500_000


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def support_rows_by_path(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in manifest.get("files", []):
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            rows[str(row["path"])] = row
    return rows


def check_pointer(root: pathlib.Path, logical_path: str, rows: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    pointer_rel = ARTIFACT_ROOT / logical_path
    pointer_path = root / pointer_rel
    payload_report: dict[str, Any] = {
        "logical_path": logical_path,
        "pointer_path": pointer_rel.as_posix(),
    }
    if not pointer_path.exists():
        return payload_report, [{"category": "pointer_file_missing", "path": pointer_rel.as_posix()}]
    try:
        pointer = load_json(pointer_path)
    except Exception as exc:  # noqa: BLE001
        return payload_report, [{"category": "pointer_json_unreadable", "path": pointer_rel.as_posix(), "error": str(exc)}]
    if not isinstance(pointer, dict):
        return payload_report, [{"category": "pointer_not_object", "path": pointer_rel.as_posix()}]
    if pointer.get("offloaded_payload_pointer") is not True:
        failures.append({"category": "pointer_flag_missing", "path": pointer_rel.as_posix()})
    if pointer.get("pointer_format") != POINTER_FORMAT:
        failures.append({"category": "pointer_format_mismatch", "path": pointer_rel.as_posix(), "actual": pointer.get("pointer_format"), "expected": POINTER_FORMAT})
    if pointer.get("logical_path") != logical_path:
        failures.append({"category": "pointer_logical_path_mismatch", "path": pointer_rel.as_posix(), "actual": pointer.get("logical_path"), "expected": logical_path})
    if pointer.get("encoding") != "gzip-json-utf8-mtime0":
        failures.append({"category": "pointer_encoding_mismatch", "path": pointer_rel.as_posix(), "actual": pointer.get("encoding")})

    payload_rel_raw = str(pointer.get("payload_path", ""))
    payload_rel = ARTIFACT_ROOT / payload_rel_raw
    payload_path = (root / payload_rel).resolve()
    try:
        payload_path.relative_to((root / ARTIFACT_ROOT).resolve())
    except Exception:
        failures.append({"category": "payload_path_escapes_artifact_root", "logical_path": logical_path, "payload_path": payload_rel_raw})
        payload_path = root / "__missing_payload__"
    if not payload_path.exists() or not payload_path.is_file():
        failures.append({"category": "payload_file_missing", "logical_path": logical_path, "payload_path": payload_rel.as_posix()})
        payload_bytes = b""
        logical_bytes = b""
    else:
        payload_bytes = payload_path.read_bytes()
        if sha256_bytes(payload_bytes) != pointer.get("payload_sha256"):
            failures.append({"category": "payload_sha256_mismatch", "logical_path": logical_path, "payload_path": payload_rel.as_posix(), "declared": pointer.get("payload_sha256"), "actual": sha256_bytes(payload_bytes)})
        try:
            logical_bytes = gzip.decompress(payload_bytes)
        except Exception as exc:  # noqa: BLE001
            failures.append({"category": "payload_decompress_failed", "logical_path": logical_path, "payload_path": payload_rel.as_posix(), "error": str(exc)})
            logical_bytes = b""

    logical_sha = sha256_bytes(logical_bytes) if logical_bytes else ""
    if logical_sha and logical_sha != pointer.get("logical_sha256"):
        failures.append({"category": "logical_sha256_mismatch", "logical_path": logical_path, "declared": pointer.get("logical_sha256"), "actual": logical_sha})
    if logical_bytes and len(logical_bytes) != int(pointer.get("logical_bytes", -1)):
        failures.append({"category": "logical_byte_count_mismatch", "logical_path": logical_path, "declared": pointer.get("logical_bytes"), "actual": len(logical_bytes)})
    if logical_bytes:
        try:
            json.loads(logical_bytes.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append({"category": "logical_payload_json_unreadable", "logical_path": logical_path, "error": str(exc)})

    logical_row = rows.get(logical_path, {})
    payload_row = rows.get(payload_rel_raw, {})
    if not logical_row:
        failures.append({"category": "support_manifest_logical_row_missing", "logical_path": logical_path})
    else:
        if logical_row.get("sha256") != pointer.get("logical_sha256"):
            failures.append({"category": "support_manifest_logical_sha_mismatch", "logical_path": logical_path, "manifest": logical_row.get("sha256"), "pointer": pointer.get("logical_sha256")})
        if logical_row.get("storage_path") != payload_rel_raw:
            failures.append({"category": "support_manifest_storage_path_mismatch", "logical_path": logical_path, "manifest": logical_row.get("storage_path"), "pointer": payload_rel_raw})
        if logical_row.get("storage_sha256") != pointer.get("payload_sha256"):
            failures.append({"category": "support_manifest_storage_sha_mismatch", "logical_path": logical_path, "manifest": logical_row.get("storage_sha256"), "pointer": pointer.get("payload_sha256")})
    if not payload_row:
        failures.append({"category": "support_manifest_payload_row_missing", "logical_path": logical_path, "payload_path": payload_rel_raw})
    else:
        if payload_row.get("sha256") != pointer.get("payload_sha256"):
            failures.append({"category": "support_manifest_payload_sha_mismatch", "logical_path": logical_path, "manifest": payload_row.get("sha256"), "pointer": pointer.get("payload_sha256")})
        if payload_row.get("logical_sha256") != pointer.get("logical_sha256"):
            failures.append({"category": "support_manifest_payload_logical_sha_mismatch", "logical_path": logical_path, "manifest": payload_row.get("logical_sha256"), "pointer": pointer.get("logical_sha256")})

    pointer_bytes = pointer_path.stat().st_size
    logical_len = len(logical_bytes)
    payload_len = len(payload_bytes)
    payload_report.update({
        "status": "pass" if not failures else "fail",
        "pointer_bytes": pointer_bytes,
        "logical_bytes": logical_len,
        "payload_bytes": payload_len,
        "logical_sha256": pointer.get("logical_sha256", ""),
        "payload_sha256": pointer.get("payload_sha256", ""),
        "payload_path": payload_rel.as_posix(),
        "hot_path_bytes_saved": max(0, logical_len - pointer_bytes),
        "logical_to_payload_ratio": round(logical_len / payload_len, 3) if payload_len else 0.0,
        "failure_count": len(failures),
    })
    return payload_report, failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    manifest_path = root / SUPPORT_MANIFEST
    if not manifest_path.exists():
        failures.append({"category": "support_manifest_missing", "path": SUPPORT_MANIFEST.as_posix()})
        manifest: dict[str, Any] = {}
    else:
        manifest = load_json(manifest_path)
    rows = support_rows_by_path(manifest) if isinstance(manifest, dict) else {}
    pointers: list[dict[str, Any]] = []
    for logical_path in sorted(REQUIRED_LOGICAL_ARTIFACTS):
        report, pointer_failures = check_pointer(root, logical_path, rows)
        pointers.append(report)
        failures.extend(pointer_failures)

    validator_text = (root / VALIDATOR).read_text(encoding="utf-8", errors="replace") if (root / VALIDATOR).exists() else ""
    support_checker_text = (root / SUPPORT_CHECKER).read_text(encoding="utf-8", errors="replace") if (root / SUPPORT_CHECKER).exists() else ""
    for token, path, text in [
        ("logical_artifact_bytes", VALIDATOR.as_posix(), validator_text),
        ("gzip.decompress", VALIDATOR.as_posix(), validator_text),
        (POINTER_FORMAT, VALIDATOR.as_posix(), validator_text),
        ("logical_manifest_target_bytes", SUPPORT_CHECKER.as_posix(), support_checker_text),
        ("gzip.decompress", SUPPORT_CHECKER.as_posix(), support_checker_text),
        (POINTER_FORMAT, SUPPORT_CHECKER.as_posix(), support_checker_text),
    ]:
        if token not in text:
            failures.append({"category": "resolver_token_missing", "path": path, "token": token})

    total_saved = sum(int(row.get("hot_path_bytes_saved", 0)) for row in pointers)
    if total_saved < MINIMUM_TOTAL_HOT_PATH_SAVED_BYTES:
        failures.append({"category": "payload_pointer_savings_below_floor", "actual": total_saved, "minimum": MINIMUM_TOTAL_HOT_PATH_SAVED_BYTES})

    required_pointer_count = len(REQUIRED_LOGICAL_ARTIFACTS)
    if len(pointers) != required_pointer_count:
        failures.append({"category": "payload_pointer_count_mismatch", "actual": len(pointers), "expected": required_pointer_count})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "worked_example_payload_pointer_check",
        "support_manifest": SUPPORT_MANIFEST.as_posix(),
        "validator": VALIDATOR.as_posix(),
        "support_manifest_checker": SUPPORT_CHECKER.as_posix(),
        "pointer_format": POINTER_FORMAT,
        "pointers": pointers,
        "summary": {
            "checks_failed": len(failures),
            "pointer_count": len(pointers),
            "required_pointer_count": required_pointer_count,
            "logical_bytes": sum(int(row.get("logical_bytes", 0)) for row in pointers),
            "payload_bytes": sum(int(row.get("payload_bytes", 0)) for row in pointers),
            "pointer_bytes": sum(int(row.get("pointer_bytes", 0)) for row in pointers),
            "hot_path_bytes_saved": total_saved,
            "minimum_hot_path_bytes_saved": MINIMUM_TOTAL_HOT_PATH_SAVED_BYTES,
            "validator_resolver_bound": True,
        },
        "failures": failures[:80],
        "fail_closed_rule": "If a worked-example payload pointer fails, do not trust the Paper17 split: restore inline JSON or repair the pointer/payload/support-manifest/validator resolver before publication decisions.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
