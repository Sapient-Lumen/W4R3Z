from __future__ import annotations

import ast
import os
from pathlib import Path
from types import SimpleNamespace

PATCH_ROOT = Path(os.environ["NICOTINE_PATCH_SOURCE_ROOT"])
GUI_PATH = PATCH_ROOT / "pynicotine/gtkgui/search.py"


def compile_method(class_name: str, method_name: str, globals_ns=None):
    source = GUI_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == method_name:
                module = ast.Module(body=[item], type_ignores=[])
                ast.fix_missing_locations(module)
                namespace = {} if globals_ns is None else dict(globals_ns)
                exec(compile(module, str(GUI_PATH), "exec"), namespace)
                return namespace[method_name]
    raise AssertionError(f"missing {class_name}.{method_name}")


def test_manager_rekeys_same_page_in_place_and_preserves_mapping_order():
    method = compile_method("Searches", "rekey_search")
    calls = []
    before = SimpleNamespace()
    page = SimpleNamespace(
        token=10,
        show_page=True,
        container=object(),
        reset_for_search_again=lambda: calls.append(("reset", page.token)),
    )
    after = SimpleNamespace()
    manager = SimpleNamespace(
        pages={1: before, 10: page, 20: after},
        remove_tab_changed=lambda container: calls.append(("read", container)),
        window=SimpleNamespace(update_title=lambda: calls.append(("title",))),
    )
    method(manager, 10, 11)
    assert tuple(manager.pages) == (1, 11, 20)
    assert manager.pages[11] is page
    assert page.token == 11
    assert calls == [("reset", 11), ("read", page.container), ("title",)]


def test_missing_gui_page_is_a_noop():
    method = compile_method("Searches", "rekey_search")
    manager = SimpleNamespace(pages={})
    method(manager, 1, 2)
    assert manager.pages == {}


def test_page_reset_clears_generation_and_selection_but_not_view_controls():
    method = compile_method("Search", "reset_for_search_again")
    calls = []
    filters = {"include": "lossless"}
    tree = object()
    page = SimpleNamespace(
        filters=filters,
        grouping_mode="user_grouping",
        tree_view=tree,
        selected_results={1: object()},
        selected_users={"alice": None},
        info_bar=SimpleNamespace(set_visible=lambda value: calls.append(("visible", value))),
        clear_model=lambda stored_results=False: calls.append(("clear", stored_results)),
        update_result_counter=lambda: calls.append(("counter",)),
    )
    method(page)
    assert page.selected_results == {}
    assert page.selected_users == {}
    assert page.filters is filters
    assert page.grouping_mode == "user_grouping"
    assert page.tree_view is tree
    assert calls == [("visible", False), ("clear", True), ("counter",)]


def run_again(mode: str, status: int):
    calls = []

    class UserStatus:
        OFFLINE = 0

    fake_core = SimpleNamespace(
        users=SimpleNamespace(login_username="me", statuses={"me": status}),
        search=SimpleNamespace(
            repeat_search=lambda token: calls.append(("repeat", token)),
            send_search_request=lambda token: calls.append(("send", token)),
        ),
    )
    method = compile_method("Search", "on_search_again", {"core": fake_core, "UserStatus": UserStatus})
    page = SimpleNamespace(
        token=44,
        mode=mode,
        info_bar=SimpleNamespace(set_visible=lambda value: calls.append(("visible", value))),
        show_error_message=lambda: calls.append(("error",)),
    )
    method(page)
    return calls


def test_regular_online_click_uses_fresh_token_api_and_rechecks_status():
    assert run_again("global", status=1) == [("repeat", 44), ("error",)]


def test_wishlist_online_click_retains_same_token_retry_policy():
    assert run_again("wishlist", status=1) == [("visible", False), ("send", 44), ("error",)]


def test_offline_click_preserves_page_instead_of_clearing_it():
    assert run_again("global", status=0) == [("error",)]
