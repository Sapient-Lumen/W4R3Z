# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit-style reproducer for duplicate peer-supplied download transfer tokens.

This is intentionally a reproducer, not a final regression test to merge as-is.
It runs without network sockets and demonstrates the current invariant violation:

a stale timeout belonging to the first transfer can delete the active-map entry
for a later same-user/same-token F-connection session.

Expected maintainer use:
  1. Drop this file into pynicotine/tests/unit/ or run it with PYTHONPATH pointing
     at a Nicotine+ source tree.
  2. Confirm it reproduces the current behavior.
  3. Convert the final assertions into fixed-behavior assertions once a patch is
     written; the core desired assertion is that deactivation of t1 must not
     remove the active mapping for t2.
"""

from __future__ import annotations

import collections
import os
import tempfile
import types
import unittest

import pynicotine.config as config_mod
import pynicotine.downloads as downloads_mod
import pynicotine.transfers as transfers_mod

from pynicotine.downloads import Downloads
from pynicotine.slskmessages import FileTransferInit
from pynicotine.slskmessages import TransferDirection
from pynicotine.slskmessages import TransferRequest
from pynicotine.transfers import Transfer
from pynicotine.transfers import TransferStatus


class FakeSock:
    def __repr__(self):
        return "<FakeSock u123>"


class StubUsers:
    login_status = 2

    def __init__(self):
        self.watches = []
        self.unwatches = []
        self.statuses = {}

    def watch_user(self, username, context=None):
        self.watches.append((username, context))

    def unwatch_user(self, username, context=None):
        self.unwatches.append((username, context))


class StubCore:
    def __init__(self):
        self.users = StubUsers()
        self.sent_peer = []
        self.sent_network = []
        self.statistics = types.SimpleNamespace(append_stat_value=lambda *args, **kwargs: None)
        self.notifications = types.SimpleNamespace(show_download_notification=lambda *args, **kwargs: None)
        self.pluginhandler = types.SimpleNamespace(
            download_started_notification=lambda *args, **kwargs: None,
            download_finished_notification=lambda *args, **kwargs: None,
            upload_queued_notification=lambda *args, **kwargs: None,
        )

    def send_message_to_peer(self, username, msg):
        self.sent_peer.append((username, msg.__class__.__name__, getattr(msg, "token", None), getattr(msg, "allowed", None)))

    def send_message_to_network_thread(self, msg):
        self.sent_network.append((msg.__class__.__name__, getattr(msg, "token", None), repr(getattr(msg, "sock", None))))


class StubEvents:
    def __init__(self):
        self.cancelled = []
        self._next_id = 1000

    def schedule(self, delay=None, callback=None, callback_args=(), repeat=False, **kwargs):
        self._next_id += 1
        return f"timer-{self._next_id}"

    def cancel_scheduled(self, timer_id):
        self.cancelled.append(timer_id)

    def emit(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass


class StubLog:
    def add(self, *args, **kwargs):
        pass

    def add_transfer(self, *args, **kwargs):
        pass

    def add_download(self, *args, **kwargs):
        pass


class ProbeDownloads(Downloads):
    __slots__ = ("tmpdir",)

    def get_incomplete_download_folder(self):
        return os.path.join(self.tmpdir, "incomplete")

    def get_incomplete_download_file_path(self, username, virtual_path):
        safe = f"{username}_{virtual_path}".replace("\\", "_").replace("/", "_")
        return os.path.join(self.get_incomplete_download_folder(), "INCOMPLETE_" + safe)

    def get_complete_download_file_path(self, username, virtual_path, size, download_folder_path=None):
        safe = f"{username}_{virtual_path}".replace("\\", "_").replace("/", "_")
        return os.path.join(self.tmpdir, "complete", safe), False

    def _update_transfer(self, transfer, update_parent=True):
        # Avoid GUI/event side effects; the state mutation under test already happened.
        return None


def make_downloads(tmpdir):
    obj = ProbeDownloads.__new__(ProbeDownloads)
    fields = {
        "transfers": {},
        "queued_transfers": {},
        "queued_users": collections.defaultdict(dict),
        "active_users": collections.defaultdict(dict),
        "failed_users": collections.defaultdict(dict),
        "transfers_file_path": os.path.join(tmpdir, "downloads.json"),
        "total_bandwidth": 0,
        "_name": "downloads",
        "_allow_saving_transfers": False,
        "_online_users": set(),
        "_user_queue_limits": collections.defaultdict(int),
        "_user_queue_sizes": collections.defaultdict(int),
        "_requested_folders": collections.defaultdict(dict),
        "_requested_folder_token": 0,
        "_folder_basename_byte_limits": {},
        "_pending_queue_messages": {},
        "_download_queue_timer_id": None,
        "_retry_connection_downloads_timer_id": None,
        "_retry_io_downloads_timer_id": None,
    }
    for key, value in fields.items():
        setattr(obj, key, value)
    obj.tmpdir = tmpdir
    return obj


def queue_download(downloads, username, virtual_path, size):
    transfer = Transfer(username=username, virtual_path=virtual_path, folder_path=os.path.join(downloads.tmpdir, "complete"), size=size)
    transfer.status = TransferStatus.QUEUED
    downloads.transfers[username + virtual_path] = transfer
    downloads.queued_transfers[transfer] = None
    downloads.queued_users[username][virtual_path] = transfer
    downloads._user_queue_sizes[username] += size
    return transfer


def make_transfer_request(username, virtual_path, size, token):
    msg = TransferRequest(direction=TransferDirection.UPLOAD, token=token, file=virtual_path, filesize=size)
    msg.username = username
    return msg


def make_file_init(username, token, sock):
    msg = FileTransferInit(token=token, is_outgoing=False)
    msg.username = username
    msg.token = token
    msg.is_outgoing = False
    msg.sock = sock
    return msg


class DuplicateDownloadTransferTokenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="nplus-u123-test-")
        tmpdir = self.tmp.name
        os.makedirs(os.path.join(tmpdir, "incomplete"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "complete"), exist_ok=True)

        self.core = StubCore()
        self.events = StubEvents()
        self.log = StubLog()
        self.config = types.SimpleNamespace(
            data_folder_path=tmpdir,
            sections={
                "transfers": {
                    "incompletedir": os.path.join(tmpdir, "incomplete"),
                    "downloaddir": os.path.join(tmpdir, "complete"),
                    "enablefilters": False,
                    "downloadregexp": "",
                    "afterfinish": "",
                    "afterfolder": "",
                    "shownotification": False,
                    "autoclear_downloads": False,
                },
                "notifications": {"notification_popup_file": False},
            },
        )
        for mod in (downloads_mod, transfers_mod):
            mod.core = self.core
            mod.events = self.events
            mod.log = self.log
            mod.config = self.config
        try:
            config_mod.config = self.config
        except Exception:
            pass

    def tearDown(self):
        self.tmp.cleanup()

    def test_duplicate_token_stale_timeout_orphans_later_f_connection_session(self):
        downloads = make_downloads(self.tmp.name)
        username = "attacker-peer"
        token = 4242
        first = queue_download(downloads, username, "Music\\A.flac", 111)
        second = queue_download(downloads, username, "Music\\B.flac", 222)

        downloads._transfer_request(make_transfer_request(username, first.virtual_path, first.size, token))
        first_timer = first.request_timer_id
        self.assertIs(downloads.active_users[username][token], first)

        downloads._transfer_request(make_transfer_request(username, second.virtual_path, second.size, token))
        self.assertIs(downloads.active_users[username][token], second)

        sock = FakeSock()
        downloads._file_transfer_init(make_file_init(username, token, sock))
        self.assertIs(downloads.active_users[username][token], second)
        self.assertIs(second.sock, sock)
        self.assertFalse(second.file_handle.closed)

        # Current-bug assertion: the stale timer for the first transfer deactivates
        # the shared username+token slot even though that slot now points at second.
        self.assertEqual(first.request_timer_id, first_timer)
        downloads._transfer_timeout(first)
        self.assertNotIn(token, downloads.active_users.get(username, {}))

        # Network-thread callbacks for the second session are now ignored.
        downloads._file_download_progress(username, token, bytes_left=second.size - 17, speed=321)
        self.assertIsNone(second.current_byte_offset)
        self.assertFalse(second.file_handle.closed)

        downloads._file_connection_closed(username, token, sock)
        self.assertEqual(second.status, TransferStatus.TRANSFERRING)
        self.assertFalse(second.file_handle.closed)

        # Probe cleanup only.
        second.file_handle.close()


if __name__ == "__main__":
    unittest.main()
