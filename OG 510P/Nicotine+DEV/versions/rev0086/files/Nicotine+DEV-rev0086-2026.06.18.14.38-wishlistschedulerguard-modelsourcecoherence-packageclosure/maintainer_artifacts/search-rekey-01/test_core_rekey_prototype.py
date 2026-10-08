from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pynicotine.config import config
from pynicotine.events import events
from pynicotine.search import Search

PATCH_ROOT = Path(os.environ["NICOTINE_PATCH_SOURCE_ROOT"])


def new_searcher(tmp_path: Path) -> Search:
    config.set_data_folder(str(tmp_path))
    return Search()


def test_regular_core_rekey_preserves_request_identity_and_orders_barriers(tmp_path):
    searcher = new_searcher(tmp_path)
    old_token = searcher.token
    request = searcher._add_search(old_token, "needle", "global")
    calls = []

    def callback(old, new):
        calls.append(("event", old, new, tuple(searcher.searches)))

    events.connect("rekey-search", callback)
    try:
        with patch.object(Search, "remove_allowed_token", side_effect=lambda token: calls.append(("remove", token))), \
             patch.object(Search, "send_search_request", side_effect=lambda token: calls.append(("send", token))):
            new_token = searcher.repeat_search(old_token)
    finally:
        events.disconnect("rekey-search", callback)

    assert request is searcher.searches[new_token]
    assert request.token == new_token
    assert old_token not in searcher.searches
    assert calls == [
        ("remove", old_token),
        ("event", old_token, new_token, (new_token,)),
        ("send", new_token),
    ]


def test_rekey_retires_old_self_search_suppression_token(tmp_path):
    searcher = new_searcher(tmp_path)
    old_token = searcher.token
    searcher._add_search(old_token, "needle", "user", users=("self",))
    searcher._own_tokens.add(old_token)
    with patch.object(Search, "remove_allowed_token"), patch.object(Search, "send_search_request"):
        new_token = searcher.repeat_search(old_token)
    assert old_token not in searcher._own_tokens
    assert new_token in searcher.searches



def test_already_parsed_old_epoch_response_is_rejected_by_core_lookup(tmp_path):
    searcher = new_searcher(tmp_path)
    old_token = searcher.token
    searcher._add_search(old_token, "needle", "global")
    with patch.object(Search, "remove_allowed_token"), patch.object(Search, "send_search_request"):
        new_token = searcher.repeat_search(old_token)

    stale = SimpleNamespace(token=old_token, list=[], username="alice", addr=("127.0.0.1", 1))
    searcher._file_search_response(stale)
    assert stale.token is None
    assert new_token in searcher.searches

def test_wishlist_is_deliberately_not_rekeyed(tmp_path):
    searcher = new_searcher(tmp_path)
    token = searcher.token
    request = searcher._add_wish_search(
        token, "wish", auto_search=False, custom_filters=["flac"], ignored_users={"alice"}
    )
    request.is_ignored = False
    with patch.object(Search, "remove_allowed_token") as remove, patch.object(Search, "send_search_request") as send:
        result = searcher.repeat_search(token)
    assert result is None
    assert searcher.searches[token] is request
    assert searcher.wishlist["wish"] is request
    assert request.ignored_users == {"alice"}
    remove.assert_not_called()
    send.assert_not_called()


def test_unknown_token_is_nondestructive(tmp_path):
    searcher = new_searcher(tmp_path)
    before = searcher.token
    with patch.object(Search, "remove_allowed_token") as remove, patch.object(Search, "send_search_request") as send:
        assert searcher.repeat_search(before + 1000) is None
    assert searcher.token == before
    remove.assert_not_called()
    send.assert_not_called()


def test_prototype_adds_no_notification_alias_state(tmp_path):
    searcher = new_searcher(tmp_path)
    assert "search_token_aliases" not in Search.__slots__
    source = (PATCH_ROOT / "pynicotine/search.py").read_text(encoding="utf-8")
    repeat = source[source.index("    def repeat_search"):source.index("    def send_search_request")]
    assert "alias" not in repeat
    assert "ignored_users.clear" not in repeat
