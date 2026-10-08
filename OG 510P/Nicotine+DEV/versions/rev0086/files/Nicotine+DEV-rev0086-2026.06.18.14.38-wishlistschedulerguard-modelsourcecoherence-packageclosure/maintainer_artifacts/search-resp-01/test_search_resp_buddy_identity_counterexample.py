"""Counterexamples to treating the rev0040 guard as authentication."""
from search_resp_harness import dispatch, make_search, response_from_peerinit_claim


def test_expected_name_claimed_in_peerinit_passes_buddy_guard():
    token = 530021
    search = make_search(token, mode="buddies", users=("buddy_a", "buddy_b"))
    init, message = response_from_peerinit_claim(token, claimed_username="buddy_a")
    assert init.target_user == "buddy_a"
    dispatch(search, message)
    assert message.token == token


def test_body_username_is_discarded_in_favor_of_connection_claim():
    token = 530022
    search = make_search(token, mode="buddies", users=("buddy_a",))
    _init, message = response_from_peerinit_claim(
        token,
        claimed_username="buddy_a",
        search_username="different_body_name",
    )
    assert message.username == "buddy_a"
    assert message.search_username is None
    dispatch(search, message)
    assert message.token == token
