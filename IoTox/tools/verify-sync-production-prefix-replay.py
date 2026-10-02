#!/usr/bin/env python3
"""Verify a content-free live-Agent sync production-prefix replay receipt."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "iotox.sync-production-prefix-replay.v1"
RECEIPT_NAME = "production-prefix-replay.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
FILESYSTEMS = {"ext4", "btrfs"}
MARKS = {
    "sync-create-generation-1": "valid-old-production-namespace",
    "sync-publish-generation-2": "accepted-current-production-namespace",
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path) -> dict[str, Any]:
    candidate = path / RECEIPT_NAME if path.is_dir() else path
    require(candidate.is_file() and not candidate.is_symlink(), "production prefix replay receipt is absent")
    with candidate.open("r", encoding="utf-8") as source:
        record = json.load(source)
    require(isinstance(record, dict), "receipt root is not an object")
    return record


def require_hex(value: object, field: str) -> str:
    require(isinstance(value, str) and HEX64.fullmatch(value) is not None, f"{field} is not a SHA-256 digest")
    return value


def require_bool(record: dict[str, Any], field: str, expected: bool = True) -> None:
    require(record.get(field) is expected, f"{field} is not {expected}")


def has_storage_media_nonclaim(nonclaims: list[object]) -> bool:
    return (
        "not-storage-media-certification" in nonclaims
        or "not-real-media-qualification" in nonclaims
    )


def require_nonnegative_int(value: object, field: str) -> int:
    require(isinstance(value, int) and value >= 0, f"{field} is not a non-negative integer")
    return value


def require_summary(summary: object, field: str) -> dict[str, Any]:
    require(isinstance(summary, dict), f"{field} is not an object")
    require_hex(summary.get("inventory_sha256"), f"{field}.inventory_sha256")
    require_nonnegative_int(summary.get("file_count"), f"{field}.file_count")
    require_nonnegative_int(summary.get("total_bytes"), f"{field}.total_bytes")
    families = summary.get("family_counts")
    require(isinstance(families, dict), f"{field}.family_counts is not an object")
    for family in (
        "namespace",
        "automation",
        "branch-pointer",
        "immutable-branch-record",
        "manifest",
        "object",
        "workspace",
        "maintenance",
        "transaction-lock",
        "source-file",
    ):
        require_nonnegative_int(families.get(family), f"{field}.family_counts.{family}")
    return summary


def verify_prefix_result(result: dict[str, Any], acknowledged_state_sha256: str) -> dict[str, Any]:
    require(isinstance(result, dict), "prefix result is not an object")
    mark = result.get("mark")
    require(isinstance(mark, str) and mark in MARKS, "prefix replay mark is unsupported")
    require(result.get("production_boundary") == MARKS[mark], f"{mark} production boundary is wrong")
    require_nonnegative_int(result.get("mark_entry"), f"{mark}.mark_entry")
    require_hex(result.get("find_output_sha256"), f"{mark}.find_output_sha256")
    replayed_state = require_hex(result.get("replayed_state_sha256"), f"{mark}.replayed_state_sha256")
    expected_state = require_hex(result.get("expected_state_sha256"), f"{mark}.expected_state_sha256")
    require(replayed_state == expected_state, f"{mark} replay did not equal expected prefix state")
    external_floor = require_hex(result.get("external_floor_state_sha256"), f"{mark}.external_floor_state_sha256")
    require(external_floor == acknowledged_state_sha256, f"{mark} external floor is not acknowledged state")
    require_bool(result, "replayed_equals_expected_prefix")
    require_bool(result, "contains_secrets", expected=False)
    expected_summary = require_summary(result.get("expected_summary"), f"{mark}.expected_summary")
    replayed_summary = require_summary(result.get("replayed_summary"), f"{mark}.replayed_summary")
    require(
        replayed_summary.get("inventory_sha256") == expected_summary.get("inventory_sha256"),
        f"{mark} replayed inventory differs from expected summary",
    )
    repair = result.get("production_repair_result")
    require(isinstance(repair, dict), f"{mark}.production_repair_result is not an object")
    require(repair.get("exit_code") == 0, f"{mark} production sync-repair did not pass before marking")
    require(repair.get("metadata") == "verified", f"{mark} production sync-repair did not verify metadata")
    require_nonnegative_int(repair.get("selected_objects"), f"{mark}.production_repair_result.selected_objects")
    require_nonnegative_int(repair.get("selected_bytes"), f"{mark}.production_repair_result.selected_bytes")
    if mark == "sync-create-generation-1":
        require(replayed_state != acknowledged_state_sha256, "generation-1 replay unexpectedly equals acknowledged current")
        require_bool(result, "rollback_detected_against_ack_floor")
        require_bool(result, "mutation_refused")
        require_bool(result, "accepted_current", expected=False)
        require(expected_summary["family_counts"]["manifest"] >= 1, "generation-1 manifest is absent")
        require(expected_summary["family_counts"]["object"] >= 1, "generation-1 object is absent")
    elif mark == "sync-publish-generation-2":
        require(replayed_state == acknowledged_state_sha256, "generation-2 replay does not equal acknowledged current")
        require_bool(result, "accepted_current")
        require_bool(result, "rollback_detected_against_ack_floor", expected=False)
        require_bool(result, "mutation_refused", expected=False)
        require(expected_summary["family_counts"]["manifest"] >= 2, "generation-2 did not retain at least two manifests")
        require(expected_summary["family_counts"]["object"] >= 2, "generation-2 did not retain at least two objects")
    else:  # pragma: no cover - guarded above
        raise VerificationError(f"unsupported replay mark: {mark}")
    return {"mark": mark, "kind": MARKS[mark], "mark_entry": result["mark_entry"]}


def verify_cell(cell: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(cell, dict), "cell is not an object")
    filesystem = cell.get("filesystem")
    require(filesystem in FILESYSTEMS, "cell filesystem is unsupported")
    require(cell.get("block_interposer") == "device-mapper-log-writes", "cell interposer is wrong")
    require(cell.get("claim_boundary") == "live-agent-production-transaction-prefix-replay", "claim boundary is wrong")
    require_bool(cell, "contains_secrets", expected=False)
    require(isinstance(cell.get("raw_retained"), bool), "raw_retained is not boolean")
    require_hex(cell.get("iotox_binary_sha256"), "iotox_binary_sha256")
    require_hex(cell.get("toxcore_provider_sha256"), "toxcore_provider_sha256")
    require_hex(cell.get("replay_tool_sha256"), "replay_tool_sha256")
    acknowledged_state = require_hex(cell.get("acknowledged_state_sha256"), "acknowledged_state_sha256")
    prefix_results = cell.get("prefix_results")
    require(isinstance(prefix_results, list), "prefix_results is not a list")
    verified = [verify_prefix_result(result, acknowledged_state) for result in prefix_results]
    require({result["mark"] for result in verified} == set(MARKS), "cell does not cover every replay mark")
    require(cell.get("namespace_class") == "fixture-single-directory-read-write", "unexpected namespace class")
    return {"filesystem": filesystem, "mark_count": len(verified)}


def verify_record(record: dict[str, Any]) -> dict[str, Any]:
    require(record.get("schema") == SCHEMA, "schema is unsupported")
    require(record.get("status") == "passed", "status is not passed")
    run_id = record.get("run_id")
    require(isinstance(run_id, str) and RUN_ID.fullmatch(run_id) is not None, "run_id is invalid")
    require_bool(record, "contains_secrets", expected=False)
    cells = record.get("cells")
    require(isinstance(cells, list) and cells, "cells are missing")
    verified = [verify_cell(cell) for cell in cells]
    requested_filesystems = record.get("filesystems", sorted(FILESYSTEMS))
    require(
        isinstance(requested_filesystems, list)
        and requested_filesystems
        and all(item in FILESYSTEMS for item in requested_filesystems),
        "requested filesystems are invalid",
    )
    observed_filesystems = {cell["filesystem"] for cell in verified}
    require(set(requested_filesystems).issubset(observed_filesystems), "receipt does not cover requested filesystems")
    nonclaims = record.get("nonclaims")
    require(isinstance(nonclaims, list) and len(nonclaims) >= 4, "nonclaims are missing")
    require(has_storage_media_nonclaim(nonclaims), "storage-media nonclaim is missing")
    require("not-independent-backup-custody" in nonclaims, "backup custody nonclaim is missing")
    require("not-precious-data-readiness" in nonclaims, "precious-data nonclaim is missing")
    require("not-internal-subtransaction-prefix-coverage" in nonclaims, "internal-prefix nonclaim is missing")
    return {
        "schema": "iotox.sync-production-prefix-replay-verification.v1",
        "status": "passed",
        "run_id": run_id,
        "cell_count": len(cells),
        "filesystems": sorted(observed_filesystems),
        "marks": sorted(MARKS),
        "contains_secrets": False,
    }


def sample_summary(*, manifests: int, objects: int, inventory: str, total_bytes: int) -> dict[str, Any]:
    return {
        "inventory_sha256": inventory,
        "file_count": manifests + objects + 6,
        "total_bytes": total_bytes,
        "family_counts": {
            "namespace": 1,
            "automation": 1,
            "branch-pointer": 1,
            "immutable-branch-record": manifests,
            "manifest": manifests,
            "object": objects,
            "workspace": 1,
            "maintenance": 0,
            "transaction-lock": 1,
            "source-file": 1,
        },
    }


def sample_prefix_result(mark: str) -> dict[str, Any]:
    if mark == "sync-create-generation-1":
        digest = "1" * 64
        summary = sample_summary(manifests=1, objects=1, inventory=digest, total_bytes=100)
        return {
            "mark": mark,
            "production_boundary": MARKS[mark],
            "mark_entry": 10,
            "find_output_sha256": "f" * 64,
            "replayed_state_sha256": digest,
            "expected_state_sha256": digest,
            "external_floor_state_sha256": "2" * 64,
            "replayed_equals_expected_prefix": True,
            "rollback_detected_against_ack_floor": True,
            "mutation_refused": True,
            "accepted_current": False,
            "contains_secrets": False,
            "expected_summary": summary,
            "replayed_summary": summary,
            "production_repair_result": {
                "exit_code": 0,
                "metadata": "verified",
                "selected_objects": 1,
                "selected_bytes": 5,
            },
        }
    if mark == "sync-publish-generation-2":
        digest = "2" * 64
        summary = sample_summary(manifests=2, objects=2, inventory=digest, total_bytes=200)
        return {
            "mark": mark,
            "production_boundary": MARKS[mark],
            "mark_entry": 20,
            "find_output_sha256": "e" * 64,
            "replayed_state_sha256": digest,
            "expected_state_sha256": digest,
            "external_floor_state_sha256": digest,
            "replayed_equals_expected_prefix": True,
            "rollback_detected_against_ack_floor": False,
            "mutation_refused": False,
            "accepted_current": True,
            "contains_secrets": False,
            "expected_summary": summary,
            "replayed_summary": summary,
            "production_repair_result": {
                "exit_code": 0,
                "metadata": "verified",
                "selected_objects": 1,
                "selected_bytes": 13,
            },
        }
    raise AssertionError(mark)


def sample_receipt() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "passed",
        "run_id": "run.SELFtest",
        "contains_secrets": False,
        "filesystems": sorted(FILESYSTEMS),
        "cells": [
            {
                "cell": index,
                "filesystem": filesystem,
                "block_interposer": "device-mapper-log-writes",
                "claim_boundary": "live-agent-production-transaction-prefix-replay",
                "namespace_class": "fixture-single-directory-read-write",
                "iotox_binary_sha256": "a" * 64,
                "toxcore_provider_sha256": "b" * 64,
                "replay_tool_sha256": "c" * 64,
                "contains_secrets": False,
                "raw_retained": False,
                "acknowledged_state_sha256": "2" * 64,
                "prefix_results": [sample_prefix_result(mark) for mark in MARKS],
            }
            for index, filesystem in enumerate(sorted(FILESYSTEMS))
        ],
        "nonclaims": [
            "not-storage-media-certification",
            "not-independent-backup-custody",
            "not-precious-data-readiness",
            "not-internal-subtransaction-prefix-coverage",
        ],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-production-prefix-verify-") as raw:
        root = Path(raw)
        receipt = root / RECEIPT_NAME
        receipt.write_text(json.dumps(sample_receipt(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = verify_record(load_json(root))
        require(summary["cell_count"] == 2, "self-test did not cover both filesystems")
        bad = sample_receipt()
        bad["cells"][0]["prefix_results"] = bad["cells"][0]["prefix_results"][:-1]
        try:
            verify_record(bad)
        except VerificationError:
            pass
        else:
            raise VerificationError("self-test accepted incomplete prefix set")
        legacy = sample_receipt()
        legacy["nonclaims"] = [
            "not-real-media-qualification"
            if item == "not-storage-media-certification"
            else item
            for item in legacy["nonclaims"]
        ]
        require(verify_record(legacy)["status"] == "passed", "legacy media nonclaim did not verify")
    print("sync-production-prefix-replay-verifier-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    require(args.path is not None, "production prefix replay receipt path is required")
    summary = verify_record(load_json(args.path))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, json.JSONDecodeError) as error:
        print(f"sync production prefix replay verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
