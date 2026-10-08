"""Late-response and queue-boundary race witnesses."""
from __future__ import annotations

from search_epoch_model import SearchEpochSystem


def test_result_parsed_before_refresh_is_rejected_by_retired_core_route():
    system = SearchEpochSystem(next_token=20)
    system.open_search("search:beta", token=20)
    assert system.receive_at_network(token=20, user="alice", payload="late-old") == "queued-main"

    outcome = system.refresh("search:beta")
    assert outcome.new_token == 21
    assert system.deliver_next_main_event() == "rejected-core-route"
    assert system.pages["search:beta"].results == {}


def test_result_parsed_during_network_control_lag_is_rejected_by_core():
    system = SearchEpochSystem(next_token=30)
    system.open_search("search:gamma", token=30)
    outcome = system.refresh("search:gamma")

    # The network thread has not processed the remove/add/send batch yet, so
    # old token 30 is still admitted there. The main-thread route is already gone.
    assert system.network.allowed_tokens == {30}
    assert system.receive_at_network(token=30, user="alice", payload="late-old") == "queued-main"
    assert system.deliver_next_main_event() == "rejected-core-route"

    system.network.process_next_batch()
    assert system.receive_at_network(token=30, user="alice", payload="later-old") == "rejected-network"
    assert system.receive_at_network(token=outcome.new_token, user="alice", payload="fresh") == "queued-main"
    assert system.deliver_next_main_event() == "accepted"
    assert system.pages["search:gamma"].results == {"alice": "fresh"}


def test_stable_notification_target_survives_wire_token_rotation():
    system = SearchEpochSystem(next_token=40)
    system.open_search("logical:stable", token=40)
    assert system.notify("logical:stable", "first result") == "logical:stable"

    outcome = system.refresh("logical:stable")
    assert outcome.new_token == 41
    page = system.activate_notification("logical:stable")
    assert page is not None
    assert page.logical_id == "logical:stable"
    assert page.current_token == 41


def test_token_keyed_notification_can_point_at_no_page_after_rotation():
    pages_by_token = {50: object()}
    notification_target = 50
    pages_by_token[51] = pages_by_token.pop(50)

    assert notification_target not in pages_by_token
