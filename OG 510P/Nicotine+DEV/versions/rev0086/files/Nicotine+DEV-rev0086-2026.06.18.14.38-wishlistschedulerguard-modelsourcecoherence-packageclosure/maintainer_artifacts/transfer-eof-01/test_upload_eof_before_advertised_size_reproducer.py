"""TRANSFER-EOF-01 / U-251 current-behavior reproducer for rev0019.

Run with:
    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
        test_upload_eof_before_advertised_size_reproducer.py

The assertions intentionally describe current behavior, not desired fixed behavior.
They exercise the upload send state machine when the opened file cannot provide
exactly the advertised number of bytes.
"""
from __future__ import annotations

import os
import selectors
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))

from pynicotine.slskmessages import ConnectionType, FileTransferInit, PeerInit, UploadFile  # noqa: E402
import pynicotine.slskproto as slskproto_module  # noqa: E402
from pynicotine.slskproto import NetworkThread, PeerConnection  # noqa: E402


class FakeEvents:
    def __init__(self):
        self.emitted = []

    def connect(self, event_name, callback):
        return None

    def emit_main_thread(self, event_name, *args, **kwargs):
        self.emitted.append((event_name, args, kwargs))


class FakeLog:
    def __init__(self):
        self.debug = []
        self.msgs = []
        self.conn = []

    def add_debug(self, message, args=None):
        self.debug.append((message, args))

    def add_msg_contents(self, msg):
        self.msgs.append(msg)

    def add_conn(self, message, args=None):
        self.conn.append((message, args))

    def add(self, message, args=None):
        self.conn.append((message, args))


class FakeSelector:
    def __init__(self):
        self.modified = []
        self.unregistered = []

    def modify(self, sock, io_events):
        self.modified.append((sock, io_events))

    def unregister(self, sock):
        self.unregistered.append(sock)


class FakeSock:
    def __init__(self):
        self.shutdown_calls = []
        self.closed = False

    def shutdown(self, how):
        self.shutdown_calls.append(how)

    def close(self):
        self.closed = True


class ScriptedFile:
    """Return scripted chunks on read(); repeat EOF after the script is exhausted."""

    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        if not self.chunks:
            return b""
        return self.chunks.pop(0)

    def seek(self, offset):
        return offset


@pytest.fixture()
def harness(monkeypatch):
    fake_events = FakeEvents()
    fake_log = FakeLog()
    monkeypatch.setattr(slskproto_module, "events", fake_events)
    monkeypatch.setattr(slskproto_module, "log", fake_log)

    proto = NetworkThread()
    proto._selector = FakeSelector()
    proto._should_process_queue = True

    sock = FakeSock()
    init = PeerInit(init_user="local_user", target_user="peer", conn_type=ConnectionType.FILE)
    conn = PeerConnection(sock=sock, init=init, io_events=selectors.EVENT_READ | selectors.EVENT_WRITE)
    conn.is_established = True
    # The upload send loop is reached after F-init/FileOffset handling, which marks post-init activity.
    conn.has_post_init_activity = True

    proto._conns[sock] = conn
    proto._num_sockets = 1
    proto._file_init_msgs[conn] = FileTransferInit(token=1234)
    proto._total_uploads = 1

    return SimpleNamespace(proto=proto, conn=conn, sock=sock, events=fake_events, log=fake_log)


def attach_upload(harness, file_obj, *, advertised_size=64, offset=0, sentbytes=0):
    upload_file = UploadFile(
        sock=harness.sock,
        token=1234,
        file=file_obj,
        size=advertised_size,
        sentbytes=sentbytes,
        offset=offset,
    )
    harness.proto._file_upload_msgs[harness.conn] = upload_file
    return upload_file


def complete_current_write_cycle(harness, bytes_to_send):
    """Model the state after the socket has accepted bytes from conn.out_buffer."""
    del harness.conn.out_buffer[:bytes_to_send]
    current_time = harness.conn.last_active + 2.0
    result = harness.proto._process_upload(
        harness.conn,
        num_sent_bytes=bytes_to_send,
        current_time=current_time,
    )
    # _write_data() updates last_active after calling _process_upload(); mirror that here.
    harness.conn.last_active = current_time
    return result


