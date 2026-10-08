from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from vhk.core.models import I3WindowSelector

_STATE_FIELDS: tuple[str, ...] = (
    "visible",
    "fullscreen",
    "fullscreen_mode",
    "floating",
    "sticky",
    "minimized",
    "hidden",
    "mapped",
    "pinned",
)

_IDENTITY_FIELDS: tuple[str, ...] = (
    "app_id",
    "title",
    "wm_class",
    "instance",
    "window_role",
    "workspace",
    "focused",
    "urgent",
)


def _iter_steps(steps: Iterable[Any], *, prefix: str = "steps") -> Iterable[tuple[Any, str]]:
    for i, step in enumerate(steps or []):
        path = f"{prefix}[{i}]"
        yield step, path
        step_type = getattr(step, "type", None)
        if step_type == "If":
            yield from _iter_steps(getattr(step, "then_steps", []) or [], prefix=f"{path}.then_steps")
            yield from _iter_steps(getattr(step, "else_steps", []) or [], prefix=f"{path}.else_steps")
        elif step_type == "While":
            yield from _iter_steps(getattr(step, "steps", []) or [], prefix=f"{path}.steps")
        elif step_type == "Try":
            yield from _iter_steps(getattr(step, "steps", []) or [], prefix=f"{path}.steps")
            yield from _iter_steps(getattr(step, "catch_steps", []) or [], prefix=f"{path}.catch_steps")
            yield from _iter_steps(getattr(step, "finally_steps", []) or [], prefix=f"{path}.finally_steps")
        elif step_type == "ForEach":
            yield from _iter_steps(getattr(step, "steps", []) or [], prefix=f"{path}.steps")


def _selector_contract(selector: I3WindowSelector | None) -> dict[str, Any]:
    if selector is None:
        return {
            "used": False,
            "state_fields": [],
            "identity_fields": [],
            "process_scoped": False,
            "field_count": 0,
        }

    state_fields = sorted(field for field in _STATE_FIELDS if getattr(selector, field, None) is not None)
    identity_fields = sorted(field for field in _IDENTITY_FIELDS if getattr(selector, field, None) is not None)
    process_scoped = getattr(selector, "pid", None) is not None

    return {
        "used": bool(state_fields or identity_fields or process_scoped),
        "state_fields": state_fields,
        "identity_fields": identity_fields,
        "process_scoped": process_scoped,
        "field_count": len(state_fields) + len(identity_fields) + (1 if process_scoped else 0),
    }


