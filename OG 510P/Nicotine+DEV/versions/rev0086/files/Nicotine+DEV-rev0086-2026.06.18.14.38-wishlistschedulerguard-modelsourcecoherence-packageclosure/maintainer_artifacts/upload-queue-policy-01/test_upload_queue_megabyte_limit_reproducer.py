from __future__ import annotations

import collections
import os
import sys
import types
from pathlib import Path

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

import pynicotine.uploads as uploads_mod  # noqa: E402
import pynicotine.transfers as transfers_mod  # noqa: E402
from pynicotine.shares import PermissionLevel  # noqa: E402
from pynicotine.slskmessages import QueueUpload, TransferDirection, TransferRejectReason, TransferRequest  # noqa: E402
from pynicotine.transfers import Transfer, TransferStatus  # noqa: E402
from pynicotine.uploads import Uploads  # noqa: E402


ONE_MIB = 1024 * 1024
USERNAME = "queue_peer"
ADDR = ("203.0.113.77", 2234)


class StubUsers:
    login_status = 2

    def __init__(self):
        self.watches = []
        self.unwatches = []
        self.statuses = {}
        self.addresses = {}
        self.privileged = set()

    def watch_user(self, username, context=None):
        self.watches.append((username, context))

    def unwatch_user(self, username, context=None):
        self.unwatches.append((username, context))


class StubShares:
    rescanning = False

    def __init__(self, file_sizes=None):
        self.file_sizes = file_sizes or {}

    def check_user_permission(self, username, ip_address):
        return PermissionLevel.PUBLIC, None

    def virtual2real(self, virtual_path, *args, **kwargs):
        return os.path.join("/virtual/share", virtual_path.replace("\\", os.sep))

    def file_is_shared(self, username, virtual_path, real_path):
        try:
            return True, self.file_sizes[virtual_path]
        except KeyError:
            return False, 0


class StubCore:
    def __init__(self, shares=None):
        self.users = StubUsers()
        self.buddies = types.SimpleNamespace(users={})
        self.shares = shares or StubShares()
        self.sent_peer = []
        self.sent_network = []
        self.statistics = types.SimpleNamespace(append_stat_value=lambda *args, **kwargs: None)
        self.pluginhandler = types.SimpleNamespace(upload_queued_notification=lambda *args, **kwargs: None)
        self.notifications = types.SimpleNamespace(show_upload_notification=lambda *args, **kwargs: None)

    def send_message_to_peer(self, username, msg):
        self.sent_peer.append((username, msg))

    def send_message_to_network_thread(self, msg):
        self.sent_network.append(msg)


class StubEvents:
    def __init__(self):
        self.emitted = []
        self.cancelled = []
        self._next_id = 9000

    def connect(self, *args, **kwargs):
        return None

    def emit(self, *args, **kwargs):
        self.emitted.append((args, kwargs))

    def emit_main_thread(self, *args, **kwargs):
        self.emitted.append((args, kwargs))

    def schedule(self, delay=None, callback=None, callback_args=(), repeat=False, **kwargs):
        self._next_id += 1
        return f"timer-{self._next_id}"

    def cancel_scheduled(self, timer_id):
        self.cancelled.append(timer_id)


class StubLog:
    def add(self, *args, **kwargs):
        pass

    def add_transfer(self, *args, **kwargs):
        pass

    def add_upload(self, *args, **kwargs):
        pass


class ProbeUploads(Uploads):
    __slots__ = ()

    def _update_transfer(self, transfer, update_parent=True):
        return None

    def _check_upload_queue(self, upload_candidate=None):
        # Keep queued transfers queued so admission/accounting is directly observable.
        return None


def _set_if_slot(obj, key, value):
    try:
        setattr(obj, key, value)
    except AttributeError:
        pass


