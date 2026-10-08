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
    # Works when the file is copied to an upstream checkout root.
    sys.path.insert(0, str(Path.cwd().resolve()))
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import ConnectionType, GetPeerAddress, UserInfoRequest, SharedFileListRequest  # noqa: E402


def _pack_ip(ip_address: str) -> bytes:
    return real_socket.inet_aton(ip_address)[::-1]


def _pack_get_peer_address_response(username: str, ip_address: str, port: int) -> bytes:
    return b"".join([
        slskmessages.SlskMessage.pack_string(username),
        _pack_ip(ip_address),
        slskmessages.SlskMessage.pack_uint32(port),
        slskmessages.SlskMessage.pack_uint32(0),
        struct.pack("<H", 0),
    ])


def _process_server_message(network_thread, msg_class, content: bytes):
    msg_type = slskmessages.SERVER_MESSAGE_CODES[msg_class]
    params = inspect.signature(network_thread._process_server_message).parameters
    if len(params) == 5:
        return network_thread._process_server_message(msg_type, len(content), bytearray(content), 0, len(content))
    return network_thread._process_server_message(msg_type, len(content), memoryview(content))


def _token_map(network_thread):
    if hasattr(network_thread, "_indirect_token_init_msgs"):
        return network_thread._indirect_token_init_msgs
    return network_thread._token_init_msgs


def _token_map_inits(network_thread):
    result = []
    for value in _token_map(network_thread).values():
        if isinstance(value, tuple):
            result.append(value[0])
        else:
            result.append(value)
    return result


def _new_thread(monkeypatch):
    network_thread = slskproto.NetworkThread()
    network_thread._server_username = "local_user"
    network_thread._server_address = ("server.slsk.example", 2242)
    network_thread._should_process_queue = True

    sent_to_server = []
    emitted = []
    network_thread._send_message_to_server = sent_to_server.append
    network_thread._set_tcp_buffer_size = lambda *a, **k: None
    network_thread._bind_socket_interface = lambda *a, **k: None
    class FakeEvents:
        @staticmethod
        def connect(*_args, **_kwargs):
            return None

        @staticmethod
        def disconnect(*_args, **_kwargs):
            return None

        @staticmethod
        def emit_main_thread(event, *args, **kwargs):
            emitted.append((event, args, kwargs))
    monkeypatch.setattr(slskproto, "events", FakeEvents)
    return network_thread, sent_to_server, emitted


def _count_pending_messages(network_thread):
    return sum(len(init.outgoing_msgs) for init_list in network_thread._pending_init_msgs.values() for init in init_list)


def _count_token_messages(network_thread):
    return sum(len(init.outgoing_msgs) for init in _token_map_inits(network_thread))


def test_same_user_peer_messages_accumulate_while_getpeeraddress_is_pending(monkeypatch):
    network_thread, sent_to_server, _emitted = _new_thread(monkeypatch)
    username = "pending_budget_peer"

    for _ in range(1500):
        network_thread._send_message_to_peer(username, UserInfoRequest())

    assert len(network_thread._pending_init_msgs[username]) == 1
    init = network_thread._pending_init_msgs[username][0]
    assert init.target_user == username
    assert init.conn_type == ConnectionType.PEER
    assert len(init.outgoing_msgs) == 1500
    assert _count_pending_messages(network_thread) == 1500
    if len(_token_map(network_thread)):
        assert _count_token_messages(network_thread) == 1500
    assert sum(msg.__class__.__name__ == "GetPeerAddress" for msg in sent_to_server) == 1


def test_distinct_users_create_unbounded_pending_init_and_token_state(monkeypatch):
    network_thread, sent_to_server, _emitted = _new_thread(monkeypatch)

    for i in range(600):
        network_thread._send_message_to_peer(f"pending_global_{i}", SharedFileListRequest())

    assert len(network_thread._pending_init_msgs) == 600
    assert sum(len(v) for v in network_thread._pending_init_msgs.values()) == 600
    assert _count_pending_messages(network_thread) == 600
    if len(_token_map(network_thread)):
        assert len(_token_map(network_thread)) == 600
        assert _count_token_messages(network_thread) == 600
    assert sum(msg.__class__.__name__ == "GetPeerAddress" for msg in sent_to_server) == 600


def test_offline_getpeeraddress_clears_pending_bucket_but_leaves_token_state_until_timeout(monkeypatch):
    network_thread, _sent_to_server, emitted = _new_thread(monkeypatch)
    username = "offline_with_buffered_messages"

    for _ in range(200):
        network_thread._send_message_to_peer(username, UserInfoRequest())

    assert _count_pending_messages(network_thread) == 200
    if len(_token_map(network_thread)):
        assert _count_token_messages(network_thread) == 200
    content = _pack_get_peer_address_response(username, "0.0.0.0", 2242)
    _process_server_message(network_thread, GetPeerAddress, content)

    assert username not in network_thread._pending_init_msgs
    if len(_token_map(network_thread)):
        assert len(_token_map(network_thread)) == 1
        assert _count_token_messages(network_thread) == 200
    peer_errors = [entry for entry in emitted if entry[0] == "peer-connection-error"]
    assert peer_errors
    assert len(peer_errors[-1][2]["msgs"]) == 200


def test_socket_cap_deferred_connection_buffers_later_same_user_messages(monkeypatch):
    network_thread, _sent_to_server, _emitted = _new_thread(monkeypatch)
    username = "socket_cap_peer"
    addr = ("203.0.113.20", 2234)
    if hasattr(slskproto, "UserAddress"):
        network_thread._user_addresses[username] = slskproto.UserAddress(addr)
    else:
        network_thread._user_addresses[username] = addr
    network_thread._num_sockets = network_thread.MAX_SOCKETS

    for _ in range(250):
        network_thread._send_message_to_peer(username, UserInfoRequest())

    init = network_thread._username_init_msgs[username + ConnectionType.PEER]
    assert len(init.outgoing_msgs) == 250
    assert len(network_thread._pending_peer_conns) == 1
    # 3.3.10 keys by address; later lanes key by init object. In both cases the same init is retained.
    pending_values = list(network_thread._pending_peer_conns.values())
    if pending_values and isinstance(pending_values[0], tuple):
        assert pending_values[0][0] == ("203.0.113.20", 2234)
    else:
        assert pending_values[0] is init