def summarize_project_window_contract(project) -> dict[str, Any]:
    state_fields_used: set[str] = set()
    identity_fields_used: set[str] = set()
    selector_examples: list[dict[str, Any]] = []
    selector_site_count = 0
    stateful_selector_count = 0
    process_scoped_selector_count = 0

    geometry_requested_count = 0
    geometry_required_count = 0
    pointer_window_count = 0
    pointer_window_required_count = 0
    active_window_steps = 0
    window_at_cursor_steps = 0
    window_list_steps = 0
    window_list_selector_count = 0
    wait_window_steps = 0
    window_event_wait_count = 0
    window_event_kinds_used: set[str] = set()

    def record_selector(selector: I3WindowSelector | None, *, source: str, macro: str | None = None, path: str | None = None, extra: dict[str, Any] | None = None) -> None:
        nonlocal selector_site_count, stateful_selector_count, process_scoped_selector_count
        info = _selector_contract(selector)
        if not info["used"]:
            return
        selector_site_count += 1
        state_fields = list(info["state_fields"] or [])
        identity_fields = list(info["identity_fields"] or [])
        if state_fields:
            stateful_selector_count += 1
            state_fields_used.update(state_fields)
        if identity_fields:
            identity_fields_used.update(identity_fields)
        if info["process_scoped"]:
            process_scoped_selector_count += 1
        if len(selector_examples) < 12:
            item = {
                "source": source,
                "state_fields": state_fields,
                "identity_fields": identity_fields,
                "process_scoped": bool(info["process_scoped"]),
            }
            if macro:
                item["macro"] = macro
            if path:
                item["path"] = path
            if extra:
                item.update(extra)
            selector_examples.append(item)

    for binding in getattr(project, "bindings", []) or []:
        record_selector(getattr(binding, "when", None), source="binding_when", extra={"keys": getattr(binding, "keys", None)})

    for hotstring in getattr(project, "hotstrings", []) or []:
        record_selector(getattr(hotstring, "when", None), source="hotstring_when", extra={"trigger": getattr(hotstring, "trigger", None)})

    for watcher in getattr(project, "bus_watchers", []) or []:
        record_selector(getattr(watcher, "when", None), source="bus_watcher_when", extra={"watcher": getattr(watcher, "name", None)})

    for watcher in getattr(project, "window_watchers", []) or []:
        watcher_event = str(getattr(watcher, "event", "") or "").strip()
        if watcher_event:
            window_event_kinds_used.add(watcher_event)
        record_selector(getattr(watcher, "when", None), source="window_watcher_when", extra={"watcher": getattr(watcher, "name", None), "event": watcher_event or None})

    for macro_name, macro in getattr(project, "macros", {}).items():
        for step, path in _iter_steps(getattr(macro, "steps", []) or []):
            step_type = str(getattr(step, "type", "") or "")
            if step_type in {"WaitForWindow", "WaitForWindowVanish", "FocusWindow"}:
                wait_window_steps += 1
                record_selector(getattr(step, "selector", None), source="step", macro=macro_name, path=path, extra={"step_type": step_type})
            elif step_type == "WaitForWindowEvent":
                window_event_wait_count += 1
                event_kind = str(getattr(step, "event", "") or "").strip()
                if event_kind:
                    window_event_kinds_used.add(event_kind)
                record_selector(getattr(step, "selector", None), source="step", macro=macro_name, path=path, extra={"step_type": step_type, "event": event_kind or None})
            elif step_type == "GetWindowList":
                window_list_steps += 1
                if bool(getattr(step, "include_geometry", False)):
                    geometry_requested_count += 1
                selector = getattr(step, "selector", None)
                if selector is not None:
                    window_list_selector_count += 1
                record_selector(selector, source="step", macro=macro_name, path=path, extra={"step_type": step_type})
            elif step_type == "GetActiveWindow":
                active_window_steps += 1
                if bool(getattr(step, "include_geometry", False)):
                    geometry_requested_count += 1
                if bool(getattr(step, "require_geometry", False)):
                    geometry_required_count += 1
            elif step_type == "GetWindowAtCursor":
                window_at_cursor_steps += 1
                pointer_window_count += 1
                if bool(getattr(step, "include_geometry", False)):
                    geometry_requested_count += 1
                if bool(getattr(step, "require_geometry", False)):
                    geometry_required_count += 1
                if bool(getattr(step, "require_window", False)):
                    pointer_window_required_count += 1

    dependency_tags: list[str] = []
    if state_fields_used:
        dependency_tags.append("stateful-window-selectors")
    if process_scoped_selector_count:
        dependency_tags.append("process-scoped-windows")
    if geometry_required_count:
        dependency_tags.append("geometry-required")
    elif geometry_requested_count:
        dependency_tags.append("geometry-observing")
    if pointer_window_count:
        dependency_tags.append("pointer-window")
    if window_event_kinds_used:
        dependency_tags.append("event-driven-window-hooks")

    summary_parts: list[str] = []
    if selector_site_count:
        summary_parts.append(f"{selector_site_count} selector site(s)")
    if state_fields_used:
        summary_parts.append("state fields: " + ", ".join(sorted(state_fields_used)))
    if process_scoped_selector_count:
        summary_parts.append(f"{process_scoped_selector_count} PID-scoped selector(s)")
    if geometry_required_count:
        summary_parts.append(f"{geometry_required_count} geometry-required step(s)")
    elif geometry_requested_count:
        summary_parts.append(f"{geometry_requested_count} geometry-observing step(s)")
    if pointer_window_count:
        summary_parts.append(f"{pointer_window_count} pointer-window step(s)")
    if window_event_kinds_used:
        summary_parts.append("event kinds: " + ", ".join(sorted(window_event_kinds_used)))
        if window_event_wait_count:
            summary_parts.append(f"{window_event_wait_count} event-wait step(s)")

    return {
        "used": bool(selector_site_count or geometry_requested_count or geometry_required_count or pointer_window_count or active_window_steps or window_list_steps or window_event_wait_count or window_event_kinds_used),
        "selector_site_count": selector_site_count,
        "stateful_selector_count": stateful_selector_count,
        "state_fields_used": sorted(state_fields_used),
        "identity_fields_used": sorted(identity_fields_used),
        "process_scoped_selector_count": process_scoped_selector_count,
        "geometry_requested_count": geometry_requested_count,
        "geometry_required_count": geometry_required_count,
        "pointer_window_count": pointer_window_count,
        "pointer_window_required_count": pointer_window_required_count,
        "active_window_steps": active_window_steps,
        "window_at_cursor_steps": window_at_cursor_steps,
        "window_list_steps": window_list_steps,
        "window_list_selector_count": window_list_selector_count,
        "wait_window_steps": wait_window_steps,
        "window_event_wait_count": window_event_wait_count,
        "event_kinds_used": sorted(window_event_kinds_used),
        "dependency_tags": dependency_tags,
        "selector_examples": selector_examples,
        "summary": "; ".join(summary_parts) if summary_parts else "no notable window contract requirements",
    }
