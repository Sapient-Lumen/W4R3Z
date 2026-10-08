"""Behavior contract for the rev0084 research prototype."""
from __future__ import annotations

import pytest

from search_notification_identity_model import NotificationStore
from search_notification_identity_model import SearchKind
from search_notification_identity_model import SearchSession
from search_notification_identity_model import WindowsBalloonStore


@pytest.mark.parametrize("kind", [SearchKind.ORDINARY, SearchKind.MANUAL_WISHLIST])
def test_refreshable_pages_rotate_wire_token_but_keep_page_identity(kind):
    session = SearchSession()
    page = session.open_page(kind, rows=["old"])
    old_token = page.token
    page_id = page.page_id

    assert session.repeat(page) != old_token
    assert page.page_id == page_id
    assert old_token not in session.by_token
    assert session.by_page_id[page_id] is page
    assert page.rows == []


def test_persistent_wishlist_retries_same_token_and_retains_rows():
    session = SearchSession()
    page = session.open_page(SearchKind.PERSISTENT_WISHLIST, rows=["old"])
    old_token = page.token

    assert session.repeat(page) == old_token
    assert page.token == old_token
    assert page.rows == ["old"]


def test_manual_wishlist_notification_survives_wire_rekey():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)
    target = page.page_id
    session.notify(page)

    session.repeat(page)

    assert session.activate(target) is page
    assert target != str(page.token)


def test_old_wire_token_is_not_an_activation_alias():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)
    old_token = page.token
    session.repeat(page)

    assert old_token not in session.by_token
    assert session.activate(str(old_token)) is None


def test_repeated_notifications_replace_one_gio_notification():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)

    first = session.notify(page)
    second = session.notify(page)

    assert first == second
    assert session.notifications.visible == {first: page.page_id}


def test_two_pages_have_independent_notification_ids():
    session = SearchSession()
    first = session.open_page(SearchKind.MANUAL_WISHLIST)
    second = session.open_page(SearchKind.MANUAL_WISHLIST)

    assert session.notify(first) != session.notify(second)
    assert len(session.notifications.visible) == 2


def test_close_withdraws_notification_and_stale_action_noops():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)
    target = page.page_id
    notification_id = session.notify(page)

    session.close(page)

    assert notification_id not in session.notifications.visible
    assert notification_id in session.notifications.withdrawn
    assert session.activate(target) is None


def test_closed_page_identity_is_not_reused():
    values = iter(("page-a", "page-b"))
    session = SearchSession(page_id_factory=lambda: next(values))
    first = session.open_page(SearchKind.MANUAL_WISHLIST)
    session.close(first)
    second = session.open_page(SearchKind.MANUAL_WISHLIST)

    assert first.page_id != second.page_id
    assert session.activate(first.page_id) is None
    assert session.activate(second.page_id) is second


def test_factory_rejects_page_id_reuse():
    session = SearchSession(page_id_factory=lambda: "reused")
    session.open_page(SearchKind.ORDINARY)
    with pytest.raises(ValueError, match="must not be reused"):
        session.open_page(SearchKind.ORDINARY)


def test_rapid_repeat_keeps_one_logical_mapping_and_no_token_aliases():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST, rows=["old"])
    page_id = page.page_id
    old_tokens = []

    for _ in range(64):
        old_tokens.append(page.token)
        session.repeat(page)

    assert session.by_page_id == {page_id: page}
    assert session.by_token == {page.token: page}
    assert not set(old_tokens) & set(session.by_token)
    assert len(session.sent_tokens) == 64


def test_notification_target_stays_constant_across_rapid_repeat():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)
    target = page.page_id

    for _ in range(32):
        session.notify(page)
        session.repeat(page)

    assert session.activate(target) is page
    assert list(session.notifications.visible.values()) == [target]


def test_offline_repeat_is_nondestructive():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST, rows=["old"])
    before = (page.token, list(page.rows), dict(session.by_token))

    assert session.repeat(page, online=False) is None
    assert (page.token, page.rows, session.by_token) == before
    assert session.sent_tokens == []


def test_seen_users_reset_for_manual_wishlist_refresh():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)
    page.seen_users.add("alice")

    session.repeat(page)

    assert page.seen_users == set()


def test_seen_users_persist_for_scheduled_wishlist_retry():
    session = SearchSession()
    page = session.open_page(SearchKind.PERSISTENT_WISHLIST)
    page.seen_users.add("alice")

    session.repeat(page)

    assert page.seen_users == {"alice"}


def test_shutdown_withdraws_every_addressable_notification():
    session = SearchSession()
    pages = [session.open_page(SearchKind.MANUAL_WISHLIST) for _ in range(3)]
    ids = {session.notify(page) for page in pages}

    session.shutdown()

    assert session.notifications.visible == {}
    assert ids <= set(session.notifications.withdrawn)
    assert session.by_page_id == {}


def test_gio_notification_id_is_stable_and_namespaced():
    assert NotificationStore.notification_id("abc") == "search-abc"


def test_win32_withdraw_matches_current_action_and_target():
    store = WindowsBalloonStore()
    store.show("app.search-notification-activated", "page-a")

    assert store.withdraw("app.search-notification-activated", "page-a") is True
    assert store.current_action is None
    assert store.withdrawals == 1


def test_win32_close_of_older_page_does_not_dismiss_newer_balloon():
    store = WindowsBalloonStore()
    store.show("app.search-notification-activated", "page-b")

    assert store.withdraw("app.search-notification-activated", "page-a") is False
    assert store.current_action == ("search-notification-activated", "page-b")
    assert store.withdrawals == 0


def test_win32_wrong_action_does_not_dismiss_search_balloon():
    store = WindowsBalloonStore()
    store.show("app.search-notification-activated", "page-a")

    assert store.withdraw("app.private-chat-notification-activated", "page-a") is False
    assert store.current_action is not None


def test_notification_emission_from_closed_page_is_rejected():
    session = SearchSession()
    page = session.open_page(SearchKind.MANUAL_WISHLIST)
    session.close(page)

    with pytest.raises(ValueError, match="closed pages"):
        session.notify(page)


def test_cross_process_stale_uuid_does_not_open_new_page():
    first = SearchSession(page_id_factory=lambda: "session-one-uuid")
    old_page = first.open_page(SearchKind.MANUAL_WISHLIST)
    stale_target = old_page.page_id

    second = SearchSession(page_id_factory=lambda: "session-two-uuid")
    new_page = second.open_page(SearchKind.MANUAL_WISHLIST)

    assert second.activate(stale_target) is None
    assert second.activate(new_page.page_id) is new_page


def test_persistent_wishlist_notification_target_remains_stable_on_retry():
    session = SearchSession()
    page = session.open_page(SearchKind.PERSISTENT_WISHLIST)
    target = page.page_id
    session.notify(page)

    session.repeat(page)

    assert page.page_id == target
    assert session.activate(target) is page


def test_close_is_idempotent():
    session = SearchSession()
    page = session.open_page(SearchKind.ORDINARY)
    session.notify(page)

    session.close(page)
    session.close(page)

    assert session.notifications.withdrawn.count(f"search-{page.page_id}") == 1


def test_mapping_size_is_bounded_by_open_pages_not_rekeys():
    session = SearchSession()
    pages = [session.open_page(SearchKind.MANUAL_WISHLIST) for _ in range(5)]
    for page in pages:
        for _ in range(20):
            session.repeat(page)

    assert len(session.by_page_id) == 5
    assert len(session.by_token) == 5
