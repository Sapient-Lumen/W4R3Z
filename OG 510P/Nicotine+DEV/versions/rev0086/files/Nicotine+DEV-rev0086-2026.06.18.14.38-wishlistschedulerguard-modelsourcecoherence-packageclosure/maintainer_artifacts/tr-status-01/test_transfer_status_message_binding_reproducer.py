"""TR-STATUS-01 current-behavior reproducer for Nicotine+ download status messages.

Run from an upstream checkout with:

    python -m pytest test_transfer_status_message_binding_reproducer.py

Or run outside the checkout with:

    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest test_transfer_status_message_binding_reproducer.py

These tests intentionally assert current behavior, not a fixed invariant. They
exercise the download-side handling of UploadFailed, UploadDenied, and
PlaceInQueueResponse messages, each of which carries a filename/path but no
transfer token or response-generation field.
"""
from __future__ import annotations

import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))
    sys.path.insert(0, str(here.parent.parent))

from pynicotine.slskmessages import (  # noqa: E402
    CloseConnection,
    PlaceInQueueResponse,
    QueueUpload,
    TransferRejectReason,
    UploadDenied,
    UploadFailed,
    UserStatus,
)
from pynicotine.transfers import Transfer, TransferStatus  # noqa: E402
import pynicotine.downloads as downloads_module  # noqa: E402
import pynicotine.transfers as transfers_module  # noqa: E402


class FakeSock:
    def __init__(self, name="file-socket"):
        self.name = name

    def __repr__(self):
        return self.name


class FakeEvents:
    def __init__(self):
        self.connected = []
        self.emitted = []
        self.scheduled = []
        self.cancelled = []
        self._next_id = 1000

    def connect(self, event_name, callback):
        self.connected.append((event_name, getattr(callback, "__name__", repr(callback))))

    def emit(self, event_name, *args, **kwargs):
        self.emitted.append((event_name, args, kwargs))

    def schedule(self, delay, callback, callback_args=None, repeat=False):
        self._next_id += 1
        self.scheduled.append({
            "id": self._next_id,
            "delay": delay,
            "callback": getattr(callback, "__name__", repr(callback)),
            "callback_args": callback_args,
            "repeat": repeat,
        })
        return self._next_id

    def cancel_scheduled(self, event_id):
        self.cancelled.append(event_id)


class FakeLog:
    def __init__(self):
        self.entries = []

    def add(self, message, args=None):
        self.entries.append(("add", message, args))

    def add_transfer(self, message, args=None):
        self.entries.append(("transfer", message, args))

    def add_download(self, message, args=None):
        self.entries.append(("download", message, args))


class FakeCore:
    def __init__(self):
        self.network_messages = []
        self.peer_messages = []
        self.users = SimpleNamespace(
            login_status=UserStatus.ONLINE,
            statuses=defaultdict(lambda: UserStatus.ONLINE),
            watched=[],
            unwatched=[],
            watch_user=lambda username, context=None: self.users.watched.append((username, context)),
            unwatch_user=lambda username, context=None: self.users.unwatched.append((username, context)),
        )
        self.shares = SimpleNamespace(initialized=True)
        self.statistics = SimpleNamespace(append_stat_value=lambda *args, **kwargs: None)
        self.pluginhandler = SimpleNamespace(download_started_notification=lambda *args, **kwargs: None)
        self.notifications = SimpleNamespace(show_download_notification=lambda *args, **kwargs: None)

    def send_message_to_network_thread(self, msg):
        self.network_messages.append(msg)

    def send_message_to_peer(self, username, msg):
        self.peer_messages.append((username, msg))


class FakeConfig:
    def __init__(self, data_folder_path):
        self.data_folder_path = data_folder_path
        self.sections = {
            "transfers": {
                "enablefilters": False,
                "downloadregexp": "",
                "autoclear_downloads": False,
                "use_download_speed_limit": "primary",
                "downloadlimit": 0,
                "downloadlimitalt": 0,
                "afterfinish": "",
                "afterfolder": "",
                "downloaddir": data_folder_path,
                "incompletedir": data_folder_path,
                "usernamesubfolders": False,
            },
            "notifications": {
                "notification_popup_file": False,
                "notification_popup_folder": False,
            },
            "statistics": {"since_timestamp": 0},
        }

    def create_data_folder(self):
        Path(self.data_folder_path).mkdir(parents=True, exist_ok=True)


