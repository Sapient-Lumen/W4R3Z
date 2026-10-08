from search_repeat_model import Response, SearchRepeatSystem


def test_search_again_reuses_the_page_token_and_preserves_rows():
    system = SearchRepeatSystem(token=41, cap=4)
    system.seed_results(["alice"])

    assert system.search_again_current(["alice", "bob"]) == 2
    assert {request.token for request in system.requests} == {41}
    assert system.page.results == {"alice": "seed:alice"}


def test_repeat_response_from_existing_username_is_ignored():
    system = SearchRepeatSystem(token=41, cap=4)
    system.seed_results(["alice"])
    system.search_again_current(["alice"])

    outcome = system.receive(Response(41, "alice", "new-list", 1))

    assert outcome == "ignored-existing-user"
    assert system.page.results["alice"] == "seed:alice"


def test_new_username_can_merge_while_capacity_remains():
    system = SearchRepeatSystem(token=41, cap=4)
    system.seed_results(["alice"])
    system.search_again_current(["bob"])

    assert system.receive(Response(41, "bob", "fresh")) == "accepted"
    assert list(system.page.results) == ["alice", "bob"]
