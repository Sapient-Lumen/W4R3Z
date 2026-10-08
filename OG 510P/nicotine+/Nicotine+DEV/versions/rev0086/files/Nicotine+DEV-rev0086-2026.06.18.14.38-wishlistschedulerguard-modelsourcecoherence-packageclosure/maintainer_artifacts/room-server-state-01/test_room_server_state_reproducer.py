"""ROOM-SERVER-STATE-01 / U-111 + U-92 current-behavior reproducer.

Run with one archived or live Nicotine+ source lane on PYTHONPATH, for example:

    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest -q \
        test_room_server_state_reproducer.py

The assertions intentionally describe current behavior, not desired fixed behavior.
They show that room/list aggregate count mismatches are not normalized at the
protocol boundary:

* RoomList with too many user-count entries raises IndexError in the parser, but
  the network thread catches/logs it and keeps the server connection open.
* RoomList with too few user-count entries parses successfully and leaves None
  as a user count; the room-list UI count formatter then raises TypeError.
* JoinRoom aggregate user-list arrays can raise IndexError when a parallel count
  is too large, or leave incomplete UserData objects with None fields when a
  parallel count is too small.
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
from pynicotine.slskmessages import JoinRoom, RoomList  # noqa: E402
from pynicotine.slskproto import NetworkThread  # noqa: E402
from pynicotine.utils import humanize  # noqa: E402


def pack_u32(value: int) -> bytes:
    return struct.pack("<I", value)


def pack_string(value: str) -> bytes:
    data = value.encode("utf-8", "surrogatepass")
    return pack_u32(len(data)) + data


def make_message(cls, payload: bytes):
    try:
        return cls(msg_content=memoryview(payload))
    except TypeError:
        return cls()


def parse_message(msg, payload: bytes) -> None:
    try:
        msg.parse_network_message(memoryview(payload))
    except TypeError:
        if getattr(msg, "_message", None) is None:
            msg._message = memoryview(payload)
            msg._offset = 0
        msg.parse_network_message()


def parse_room_list(payload: bytes) -> RoomList:
    msg = make_message(RoomList, payload)
    parse_message(msg, payload)
    return msg


def parse_join_room(payload: bytes) -> JoinRoom:
    msg = make_message(JoinRoom, payload)
    parse_message(msg, payload)
    return msg


def room_list_section(rooms: list[str], counts: list[int] | None = None) -> bytes:
    payload = bytearray()
    payload += pack_u32(len(rooms))
    for room in rooms:
        payload += pack_string(room)

    if counts is not None:
        payload += pack_u32(len(counts))
        for count in counts:
            payload += pack_u32(count)

    return bytes(payload)


def full_room_list_payload(
    public_rooms: list[str],
    public_counts: list[int],
    owned_rooms: list[str] | None = None,
    owned_counts: list[int] | None = None,
    member_rooms: list[str] | None = None,
    member_counts: list[int] | None = None,
    operator_rooms: list[str] | None = None,
) -> bytes:
    owned_rooms = owned_rooms or []
    owned_counts = owned_counts if owned_counts is not None else []
    member_rooms = member_rooms or []
    member_counts = member_counts if member_counts is not None else []
    operator_rooms = operator_rooms or []

    return (
        room_list_section(public_rooms, public_counts)
        + room_list_section(owned_rooms, owned_counts)
        + room_list_section(member_rooms, member_counts)
        + room_list_section(operator_rooms, None)
    )


def join_room_payload(
    room: str,
    users: list[str],
    statuses: list[int],
    stats_rows: list[tuple[int, int, int, int, int]],
    slots: list[int],
    countries: list[str],
) -> bytes:
    payload = bytearray()
    payload += pack_string(room)
    payload += pack_u32(len(users))
    for username in users:
        payload += pack_string(username)
    payload += pack_u32(len(statuses))
    for status in statuses:
        payload += pack_u32(status)
    payload += pack_u32(len(stats_rows))
    for row in stats_rows:
        for value in row:
            payload += pack_u32(value)
    payload += pack_u32(len(slots))
    for slot_value in slots:
        payload += pack_u32(slot_value)
    payload += pack_u32(len(countries))
    for country in countries:
        payload += pack_string(country)
    return bytes(payload)


def server_frame(msg_type: int, content: bytes) -> bytearray:
    # Nicotine+ server frame length includes the uint32 message code plus content,
    # but not the initial uint32 length field itself.
    return bytearray(pack_u32(4 + len(content)) + pack_u32(msg_type) + content)


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


class FakeEvents:
    def __init__(self):
        self.emitted = []

    def connect(self, *args, **kwargs):
        return None

    def emit_main_thread(self, event_name, *args, **kwargs):
        self.emitted.append((event_name, args, kwargs))


def public_rooms_attr(msg: RoomList):
    return getattr(msg, "rooms", None)


def owned_rooms_attr(msg: RoomList):
    return getattr(msg, "ownedprivaterooms", getattr(msg, "rooms_owner", None))


def test_room_list_too_many_user_count_entries_raises_index_error():
    payload = full_room_list_payload(["alpha"], [7, 8])

    with pytest.raises(IndexError):
        parse_room_list(payload)


def test_room_list_too_many_counts_is_logged_and_server_connection_stays_open(monkeypatch):
    fake_log = FakeLog()
    fake_events = FakeEvents()
    monkeypatch.setattr(slskproto_module, "log", fake_log)
    monkeypatch.setattr(slskproto_module, "events", fake_events)

    proto = NetworkThread()
    closed = []
    proto._close_connection = lambda conn: closed.append(conn)
    conn = SimpleNamespace(in_buffer=server_frame(64, full_room_list_payload(["alpha"], [7, 8])))

    proto._process_server_input(conn)

    assert closed == []
    assert conn.in_buffer == bytearray()
    assert fake_events.emitted == []
    assert fake_log.debug, "malformed RoomList is logged, then ignored"


def test_room_list_too_few_user_count_entries_parses_none_user_count_then_ui_formatter_fails():
    payload = full_room_list_payload(["alpha", "beta"], [7])

    msg = parse_room_list(payload)
    assert public_rooms_attr(msg) == [["alpha", 7], ["beta", None]]

    with pytest.raises(TypeError):
        humanize(public_rooms_attr(msg)[1][1])


def test_room_list_private_room_too_few_counts_also_preserves_none_count():
    payload = full_room_list_payload([], [], owned_rooms=["secret-alpha", "secret-beta"], owned_counts=[1])

    msg = parse_room_list(payload)
    assert owned_rooms_attr(msg) == [["secret-alpha", 1], ["secret-beta", None]]

    with pytest.raises(TypeError):
        humanize(owned_rooms_attr(msg)[1][1])


def test_join_room_status_count_larger_than_user_count_raises_index_error():
    payload = join_room_payload(
        room="alpha",
        users=["alice"],
        statuses=[1, 2],
        stats_rows=[],
        slots=[],
        countries=[],
    )

    with pytest.raises(IndexError):
        parse_join_room(payload)


def test_join_room_stats_count_larger_than_user_count_raises_index_error_after_statuses():
    payload = join_room_payload(
        room="alpha",
        users=["alice"],
        statuses=[1],
        stats_rows=[(10, 1, 0, 100, 5), (20, 2, 0, 200, 6)],
        slots=[],
        countries=[],
    )

    with pytest.raises(IndexError):
        parse_join_room(payload)


def test_join_room_too_few_parallel_entries_parses_incomplete_userdata_objects():
    payload = join_room_payload(
        room="alpha",
        users=["alice", "bob"],
        statuses=[1],
        stats_rows=[(10, 1, 0, 100, 5)],
        slots=[0],
        countries=["US"],
    )

    msg = parse_join_room(payload)

    assert msg.room == "alpha"
    assert [user.username for user in msg.users] == ["alice", "bob"]
    assert msg.users[0].status == 1
    assert msg.users[0].avgspeed == 10
    assert msg.users[0].country == "US"
    assert msg.users[1].status is None
    assert msg.users[1].avgspeed is None
    assert msg.users[1].files is None
    assert msg.users[1].slotsfull is None
    assert msg.users[1].country is None
