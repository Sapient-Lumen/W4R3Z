from __future__ import annotations

import collections
import os
import sys
import types
import zlib
from pathlib import Path

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

import pynicotine.shares as shares_mod  # noqa: E402
import pynicotine.uploads as uploads_mod  # noqa: E402
import pynicotine.transfers as transfers_mod  # noqa: E402
from pynicotine.shares import PermissionLevel, Shares  # noqa: E402
from pynicotine.slskmessages import (  # noqa: E402
    FolderContentsRequest,
    FolderContentsResponse,
    PlaceInQueueRequest,
    PlaceInQueueResponse,
    QueueUpload,
    TransferDirection,
    TransferRejectReason,
    TransferRequest,
    TransferResponse,
)
from pynicotine.transfers import Transfer, TransferStatus  # noqa: E402
from pynicotine.uploads import Uploads  # noqa: E402

USERNAME = "path_budget_peer"
ADDR = ("203.0.113.88", 2234)
HUGE_COMPONENT = "x" * (256 * 1024)
HUGE_PATH = "Music\\" + HUGE_COMPONENT + "\\track.flac"
DEEP_PATH = "Music\\" + "\\".join("d" for _ in range(4096)) + "\\track.flac"
LEGACY_TOKEN = 24680
FOLDER_TOKEN = 13579


class StubUsers:
    login_status = 2

    def __init__(self):
        self.statuses = {}
        self.privileged = set()
        self.watches = []
        self.unwatches = []

    def watch_user(self, username, context=None):
        self.watches.append((username, context))

    def unwatch_user(self, username, context=None):
        self.unwatches.append((username, context))


class StubShares:
    rescanning = False

    def __init__(self, file_sizes=None):
        self.file_sizes = file_sizes or {}
        self.virtual2real_calls = []
        self.file_is_shared_calls = []
        self.lowercase_index_calls = []

    def check_user_permission(self, username, ip_address):
        return PermissionLevel.PUBLIC, None

    def virtual2real(self, virtual_path, *args, **kwargs):
        self.virtual2real_calls.append(virtual_path)
        return os.path.join("/virtual/share", virtual_path.replace("\\", os.sep))

    def file_is_shared(self, username, virtual_path, real_path):
        self.file_is_shared_calls.append((username, virtual_path, real_path))
        return virtual_path in self.file_sizes, self.file_sizes.get(virtual_path, 0)

    def get_lowercase_path_index(self, virtual_path):
        self.lowercase_index_calls.append(virtual_path)
        return None


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
        self._next_id = 5000

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
    def __init__(self):
        self.transfer_messages = []

    def add(self, *args, **kwargs):
        pass

    def add_transfer(self, *args, **kwargs):
        self.transfer_messages.append((args, kwargs))

    def add_upload(self, *args, **kwargs):
        pass


class ProbeUploads(Uploads):
    __slots__ = ()

    def _update_transfer(self, transfer, update_parent=True):
        return None

    def _check_upload_queue(self, upload_candidate=None):
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
                "filelimit": 1000000,
                "queuelimit": 1000000,
                "friendsnolimits": False,
                "preferfriends": False,
                "fifoqueue": False,
                "useupslots": True,
                "uploadslots": 0,
                "use_upload_speed_limit": "unlimited",
                "uploadlimit": 1000,
                "uploadlimitalt": 100,
                "uploadbandwidth": 0,
                "limitby": True,
                "autoclear_uploads": False,
                "reveal_buddy_shares": False,
                "reveal_trusted_shares": False,
            },
            "notifications": {"notification_popup_file": False, "notification_popup_queued_upload": False},
        },
    )
    core = StubCore()
    for mod in (uploads_mod, transfers_mod, shares_mod):
        monkeypatch.setattr(mod, "events", events, raising=False)
        monkeypatch.setattr(mod, "log", log, raising=False)
        monkeypatch.setattr(mod, "core", core, raising=False)
        monkeypatch.setattr(mod, "config", config, raising=False)
    return core, events, config, log


def parse_peer_message(message_cls, wire):
    try:
        inbound = message_cls(msg_content=memoryview(wire))
    except TypeError:
        inbound = message_cls()

    try:
        inbound.parse_network_message()
    except TypeError:
        inbound.parse_network_message(memoryview(wire))

    return inbound


def msg_wire_roundtrip(message_cls, value, *args):
    outbound = message_cls(value, *args) if args else message_cls(value)
    return parse_peer_message(message_cls, outbound.make_network_message())


def queue_upload_message(virtual_path: str) -> QueueUpload:
    msg = QueueUpload(virtual_path)
    msg.username = USERNAME
    msg.addr = ADDR
    return msg


def place_in_queue_request(virtual_path: str) -> PlaceInQueueRequest:
    msg = PlaceInQueueRequest(virtual_path)
    msg.username = USERNAME
    msg.addr = ADDR
    return msg


def legacy_download_request(virtual_path: str, token: int = LEGACY_TOKEN) -> TransferRequest:
    msg = TransferRequest(direction=TransferDirection.DOWNLOAD, token=token, file=virtual_path)
    msg.username = USERNAME
    msg.addr = ADDR
    return msg


def add_queued_upload(uploads: Uploads, username: str, virtual_path: str, size: int = 1) -> Transfer:
    transfer = Transfer(username=username, virtual_path=virtual_path, folder_path="/virtual/share", size=size)
    uploads.transfers[username + virtual_path] = transfer
    uploads._enqueue_transfer(transfer)
    return transfer