def make_uploads():
    obj = ProbeUploads.__new__(ProbeUploads)
    fields = {
        "transfers": {},
        "queued_transfers": {},
        "queued_users": collections.defaultdict(dict),
        "active_users": collections.defaultdict(dict),
        "failed_users": collections.defaultdict(dict),
        "transfers_file_path": os.devnull,
        "total_bandwidth": 0,
        "_name": "uploads",
        "_allow_saving_transfers": False,
        "_online_users": set(),
        "_user_queue_limits": collections.defaultdict(int),
        "_user_queue_sizes": collections.defaultdict(int),
        "pending_shutdown": False,
        "upload_speed": 0,
        "token": 123456,
        "_queue_positions": {},
        "_queue_position_users": collections.defaultdict(dict),
        "_privileged_position_requested": False,
        "_pending_network_msgs": [],
        "_queue_notification_users": collections.defaultdict(list),
        "_user_update_counter": 0,
        "_user_update_counters": {},
        "_queue_notification_timer_id": None,
        "_upload_queue_timer_id": None,
        "_retry_failed_uploads_timer_id": None,
    }
    for key, value in fields.items():
        _set_if_slot(obj, key, value)
    return obj


@pytest.fixture(autouse=True)
def patch_global_modules(monkeypatch, tmp_path):
    events = StubEvents()
    log = StubLog()
    config = types.SimpleNamespace(
        data_folder_path=str(tmp_path),
        sections={
            "transfers": {
                "filelimit": 100,
                "queuelimit": 1,  # MiB per user
                "friendsnolimits": False,
                "preferfriends": False,
                "fifoqueue": False,
                "useupslots": True,
                "uploadslots": 1,
                "use_upload_speed_limit": "unlimited",
                "uploadlimit": 1000,
                "uploadlimitalt": 100,
                "uploadbandwidth": 0,
                "limitby": True,
                "autoclear_uploads": False,
            },
            "notifications": {"notification_popup_file": False, "notification_popup_queued_upload": False},
        },
    )
    core = StubCore()
    for mod in (uploads_mod, transfers_mod):
        monkeypatch.setattr(mod, "events", events, raising=False)
        monkeypatch.setattr(mod, "log", log, raising=False)
        monkeypatch.setattr(mod, "core", core, raising=False)
        monkeypatch.setattr(mod, "config", config, raising=False)
    return core, events, config


def queue_upload_message(virtual_path: str) -> QueueUpload:
    msg = QueueUpload(virtual_path)
    msg.username = USERNAME
    msg.addr = ADDR
    return msg


def legacy_download_request(virtual_path: str, token: int = 8080) -> TransferRequest:
    msg = TransferRequest(direction=TransferDirection.DOWNLOAD, token=token, file=virtual_path)
    msg.username = USERNAME
    msg.addr = ADDR
    return msg


def add_existing_queued_upload(uploads: Uploads, username: str, virtual_path: str, size: int) -> Transfer:
    transfer = Transfer(username=username, virtual_path=virtual_path, folder_path="/virtual/share", size=size)
    uploads.transfers[username + virtual_path] = transfer
    uploads._enqueue_transfer(transfer)
    return transfer


def add_active_upload_for_same_user(uploads: Uploads, username: str, virtual_path: str = "Music\\active.bin") -> Transfer:
    transfer = Transfer(username=username, virtual_path=virtual_path, folder_path="/virtual/share", size=1)
    transfer.status = TransferStatus.TRANSFERRING
    uploads.transfers[username + virtual_path] = transfer
    transfers_mod.Transfers._activate_transfer(uploads, transfer, token=777)
    return transfer


def only_peer_message(core: StubCore):
    assert len(core.sent_peer) == 1
    return core.sent_peer[0][1]


def test_modern_queue_upload_accepts_single_candidate_larger_than_megabyte_limit(patch_global_modules):
    core, _events, _config = patch_global_modules
    large_file = "Music\\oversized.flac"
    core.shares = StubShares({large_file: 2 * ONE_MIB})
    uploads = make_uploads()

    uploads._queue_upload(queue_upload_message(large_file))

    assert large_file in uploads.queued_users[USERNAME]
    assert uploads._user_queue_sizes[USERNAME] == 2 * ONE_MIB
    assert uploads._user_queue_sizes[USERNAME] > ONE_MIB
    assert core.sent_peer == []  # No UploadDenied(Too many megabytes) was sent.


