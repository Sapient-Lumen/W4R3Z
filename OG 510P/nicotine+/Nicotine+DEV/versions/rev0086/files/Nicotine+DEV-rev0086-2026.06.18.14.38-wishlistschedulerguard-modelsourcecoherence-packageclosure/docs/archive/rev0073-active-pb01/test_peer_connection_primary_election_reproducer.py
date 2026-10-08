"""PB-01 current-behavior reproducer for Nicotine+ peer connection election.

Run from an upstream checkout with:

    python -m pytest test_pb01_peer_connection_primary_election_reproducer.py

Or run outside the checkout with:

    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest test_pb01_peer_connection_primary_election_reproducer.py

These tests intentionally assert current behavior, not a fixed invariant.  They
are intended to give maintainers a small executable witness for the behavior
before deciding the compatibility-preserving fix shape.
"""
from __future__ import annotations

import os
import selectors
import socket
import struct
import sys
import time
from pathlib import Path

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    # When copied into the upstream tests directory, the repository root is one
    # or two levels above the file.  Add both common roots defensively.
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))
    sys.path.insert(0, str(here.parent.parent))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import (  # noqa: E402
    ConnectionType,
    FileTransferInit,
    PeerInit,
    PierceFireWall,
    SharedFileListRequest,
    UserInfoRequest,
)


class FakeSock:
    """Small socket stand-in sufficient for NetworkThread connection cleanup."""

    _next_fd = 5000

    def __init__(self, name: str):
        self.name = name
        self.closed = False
        self.shutdown_calls = 0
        self.close_calls = 0
        self._fileno = FakeSock._next_fd
        FakeSock._next_fd += 1

    def fileno(self):
        return self._fileno

    def shutdown(self, how):
        assert how == socket.SHUT_RDWR
        self.shutdown_calls += 1

    def close(self):
        self.closed = True
        self.close_calls += 1

    def setblocking(self, _flag):
        return None

    def setsockopt(self, *args):
        return None

    def connect_ex(self, _addr):
        return 0

    def __repr__(self):
        return self.name


class FakeSelector:
    def __init__(self):
        self.registered = set()
        self.unregistered = []
        self.modified = []

    def register(self, sock, events):
        self.registered.add(sock)

    def unregister(self, sock):
        self.unregistered.append(getattr(sock, "name", repr(sock)))
        self.registered.discard(sock)

    def modify(self, sock, events):
        self.modified.append((getattr(sock, "name", repr(sock)), events))


def _new_peer_init(username: str, conn_type: str):
    try:
        return PeerInit(init_user=username, target_user=username, conn_type=conn_type)
    except TypeError:
        # Compatibility with older constructor shapes.
        msg = PeerInit()
        msg.init_user = username
        msg.target_user = username
        msg.conn_type = conn_type
        return msg


def _frame_peer_init(msg):
    content = msg.make_network_message()
    code = slskmessages.PEER_INIT_MESSAGE_CODES[msg.__class__]
    return bytearray(struct.pack("<I", len(content) + 1) + bytes([code]) + content)


def _frame_peer_message(msg):
    content = msg.make_network_message()
    code = slskmessages.PEER_MESSAGE_CODES[msg.__class__]
    return bytearray(struct.pack("<II", len(content) + 4, code) + content)


def _frame_unknown_peer_message():
    return bytearray(struct.pack("<II", 4, 0xFEEDBEEF))


def _frame_unknown_distrib_message():
    return bytearray(struct.pack("<IB", 1, 0xEF))


def _frame_file_transfer_init(token=31337):
    return bytearray(FileTransferInit(token=token).make_network_message())


