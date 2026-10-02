#!/usr/bin/env python3
"""Verify a content-free dm-log-writes synchronization prefix-replay receipt."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "iotox.sync-log-writes-prefix-replay.v1"
RECEIPT_NAME = "prefix-replay.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
FILESYSTEMS = {"ext4", "btrfs"}
FAMILIES = (
    "branch-pointer",
    "immutable-branch-record",
    "manifest",
    "workspace",
    "maintenance",
    "projection-marker",
)
MARKS = {
    "generation-1-stable": "valid-old",
    "manifest-record-prefix": "mixed-prefix",
    "generation-2-stable": "complete-current",
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path) -> dict[str, Any]:
    candidate = path / RECEIPT_NAME if path.is_dir() else path
    require(candidate.is_file() and not candidate.is_symlink(), "prefix replay receipt is absent")
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


def require_family_results(result: dict[str, Any], mark: str) -> list[dict[str, Any]]:
    family_results = result.get("family_results")
    require(isinstance(family_results, list), f"{mark} family_results is not a list")
    require(len(family_results) == len(FAMILIES), f"{mark} family_results has wrong length")
    seen = []
    generations = {}
    for index, family_result in enumerate(family_results):
        require(isinstance(family_result, dict), f"{mark} family_results[{index}] is not an object")
        family = family_result.get("family")
        require(isinstance(family, str), f"{mark} family_results[{index}].family is invalid")
        seen.append(family)
        require(family_result.get("acknowledged_parse_status") == "valid", f"{mark}/{family} acknowledged record is invalid")
        require(family_result.get("replayed_parse_status") == "valid", f"{mark}/{family} replayed record is invalid")
        require(family_result.get("acknowledged_generation") == 2, f"{mark}/{family} acknowledged generation is not 2")
        replayed_generation = family_result.get("replayed_generation")
        require(isinstance(replayed_generation, int), f"{mark}/{family} replayed generation is invalid")
        generations[family] = replayed_generation
        require_hex(family_result.get("acknowledged_bytes_sha256"), f"{mark}/{family}.acknowledged_bytes_sha256")
        require_hex(family_result.get("replayed_bytes_sha256"), f"{mark}/{family}.replayed_bytes_sha256")
    require(tuple(sorted(seen)) == tuple(sorted(FAMILIES)), f"{mark} family set is invalid")
    if mark == "generation-1-stable":
        require(set(generations.values()) == {1}, "generation-1 replay was not wholly valid-old")
    elif mark == "manifest-record-prefix":
        require(generations.get("manifest") == 2, "manifest prefix did not replay manifest generation 2")
        require(
            generations.get("immutable-branch-record") == 2,
            "manifest prefix did not replay immutable branch record generation 2",
        )
        for family in ("branch-pointer", "workspace", "maintenance", "projection-marker"):
            require(generations.get(family) == 1, f"manifest prefix replayed unexpected {family} generation")
    elif mark == "generation-2-stable":
        require(set(generations.values()) == {2}, "generation-2 replay was not wholly current")
    else:
        raise VerificationError(f"unsupported replay mark: {mark}")
    return family_results


def verify_prefix_result(result: dict[str, Any], acknowledged_state_sha256: str) -> dict[str, Any]:
    require(isinstance(result, dict), "prefix result is not an object")
    mark = result.get("mark")
    require(isinstance(mark, str) and mark in MARKS, "prefix replay mark is unsupported")
    require(isinstance(result.get("production_boundary"), str) and result["production_boundary"], f"{mark} boundary is invalid")
    require(isinstance(result.get("mark_entry"), int) and result["mark_entry"] >= 0, f"{mark} entry is invalid")
    require_hex(result.get("find_output_sha256"), f"{mark}.find_output_sha256")
    replayed_state = require_hex(result.get("replayed_state_sha256"), f"{mark}.replayed_state_sha256")
    expected_state = require_hex(result.get("expected_state_sha256"), f"{mark}.expected_state_sha256")
    require(replayed_state == expected_state, f"{mark} replay did not equal expected prefix state")
    require_hex(result.get("external_floor_state_sha256"), f"{mark}.external_floor_state_sha256")
    require(result["external_floor_state_sha256"] == acknowledged_state_sha256, f"{mark} external floor is not acknowledged state")
    require_bool(result, "replayed_equals_expected_prefix")
    require_bool(result, "contains_secrets", expected=False)
    require_family_results(result, mark)
    if mark == "generation-2-stable":
        require(replayed_state == acknowledged_state_sha256, "generation-2 replay does not equal acknowledged current")
        require_bool(result, "accepted_current")
        require_bool(result, "rollback_detected_against_ack_floor", expected=False)
        require_bool(result, "mutation_refused", expected=False)
    else:
        require(replayed_state != acknowledged_state_sha256, f"{mark} did not differ from acknowledged current")
        require_bool(result, "rollback_detected_against_ack_floor")
        require_bool(result, "mutation_refused")
        require_bool(result, "accepted_current", expected=False)
    return {
        "mark": mark,
        "kind": MARKS[mark],
        "mark_entry": result["mark_entry"],
    }


def verify_cell(cell: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(cell, dict), "cell is not an object")
    filesystem = cell.get("filesystem")
    require(filesystem in FILESYSTEMS, "cell filesystem is unsupported")
    require(cell.get("block_interposer") == "device-mapper-log-writes", "cell interposer is wrong")
    require(cell.get("claim_boundary") == "same-host-dm-log-writes-prefix-replay-substrate", "claim boundary is wrong")
    require_bool(cell, "contains_secrets", expected=False)
    require(isinstance(cell.get("raw_retained"), bool), "raw_retained is not boolean")
    require_hex(cell.get("replay_tool_sha256"), "replay_tool_sha256")
    require_hex(cell.get("base_state_sha256"), "base_state_sha256")
    acknowledged_state = require_hex(cell.get("acknowledged_state_sha256"), "acknowledged_state_sha256")
    require(cell["base_state_sha256"] != acknowledged_state, "acknowledged state did not change")
    prefix_results = cell.get("prefix_results")
    require(isinstance(prefix_results, list), "prefix_results is not a list")
    verified = [verify_prefix_result(result, acknowledged_state) for result in prefix_results]
    require({result["mark"] for result in verified} == set(MARKS), "cell does not cover every replay mark")
    return {
        "filesystem": filesystem,
        "mark_count": len(verified),
    }


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
    require(isinstance(nonclaims, list) and len(nonclaims) >= 5, "nonclaims are missing")
    require("not-live-agent-production-prefix-replay" in nonclaims, "live-Agent production nonclaim is missing")
    require(has_storage_media_nonclaim(nonclaims), "storage-media nonclaim is missing")
    require("not-precious-data-readiness" in nonclaims, "precious-data nonclaim is missing")
    return {
        "schema": "iotox.sync-log-writes-prefix-replay-verification.v1",
        "status": "passed",
        "run_id": run_id,
        "cell_count": len(cells),
        "filesystems": sorted(observed_filesystems),
        "marks": sorted(MARKS),
        "contains_secrets": False,
    }


def family_result(family: str, replayed_generation: int) -> dict[str, Any]:
    return {
        "family": family,
        "acknowledged_generation": 2,
        "replayed_generation": replayed_generation,
        "acknowledged_parse_status": "valid",
        "replayed_parse_status": "valid",
        "acknowledged_bytes_sha256": "a" * 64,
        "replayed_bytes_sha256": f"{replayed_generation:064x}"[-64:],
    }


def sample_prefix_result(mark: str) -> dict[str, Any]:
    if mark == "generation-1-stable":
        generations = {family: 1 for family in FAMILIES}
        expected = "1" * 64
        accepted = False
        rollback = True
        refused = True
    elif mark == "manifest-record-prefix":
        generations = {family: 1 for family in FAMILIES}
        generations["manifest"] = 2
        generations["immutable-branch-record"] = 2
        expected = "2" * 64
        accepted = False
        rollback = True
        refused = True
    elif mark == "generation-2-stable":
        generations = {family: 2 for family in FAMILIES}
        expected = "b" * 64
        accepted = True
        rollback = False
        refused = False
    else:
        raise AssertionError(mark)
    return {
        "mark": mark,
        "production_boundary": f"self-test-{mark}",
        "mark_entry": 10,
        "find_output_sha256": "f" * 64,
        "replayed_state_sha256": expected,
        "expected_state_sha256": expected,
        "external_floor_state_sha256": "b" * 64,
        "replayed_equals_expected_prefix": True,
        "rollback_detected_against_ack_floor": rollback,
        "mutation_refused": refused,
        "accepted_current": accepted,
        "contains_secrets": False,
        "family_results": [family_result(family, generations[family]) for family in FAMILIES],
    }


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
                "claim_boundary": "same-host-dm-log-writes-prefix-replay-substrate",
                "replay_tool_sha256": "c" * 64,
                "contains_secrets": False,
                "raw_retained": False,
                "base_state_sha256": "1" * 64,
                "acknowledged_state_sha256": "b" * 64,
                "prefix_results": [sample_prefix_result(mark) for mark in MARKS],
            }
            for index, filesystem in enumerate(sorted(FILESYSTEMS))
        ],
        "nonclaims": [
            "not-live-agent-production-prefix-replay",
            "not-storage-media-certification",
            "not-independent-backup-custody",
            "not-precious-data-readiness",
            "not-physical-power-removal",
        ],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-log-writes-prefix-verify-") as raw:
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
    print("sync-log-writes-prefix-replay-verifier-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    require(args.path is not None, "prefix replay receipt path is required")
    summary = verify_record(load_json(args.path))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, json.JSONDecodeError) as error:
        print(f"sync log-writes prefix replay verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
