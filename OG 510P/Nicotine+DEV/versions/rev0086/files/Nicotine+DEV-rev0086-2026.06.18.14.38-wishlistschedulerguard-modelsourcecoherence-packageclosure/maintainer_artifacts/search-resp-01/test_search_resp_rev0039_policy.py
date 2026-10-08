"""Assertions encoded by the historical rev0039 username-set guard."""
from search_resp_harness import dispatch, make_message, make_search


def test_unexpected_connection_username_is_rejected():
    token = 750011
    search = make_search(token, users=["expected_peer"])
    msg = dispatch(search, make_message(token, "unexpected_peer"))
    assert msg.token is None


def test_expected_connection_username_is_preserved():
    token = 750012
    search = make_search(token, users=["expected_peer"])
    msg = dispatch(search, make_message(token, "expected_peer"))
    assert msg.token == token


def test_empty_expected_user_set_rejects_closed():
    token = 750013
    search = make_search(token, users=[])
    msg = dispatch(search, make_message(token, "unexpected_peer"))
    assert msg.token is None


def test_global_mode_remains_broad_source_compatible():
    token = 750014
    search = make_search(token, mode="global")
    msg = dispatch(search, make_message(token, "any_peer"))
    assert msg.token == token
