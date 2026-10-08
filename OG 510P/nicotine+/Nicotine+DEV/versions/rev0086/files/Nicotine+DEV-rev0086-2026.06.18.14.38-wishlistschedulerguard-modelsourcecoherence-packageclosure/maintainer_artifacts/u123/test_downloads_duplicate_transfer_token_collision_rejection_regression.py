# SPDX-License-Identifier: GPL-3.0-or-later
"""Selected invariant: a peer token cannot be rebound to another download."""
from __future__ import annotations

from pynicotine.slskmessages import TransferRejectReason
from pynicotine.transfers import TransferStatus

from u123_harness import (
    FakeSock,
    U123TestCase,
    make_file_init,
    make_transfer_request,
    queue_download,
)


class DuplicateDownloadTransferTokenCollisionRejectionRegression(U123TestCase):
    def test_duplicate_token_request_preserves_existing_f_connection_owner(self):
        downloads = self.make_downloads()
        username = "attacker-peer"
        token = 4242
        first = queue_download(downloads, username, "Music\\A.flac", 111)
        second = queue_download(downloads, username, "Music\\B.flac", 222)

        first_response = downloads._transfer_request_downloads(
            make_transfer_request(username, first.virtual_path, first.size, token)
        )
        self.assertTrue(first_response.allowed)

        sock = FakeSock("first")
        downloads._file_transfer_init(make_file_init(username, token, sock))
        self.assertIs(downloads.active_users[username][token], first)
        self.assertIs(first.sock, sock)
        self.assertFalse(first.file_handle.closed)

        second_response = downloads._transfer_request_downloads(
            make_transfer_request(username, second.virtual_path, second.size, token)
        )
        self.assertFalse(second_response.allowed)
        self.assertEqual(second_response.reason, TransferRejectReason.QUEUED)
        self.assertIs(downloads.active_users[username][token], first)
        self.assertIs(first.sock, sock)
        self.assertIs(downloads.queued_users[username][second.virtual_path], second)
        self.assertIn(second, downloads.queued_transfers)
        self.assertIsNone(second.token)
        self.assertEqual(second.status, TransferStatus.QUEUED)

        downloads._file_download_progress(
            username, token, bytes_left=first.size - 17, speed=321
        )
        self.assertEqual(first.current_byte_offset, 17)
        self.assertEqual(first.speed, 321)
        self.assertIsNone(second.current_byte_offset)


if __name__ == "__main__":
    import unittest

    unittest.main()
