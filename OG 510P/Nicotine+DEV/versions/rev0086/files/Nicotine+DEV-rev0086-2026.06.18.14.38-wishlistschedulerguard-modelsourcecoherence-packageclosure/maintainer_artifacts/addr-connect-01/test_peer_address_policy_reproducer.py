"""ADDR-CONNECT-01 current-behavior reproducer for Nicotine+ peer-address handling.

Run from an upstream checkout with:

    python -m pytest test_peer_address_policy_reproducer.py

or outside the checkout with:

    NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest test_peer_address_policy_reproducer.py

These tests intentionally assert current behavior, not a fixed invariant. They
verify the source paths that consume server-supplied GetPeerAddress and
ConnectToPeer addresses, while preserving the compatibility fact that private
LAN/VPN addresses can be legitimate for Soulseek direct connections.
"""
from __future__ import annotations

import inspect
import os
import socket as real_socket
import struct
import sys
from pathlib import Path

import pytest

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    here = Path(__file__).resolve()
    sys.path.insert(0, str(here.parent))
    sys.path.insert(0, str(here.parent.parent))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import ConnectionType, ConnectToPeer, GetPeerAddress, PeerInit  # noqa: E402


class FakeSock:
    """Small socket stand-in that records outbound connect_ex targets."""

    _next_fd = 9000
    instances = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.connect_ex_calls = []
        self.closed = False
        self._fileno = FakeSock._next_fd
        FakeSock._next_fd += 1
        FakeSock.instances.append(self)

    def fileno(self):
        return self._fileno

    def setblocking(self, _flag):
        return None

    def setsockopt(self, *args):
        return None

    def connect_ex(self, addr):
        self.connect_ex_calls.append(addr)
        return 0

    def shutdown(self, _how):
        return None

    def close(self):
        self.closed = True


class FakeSelector:
    def __init__(self):
        self.registered = []
        self.modified = []
        self.unregistered = []

    def register(self, sock, events):
        self.registered.append((sock, events))

    def modify(self, sock, events):
        self.modified.append((sock, events))

    def unregister(self, sock):
        self.unregistered.append(sock)


def _pack_ip(ip_address: str) -> bytes:
    # Nicotine+ unpack_ip() reverses the four network-order bytes.
    return real_socket.inet_aton(ip_address)[::-1]


def _pack_get_peer_address_response(username: str, ip_address: str, port: int) -> bytes:
    return b"".join([
        slskmessages.SlskMessage.pack_string(username),
        _pack_ip(ip_address),
        slskmessages.SlskMessage.pack_uint32(port),
        slskmessages.SlskMessage.pack_uint32(0),
        struct.pack("<H", 0),
    ])


def _pack_connect_to_peer_request(username: str, conn_type: str, ip_address: str, port: int, token: int = 4242) -> bytes:
    return b"".join([
        slskmessages.SlskMessage.pack_string(username),
        slskmessages.SlskMessage.pack_string(conn_type),
        _pack_ip(ip_address),
        slskmessages.SlskMessage.pack_uint32(port),
        slskmessages.SlskMessage.pack_uint32(token),
        slskmessages.SlskMessage.pack_bool(False),
        slskmessages.SlskMessage.pack_uint32(0),
        slskmessages.SlskMessage.pack_uint32(0),
    ])


def _process_server_message(network_thread, msg_class, content: bytes):
    msg_type = slskmessages.SERVER_MESSAGE_CODES[msg_class]
    params = inspect.signature(network_thread._process_server_message).parameters
    if len(params) == 5:
        # 3.3.10 / 3.3.x: msg_type, msg_size, in_buffer, start_offset, end_offset
        return network_thread._process_server_message(msg_type, len(content), bytearray(content), 0, len(content))

    # master: msg_type, msg_size, msg_content
    return network_thread._process_server_message(msg_type, len(content), memoryview(content))


def _new_peer_init(username: str, conn_type: str):
    try:
        return PeerInit(init_user="local_user", target_user=username, conn_type=conn_type)
    except TypeError:
        msg = PeerInit()
        msg.init_user = "local_user"
        msg.target_user = username
        msg.conn_type = conn_type
        return msg


