#!/usr/bin/env python3
"""rev0008 U-123 socket/progress/close limbo probe.

Runs a local, non-network simulation against a Nicotine+ source tree. It exercises:
  TransferRequest duplicate token -> FileTransferInit -> stale first timeout ->
  file progress/close callbacks.

No Soulseek network connection is made. Temporary local files are used only for the
incomplete download handle that Nicotine+'s Downloads._file_transfer_init() opens.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import tempfile
import types
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("source_tree")
parser.add_argument("--lane", default="unknown")
args = parser.parse_args()
SRC = str(Path(args.source_tree).resolve())
sys.path.insert(0, SRC)

try:
    import pynicotine.downloads as downloads_mod
    import pynicotine.transfers as transfers_mod
    import pynicotine.config as config_mod
    from pynicotine.downloads import Downloads
    from pynicotine.transfers import Transfer, TransferStatus
    from pynicotine.slskmessages import TransferRequest, TransferDirection, FileTransferInit
except Exception as exc:  # pragma: no cover - probe diagnostics
    print(json.dumps({"lane": args.lane, "status": "import-error", "error": repr(exc)}, sort_keys=True))
    raise SystemExit(0)


class FakeSock:
    def __repr__(self):
        return "<FakeSock rev0008>"


class StubUsers:
    def __init__(self):
        self.watches = []
        self.unwatches = []
        self.statuses = {}
        self.login_status = 2

    def watch_user(self, username, context=None):
        self.watches.append({"username": username, "context": context})

    def unwatch_user(self, username, context=None):
        self.unwatches.append({"username": username, "context": context})


class StubPluginHandler:
    def __init__(self):
        self.started = []
        self.finished = []

    def download_started_notification(self, username, virtual_path, incomplete_file_path):
        self.started.append({
            "username": username,
            "virtual_path": virtual_path,
            "incomplete_file_path": str(incomplete_file_path),
        })

    def download_finished_notification(self, username, virtual_path, download_file_path):
        self.finished.append({
            "username": username,
            "virtual_path": virtual_path,
            "download_file_path": str(download_file_path),
        })

    def upload_queued_notification(self, *args, **kwargs):
        pass


class StubStatistics:
    def __init__(self):
        self.values = []

    def append_stat_value(self, key, value):
        self.values.append({"key": key, "value": value})


class StubNotifications:
    def __init__(self):
        self.messages = []

    def show_download_notification(self, *args, **kwargs):
        self.messages.append({"args": [str(a) for a in args], "kwargs": {k: str(v) for k, v in kwargs.items()}})


class StubCore:
    def __init__(self):
        self.users = StubUsers()
        self.pluginhandler = StubPluginHandler()
        self.statistics = StubStatistics()
        self.notifications = StubNotifications()
        self.sent_peer = []
        self.sent_network = []

    def send_message_to_peer(self, username, msg):
        self.sent_peer.append({
            "username": username,
            "class": msg.__class__.__name__,
            "token": getattr(msg, "token", None),
            "offset": getattr(msg, "offset", None),
            "allowed": getattr(msg, "allowed", None),
            "reason": getattr(msg, "reason", None),
            "sock_repr": repr(getattr(msg, "sock", None)),
        })

    def send_message_to_network_thread(self, msg):
        self.sent_network.append({
            "class": msg.__class__.__name__,
            "token": getattr(msg, "token", None),
            "leftbytes": getattr(msg, "leftbytes", None),
            "sock_is_fake": isinstance(getattr(msg, "sock", None), FakeSock),
            "sock_repr": repr(getattr(msg, "sock", None)),
        })


class StubEvents:
    def __init__(self):
        self.scheduled = []
        self.cancelled = []
        self.emitted = []
        self._next_id = 7000

    def schedule(self, delay=None, callback=None, callback_args=(), repeat=False, **kwargs):
        self._next_id += 1
        timer_id = f"timer-{self._next_id}"
        self.scheduled.append({
            "timer_id": timer_id,
            "delay": delay,
            "callback": getattr(callback, "__name__", repr(callback)),
            "args": [getattr(a, "virtual_path", repr(a)) for a in (callback_args or ())],
            "repeat": repeat,
        })
        return timer_id

    def cancel_scheduled(self, timer_id):
        self.cancelled.append(timer_id)

    def emit(self, *args, **kwargs):
        self.emitted.append({"args": [str(a) for a in args], "kwargs": {k: str(v) for k, v in kwargs.items()}})

    def connect(self, *args, **kwargs):
        pass


class StubLog:
    def __init__(self):
        self.entries = []

    def add(self, fmt, args=None):
        self.entries.append({"type": "general", "fmt": str(fmt), "args": repr(args)})

    def add_transfer(self, fmt, args=None):
        self.entries.append({"type": "transfer", "fmt": str(fmt), "args": repr(args)})

    def add_download(self, fmt, args=None):
        self.entries.append({"type": "download", "fmt": str(fmt), "args": repr(args)})


class ProbeDownloads(Downloads):
    __slots__ = ("tmpdir", "updates")

    def get_incomplete_download_folder(self):
        return os.path.join(self.tmpdir, "incomplete")

    def get_incomplete_download_file_path(self, username, virtual_path):
        safe = (username + "_" + virtual_path.strip("\\").replace("\\", "_").replace("/", "_"))
        return os.path.join(self.get_incomplete_download_folder(), "INCOMPLETE_" + safe)

    def get_complete_download_file_path(self, username, virtual_path, size, download_folder_path=None):
        # Avoid depending on the full user config/download folder stack in this probe.
        safe = (username + "_" + virtual_path.strip("\\").replace("\\", "_").replace("/", "_"))
        return os.path.join(self.tmpdir, "complete", safe), False

    def _update_transfer(self, transfer, update_parent=True):
        self.updates.append({
            "username": transfer.username,
            "virtual_path": transfer.virtual_path,
            "status": transfer.status,
            "token": transfer.token,
            "sock_attached": transfer.sock is not None,
            "current_byte_offset": transfer.current_byte_offset,
            "update_parent": update_parent,
        })
        try:
            return super()._update_transfer(transfer, update_parent=update_parent)
        except Exception:
            # Some GUI event/config paths are irrelevant to this local invariant probe.
            return None


def patch_modules(tmpdir):
    core = StubCore()
    events = StubEvents()
    log = StubLog()
    cfg = types.SimpleNamespace(
        data_folder_path=tmpdir,
        sections={
            "transfers": {
                "incompletedir": os.path.join(tmpdir, "incomplete"),
                "downloaddir": os.path.join(tmpdir, "complete"),
                "uploaddir": os.path.join(tmpdir, "uploads"),
                "remotedownloads": False,
                "uploadallowed": 0,
                "enablefilters": False,
                "downloadregexp": "",
                "afterfinish": "",
                "afterfolder": "",
                "shownotification": False,
                "use_download_speed_limit": "unlimited",
                "downloadlimit": 0,
                "downloadlimitalt": 0,
            },
            "notifications": {"notification_popup_file": False},
        },
    )
    for mod in (downloads_mod, transfers_mod):
        mod.core = core
        mod.events = events
        mod.log = log
        mod.config = cfg
    try:
        config_mod.config = cfg
    except Exception:
        pass
    return core, events, log, cfg


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
        try:
            setattr(obj, key, value)
        except Exception:
            pass
    obj.tmpdir = tmpdir
    obj.updates = []
    return obj


def queue_download(obj, username, virtual_path, size):
    t = Transfer(username=username, virtual_path=virtual_path, folder_path=os.path.join(obj.tmpdir, "complete"), size=size)
    t.status = TransferStatus.QUEUED
    obj.transfers[username + virtual_path] = t
    obj.queued_transfers[t] = None
    obj.queued_users[username][virtual_path] = t
    obj._user_queue_sizes[username] += size
    return t


def make_transfer_request(username, path, size, token):
    msg = TransferRequest(direction=TransferDirection.UPLOAD, token=token, file=path, filesize=size)
    # Make a real wire message and parse it back when supported, to avoid relying only on SimpleNamespace.
    try:
        wire = msg.make_network_message()
        try:
            parsed = TransferRequest()
            parsed.parse_network_message(memoryview(wire))
        except TypeError:
            parsed = TransferRequest(msg_content=memoryview(wire))
            parsed.parse_network_message()
            try:
                parsed.finish_parsing()
            except Exception:
                pass
        msg = parsed
    except Exception:
        pass
    msg.username = username
    return msg


def make_file_init(username, token, sock):
    msg = FileTransferInit(token=token, is_outgoing=False)
    try:
        wire = msg.make_network_message()
        try:
            parsed = FileTransferInit()
            parsed.parse_network_message(memoryview(wire))
        except TypeError:
            parsed = FileTransferInit(msg_content=memoryview(wire))
            parsed.parse_network_message()
            try:
                parsed.finish_parsing()
            except Exception:
                pass
        msg = parsed
    except Exception:
        pass
    msg.username = username
    msg.token = token
    msg.is_outgoing = False
    msg.sock = sock
    return msg


def identity(active, token, t1, t2):
    value = active.get(token)
    if value is t1:
        return "first"
    if value is t2:
        return "second"
    if value is None:
        return None
    return "other"


def snapshot(label, obj, username, token, t1, t2, core, events):
    active = obj.active_users.get(username, {})
    return {
        "label": label,
        "active_tokens": sorted([str(k) for k in active.keys()]),
        "active_identity_for_token": identity(active, token, t1, t2),
        "queued_paths": sorted(list(obj.queued_users.get(username, {}).keys())),
        "failed_paths": sorted(list(obj.failed_users.get(username, {}).keys())),
        "first": transfer_state(t1, active),
        "second": transfer_state(t2, active),
        "network_messages_count": len(core.sent_network),
        "peer_messages_count": len(core.sent_peer),
        "cancelled_timers": list(events.cancelled),
    }


def transfer_state(t, active):
    return {
        "status": t.status,
        "token": t.token,
        "timer": t.request_timer_id,
        "sock_attached": t.sock is not None,
        "indexed_by_own_token": (t.token is not None and active.get(t.token) is t),
        "file_handle_open": t.file_handle is not None and not getattr(t.file_handle, "closed", True),
        "current_byte_offset": t.current_byte_offset,
        "last_byte_offset": t.last_byte_offset,
        "speed": t.speed,
        "avg_speed": t.avg_speed,
    }


def run_scenario(duplicate=True):
    with tempfile.TemporaryDirectory(prefix="nplus-rev0008-u123-") as tmpdir:
        os.makedirs(os.path.join(tmpdir, "incomplete"), exist_ok=True)
        os.makedirs(os.path.join(tmpdir, "complete"), exist_ok=True)
        core, events, log, cfg = patch_modules(tmpdir)
        obj = make_downloads(tmpdir)
        username = "attacker-peer"
        token1 = 4242
        token2 = 4242 if duplicate else 4243
        t1 = queue_download(obj, username, "Music\\A.flac", 111)
        t2 = queue_download(obj, username, "Music\\B.flac", 222)
        states = [snapshot("initial", obj, username, token2, t1, t2, core, events)]

        r1 = obj._transfer_request(make_transfer_request(username, t1.virtual_path, t1.size, token1))
        first_timer = t1.request_timer_id
        states.append(snapshot("after_first_transfer_request", obj, username, token2, t1, t2, core, events))

        r2 = obj._transfer_request(make_transfer_request(username, t2.virtual_path, t2.size, token2))
        states.append(snapshot("after_second_transfer_request", obj, username, token2, t1, t2, core, events))

        sock = FakeSock()
        obj._file_transfer_init(make_file_init(username, token2, sock))
        states.append(snapshot("after_file_transfer_init_for_second_token", obj, username, token2, t1, t2, core, events))

        # Fire the stale timeout for the first accepted transfer after the second transfer has an F socket.
        obj._transfer_timeout(t1)
        states.append(snapshot("after_stale_first_timeout", obj, username, token2, t1, t2, core, events))

        # Network-thread callbacks that should belong to the second transfer. These become no-ops if the active map was deleted.
        obj._file_download_progress(username, token2, bytes_left=max(1, t2.size - 17), speed=321)
        states.append(snapshot("after_progress_callback_for_second", obj, username, token2, t1, t2, core, events))

        obj._file_connection_closed(username, token2, sock)
        states.append(snapshot("after_close_callback_for_second_socket", obj, username, token2, t1, t2, core, events))

        # Cleanup any file handle left open by the behavior under test.
        open_handles_before_probe_cleanup = {
            "first": t1.file_handle is not None and not getattr(t1.file_handle, "closed", True),
            "second": t2.file_handle is not None and not getattr(t2.file_handle, "closed", True),
        }
        for t in (t1, t2):
            try:
                if t.file_handle is not None and not t.file_handle.closed:
                    t.file_handle.close()
            except Exception:
                pass

        return {
            "scenario": "duplicate-token" if duplicate else "distinct-token-control",
            "responses": [
                {"class": getattr(r, "__class__", type(None)).__name__, "allowed": getattr(r, "allowed", None), "token": getattr(r, "token", None), "reason": getattr(r, "reason", None)}
                for r in (r1, r2)
            ],
            "first_timer": first_timer,
            "states": states,
            "peer_messages": core.sent_peer,
            "network_messages": core.sent_network,
            "watch_calls": core.users.watches,
            "unwatch_calls": core.users.unwatches,
            "scheduled_timers": events.scheduled,
            "cancelled_timers": events.cancelled,
            "emitted_events": events.emitted,
            "stats": core.statistics.values,
            "plugin_started": core.pluginhandler.started,
            "log_excerpt": log.entries[-12:],
            "open_handles_before_probe_cleanup": open_handles_before_probe_cleanup,
        }

try:
    duplicate_result = run_scenario(duplicate=True)
    control_result = run_scenario(duplicate=False)
    result = {
        "lane": args.lane,
        "source_tree": SRC,
        "status": "ran",
        "duplicate_token_result": duplicate_result,
        "distinct_token_control": control_result,
    }
    d = duplicate_result
    c = control_result
    # Extract high-value invariants from labels.
    dstates = {s["label"]: s for s in d["states"]}
    cstates = {s["label"]: s for s in c["states"]}
    result["invariants"] = {
        "both_duplicate_requests_allowed": [m.get("allowed") for m in d["peer_messages"] if m.get("class") == "TransferResponse"][:2] == [True, True],
        "duplicate_second_attached_f_socket": dstates["after_file_transfer_init_for_second_token"]["second"]["sock_attached"] is True,
        "stale_first_timeout_deleted_second_active_mapping": (
            dstates["after_file_transfer_init_for_second_token"]["active_identity_for_token"] == "second"
            and dstates["after_stale_first_timeout"]["active_identity_for_token"] is None
        ),
        "progress_after_deletion_was_ignored": (
            dstates["after_progress_callback_for_second"]["second"]["current_byte_offset"] is None
            and dstates["after_progress_callback_for_second"]["second"]["file_handle_open"] is True
        ),
        "close_after_deletion_was_ignored_and_handle_left_open": (
            dstates["after_close_callback_for_second_socket"]["second"]["file_handle_open"] is True
            and dstates["after_close_callback_for_second_socket"]["second"]["status"] == TransferStatus.TRANSFERRING
        ),
        "control_second_mapping_survives_first_timeout": cstates["after_stale_first_timeout"]["active_identity_for_token"] == "second",
        "control_progress_updates_second": cstates["after_progress_callback_for_second"]["second"]["current_byte_offset"] == 17,
        "control_close_aborts_or_cleans_second": cstates["after_close_callback_for_second_socket"]["second"]["file_handle_open"] is False,
    }
except Exception as exc:  # pragma: no cover - probe diagnostics
    result = {"lane": args.lane, "source_tree": SRC, "status": "error", "error": repr(exc)}

print(json.dumps(result, sort_keys=True))
