"""DOWNLOAD-INCOMPLETE-PROVENANCE-01 current-behavior reproducer for rev0023.

Run with:
    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
        test_download_incomplete_provenance_reproducer.py

The assertions intentionally describe current behavior, not desired fixed behavior.
They exercise local filesystem/provenance edges in the download incomplete-file
lifecycle without making network connections.
"""
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

import pynicotine.downloads as downloads_mod  # noqa: E402
import pynicotine.transfers as transfers_mod  # noqa: E402
from pynicotine.downloads import Downloads  # noqa: E402
from pynicotine.slskmessages import FileTransferInit  # noqa: E402
from pynicotine.transfers import Transfer, TransferStatus  # noqa: E402


class FakeSock:
    pass


class StubUsers:
    login_status = 2

    def __init__(self):
        self.watches = []
        self.unwatches = []
        self.statuses = {}
        self.watched = set()

    def watch_user(self, username, context=None):
        self.watches.append((username, context))
        self.watched.add(username)

    def unwatch_user(self, username, context=None):
        self.unwatches.append((username, context))
        self.watched.discard(username)


class StubCore:
    def __init__(self):
        self.users = StubUsers()
        self.buddies = types.SimpleNamespace(users={})
        self.shares = types.SimpleNamespace(initialized=True)
        self.sent_peer = []
        self.sent_network = []
        self.statistics = types.SimpleNamespace(append_stat_value=lambda *args, **kwargs: None)
        self.notifications = types.SimpleNamespace(show_download_notification=lambda *args, **kwargs: None)
        self.pluginhandler = types.SimpleNamespace(
            download_started_notification=lambda *args, **kwargs: None,
            download_finished_notification=lambda *args, **kwargs: None,
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

    def connect(self, *args, **kwargs):
        return None

    def schedule(self, delay=None, callback=None, callback_args=(), repeat=False, **kwargs):
        self._next_id += 1
        return f"timer-{self._next_id}"

    def cancel_scheduled(self, timer_id):
        self.cancelled.append(timer_id)

    def emit(self, *args, **kwargs):
        self.emitted.append((args, kwargs))


class StubLog:
    def __init__(self):
        self.messages = []
        self.transfer_messages = []
        self.download_messages = []

    def add(self, message, args=None):
        self.messages.append((str(message), args))

    def add_transfer(self, message, args=None):
        self.transfer_messages.append((str(message), args))

    def add_download(self, message, args=None):
        self.download_messages.append((str(message), args))


class ProbeDownloads(Downloads):
    __slots__ = ("tmpdir",)

    def get_incomplete_download_folder(self):
        return os.path.join(self.tmpdir, "incomplete")

    def _update_transfer(self, transfer, update_parent=True):
        return None


class RaceDownloads(ProbeDownloads):
    __slots__ = ()

    def get_download_basename(self, virtual_path, download_folder_path, avoid_conflict=False):
        # Simulate a destination entry appearing after the conflict decision but
        # before shutil.move() is called by _move_finished_transfer().
        Path(download_folder_path).mkdir(parents=True, exist_ok=True)
        Path(download_folder_path, "race.bin").write_bytes(b"victim-before-move")
        return "race.bin"


def _set_if_slot(obj, key, value):
    try:
        setattr(obj, key, value)
    except AttributeError:
        pass


def make_downloads(tmp_path, cls=ProbeDownloads):
    obj = cls.__new__(cls)
    fields = {
        "transfers": {},
        "queued_transfers": {},
        "queued_users": collections.defaultdict(dict),
        "active_users": collections.defaultdict(dict),
        "failed_users": collections.defaultdict(dict),
        "transfers_file_path": str(tmp_path / "downloads.json"),
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
        "tmpdir": str(tmp_path),
    }
    for key, value in fields.items():
        _set_if_slot(obj, key, value)
    return obj


@pytest.fixture(autouse=True)
def patch_globals(monkeypatch, tmp_path):
    events = StubEvents()
    log = StubLog()
    core = StubCore()
    config = types.SimpleNamespace(
        data_folder_path=str(tmp_path),
        sections={
            "transfers": {
                "incompletedir": str(tmp_path / "incomplete"),
                "downloaddir": str(tmp_path / "complete"),
                "uploaddir": str(tmp_path / "received"),
                "usernamesubfolders": False,
                "enablefilters": False,
                "downloadregexp": "",
                "afterfinish": "",
                "afterfolder": "",
                "shownotification": False,
                "autoclear_downloads": False,
                "remotedownloads": False,
                "uploadallowed": 0,
            },
            "notifications": {
                "notification_popup_file": False,
                "notification_popup_folder": False,
            },
        },
    )
    for mod in (downloads_mod, transfers_mod):
        monkeypatch.setattr(mod, "events", events, raising=False)
        monkeypatch.setattr(mod, "log", log, raising=False)
        monkeypatch.setattr(mod, "core", core, raising=False)
        monkeypatch.setattr(mod, "config", config, raising=False)
    return types.SimpleNamespace(core=core, events=events, log=log, config=config)


def make_active_download(downloads, username, virtual_path, size, token=4242):
    complete_dir = Path(downloads.tmpdir) / "complete"
    complete_dir.mkdir(parents=True, exist_ok=True)
    transfer = Transfer(username=username, virtual_path=virtual_path, folder_path=str(complete_dir), size=size)
    downloads._append_transfer(transfer)
    transfers_mod.Transfers._activate_transfer(downloads, transfer, token)
    return transfer


def file_transfer_init(username, token=4242):
    msg = FileTransferInit(token=token)
    msg.sock = FakeSock()
    msg.username = username
    msg.is_outgoing = False
    return msg


def download_file_msgs(core):
    return [msg for msg in core.sent_network if msg.__class__.__name__ == "DownloadFile"]


def close_connection_msgs(core):
    return [msg for msg in core.sent_network if msg.__class__.__name__ == "CloseConnection"]


def test_exact_size_stale_incomplete_file_is_promoted_to_finished_without_new_download_bytes(tmp_path, patch_globals):
    downloads = make_downloads(tmp_path)
    username = "peer_a"
    virtual_path = "Album\\song.flac"
    stale_bytes = b"STALE-LOCAL-BYTES"
    transfer = make_active_download(downloads, username, virtual_path, size=len(stale_bytes))

    incomplete_path = Path(downloads.get_incomplete_download_file_path(username, virtual_path))
    incomplete_path.parent.mkdir(parents=True, exist_ok=True)
    incomplete_path.write_bytes(stale_bytes)

    downloads._file_transfer_init(file_transfer_init(username))

    complete_path = Path(transfer.folder_path) / downloads.get_download_basename(virtual_path, transfer.folder_path)
    assert transfer.status == TransferStatus.FINISHED
    assert complete_path.read_bytes() == stale_bytes
    assert not download_file_msgs(patch_globals.core)
    assert not incomplete_path.exists()


def test_partial_stale_incomplete_file_is_trusted_as_resume_offset(tmp_path, patch_globals):
    downloads = make_downloads(tmp_path)
    username = "peer_b"
    virtual_path = "Album\\resume.flac"
    transfer = make_active_download(downloads, username, virtual_path, size=32)

    incomplete_path = Path(downloads.get_incomplete_download_file_path(username, virtual_path))
    incomplete_path.parent.mkdir(parents=True, exist_ok=True)
    incomplete_path.write_bytes(b"STALE-PREFIX")  # 12 bytes

    downloads._file_transfer_init(file_transfer_init(username))

    msgs = download_file_msgs(patch_globals.core)
    assert msgs
    assert transfer.status == TransferStatus.TRANSFERRING
    assert transfer.last_byte_offset == len(b"STALE-PREFIX")
    assert msgs[-1].leftbytes == 32 - len(b"STALE-PREFIX")
    assert transfer.file_handle is not None
    transfer.file_handle.close()


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="requires symlink support")
def test_incomplete_download_path_follows_symlink_instead_of_requiring_regular_file(tmp_path, patch_globals):
    downloads = make_downloads(tmp_path)
    username = "peer_c"
    virtual_path = "Album\\linked.bin"
    transfer = make_active_download(downloads, username, virtual_path, size=20)

    incomplete_path = Path(downloads.get_incomplete_download_file_path(username, virtual_path))
    incomplete_path.parent.mkdir(parents=True, exist_ok=True)
    target_path = tmp_path / "symlink-target.bin"
    target_path.write_bytes(b"TARGET")
    incomplete_path.symlink_to(target_path)

    downloads._file_transfer_init(file_transfer_init(username))

    assert incomplete_path.is_symlink()
    assert transfer.file_handle is not None
    transfer.file_handle.write(b"-WRITE")
    transfer.file_handle.flush()
    transfer.file_handle.close()
    assert target_path.read_bytes().endswith(b"-WRITE")
    assert download_file_msgs(patch_globals.core)


