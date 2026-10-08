"""Transactional refresh contract and rollback checks."""
from __future__ import annotations

import pytest

from search_epoch_model import RefreshError, SearchEpochSystem


CHECKPOINTS = (
    "allocated",
    "new-route-installed",
    "current-token-switched",
    "old-route-retired",
    "results-cleared",
    "before-enqueue",
)


def populated_system() -> SearchEpochSystem:
    system = SearchEpochSystem(next_token=10)
    system.open_search("search:alpha", token=10, term="alpha")
    assert system.receive_at_network(token=10, user="alice", payload="old") == "queued-main"
    assert system.deliver_next_main_event() == "accepted"
    return system


@pytest.mark.parametrize("checkpoint", CHECKPOINTS)
def test_preenqueue_failure_restores_old_epoch(checkpoint):
    system = populated_system()

    with pytest.raises(RefreshError, match=checkpoint):
        system.refresh("search:alpha", fail_at=checkpoint)

    assert system.searches["search:alpha"].current_token == 10
    assert system.pages["search:alpha"].current_token == 10
    assert system.pages["search:alpha"].results == {"alice": "old"}
    assert system.token_routes == {10: "search:alpha"}
    assert list(system.network.batches) == []
    assert system.network.sent_requests == []


def test_rejected_network_enqueue_rolls_back_without_request():
    system = populated_system()
    system.network.queue_enabled = False

    with pytest.raises(RefreshError, match="network-enqueue-rejected"):
        system.refresh("search:alpha")

    assert system.searches["search:alpha"].current_token == 10
    assert system.pages["search:alpha"].results == {"alice": "old"}
    assert system.token_routes == {10: "search:alpha"}
    assert list(system.network.batches) == []


def test_success_enqueues_one_ordered_batch_and_commits_clear():
    system = populated_system()
    outcome = system.refresh("search:alpha")

    assert outcome.old_token == 10
    assert outcome.new_token == 11
    assert system.searches["search:alpha"].current_token == 11
    assert system.pages["search:alpha"].current_token == 11
    assert system.pages["search:alpha"].results == {}
    assert system.token_routes == {11: "search:alpha"}
    assert len(system.network.batches) == 1
    assert system.network.sent_requests == []

    system.network.process_next_batch()
    assert system.network.operation_log == [("remove", 10), ("add", 11), ("send", 11)]
    assert system.network.allowed_tokens == {11}
    assert [request.token for request in system.network.sent_requests] == [11]
