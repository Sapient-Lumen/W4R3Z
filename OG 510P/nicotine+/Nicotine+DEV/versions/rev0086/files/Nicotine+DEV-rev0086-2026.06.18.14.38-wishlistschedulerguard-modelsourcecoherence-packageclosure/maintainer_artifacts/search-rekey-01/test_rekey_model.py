from search_rekey_model import SearchRepeatSystem


def test_current_same_token_retry_is_dead_at_cap_and_can_repeat_fanout():
    system = SearchRepeatSystem(cap=2)
    system.seed_results("alice", "bob")
    for _ in range(12):
        system.current_search_again(tuple(f"buddy-{index}" for index in range(32)))
        assert system.accept_response(system.token, "new-user") == "retired-at-cap"
    assert len(system.requests) == 384
    assert system.page.results == {"alice": "seed:alice", "bob": "seed:bob"}


def test_current_same_token_retry_below_cap_merges_and_deduplicates_users():
    system = SearchRepeatSystem(cap=3)
    system.seed_results("alice")
    system.current_search_again()
    assert system.accept_response(system.token, "alice") == "duplicate-user"
    assert system.accept_response(system.token, "bob") == "accepted"
    assert set(system.page.results) == {"alice", "bob"}


def test_rekey_clears_capacity_and_old_epoch_is_rejected():
    system = SearchRepeatSystem(cap=2)
    system.seed_results("alice", "bob")
    old_token = system.token
    new_token = system.rekey_same_page()
    assert new_token == old_token + 1
    assert system.accept_response(old_token, "late") == "rejected-token"
    assert system.accept_response(new_token, "fresh") == "accepted"
    assert system.page.results == {"fresh": "fresh:fresh"}


def test_rekey_preserves_page_identity_view_state_and_non_result_owners():
    system = SearchRepeatSystem(cap=2)
    page = system.page
    search = system.search
    page.filters["include"] = "lossless"
    page.grouping = "user_grouping"
    page.sort = ("size", "descending")
    page.tab_index = 4
    page.focused = True
    page.selected_users.add("alice")
    page.selected_results.add(9)
    system.seed_results("alice")
    history_writes = system.history_writes
    plugin_runs = system.plugin_runs
    system.rekey_same_page()
    assert system.page is page
    assert system.search is search
    assert page.filters == {"include": "lossless"}
    assert page.grouping == "user_grouping"
    assert page.sort == ("size", "descending")
    assert page.tab_index == 4 and page.focused
    assert page.selected_users == set() and page.selected_results == set()
    assert system.history_writes == history_writes
    assert system.plugin_runs == plugin_runs
    assert system.recently_closed == []


def test_rapid_repeat_accepts_only_latest_epoch():
    system = SearchRepeatSystem()
    first = system.token
    second = system.rekey_same_page()
    third = system.rekey_same_page()
    fourth = system.rekey_same_page()
    assert tuple(system.searches) == (fourth,)
    assert tuple(system.pages) == (fourth,)
    assert system.accept_response(first, "one") == "rejected-token"
    assert system.accept_response(second, "two") == "rejected-token"
    assert system.accept_response(third, "three") == "rejected-token"
    assert system.accept_response(fourth, "four") == "accepted"


def test_offline_click_is_nondestructive():
    system = SearchRepeatSystem(cap=2)
    system.seed_results("alice")
    before = (system.token, dict(system.page.results), list(system.requests))
    assert system.rekey_same_page(online=False) is None
    assert (system.token, system.page.results, system.requests) == before


def test_wishlist_retains_token_rows_seen_history_and_same_token_retry():
    system = SearchRepeatSystem(mode="wishlist", cap=2)
    system.search.ignored_users.add("seen-user")
    system.seed_results("alice")
    page = system.page
    token = system.token
    assert system.rekey_same_page(("server",)) == token
    assert system.token == token
    assert system.page is page
    assert system.page.results == {"alice": "seed:alice"}
    assert system.search.ignored_users == {"seen-user"}
    assert len(system.requests) == 1
    assert system.requests[0].token == token
