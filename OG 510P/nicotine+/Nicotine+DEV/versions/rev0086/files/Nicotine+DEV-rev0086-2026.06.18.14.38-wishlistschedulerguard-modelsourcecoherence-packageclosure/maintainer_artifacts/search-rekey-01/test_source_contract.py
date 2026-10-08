from __future__ import annotations

import ast
import os
from pathlib import Path

BASE = Path(os.environ["NICOTINE_BASE_SOURCE_ROOT"])
PATCH = Path(os.environ["NICOTINE_PATCH_SOURCE_ROOT"])


def method_source(path: Path, class_name: str, method_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                segment = ast.get_source_segment(source, item)
                if segment is not None:
                    return segment
    raise AssertionError(f"missing {class_name}.{method_name}")


def test_baseline_same_token_cap_flow_is_still_present():
    gui = BASE / "pynicotine/gtkgui/search.py"
    again = method_source(gui, "Search", "on_search_again")
    dispatch = method_source(gui, "Searches", "file_search_response")
    assert "core.search.send_search_request(self.token)" in again
    assert 'page.num_results_found >= config.sections["searches"]["max_displayed_results"]' in dispatch
    assert "core.search.remove_allowed_token(msg.token)" in dispatch


def test_prototype_changes_only_three_upstream_files():
    changed = []
    for path in BASE.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(BASE)
        other = PATCH / relative
        if not other.is_file() or path.read_bytes() != other.read_bytes():
            changed.append(relative.as_posix())
    for path in PATCH.rglob("*"):
        if (
            path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
            and not (BASE / path.relative_to(PATCH)).exists()
        ):
            changed.append(path.relative_to(PATCH).as_posix())
    assert sorted(set(changed)) == [
        "pynicotine/events.py",
        "pynicotine/gtkgui/search.py",
        "pynicotine/search.py",
    ]


def test_prototype_has_ordered_old_token_barriers_and_same_page_rekey():
    core = PATCH / "pynicotine/search.py"
    gui = PATCH / "pynicotine/gtkgui/search.py"
    repeat = method_source(core, "Search", "repeat_search")
    rekey = method_source(gui, "Searches", "rekey_search")
    assert repeat.index("self.remove_allowed_token(token)") < repeat.index("del self.searches[token]")
    assert repeat.index('events.emit("rekey-search"') < repeat.index("self.send_search_request(new_token)")
    assert "self._own_tokens.discard(token)" in repeat
    assert "page.reset_for_search_again()" in rekey
    assert "self.remove_page" not in rekey
    assert "self.create_page" not in rekey


def test_rekey_event_is_synchronous_before_new_request_dispatch():
    events_source = (BASE / "pynicotine/events.py").read_text(encoding="utf-8")
    emit = method_source(BASE / "pynicotine/events.py", "Events", "emit")
    assert "for function in self._callbacks[event_name]" in emit
    assert "function(*args, **kwargs)" in emit
    assert "emit_main_thread" not in emit
    assert '"rekey-search"' in (PATCH / "pynicotine/events.py").read_text(encoding="utf-8")
    assert '"rekey-search"' not in events_source


def test_reset_clears_invalid_selection_caches_before_model_iterators():
    reset = method_source(PATCH / "pynicotine/gtkgui/search.py", "Search", "reset_for_search_again")
    assert reset.index("self.selected_results.clear()") < reset.index("self.clear_model(stored_results=True)")
    assert reset.index("self.selected_users.clear()") < reset.index("self.clear_model(stored_results=True)")


def test_wishlist_seen_history_has_a_separate_explicit_reset_action():
    wishlist = BASE / "pynicotine/gtkgui/dialogs/wishlist.py"
    source = wishlist.read_text(encoding="utf-8")
    reset = method_source(wishlist, "WishList", "on_reset_seen_results")
    assert '_("Reset Seen Results")' in source
    assert "search.ignored_users.clear()" in reset


def test_only_wishlist_results_emit_search_desktop_notifications():
    gui = (BASE / "pynicotine/gtkgui/search.py").read_text(encoding="utf-8")
    assert gui.count("show_search_notification(") == 1
    context = gui[gui.index("show_search_notification(") - 300:gui.index("show_search_notification(") + 200]
    assert "if tab_changed and is_wish:" in context
    patched_core = (PATCH / "pynicotine/search.py").read_text(encoding="utf-8")
    assert "search_token_alias" not in patched_core
