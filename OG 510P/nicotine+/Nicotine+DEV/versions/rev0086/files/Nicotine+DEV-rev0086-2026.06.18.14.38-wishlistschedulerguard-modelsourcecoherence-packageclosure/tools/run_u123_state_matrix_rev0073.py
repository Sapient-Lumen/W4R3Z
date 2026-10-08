#!/usr/bin/env python3
"""Run all rev0073 U-123 research harnesses in one source-bound process.

One process per source state avoids repeatedly paying the unusually large Python
startup footprint of this execution environment while preserving fresh process
isolation between unpatched and prototype states.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "maintainer_artifacts" / "u123"
sys.path.insert(0, str(ARTIFACTS))

TESTS = {
    "current-behavior-witness": "test_downloads_duplicate_transfer_token_reproducer",
    "collision-rejection": "test_downloads_duplicate_transfer_token_collision_rejection_regression",
    "identity-aware-cleanup": "test_downloads_duplicate_transfer_token_identity_guard_regression",
    "burst-resource-bound": "test_downloads_duplicate_transfer_token_burst_bound_regression",
    "fixed-composite": "test_downloads_duplicate_transfer_token_fixed_regression",
    "same-object-reentry-experiment": "test_downloads_duplicate_transfer_token_same_object_reentry_experiment",
}


def run_suite(module_name: str) -> dict[str, object]:
    module = __import__(module_name)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    output = stream.getvalue()
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "passed": result.wasSuccessful(),
        "summary": "OK" if result.wasSuccessful() else f"FAILED (failures={len(result.failures)}, errors={len(result.errors)})",
        "output_tail": "\n".join(output.splitlines()[-16:]),
    }


def burst_metrics(burst_size: int) -> dict[str, object]:
    from u123_harness import (  # pylint: disable=import-outside-toplevel
        FakeSock,
        U123TestCase,
        make_file_init,
        make_transfer_request,
        open_file_handle_count,
        queue_download,
        socket_owner_count,
    )

    case = U123TestCase(methodName="runTest")
    case.setUp()
    try:
        downloads = case.make_downloads()
        username, token = "attacker-peer", 4242
        transfers = [
            queue_download(downloads, username, f"Music\\file-{index:04d}.flac", 1000 + index)
            for index in range(burst_size)
        ]
        allowed = rejected = 0
        for index, transfer in enumerate(transfers):
            response = downloads._transfer_request_downloads(
                make_transfer_request(username, transfer.virtual_path, transfer.size, token)
            )
            if response.allowed:
                allowed += 1
                downloads._file_transfer_init(
                    make_file_init(username, token, FakeSock(f"burst-{index}"))
                )
            else:
                rejected += 1
        active = downloads.active_users.get(username, {}).get(token)
        return {
            "burst_size": burst_size,
            "allowed": allowed,
            "rejected": rejected,
            "open_file_handles": open_file_handle_count(downloads),
            "socket_owners": socket_owner_count(downloads),
            "queued_remaining": len(downloads.queued_users.get(username, {})),
            "active_owner": active.virtual_path if active is not None else None,
            "network_close_messages": len(case.core.sent_network),
        }
    finally:
        case.tearDown()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--burst-size", type=int, default=32)
    args = parser.parse_args()
    if args.burst_size < 2:
        parser.error("--burst-size must be at least 2")

    output = {
        "tests": {test_id: run_suite(module) for test_id, module in TESTS.items()},
        "burst": burst_metrics(args.burst_size),
    }
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