def _new_thread():
    network_thread = slskproto.NetworkThread()
    network_thread._selector = FakeSelector()
    network_thread._server_username = "local_user"
    network_thread._should_process_queue = True

    if hasattr(network_thread, "_set_tcp_buffer_size"):
        network_thread._set_tcp_buffer_size = lambda *a, **k: None

    emitted = []
    sent = []

    def emit(msg):
        if msg is None:
            return
        emitted.append({
            "class": msg.__class__.__name__,
            "username": getattr(msg, "username", None),
            "target_user": getattr(msg, "target_user", None),
            "conn_type": getattr(msg, "conn_type", None),
            "sock": getattr(getattr(msg, "sock", None), "name", None),
            "token": getattr(msg, "token", None),
        })

    def capture_outgoing(msgs):
        for msg in list(msgs):
            sent.append({
                "class": msg.__class__.__name__,
                "username": getattr(msg, "username", None),
                "target_user": getattr(msg, "target_user", None),
                "conn_type": getattr(msg, "conn_type", None),
                "sock": getattr(getattr(msg, "sock", None), "name", None),
                "token": getattr(msg, "token", None),
            })

    network_thread._emit_network_message_event = emit
    network_thread._process_outgoing_messages = capture_outgoing
    network_thread._send_message_to_server = lambda msg: None
    network_thread._modify_connection_events = lambda conn, events: setattr(conn, "io_events", events)
    return network_thread, emitted, sent


