from wishlist_inbox_model import PersistentWishInbox


def fill(inbox: PersistentWishInbox) -> None:
    inbox.dispatch_selected_request()
    assert inbox.receive("alice", ["a", "b", "c"]).outcome == "added"
    assert inbox.at_capacity


def test_scheduler_reopens_response_admission_for_each_epoch():
    inbox = PersistentWishInbox()
    assert inbox.dispatch_selected_request()
    assert inbox.allowed
    assert not inbox.is_ignored
    assert inbox.scheduled_requests == 1


def test_first_admissible_response_at_capacity_revokes_epoch():
    inbox = PersistentWishInbox()
    fill(inbox)
    inbox.dispatch_selected_request()
    assert inbox.receive("bob", ["d"]).outcome == "capacity-drop"
    assert not inbox.allowed
    assert inbox.num_results == 3


def test_repeated_scheduler_ticks_can_send_without_visible_progress():
    inbox = PersistentWishInbox()
    fill(inbox)
    before = inbox.num_results
    for index in range(12):
        inbox.dispatch_selected_request()
        assert inbox.receive(f"peer-{index}", [f"new-{index}"]).outcome == "capacity-drop"
    assert inbox.scheduled_requests == 13
    assert inbox.num_results == before
    assert inbox.cap_drops == 12


def test_current_search_again_at_capacity_is_request_waste():
    inbox = PersistentWishInbox()
    fill(inbox)
    inbox.current_search_again()
    assert inbox.receive("bob", ["new"]).outcome == "capacity-drop"
    assert inbox.manual_same_token_requests == 1
    assert inbox.num_results == 3


def test_candidate_removes_persistent_search_again_capability():
    inbox = PersistentWishInbox()
    assert not inbox.candidate_search_again_available()
    assert inbox.manual_same_token_requests == 0


def test_dialog_manual_search_is_independent_page_owned_request():
    inbox = PersistentWishInbox()
    page = inbox.search_for_item(token=200)
    page.rows.append(("alice", "a"))
    assert page.request_class == "SearchRequest"
    assert page.mode == "wishlist"
    assert inbox.token == 100
    assert inbox.rows == []
    assert inbox.ignored_users == set()


def test_mark_read_persists_sender_identity_not_file_identity():
    inbox = PersistentWishInbox()
    inbox.dispatch_selected_request()
    inbox.receive("alice", ["old-edition"])
    inbox.mark_read()
    assert inbox.ignored_users == {"alice"}


def test_seen_sender_new_file_is_suppressed_before_gui_comparison():
    inbox = PersistentWishInbox()
    inbox.dispatch_selected_request()
    inbox.receive("alice", ["old-edition"])
    inbox.mark_read()
    inbox.close_page()
    inbox.dispatch_selected_request()
    result = inbox.receive("alice", ["new-edition"])
    assert result.outcome == "core-ignored"
    assert inbox.rows == []


def test_reset_seen_results_is_a_distinct_destructive_operation():
    inbox = PersistentWishInbox()
    inbox.ignored_users.add("alice")
    inbox.reset_seen_results()
    assert inbox.ignored_users == set()


def test_close_preserves_seen_history_but_releases_batch_capacity():
    inbox = PersistentWishInbox()
    inbox.dispatch_selected_request()
    inbox.receive("alice", ["a", "b", "c"])
    inbox.mark_read()
    inbox.close_page()
    assert inbox.num_results == 0
    assert inbox.ignored_users == {"alice"}
    assert inbox.is_ignored


def test_next_scheduled_epoch_can_open_new_batch_for_unseen_sender():
    inbox = PersistentWishInbox()
    inbox.dispatch_selected_request()
    inbox.receive("alice", ["a"])
    inbox.mark_read()
    inbox.close_page()
    inbox.dispatch_selected_request()
    result = inbox.receive("bob", ["b"])
    assert result.outcome == "added"
    assert inbox.page_open
    assert inbox.rows == [("bob", "b")]


def test_dispatch_of_scheduler_selected_disabled_request_exposes_current_bug():
    inbox = PersistentWishInbox(auto_search=False)
    assert inbox.dispatch_selected_request()
    assert inbox.scheduled_requests == 1
    assert inbox.allowed
    assert not inbox.is_ignored


def test_closed_page_rejects_unscheduled_late_response():
    inbox = PersistentWishInbox()
    inbox.dispatch_selected_request()
    inbox.close_page()
    assert inbox.receive("alice", ["late"]).outcome == "parser-denied"


def test_page_user_dedup_discards_later_response_from_same_sender():
    inbox = PersistentWishInbox(max_results=10)
    inbox.dispatch_selected_request()
    assert inbox.receive("alice", ["a"]).outcome == "added"
    assert inbox.receive("alice", ["b"]).outcome == "page-user-dedup"
    assert inbox.rows == [("alice", "a")]
