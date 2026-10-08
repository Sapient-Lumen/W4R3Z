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


def test_current_post_scan_guard_ignores_auto_search_eligibility():
    text = method(BASELINE / "pynicotine/search.py", "Search", "_do_next_wishlist_search")
    assert "if search is not None:" in text
    assert "if search is not None and search.auto_search:" not in text


def test_candidate_post_scan_guard_requires_enabled_request():
    text = method(PATCHED / "pynicotine/search.py", "Search", "_do_next_wishlist_search")
    assert "if search is not None and search.auto_search:" in text
    assert "if search is not None:" not in text


def test_candidate_preserves_bounded_rotation_and_first_enabled_break():
    current = method(BASELINE / "pynicotine/search.py", "Search", "_do_next_wishlist_search")
    candidate = method(PATCHED / "pynicotine/search.py", "Search", "_do_next_wishlist_search")
    for fragment in (
        "while nth_search < len(self.wishlist):",
        "search = self.wishlist.pop(term)",
        "self.wishlist[term] = search",
        "if search.auto_search:",
        "break",
    ):
        assert fragment in current
        assert fragment in candidate


def test_auto_search_is_persisted_user_owned_wishlist_state():
    init = method(BASELINE / "pynicotine/search.py", "WishSearchRequest", "__init__")
    serialized = method(BASELINE / "pynicotine/search.py", "WishSearchRequest", "as_dict")
    assert "self.auto_search = auto_search" in init
    assert '"auto_search": self.auto_search' in serialized