def upload_progress_events(harness):
    return [event for event in harness.events.emitted if event[0] == "file-upload-progress"]


def test_eof_before_advertised_size_is_not_treated_as_local_file_error_or_close(harness):
    file_obj = ScriptedFile([b"A" * 16, b""])
    upload_file = attach_upload(harness, file_obj, advertised_size=64)

    assert harness.proto._process_upload(harness.conn, num_sent_bytes=0, current_time=harness.conn.last_active + 1.0)
    assert bytes(harness.conn.out_buffer) == b"A" * 16

    # After those bytes are accepted by the socket, the next file read reaches EOF,
    # but current behavior keeps the F connection/upload state alive.
    assert complete_current_write_cycle(harness, 16)

    assert harness.conn in harness.proto._file_upload_msgs
    assert upload_file.sentbytes == 16
    assert harness.conn.out_buffer == bytearray()
    assert not any(event[0] == "upload-file-error" for event in harness.events.emitted)
    assert upload_progress_events(harness) == []


def test_short_file_remains_active_until_idle_timeout_then_closes_as_timed_out(harness):
    file_obj = ScriptedFile([b"B" * 8, b""])
    attach_upload(harness, file_obj, advertised_size=64)

    start = harness.conn.last_active
    assert harness.proto._process_upload(harness.conn, num_sent_bytes=0, current_time=start + 1.0)
    assert complete_current_write_cycle(harness, 8)

    # Not closed merely because the local file hit EOF before the advertised size.
    harness.conn.last_active = time.monotonic() - harness.proto.CONNECTION_MAX_IDLE + 1.0
    harness.proto._check_connections(time.monotonic())
    assert harness.conn in harness.proto._file_upload_msgs
    assert harness.sock.closed is False

    # The eventual closure is idle-timeout based, not a direct short-read/file-size mismatch.
    harness.conn.last_active = time.monotonic() - harness.proto.CONNECTION_MAX_IDLE - 1.0
    harness.proto._check_connections(time.monotonic())
    assert harness.conn not in harness.proto._file_upload_msgs
    assert harness.sock.closed is True
    closed_events = [event for event in harness.events.emitted if event[0] == "file-connection-closed"]
    assert closed_events
    assert closed_events[-1][2]["timed_out"] is True


def test_later_growth_after_initial_eof_can_be_sent_without_restart(harness):
    file_obj = ScriptedFile([b"ABC", b"", b"DEF"])
    upload_file = attach_upload(harness, file_obj, advertised_size=9)

    assert harness.proto._process_upload(harness.conn, num_sent_bytes=0, current_time=harness.conn.last_active + 1.0)
    assert bytes(harness.conn.out_buffer) == b"ABC"
    assert complete_current_write_cycle(harness, 3)
    assert harness.conn.out_buffer == bytearray()

    # A later read can still feed more bytes after the earlier EOF observation.
    assert harness.proto._process_upload(harness.conn, num_sent_bytes=0, current_time=harness.conn.last_active + 3.0)
    assert bytes(harness.conn.out_buffer) == b"DEF"
    assert upload_file.sentbytes == 3


def test_sentbytes_overshooting_advertised_size_misses_exact_completion_event(harness):
    # This is the completion side of the same invariant: if a previous unbounded
    # read queued more bytes than the advertised remaining size, the exact == size
    # finish check is skipped once those bytes are reported as sent.
    file_obj = ScriptedFile([b""])
    upload_file = attach_upload(harness, file_obj, advertised_size=8)

    assert harness.proto._process_upload(harness.conn, num_sent_bytes=16, current_time=harness.conn.last_active + 1.0)

    assert upload_file.sentbytes == 16
    assert upload_file.sentbytes > upload_file.size
    assert upload_progress_events(harness) == []
    assert harness.conn in harness.proto._file_upload_msgs
