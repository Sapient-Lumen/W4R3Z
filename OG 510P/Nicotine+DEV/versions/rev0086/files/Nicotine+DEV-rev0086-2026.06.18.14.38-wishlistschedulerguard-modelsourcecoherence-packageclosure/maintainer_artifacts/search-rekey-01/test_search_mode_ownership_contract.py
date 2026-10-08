from __future__ import annotations

import ast
import os
from pathlib import Path
from unittest.mock import patch

from pynicotine.config import config
from pynicotine.events import events
from pynicotine.search import Search
from pynicotine.search import SearchRequest
from pynicotine.search import WishSearchRequest

from search_mode_ownership_model import SearchAgainOwnershipModel

BASELINE = Path(os.environ["NICOTINE_SOURCE_ROOT"])
PATCHED = Path(os.environ["NICOTINE_PATCH_SOURCE_ROOT"])


def method_source(path: Path, class_name: str, method_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                segment = ast.get_source_segment(source, item)
                assert segment is not None
                return segment
    raise AssertionError(f"missing {class_name}.{method_name}")


def new_searcher(tmp_path: Path) -> Search:
    config.set_data_folder(str(tmp_path))
    return Search()


def test_manual_wishlist_actions_create_normal_searches_by_mode_string():
    source = (BASELINE / "pynicotine/gtkgui/dialogs/wishlist.py").read_text(encoding="utf-8")
    assert source.count('core.search.do_search(wish, mode="wishlist")') >= 2


def test_do_search_uses_normal_search_request_constructor_path():
    body = method_source(BASELINE / "pynicotine/search.py", "Search", "do_search")
    assert "self._add_search(" in body
    assert "self._add_wish_search(" not in body


def test_normal_and_persistent_wishlist_constructors_are_distinct():
    add_search = method_source(BASELINE / "pynicotine/search.py", "Search", "_add_search")
    add_wish = method_source(BASELINE / "pynicotine/search.py", "Search", "_add_wish_search")
    assert "SearchRequest(" in add_search and "WishSearchRequest(" not in add_search
    assert "WishSearchRequest(" in add_wish


def test_manual_wishlist_request_is_ephemeral_class_with_wishlist_mode(tmp_path):
    searcher = new_searcher(tmp_path)
    request = searcher._add_search(searcher.token, "needle", "wishlist")
    assert type(request) is SearchRequest
    assert request.mode == "wishlist"
    assert not hasattr(request, "ignored_users")


def test_persistent_wishlist_request_owns_seen_history(tmp_path):
    searcher = new_searcher(tmp_path)
    request = searcher._add_wish_search(searcher.token, "needle")
    assert isinstance(request, WishSearchRequest)
    assert request.mode == "wishlist"
    assert request.ignored_users == set()


def test_wishlist_gui_notifications_use_wire_token_as_action_target():
    page_body = method_source(BASELINE / "pynicotine/gtkgui/search.py", "Search", "file_search_response")
    app_body = method_source(
        BASELINE / "pynicotine/gtkgui/application.py", "Application", "on_search_notification_activated"
    )
    assert 'is_wish = (self.mode == "wishlist")' in page_body
    assert "show_search_notification(" in page_body
    assert "str(self.token)" in page_body
    assert "core.search.show_search(search_token)" in app_body


def test_wishlist_seen_history_updates_only_for_persistent_matching_token():
    body = method_source(BASELINE / "pynicotine/gtkgui/search.py", "Search", "on_read_changed")
    assert "core.search.wishlist.get(self.text)" in body
    assert "search.token != self.token" in body
    assert "search.ignored_users.add(username)" in body


def test_candidate_core_owns_mode_classification():
    body = method_source(PATCHED / "pynicotine/search.py", "Search", "repeat_search")
    assert 'if search.mode == "wishlist":' in body
    assert "self.send_search_request(token)" in body
    assert "isinstance(search, WishSearchRequest)" not in body


def test_candidate_gui_delegates_without_a_second_wishlist_classifier():
    body = method_source(PATCHED / "pynicotine/gtkgui/search.py", "Search", "on_search_again")
    assert "core.search.repeat_search(self.token)" in body
    assert 'self.mode == "wishlist"' not in body
    assert "core.search.send_search_request(self.token)" not in body


def test_candidate_rekeys_an_ordinary_search(tmp_path):
    searcher = new_searcher(tmp_path)
    old_token = searcher.token
    request = searcher._add_search(old_token, "needle", "global")
    trace = []

    def on_rekey(old, new):
        trace.append((old, new))

    events.connect("rekey-search", on_rekey)
    try:
        with patch.object(Search, "remove_allowed_token"), patch.object(Search, "send_search_request") as send:
            new_token = searcher.repeat_search(old_token)
    finally:
        events.disconnect("rekey-search", on_rekey)
    assert new_token != old_token
    assert request is searcher.searches[new_token]
    assert old_token not in searcher.searches
    assert trace == [(old_token, new_token)]
    send.assert_called_once_with(new_token)


def test_candidate_retries_manual_wishlist_without_rekey(tmp_path):
    searcher = new_searcher(tmp_path)
    token = searcher.token
    request = searcher._add_search(token, "needle", "wishlist")
    rekeys = []

    def on_rekey(old, new):
        rekeys.append((old, new))

    events.connect("rekey-search", on_rekey)
    try:
        with patch.object(Search, "send_search_request") as send:
            result = searcher.repeat_search(token)
    finally:
        events.disconnect("rekey-search", on_rekey)
    assert result == token
    assert searcher.searches == {token: request}
    send.assert_called_once_with(token)
    assert rekeys == []


def test_candidate_retries_persistent_wishlist_without_rekey_or_seen_reset(tmp_path):
    searcher = new_searcher(tmp_path)
    token = searcher.token
    request = searcher._add_wish_search(token, "needle", ignored_users={"seen"})
    with patch.object(Search, "send_search_request") as send:
        result = searcher.repeat_search(token)
    assert result == token
    assert searcher.searches[token] is request
    assert request.ignored_users == {"seen"}
    send.assert_called_once_with(token)


def test_mode_owned_model_preserves_manual_wishlist_notification_target():
    model = SearchAgainOwnershipModel(mode="wishlist", request_kind="SearchRequest")
    old_target = model.notify()
    assert model.repeat_mode_owned() == old_target
    assert model.activate_notification(old_target) == "opened"


def test_type_only_policy_stales_manual_wishlist_notification_target():
    model = SearchAgainOwnershipModel(mode="wishlist", request_kind="SearchRequest")
    old_target = model.notify()
    assert model.repeat_type_only() != old_target
    assert model.activate_notification(old_target) == "stale-target"


def test_mode_owned_model_rekeys_nonwishlist_and_rejects_old_owner():
    model = SearchAgainOwnershipModel(mode="global", request_kind="SearchRequest")
    old_token = model.token
    new_token = model.repeat_mode_owned()
    assert new_token != old_token
    assert old_token not in model.pages and old_token not in model.searches
    assert model.trace == ["core-rekey", "gui-rekey", "send"]


def test_both_wishlist_provenances_remain_same_token_retries():
    manual = SearchAgainOwnershipModel(mode="wishlist", request_kind="SearchRequest")
    scheduled = SearchAgainOwnershipModel(mode="wishlist", request_kind="WishSearchRequest")
    assert manual.repeat_mode_owned() == manual.token
    assert scheduled.repeat_mode_owned() == scheduled.token
    assert manual.trace == ["wishlist-retry", "send"]
    assert scheduled.trace == ["wishlist-retry", "send"]
