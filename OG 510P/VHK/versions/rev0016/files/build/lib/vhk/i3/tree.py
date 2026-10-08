from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from vhk.core.models import I3WindowSelector


@dataclass
class I3Match:
    node: dict[str, Any]
    workspace: str | None


def _iter_nodes(tree: dict[str, Any]) -> Iterable[tuple[dict[str, Any], str | None]]:
    """Yield (node, workspace_name) pairs depth-first."""

    stack: list[tuple[dict[str, Any], str | None]] = [(tree, None)]
    while stack:
        node, ws = stack.pop()

        ws2 = ws
        if node.get("type") == "workspace":
            ws2 = node.get("name")

        yield node, ws2

        # i3 tree uses "nodes" and "floating_nodes".
        children = list(node.get("nodes") or []) + list(node.get("floating_nodes") or [])
        for c in reversed(children):
            stack.append((c, ws2))


def _str_match(value: str, pattern: str, regex: bool) -> bool:
    if regex:
        return re.search(pattern, value or "") is not None
    return value == pattern


def node_matches(node: dict[str, Any], selector: I3WindowSelector, workspace: str | None) -> bool:
    wp = node.get("window_properties") or {}

    # sway native windows commonly expose app_id.
    if selector.app_id is not None:
        if not _str_match(str(node.get("app_id") or ""), selector.app_id, selector.app_id_regex):
            return False

    title = (wp.get("title") or node.get("name") or "")

    if selector.title is not None:
        if not _str_match(str(title), selector.title, selector.title_regex):
            return False

    if selector.wm_class is not None:
        if str(wp.get("class") or "") != selector.wm_class:
            return False

    if selector.instance is not None:
        if str(wp.get("instance") or "") != selector.instance:
            return False

    if selector.urgent is not None:
        if bool(node.get("urgent")) != bool(selector.urgent):
            return False

    if selector.focused is not None:
        if bool(node.get("focused")) != bool(selector.focused):
            return False

    if selector.workspace is not None:
        if workspace != selector.workspace:
            return False

    return True


def find_first(tree: dict[str, Any], selector: I3WindowSelector) -> I3Match | None:
    for node, ws in _iter_nodes(tree):
        # Most interesting nodes have a window id or app_id; we still allow
        # matching containers by name.
        if node_matches(node, selector, ws):
            return I3Match(node=node, workspace=ws)
    return None
