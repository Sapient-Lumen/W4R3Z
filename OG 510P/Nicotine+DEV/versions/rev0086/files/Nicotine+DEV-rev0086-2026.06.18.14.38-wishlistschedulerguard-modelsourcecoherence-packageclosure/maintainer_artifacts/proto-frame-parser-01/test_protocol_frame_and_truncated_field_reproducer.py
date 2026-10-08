"""PROTO-FRAME-PARSER-01 / U-137 + U-175 current-behavior reproducer.

Run with one archived or live Nicotine+ source lane on PYTHONPATH, for example:

    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
        test_protocol_frame_and_truncated_field_reproducer.py

The assertions intentionally describe current behavior, not desired fixed behavior.
They show two parser/frame invariants that should become regression tests for a
future hardened parser:

* length-prefixed final string/bytes fields accept short payloads;
* server/peer/distributed framed-message loops do not fail-closed when the
  declared frame length is smaller than the mandatory message-code field.
"""
from __future__ import annotations

import os
import struct
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

import pynicotine.slskproto as slskproto_module  # noqa: E402
from pynicotine.slskmessages import (  # noqa: E402
    ConnectionType,
    DistribSearch,
    FileSearchRequest,
    PeerInit,
    SayChatroom,
    SlskMessage,
)
from pynicotine.slskproto import NetworkThread  # noqa: E402


class FakeEvents:
    def __init__(self):
        self.emitted = []

    def connect(self, *args, **kwargs):
        return None

    def emit_main_thread(self, event_name, *args, **kwargs):
        self.emitted.append((event_name, args, kwargs))


class FakeLog:
    def __init__(self):
        self.debug = []
        self.conn = []
        self.msgs = []

    def add_debug(self, message, args=None):
        self.debug.append((message, repr(args)))

    def add_conn(self, message, args=None):
        self.conn.append((message, repr(args)))

    def add(self, message, args=None):
        self.conn.append((message, repr(args)))

    def add_msg_contents(self, msg):
        self.msgs.append(type(msg).__name__)


def pack_declared_string(declared_length: int, actual_bytes: bytes) -> bytes:
    return struct.pack("<I", declared_length) + actual_bytes


def make_message(cls, payload: bytes):
    try:
        return cls(msg_content=memoryview(payload))
    except TypeError:
        return cls()


def parse_message(msg, payload: bytes) -> None:
    try:
        msg.parse_network_message(memoryview(payload))
    except TypeError:
        # master stores the payload in the message instance.
        if getattr(msg, "_message", None) is None:
            msg._message = memoryview(payload)
            msg._offset = 0
        msg.parse_network_message()


@pytest.mark.parametrize(
    "name,cls,payload,attr,expected_value,declared_length,actual_length",
    [
        (
            "server SayChatroom.message",
            SayChatroom,
            pack_declared_string(4, b"room")
            + pack_declared_string(4, b"user")
            + pack_declared_string(10, b"abc"),
            "message",
            "abc",
            10,
            3,
        ),
        (
            "peer FileSearchRequest.searchterm",
            FileSearchRequest,
            struct.pack("<I", 0x12345678) + pack_declared_string(12, b"needle"),
            "searchterm",
            "needle",
            12,
            6,
        ),
        (
            "distributed DistribSearch.searchterm",
            DistribSearch,
            struct.pack("<I", 1)
            + pack_declared_string(6, b"srcusr")
            + struct.pack("<I", 0x778899AA)
            + pack_declared_string(12, b"query"),
            "searchterm",
            "query",
            12,
            5,
        ),
    ],
)
def test_length_prefixed_final_string_fields_accept_short_payload(
    name, cls, payload, attr, expected_value, declared_length, actual_length
):
    msg = make_message(cls, payload)

    parse_message(msg, payload)

    assert getattr(msg, attr) == expected_value, name
    assert declared_length > actual_length
    # In master, the parser offset records the declared end, not the actual end.
    if hasattr(msg, "_offset"):
        assert msg._offset > len(payload)


def test_low_level_unpack_bytes_accepts_short_payload():
    payload = pack_declared_string(20, b"abc")

    try:
        offset, value = SlskMessage.unpack_bytes(memoryview(payload), 0)
    except TypeError:
        msg = SlskMessage(msg_content=memoryview(payload))
        value = msg.unpack_bytes()
        offset = msg._offset

    assert value == b"abc"
    assert offset == 24
    assert offset > len(payload)


@pytest.fixture()
def protocol_harness(monkeypatch):
    fake_log = FakeLog()
    fake_events = FakeEvents()
    monkeypatch.setattr(slskproto_module, "log", fake_log)
    monkeypatch.setattr(slskproto_module, "events", fake_events)

    proto = NetworkThread()
    closed = []
    proto._close_connection = lambda conn: closed.append(conn)
    return SimpleNamespace(proto=proto, closed=closed, log=fake_log, events=fake_events)


def malformed_8_byte_frame(declared_size: int) -> bytearray:
    # Unknown message type 0x41424344. For server and peer frames, msg_size must
    # include the 4-byte message code. Values 0..3 are smaller than that code.
    return bytearray(struct.pack("<I", declared_size) + struct.pack("<I", 0x41424344))


@pytest.mark.parametrize("declared_size,expected_remaining", [(0, 4), (1, 3), (2, 2), (3, 1)])
def test_server_frame_size_smaller_than_message_code_is_not_rejected(protocol_harness, declared_size, expected_remaining):
    conn = SimpleNamespace(in_buffer=malformed_8_byte_frame(declared_size), has_post_init_activity=False)

    protocol_harness.proto._process_server_input(conn)

    assert protocol_harness.closed == []
    assert len(conn.in_buffer) == expected_remaining
    assert len(protocol_harness.log.debug) == 1


@pytest.mark.parametrize("declared_size,expected_remaining", [(0, 4), (1, 3), (2, 2), (3, 1)])
def test_peer_frame_size_smaller_than_message_code_is_not_rejected(protocol_harness, declared_size, expected_remaining):
    conn = SimpleNamespace(
        in_buffer=malformed_8_byte_frame(declared_size),
        has_post_init_activity=False,
        init=PeerInit(init_user="peer", target_user="peer", conn_type=ConnectionType.PEER),
        sock=object(),
        addr=("203.0.113.9", 2234),
    )

    protocol_harness.proto._process_peer_input(conn)

    assert protocol_harness.closed == []
    assert len(conn.in_buffer) == expected_remaining
    assert len(protocol_harness.log.debug) == 1
    assert conn.has_post_init_activity is True


def test_distributed_frame_size_smaller_than_message_code_is_not_rejected(protocol_harness):
    # Distributed frames have a 1-byte message code after the uint32 length; size 0
    # is therefore smaller than the mandatory code field.
    conn = SimpleNamespace(
        in_buffer=bytearray(struct.pack("<I", 0) + b"X"),
        has_post_init_activity=False,
        init=PeerInit(init_user="peer", target_user="peer", conn_type=ConnectionType.DISTRIBUTED),
        sock=object(),
        addr=("203.0.113.9", 2234),
    )

    protocol_harness.proto._process_distrib_input(conn)

    assert protocol_harness.closed == []
    assert conn.in_buffer == bytearray(b"X")
    assert len(protocol_harness.log.debug) == 1
    assert conn.has_post_init_activity is True
