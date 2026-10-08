"""Current SEARCH-RESP-01A behavior witnesses, not desired policy tests."""
from search_resp_harness import dispatch, make_message, make_search


def test_unexpected_connection_username_is_currently_accepted():
    token = 750001
    search = make_search(token, users=["expected_peer"])
    msg = dispatch(search, make_message(token, "unexpected_peer"))
    assert msg.token == token


def test_expected_connection_username_is_currently_accepted():
    token = 750002
    search = make_search(token, users=["expected_peer"])
    msg = dispatch(search, make_message(token, "expected_peer"))
    assert msg.token == token