class ProbeShares:
    def __init__(self):
        self.share_dbs = {"public_streams": {}, "buddy_streams": {}, "trusted_streams": {}}
        self.requested_share_times = {}

    def check_user_permission(self, username, ip_address):
        return PermissionLevel.PUBLIC, None


def folder_contents_request(directory: str, token: int = FOLDER_TOKEN) -> FolderContentsRequest:
    msg = FolderContentsRequest(directory=directory, token=token)
    msg.username = USERNAME
    msg.addr = ADDR
    return msg


def decode_folder_response_dir(response: FolderContentsResponse) -> tuple[int, str, int, int]:
    raw = zlib.decompress(response.make_network_message())
    # Avoid parser-lane differences; decode the prefix manually.
    token = int.from_bytes(raw[0:4], "little")
    directory_len = int.from_bytes(raw[4:8], "little")
    directory = raw[8:8 + directory_len].decode("utf-8")
    ndirs = int.from_bytes(raw[8 + directory_len:12 + directory_len], "little")
    return token, directory, ndirs, len(raw)


def test_peer_message_parsers_preserve_oversized_virtual_paths_without_semantic_component_budget():
    queue_msg = msg_wire_roundtrip(QueueUpload, HUGE_PATH)
    place_msg = msg_wire_roundtrip(PlaceInQueueRequest, HUGE_PATH)
    folder_msg = parse_peer_message(FolderContentsRequest, FolderContentsRequest(HUGE_PATH, FOLDER_TOKEN).make_network_message())
    legacy_msg = parse_peer_message(TransferRequest, TransferRequest(
        direction=TransferDirection.DOWNLOAD, token=LEGACY_TOKEN, file=HUGE_PATH).make_network_message())

    assert queue_msg.file == HUGE_PATH
    assert place_msg.file == HUGE_PATH
    assert folder_msg.dir == HUGE_PATH
    assert folder_msg.token == FOLDER_TOKEN
    assert legacy_msg.file == HUGE_PATH
    assert legacy_msg.direction == TransferDirection.DOWNLOAD


def test_queue_upload_accepts_and_keys_oversized_virtual_path_before_shared_transfer_control_budget(patch_global_modules):
    core, _events, _config, log = patch_global_modules
    core.shares = StubShares({HUGE_PATH: 4096})
    uploads = make_uploads()

    uploads._queue_upload(queue_upload_message(HUGE_PATH))

    assert HUGE_PATH in uploads.queued_users[USERNAME]
    assert core.shares.file_is_shared_calls[-1][1] == HUGE_PATH
    assert len(next(iter(uploads.queued_users[USERNAME]))) > 256 * 1024
    assert core.sent_peer == []


def test_legacy_transfer_request_download_path_is_queued_and_echoed_in_response_context(patch_global_modules):
    core, _events, _config, log = patch_global_modules
    core.shares = StubShares({HUGE_PATH: 4096})
    uploads = make_uploads()
    active = Transfer(username=USERNAME, virtual_path="Other\\active.flac", folder_path="/virtual/share", size=1)
    uploads.active_users[USERNAME][999] = active  # 3.3.10 queues legacy requests when the user already has an active upload.

    uploads._transfer_request(legacy_download_request(HUGE_PATH))

    assert HUGE_PATH in uploads.queued_users[USERNAME]
    assert len(core.sent_peer) == 1
    sent_username, response = core.sent_peer[0]
    assert sent_username == USERNAME
    assert isinstance(response, TransferResponse)
    assert response.allowed is False
    assert response.reason == TransferRejectReason.QUEUED


def test_place_in_queue_request_lookup_then_echoes_oversized_matching_virtual_path(patch_global_modules):
    core, _events, _config, _log = patch_global_modules
    uploads = make_uploads()
    add_queued_upload(uploads, USERNAME, HUGE_PATH, size=4096)

    uploads._place_in_queue_request(place_in_queue_request(HUGE_PATH))

    assert len(core.sent_peer) == 1
    sent_username, response = core.sent_peer[0]
    assert sent_username == USERNAME
    assert isinstance(response, PlaceInQueueResponse)
    assert response.filename == HUGE_PATH
    assert response.place > 0
    assert len(response.make_network_message()) > 256 * 1024


def test_folder_contents_request_sends_compressed_response_echoing_oversized_unmatched_directory(patch_global_modules):
    core, _events, _config, _log = patch_global_modules
    shares = ProbeShares()
    msg = folder_contents_request(HUGE_PATH)

    Shares._folder_contents_request(shares, msg)

    assert len(core.sent_peer) == 1
    sent_username, response = core.sent_peer[0]
    assert sent_username == USERNAME
    assert isinstance(response, FolderContentsResponse)
    assert response.dir == HUGE_PATH
    assert response.token == FOLDER_TOKEN
    token, directory, ndirs, raw_len = decode_folder_response_dir(response)
    assert token == FOLDER_TOKEN
    assert directory == HUGE_PATH
    assert ndirs == 0
    assert raw_len > 256 * 1024


def test_deep_component_count_path_is_preserved_by_transfer_control_parsers():
    queue_msg = msg_wire_roundtrip(QueueUpload, DEEP_PATH)
    place_msg = msg_wire_roundtrip(PlaceInQueueRequest, DEEP_PATH)
    legacy_msg = parse_peer_message(TransferRequest, TransferRequest(
        direction=TransferDirection.DOWNLOAD, token=LEGACY_TOKEN, file=DEEP_PATH).make_network_message())

    assert queue_msg.file.count("\\") > 4096
    assert place_msg.file == DEEP_PATH
    assert legacy_msg.file == DEEP_PATH
