#!/usr/bin/env python3
"""Verify one content-free sync dishonest-storage drill receipt.

The receipt is intentionally small: it proves the shape of the exercised
failure, not the private synchronized content.  A valid receipt must show that
an acknowledged generation was visible before the cut, that a later cold read
returned an older valid generation, and that an external witness floor refused
to treat that older state as current.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


SCHEMA = "iotox.sync-dishonest-storage-drill.v1"
RECEIPT_NAME = "receipt.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
EXPECTED_FAMILIES = ("branch-pointer", "workspace", "maintenance")


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as source:
        record = json.load(source)
    require(isinstance(record, dict), "receipt root is not an object")
    return record


def receipt_path(path: Path) -> Path:
    candidate = path / RECEIPT_NAME if path.is_dir() else path
    require(candidate.is_file() and not candidate.is_symlink(), "receipt is absent")
    return candidate


def require_hex(value: object, field: str) -> str:
    require(isinstance(value, str) and HEX64.fullmatch(value) is not None, f"{field} is not a SHA-256 hex digest")
    return value


def require_bool(record: dict[str, object], field: str, expected: bool = True) -> None:
    require(record.get(field) is expected, f"{field} is not {expected}")


def require_generation_map(record: dict[str, object]) -> dict[str, object]:
    generations = record.get("generations")
    require(isinstance(generations, dict), "generations is not an object")
    expected = {
        "base": 1,
        "acknowledged": 2,
        "cold": 1,
        "external_floor": 2,
    }
    for key, value in expected.items():
        require(generations.get(key) == value, f"generation {key} is not {value}")
    return generations


def require_state_digests(record: dict[str, object]) -> dict[str, str]:
    digests = record.get("state_digests")
    require(isinstance(digests, dict), "state_digests is not an object")
    base = require_hex(digests.get("base"), "state_digests.base")
    acknowledged = require_hex(
        digests.get("acknowledged"), "state_digests.acknowledged"
    )
    cold = require_hex(digests.get("cold"), "state_digests.cold")
    floor = require_hex(
        digests.get("external_floor"), "state_digests.external_floor"
    )
    require(base == cold, "cold state digest is not the older base state")
    require(acknowledged == floor, "external witness floor is not the acknowledged state")
    require(base != acknowledged, "acknowledged state did not change from base")
    return {
        "base": base,
        "acknowledged": acknowledged,
        "cold": cold,
        "external_floor": floor,
    }


def require_family_results(record: dict[str, object]) -> list[dict[str, object]]:
    value = record.get("family_results")
    require(isinstance(value, list), "family_results is not a list")
    require(len(value) == len(EXPECTED_FAMILIES), "family_results has the wrong length")
    seen: list[str] = []
    for index, item in enumerate(value):
        require(isinstance(item, dict), f"family_results[{index}] is not an object")
        family = item.get("family")
        require(isinstance(family, str), f"family_results[{index}].family is invalid")
        seen.append(family)
        require(item.get("base_generation") == 1, f"{family} base_generation is not 1")
        require(
            item.get("acknowledged_generation") == 2,
            f"{family} acknowledged_generation is not 2",
        )
        require(item.get("cold_generation") == 1, f"{family} cold_generation is not 1")
        require(item.get("external_floor_generation") == 2, f"{family} floor is not 2")
        base = require_hex(item.get("base_record_sha256"), f"{family} base digest")
        acknowledged = require_hex(
            item.get("acknowledged_record_sha256"),
            f"{family} acknowledged digest",
        )
        cold = require_hex(item.get("cold_record_sha256"), f"{family} cold digest")
        require(base == cold, f"{family} cold record is not the base record")
        require(base != acknowledged, f"{family} acknowledged record did not change")
        require(item.get("rollback_detected") is True, f"{family} rollback was not detected")
        require(item.get("mutation_refused") is True, f"{family} mutation was not refused")
    require(tuple(sorted(seen)) == tuple(sorted(EXPECTED_FAMILIES)), "family set is invalid")
    return value


def verify_record(record: dict[str, object]) -> dict[str, object]:
    require(record.get("schema") == SCHEMA, "schema is unsupported")
    require(record.get("status") == "passed", "status is not passed")
    run_id = record.get("run_id")
    require(isinstance(run_id, str) and RUN_ID.fullmatch(run_id) is not None, "run_id is invalid")
    require(record.get("block_interposer") == "device-mapper-snapshot", "unexpected block interposer")
    require(record.get("filesystem") == "ext4", "unexpected filesystem")
    require(
        record.get("storage_lie")
        == "snapshot-cow-discard-after-acknowledged-fsync",
        "unexpected storage lie",
    )
    require(record.get("claim_boundary") == "same-host-dm-snapshot-valid-old-rollback-drill", "claim boundary is invalid")
    require_bool(record, "dm_snapshot_target_present")
    require_bool(record, "acknowledged_generation_visible_before_cut")
    require_bool(record, "cold_valid_old_returned")
    require_bool(record, "rollback_detected")
    require_bool(record, "mutation_refused")
    require_bool(record, "contains_secrets", expected=False)
    require(isinstance(record.get("raw_retained"), bool), "raw_retained is not boolean")
    require_generation_map(record)
    digests = require_state_digests(record)
    family_results = require_family_results(record)
    fsyncs = record.get("fsyncs")
    require(isinstance(fsyncs, dict), "fsyncs is not an object")
    for field in (
        "generation_1_file_and_directory",
        "generation_2_file_and_directory",
        "os_sync_after_acknowledged_write",
    ):
        require(fsyncs.get(field) is True, f"fsync flag {field} is not true")
    devices = record.get("devices")
    require(isinstance(devices, dict), "devices is not an object")
    for field in ("origin_loop_sha256", "cow_loop_sha256", "snapshot_dm_name_sha256"):
        require_hex(devices.get(field), f"devices.{field}")
    for field in ("origin_size_bytes", "cow_size_bytes"):
        require(isinstance(devices.get(field), int) and devices[field] > 0, f"devices.{field} is invalid")
    nonclaims = record.get("nonclaims")
    require(isinstance(nonclaims, list) and len(nonclaims) >= 3, "nonclaims are missing")
    require(all(isinstance(item, str) and item for item in nonclaims), "nonclaims contain invalid entries")
    return {
        "schema": "iotox.sync-dishonest-storage-drill-verification.v1",
        "status": "passed",
        "run_id": run_id,
        "families": sorted(item["family"] for item in family_results),
        "base_state_sha256": digests["base"],
        "acknowledged_state_sha256": digests["acknowledged"],
        "cold_state_sha256": digests["cold"],
        "external_floor_state_sha256": digests["external_floor"],
        "claim_boundary": record.get("claim_boundary"),
        "contains_secrets": False,
    }


def sample_receipt() -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "status": "passed",
        "run_id": "run.SELFtest",
        "block_interposer": "device-mapper-snapshot",
        "filesystem": "ext4",
        "storage_lie": "snapshot-cow-discard-after-acknowledged-fsync",
        "claim_boundary": "same-host-dm-snapshot-valid-old-rollback-drill",
        "dm_snapshot_target_present": True,
        "acknowledged_generation_visible_before_cut": True,
        "cold_valid_old_returned": True,
        "rollback_detected": True,
        "mutation_refused": True,
        "contains_secrets": False,
        "raw_retained": False,
        "generations": {
            "base": 1,
            "acknowledged": 2,
            "cold": 1,
            "external_floor": 2,
        },
        "state_digests": {
            "base": "0" * 64,
            "acknowledged": "1" * 64,
            "cold": "0" * 64,
            "external_floor": "1" * 64,
        },
        "family_results": [
            {
                "family": family,
                "base_generation": 1,
                "acknowledged_generation": 2,
                "cold_generation": 1,
                "external_floor_generation": 2,
                "base_record_sha256": "2" * 64,
                "acknowledged_record_sha256": "3" * 64,
                "cold_record_sha256": "2" * 64,
                "rollback_detected": True,
                "mutation_refused": True,
            }
            for family in EXPECTED_FAMILIES
        ],
        "fsyncs": {
            "generation_1_file_and_directory": True,
            "generation_2_file_and_directory": True,
            "os_sync_after_acknowledged_write": True,
        },
        "devices": {
            "origin_loop_sha256": "4" * 64,
            "cow_loop_sha256": "5" * 64,
            "snapshot_dm_name_sha256": "6" * 64,
            "origin_size_bytes": 67108864,
            "cow_size_bytes": 33554432,
        },
        "nonclaims": [
            "not-storage-media-certification",
            "not-full-dishonest-storage-matrix",
            "not-precious-data-readiness",
        ],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-dishonest-storage-verify-") as raw:
        root = Path(raw)
        receipt = root / RECEIPT_NAME
        receipt.write_text(
            json.dumps(sample_receipt(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary = verify_record(load_json(receipt_path(root)))
        require(summary["status"] == "passed", "self-test summary failed")

        bad = sample_receipt()
        bad["cold_valid_old_returned"] = False
        try:
            verify_record(bad)
        except VerificationError:
            pass
        else:
            raise VerificationError("self-test accepted missing rollback")
    print("sync-dishonest-storage-drill-verifier-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    require(args.path is not None, "receipt path is required")
    summary = verify_record(load_json(receipt_path(args.path)))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, json.JSONDecodeError) as error:
        print(f"sync dishonest-storage drill verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
