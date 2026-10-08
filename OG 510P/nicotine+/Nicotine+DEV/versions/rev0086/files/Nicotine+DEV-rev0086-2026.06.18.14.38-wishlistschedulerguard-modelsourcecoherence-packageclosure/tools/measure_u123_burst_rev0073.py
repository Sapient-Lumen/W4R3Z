#!/usr/bin/env python3
"""Emit machine-readable U-123 duplicate-token burst observations."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maintainer_artifacts" / "u123"))
from u123_harness import (  # noqa: E402
    FakeSock, U123TestCase, make_file_init, make_transfer_request,
    open_file_handle_count, queue_download, socket_owner_count,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--burst-size", type=int, default=32)
    args = parser.parse_args()
    if args.burst_size < 2:
        parser.error("--burst-size must be at least 2")

    case = U123TestCase(methodName="runTest")
    case.setUp()
    try:
        downloads = case.make_downloads()
        username, token = "attacker-peer", 4242
        transfers = [
            queue_download(downloads, username, f"Music\\file-{index:02d}.flac", 1000 + index)
            for index in range(args.burst_size)
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
        result = {
            "burst_size": args.burst_size,
            "allowed": allowed,
            "rejected": rejected,
            "open_file_handles": open_file_handle_count(downloads),
            "socket_owners": socket_owner_count(downloads),
            "queued_remaining": len(downloads.queued_users.get(username, {})),
            "active_owner": active.virtual_path if active is not None else None,
            "network_close_messages": len(case.core.sent_network),
        }
        print(json.dumps(result, sort_keys=True))
        return 0
    finally:
        case.tearDown()


if __name__ == "__main__":
    raise SystemExit(main())
