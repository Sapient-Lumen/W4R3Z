# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness: passes unpatched and fails after collision rejection."""
from __future__ import annotations

from pynicotine.transfers import TransferStatus

from u123_harness import FakeSock
from u123_harness import U123TestCase
from u123_harness import make_file_init
from u123_harness import make_transfer_request
from u123_harness import queue_download


class DuplicateDownloadTransferTokenCurrentBehaviorWitness(U123TestCase):
    def test_duplicate_token_stale_timeout_orphans_later_f_connection_session(self):
        downloads = self.make_downloads()
        username = "attacker-peer"
        token = 4242
        first = queue_download(downloads, username, "Music\\A.flac", 111)
        second = queue_download(downloads, username, "Music\\B.flac", 222)

        downloads._transfer_request(
            make_transfer_request(username, first.virtual_path, first.size, token)
        )
        first_timer = first.request_timer_id
        self.assertIs(downloads.active_users[username][token], first)

        downloads._transfer_request(
            make_transfer_request(username, second.virtual_path, second.size, token)
        )
        self.assertIs(downloads.active_users[username][token], second)

        sock = FakeSock("witness")
        downloads._file_transfer_init(make_file_init(username, token, sock))
        self.assertIs(downloads.active_users[username][token], second)
        self.assertIs(second.sock, sock)
        self.assertFalse(second.file_handle.closed)
        self.assertEqual(first.request_timer_id, first_timer)

        downloads._transfer_timeout(first)
        self.assertNotIn(token, downloads.active_users.get(username, {}))

        downloads._file_download_progress(
            username,
            token,
            bytes_left=second.size - 17,
            speed=321,
        )
        self.assertIsNone(second.current_byte_offset)
        self.assertFalse(second.file_handle.closed)

        downloads._file_connection_closed(username, token, sock)
        self.assertEqual(second.status, TransferStatus.TRANSFERRING)
        self.assertFalse(second.file_handle.closed)


if __name__ == "__main__":
    import unittest

    unittest.main()
