"""F-CONN-FRAME-01 / U-164 current-behavior reproducer for rev0015.

Run with:
    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
        test_f_connection_fixed_frame_fragment_reproducer.py

The assertions intentionally describe current behavior, not desired fixed behavior.
They exercise partial 4-byte FileTransferInit and 8-byte FileOffset F-connection
frames, including resynchronization into wrong token/offset values after a
short prefix has been consumed.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))

from pynicotine.slskmessages import ConnectionType, FileOffset, FileTransferInit, PeerInit, UploadFile  # noqa: E402
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
        # Do not retain msg_content memoryviews; production logging formats/releases them.
        self.debug.append(message)

    def add_msg_contents(self, msg):
        self.msgs.append(msg)

    def add_conn(self, message, args=None):
        self.conn.append((message, args))

    def add(self, message, args=None):
        self.conn.append((message, args))


class FakeSelector:
    def __init__(self):
        self.modified = []

    def modify(self, sock, io_events):
        self.modified.append((sock, io_events))


class SeekRecorder:
    def __init__(self):
        self.seeks = []

    def seek(self, offset):
        self.seeks.append(offset)


def _pack_u32(value):
    return FileTransferInit(token=value).make_network_message()


def _pack_u64(value):
    return FileOffset(offset=value).make_network_message()


@pytest.fixture()
def harness(monkeypatch):
    fake_events = FakeEvents()
    fake_log = FakeLog()
    monkeypatch.setattr(slskproto_module, "events", fake_events)
    monkeypatch.setattr(slskproto_module, "log", fake_log)

    proto = NetworkThread()
    proto._selector = FakeSelector()

    init = PeerInit(init_user="peer", target_user="peer", conn_type=ConnectionType.FILE)
    conn = PeerConnection(sock=object(), init=init)
    return SimpleNamespace(proto=proto, conn=conn, events=fake_events, log=fake_log)


@pytest.mark.parametrize("split_at", [1, 2, 3])
def test_partial_file_transfer_init_prefix_is_consumed_instead_of_buffered(harness, split_at):
    token = 0x11223344
    first = _pack_u32(token)[:split_at]

    harness.conn.in_buffer.extend(first)
    harness.proto._process_file_input(harness.conn)

    assert harness.conn.in_buffer == bytearray()
    assert harness.conn not in harness.proto._file_init_msgs
    assert harness.events.emitted == []


@pytest.mark.parametrize("split_at", [1, 2, 3])
def test_fragmented_file_transfer_init_can_be_resynchronized_as_wrong_token(harness, split_at):
    original_token = 0x11223344
    original = _pack_u32(original_token)
    suffix = bytes([0xAA, 0xBB, 0xCC])
    expected_wrong_token = int.from_bytes((original[split_at:] + suffix)[:4], "little")

    harness.conn.in_buffer.extend(original[:split_at])
    harness.proto._process_file_input(harness.conn)
    assert harness.conn not in harness.proto._file_init_msgs

    harness.conn.in_buffer.extend(original[split_at:] + suffix)
    harness.proto._process_file_input(harness.conn)

    parsed = harness.proto._file_init_msgs[harness.conn]
    assert parsed.token == expected_wrong_token
    assert parsed.token != original_token
    assert len(harness.conn.in_buffer) == len(original[split_at:] + suffix) - 4


def test_complete_file_transfer_init_frame_is_parsed_and_consumed(harness):
    token = 0x11223344
    harness.conn.in_buffer.extend(_pack_u32(token))

    harness.proto._process_file_input(harness.conn)

    assert harness.conn.in_buffer == bytearray()
    assert harness.proto._file_init_msgs[harness.conn].token == token
    assert harness.events.emitted


@pytest.mark.parametrize("split_at", [1, 2, 3, 4, 5, 6, 7])
def test_partial_file_offset_prefix_is_consumed_instead_of_buffered(harness, split_at):
    # Mark FileTransferInit as already complete and attach an upload object so the FileOffset path is active.
    harness.proto._file_init_msgs[harness.conn] = FileTransferInit(token=1234)
    upload_file = UploadFile(sock=harness.conn.sock, token=1234, file=SeekRecorder(), size=9999, sentbytes=0, offset=None)
    harness.proto._file_upload_msgs[harness.conn] = upload_file

    offset = 0x0102030405060708
    harness.conn.in_buffer.extend(_pack_u64(offset)[:split_at])
    harness.proto._process_file_input(harness.conn)

    assert harness.conn.in_buffer == bytearray()
    assert upload_file.offset is None
    assert upload_file.file.seeks == []


@pytest.mark.parametrize("split_at", [1, 2, 3, 4, 5, 6, 7])
def test_fragmented_file_offset_can_be_resynchronized_as_wrong_offset(harness, split_at):
    harness.proto._file_init_msgs[harness.conn] = FileTransferInit(token=1234)
    upload_file = UploadFile(sock=harness.conn.sock, token=1234, file=SeekRecorder(), size=2**60, sentbytes=0, offset=None)
    harness.proto._file_upload_msgs[harness.conn] = upload_file

    original_offset = 0x0102030405060708
    original = _pack_u64(original_offset)
    suffix = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0x11, 0x22])
    expected_wrong_offset = int.from_bytes((original[split_at:] + suffix)[:8], "little")

    harness.conn.in_buffer.extend(original[:split_at])
    harness.proto._process_file_input(harness.conn)
    assert upload_file.offset is None

    harness.conn.in_buffer.extend(original[split_at:] + suffix)
    harness.proto._process_file_input(harness.conn)

    assert upload_file.offset == expected_wrong_offset
    assert upload_file.offset != original_offset
    assert upload_file.file.seeks == [expected_wrong_offset]
    assert len(harness.conn.in_buffer) == len(original[split_at:] + suffix) - 8


def test_complete_file_offset_frame_is_parsed_and_consumed(harness):
    harness.proto._file_init_msgs[harness.conn] = FileTransferInit(token=1234)
    upload_file = UploadFile(sock=harness.conn.sock, token=1234, file=SeekRecorder(), size=9999, sentbytes=0, offset=None)
    harness.proto._file_upload_msgs[harness.conn] = upload_file
    offset = 4096

    harness.conn.in_buffer.extend(_pack_u64(offset))
    harness.proto._process_file_input(harness.conn)

    assert harness.conn.in_buffer == bytearray()
    assert upload_file.offset == offset
    assert upload_file.file.seeks == [offset]
    assert harness.events.emitted
