from __future__ import annotations

import collections
import io
import os
import sys
import tempfile
import types
from pathlib import Path

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

import pynicotine.downloads as downloads_mod  # noqa: E402
import pynicotine.uploads as uploads_mod  # noqa: E402
import pynicotine.transfers as transfers_mod  # noqa: E402
import pynicotine.slskproto as slskproto_mod  # noqa: E402
from pynicotine.downloads import Downloads  # noqa: E402
from pynicotine.uploads import Uploads  # noqa: E402
from pynicotine.slskmessages import (  # noqa: E402
    FileTransferInit,
    TransferDirection,
    TransferRequest,
    TransferResponse,
    UploadFile,
)
from pynicotine.transfers import Transfer, TransferStatus  # noqa: E402


class FakeSock:
    pass


class StubUsers:
    login_status = 2
    def __init__(self):
        self.watches = []
        self.unwatches = []
        self.statuses = {}
        self.addresses = {}
    def watch_user(self, username, context=None):
        self.watches.append((username, context))
    def unwatch_user(self, username, context=None):
        self.unwatches.append((username, context))


class StubShares:
    def __init__(self, mapping=None):
        self.mapping = mapping or {}
    def virtual2real(self, virtual_path, *args, **kwargs):
        return self.mapping[virtual_path]


class StubCore:
    def __init__(self, shares=None):
        self.users = StubUsers()
        self.buddies = types.SimpleNamespace(users={})
        self.shares = shares or StubShares()
        self.sent_peer = []
        self.sent_network = []
        self.statistics = types.SimpleNamespace(append_stat_value=lambda *args, **kwargs: None)
        self.notifications = types.SimpleNamespace(show_download_notification=lambda *args, **kwargs: None)
        self.pluginhandler = types.SimpleNamespace(
            download_started_notification=lambda *args, **kwargs: None,
            download_finished_notification=lambda *args, **kwargs: None,
            upload_queued_notification=lambda *args, **kwargs: None,
            upload_started_notification=lambda *args, **kwargs: None,
            upload_finished_notification=lambda *args, **kwargs: None,
        )
    def send_message_to_peer(self, username, msg):
        self.sent_peer.append((username, msg))
    def send_message_to_network_thread(self, msg):
        self.sent_network.append(msg)


class StubEvents:
    def __init__(self):
        self.cancelled = []
        self.emitted = []
        self._next_id = 1000
    def schedule(self, delay=None, callback=None, callback_args=(), repeat=False, **kwargs):
        self._next_id += 1
        return f"timer-{self._next_id}"
    def cancel_scheduled(self, timer_id):
        self.cancelled.append(timer_id)
    def emit(self, *args, **kwargs):
        self.emitted.append((args, kwargs))
    def connect(self, *args, **kwargs):
        return None
    def emit_main_thread(self, *args, **kwargs):
        self.emitted.append((args, kwargs))


class StubLog:
    def add(self, *args, **kwargs):
        pass
    def add_transfer(self, *args, **kwargs):
        pass
    def add_download(self, *args, **kwargs):
        pass
    def add_upload(self, *args, **kwargs):
        pass


class ProbeDownloads(Downloads):
    __slots__ = ("tmpdir",)
    def get_incomplete_download_folder(self):
        return os.path.join(self.tmpdir, "incomplete")
    def get_incomplete_download_file_path(self, username, virtual_path):
        return os.path.join(self.get_incomplete_download_folder(), "INCOMPLETE.bin")
    def get_complete_download_file_path(self, username, virtual_path, size, download_folder_path=None):
        return os.path.join(self.tmpdir, "complete", "complete.bin"), False
    def _update_transfer(self, transfer, update_parent=True):
        return None


class ProbeUploads(Uploads):
    __slots__ = ()
    def _update_transfer(self, transfer, update_parent=True):
        return None
    def _check_upload_queue(self):
        return None
    def _finish_transfer(self, transfer, already_exists=False):
        return transfers_mod.Transfers._finish_transfer(self, transfer)


def _set_if_slot(obj, key, value):
    try:
        setattr(obj, key, value)
    except AttributeError:
        pass


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
        "tmpdir": tmpdir,
    }
    for k, v in fields.items():
        _set_if_slot(obj, k, v)
    return obj


