"""Executable counterexample for the superseded rev0038 blanket guard."""
from pb01_harness import (
    ConnectionType,
    FakeSock,
    PierceFireWall,
    add_established_connection,
    add_incoming_direct,
    frame_peer_init,
    new_thread,
    selectors,
    slskproto,
    time,
)


def test_rev0038_guard_can_leave_peers_on_opposite_connection_legs():
    initiator = new_thread()
    responder = new_thread()

    a_direct_sock, _a_direct_conn, a_init = add_established_connection(
        initiator,
        "responder_b",
        ConnectionType.PEER,
        "A_to_B_direct",
        ("198.51.100.20", 2234),
    )
    token = 912345
    initiator._token_init_msgs[token] = (a_init, time.monotonic())
    a_secondary_sock = FakeSock("B_to_A_indirect_at_A")
    a_secondary = slskproto.PeerConnection(
        sock=a_secondary_sock,
        addr=("203.0.113.20", 4444),
        io_events=selectors.EVENT_READ,
    )
    a_secondary.is_established = True
    a_secondary.in_buffer += frame_peer_init(PierceFireWall(token=token))
    initiator._conns[a_secondary_sock] = a_secondary
    initiator._selector.register(a_secondary_sock, selectors.EVENT_READ)
    initiator._num_sockets += 1

    assert initiator._process_peer_init_input(a_secondary) is a_init
    assert a_init.sock is a_direct_sock

    b_indirect_sock, _b_indirect_conn, b_init = add_established_connection(
        responder,
        "initiator_a",
        ConnectionType.PEER,
        "B_to_A_indirect_response",
        ("198.51.100.30", 2234),
        response_token=token,
    )
    b_direct_sock, b_direct_conn = add_incoming_direct(
        responder,
        "initiator_a",
        "A_to_B_direct_at_B",
    )

    parsed = responder._process_peer_init_input(b_direct_conn)
    active_b = responder._username_init_msgs[
        "initiator_a" + ConnectionType.PEER
    ]

    assert parsed is None
    assert active_b is b_init
    assert active_b.sock is b_indirect_sock
    assert b_direct_sock.closed is True
    assert a_init.sock.name.startswith("A_to_B_direct")
    assert active_b.sock.name.startswith("B_to_A_indirect")
