"""Narrow research experiment: reject direct-over-direct, preserve races."""
from pb01_harness import (
    ConnectionType,
    FakeSock,
    PierceFireWall,
    UserInfoRequest,
    add_established_connection,
    add_incoming_direct,
    frame_peer_init,
    frame_peer_message,
    new_thread,
    selectors,
    slskproto,
    time,
)


def test_later_direct_does_not_replace_established_direct_primary():
    thread = new_thread()
    username = "peer_user"
    primary_sock, _primary_conn, primary_init = add_established_connection(
        thread,
        username,
        ConnectionType.PEER,
        "direct_primary",
        ("198.51.100.10", 2234),
    )
    incoming_sock, incoming_conn = add_incoming_direct(thread, username)

    parsed = thread._process_peer_init_input(incoming_conn)
    active = thread._username_init_msgs[username + ConnectionType.PEER]

    assert parsed is None
    assert active is primary_init
    assert active.sock is primary_sock
    assert primary_sock.closed is False
    assert incoming_sock.closed is True


def test_direct_still_supersedes_established_indirect_response_connection():
    thread = new_thread()
    username = "peer_user"
    indirect_sock, _indirect_conn, indirect_init = add_established_connection(
        thread,
        username,
        ConnectionType.PEER,
        "outgoing_indirect_response",
        ("198.51.100.10", 2234),
        response_token=876543,
    )
    incoming_sock, incoming_conn = add_incoming_direct(thread, username)

    parsed = thread._process_peer_init_input(incoming_conn)
    active = thread._username_init_msgs[username + ConnectionType.PEER]

    assert parsed is active
    assert active is not indirect_init
    assert active.sock is incoming_sock
    assert indirect_sock.closed is True


def test_secondary_message_promotion_is_not_blanket_disabled():
    thread = new_thread()
    username = "peer_user"
    primary_sock, _primary_conn, init = add_established_connection(
        thread,
        username,
        ConnectionType.PEER,
        "direct_primary",
        ("198.51.100.10", 2234),
    )
    token = 424242
    thread._token_init_msgs[token] = (init, time.monotonic())
    secondary_sock = FakeSock("secondary_indirect_pf")
    secondary_conn = slskproto.PeerConnection(
        sock=secondary_sock,
        addr=("203.0.113.88", 7777),
        io_events=selectors.EVENT_READ,
    )
    secondary_conn.is_established = True
    secondary_conn.in_buffer += frame_peer_init(PierceFireWall(token=token))
    thread._conns[secondary_sock] = secondary_conn
    thread._selector.register(secondary_sock, selectors.EVENT_READ)
    thread._num_sockets += 1

    assert thread._process_peer_init_input(secondary_conn) is init
    assert init.sock is primary_sock

    secondary_conn.in_buffer += frame_peer_message(UserInfoRequest())
    thread._process_conn_incoming_messages(secondary_conn)

    assert init.sock is secondary_sock