@pytest.fixture()
def harness(monkeypatch, tmp_path):
    fake_events = FakeEvents()
    fake_core = FakeCore()
    fake_log = FakeLog()
    fake_config = FakeConfig(str(tmp_path))

    monkeypatch.setattr(downloads_module, "events", fake_events)
    monkeypatch.setattr(transfers_module, "events", fake_events)
    monkeypatch.setattr(downloads_module, "core", fake_core)
    monkeypatch.setattr(transfers_module, "core", fake_core)
    monkeypatch.setattr(downloads_module, "log", fake_log)
    monkeypatch.setattr(transfers_module, "log", fake_log)
    monkeypatch.setattr(downloads_module, "config", fake_config)
    monkeypatch.setattr(transfers_module, "config", fake_config)

    monkeypatch.setattr(
        downloads_module.Downloads,
        "get_complete_download_file_path",
        lambda self, *args, **kwargs: (str(tmp_path / "complete.bin"), False),
    )

    downloads = downloads_module.Downloads()
    return SimpleNamespace(downloads=downloads, core=fake_core, events=fake_events, log=fake_log)


def add_queued(downloads, username="victim", virtual_path="folder\\song.flac"):
    transfer = Transfer(username, virtual_path, folder_path=tempfile.gettempdir(), size=1234,
                        status=TransferStatus.QUEUED)
    downloads.transfers[username + virtual_path] = transfer
    downloads.queued_users[username][virtual_path] = transfer
    downloads.queued_transfers[transfer] = None
    downloads._user_queue_sizes[username] += transfer.size
    return transfer


def add_active(downloads, username="victim", virtual_path="folder\\song.flac", token=4242):
    transfer = Transfer(username, virtual_path, folder_path=tempfile.gettempdir(), size=1234,
                        status=TransferStatus.TRANSFERRING, current_byte_offset=128)
    transfer.token = token
    transfer.sock = FakeSock("active-file-socket")
    transfer.request_timer_id = 777
    downloads.transfers[username + virtual_path] = transfer
    downloads.active_users[username][token] = transfer
    return transfer


def _claiming_message(msg, username):
    msg.username = username
    return msg


def test_upload_failed_closes_active_download_and_requeues_by_claimed_username_and_path(harness):
    downloads = harness.downloads
    transfer = add_active(downloads)

    downloads._upload_failed(_claiming_message(UploadFailed(transfer.virtual_path), transfer.username))

    assert transfer.sock is None
    assert transfer.token is None
    assert transfer.status == TransferStatus.QUEUED
    assert transfer.legacy_attempt is True
    assert transfer.retry_attempt is True
    assert transfer.virtual_path in downloads.queued_users[transfer.username]
    assert transfer.username not in downloads.active_users
    assert harness.events.cancelled == [777]
    assert any(isinstance(msg, CloseConnection) for msg in harness.core.network_messages)
    assert any(isinstance(msg, QueueUpload) for _username, msg in harness.core.peer_messages)


def test_upload_denied_moves_queued_download_to_peer_supplied_failure_reason_by_claimed_username_and_path(harness):
    downloads = harness.downloads
    transfer = add_queued(downloads)
    reason = "Remote status string chosen by peer"

    downloads._upload_denied(_claiming_message(UploadDenied(transfer.virtual_path, reason), transfer.username))

    assert transfer.virtual_path not in downloads.queued_users.get(transfer.username, {})
    assert transfer.virtual_path in downloads.failed_users[transfer.username]
    assert transfer.status == reason


def test_upload_denied_queue_limit_reason_can_force_limited_retry_state_by_claimed_username_and_path(harness):
    downloads = harness.downloads
    transfer = add_queued(downloads)

    downloads._upload_denied(_claiming_message(UploadDenied(
        transfer.virtual_path, TransferRejectReason.TOO_MANY_FILES), transfer.username))

    assert transfer.status == TransferRejectReason.QUEUED
    assert transfer.virtual_path in downloads.failed_users[transfer.username]


def test_place_in_queue_response_updates_visible_queue_position_by_claimed_username_and_path(harness):
    downloads = harness.downloads
    transfer = add_queued(downloads)
    large_position = 2**32 - 1

    downloads._place_in_queue_response(_claiming_message(
        PlaceInQueueResponse(transfer.virtual_path, large_position), transfer.username))

    assert transfer.queue_position == large_position
    assert ("update-download", (transfer, False), {}) in harness.events.emitted
