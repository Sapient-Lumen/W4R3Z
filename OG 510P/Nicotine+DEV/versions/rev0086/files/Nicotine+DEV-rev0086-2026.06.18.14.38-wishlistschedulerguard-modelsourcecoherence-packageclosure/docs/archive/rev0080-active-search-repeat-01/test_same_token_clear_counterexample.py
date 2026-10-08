from search_repeat_model import Response, SearchRepeatSystem


def test_clear_same_token_restores_capacity_but_accepts_delayed_old_response():
    system = SearchRepeatSystem(token=90, cap=2)
    system.seed_results(["old-a", "old-b"])

    system.clear_same_token(["fresh-peer"])
    delayed = Response(90, "old-peer", "delayed-from-prior-request", originating_click=0)

    assert system.receive(delayed) == "accepted"
    assert system.page.results == {"old-peer": "delayed-from-prior-request"}


def test_same_token_has_no_wire_epoch_information_to_separate_old_and_new():
    system = SearchRepeatSystem(token=90, cap=3)
    system.clear_same_token(["peer"])

    old = Response(90, "old", "old", originating_click=0)
    new = Response(90, "new", "new", originating_click=1)

    assert system.receive(old) == "accepted"
    assert system.receive(new) == "accepted"
    assert set(system.page.results) == {"old", "new"}
