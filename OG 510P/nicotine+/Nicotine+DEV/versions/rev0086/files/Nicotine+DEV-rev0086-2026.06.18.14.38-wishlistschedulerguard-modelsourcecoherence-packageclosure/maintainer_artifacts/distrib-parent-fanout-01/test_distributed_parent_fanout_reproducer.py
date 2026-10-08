from __future__ import annotations
import inspect, os, selectors, socket, struct, sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_SOURCE = os.environ.get('NICOTINE_SOURCE')
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

from pynicotine import slskmessages, slskproto  # noqa: E402
from pynicotine.slskmessages import (  # noqa: E402
    ConnectionType,
    PeerInit,
    PossibleParents,
    DistribBranchLevel,
    DistribBranchRoot,
    DistribSearch,
    EmbeddedMessage,
)


def pack_u8(value: int) -> bytes:
    return struct.pack('<B', value)


def pack_u32(value: int) -> bytes:
    return struct.pack('<I', value)


def pack_i32(value: int) -> bytes:
    return struct.pack('<i', value)


def pack_ip(ip_address: str) -> bytes:
    # slskmessages.unpack_ip expects wire order compatible with inet_aton()[::-1]
    return socket.inet_aton(ip_address)[::-1]


def pack_string(value: str) -> bytes:
    data = value.encode('utf-8', 'surrogatepass')
    return pack_u32(len(data)) + data


def pack_possible_parents(count: int) -> bytes:
    payload = bytearray(pack_u32(count))
    for i in range(count):
        payload += pack_string(f'parent_{i:03d}')
        payload += pack_ip(f'203.0.113.{(i % 200) + 1}')
        payload += pack_u32(2200 + i)
    return bytes(payload)


def make_peer_init(username: str, conn_type: str):
    try:
        return PeerInit(init_user=username, target_user=username, conn_type=conn_type)
    except TypeError:
        return PeerInit(target_user=username, conn_type=conn_type)


def frame_peer_init(msg) -> bytearray:
    content = msg.make_network_message()
    code = slskmessages.PEER_INIT_MESSAGE_CODES[msg.__class__]
    return bytearray(pack_u32(len(content) + 1) + pack_u8(code) + content)


def pack_distrib_branch_level(level: int) -> bytes:
    return pack_i32(level)


def pack_distrib_branch_root(root: str) -> bytes:
    return pack_string(root)


def pack_distrib_search(identifier: str = '1', user: str = 'searcher', token: int = 1234, term: str = 'needle') -> bytes:
    return pack_u32(ord(identifier)) + pack_string(user) + pack_u32(token) + pack_string(term)


def process_server_message(network_thread, msg_class, content: bytes):
    msg_type = slskmessages.SERVER_MESSAGE_CODES[msg_class]
    params = inspect.signature(network_thread._process_server_message).parameters
    if len(params) == 5:
        return network_thread._process_server_message(msg_type, len(content), bytearray(content), 0, len(content))
    return network_thread._process_server_message(msg_type, len(content), memoryview(content))


def process_distrib_message(network_thread, conn, msg_class, content: bytes):
    msg_type = slskmessages.DISTRIBUTED_MESSAGE_CODES[msg_class]
    params = inspect.signature(network_thread._process_distrib_message).parameters
    if len(params) == 6:
        return network_thread._process_distrib_message(conn, msg_type, len(content), bytearray(content), 0, len(content))
    return network_thread._process_distrib_message(conn, msg_type, len(content), memoryview(content))


class FakeSock:
    _next_fd = 7000
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
        self.shutdown_calls += 1
    def close(self):
        self.closed = True
        self.close_calls += 1
    def setblocking(self, flag):
        pass
    def setsockopt(self, *args):
        pass
    def connect_ex(self, addr):
        return 0
    def __repr__(self):
        return self.name


class FakeSelector:
    def __init__(self):
        self.registered = []
        self.unregistered = []
        self.modified = []
    def register(self, sock, events):
        self.registered.append((getattr(sock, 'name', repr(sock)), events))
    def unregister(self, sock):
        self.unregistered.append(getattr(sock, 'name', repr(sock)))
    def modify(self, sock, events):
        self.modified.append((getattr(sock, 'name', repr(sock)), events))


def new_thread():
    nt = slskproto.NetworkThread()
    nt._selector = FakeSelector()
    nt._server_username = 'local_user'
    nt._branch_root = 'local_user'
    nt._branch_level = 0
    nt._should_process_queue = True
    nt._server_address = ('server.slsk.example', 2242)
    nt._is_server_parent = False
    sent_server = []
    sent_peer = []
    initiated = []
    child_fanout = []
    emitted = []
    nt._send_message_to_server = sent_server.append
    nt._send_message_to_peer = lambda username, msg: sent_peer.append((username, msg.__class__.__name__, getattr(msg, 'level', None), getattr(msg, 'root_username', None)))
    nt._send_message_to_child_peers = lambda msg, msg_content=None: child_fanout.append((msg.__class__.__name__, getattr(msg, 'level', None), getattr(msg, 'root_username', None), len(msg_content) if msg_content is not None else None))
    nt._emit_network_message_event = lambda msg: emitted.append(msg.__class__.__name__ if msg is not None else None)
    nt._modify_connection_events = lambda conn, events: setattr(conn, 'io_events', events)
    nt._process_outgoing_messages = lambda msgs: None
    nt._set_tcp_buffer_size = lambda *a, **k: None
    nt._bind_socket_interface = lambda *a, **k: None
    nt._initiate_connection_to_peer = lambda username, conn_type, in_address=None: initiated.append((username, conn_type, in_address))
    return nt, sent_server, sent_peer, initiated, child_fanout, emitted


