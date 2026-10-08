import ast
import os
from pathlib import Path


SOURCE = Path(os.environ["NICOTINE_SOURCE_ROOT"])


def method_source(relative, class_name, method_name):
    path = SOURCE / relative
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return ast.get_source_segment(source, item)
    raise AssertionError(f"missing {class_name}.{method_name}")


def test_current_search_again_is_same_token_resend_without_clear():
    source = method_source("pynicotine/gtkgui/search.py", "Search", "on_search_again")
    assert "core.search.send_search_request(self.token)" in source
    assert "clear_model" not in source
    assert "do_search" not in source


def test_dispatcher_retires_token_when_page_count_is_already_at_cap():
    source = method_source("pynicotine/gtkgui/search.py", "Searches", "file_search_response")
    cap = source.index('page.num_results_found >= config.sections["searches"]["max_displayed_results"]')
    retire = source.index("core.search.remove_allowed_token(msg.token)")
    dispatch = source.rindex("page.file_search_response(msg)")
    assert cap < retire < dispatch


def test_page_rejects_second_response_from_same_username():
    source = method_source("pynicotine/gtkgui/search.py", "Search", "file_search_response")
    assert "if user in self.users:" in source
    assert source.index("if user in self.users:") < source.index("self.initialized = True")


def test_current_page_has_no_clear_results_handler_or_menu_label():
    source = (SOURCE / "pynicotine/gtkgui/search.py").read_text(encoding="utf-8")
    assert "Clear All Results" not in source
    tree = ast.parse(source)
    methods = {
        item.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Search"
        for item in node.body
        if isinstance(item, ast.FunctionDef)
    }
    assert "on_clear" not in methods


def test_new_search_and_removed_page_restore_already_allocate_fresh_tokens():
    core = method_source("pynicotine/search.py", "Search", "do_search")
    restore = method_source("pynicotine/gtkgui/search.py", "Searches", "on_restore_removed_page")
    assert "self.token = increment_token(self.token)" in core
    assert "core.search.do_search(search_term, mode" in restore


def test_current_remove_search_retires_admission_before_deleting_registry_entry():
    source = method_source("pynicotine/search.py", "Search", "remove_search")
    assert source.index("self.remove_allowed_token(token)") < source.index("search = self.searches.get(token)")
