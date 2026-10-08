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


def _i3_floating_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"auto_off", "off", "none", "false", "0"}:
        return False
    if s:
        return True
    return None


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

    if selector.window_role is not None:
        if str(wp.get("window_role") or wp.get("role") or "") != selector.window_role:
            return False

    if selector.pid is not None:
        try:
            if int(node.get("pid") or 0) != int(selector.pid):
                return False
        except Exception:
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

    if selector.visible is not None:
        if "visible" not in node:
            return False
        if bool(node.get("visible")) != bool(selector.visible):
            return False

    if selector.fullscreen_mode is not None:
        if "fullscreen_mode" not in node:
            return False
        try:
            if int(node.get("fullscreen_mode") or 0) != int(selector.fullscreen_mode):
                return False
        except Exception:
            return False

    if selector.fullscreen is not None:
        if "fullscreen_mode" not in node:
            return False
        try:
            fullscreen = int(node.get("fullscreen_mode") or 0) > 0
        except Exception:
            return False
        if fullscreen != bool(selector.fullscreen):
            return False

    if selector.floating is not None:
        floating = _i3_floating_bool(node.get("floating"))
        if floating is None or floating != bool(selector.floating):
            return False

    if selector.sticky is not None:
        if "sticky" not in node:
            return False
        if bool(node.get("sticky")) != bool(selector.sticky):
            return False

    if selector.minimized is not None:
        return False
    if selector.hidden is not None:
        return False
    if selector.mapped is not None:
        return False
    if selector.pinned is not None:
        return False

    return True


def find_first(tree: dict[str, Any], selector: I3WindowSelector) -> I3Match | None:
    for node, ws in _iter_nodes(tree):
        # Most interesting nodes have a window id or app_id; we still allow
        # matching containers by name.
        if node_matches(node, selector, ws):
            return I3Match(node=node, workspace=ws)
    return None


def find_all(tree: dict[str, Any], selector: I3WindowSelector) -> list[I3Match]:
    matches: list[I3Match] = []
    for node, ws in _iter_nodes(tree):
        if node_matches(node, selector, ws):
            matches.append(I3Match(node=node, workspace=ws))
    return matches