def test_modern_queue_upload_accepts_candidate_that_pushes_existing_queue_over_limit(patch_global_modules):
    core, _events, _config = patch_global_modules
    existing = "Music\\existing.flac"
    candidate = "Music\\candidate.flac"
    core.shares = StubShares({existing: 700 * 1024, candidate: 500 * 1024})
    uploads = make_uploads()
    add_existing_queued_upload(uploads, USERNAME, existing, 700 * 1024)

    assert uploads._user_queue_sizes[USERNAME] < ONE_MIB
    uploads._queue_upload(queue_upload_message(candidate))

    assert set(uploads.queued_users[USERNAME]) == {existing, candidate}
    assert uploads._user_queue_sizes[USERNAME] == 1200 * 1024
    assert uploads._user_queue_sizes[USERNAME] > ONE_MIB
    assert core.sent_peer == []


def test_modern_queue_upload_rejects_only_after_existing_queue_already_reaches_limit(patch_global_modules):
    core, _events, _config = patch_global_modules
    existing = "Music\\at_limit.flac"
    candidate = "Music\\one_more_byte.flac"
    core.shares = StubShares({existing: ONE_MIB, candidate: 1})
    uploads = make_uploads()
    add_existing_queued_upload(uploads, USERNAME, existing, ONE_MIB)

    uploads._queue_upload(queue_upload_message(candidate))

    assert candidate not in uploads.queued_users[USERNAME]
    denied = only_peer_message(core)
    assert denied.__class__.__name__ == "UploadDenied"
    assert denied.reason == TransferRejectReason.TOO_MANY_MEGABYTES


def test_file_count_limit_counts_existing_items_and_rejects_second_candidate(patch_global_modules):
    core, _events, config = patch_global_modules
    config.sections["transfers"]["filelimit"] = 1
    config.sections["transfers"]["queuelimit"] = 0
    first = "Music\\first.flac"
    second = "Music\\second.flac"
    core.shares = StubShares({first: 2 * ONE_MIB, second: 1})
    uploads = make_uploads()

    uploads._queue_upload(queue_upload_message(first))
    uploads._queue_upload(queue_upload_message(second))

    assert first in uploads.queued_users[USERNAME]
    assert second not in uploads.queued_users[USERNAME]
    denied = only_peer_message(core)
    assert denied.__class__.__name__ == "UploadDenied"
    assert denied.reason == TransferRejectReason.TOO_MANY_FILES


def test_legacy_download_request_queues_oversized_candidate_when_same_user_already_active(patch_global_modules):
    core, _events, _config = patch_global_modules
    large_file = "Music\\legacy_oversized.flac"
    core.shares = StubShares({large_file: 3 * ONE_MIB})
    uploads = make_uploads()
    add_active_upload_for_same_user(uploads, USERNAME)

    response = uploads._transfer_request_uploads(legacy_download_request(large_file))

    assert large_file in uploads.queued_users[USERNAME]
    assert uploads._user_queue_sizes[USERNAME] == 3 * ONE_MIB
    assert uploads._user_queue_sizes[USERNAME] > ONE_MIB
    assert response.allowed is False
    assert response.reason == TransferRejectReason.QUEUED


def test_legacy_download_request_rejects_when_existing_queue_already_reaches_limit(patch_global_modules):
    core, _events, _config = patch_global_modules
    existing = "Music\\legacy_at_limit.flac"
    candidate = "Music\\legacy_one_more.flac"
    core.shares = StubShares({existing: ONE_MIB, candidate: 1})
    uploads = make_uploads()
    add_existing_queued_upload(uploads, USERNAME, existing, ONE_MIB)

    response = uploads._transfer_request_uploads(legacy_download_request(candidate))

    assert candidate not in uploads.queued_users[USERNAME]
    assert response.allowed is False
    assert response.reason == TransferRejectReason.TOO_MANY_MEGABYTES