def add_incoming_d_conn(nt, username: str, sock_name: str, addr=('198.51.100.50', 4444)):
    sock = FakeSock(sock_name)
    conn = slskproto.PeerConnection(sock=sock, addr=addr, io_events=selectors.EVENT_READ)
    conn.is_established = True
    conn.in_buffer += frame_peer_init(make_peer_init(username, ConnectionType.DISTRIBUTED))
    nt._conns[sock] = conn
    nt._selector.register(sock, selectors.EVENT_READ)
    nt._num_sockets += 1
    parsed = nt._process_peer_init_input(conn)
    return sock, conn, parsed


def test_possibleparents_with_more_than_documented_ten_causes_one_outbound_attempt_per_distinct_parent():
    nt, sent_server, sent_peer, initiated, child_fanout, emitted = new_thread()
    payload = pack_possible_parents(25)
    result = process_server_message(nt, PossibleParents, payload)
    assert result is True
    assert len(nt._potential_parents) == 25
    assert len(initiated) == 25
    assert {entry[0] for entry in initiated} == {f'parent_{i:03d}' for i in range(25)}
    assert all(entry[1] == ConnectionType.DISTRIBUTED for entry in initiated)


def test_distinct_claimed_distributed_child_usernames_can_fill_child_slot_limit_and_turn_off_accept_children():
    nt, sent_server, sent_peer, initiated, child_fanout, emitted = new_thread()
    nt._is_server_parent = True
    nt._max_distrib_children = 3
    nt._branch_root = 'local_user'
    nt._branch_level = 0
    for i in range(3):
        sock, conn, parsed = add_incoming_d_conn(nt, f'child_claim_{i}', f'child_{i}')
        assert parsed is not None
        assert sock.closed is False
    assert sorted(nt._child_peers) == ['child_claim_0', 'child_claim_1', 'child_claim_2']
    assert len(nt._child_peers) == 3
    assert sent_server and sent_server[-1].__class__.__name__ == 'AcceptChildren'
    assert getattr(sent_server[-1], 'enabled', None) is False
    overflow_sock, overflow_conn, overflow_parsed = add_incoming_d_conn(nt, 'child_claim_3', 'child_overflow')
    assert overflow_parsed is not None
    assert overflow_sock.closed is True
    assert 'child_claim_3' not in nt._child_peers


def test_duplicate_claimed_distributed_child_username_replaces_existing_child_connection_pb01_support():
    nt, sent_server, sent_peer, initiated, child_fanout, emitted = new_thread()
    nt._is_server_parent = True
    nt._max_distrib_children = 3
    first_sock, first_conn, first = add_incoming_d_conn(nt, 'same_claim', 'child_same_first')
    second_sock, second_conn, second = add_incoming_d_conn(nt, 'same_claim', 'child_same_second')
    assert first is not None and second is not None
    assert 'same_claim' in nt._child_peers
    # Current behavior: the second claimed PeerInit replaces the first child connection before duplicate-child rejection can preserve the old one.
    assert nt._child_peers['same_claim'] is second_conn
    assert first_sock.closed is True
    assert second_sock.closed is False
    assert len(nt._child_peers) == 1


def test_parent_branch_root_update_accepts_and_propagates_oversized_root_string():
    nt, sent_server, sent_peer, initiated, child_fanout, emitted = new_thread()
    parent_sock = FakeSock('parent_sock')
    parent_init = make_peer_init('parent_user', ConnectionType.DISTRIBUTED)
    parent_init.sock = parent_sock
    parent_conn = slskproto.PeerConnection(sock=parent_sock, addr=('198.51.100.88', 5555), io_events=selectors.EVENT_READ, init=parent_init)
    parent_conn.is_established = True
    nt._conns[parent_sock] = parent_conn
    nt._selector.register(parent_sock, selectors.EVENT_READ)
    nt._num_sockets += 1
    if hasattr(nt, '_parent_conn'):
        nt._parent_conn = parent_conn
    else:
        nt._parent = SimpleNamespace(conn=parent_conn)
    nt._branch_root = 'old_root'
    oversized_root = 'root_' + ('A' * 4096)
    result = process_distrib_message(nt, parent_conn, DistribBranchRoot, pack_distrib_branch_root(oversized_root))
    assert result is True
    assert nt._branch_root == oversized_root
    assert any(msg.__class__.__name__ == 'BranchRoot' and getattr(msg, 'user', None) == oversized_root for msg in sent_server)
    assert any(entry[0] == 'DistribBranchRoot' and entry[2] == oversized_root for entry in child_fanout)


def test_server_embedded_unsupported_distributed_message_is_not_forwarded_on_current_future_lanes_but_is_3310_backport_note():
    nt, sent_server, sent_peer, initiated, child_fanout, emitted = new_thread()
    # Make child fanout observable.
    nt._is_server_parent = False
    nt._max_distrib_children = 3
    payload = pack_u8(slskmessages.DISTRIBUTED_MESSAGE_CODES[DistribBranchRoot]) + pack_distrib_branch_root('server_root_claim')
    result = process_server_message(nt, EmbeddedMessage, payload)
    is_legacy_forwarding = any(entry[0] == 'DistribEmbeddedMessage' for entry in child_fanout)
    # 3.3.10 forwards the raw embedded message before validation; 3.3.x/master do not.
    if is_legacy_forwarding:
        assert emitted == ['DistribBranchRoot']
    else:
        assert child_fanout == []
        assert emitted == []
    assert result is True
