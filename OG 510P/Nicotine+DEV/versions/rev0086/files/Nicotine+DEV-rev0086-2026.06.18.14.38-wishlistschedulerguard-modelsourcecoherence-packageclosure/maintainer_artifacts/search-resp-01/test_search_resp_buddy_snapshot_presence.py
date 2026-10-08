"""The historical guard distinguishes absent from present-empty snapshots."""
from search_resp_harness import dispatch, make_message, make_search


def test_absent_snapshot_remains_broad_source_compatible():
    search = make_search(530041, mode="buddies", users=None)
    message = make_message(search.token, "not_in_any_snapshot")
    dispatch(search, message)
    assert message.token == search.token


def test_present_empty_snapshot_is_rejected_by_rev0040_guard():
    search = make_search(530042, mode="buddies", users=())
    message = make_message(search.token, "not_in_any_snapshot")
    dispatch(search, message)
    assert message.token is None
