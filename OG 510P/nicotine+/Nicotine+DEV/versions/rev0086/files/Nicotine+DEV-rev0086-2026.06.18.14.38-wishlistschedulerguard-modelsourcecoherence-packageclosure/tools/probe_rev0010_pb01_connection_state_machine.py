#!/usr/bin/env python3
"""rev0010 PB-01 current-behavior probe.

Hermetic handler/state-machine harness for Nicotine+ peer-connection binding.
It does not open real network sockets. It imports one source lane, builds fake
PeerConnection/socket objects, and exercises the same NetworkThread methods that
handle PeerInit/PierceFireWall/post-init data.

Covered invariants:
- U-168: direct PeerInit claiming an existing username+connection type replaces
  an existing primary P or D connection and migrates queued outgoing messages.
- U-176: a secondary P/D/F connection that shares the same PeerInit object is
  promoted to primary after any post-init message/frame. For P, an additional
  PierceFireWall-token path shows U-165 as support/context.
"""
import argparse
import json
import selectors
import struct
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--lane", required=True)
args = parser.parse_args()

sys.path.insert(0, str(Path(args.source).resolve()))

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
    _next = 3000

    def __init__(self, name):
        self.name = name
        self.closed = False
        self.shutdown_calls = 0
        self.close_calls = 0
        self._fileno = FakeSock._next
        FakeSock._next += 1

    def fileno(self):
        return self._fileno

    def shutdown(self, _how):
        self.shutdown_calls += 1

    def close(self):
        self.close_calls += 1
        self.closed = True

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


def frame_peer_init(msg):
    content = msg.make_network_message()
    code = slskmessages.PEER_INIT_MESSAGE_CODES[msg.__class__]
    return bytearray(struct.pack("<I", len(content) + 1) + bytes([code]) + content)


def frame_peer_message(msg):
    content = msg.make_network_message()
    code = slskmessages.PEER_MESSAGE_CODES[msg.__class__]
    return bytearray(struct.pack("<II", len(content) + 4, code) + content)


def frame_unknown_peer_message():
    return bytearray(struct.pack("<II", 4, 0xFEEDBEEF))


def frame_unknown_distrib_message():
    return bytearray(struct.pack("<IB", 1, 0xEF))


def frame_file_transfer_init(token=31337):
    msg = FileTransferInit(token=token)
    return bytearray(msg.make_network_message())


def new_peer_init(username, conn_type):
    try:
        return PeerInit(init_user=username, target_user=username, conn_type=conn_type)
    except TypeError:
        msg = PeerInit()
        msg.init_user = username
        msg.target_user = username
        msg.conn_type = conn_type
        return msg


def new_thread():
    nt = slskproto.NetworkThread()
    nt._selector = FakeSelector()
    nt._server_username = "local_user"
    nt._should_process_queue = True
    if hasattr(nt, "_set_tcp_buffer_size"):
        nt._set_tcp_buffer_size = lambda *a, **k: None
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

    nt._emit_network_message_event = emit
    nt._process_outgoing_messages = capture_outgoing
    nt._send_message_to_server = lambda msg: None
    nt._modify_connection_events = lambda conn, events: setattr(conn, "io_events", events)
    return nt, emitted, sent


def add_conn(nt, username, conn_type, sock_name, addr, init=None, put_username_key=True):
    sock = FakeSock(sock_name)
    if init is None:
        init = new_peer_init(username, conn_type)
        init.sock = sock
    conn = slskproto.PeerConnection(sock=sock, addr=addr, io_events=selectors.EVENT_READ, init=init)
    conn.is_established = True
    nt._conns[sock] = conn
    nt._selector.register(sock, selectors.EVENT_READ)
    nt._num_sockets += 1
    if put_username_key:
        nt._username_init_msgs[username + conn_type] = init
    return sock, conn, init


def probe_u168_direct_replace(conn_type):
    nt, emitted, sent = new_thread()
    victim = "victim_user"
    nt._user_addresses[victim] = ("198.51.100.10", 2234)
    if conn_type == ConnectionType.DISTRIBUTED:
        # Put the distributed path into a state where a child peer is acceptable; otherwise
        # the replacement would be closed for the unrelated "no parent/server-parent" policy.
        nt._is_server_parent = True
        nt._max_distrib_children = max(getattr(nt, "_max_distrib_children", 0), 10)
        nt._branch_level = 1
        nt._branch_root = "root_user"
    primary_sock, primary_conn, primary_init = add_conn(
        nt, victim, conn_type, f"primary_{conn_type}", ("198.51.100.10", 2234)
    )
    if conn_type == ConnectionType.DISTRIBUTED:
        nt._child_peers[victim] = primary_conn
    # A pending message on the old init lets us observe migration to the replacement.
    primary_init.outgoing_msgs.append(UserInfoRequest() if conn_type == ConnectionType.PEER else SharedFileListRequest())

    incoming_sock = FakeSock(f"incoming_replacer_{conn_type}")
    incoming_conn = slskproto.PeerConnection(sock=incoming_sock, addr=("203.0.113.66", 5555), io_events=selectors.EVENT_READ)
    incoming_conn.is_established = True
    incoming_conn.in_buffer += frame_peer_init(new_peer_init(victim, conn_type))
    nt._conns[incoming_sock] = incoming_conn
    nt._selector.register(incoming_sock, selectors.EVENT_READ)
    nt._num_sockets += 1

    parsed_init = nt._process_peer_init_input(incoming_conn)
    after_key = nt._username_init_msgs.get(victim + conn_type)

    return {
        "id": "U-168",
        "conn_type": conn_type,
        "scenario": "incoming direct PeerInit claims existing username and connection type",
        "parsed_target_user": getattr(parsed_init, "target_user", None),
        "parsed_conn_type": getattr(parsed_init, "conn_type", None),
        "old_primary_closed": primary_sock.closed,
        "old_primary_removed_from_conns": primary_sock not in nt._conns,
        "replacement_kept": incoming_sock in nt._conns,
        "username_key_sock_after": getattr(getattr(after_key, "sock", None), "name", None),
        "pending_outgoing_messages_migrated_to_replacement": any(e.get("sock") == incoming_sock.name for e in sent),
        "selector_unregistered": nt._selector.unregistered[:],
        "emitted": emitted,
        "sent": sent,
        "result": "REPLACE_CONFIRMED" if (
            primary_sock.closed
            and primary_sock not in nt._conns
            and getattr(getattr(after_key, "sock", None), "name", None) == incoming_sock.name
        ) else "NOT_REPRODUCED",
    }


