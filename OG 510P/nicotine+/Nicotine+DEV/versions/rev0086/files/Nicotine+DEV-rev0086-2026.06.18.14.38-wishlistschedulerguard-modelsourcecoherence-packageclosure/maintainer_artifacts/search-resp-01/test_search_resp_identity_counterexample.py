"""Counterexample: the rev0039 comparison is not peer authentication."""
from search_resp_harness import dispatch, make_search, response_from_peerinit_claim


def test_wire_peerinit_name_becomes_connection_target_user():
    init, msg = response_from_peerinit_claim(750021, claimed_username="expected_peer")
    assert init.init_user == "expected_peer"
    assert init.target_user == "expected_peer"
    assert msg.username == "expected_peer"


def test_expected_name_claim_passes_user_scope_guard():
    token = 750022
    search = make_search(token, users=["expected_peer"])
    _init, msg = response_from_peerinit_claim(token, claimed_username="expected_peer")
    dispatch(search, msg)
    assert msg.token == token


def test_wrong_payload_username_does_not_override_connection_claim():
    token = 750023
    search = make_search(token, users=["expected_peer"])
    _init, msg = response_from_peerinit_claim(
        token,
        claimed_username="expected_peer",
        search_username="legacy_client_wrong_name",
    )
    dispatch(search, msg)
    assert msg.username == "expected_peer"
    assert msg.search_username is None
    assert msg.token == token
