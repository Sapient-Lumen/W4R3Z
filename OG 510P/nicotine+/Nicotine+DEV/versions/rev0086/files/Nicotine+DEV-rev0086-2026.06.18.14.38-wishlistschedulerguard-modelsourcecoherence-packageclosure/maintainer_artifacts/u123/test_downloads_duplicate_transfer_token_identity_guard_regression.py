# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixed invariant: stale cleanup cannot delete another object's active slot."""
from __future__ import annotations

from pynicotine.transfers import TransferStatus

from u123_harness import FakeSock
from u123_harness import U123TestCase
from u123_harness import make_file_init
from u123_harness import make_transfer_request
from u123_harness import queue_download


class DuplicateDownloadTransferTokenIdentityGuardRegression(U123TestCase):
    def test_stale_timeout_preserves_newer_slot_and_cleans_old_transfer(self):
        downloads = self.make_downloads()
        username = "attacker-peer"
        token = 4242
        first = queue_download(downloads, username, "Music\\A.flac", 111)
        second = queue_download(downloads, username, "Music\\B.flac", 222)

        response = downloads._transfer_request_downloads(
            make_transfer_request(username, first.virtual_path, first.size, token)
        )
        self.assertTrue(response.allowed)
        first_timer = first.request_timer_id

        # Construct the post-collision ownership shape directly. This isolates
        # deactivation identity from the admission guard tested elsewhere.
        downloads._dequeue_transfer(second)
        downloads._activate_transfer(second, token)
        second_timer = second.request_timer_id
        sock = FakeSock("replacement")
        downloads._file_transfer_init(make_file_init(username, token, sock))

        downloads._transfer_timeout(first)

        self.assertIs(downloads.active_users[username][token], second)
        self.assertIs(second.sock, sock)
        self.assertEqual(second.request_timer_id, second_timer)
        self.assertIsNone(first.token)
        self.assertIsNone(first.request_timer_id)
        self.assertIn(first_timer, self.events.cancelled)
        self.assertEqual(first.status, TransferStatus.CONNECTION_TIMEOUT)
        self.assertIs(downloads.failed_users[username][first.virtual_path], first)

        downloads._file_download_progress(
            username,
            token,
            bytes_left=second.size - 17,
            speed=321,
        )
        self.assertEqual(second.current_byte_offset, 17)
        self.assertEqual(second.speed, 321)


if __name__ == "__main__":
    import unittest

    unittest.main()
