"""Disconnect placement and acknowledgement durability boundaries."""
from __future__ import annotations

from search_epoch_ack_model import RefreshRejected, SearchEpochSystem


def make_system(token: int = 20) -> SearchEpochSystem:
    system = SearchEpochSystem(next_token=token)
    system.open_search("search:disconnect", token=token, term="delta")
    system.pages["search:disconnect"].results["alice"] = "old"
    return system


def test_disconnect_before_enqueue_is_a_synchronous_rejection():
    system = make_system()
    system.network.queue_enabled = False

    try:
        system.begin_refresh("search:disconnect")
    except RefreshRejected:
        pass
    else:  # pragma: no cover - explicit witness
        raise AssertionError("refresh unexpectedly entered disabled queue")

    assert system.pages["search:disconnect"].results == {"alice": "old"}


def test_disconnect_after_enqueue_before_apply_aborts_pending_on_event():
    system = make_system()
    system.begin_refresh("search:disconnect")

    system.network.disconnect(system.main_events)
    assert list(system.network.commands) == []
    assert system.deliver_next_main_event() == "disconnect-aborted:1"
    assert system.pages["search:disconnect"].results == {"alice": "old"}
    assert system.searches["search:disconnect"].current_token == 20
    assert system.token_routes == {20: "search:disconnect"}


def test_apply_then_disconnect_queues_ack_before_disconnect_event():
    system = make_system(30)
    outcome = system.begin_refresh("search:disconnect")
    system.network.process_next_command(system.main_events)
    system.network.disconnect(system.main_events)

    assert type(system.main_events[0]).__name__ == "EpochApplied"
    assert type(system.main_events[1]).__name__ == "ServerDisconnected"
    assert system.deliver_next_main_event() == "committed"
    assert system.pages["search:disconnect"].results == {}
    assert system.deliver_next_main_event() == "disconnect-aborted:0"
    assert system.searches["search:disconnect"].current_token == outcome.new_token


def test_ownership_ack_is_not_socket_serialization_or_remote_delivery():
    system = make_system(40)
    system.begin_refresh("search:disconnect")
    system.network.process_next_command(system.main_events)

    assert len(system.network.owned_requests) == 1
    assert system.network.serialized_requests == []
    assert system.deliver_next_main_event() == "committed"

    # A disconnect after the ack but before modeled socket serialization loses
    # the locally owned request.  This is why the ack is a commit-policy choice,
    # not proof of remote delivery.
    system.network.disconnect(system.main_events)
    assert list(system.network.owned_requests) == []
    assert system.network.serialized_requests == []
    assert system.pages["search:disconnect"].results == {}


def test_serialization_can_follow_ack_without_result_overtaking_it():
    system = make_system(50)
    outcome = system.begin_refresh("search:disconnect")
    system.network.process_next_command(system.main_events)
    request = system.network.serialize_next_request()

    assert request is not None
    assert request.token == outcome.new_token
    assert system.network.receive_result(
        system.main_events,
        token=outcome.new_token,
        user="bob",
        payload="fresh",
    ) == "queued-main"
    assert system.deliver_next_main_event() == "committed"
    assert system.deliver_next_main_event() == "accepted"


def test_stale_generation_batch_is_rejected_after_reconnect():
    system = make_system(60)
    system.begin_refresh("search:disconnect")
    system.network.disconnect(system.main_events)
    system.network.reconnect()

    # The queued batch was cleared; the disconnect event aborts its main state.
    assert system.deliver_next_main_event() == "disconnect-aborted:1"
    assert system.network.generation == 2
    assert system.pages["search:disconnect"].results == {"alice": "old"}
