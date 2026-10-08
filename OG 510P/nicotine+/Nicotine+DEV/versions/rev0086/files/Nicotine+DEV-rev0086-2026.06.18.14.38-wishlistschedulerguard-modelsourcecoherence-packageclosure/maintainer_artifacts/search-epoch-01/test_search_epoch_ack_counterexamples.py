"""Counterexamples to acknowledgement-before-ownership and weak ack matching."""
from __future__ import annotations

from search_epoch_ack_model import EpochApplied, SearchEpochSystem


def make_system(token: int = 70) -> SearchEpochSystem:
    system = SearchEpochSystem(next_token=token)
    system.open_search("search:counter", token=token, term="counter")
    system.pages["search:counter"].results["alice"] = "old"
    return system


def test_ack_before_request_ownership_can_commit_a_request_that_never_exists():
    system = make_system()
    outcome = system.begin_refresh("search:counter")

    result = system.network.process_next_command_ack_first(
        system.main_events,
        disconnect_before_ownership=True,
    )
    assert result == "acknowledged-then-lost"
    assert list(system.network.owned_requests) == []
    assert system.network.serialized_requests == []

    # Main sees the ack before the subsequently queued disconnect event.
    assert system.deliver_next_main_event() == "committed"
    assert system.pages["search:counter"].results == {}
    assert system.searches["search:counter"].current_token == outcome.new_token
    assert system.deliver_next_main_event() == "disconnect-aborted:0"


def test_mismatched_ack_cannot_commit_pending_epoch():
    system = make_system(80)
    outcome = system.begin_refresh("search:counter")
    system.main_events.append(EpochApplied(
        outcome.transaction_id,
        outcome.logical_id,
        outcome.generation,
        outcome.old_token,
        outcome.new_token + 1,
    ))

    assert system.deliver_next_main_event() == "ignored-mismatched-ack"
    assert system.pages["search:counter"].results == {"alice": "old"}
    assert "search:counter" in system.pending


def test_duplicate_ack_is_idempotently_ignored():
    system = make_system(90)
    outcome = system.begin_refresh("search:counter")
    system.network.process_next_command(system.main_events)
    applied = system.main_events[0]

    assert system.deliver_next_main_event() == "committed"
    system.main_events.append(applied)
    assert system.deliver_next_main_event() == "ignored-duplicate-ack"
    assert system.searches["search:counter"].current_token == outcome.new_token


def test_stale_ack_after_pending_abort_does_not_clear_old_rows():
    system = make_system(100)
    system.begin_refresh("search:counter")
    system.network.process_next_command(system.main_events)
    applied = system.main_events.popleft()
    system._abort_pending("search:counter", "test-abort")
    system.main_events.append(applied)

    assert system.deliver_next_main_event() == "ignored-stale-ack"
    assert system.pages["search:counter"].results == {"alice": "old"}


def test_partial_buddy_fanout_ack_can_commit_after_only_one_request_is_owned():
    system = SearchEpochSystem(next_token=90)
    system.open_search(
        "buddy:partial",
        token=90,
        mode="buddies",
        recipients=("alice", "bob", "carol"),
    )
    outcome = system.begin_refresh(
        "buddy:partial",
        live_buddies=("alice", "bob", "carol"),
    )
    batch = system.pending["buddy:partial"].batch
    assert [request.destination for request in batch.requests] == [
        "alice",
        "bob",
        "carol",
    ]

    assert system.network.process_next_command_partial_ownership(
        system.main_events,
        owned_count=1,
    ) == "partially-applied"
    assert system.deliver_next_main_event() == "committed"
    assert [request.destination for request in system.network.owned_requests] == [
        "alice"
    ]
    assert system.pages["buddy:partial"].current_token == outcome.new_token

    # The visible page has committed, but two intended peers were never handed
    # to network-owned state. A correct ack must follow ownership of all three.
    assert {"bob", "carol"}.isdisjoint(
        request.destination for request in system.network.owned_requests
    )
