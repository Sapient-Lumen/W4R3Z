#!/usr/bin/env python3
"""PENDING-CONN-BUDGET-01 / U-181 current-source probe.

Run per lane with:

    NICOTINE_SOURCE=/path/to/source LANE_NAME=github-branch-master python tools/probe_rev0017_pending_conn_budget.py

Outputs one JSON object with aggregate state sizes for the pending-init, token,
and socket-cap deferred paths.
"""
from __future__ import annotations

import inspect
import json
import os
import socket as real_socket
import struct
import sys
from pathlib import Path

source = os.environ.get("NICOTINE_SOURCE")
if not source:
    raise SystemExit("NICOTINE_SOURCE is required")
sys.path.insert(0, str(Path(source).resolve()))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import ConnectionType, GetPeerAddress, SharedFileListRequest, UserInfoRequest  # noqa: E402


def pack_ip(ip_address: str) -> bytes:
    return real_socket.inet_aton(ip_address)[::-1]


def pack_get_peer_address_response(username: str, ip_address: str, port: int) -> bytes:
    return b"".join([
        slskmessages.SlskMessage.pack_string(username),
        pack_ip(ip_address),
        slskmessages.SlskMessage.pack_uint32(port),
        slskmessages.SlskMessage.pack_uint32(0),
        struct.pack("<H", 0),
    ])


def process_server_message(network_thread, msg_class, content: bytes):
    msg_type = slskmessages.SERVER_MESSAGE_CODES[msg_class]
    params = inspect.signature(network_thread._process_server_message).parameters
    if len(params) == 5:
        return network_thread._process_server_message(msg_type, len(content), bytearray(content), 0, len(content))
    return network_thread._process_server_message(msg_type, len(content), memoryview(content))


def token_map(network_thread):
    return getattr(network_thread, "_indirect_token_init_msgs", getattr(network_thread, "_token_init_msgs", {}))


def token_map_inits(network_thread):
    result = []
    for value in token_map(network_thread).values():
        result.append(value[0] if isinstance(value, tuple) else value)
    return result


def count_pending_messages(network_thread) -> int:
    return sum(len(init.outgoing_msgs) for inits in network_thread._pending_init_msgs.values() for init in inits)


def count_token_messages(network_thread) -> int:
    return sum(len(init.outgoing_msgs) for init in token_map_inits(network_thread))


def new_thread():
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

    slskproto.events = FakeEvents
    return network_thread, sent_to_server, emitted


def set_cached_user_address(network_thread, username: str, addr: tuple[str, int]) -> None:
    if hasattr(slskproto, "UserAddress"):
        network_thread._user_addresses[username] = slskproto.UserAddress(addr)
    else:
        network_thread._user_addresses[username] = addr


def main():
    lane = os.environ.get("LANE_NAME", Path(source).name)

    # Same-user growth while address resolution is pending.
    nt, sent, _emitted = new_thread()
    same_user = "pending_budget_peer"
    for _ in range(1500):
        nt._send_message_to_peer(same_user, UserInfoRequest())
    same_user_pending_messages = len(nt._pending_init_msgs[same_user][0].outgoing_msgs)
    same_user_getpeeraddress = sum(msg.__class__.__name__ == "GetPeerAddress" for msg in sent)
    same_user_connecttopeer = sum(msg.__class__.__name__ == "ConnectToPeer" for msg in sent)
    same_user_token_messages = count_token_messages(nt)

    # Distinct-user global growth.
    nt, sent, _emitted = new_thread()
    for i in range(600):
        nt._send_message_to_peer(f"pending_global_{i}", SharedFileListRequest())
    distinct_user_count = len(nt._pending_init_msgs)
    distinct_pending_inits = sum(len(v) for v in nt._pending_init_msgs.values())
    distinct_pending_messages = count_pending_messages(nt)
    distinct_token_count = len(token_map(nt))
    distinct_token_messages = count_token_messages(nt)
    distinct_getpeeraddress = sum(msg.__class__.__name__ == "GetPeerAddress" for msg in sent)
    distinct_connecttopeer = sum(msg.__class__.__name__ == "ConnectToPeer" for msg in sent)

    # Offline cleanup semantics.
    nt, _sent, emitted = new_thread()
    offline_user = "offline_with_buffered_messages"
    for _ in range(200):
        nt._send_message_to_peer(offline_user, UserInfoRequest())
    before_offline_pending = count_pending_messages(nt)
    before_offline_token_messages = count_token_messages(nt)
    process_server_message(nt, GetPeerAddress, pack_get_peer_address_response(offline_user, "0.0.0.0", 2242))
    offline_pending_remaining = offline_user in nt._pending_init_msgs
    offline_token_count = len(token_map(nt))
    offline_token_messages = count_token_messages(nt)
    peer_errors = [entry for entry in emitted if entry[0] == "peer-connection-error"]
    offline_error_msg_count = len(peer_errors[-1][2]["msgs"]) if peer_errors else 0

    # Socket-cap deferred connection path.
    nt, _sent, _emitted = new_thread()
    socket_user = "socket_cap_peer"
    set_cached_user_address(nt, socket_user, ("203.0.113.20", 2234))
    nt._num_sockets = nt.MAX_SOCKETS
    for _ in range(250):
        nt._send_message_to_peer(socket_user, UserInfoRequest())
    socket_init = nt._username_init_msgs[socket_user + ConnectionType.PEER]
    socket_pending_messages = len(socket_init.outgoing_msgs)
    socket_deferred_count = len(nt._pending_peer_conns)
    socket_deferred_key_shape = "init-keyed" if list(nt._pending_peer_conns.keys()) and list(nt._pending_peer_conns.keys())[0] is socket_init else "address-keyed-or-other"

    print(json.dumps({
        "lane": lane,
        "same_user_requested_messages": 1500,
        "same_user_pending_messages": same_user_pending_messages,
        "same_user_getpeeraddress_messages": same_user_getpeeraddress,
        "same_user_connecttopeer_messages": same_user_connecttopeer,
        "same_user_token_messages": same_user_token_messages,
        "distinct_users_requested": 600,
        "distinct_pending_users": distinct_user_count,
        "distinct_pending_inits": distinct_pending_inits,
        "distinct_pending_messages": distinct_pending_messages,
        "distinct_token_count": distinct_token_count,
        "distinct_token_messages": distinct_token_messages,
        "distinct_getpeeraddress_messages": distinct_getpeeraddress,
        "distinct_connecttopeer_messages": distinct_connecttopeer,
        "before_offline_pending_messages": before_offline_pending,
        "before_offline_token_messages": before_offline_token_messages,
        "offline_pending_remaining": offline_pending_remaining,
        "offline_token_count": offline_token_count,
        "offline_token_messages": offline_token_messages,
        "offline_error_msg_count": offline_error_msg_count,
        "socket_cap_requested_messages": 250,
        "socket_cap_init_outgoing_messages": socket_pending_messages,
        "socket_cap_deferred_count": socket_deferred_count,
        "socket_cap_deferred_key_shape": socket_deferred_key_shape,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
