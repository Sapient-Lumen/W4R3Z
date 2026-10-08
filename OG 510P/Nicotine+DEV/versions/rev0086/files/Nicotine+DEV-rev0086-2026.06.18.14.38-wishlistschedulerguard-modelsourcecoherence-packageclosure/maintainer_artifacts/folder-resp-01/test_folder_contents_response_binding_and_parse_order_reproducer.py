"""FOLDER-RESP-01 current-behavior reproducer for rev0014.

Run from an upstream checkout with:

    python -m pytest test_folder_contents_response_binding_and_parse_order_reproducer.py

Or outside the checkout with:

    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest \
        test_folder_contents_response_binding_and_parse_order_reproducer.py

These tests intentionally assert current behavior, not desired fixed behavior.
They exercise FolderContentsResponse parsing and download-side request-consumption
rules around username+folder-path matching and missing token/generation binding.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
import tracemalloc
import zlib
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

from pynicotine.slskmessages import FolderContentsResponse, QueueUpload, UserStatus  # noqa: E402
from pynicotine.transfers import TransferStatus  # noqa: E402
import pynicotine.downloads as downloads_module  # noqa: E402
import pynicotine.transfers as transfers_module  # noqa: E402


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


def _pack_folder_payload(token, root_folder, folders):
    """Build compressed FolderContentsResponse bytes without relying on branch constructor details."""
    msg = bytearray()
    msg += FolderContentsResponse.pack_uint32(token)
    msg += FolderContentsResponse.pack_string(root_folder)
    msg += FolderContentsResponse.pack_uint32(len(folders))

    for folder, files in folders.items():
        msg += FolderContentsResponse.pack_string(folder)
        msg += FolderContentsResponse.pack_uint32(len(files))
        for name, size in files:
            msg += FolderContentsResponse.pack_uint8(1)
            msg += FolderContentsResponse.pack_string(name)
            msg += FolderContentsResponse.pack_uint64(size)
            msg += FolderContentsResponse.pack_uint32(0)  # obsolete extension length
            msg += FolderContentsResponse.pack_uint32(0)  # number of attributes
    return zlib.compress(bytes(msg))


def _parse_folder_response(payload, username="peer", allowed_key=None):
    try:
        msg = FolderContentsResponse(msg_content=payload)
        msg.username = username
        msg.allowed_responses = set()
        if allowed_key is not None:
            msg.allowed_responses.add(allowed_key)
        msg.parse_network_message()
        return msg
    except TypeError:
        msg = FolderContentsResponse()
        msg.username = username
        msg.parse_network_message(payload)
        return msg


def _make_requested_folder(username, folder_path, download_folder_path):
    RequestedFolder = downloads_module.RequestedFolder
    try:
        rf = RequestedFolder(username, folder_path, download_folder_path)
    except TypeError:
        rf = RequestedFolder(username, folder_path)
    rf.request_timer_id = 777
    return rf


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
        raising=False,
    )

    # Isolate the folder-response handler from actual filesystem/queue side effects while preserving the call shape.
    recorded_downloads = []

    def record_enqueue(self, username, virtual_path, folder_path=None, size=0, file_attributes=None, **kwargs):
        recorded_downloads.append({
            "username": username,
            "virtual_path": virtual_path,
            "folder_path": folder_path,
            "size": size,
            "file_attributes": file_attributes,
            "kwargs": kwargs,
        })

    monkeypatch.setattr(downloads_module.Downloads, "enqueue_download", record_enqueue, raising=True)

    downloads = downloads_module.Downloads()
    return SimpleNamespace(
        downloads=downloads,
        core=fake_core,
        events=fake_events,
        log=fake_log,
        recorded_downloads=recorded_downloads,
        tmp_path=tmp_path,
    )


def test_folder_contents_response_parser_keeps_peer_token_without_comparing_requested_token():
    username = "folder_peer"
    folder = "Music\\Album"
    requested_token = 123456
    peer_token = 0xDEADBEEF
    payload = _pack_folder_payload(peer_token, folder, {folder: [("track01.flac", 1111)]})

    msg = _parse_folder_response(payload, username=username, allowed_key=username + folder)

    assert peer_token != requested_token
    assert msg.token == peer_token
    assert msg.dir == folder
    assert msg.list[folder][0][1] == "track01.flac"


def test_pending_folder_response_with_wrong_token_is_consumed_by_username_and_folder_path(harness):
    username = "folder_peer"
    folder = "Music\\Album"
    wrong_token = 0xABCDEF01
    downloads = harness.downloads
    downloads._requested_folders[username][folder] = _make_requested_folder(username, folder, str(harness.tmp_path))

    msg = SimpleNamespace(
        username=username,
        dir=folder,
        token=wrong_token,
        list={folder: [(1, "track01.flac", 1111, None, {}), (1, "track02.flac", 2222, None, {})]},
    )

    try:
        downloads._folder_contents_response(msg, check_num_files=False)
    except TypeError:
        downloads._folder_contents_response(msg)

    assert harness.events.cancelled == [777]
    assert folder not in downloads._requested_folders.get(username, {})

    if harness.recorded_downloads:
        assert [entry["virtual_path"] for entry in harness.recorded_downloads] == [
            "Music\\Album\\track01.flac",
            "Music\\Album\\track02.flac",
        ]
    else:
        # Newer master routes parsed folder contents to the download dialog/UI layer but still consumes the pending request.
        assert msg.token == wrong_token
        assert msg.dir == folder


def test_folder_contents_response_parser_materializes_nonmatching_folders_before_requested_folder_filter():
    username = "folder_peer"
    folder = "Music\\Album"
    folders = {folder: [("wanted.flac", 1)]}
    for index in range(64):
        folders[f"Other\\Album{index:03d}"] = [(f"noise{index:03d}.flac", index + 100)]

    payload = _pack_folder_payload(909090, folder, folders)
    msg = _parse_folder_response(payload, username=username, allowed_key=username + folder)

    assert folder in msg.list
    assert len(msg.list) == 65
    assert sum(len(files) for files in msg.list.values()) == 65


def test_nonmatching_folder_contents_response_cancels_pending_request_without_queueing(harness):
    username = "folder_peer"
    folder = "Music\\Album"
    downloads = harness.downloads
    downloads._requested_folders[username][folder] = _make_requested_folder(username, folder, str(harness.tmp_path))

    msg = SimpleNamespace(
        username=username,
        dir=folder,
        token=0x33333333,
        list={"Other\\Album": [(1, "noise.flac", 999, None, {})]},
    )

    try:
        downloads._folder_contents_response(msg, check_num_files=False)
    except TypeError:
        downloads._folder_contents_response(msg)

    assert harness.events.cancelled == [777]
    assert harness.recorded_downloads == []
    assert folder not in downloads._requested_folders.get(username, {})


def test_rejected_or_unmatched_folder_response_still_decompresses_peer_controlled_directory_prefix():
    username = "folder_peer"
    huge_folder = "X" * 250_000
    payload = _pack_folder_payload(12345, huge_folder, {})

    tracemalloc.start()
    start = time.perf_counter()
    msg = _parse_folder_response(payload, username=username, allowed_key=None)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert len(payload) < len(huge_folder) // 100
    assert msg.dir == huge_folder
    assert peak >= len(huge_folder)
    assert elapsed_ms >= 0
