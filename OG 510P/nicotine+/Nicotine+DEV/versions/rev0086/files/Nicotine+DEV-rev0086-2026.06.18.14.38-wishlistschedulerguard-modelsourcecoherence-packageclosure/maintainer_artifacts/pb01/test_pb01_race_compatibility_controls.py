"""Compatibility control derived from the documented simultaneous race."""
from pb01_harness import (
    ConnectionType,
    add_established_connection,
    add_incoming_direct,
    new_thread,
)


def test_direct_peerinit_supersedes_established_indirect_response_connection():
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
