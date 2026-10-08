"""Source-backed and model checks for ordinary Search Again consumers."""
from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

from search_consumer_model import SearchConsumerModel

SOURCE = Path(os.environ["NICOTINE_SOURCE_ROOT"])


def read(relative: str) -> str:
    return (SOURCE / relative).read_text(encoding="utf-8")


def method(relative: str, class_name: str, method_name: str) -> str:
    source = read(relative)
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


def argument_names(relative: str, class_name: str, method_name: str) -> list[str]:
    source = read(relative)
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                return [arg.arg for arg in item.args.args]
    raise AssertionError(f"missing {class_name}.{method_name}")


def test_event_emit_is_synchronous_and_registration_ordered():
    body = method("pynicotine/events.py", "Events", "emit")
    assert "for function in self._callbacks[event_name]" in body
    assert "emit_main_thread" not in body


def test_candidate_event_is_registered():
    assert '"rekey-search"' in read("pynicotine/events.py")


def test_core_rekey_precedes_event_and_send():
    body = method("pynicotine/search.py", "Search", "repeat_search")
    assert body.index("self.searches[new_token] = search") < body.index('events.emit("rekey-search"')
    assert body.index('events.emit("rekey-search"') < body.index("self.send_search_request(new_token)")


def test_old_parser_and_self_tokens_are_retired():
    body = method("pynicotine/search.py", "Search", "repeat_search")
    assert "self.remove_allowed_token(token)" in body
    assert "self._own_tokens.discard(token)" in body


def test_wishlist_is_excluded_from_core_rekey():
    body = method("pynicotine/search.py", "Search", "repeat_search")
    assert "isinstance(search, WishSearchRequest)" in body
    assert "return None" in body


def test_gui_callback_is_registered():
    source = read("pynicotine/gtkgui/search.py")
    assert '("rekey-search", self.rekey_search)' in source


def test_gui_rekey_preserves_page_object_and_insertion_position():
    body = method("pynicotine/gtkgui/search.py", "Searches", "rekey_search")
    assert "page = self.pages.get(old_token)" in body
    assert "new_token if token == old_token else token" in body
    assert "page.token = new_token" in body
    assert "page.reset_for_search_again()" in body


def test_gui_reset_clears_stale_selection_iterators():
    body = method("pynicotine/gtkgui/search.py", "Search", "reset_for_search_again")
    assert "self.selected_results.clear()" in body
    assert "self.selected_users.clear()" in body
    assert "self.clear_model(stored_results=True)" in body


def test_core_unknown_token_response_is_invalidated():
    body = method("pynicotine/search.py", "Search", "_file_search_response")
    assert "search = self.searches.get(msg.token)" in body
    assert "if search is None:" in body
    assert "msg.token = None" in body


def test_gui_routes_response_by_current_wire_token():
    body = method("pynicotine/gtkgui/search.py", "Searches", "file_search_response")
    assert "page = self.pages.get(msg.token)" in body


def test_ordinary_pages_do_not_emit_search_notifications():
    body = method("pynicotine/gtkgui/search.py", "Search", "file_search_response")
    assert "if tab_changed and is_wish:" in body
    notification = body.index("core.notifications.show_search_notification")
    wish_guard = body.index("if tab_changed and is_wish:")
    assert wish_guard < notification


def test_search_notification_action_target_is_the_token():
    body = method("pynicotine/gtkgui/application.py", "Application", "_show_search_notification")
    assert "action_target=search_token" in body


@pytest.mark.parametrize(
    "method_name,expected",
    [
        ("outgoing_global_search_event", ["self", "text"]),
        ("outgoing_room_search_event", ["self", "rooms", "text"]),
        ("outgoing_buddy_search_event", ["self", "text"]),
        ("outgoing_user_search_event", ["self", "users", "text"]),
        ("outgoing_wishlist_search_event", ["self", "text"]),
    ],
)
def test_documented_plugin_search_hooks_do_not_expose_wire_token(method_name, expected):
    assert argument_names("pynicotine/pluginsystem.py", "BasePlugin", method_name) == expected


def test_repeat_uses_processed_request_without_rerunning_plugin_hooks():
    repeat = method("pynicotine/search.py", "Search", "repeat_search")
    assert "pluginhandler" not in repeat
    assert "self.send_search_request(new_token)" in repeat


def test_recently_closed_search_identity_is_token_free():
    body = method("pynicotine/gtkgui/search.py", "Searches", "remove_search")
    assert "page_args=(page.text, page.mode, page.room, page.searched_users)" in body
    assert "page.token" not in body


def test_recently_closed_restore_creates_a_new_search_epoch():
    body = method("pynicotine/gtkgui/search.py", "Searches", "on_restore_removed_page")
    assert "core.search.do_search(search_term, mode, room=room, users=users)" in body


def test_close_uses_the_pages_current_token():
    body = method("pynicotine/gtkgui/search.py", "Search", "on_close")
    assert "core.search.remove_search(self.token)" in body


def test_gui_mode_split_keeps_wishlist_on_legacy_retry():
    body = method("pynicotine/gtkgui/search.py", "Search", "on_search_again")
    assert 'if self.mode == "wishlist":' in body
    assert "core.search.send_search_request(self.token)" in body
    assert "core.search.repeat_search(self.token)" in body


def test_model_rekey_preserves_order_and_page_identity():
    model = SearchConsumerModel()
    page = model.pages[20]
    assert model.repeat(20, 21) == 21
    assert list(model.pages) == [10, 21, 30]
    assert model.pages[21] is page
    assert page.rows == 0


def test_model_old_response_is_rejected_and_new_response_is_accepted():
    model = SearchConsumerModel()
    model.repeat(20, 21)
    assert not model.accept_response(20)
    assert model.accept_response(21)


def test_model_rekeys_before_send():
    model = SearchConsumerModel()
    model.repeat(20, 21)
    assert model.trace == ["core-rekey", "gui-rekey", "send"]


def test_model_rapid_repeat_leaves_only_latest_epoch_live():
    model = SearchConsumerModel()
    model.repeat(20, 21)
    model.repeat(21, 22)
    assert 20 not in model.requests and 21 not in model.requests
    assert 22 in model.requests and model.accept_response(22)
    assert not model.accept_response(20) and not model.accept_response(21)


def test_model_close_after_rekey_closes_current_epoch():
    model = SearchConsumerModel()
    model.repeat(20, 21)
    model.close(model.pages[21].token)
    assert 21 not in model.pages
    assert 21 not in model.requests
    assert 21 not in model.allowed_tokens


def test_model_recently_closed_args_are_independent_of_wire_epoch():
    model = SearchConsumerModel()
    before = model.restore_args(20)
    model.repeat(20, 21)
    after = model.restore_args(21)
    assert before == after


def test_model_wishlist_rekey_is_rejected_without_state_change():
    model = SearchConsumerModel(tokens=(7,))
    model.requests[7].mode = "wishlist"
    model.pages[7].mode = "wishlist"
    assert model.repeat(7, 8) is None
    assert list(model.pages) == [7]
    assert list(model.requests) == [7]