def make_uploads(tmpdir):
    obj = ProbeUploads.__new__(ProbeUploads)
    fields = {
        "transfers": {},
        "queued_transfers": {},
        "queued_users": collections.defaultdict(dict),
        "active_users": collections.defaultdict(dict),
        "failed_users": collections.defaultdict(dict),
        "transfers_file_path": os.path.join(tmpdir, "uploads.json"),
        "total_bandwidth": 0,
        "_name": "uploads",
        "_allow_saving_transfers": False,
        "_online_users": set(),
        "_user_queue_limits": collections.defaultdict(int),
        "_user_queue_sizes": collections.defaultdict(int),
        "pending_shutdown": False,
        "upload_speed": 0,
        "token": 12345,
        "_queue_positions": {},
        "_queue_position_users": collections.defaultdict(dict),
        "_privileged_position_requested": False,
        "_pending_network_msgs": [],
        "_queue_notification_users": set(),
        "_user_update_counter": 0,
        "_user_update_counters": {},
        "_queue_notification_timer_id": None,
        "_upload_queue_timer_id": None,
        "_retry_failed_uploads_timer_id": None,
    }
    for k, v in fields.items():
        _set_if_slot(obj, k, v)
    return obj


@pytest.fixture(autouse=True)
def patch_global_modules(monkeypatch, tmp_path):
    events = StubEvents()
    log = StubLog()
    config = types.SimpleNamespace(
        data_folder_path=str(tmp_path),
        sections={
            "transfers": {
                "incompletedir": str(tmp_path / "incomplete"),
                "downloaddir": str(tmp_path / "complete"),
                "enablefilters": False,
                "downloadregexp": "",
                "afterfinish": "",
                "afterfolder": "",
                "shownotification": False,
                "autoclear_downloads": False,
                "autoclear_uploads": False,
                "useupslots": True,
                "uploadslots": 10,
                "use_upload_speed_limit": "none",
                "uploadlimit": 0,
                "uploadlimitalt": 0,
                "uploadbandwidth": 0,
                "uselimit": False,
                "friendsnolimits": False,
                "preferfriends": False,
            },
            "notifications": {"notification_popup_file": False},
        },
    )
    core = StubCore()
    for mod in (downloads_mod, uploads_mod, transfers_mod, slskproto_mod):
        monkeypatch.setattr(mod, "events", events, raising=False)
        monkeypatch.setattr(mod, "log", log, raising=False)
    for mod in (downloads_mod, uploads_mod, transfers_mod):
        monkeypatch.setattr(mod, "core", core, raising=False)
        monkeypatch.setattr(mod, "config", config, raising=False)
    return core, events, config


def queue_download(downloads, username, virtual_path, size):
    transfer = Transfer(username=username, virtual_path=virtual_path, folder_path=os.path.join(downloads.tmpdir, "complete"), size=size)
    transfer.status = TransferStatus.QUEUED
    downloads.transfers[username + virtual_path] = transfer
    downloads.queued_transfers[transfer] = None
    downloads.queued_users[username][virtual_path] = transfer
    downloads._user_queue_sizes[username] += size
    return transfer


def test_peer_transfer_request_can_expand_queued_download_size_and_network_leftbytes(tmp_path, patch_global_modules):
    core, _events, _config = patch_global_modules
    os.makedirs(tmp_path / "incomplete", exist_ok=True)
    os.makedirs(tmp_path / "complete", exist_ok=True)
    downloads = make_downloads(str(tmp_path))
    username = "size_peer"
    virtual_path = "Music\\song.flac"
    original_size = 1024
    peer_declared_size = 64 * 1024 * 1024
    token = 6969
    transfer = queue_download(downloads, username, virtual_path, original_size)

    msg = TransferRequest(direction=TransferDirection.UPLOAD, token=token, file=virtual_path, filesize=peer_declared_size)
    msg.username = username
    downloads._transfer_request(msg)

    assert transfer.size == peer_declared_size
    assert transfer.size_changed is True
    assert downloads.active_users[username][token] is transfer
    sent_response = core.sent_peer[-1][1]
    assert sent_response.__class__.__name__ == "TransferResponse"
    assert sent_response.allowed is True

    init = FileTransferInit(token=token)
    init.sock = FakeSock()
    init.username = username
    init.is_outgoing = False
    downloads._file_transfer_init(init)

    download_file_msgs = [msg for msg in core.sent_network if msg.__class__.__name__ == "DownloadFile"]
    assert download_file_msgs
    assert download_file_msgs[-1].leftbytes == peer_declared_size
    assert transfer.status == TransferStatus.TRANSFERRING
    assert transfer.file_handle is not None
    transfer.file_handle.close()


