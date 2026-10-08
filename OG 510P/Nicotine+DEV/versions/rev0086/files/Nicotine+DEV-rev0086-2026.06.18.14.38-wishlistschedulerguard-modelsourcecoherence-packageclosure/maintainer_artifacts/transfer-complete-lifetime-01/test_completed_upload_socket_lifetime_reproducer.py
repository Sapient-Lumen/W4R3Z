"""TRANSFER-COMPLETE-LIFETIME-01 / U-269 current-behavior reproducer for rev0022.

Run with:
    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
        test_completed_upload_socket_lifetime_reproducer.py

The assertions intentionally describe current behavior, not desired fixed behavior.
They exercise the network-thread upload send path after the advertised number of
bytes has been accepted by the socket. The key distinction is that silent peers
are eventually bounded by idle cleanup, while post-completion peer input keeps
refreshing connection activity and the completed upload remains active.
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
        self.conn = []
        self.debug = []
        self.msgs = []

    def add_conn(self, message, args=None):
        self.conn.append((message, args))

    def add_debug(self, message, args=None):
        self.debug.append((message, args))

    def add_msg_contents(self, msg, is_outgoing=False):
        self.msgs.append((msg, is_outgoing))

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
        self.recv_queue = []
        self.sent_payloads = []
        self.shutdown_calls = []
        self.closed = False

    def send(self, data):
        payload = bytes(data)
        self.sent_payloads.append(payload)
        return len(payload)

    def recv(self, size):
        if not self.recv_queue:
            return b""
        payload = self.recv_queue.pop(0)
        if len(payload) > size:
            self.recv_queue.insert(0, payload[size:])
            payload = payload[:size]
        return payload

    def push_recv(self, data):
        self.recv_queue.append(data)

    def shutdown(self, how):
        self.shutdown_calls.append(how)

    def close(self):
        self.closed = True


class FakeFile:
    def __init__(self):
        self.closed = False

    def read(self, size=-1):
        return b""

    def seek(self, offset):
        return offset

    def close(self):
        self.closed = True


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
    conn = PeerConnection(
        sock=sock,
        addr=("203.0.113.10", 2234),
        init=init,
        io_events=selectors.EVENT_READ | selectors.EVENT_WRITE,
    )
    conn.is_established = True
    conn.has_post_init_activity = True
    init.sock = sock

    file_init = FileTransferInit(token=9001)
    upload_file = UploadFile(sock=sock, token=9001, file=FakeFile(), size=32, sentbytes=0, offset=0)

    proto._conns[sock] = conn
    proto._num_sockets = 1
    proto._file_init_msgs[conn] = file_init
    proto._file_upload_msgs[conn] = upload_file
    proto._total_uploads = 1
    proto._username_init_msgs["peer" + ConnectionType.FILE] = init
    conn.out_buffer += b"A" * 32

    return SimpleNamespace(
        proto=proto,
        conn=conn,
        sock=sock,
        init=init,
        upload_file=upload_file,
        events=fake_events,
        log=fake_log,
    )


def complete_advertised_upload(harness, *, current_time=None):
    if current_time is None:
        current_time = harness.conn.last_active + 1.0
    assert harness.proto._write_data(harness.conn, current_time)
    return current_time


def upload_progress_events(harness):
    return [event for event in harness.events.emitted if event[0] == "file-upload-progress"]


def file_closed_events(harness):
    return [event for event in harness.events.emitted if event[0] == "file-connection-closed"]


def test_exact_advertised_size_write_leaves_completed_upload_active(harness):
    complete_advertised_upload(harness)

    assert harness.upload_file.sentbytes == harness.upload_file.size == 32
    assert harness.conn.out_buffer == bytearray()
    assert harness.conn in harness.proto._file_upload_msgs
    assert harness.conn in harness.proto._file_init_msgs
    assert harness.proto._total_uploads == 1
    assert harness.sock.closed is False
    assert upload_progress_events(harness)
    assert file_closed_events(harness) == []


def test_silent_completed_upload_is_eventually_closed_by_idle_timeout(harness):
    complete_advertised_upload(harness)

    now = time.monotonic()
    harness.conn.last_active = now - harness.proto.CONNECTION_MAX_IDLE - 1.0
    harness.proto._check_connections(now)

    assert harness.conn not in harness.proto._file_upload_msgs
    assert harness.conn not in harness.proto._file_init_msgs
    assert harness.proto._total_uploads == 0
    assert harness.sock.closed is True
    assert file_closed_events(harness)
    assert file_closed_events(harness)[-1][2]["timed_out"] is True


def test_post_completion_peer_trickle_keeps_completed_upload_active_past_idle_window(harness):
    completion_time = current_time = complete_advertised_upload(harness)

    # A silent completed upload would be closed after CONNECTION_MAX_IDLE. Instead,
    # a peer sends one invalid post-FileOffset byte before each idle window expires.
    for _cycle in range(4):
        current_time += harness.proto.CONNECTION_MAX_IDLE - 1.0
        harness.sock.push_recv(b"x")
        harness.proto._process_ready_input_socket(harness.sock, current_time)
        harness.proto._check_connections(current_time)

        assert harness.conn in harness.proto._file_upload_msgs
        assert harness.conn in harness.proto._file_init_msgs
        assert harness.proto._total_uploads == 1
        assert harness.sock.closed is False
        assert harness.conn.last_active == current_time

    assert current_time - completion_time > harness.proto.CONNECTION_MAX_IDLE
    assert file_closed_events(harness) == []


def test_post_completion_peer_bytes_are_discarded_after_file_offset_without_cleanup(harness):
    current_time = complete_advertised_upload(harness)
    harness.sock.push_recv(b"post-completion-noise")

    harness.proto._process_ready_input_socket(harness.sock, current_time + 5.0)

    assert harness.conn.in_buffer == bytearray()
    assert harness.conn.has_post_init_activity is True
    assert harness.conn in harness.proto._file_upload_msgs
    assert not any(event[0] == "upload-file-error" for event in harness.events.emitted)
    assert file_closed_events(harness) == []


def test_control_close_after_completed_upload_retires_slot_and_reports_non_timeout(harness):
    current_time = complete_advertised_upload(harness)

    # Simulate the downloader closing the F socket after receiving all bytes.
    # recv() returning b"" drives the normal close path.
    harness.proto._process_ready_input_socket(harness.sock, current_time + 1.0)

    assert harness.conn not in harness.proto._file_upload_msgs
    assert harness.conn not in harness.proto._file_init_msgs
    assert harness.proto._total_uploads == 0
    assert harness.sock.closed is True
    assert file_closed_events(harness)
    assert file_closed_events(harness)[-1][2]["timed_out"] is False