def test_advisory_lock_failure_is_logged_but_download_continues(tmp_path, monkeypatch, patch_globals):
    downloads = make_downloads(tmp_path)
    username = "peer_d"
    virtual_path = "Album\\lock.flac"
    transfer = make_active_download(downloads, username, virtual_path, size=32)

    incomplete_path = Path(downloads.get_incomplete_download_file_path(username, virtual_path))
    incomplete_path.parent.mkdir(parents=True, exist_ok=True)
    incomplete_path.write_bytes(b"LOCKED")

    try:
        import fcntl  # noqa: PLC0415
    except ImportError:  # pragma: no cover - Windows/POSIX split
        pytest.skip("fcntl unavailable")

    def raising_lockf(*_args, **_kwargs):
        raise OSError("simulated exclusive-lock failure")

    monkeypatch.setattr(fcntl, "lockf", raising_lockf)

    downloads._file_transfer_init(file_transfer_init(username))

    assert transfer.status == TransferStatus.TRANSFERRING
    assert transfer.file_handle is not None
    assert download_file_msgs(patch_globals.core)
    assert any("exclusive lock" in msg for msg, _args in patch_globals.log.messages)
    transfer.file_handle.close()


def test_virtual_path_username_boundary_plus_basename_truncation_can_collide(tmp_path):
    downloads = make_downloads(tmp_path)
    long_base = "A" * 300
    path_one = long_base
    user_one = "TAILX"
    path_two = long_base + "TAIL"
    user_two = "X"

    assert path_one + user_one == path_two + user_two
    assert (path_one, user_one) != (path_two, user_two)

    incomplete_one = downloads.get_incomplete_download_file_path(user_one, path_one)
    incomplete_two = downloads.get_incomplete_download_file_path(user_two, path_two)

    assert incomplete_one == incomplete_two


