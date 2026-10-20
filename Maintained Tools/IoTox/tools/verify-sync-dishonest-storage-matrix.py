#!/usr/bin/env python3
"""Verify a content-free sync dishonest-storage matrix receipt."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "iotox.sync-dishonest-storage-matrix.v1"
RECEIPT_NAME = "matrix.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RUN_ID = re.compile(r"^run\.[A-Za-z0-9_]{8}$")
FILESYSTEMS = {"ext4", "btrfs"}
SCENARIOS = {
    "valid-old-rollback",
    "cross-family-rollback",
    "torn-record",
    "flakey-drop-writes",
}
FAMILIES = (
    "branch-pointer",
    "immutable-branch-record",
    "manifest",
    "workspace",
    "maintenance",
    "projection-marker",
)


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def load_json(path: Path) -> dict[str, Any]:
    candidate = path / RECEIPT_NAME if path.is_dir() else path
    require(candidate.is_file() and not candidate.is_symlink(), "matrix receipt is absent")
    with candidate.open("r", encoding="utf-8") as source:
        record = json.load(source)
    require(isinstance(record, dict), "receipt root is not an object")
    return record


def require_hex(value: object, field: str) -> str:
    require(isinstance(value, str) and HEX64.fullmatch(value) is not None, f"{field} is not a SHA-256 digest")
    return value


def require_bool(record: dict[str, Any], field: str, expected: bool = True) -> None:
    require(record.get(field) is expected, f"{field} is not {expected}")


def require_family_results(cell: dict[str, Any]) -> list[dict[str, Any]]:
    family_results = cell.get("family_results")
    require(isinstance(family_results, list), "family_results is not a list")
    require(len(family_results) == len(FAMILIES), "family_results has wrong length")
    seen = []
    for index, result in enumerate(family_results):
        require(isinstance(result, dict), f"family_results[{index}] is not an object")
        family = result.get("family")
        require(isinstance(family, str), f"family_results[{index}].family is invalid")
        seen.append(family)
        for key in ("base_bytes_sha256", "acknowledged_bytes_sha256", "cold_bytes_sha256"):
            require_hex(result.get(key), f"{family}.{key}")
        require(result.get("base_parse_status") == "valid", f"{family} base was not valid")
        require(result.get("acknowledged_parse_status") == "valid", f"{family} acknowledged was not valid")
        require(result.get("base_generation") == 1, f"{family} base generation is not 1")
        require(result.get("acknowledged_generation") == 2, f"{family} acknowledged generation is not 2")
    require(tuple(sorted(seen)) == tuple(sorted(FAMILIES)), "family set is invalid")
    return family_results


def verify_cell(cell: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(cell, dict), "cell is not an object")
    filesystem = cell.get("filesystem")
    scenario = cell.get("scenario")
    require(filesystem in FILESYSTEMS, "cell filesystem is unsupported")
    require(scenario in SCENARIOS, "cell scenario is unsupported")
    expected_interposer = (
        "device-mapper-flakey"
        if scenario == "flakey-drop-writes"
        else "device-mapper-snapshot"
    )
    require(cell.get("block_interposer") == expected_interposer, "cell interposer is wrong")
    require_bool(cell, "acknowledged_generation_visible_before_cut")
    require_bool(cell, "rollback_detected")
    require_bool(cell, "mutation_refused")
    require_bool(cell, "contains_secrets", expected=False)
    require(isinstance(cell.get("raw_retained"), bool), "cell raw_retained is not boolean")
    require_hex(cell.get("base_state_sha256"), "base_state_sha256")
    require_hex(cell.get("acknowledged_state_sha256"), "acknowledged_state_sha256")
    require_hex(cell.get("cold_state_sha256"), "cold_state_sha256")
    require_hex(cell.get("external_floor_state_sha256"), "external_floor_state_sha256")
    require(
        cell["acknowledged_state_sha256"] == cell["external_floor_state_sha256"],
        "external floor is not the acknowledged state",
    )
    require(
        cell["base_state_sha256"] != cell["acknowledged_state_sha256"],
        "acknowledged state did not change",
    )
    require(cell["cold_state_sha256"] != cell["acknowledged_state_sha256"], "cold state still equals acknowledged state")
    families = require_family_results(cell)
    cold_statuses = {item["cold_parse_status"] for item in families}
    cold_generations = [
        item.get("cold_generation")
        for item in families
        if item.get("cold_parse_status") == "valid"
    ]
    if scenario in {"valid-old-rollback", "flakey-drop-writes"}:
        require(cold_statuses == {"valid"}, f"{scenario} cold statuses are not all valid")
        require(set(cold_generations) == {1}, f"{scenario} did not return generation 1")
    elif scenario == "cross-family-rollback":
        require(cold_statuses == {"valid"}, "cross-family cold state contains invalid records")
        require(set(cold_generations) == {1, 2}, "cross-family cold state is not mixed")
    elif scenario == "torn-record":
        require("invalid-json" in cold_statuses or "invalid-record" in cold_statuses, "torn-record did not expose an invalid cold record")
        require(1 in cold_generations, "torn-record did not retain older valid state beside the tear")
    return {
        "filesystem": filesystem,
        "scenario": scenario,
        "block_interposer": expected_interposer,
        "cold_statuses": sorted(cold_statuses),
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
    requested_scenarios = record.get("scenarios", sorted(SCENARIOS))
    require(
        isinstance(requested_filesystems, list)
        and requested_filesystems
        and all(item in FILESYSTEMS for item in requested_filesystems),
        "requested filesystems are invalid",
    )
    require(
        isinstance(requested_scenarios, list)
        and requested_scenarios
        and all(item in SCENARIOS for item in requested_scenarios),
        "requested scenarios are invalid",
    )
    observed = {(cell["filesystem"], cell["scenario"]) for cell in verified}
    expected = {
        (filesystem, scenario)
        for filesystem in requested_filesystems
        for scenario in requested_scenarios
    }
    require(expected.issubset(observed), "matrix does not cover every filesystem/scenario pair")
    nonclaims = record.get("nonclaims")
    require(isinstance(nonclaims, list) and len(nonclaims) >= 4, "nonclaims are missing")
    require(all(isinstance(item, str) and item for item in nonclaims), "nonclaims contain invalid entries")
    return {
        "schema": "iotox.sync-dishonest-storage-matrix-verification.v1",
        "status": "passed",
        "run_id": run_id,
        "cell_count": len(cells),
        "filesystems": sorted(FILESYSTEMS),
        "scenarios": sorted(SCENARIOS),
        "contains_secrets": False,
    }


def sample_cell(filesystem: str, scenario: str) -> dict[str, Any]:
    cold_status = "invalid-json" if scenario == "torn-record" else "valid"
    family_results = []
    for index, family in enumerate(FAMILIES):
        if scenario == "cross-family-rollback":
            cold_generation = 2 if family in {"manifest", "immutable-branch-record"} else 1
        elif scenario == "torn-record" and family == "manifest":
            cold_generation = None
        else:
            cold_generation = 1
        status = cold_status if family == "manifest" else "valid"
        family_results.append(
            {
                "family": family,
                "base_generation": 1,
                "acknowledged_generation": 2,
                "cold_generation": cold_generation,
                "base_parse_status": "valid",
                "acknowledged_parse_status": "valid",
                "cold_parse_status": status,
                "base_bytes_sha256": f"{index:064x}"[-64:],
                "acknowledged_bytes_sha256": f"{index + 10:064x}"[-64:],
                "cold_bytes_sha256": f"{index + 20:064x}"[-64:],
            }
        )
    return {
        "filesystem": filesystem,
        "scenario": scenario,
        "block_interposer": "device-mapper-flakey" if scenario == "flakey-drop-writes" else "device-mapper-snapshot",
        "storage_lie": scenario,
        "claim_boundary": "same-host-dishonest-storage-matrix-drill",
        "acknowledged_generation_visible_before_cut": True,
        "rollback_detected": True,
        "mutation_refused": True,
        "contains_secrets": False,
        "raw_retained": False,
        "base_state_sha256": "a" * 64,
        "acknowledged_state_sha256": "b" * 64,
        "cold_state_sha256": "c" * 64,
        "external_floor_state_sha256": "b" * 64,
        "family_results": family_results,
    }


def sample_receipt() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "passed",
        "run_id": "run.SELFtest",
        "contains_secrets": False,
        "cells": [
            sample_cell(filesystem, scenario)
            for filesystem in sorted(FILESYSTEMS)
            for scenario in sorted(SCENARIOS)
        ],
        "nonclaims": [
            "not-storage-media-certification",
            "not-independent-backup-custody",
            "not-precious-data-readiness",
            "not-full-production-agent-prefix-replay",
        ],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="iotox-dishonest-storage-matrix-verify-") as raw:
        root = Path(raw)
        receipt = root / RECEIPT_NAME
        receipt.write_text(json.dumps(sample_receipt(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = verify_record(load_json(root))
        require(summary["cell_count"] == 8, "self-test did not cover 8 cells")
        bad = sample_receipt()
        bad["cells"] = bad["cells"][:-1]
        try:
            verify_record(bad)
        except VerificationError:
            pass
        else:
            raise VerificationError("self-test accepted incomplete matrix")
    print("sync-dishonest-storage-matrix-verifier-self-test=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    require(args.path is not None, "matrix receipt path is required")
    summary = verify_record(load_json(args.path))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, json.JSONDecodeError) as error:
        print(f"sync dishonest-storage matrix verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
