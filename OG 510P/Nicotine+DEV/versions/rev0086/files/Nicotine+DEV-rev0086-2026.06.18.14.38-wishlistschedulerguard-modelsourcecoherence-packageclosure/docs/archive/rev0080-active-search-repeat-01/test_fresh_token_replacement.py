from search_repeat_model import Response, SearchRepeatSystem, policy_matrix


def test_fresh_token_page_replacement_restores_capacity_and_rejects_old_token():
    system = SearchRepeatSystem(token=100, cap=2)
    system.seed_results(["alice", "bob"])

    old_token, new_token = system.replace_page_fresh_token(["carol"])

    assert (old_token, new_token) == (100, 101)
    assert system.page.count == 0
    assert system.receive(Response(old_token, "late", "stale")) == "rejected-token"
    assert system.receive(Response(new_token, "carol", "fresh")) == "accepted"
    assert system.page.results == {"carol": "fresh"}


def test_page_replacement_makes_view_state_carry_an_explicit_policy():
    system = SearchRepeatSystem(token=100, cap=2)
    system.page.view_state = {"filter": "lossless", "grouping": "folder"}

    system.replace_page_fresh_token([], preserve_view_state=False)
    assert system.page.view_state == {}

    system.page.view_state = {"filter": "audio"}
    system.replace_page_fresh_token([], preserve_view_state=True)
    assert system.page.view_state == {"filter": "audio"}


def test_policy_matrix_does_not_claim_ack_is_mandatory_for_page_recreation():
    rows = {row["policy"]: row for row in policy_matrix()}

    assert rows["fresh-token page replacement"]["network_ack_required"] == (
        "no for best-effort new-search semantics"
    )
    assert rows["fresh-token in-place transactional refresh"]["network_ack_required"].startswith("yes")
