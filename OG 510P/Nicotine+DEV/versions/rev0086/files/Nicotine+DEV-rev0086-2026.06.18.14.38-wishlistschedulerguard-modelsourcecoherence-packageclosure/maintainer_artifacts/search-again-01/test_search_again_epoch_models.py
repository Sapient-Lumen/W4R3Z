"""Pure models for the unresolved refresh/late-response policy choices."""
from __future__ import annotations

from search_again_harness import EpochModel


def test_current_same_token_keeps_first_response_from_each_user():
    model = EpochModel(current_token=10)
    model.allow(10)

    assert model.receive(token=10, user="alice", payload="old") == "accepted"
    assert model.receive(token=10, user="alice", payload="new") == "ignored-existing-user"
    assert model.visible_users == {"alice": "old"}


def test_clear_with_same_token_cannot_distinguish_late_old_response():
    model = EpochModel(current_token=10)
    model.allow(10)
    assert model.receive(token=10, user="alice", payload="old") == "accepted"

    model.clear_results()
    assert model.receive(token=10, user="alice", payload="late-old") == "accepted"
    assert model.receive(token=10, user="alice", payload="new") == "ignored-existing-user"
    assert model.visible_users == {"alice": "late-old"}


def test_new_token_clear_and_retire_old_is_a_true_replace_epoch():
    model = EpochModel(current_token=10)
    model.allow(10)
    assert model.receive(token=10, user="alice", payload="old") == "accepted"

    model.retire(10)
    model.current_token = 11
    model.allow(11)
    model.clear_results()

    assert model.receive(token=10, user="alice", payload="late-old") == "rejected-token"
    assert model.receive(token=11, user="alice", payload="new") == "accepted"
    assert model.visible_users == {"alice": "new"}


def test_new_token_without_clear_is_union_not_refresh():
    model = EpochModel(current_token=10)
    model.allow(10)
    assert model.receive(token=10, user="alice", payload="old") == "accepted"

    model.retire(10)
    model.current_token = 11
    model.allow(11)

    assert model.receive(token=11, user="alice", payload="new") == "ignored-existing-user"
    assert model.receive(token=11, user="bob", payload="new-bob") == "accepted"
    assert model.visible_users == {"alice": "old", "bob": "new-bob"}