def post_init_frame_for(conn_type):
    if conn_type == ConnectionType.PEER:
        return frame_unknown_peer_message()
    if conn_type == ConnectionType.DISTRIBUTED:
        return frame_unknown_distrib_message()
    if conn_type == ConnectionType.FILE:
        return frame_file_transfer_init()
    raise AssertionError(conn_type)


def probe_u176_secondary_promotion(conn_type):
    nt, emitted, sent = new_thread()
    victim = "victim_user"
    nt._user_addresses[victim] = ("198.51.100.10", 2234)
    primary_sock, primary_conn, init = add_conn(
        nt, victim, conn_type, f"direct_primary_{conn_type}", ("198.51.100.10", 2234)
    )
    secondary_sock, secondary_conn, _ = add_conn(
        nt, victim, conn_type, f"secondary_{conn_type}", ("203.0.113.77", 6666), init=init, put_username_key=False
    )
    before = getattr(init.sock, "name", None)
    secondary_conn.in_buffer += post_init_frame_for(conn_type)
    nt._process_conn_incoming_messages(secondary_conn)
    after = getattr(init.sock, "name", None)
    return {
        "id": "U-176",
        "conn_type": conn_type,
        "scenario": "secondary connection shares PeerInit object with primary; post-init data promotes it to primary",
        "before_primary_sock": before,
        "after_primary_sock": after,
        "secondary_promoted": after == secondary_sock.name,
        "old_primary_still_open": primary_sock in nt._conns and not primary_sock.closed,
        "secondary_still_open": secondary_sock in nt._conns and not secondary_sock.closed,
        "secondary_post_init_activity": secondary_conn.has_post_init_activity,
        "emitted": emitted,
        "sent": sent,
        "result": "PROMOTION_CONFIRMED" if after == secondary_sock.name else "NOT_REPRODUCED",
    }


def probe_u176_late_piercefirewall_support():
    nt, emitted, sent = new_thread()
    victim = "victim_user"
    nt._user_addresses[victim] = ("198.51.100.10", 2234)
    primary_sock, primary_conn, init = add_conn(
        nt, victim, ConnectionType.PEER, "direct_primary_after_pf", ("198.51.100.10", 2234)
    )
    token = 424242
    if hasattr(nt, "_token_init_msgs"):
        nt._token_init_msgs[token] = (init, time.monotonic())
        token_table = "_token_init_msgs"
    else:
        nt._indirect_token_init_msgs[token] = init
        token_table = "_indirect_token_init_msgs"

    secondary_sock = FakeSock("secondary_indirect_pf")
    secondary_conn = slskproto.PeerConnection(sock=secondary_sock, addr=("203.0.113.88", 7777), io_events=selectors.EVENT_READ)
    secondary_conn.is_established = True
    secondary_conn.in_buffer += frame_peer_init(PierceFireWall(token=token))
    nt._conns[secondary_sock] = secondary_conn
    nt._selector.register(secondary_sock, selectors.EVENT_READ)
    nt._num_sockets += 1

    parsed = nt._process_peer_init_input(secondary_conn)
    after_pf = getattr(init.sock, "name", None)
    secondary_conn.in_buffer += frame_peer_message(UserInfoRequest())
    nt._process_conn_incoming_messages(secondary_conn)
    after_msg = getattr(init.sock, "name", None)
    return {
        "id": "U-176/U-165-support",
        "scenario": "valid PierceFireWall token creates secondary P connection while direct primary remains; next P message promotes secondary",
        "token_table": token_table,
        "parsed_target_user": getattr(parsed, "target_user", None),
        "primary_after_piercefirewall": after_pf,
        "primary_after_secondary_message": after_msg,
        "secondary_bound_to_user": getattr(secondary_conn.init, "target_user", None),
        "secondary_still_open": secondary_sock in nt._conns and not secondary_sock.closed,
        "result": "LATE_INDIRECT_SECONDARY_PROMOTED" if after_pf == "direct_primary_after_pf" and after_msg == "secondary_indirect_pf" else "NOT_REPRODUCED",
    }


record = {
    "lane": args.lane,
    "source": str(Path(args.source).resolve()),
    "status": "ok",
    "u168_direct_replace": [
        probe_u168_direct_replace(ConnectionType.PEER),
        probe_u168_direct_replace(ConnectionType.DISTRIBUTED),
    ],
    "u176_secondary_promotion": [
        probe_u176_secondary_promotion(ConnectionType.PEER),
        probe_u176_secondary_promotion(ConnectionType.DISTRIBUTED),
        probe_u176_secondary_promotion(ConnectionType.FILE),
    ],
    "u176_late_piercefirewall_support": probe_u176_late_piercefirewall_support(),
}
print(json.dumps(record, sort_keys=True))
