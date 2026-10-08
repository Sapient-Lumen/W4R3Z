# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared isolated harness for the rev0073 U-123 research probes.

Research-only: Nicotine+'s contribution policy prohibits submitting generative-AI
content. These fixtures are evidence tools, not upstream contribution material.
"""
from __future__ import annotations

import collections
import importlib
import os
import tempfile
import types
import unittest

from pynicotine.downloads import Downloads
from pynicotine.slskmessages import FileTransferInit
from pynicotine.slskmessages import TransferDirection
from pynicotine.slskmessages import TransferRequest
from pynicotine.transfers import Transfer
from pynicotine.transfers import TransferStatus

config_module = importlib.import_module("pynicotine.config")
downloads_module = importlib.import_module("pynicotine.downloads")
transfers_module = importlib.import_module("pynicotine.transfers")


class FakeSock:
    """Small identity-bearing stand-in for a network socket."""

    def __init__(self, label: str = "u123") -> None:
        self.label = label

    def __repr__(self) -> str:
        return f"<FakeSock {self.label}>"


class StubUsers:
    login_status = 2

    def __init__(self) -> None:
        self.watches = []
        self.unwatches = []
        self.statuses = {}

    def watch_user(self, username, context=None) -> None:
        self.watches.append((username, context))

    def unwatch_user(self, username, context=None) -> None:
        self.unwatches.append((username, context))


class StubCore:
    def __init__(self) -> None:
        self.users = StubUsers()
        self.sent_peer = []
        self.sent_network = []
        self.statistics = types.SimpleNamespace(
            append_stat_value=lambda *args, **kwargs: None
        )
        self.notifications = types.SimpleNamespace(
            show_download_notification=lambda *args, **kwargs: None
        )
        self.pluginhandler = types.SimpleNamespace(
            download_started_notification=lambda *args, **kwargs: None,
            download_finished_notification=lambda *args, **kwargs: None,
            upload_queued_notification=lambda *args, **kwargs: None,
        )

    def send_message_to_peer(self, username, message) -> None:
        self.sent_peer.append(
            (
                username,
                message.__class__.__name__,
                getattr(message, "token", None),
                getattr(message, "allowed", None),
            )
        )

    def send_message_to_network_thread(self, message) -> None:
        self.sent_network.append(
            (
                message.__class__.__name__,
                getattr(message, "token", None),
                repr(getattr(message, "sock", None)),
            )
        )


class StubEvents:
    def __init__(self) -> None:
        self.cancelled = []
        self._next_id = 1000

    def schedule(
        self,
        delay=None,
        callback=None,
        callback_args=(),
        repeat=False,
        **kwargs,
    ):
        self._next_id += 1
        return f"timer-{self._next_id}"

    def cancel_scheduled(self, timer_id) -> None:
        self.cancelled.append(timer_id)

    def emit(self, *args, **kwargs) -> None:
        pass

    def connect(self, *args, **kwargs) -> None:
        pass


class StubLog:
    def add(self, *args, **kwargs) -> None:
        pass

    def add_transfer(self, *args, **kwargs) -> None:
        pass

    def add_download(self, *args, **kwargs) -> None:
        pass


class ProbeDownloads(Downloads):
    __slots__ = ("tmpdir",)

    def get_incomplete_download_folder(self):
        return os.path.join(self.tmpdir, "incomplete")

    def get_incomplete_download_file_path(self, username, virtual_path):
        safe_name = f"{username}_{virtual_path}".replace("\\", "_").replace("/", "_")
        return os.path.join(
            self.get_incomplete_download_folder(),
            "INCOMPLETE_" + safe_name,
        )

    def get_complete_download_file_path(
        self,
        username,
        virtual_path,
        size,
        download_folder_path=None,
    ):
        safe_name = f"{username}_{virtual_path}".replace("\\", "_").replace("/", "_")
        return os.path.join(self.tmpdir, "complete", safe_name), False

    def _update_transfer(self, transfer, update_parent=True):
        return None


def make_downloads(tmpdir: str) -> ProbeDownloads:
    """Construct only the Downloads state needed by the focused probes."""

    downloads = ProbeDownloads.__new__(ProbeDownloads)
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
    for name, value in fields.items():
        setattr(downloads, name, value)

    downloads.tmpdir = tmpdir
    return downloads


def queue_download(
    downloads: ProbeDownloads,
    username: str,
    virtual_path: str,
    size: int,
) -> Transfer:
    transfer = Transfer(
        username=username,
        virtual_path=virtual_path,
        folder_path=os.path.join(downloads.tmpdir, "complete"),
        size=size,
    )
    transfer.status = TransferStatus.QUEUED
    downloads.transfers[username + virtual_path] = transfer
    downloads.queued_transfers[transfer] = None
    downloads.queued_users[username][virtual_path] = transfer
    downloads._user_queue_sizes[username] += size
    return transfer


def make_transfer_request(
    username: str,
    virtual_path: str,
    size: int,
    token: int,
) -> TransferRequest:
    message = TransferRequest(
        direction=TransferDirection.UPLOAD,
        token=token,
        file=virtual_path,
        filesize=size,
    )
    message.username = username
    return message


def make_file_init(username: str, token: int, sock: FakeSock) -> FileTransferInit:
    message = FileTransferInit(token=token, is_outgoing=False)
    message.username = username
    message.token = token
    message.is_outgoing = False
    message.sock = sock
    return message


def open_file_handle_count(downloads: ProbeDownloads) -> int:
    return sum(
        transfer.file_handle is not None and not transfer.file_handle.closed
        for transfer in downloads.transfers.values()
    )


def socket_owner_count(downloads: ProbeDownloads) -> int:
    return sum(
        transfer.sock is not None
        for transfer in downloads.transfers.values()
    )


class U123TestCase(unittest.TestCase):
    """Install isolated module globals and temporary transfer storage."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="nplus-u123-rev0073-")
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

        replacements = (
            ("core", self.core),
            ("events", self.events),
            ("log", self.log),
            ("config", self.config),
        )
        self._globals = []
        for module in (downloads_module, transfers_module):
            for name, value in replacements:
                self._globals.append((module, name, getattr(module, name)))
                setattr(module, name, value)

        self._config_global = config_module.config
        config_module.config = self.config
        self._downloads = []

    def tearDown(self) -> None:
        for downloads in self._downloads:
            for transfer in downloads.transfers.values():
                handle = transfer.file_handle
                if handle is not None and not handle.closed:
                    handle.close()

        config_module.config = self._config_global
        for module, name, value in reversed(self._globals):
            setattr(module, name, value)
        self.tmp.cleanup()

    def make_downloads(self) -> ProbeDownloads:
        downloads = make_downloads(self.tmp.name)
        self._downloads.append(downloads)
        return downloads