def test_existing_complete_file_same_size_marks_download_finished_without_transfer_request(tmp_path, patch_globals):
    downloads = make_downloads(tmp_path)
    username = "peer_e"
    virtual_path = "Album\\already.flac"
    complete_dir = tmp_path / "complete"
    complete_dir.mkdir(parents=True, exist_ok=True)
    (complete_dir / "already.flac").write_bytes(b"EXISTING")

    downloads.enqueue_download(username, virtual_path, folder_path=str(complete_dir), size=len(b"EXISTING"))

    transfer = downloads.transfers[username + virtual_path]
    assert transfer.status == TransferStatus.FINISHED
    assert not patch_globals.core.sent_peer
    assert not download_file_msgs(patch_globals.core)


def test_completed_move_has_no_post_decision_destination_revalidation(tmp_path):
    downloads = make_downloads(tmp_path, cls=RaceDownloads)
    complete_dir = tmp_path / "complete"
    incomplete_file = tmp_path / "incomplete-ready.bin"
    incomplete_file.write_bytes(b"new-complete-bytes")
    transfer = Transfer("peer_f", "Album\\race.bin", str(complete_dir), size=len(b"new-complete-bytes"))

    moved_path = downloads._move_finished_transfer(transfer, os.fsencode(str(incomplete_file)))

    assert moved_path == str(complete_dir / "race.bin")
    assert (complete_dir / "race.bin").read_bytes() == b"new-complete-bytes"
    assert not incomplete_file.exists()
