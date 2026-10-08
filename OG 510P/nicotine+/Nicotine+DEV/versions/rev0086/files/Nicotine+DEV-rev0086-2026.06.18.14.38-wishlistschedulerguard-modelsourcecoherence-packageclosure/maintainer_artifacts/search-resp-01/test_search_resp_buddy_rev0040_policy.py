"""Behavior encoded by the historical rev0040 buddy-snapshot guard."""
from buddy_search_harness import install_environment, make_component, recipient_names
from search_resp_harness import dispatch, make_message, make_search


def test_off_snapshot_connection_name_is_rejected():
    search = make_search(530011, mode="buddies", users=("buddy_a", "buddy_b"))
    message = make_message(search.token, "not_a_buddy")
    dispatch(search, message)
    assert message.token is None


def test_expected_connection_name_is_preserved():
    search = make_search(530012, mode="buddies", users=("buddy_a", "buddy_b"))
    message = make_message(search.token, "buddy_a")
    dispatch(search, message)
    assert message.token == search.token


def test_empty_snapshot_rejects_closed():
    search = make_search(530013, mode="buddies", users=())
    message = make_message(search.token, "buddy_a")
    dispatch(search, message)
    assert message.token is None


def test_initial_search_captures_and_sends_same_snapshot(monkeypatch):
    component = make_component()
    _core, sent = install_environment(monkeypatch, ["buddy_a", "buddy_b"])
    component.do_search("rareprobe", mode="buddies", switch_page=False)
    search = next(iter(component.searches.values()))
    assert tuple(search.users or ()) == ("buddy_a", "buddy_b")
    assert recipient_names(sent) == ["buddy_a", "buddy_b"]
