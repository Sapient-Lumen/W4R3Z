"""Shared isolated harness for PB-01 peer-connection election research.

No real sockets are opened. Role-specific tests are interpreted by the
rev0074 disposition gate and are not upstream contribution artifacts.
"""
from __future__ import annotations

import os
import selectors
import socket
import struct
import sys
import time
from pathlib import Path

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))
    sys.path.insert(0, str(here.parent.parent))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import (  # noqa: E402
    ConnectionType,
    PeerInit,
    PierceFireWall,
    UserInfoRequest,
)


class FakeSock:
    """Socket stand-in sufficient for NetworkThread connection cleanup."""

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

    def register(self, sock, _events):
        self.registered.add(sock)

    def unregister(self, sock):
        self.unregistered.append(getattr(sock, "name", repr(sock)))
        self.registered.discard(sock)


def new_peer_init(username: str, conn_type: str):
    try:
        return PeerInit(
            init_user=username,
            target_user=username,
            conn_type=conn_type,
        )
    except TypeError:
        # Compatibility with older constructor shapes retained in cube history.
        msg = PeerInit()
        msg.init_user = username
        msg.target_user = username
        msg.conn_type = conn_type
        return msg


def frame_peer_init(msg):
    content = msg.make_network_message()
    code = slskmessages.PEER_INIT_MESSAGE_CODES[msg.__class__]
    return bytearray(
        struct.pack("<I", len(content) + 1) + bytes([code]) + content
    )


def frame_peer_message(msg):
    content = msg.make_network_message()
    code = slskmessages.PEER_MESSAGE_CODES[msg.__class__]
    return bytearray(
        struct.pack("<II", len(content) + 4, code) + content
    )


def new_thread():
    network_thread = slskproto.NetworkThread()
    network_thread._selector = FakeSelector()
    network_thread._server_username = "local_user"
    network_thread._should_process_queue = True

    if hasattr(network_thread, "_set_tcp_buffer_size"):
        network_thread._set_tcp_buffer_size = lambda *args, **kwargs: None

    network_thread._emit_network_message_event = lambda msg: None
    network_thread._process_outgoing_messages = lambda msgs: None
    network_thread._send_message_to_server = lambda msg: None
    network_thread._modify_connection_events = (
        lambda conn, events: setattr(conn, "io_events", events)
    )
    return network_thread


def add_established_connection(
    network_thread,
    username,
    conn_type,
    sock_name,
    addr,
    *,
    response_token=None,
):
    sock = FakeSock(sock_name)
    init = new_peer_init(username, conn_type)
    init.sock = sock
    conn = slskproto.PeerConnection(
        sock=sock,
        addr=addr,
        io_events=selectors.EVENT_READ,
        init=init,
    )
    conn.is_established = True
    conn.response_token = response_token
    network_thread._conns[sock] = conn
    network_thread._selector.register(sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1
    network_thread._username_init_msgs[username + conn_type] = init
    return sock, conn, init


def add_incoming_direct(
    network_thread,
    username,
    sock_name="incoming_direct",
):
    sock = FakeSock(sock_name)
    conn = slskproto.PeerConnection(
        sock=sock,
        addr=("203.0.113.66", 5555),
        io_events=selectors.EVENT_READ,
    )
    conn.is_established = True
    conn.in_buffer += frame_peer_init(
        new_peer_init(username, ConnectionType.PEER)
    )
    network_thread._conns[sock] = conn
    network_thread._selector.register(sock, selectors.EVENT_READ)
    network_thread._num_sockets += 1
    return sock, conn
