#!/usr/bin/env python3
"""rev0016 ADDR-CONNECT-01 current-behavior probe.

Hermetic source-lane harness for Nicotine+ server-supplied peer-address paths.
It replaces socket.socket with a fake object and records connect_ex targets,
without opening network connections.
"""
from __future__ import annotations

import argparse
import inspect
import json
import socket as real_socket
import struct
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--lane", required=True)
args = parser.parse_args()

sys.path.insert(0, str(Path(args.source).resolve()))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import ConnectionType, ConnectToPeer, GetPeerAddress, PeerInit  # noqa: E402


class FakeSock:
    _next_fd = 9100
    instances = []

    def __init__(self, *init_args, **kwargs):
        self.init_args = repr(init_args)
        self.kwargs = repr(kwargs)
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
        self.registered.append((repr(sock), events))

    def modify(self, sock, events):
        self.modified.append((repr(sock), events))

    def unregister(self, sock):
        self.unregistered.append(repr(sock))


def pack_ip(ip_address):
    return real_socket.inet_aton(ip_address)[::-1]


def pack_get_peer_address(username, ip_address, port):
    return b"".join([
        slskmessages.SlskMessage.pack_string(username),
        pack_ip(ip_address),
        slskmessages.SlskMessage.pack_uint32(port),
        slskmessages.SlskMessage.pack_uint32(0),
        struct.pack("<H", 0),
    ])


def pack_connect_to_peer(username, conn_type, ip_address, port, token=4242):
    return b"".join([
        slskmessages.SlskMessage.pack_string(username),
        slskmessages.SlskMessage.pack_string(conn_type),
        pack_ip(ip_address),
        slskmessages.SlskMessage.pack_uint32(port),
        slskmessages.SlskMessage.pack_uint32(token),
        slskmessages.SlskMessage.pack_bool(False),
        slskmessages.SlskMessage.pack_uint32(0),
        slskmessages.SlskMessage.pack_uint32(0),
    ])


def process_server_message(nt, msg_class, content):
    msg_type = slskmessages.SERVER_MESSAGE_CODES[msg_class]
    params = inspect.signature(nt._process_server_message).parameters
    if len(params) == 5:
        return nt._process_server_message(msg_type, len(content), bytearray(content), 0, len(content))
    return nt._process_server_message(msg_type, len(content), memoryview(content))


def new_peer_init(username, conn_type):
    try:
        return PeerInit(init_user="local_user", target_user=username, conn_type=conn_type)
    except TypeError:
        msg = PeerInit()
        msg.init_user = "local_user"
        msg.target_user = username
        msg.conn_type = conn_type
        return msg


def new_thread():
    FakeSock.instances = []
    nt = slskproto.NetworkThread()
    nt._selector = FakeSelector()
    nt._server_username = "local_user"
    nt._server_address = ("server.slsk.example", 2242)
    nt._should_process_queue = True
    nt._sent_to_server = []
    nt._emitted_messages = []
    nt._send_message_to_server = nt._sent_to_server.append
    nt._emit_network_message_event = nt._emitted_messages.append
    nt._set_tcp_buffer_size = lambda *a, **k: None
    nt._bind_socket_interface = lambda *a, **k: None
    slskproto.socket.socket = lambda *a, **k: FakeSock(*a, **k)
    return nt


def attempts():
    return [addr for sock in FakeSock.instances for addr in sock.connect_ex_calls]


def run_getpeeraddress(label, ip_address, port):
    nt = new_thread()
    username = f"peer_{label}"
    nt._pending_init_msgs[username].append(new_peer_init(username, ConnectionType.PEER))
    process_server_message(nt, GetPeerAddress, pack_get_peer_address(username, ip_address, port))
    sent = [msg.__class__.__name__ for msg in nt._sent_to_server]
    return {
        "lane": args.lane,
        "surface": "GetPeerAddress pending local request",
        "case": label,
        "ip_address": ip_address,
        "port": port,
        "connect_attempts": attempts(),
        "connect_attempted": (ip_address, port) in attempts(),
        "sent_to_server_classes": sent,
        "connect_to_peer_side_effects": sent.count("ConnectToPeer"),
        "pending_cleared": username not in nt._pending_init_msgs,
    }


def run_connecttopeer(label, ip_address, port):
    nt = new_thread()
    username = f"peer_{label}"
    had_pending_before = bool(nt._pending_init_msgs.get(username))
    process_server_message(
        nt, ConnectToPeer, pack_connect_to_peer(username, ConnectionType.PEER, ip_address, port)
    )
    sent = [msg.__class__.__name__ for msg in nt._sent_to_server]
    return {
        "lane": args.lane,
        "surface": "ConnectToPeer unsolicited server request",
        "case": label,
        "ip_address": ip_address,
        "port": port,
        "had_local_pending_before": had_pending_before,
        "connect_attempts": attempts(),
        "connect_attempted": (ip_address, port) in attempts(),
        "sent_to_server_classes": sent,
    }


rows = []
for label, ip_address, port in [
    ("loopback_local_service", "127.0.0.1", 631),
    ("link_local_metadata", "169.254.169.254", 80),
    ("documentation_address", "203.0.113.10", 2234),
    ("lan_private_compatibility_baseline", "192.168.1.24", 2234),
]:
    rows.append(run_getpeeraddress(label, ip_address, port))

for label, ip_address, port in [
    ("loopback_local_service", "127.0.0.1", 631),
    ("link_local_metadata", "169.254.169.254", 80),
    ("lan_private_compatibility_baseline", "192.168.1.24", 2234),
]:
    rows.append(run_connecttopeer(label, ip_address, port))

rows.append(run_getpeeraddress("offline_zero_ip_baseline", "0.0.0.0", 2234))
rows.append(run_getpeeraddress("nonoffline_port_zero", "198.51.100.20", 0))

for row in rows:
    print(json.dumps(row, sort_keys=True))
