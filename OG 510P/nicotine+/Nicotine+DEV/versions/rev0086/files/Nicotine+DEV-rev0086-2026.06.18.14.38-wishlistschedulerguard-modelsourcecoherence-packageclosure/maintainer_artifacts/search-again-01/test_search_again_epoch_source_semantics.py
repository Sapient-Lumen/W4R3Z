"""AST-level witnesses for the current same-token/no-clear GUI behavior."""
from __future__ import annotations

import ast
from pathlib import Path

import pynicotine.search as search_mod


def function_node(source: str, class_name: str, function_name: str) -> ast.FunctionDef:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == function_name:
                    return child
    raise AssertionError(f"missing {class_name}.{function_name}")


def source_text(node: ast.AST, source: str) -> str:
    text = ast.get_source_segment(source, node)
    assert text is not None
    return text


def gui_source() -> str:
    path = Path(search_mod.__file__).resolve().parent / "gtkgui" / "search.py"
    return path.read_text(encoding="utf-8")


def test_search_again_reuses_page_token_without_clearing_results():
    source = gui_source()
    node = function_node(source, "Search", "on_search_again")
    text = source_text(node, source)

    assert "send_search_request(self.token)" in text
    assert "clear(" not in text
    assert "clear_model(" not in text


def test_result_handler_deduplicates_username_for_page_lifetime():
    source = gui_source()
    node = function_node(source, "Search", "file_search_response")
    text = source_text(node, source)

    assert "if user in self.users:" in text
    assert "return" in text


def test_clear_model_is_the_path_that_resets_username_deduplication():
    source = gui_source()
    node = function_node(source, "Search", "clear_model")
    text = source_text(node, source)

    assert "self.users.clear()" in text
