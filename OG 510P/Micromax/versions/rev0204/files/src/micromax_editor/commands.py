from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


ActionFn = Callable[["Editor"], bool]


@dataclass
class Action:
    name: str
    fn: ActionFn
    doc: str = ""


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, name: str, fn: ActionFn, *, doc: str = "") -> None:
        self._actions[name] = Action(name=name, fn=fn, doc=doc)

    def get(self, name: str) -> Action | None:
        return self._actions.get(name)

    def names(self) -> list[str]:
        return sorted(self._actions.keys())


# Back-compat: older revs called this CommandRegistry.
CommandRegistry = ActionRegistry
