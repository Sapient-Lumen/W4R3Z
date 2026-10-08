"""Acknowledgement-gated refresh state transitions."""
from __future__ import annotations

import pytest

from search_epoch_ack_model import (
    RefreshRejected,
    ResultEvent,
    SearchEpochSystem,
)


def populated_system() -> SearchEpochSystem:
    system = SearchEpochSystem(next_token=10)
    system.open_search("search:alpha", token=10, term="alpha")
    system.pages["search:alpha"].results["alice"] = "old"
    return system


def test_pending_epoch_preserves_visible_state_and_old_identity():
    system = populated_system()
    outcome = system.begin_refresh("search:alpha")

    assert outcome.old_token == 10
    assert outcome.new_token == 11
    assert system.searches["search:alpha"].current_token == 10
    assert system.pages["search:alpha"].current_token == 10
    assert system.pages["search:alpha"].results == {"alice": "old"}
    assert system.token_routes == {10: "search:alpha", 11: "search:alpha"}


def test_disabled_queue_rejects_without_mutating_visible_state():
    system = populated_system()
    system.network.queue_enabled = False

    with pytest.raises(RefreshRejected, match="network-enqueue-rejected"):
        system.begin_refresh("search:alpha")

    assert system.searches["search:alpha"].current_token == 10
    assert system.pages["search:alpha"].results == {"alice": "old"}
    assert system.token_routes == {10: "search:alpha"}
    assert system.pending == {}


def test_network_preflight_rejection_aborts_pending_without_clear():
    system = populated_system()
    system.network.authenticated = False
    system.begin_refresh("search:alpha")

    assert system.network.process_next_command(system.main_events) == "rejected"
    assert system.deliver_next_main_event() == "aborted-pending"
    assert system.pages["search:alpha"].results == {"alice": "old"}
    assert system.searches["search:alpha"].current_token == 10
    assert system.token_routes == {10: "search:alpha"}


def test_success_owns_request_before_ack_and_commits_on_ack():
    system = populated_system()
    outcome = system.begin_refresh("search:alpha")

    assert system.network.process_next_command(system.main_events) == "applied"
    assert system.network.operation_log == [
        ("remove", 10),
        ("add", 11),
        ("own", 11),
        ("ack", 11),
    ]
    assert [request.token for request in system.network.owned_requests] == [11]
    assert system.pages["search:alpha"].results == {"alice": "old"}

    assert system.deliver_next_main_event() == "committed"
    assert system.searches["search:alpha"].current_token == outcome.new_token
    assert system.pages["search:alpha"].current_token == outcome.new_token
    assert system.pages["search:alpha"].results == {}
    assert system.token_routes == {11: "search:alpha"}


def test_old_result_queued_before_ack_mutates_old_view_then_is_cleared():
    system = populated_system()
    system.begin_refresh("search:alpha")

    assert system.network.receive_result(
        system.main_events,
        token=10,
        user="bob",
        payload="late-old",
    ) == "queued-main"
    assert system.network.process_next_command(system.main_events) == "applied"

    assert system.deliver_next_main_event() == "accepted"
    assert system.pages["search:alpha"].results == {
        "alice": "old",
        "bob": "late-old",
    }
    assert system.deliver_next_main_event() == "committed"
    assert system.pages["search:alpha"].results == {}


def test_new_result_follows_ack_and_is_accepted_after_commit():
    system = populated_system()
    outcome = system.begin_refresh("search:alpha")
    system.network.process_next_command(system.main_events)

    assert system.network.receive_result(
        system.main_events,
        token=outcome.new_token,
        user="carol",
        payload="fresh",
    ) == "queued-main"
    assert system.deliver_next_main_event() == "committed"
    assert system.deliver_next_main_event() == "accepted"
    assert system.pages["search:alpha"].results == {"carol": "fresh"}


def test_result_before_matching_ack_fails_closed():
    system = populated_system()
    outcome = system.begin_refresh("search:alpha")
    system.main_events.appendleft(
        # Deliberate contract violation: no correct network path should do this.
        ResultEvent(
            outcome.generation,
            outcome.new_token,
            "mallory",
            "too-early",
        )
    )

    assert system.deliver_next_main_event() == "rejected-result-before-ack"
    assert system.pages["search:alpha"].results == {"alice": "old"}


def test_one_unserializable_fanout_member_rejects_whole_epoch_before_mutation():
    system = SearchEpochSystem(next_token=20)
    system.open_search(
        "buddy:packing",
        token=20,
        mode="buddies",
        recipients=("alice", "bob", "carol"),
    )
    system.pages["buddy:packing"].results["alice"] = "old"
    system.network.pack_failures.add("bob")
    outcome = system.begin_refresh(
        "buddy:packing",
        live_buddies=("alice", "bob", "carol"),
    )

    assert system.network.process_next_command(system.main_events) == "rejected"
    assert system.deliver_next_main_event() == "aborted-pending"
    assert system.network.allowed_tokens == {20}
    assert list(system.network.owned_requests) == []
    assert system.pages["buddy:packing"].results == {"alice": "old"}
    assert system.searches["buddy:packing"].current_token == 20
    assert outcome.new_token not in system.token_routes
