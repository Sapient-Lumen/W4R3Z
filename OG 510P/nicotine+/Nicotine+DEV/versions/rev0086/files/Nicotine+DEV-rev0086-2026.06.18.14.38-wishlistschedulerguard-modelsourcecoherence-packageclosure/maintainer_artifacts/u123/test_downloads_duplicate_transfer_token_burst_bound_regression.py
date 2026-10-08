# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixed invariant: repeated duplicate tokens allocate at most one live session."""
from __future__ import annotations

from u123_harness import FakeSock
from u123_harness import U123TestCase
from u123_harness import make_file_init
from u123_harness import make_transfer_request
from u123_harness import open_file_handle_count
from u123_harness import queue_download
from u123_harness import socket_owner_count


class DuplicateDownloadTransferTokenBurstBoundRegression(U123TestCase):
    def test_duplicate_token_burst_has_constant_live_resource_footprint(self):
        downloads = self.make_downloads()
        username = "attacker-peer"
        token = 4242
        burst_size = 32
        transfers = [
            queue_download(
                downloads,
                username,
                f"Music\\file-{index:02d}.flac",
                1000 + index,
            )
            for index in range(burst_size)
        ]

        allowed = 0
        rejected = 0
        for index, transfer in enumerate(transfers):
            response = downloads._transfer_request_downloads(
                make_transfer_request(
                    username,
                    transfer.virtual_path,
                    transfer.size,
                    token,
                )
            )
            if response.allowed:
                allowed += 1
                downloads._file_transfer_init(
                    make_file_init(
                        username,
                        token,
                        FakeSock(f"burst-{index}"),
                    )
                )
            else:
                rejected += 1

        self.assertEqual(allowed, 1)
        self.assertEqual(rejected, burst_size - 1)
        self.assertEqual(open_file_handle_count(downloads), 1)
        self.assertEqual(socket_owner_count(downloads), 1)
        self.assertEqual(len(downloads.queued_users[username]), burst_size - 1)
        self.assertIs(downloads.active_users[username][token], transfers[0])


if __name__ == "__main__":
    import unittest

    unittest.main()
