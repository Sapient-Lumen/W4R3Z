from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Any


ActionFn = Callable[["Editor"], bool]


@dataclass(frozen=True)
class Action:
    name: str
    fn: ActionFn
    doc: str = ""
    group: str | None = None
    script_context: bool = False
    plugin_load_root: str | None = None
    plugin_generation: int | None = None
    script_origin_id: str | None = None


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}
        self._context_provider: Callable[[], dict[str, object]] | None = None
        self._mutation_guard: Callable[[str, Action | None], None] | None = None

    def set_context_provider(self, provider: Callable[[], dict[str, object]] | None) -> None:
        """Install a best-effort owner callback for direct registrations.

        The editor intentionally still exposes ``actions.register(...)`` for
        older tests/plugins.  The callback lets those direct calls inherit the
        same script/plugin provenance and group cleanup as checked command/key
        registration without making this tiny registry depend on ``Editor``.
        """

        self._context_provider = provider

    def set_mutation_guard(self, guard: Callable[[str, Action | None], None] | None) -> None:
        """Install an owner callback that can reject unsafe overwrites."""

        self._mutation_guard = guard

    def _context(self) -> dict[str, object]:
        provider = self._context_provider
        if provider is None:
            return {}
        try:
            ctx = provider()
        except Exception:
            return {}
        return dict(ctx or {})

    def register(
        self,
        name: str,
        fn: ActionFn,
        *,
        doc: str = "",
        group: str | None = None,
        script_context: bool | None = None,
        plugin_load_root: str | None = None,
        plugin_generation: int | None = None,
        script_origin_id: str | None = None,
    ) -> None:
        action_name = str(name)
        existing = self._actions.get(action_name)
        if existing is not None and self._mutation_guard is not None:
            self._mutation_guard(action_name, existing)

        ctx = self._context()
        if group is None:
            raw_group = ctx.get("group")
            group = str(raw_group) if raw_group not in (None, "", 0) else None
        if script_context is None:
            script_context = bool(ctx.get("script_context", False))
        if plugin_load_root is None:
            raw_root = ctx.get("plugin_load_root")
            plugin_load_root = str(raw_root) if raw_root not in (None, "") else None
        if plugin_generation is None:
            raw_generation = ctx.get("plugin_generation")
            if raw_generation not in (None, ""):
                try:
                    plugin_generation = int(raw_generation)  # type: ignore[arg-type]
                except Exception:
                    plugin_generation = None
        if script_origin_id is None:
            raw_origin = ctx.get("script_origin_id")
            script_origin_id = str(raw_origin) if raw_origin not in (None, "") else None

        self._actions[action_name] = Action(
            name=action_name,
            fn=fn,
            doc=str(doc),
            group=group,
            script_context=bool(script_context),
            plugin_load_root=(str(plugin_load_root) if plugin_load_root else None),
            plugin_generation=(int(plugin_generation) if plugin_generation not in (None, "") else None),
            script_origin_id=(str(script_origin_id) if script_origin_id else None),
        )

    def remove(self, name: str) -> bool:
        return self._actions.pop(str(name), None) is not None

    def get(self, name: str) -> Action | None:
        return self._actions.get(str(name))

    def names(self) -> list[str]:
        return sorted(self._actions.keys())

    def action_rows(self) -> list[list[object]]:
        rows: list[list[object]] = []
        for name in sorted(self._actions.keys()):
            action = self._actions[name]
            rows.append([action.name, action.doc, action.group or 0])
        return rows

    def remove_group(self, group: str) -> int:
        group_s = str(group or "")
        if not group_s:
            return 0
        removed = 0
        for name, action in list(self._actions.items()):
            if str(action.group or "") == group_s:
                del self._actions[name]
                removed += 1
        return int(removed)

    def retag_group(self, old: str, new: str) -> int:
        old_s = str(old or "")
        new_s = str(new or "")
        if not old_s or not new_s or old_s == new_s:
            return 0
        changed = 0
        for name, action in list(self._actions.items()):
            if str(action.group or "") == old_s:
                self._actions[name] = replace(action, group=new_s)
                changed += 1
        return int(changed)

    def groups(self) -> list[str]:
        return sorted({str(a.group) for a in self._actions.values() if a.group})


# Back-compat: older revs called this CommandRegistry.
CommandRegistry = ActionRegistry
