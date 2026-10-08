"""Page-close and audience-epoch policy checks."""
from __future__ import annotations

import pytest

from search_epoch_model import SearchClosed, SearchEpochSystem


CHECKPOINTS = (
    "allocated",
    "new-route-installed",
    "current-token-switched",
    "old-route-retired",
    "results-cleared",
    "before-enqueue",
)


@pytest.mark.parametrize("checkpoint", CHECKPOINTS)
def test_close_before_enqueue_never_resurrects_or_sends(checkpoint):
    system = SearchEpochSystem(next_token=60)
    system.open_search("search:close", token=60)

    with pytest.raises(SearchClosed, match=checkpoint):
        system.refresh("search:close", close_at=checkpoint)

    assert "search:close" not in system.searches
    assert "search:close" not in system.pages
    assert "search:close" not in system.token_routes.values()
    assert list(system.network.batches) == []
    assert system.network.allowed_tokens == set()
    assert system.network.sent_requests == []


def test_buddy_refresh_can_bind_live_epoch_audience_explicitly():
    system = SearchEpochSystem(next_token=70)
    system.open_search(
        "buddy:live",
        token=70,
        mode="buddies",
        recipients=("alice", "bob"),
    )
    outcome = system.refresh(
        "buddy:live",
        live_buddies=("bob", "carol"),
        buddy_policy="live-at-epoch",
    )
    assert outcome.recipients == ("bob", "carol")


def test_buddy_original_audience_is_a_distinct_product_policy():
    system = SearchEpochSystem(next_token=80)
    system.open_search(
        "buddy:snapshot",
        token=80,
        mode="buddies",
        recipients=("alice", "bob"),
    )
    outcome = system.refresh(
        "buddy:snapshot",
        live_buddies=("bob", "carol"),
        buddy_policy="original-request",
    )
    assert outcome.recipients == ("alice", "bob")


def test_accepted_enqueue_is_not_durable_across_disconnect_clear():
    system = SearchEpochSystem(next_token=85)
    system.open_search("search:disconnect", token=85)
    system.pages["search:disconnect"].results["alice"] = "old"

    outcome = system.refresh("search:disconnect")
    assert outcome.new_token == 86
    assert len(system.network.batches) == 1

    # Upstream clears both the outgoing queue and response admissions during
    # server disconnect. Queue acceptance therefore is not a processing ack.
    system.network.disconnect_and_clear()

    assert list(system.network.batches) == []
    assert system.network.allowed_tokens == set()
    assert system.network.sent_requests == []
    assert system.searches["search:disconnect"].current_token == 86
    assert system.pages["search:disconnect"].results == {}
    assert system.receive_at_network(token=86, user="alice", payload="fresh") == "rejected-network"