def test_upload_network_read_is_not_clamped_to_advertised_remaining_size(monkeypatch):
    events = StubEvents()
    monkeypatch.setattr(slskproto_mod, "events", events, raising=False)
    network_thread = slskproto_mod.NetworkThread()
    network_thread._modify_connection_events = lambda *args, **kwargs: None

    class FakeConn:
        pass
    conn = FakeConn()
    conn.out_buffer = bytearray()
    conn.last_active = 0
    conn.init = types.SimpleNamespace(target_user="reader")
    upload_msg = UploadFile(sock=FakeSock(), token=107, file=io.BytesIO(b"X" * 4096), size=10)
    upload_msg.offset = 0
    network_thread._file_upload_msgs[conn] = upload_msg

    assert network_thread._process_upload(conn, num_sent_bytes=0, current_time=1) is True
    assert len(conn.out_buffer) == 4096
    assert len(conn.out_buffer) > upload_msg.size
    assert upload_msg.file.tell() == 4096


def test_upload_file_transfer_init_opens_replaced_path_not_authorized_inode(tmp_path, patch_global_modules):
    core, _events, _config = patch_global_modules
    virtual_path = "Share\\race.bin"
    real_path = tmp_path / "share" / "race.bin"
    real_path.parent.mkdir(parents=True)
    real_path.write_bytes(b"ORIGINAL")
    before = real_path.stat()
    core.shares = StubShares({virtual_path: str(real_path)})
    core.users.addresses["downloader"] = ("203.0.113.20", 2234)

    uploads = make_uploads(str(tmp_path))
    transfer = Transfer(username="downloader", virtual_path=virtual_path, folder_path=str(real_path.parent), size=len(b"ORIGINAL"))
    uploads.transfers[transfer.username + transfer.virtual_path] = transfer
    transfers_mod.Transfers._activate_transfer(uploads, transfer, token=198)

    response = TransferResponse(allowed=True, token=198)
    response.username = transfer.username
    uploads._transfer_response(response)
    assert core.sent_peer and core.sent_peer[-1][1].__class__.__name__ == "FileTransferInit"

    replacement = b"REPLACED-SECRET-BEYOND-ORIGINAL-SIZE"
    real_path.unlink()
    real_path.write_bytes(replacement)
    after = real_path.stat()
    # On POSIX this verifies a different file entry; on non-POSIX the content check below is the core invariant.
    if hasattr(before, "st_ino"):
        assert (before.st_ino, before.st_mtime_ns) != (after.st_ino, after.st_mtime_ns)

    init = FileTransferInit(token=198, is_outgoing=True)
    init.sock = FakeSock()
    init.username = transfer.username
    uploads._file_transfer_init(init)

    upload_file_msgs = [msg for msg in core.sent_network if msg.__class__.__name__ == "UploadFile"]
    assert upload_file_msgs
    upload_file = upload_file_msgs[-1]
    assert upload_file.size == len(b"ORIGINAL")

    # Current combined behavior: the file opened at F-connection time is the replaced
    # path, and the network uploader is not clamped to the advertised/authorized
    # remaining size. Bytes after the advertised size enter the socket out buffer.
    network_thread = slskproto_mod.NetworkThread()
    network_thread._modify_connection_events = lambda *args, **kwargs: None
    class FakeConn:
        pass
    conn = FakeConn()
    conn.out_buffer = bytearray()
    conn.last_active = 0
    conn.init = types.SimpleNamespace(target_user=transfer.username)
    upload_file.offset = 0
    network_thread._file_upload_msgs[conn] = upload_file
    assert network_thread._process_upload(conn, num_sent_bytes=0, current_time=1) is True
    assert bytes(conn.out_buffer) == replacement
    assert len(conn.out_buffer) > upload_file.size
    upload_file.file.close()
