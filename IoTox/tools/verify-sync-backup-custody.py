#!/usr/bin/env python3
"""Verify a content-free IoTox sync recovery-custody receipt."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "iotox.sync-backup-custody.v1"
RECEIPT_NAME = "backup-custody.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
LABEL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@+-]{0,127}$")
CUSTODY_CLASSES = {
    "same-host-versioned",
    "sync-external-versioned",
    "off-host-versioned",
    "offline-or-remote-versioned",
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path) -> dict[str, Any]:
    candidate = path / RECEIPT_NAME if path.is_dir() else path
    require(candidate.is_file() and not candidate.is_symlink(), "backup custody receipt is absent")
    with candidate.open("r", encoding="utf-8") as source:
        record = json.load(source)
    require(isinstance(record, dict), "receipt root is not an object")
    return record


def require_hex(value: object, field: str) -> str:
    require(isinstance(value, str) and HEX64.fullmatch(value) is not None, f"{field} is not a SHA-256 digest")
    return value


def require_label(value: object, field: str) -> str:
    require(isinstance(value, str) and LABEL.fullmatch(value) is not None, f"{field} is not a bounded label")
    return value


def require_bool(record: dict[str, Any], field: str, expected: bool = True) -> None:
    require(record.get(field) is expected, f"{field} is not {expected}")


def require_nonnegative_int(value: object, field: str) -> int:
    require(isinstance(value, int) and value >= 0, f"{field} is not a non-negative integer")
    return value


def verify_record(record: dict[str, Any]) -> dict[str, Any]:
    require(record.get("schema") == SCHEMA, "schema is unsupported")
    require(record.get("status") == "passed", "status is not passed")
    run_id = record.get("run_id")
    require(isinstance(run_id, str) and RUN_ID.fullmatch(run_id) is not None, "run_id is invalid")
    require_bool(record, "contains_secrets", expected=False)
    custody_class = record.get("custody_class")
    if custody_class is None and record.get("backup_independent") is True:
        custody_class = "legacy-independent-versioned"
    require(
        isinstance(custody_class, str)
        and (custody_class in CUSTODY_CLASSES or custody_class == "legacy-independent-versioned"),
        "custody_class is unsupported",
    )
    require_bool(record, "immutable_or_versioned")
    require_bool(record, "restore_verified")
    require_bool(record, "operator_rehearsal_repeatable")

    backup_system = require_label(record.get("backup_system"), "backup_system")
    backup_generation = require_label(record.get("backup_generation"), "backup_generation")
    live_failure_domain = require_label(record.get("live_failure_domain"), "live_failure_domain")
    backup_failure_domain = require_label(record.get("backup_failure_domain"), "backup_failure_domain")
    restored_failure_domain = require_label(record.get("restored_failure_domain"), "restored_failure_domain")
    restore_provenance = require_label(record.get("restore_provenance"), "restore_provenance")
    require_hex(record.get("recovery_report_sha256"), "recovery_report_sha256")
    require_hex(record.get("backup_inventory_sha256"), "backup_inventory_sha256")
    require_hex(record.get("restored_inventory_sha256"), "restored_inventory_sha256")

    comparison = record.get("recovery_comparison")
    require(isinstance(comparison, dict), "recovery_comparison is not an object")
    require_bool(comparison, "matches")
    require_bool(comparison, "contains_secrets", expected=False)
    backup_entries = require_nonnegative_int(comparison.get("backup_entries"), "recovery_comparison.backup_entries")
    restored_entries = require_nonnegative_int(comparison.get("restored_entries"), "recovery_comparison.restored_entries")
    require(backup_entries == restored_entries, "recovery comparison entry counts differ")
    require(isinstance(comparison.get("roots_on_distinct_devices"), bool), "roots_on_distinct_devices is not boolean")

    nonclaims = record.get("nonclaims")
    require(isinstance(nonclaims, list) and len(nonclaims) >= 5, "nonclaims are missing")
    require("not-storage-media-certification" in nonclaims, "storage-media nonclaim is missing")
    require("not-disk-loss-protection" in nonclaims, "disk-loss nonclaim is missing")
    require("not-host-compromise-protection" in nonclaims, "host-compromise nonclaim is missing")
    require("not-filesystem-wide-corruption-protection" in nonclaims, "filesystem-wide corruption nonclaim is missing")
    require("not-content-custody" in nonclaims, "content-custody nonclaim is missing")
    return {
        "schema": "iotox.sync-backup-custody-verification.v1",
        "status": "passed",
        "run_id": run_id,
        "custody_class": custody_class,
        "backup_system": backup_system,
        "backup_generation": backup_generation,
        "backup_failure_domain": backup_failure_domain,
        "restored_failure_domain": restored_failure_domain,
        "restore_provenance": restore_provenance,
        "backup_entries": backup_entries,
        "restored_entries": restored_entries,
        "contains_secrets": False,
    }


def sample_receipt() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "passed",
        "run_id": "run.SELFtest",
        "contains_secrets": False,
        "backup_independent": False,
        "custody_class": "same-host-versioned",
        "immutable_or_versioned": True,
        "restore_verified": True,
        "operator_rehearsal_repeatable": True,
        "backup_system": "borg",
        "backup_generation": "gen.SELFtest",
        "live_failure_domain": "live.host",
        "backup_failure_domain": "offline.ssd",
        "restored_failure_domain": "restore.host",
        "restore_provenance": "restore.drill",
        "recovery_report_sha256": "a" * 64,
        "backup_inventory_sha256": "b" * 64,
        "restored_inventory_sha256": "b" * 64,
        "recovery_comparison": {
            "matches": True,
            "contains_secrets": False,
            "backup_entries": 8,
            "restored_entries": 8,
            "roots_on_distinct_devices": False,
        },
        "nonclaims": [
            "not-storage-media-certification",
            "not-disk-loss-protection",
            "not-host-compromise-protection",
            "not-filesystem-wide-corruption-protection",
            "not-content-custody",
        ],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-backup-custody-") as raw:
        path = Path(raw) / RECEIPT_NAME
        path.write_text(json.dumps(sample_receipt(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verified = verify_record(load_json(path))
        require(verified["status"] == "passed", "sample receipt did not verify")
        tampered = sample_receipt()
        tampered["custody_class"] = "unversioned-live-copy"
        try:
            verify_record(tampered)
        except VerificationError:
            pass
        else:  # pragma: no cover
            raise VerificationError("unsupported custody class was accepted")
    print("sync-backup-custody-verifier-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.receipt is None:
        parser.error("receipt path is required unless --self-test is used")
    verified = verify_record(load_json(args.receipt))
    print(json.dumps(verified, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, json.JSONDecodeError) as error:
        print(f"sync backup custody verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
