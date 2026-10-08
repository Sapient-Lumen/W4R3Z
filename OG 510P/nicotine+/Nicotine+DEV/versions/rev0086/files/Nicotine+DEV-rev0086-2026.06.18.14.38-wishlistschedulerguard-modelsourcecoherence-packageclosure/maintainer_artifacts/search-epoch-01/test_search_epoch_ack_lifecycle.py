"""Close/cancel, buddy audience, and rapid-repeat policy checks."""
from __future__ import annotations

import pytest

from search_epoch_ack_model import (
    RefreshPending,
    SearchEpochSystem,
    click_storm_fanout,
)


def test_second_refresh_is_rejected_while_first_is_pending():
    system = SearchEpochSystem(next_token=110)
    system.open_search("search:rapid", token=110)
    system.begin_refresh("search:rapid")

    with pytest.raises(RefreshPending, match="search:rapid"):
        system.begin_refresh("search:rapid")

    assert len(system.network.commands) == 1


def test_rapid_repeat_policies_bound_fanout_differently():
    assert click_storm_fanout(12, 40, policy="allow") == (12, 480)
    assert click_storm_fanout(12, 40, policy="reject-while-pending") == (1, 40)
    assert click_storm_fanout(12, 40, policy="coalesce-one-trailing") == (2, 80)


def test_close_before_network_apply_never_resurrects_page():
    system = SearchEpochSystem(next_token=120)
    system.open_search("search:close", token=120)
    outcome = system.begin_refresh("search:close")
    system.close_search("search:close")

    # FIFO means the batch is applied before the cancellation queued by close.
    assert system.network.process_next_command(system.main_events) == "applied"
    assert system.network.process_next_command(system.main_events) == "cancelled"
    assert outcome.new_token not in system.network.allowed_tokens
    assert list(system.network.owned_requests) == []

    assert system.deliver_next_main_event() == "ignored-stale-ack"
    assert "search:close" not in system.searches
    assert "search:close" not in system.pages
    assert "search:close" not in system.token_routes.values()


def test_close_after_apply_before_ack_delivery_remains_closed():
    system = SearchEpochSystem(next_token=130)
    system.open_search("search:close", token=130)
    outcome = system.begin_refresh("search:close")
    system.network.process_next_command(system.main_events)
    system.close_search("search:close")

    assert system.network.process_next_command(system.main_events) == "cancelled"
    assert system.deliver_next_main_event() == "ignored-stale-ack"
    assert outcome.new_token not in system.network.allowed_tokens
    assert "search:close" not in system.searches


def test_result_for_closed_page_is_rejected_at_core_route():
    system = SearchEpochSystem(next_token=140)
    system.open_search("search:close", token=140)
    outcome = system.begin_refresh("search:close")
    system.network.process_next_command(system.main_events)
    system.close_search("search:close")
    system.network.receive_result(
        system.main_events,
        token=outcome.new_token,
        user="alice",
        payload="late",
    )

    assert system.deliver_next_main_event() == "ignored-stale-ack"
    assert system.deliver_next_main_event() == "rejected-core-route"


def test_buddy_live_audience_is_bound_to_pending_epoch():
    system = SearchEpochSystem(next_token=150)
    system.open_search(
        "buddy:live",
        token=150,
        mode="buddies",
        recipients=("alice", "bob"),
    )
    outcome = system.begin_refresh(
        "buddy:live",
        live_buddies=("bob", "carol"),
        buddy_policy="live-at-epoch",
    )
    assert outcome.recipients == ("bob", "carol")


def test_buddy_original_audience_is_a_distinct_policy():
    system = SearchEpochSystem(next_token=160)
    system.open_search(
        "buddy:snapshot",
        token=160,
        mode="buddies",
        recipients=("alice", "bob"),
    )
    outcome = system.begin_refresh(
        "buddy:snapshot",
        live_buddies=("bob", "carol"),
        buddy_policy="original-request",
    )
    assert outcome.recipients == ("alice", "bob")


def test_empty_live_buddy_epoch_is_rejected_without_clearing_old_rows():
    system = SearchEpochSystem(next_token=170)
    system.open_search(
        "buddy:empty",
        token=170,
        mode="buddies",
        recipients=("alice",),
    )
    system.pages["buddy:empty"].results["alice"] = "old"
    system.begin_refresh(
        "buddy:empty",
        live_buddies=(),
        buddy_policy="live-at-epoch",
    )

    assert system.network.process_next_command(system.main_events) == "rejected"
    assert system.deliver_next_main_event() == "aborted-pending"
    assert system.pages["buddy:empty"].results == {"alice": "old"}
    assert system.searches["buddy:empty"].current_token == 170


def test_close_without_pending_queues_network_retirement_instead_of_cross_thread_mutation():
    system = SearchEpochSystem(next_token=180)
    system.open_search("search:plain-close", token=180)

    system.close_search("search:plain-close")
    # Main-thread closure removes core routes immediately, but parser admission
    # remains network-owned until the queued cancellation is processed.
    assert 180 in system.network.allowed_tokens
    assert len(system.network.commands) == 1
    assert system.network.process_next_command(system.main_events) == "cancelled"
    assert 180 not in system.network.allowed_tokens
    assert "search:plain-close" not in system.pages
