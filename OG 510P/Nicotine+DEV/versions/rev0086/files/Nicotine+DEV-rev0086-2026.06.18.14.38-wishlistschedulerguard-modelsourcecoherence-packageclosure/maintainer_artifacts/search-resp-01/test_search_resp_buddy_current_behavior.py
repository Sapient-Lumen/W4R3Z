"""Exact-current SEARCH-RESP-01B behavior witnesses."""
from buddy_search_harness import install_environment, make_component, recipient_names
from search_resp_harness import dispatch, make_message, make_search


def test_current_buddy_search_does_not_store_recipient_snapshot(monkeypatch):
    component = make_component()
    _core, sent = install_environment(monkeypatch, ["buddy_a", "buddy_b"])
    component.do_search("rareprobe", mode="buddies", switch_page=False)
    search = next(iter(component.searches.values()))
    assert search.users is None
    assert recipient_names(sent) == ["buddy_a", "buddy_b"]


def test_current_handler_accepts_off_snapshot_connection_name():
    search = make_search(530001, mode="buddies", users=("buddy_a", "buddy_b"))
    message = make_message(search.token, "not_a_buddy")
    dispatch(search, message)
    assert message.token == search.token


def test_current_handler_preserves_expected_connection_name():
    search = make_search(530002, mode="buddies", users=("buddy_a", "buddy_b"))
    message = make_message(search.token, "buddy_b")
    dispatch(search, message)
    assert message.token == search.token