def _add_established_conn(network_thread, username, conn_type, sock_name, addr, init=None, username_key=True):
    sock = FakeSock(sock_name)
    if init is None:
        init = _new_peer_init(username, conn_type)
        init.sock = sock

    conn = slskproto.PeerConnection(sock=sock, addr=addr, io_events=selectors.EVENT_READ, init=init)
    conn.is_established = True
    network_thread._conns[sock] = conn
    network_thread._selector.register(sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1

    if username_key:
        network_thread._username_init_msgs[username + conn_type] = init

    return sock, conn, init


def _post_init_frame_for(conn_type):
    if conn_type == ConnectionType.PEER:
        return _frame_unknown_peer_message()
    if conn_type == ConnectionType.DISTRIBUTED:
        return _frame_unknown_distrib_message()
    if conn_type == ConnectionType.FILE:
        return _frame_file_transfer_init()
    raise AssertionError(conn_type)




@pytest.mark.parametrize("conn_type", [ConnectionType.PEER, ConnectionType.DISTRIBUTED])
def test_direct_peerinit_without_existing_primary_is_accepted_as_primary_compatibility_baseline(conn_type):
    """Compatibility baseline: a first valid direct P/D PeerInit should still work.

    This should remain true after a PB-01 fix. The report is not asking to reject
    ordinary first connections; it is asking not to let a later claimed PeerInit
    steal an established primary/generation.
    """

    network_thread, emitted, sent = _new_thread()
    victim = "victim_user"
    network_thread._user_addresses[victim] = ("198.51.100.10", 2234)

    if conn_type == ConnectionType.DISTRIBUTED:
        network_thread._is_server_parent = True
        network_thread._max_distrib_children = max(getattr(network_thread, "_max_distrib_children", 0), 10)
        network_thread._branch_level = 1
        network_thread._branch_root = "root_user"

    incoming_sock = FakeSock(f"first_direct_{conn_type}")
    incoming_conn = slskproto.PeerConnection(
        sock=incoming_sock,
        addr=("198.51.100.10", 2234),
        io_events=selectors.EVENT_READ,
    )
    incoming_conn.is_established = True
    incoming_conn.in_buffer += _frame_peer_init(_new_peer_init(victim, conn_type))
    network_thread._conns[incoming_sock] = incoming_conn
    network_thread._selector.register(incoming_sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1

    parsed_init = network_thread._process_peer_init_input(incoming_conn)
    active_init = network_thread._username_init_msgs[victim + conn_type]

    assert parsed_init.target_user == victim
    assert active_init.sock is incoming_sock
    assert incoming_sock in network_thread._conns
    assert incoming_sock.closed is False


def test_valid_piercefirewall_without_direct_primary_becomes_primary_compatibility_baseline():
    """Compatibility baseline: indirect fallback works when no direct primary exists."""

    network_thread, emitted, sent = _new_thread()
    victim = "victim_user"
    init = _new_peer_init(victim, ConnectionType.PEER)
    token = 111222
    if hasattr(network_thread, "_token_init_msgs"):
        network_thread._token_init_msgs[token] = (init, time.monotonic())
    else:
        network_thread._indirect_token_init_msgs[token] = init

    secondary_sock = FakeSock("indirect_primary_pf")
    secondary_conn = slskproto.PeerConnection(
        sock=secondary_sock,
        addr=("198.51.100.20", 4444),
        io_events=selectors.EVENT_READ,
    )
    secondary_conn.is_established = True
    secondary_conn.in_buffer += _frame_peer_init(PierceFireWall(token=token))
    network_thread._conns[secondary_sock] = secondary_conn
    network_thread._selector.register(secondary_sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1

    parsed = network_thread._process_peer_init_input(secondary_conn)

    assert parsed.target_user == victim
    assert secondary_conn.init is init
    assert init.sock is secondary_sock
    assert network_thread._username_init_msgs[victim + ConnectionType.PEER] is init
    assert secondary_sock in network_thread._conns
    assert secondary_sock.closed is False


def test_valid_piercefirewall_during_unestablished_direct_attempt_replaces_direct_socket_compatibility_baseline():
    """Compatibility baseline: indirect fallback can win over an unestablished direct attempt."""

    network_thread, emitted, sent = _new_thread()
    victim = "victim_user"
    init = _new_peer_init(victim, ConnectionType.PEER)

    direct_sock, direct_conn, _ = _add_established_conn(
        network_thread,
        victim,
        ConnectionType.PEER,
        "direct_attempt_not_established",
        ("198.51.100.10", 2234),
        init=init,
    )
    init.sock = direct_sock
    direct_conn.is_established = False

    token = 333444
    if hasattr(network_thread, "_token_init_msgs"):
        network_thread._token_init_msgs[token] = (init, time.monotonic())
    else:
        network_thread._indirect_token_init_msgs[token] = init

    secondary_sock = FakeSock("indirect_wins_pf")
    secondary_conn = slskproto.PeerConnection(
        sock=secondary_sock,
        addr=("198.51.100.20", 4444),
        io_events=selectors.EVENT_READ,
    )
    secondary_conn.is_established = True
    secondary_conn.in_buffer += _frame_peer_init(PierceFireWall(token=token))
    network_thread._conns[secondary_sock] = secondary_conn
    network_thread._selector.register(secondary_sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1

    parsed = network_thread._process_peer_init_input(secondary_conn)

    assert parsed.target_user == victim
    assert init.sock is secondary_sock
    assert direct_sock.closed is True
    assert direct_sock not in network_thread._conns
    assert secondary_sock in network_thread._conns
    assert secondary_sock.closed is False

@pytest.mark.parametrize("conn_type,pending_msg_factory", [
    (ConnectionType.PEER, UserInfoRequest),
    (ConnectionType.DISTRIBUTED, SharedFileListRequest),
])
def test_incoming_direct_peerinit_replaces_existing_primary_and_migrates_queued_messages(conn_type, pending_msg_factory):
    """U-168 current behavior: a claimed username/type can replace a P/D primary."""

    network_thread, emitted, sent = _new_thread()
    victim = "victim_user"
    network_thread._user_addresses[victim] = ("198.51.100.10", 2234)

    if conn_type == ConnectionType.DISTRIBUTED:
        # Keep the distributed child acceptance path out of the way so this test
        # isolates primary replacement rather than no-parent policy rejection.
        network_thread._is_server_parent = True
        network_thread._max_distrib_children = max(getattr(network_thread, "_max_distrib_children", 0), 10)
        network_thread._branch_level = 1
        network_thread._branch_root = "root_user"

    primary_sock, primary_conn, primary_init = _add_established_conn(
        network_thread, victim, conn_type, f"primary_{conn_type}", ("198.51.100.10", 2234)
    )
    if conn_type == ConnectionType.DISTRIBUTED:
        network_thread._child_peers[victim] = primary_conn

    primary_init.outgoing_msgs.append(pending_msg_factory())

    incoming_sock = FakeSock(f"incoming_replacer_{conn_type}")
    incoming_conn = slskproto.PeerConnection(
        sock=incoming_sock,
        addr=("203.0.113.66", 5555),
        io_events=selectors.EVENT_READ,
    )
    incoming_conn.is_established = True
    incoming_conn.in_buffer += _frame_peer_init(_new_peer_init(victim, conn_type))
    network_thread._conns[incoming_sock] = incoming_conn
    network_thread._selector.register(incoming_sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1

    parsed_init = network_thread._process_peer_init_input(incoming_conn)
    active_init = network_thread._username_init_msgs[victim + conn_type]

    assert parsed_init.target_user == victim
    assert primary_sock.closed is True
    assert primary_sock not in network_thread._conns
    assert incoming_sock in network_thread._conns
    assert active_init.sock is incoming_sock
    assert any(item["sock"] == incoming_sock.name for item in sent)


@pytest.mark.parametrize("conn_type", [ConnectionType.PEER, ConnectionType.DISTRIBUTED, ConnectionType.FILE])
def test_secondary_connection_is_promoted_to_primary_after_post_init_activity(conn_type):
    """U-176 current behavior: P/D/F secondary sockets can become init.sock."""

    network_thread, emitted, sent = _new_thread()
    victim = "victim_user"
    network_thread._user_addresses[victim] = ("198.51.100.10", 2234)

    primary_sock, primary_conn, init = _add_established_conn(
        network_thread, victim, conn_type, f"direct_primary_{conn_type}", ("198.51.100.10", 2234)
    )
    secondary_sock, secondary_conn, _ = _add_established_conn(
        network_thread,
        victim,
        conn_type,
        f"secondary_{conn_type}",
        ("203.0.113.77", 6666),
        init=init,
        username_key=False,
    )

    assert init.sock is primary_sock
    secondary_conn.in_buffer += _post_init_frame_for(conn_type)
    network_thread._process_conn_incoming_messages(secondary_conn)

    assert init.sock is secondary_sock
    assert primary_sock in network_thread._conns
    assert primary_sock.closed is False
    assert secondary_sock in network_thread._conns
    assert secondary_sock.closed is False
    assert secondary_conn.has_post_init_activity is True


def test_valid_piercefirewall_keeps_established_direct_primary_until_secondary_sends_peer_message():
    """Compatibility baseline plus U-165 support path for U-176.

    Current code has a compatibility rule for the modern direct+indirect race:
    when an established direct primary already exists, a valid PierceFireWall
    response is kept as secondary rather than immediately replacing the primary.
    The PB-01 issue is the later generic post-init promotion rule, not that
    initial compatibility behavior by itself.
    """

    network_thread, emitted, sent = _new_thread()
    victim = "victim_user"
    network_thread._user_addresses[victim] = ("198.51.100.10", 2234)
    primary_sock, primary_conn, init = _add_established_conn(
        network_thread, victim, ConnectionType.PEER, "direct_primary_after_pf", ("198.51.100.10", 2234)
    )

    token = 424242
    if hasattr(network_thread, "_token_init_msgs"):
        network_thread._token_init_msgs[token] = (init, time.monotonic())
    else:
        network_thread._indirect_token_init_msgs[token] = init

    secondary_sock = FakeSock("secondary_indirect_pf")
    secondary_conn = slskproto.PeerConnection(
        sock=secondary_sock,
        addr=("203.0.113.88", 7777),
        io_events=selectors.EVENT_READ,
    )
    secondary_conn.is_established = True
    secondary_conn.in_buffer += _frame_peer_init(PierceFireWall(token=token))
    network_thread._conns[secondary_sock] = secondary_conn
    network_thread._selector.register(secondary_sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1

    parsed = network_thread._process_peer_init_input(secondary_conn)

    assert parsed.target_user == victim
    assert secondary_conn.init is init
    assert init.sock is primary_sock
    assert primary_sock.closed is False

    secondary_conn.in_buffer += _frame_peer_message(UserInfoRequest())
    network_thread._process_conn_incoming_messages(secondary_conn)

    assert init.sock is secondary_sock
    assert primary_sock in network_thread._conns
    assert primary_sock.closed is False
