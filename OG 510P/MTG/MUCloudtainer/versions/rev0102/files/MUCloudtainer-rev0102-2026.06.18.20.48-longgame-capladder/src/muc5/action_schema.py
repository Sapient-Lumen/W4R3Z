from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Action:
    """A legal macro-action emitted by the MUC-5 referee kernel.

    The neural policy should rank instances of this class, not invent arbitrary moves.
    """

    kind: str
    params: Dict[str, Any] = field(default_factory=dict)

    def compact(self) -> str:
        if not self.params:
            return self.kind
        args = ", ".join(f"{k}={v}" for k, v in sorted(self.params.items()))
        return f"{self.kind}({args})"


PASS = Action("PASS")
PLAY_ISLAND = Action("PLAY_ISLAND")


def cast(card_id: str, **params: Any) -> Action:
    p = {"card": card_id}
    p.update(params)
    return Action("CAST", p)


def activate_jace(mode: str, **params: Any) -> Action:
    p = {"mode": mode}
    p.update(params)
    return Action("ACTIVATE_JACE", p)


def choose(effect: str, **params: Any) -> Action:
    p = {"effect": effect}
    p.update(params)
    return Action("CHOOSE_FOR_EFFECT", p)
