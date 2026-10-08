# SPDX-License-Identifier: GPL-3.0-or-later
"""Stress-only experiment for an occupied slot whose owner is also requeued.

The harness deliberately constructs a transfer that is simultaneously active and
queued.  Rev0073 did not establish that this state is reachable through the
supported runtime.  This is therefore not part of the selected U-123 acceptance
contract. It only distinguishes the minimal patch from a stricter fail-closed
alternative.
"""
from __future__ import annotations

from u123_harness import U123TestCase, make_transfer_request, queue_download


class DuplicateDownloadTransferTokenSameObjectReentryExperiment(U123TestCase):
    def test_same_object_cannot_reenter_an_occupied_token_slot(self):
        downloads = self.make_downloads()
        username = "attacker-peer"
        token = 4242
        transfer = queue_download(downloads, username, "Music\\A.flac", 111)

        response = downloads._transfer_request_downloads(
            make_transfer_request(username, transfer.virtual_path, transfer.size, token)
        )
        self.assertTrue(response.allowed)
        first_timer = transfer.request_timer_id

        # Deliberately synthesize an inconsistent state.  No supported transition
        # producing this overlap was demonstrated in the current-source trace.
        downloads.queued_users[username][transfer.virtual_path] = transfer
        downloads.queued_transfers[transfer] = None
        downloads._user_queue_sizes[username] += transfer.size

        duplicate = downloads._transfer_request_downloads(
            make_transfer_request(username, transfer.virtual_path, transfer.size, token)
        )
        self.assertFalse(duplicate.allowed)
        self.assertIs(downloads.active_users[username][token], transfer)
        self.assertEqual(transfer.request_timer_id, first_timer)


if __name__ == "__main__":
    import unittest

    unittest.main()
