"""Bounded model of wishlist scheduler rotation and eligibility.

Research scaffolding only. The model intentionally has separate current and
candidate policies so that source parity can be checked in both states.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Wish:
    term: str
    auto_search: bool
    is_ignored: bool = True


class WishlistScheduler:
    """Model ``Search._do_next_wishlist_search`` over insertion-ordered wishes."""

    def __init__(self, items: Iterable[tuple[str, bool]], *, require_enabled_dispatch: bool):
        self.wishlist = {
            term: Wish(term=term, auto_search=enabled)
            for term, enabled in items
        }
        self.require_enabled_dispatch = require_enabled_dispatch

    def tick(self) -> str | None:
        search: Wish | None = None
        inspected = 0

        while inspected < len(self.wishlist):
            term = next(iter(self.wishlist))
            search = self.wishlist.pop(term)
            self.wishlist[term] = search
            inspected += 1
            if search.auto_search:
                break

        should_dispatch = search is not None
        if self.require_enabled_dispatch:
            should_dispatch = should_dispatch and search.auto_search

        if not should_dispatch:
            return None

        search.is_ignored = False
        return search.term

    def snapshot(self) -> dict[str, object]:
        return {
            "order": list(self.wishlist),
            "ignored": {
                term: wish.is_ignored
                for term, wish in self.wishlist.items()
            },
        }


def run_scenario(
    items: list[tuple[str, bool]],
    ticks: int,
    *,
    require_enabled_dispatch: bool,
) -> dict[str, object]:
    scheduler = WishlistScheduler(
        items,
        require_enabled_dispatch=require_enabled_dispatch,
    )
    selected = [scheduler.tick() for _ in range(ticks)]
    return {"selected": selected, **scheduler.snapshot()}


SCENARIOS: dict[str, tuple[list[tuple[str, bool]], int]] = {
    "empty": ([], 1),
    "single_disabled": ([('disabled', False)], 1),
    "all_disabled": ([('a', False), ('b', False), ('c', False)], 4),
    "disabled_then_enabled": ([('off-a', False), ('on-b', True)], 2),
    "enabled_then_disabled": ([('on-a', True), ('off-b', False)], 2),
    "all_enabled": ([('a', True), ('b', True), ('c', True)], 6),
    "mixed": ([('off-a', False), ('on-b', True), ('off-c', False), ('on-d', True)], 4),
}


def run_matrix(*, candidate: bool) -> dict[str, dict[str, object]]:
    return {
        name: run_scenario(items, ticks, require_enabled_dispatch=candidate)
        for name, (items, ticks) in SCENARIOS.items()
    }
