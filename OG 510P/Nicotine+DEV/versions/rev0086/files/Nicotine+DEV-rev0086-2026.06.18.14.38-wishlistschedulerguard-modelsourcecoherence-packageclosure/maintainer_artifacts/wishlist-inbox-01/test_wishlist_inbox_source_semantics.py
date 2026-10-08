from __future__ import annotations

import ast
import os
from pathlib import Path


BASELINE = Path(os.environ["NICOTINE_SOURCE_ROOT"])
PATCHED = Path(os.environ["NICOTINE_PATCHED_SOURCE_ROOT"])


def method(path: Path, class_name: str, method_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    segment = ast.get_source_segment(source, item)
                    assert segment is not None
                    return segment
    raise AssertionError(f"missing {class_name}.{method_name}")


def test_persistent_request_owns_seen_users_and_ignore_state():
    text = method(BASELINE / "pynicotine/search.py", "WishSearchRequest", "__init__")
    assert "self.ignored_users" in text
    assert "self.is_ignored = True" in text


def test_seen_users_are_serialized_as_durable_wishlist_state():
    text = method(BASELINE / "pynicotine/search.py", "WishSearchRequest", "as_dict")
    assert '"ignored_users"' in text
    assert "list(sorted(self.ignored_users))" in text


def test_scheduler_reactivates_wish_and_issues_special_request():
    path = BASELINE / "pynicotine/search.py"
    next_search = method(path, "Search", "_do_next_wishlist_search")
    send = method(path, "Search", "_do_wishlist_search")
    assert "search.is_ignored = False" in next_search
    assert "self._do_wishlist_search(search)" in next_search
    assert "self.add_allowed_token(search.token)" in send
    assert "WishlistSearch(search.token, text)" in send


def test_inherited_search_again_uses_ordinary_global_send_path():
    path = BASELINE / "pynicotine/search.py"
    repeat = method(BASELINE / "pynicotine/gtkgui/search.py", "Search", "on_search_again")
    dispatch = method(path, "Search", "send_search_request")
    assert "send_search_request(self.token)" in repeat
    assert 'search.mode in {"global", "wishlist"}' in dispatch
    assert "self._send_global_search_request(search)" in dispatch


def test_gui_capacity_gate_revokes_admission_without_pausing_scheduler():
    gui = method(BASELINE / "pynicotine/gtkgui/search.py", "Searches", "file_search_response")
    core = method(BASELINE / "pynicotine/search.py", "Search", "_do_next_wishlist_search")
    assert "page.num_results_found >=" in gui
    assert "core.search.remove_allowed_token(msg.token)" in gui
    assert "search.is_ignored = False" in core
    assert "is_paused" not in core


def test_read_transition_records_sender_level_seen_state():
    text = method(BASELINE / "pynicotine/gtkgui/search.py", "Search", "on_read_changed")
    assert "username = row[0]" in text
    assert "search.ignored_users.add(username)" in text


def test_core_drops_seen_sender_before_page_file_comparison():
    text = method(BASELINE / "pynicotine/search.py", "Search", "_file_search_response")
    assert "username in search.ignored_users" in text
    assert "msg.token = None" in text


def test_dialog_has_separate_manual_search_and_seen_reset_commands():
    text = (BASELINE / "pynicotine/gtkgui/dialogs/wishlist.py").read_text(encoding="utf-8")
    assert '_Search for Item' in text
    assert 'Reset Seen Results' in text
    reset = method(BASELINE / "pynicotine/gtkgui/dialogs/wishlist.py", "WishList", "on_reset_seen_results")
    assert "search.ignored_users.clear()" in reset


def test_closing_persistent_page_ignores_instead_of_deleting_request():
    text = method(BASELINE / "pynicotine/search.py", "Search", "remove_search")
    assert "isinstance(search, WishSearchRequest)" in text
    assert "search.is_ignored = True" in text


def test_current_page_menu_exposes_search_again_to_all_search_pages():
    text = (BASELINE / "pynicotine/gtkgui/search.py").read_text(encoding="utf-8")
    assert '("#" + _("Search _Again"), self.on_search_again)' in text


def test_candidate_classifies_repeatability_by_request_owner_not_mode():
    text = method(PATCHED / "pynicotine/search.py", "Search", "can_repeat_search")
    assert "not isinstance(search, WishSearchRequest)" in text
    assert ".mode" not in text


def test_candidate_repeat_guard_never_resends_persistent_request():
    text = method(PATCHED / "pynicotine/search.py", "Search", "repeat_search")
    assert "search is None or isinstance(search, WishSearchRequest)" in text
    assert "self.send_search_request(token)" not in text


def test_candidate_hides_disabled_action_and_defends_callback():
    path = PATCHED / "pynicotine/gtkgui/search.py"
    source = path.read_text(encoding="utf-8")
    callback = method(path, "Search", "on_search_again")
    assert '("=" + _("Search _Again"), self.on_search_again)' in source
    assert 'set_enabled(\n            core.search.can_repeat_search(self.token)' in source
    assert "if not core.search.can_repeat_search(self.token):" in callback


def test_candidate_does_not_clear_persistent_seen_history():
    text = method(PATCHED / "pynicotine/search.py", "Search", "repeat_search")
    assert "ignored_users" not in text
    assert "clear_wish" not in text