def _new_thread(monkeypatch):
    FakeSock.instances = []
    network_thread = slskproto.NetworkThread()
    network_thread._selector = FakeSelector()
    network_thread._server_username = "local_user"
    network_thread._server_address = ("server.slsk.example", 2242)
    network_thread._should_process_queue = True

    sent_to_server = []
    emitted = []
    network_thread._send_message_to_server = sent_to_server.append
    network_thread._emit_network_message_event = emitted.append
    network_thread._set_tcp_buffer_size = lambda *a, **k: None
    network_thread._bind_socket_interface = lambda *a, **k: None

    monkeypatch.setattr(slskproto.socket, "socket", lambda *a, **k: FakeSock(*a, **k))
    return network_thread, sent_to_server, emitted


def _connection_attempts():
    return [addr for sock in FakeSock.instances for addr in sock.connect_ex_calls]


@pytest.mark.parametrize(
    ("label", "ip_address", "port"),
    [
        ("loopback_local_service", "127.0.0.1", 631),
        ("link_local_metadata", "169.254.169.254", 80),
        ("documentation_address", "203.0.113.10", 2234),
        ("lan_private_compatibility_baseline", "192.168.1.24", 2234),
    ],
)
def test_pending_getpeeraddress_response_drives_direct_connect_to_supplied_address(monkeypatch, label, ip_address, port):
    """A pending local peer request trusts the next server-supplied address.

    The LAN/private case is a compatibility baseline, not a proposed rejection:
    Soulseek users can legitimately connect across LAN/VPN/private routes. The
    risky part is that special-use addresses follow the same unconditional path.
    """

    network_thread, _sent_to_server, _emitted = _new_thread(monkeypatch)
    username = f"peer_{label}"
    network_thread._pending_init_msgs[username].append(_new_peer_init(username, ConnectionType.PEER))

    content = _pack_get_peer_address_response(username, ip_address, port)
    _process_server_message(network_thread, GetPeerAddress, content)

    assert (ip_address, port) in _connection_attempts()


@pytest.mark.parametrize(
    ("label", "ip_address", "port"),
    [
        ("loopback_local_service", "127.0.0.1", 631),
        ("link_local_metadata", "169.254.169.254", 80),
        ("lan_private_compatibility_baseline", "192.168.1.24", 2234),
    ],
)
def test_unsolicited_connecttopeer_drives_outbound_connect_without_local_pending_request(monkeypatch, label, ip_address, port):
    """A server ConnectToPeer request can trigger a peer socket without local pending state."""

    network_thread, _sent_to_server, _emitted = _new_thread(monkeypatch)
    username = f"peer_{label}"
    assert not network_thread._pending_init_msgs.get(username)

    content = _pack_connect_to_peer_request(username, ConnectionType.PEER, ip_address, port)
    _process_server_message(network_thread, ConnectToPeer, content)

    assert (ip_address, port) in _connection_attempts()


def test_getpeeraddress_zero_zero_zero_zero_is_offline_baseline_and_does_not_open_socket(monkeypatch):
    """Compatibility baseline: 0.0.0.0 is treated as offline and should not connect."""

    network_thread, _sent_to_server, emitted = _new_thread(monkeypatch)
    username = "offline_peer"
    network_thread._pending_init_msgs[username].append(_new_peer_init(username, ConnectionType.PEER))

    content = _pack_get_peer_address_response(username, "0.0.0.0", 2234)
    _process_server_message(network_thread, GetPeerAddress, content)

    assert _connection_attempts() == []
    assert username not in network_thread._pending_init_msgs


def test_getpeeraddress_nonoffline_port_zero_is_rejected_after_legacy_indirect_side_effect(monkeypatch):
    """Port 0 does not open a socket; older lanes still schedule indirect first.

    3.3.10/3.3.x request an indirect ConnectToPeer before the direct port check
    rejects port 0. master moved the indirect request earlier in the ordinary
    initiation flow and does not create this extra side effect in this handler.
    """

    network_thread, sent_to_server, _emitted = _new_thread(monkeypatch)
    username = "port_zero_peer"
    network_thread._pending_init_msgs[username].append(_new_peer_init(username, ConnectionType.PEER))

    content = _pack_get_peer_address_response(username, "198.51.100.20", 0)
    _process_server_message(network_thread, GetPeerAddress, content)

    assert _connection_attempts() == []
    connect_to_peer_count = sum(msg.__class__ is ConnectToPeer for msg in sent_to_server)

    if hasattr(network_thread, "_token_init_msgs"):
        assert connect_to_peer_count == 1
    else:
        assert connect_to_peer_count == 0
