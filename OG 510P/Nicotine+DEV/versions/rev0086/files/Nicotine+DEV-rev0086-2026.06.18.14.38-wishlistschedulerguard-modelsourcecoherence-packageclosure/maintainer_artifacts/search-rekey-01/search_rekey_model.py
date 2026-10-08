"""Bounded model for same-page Search Again token rekeying.

This is research scaffolding, not upstream implementation code.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SearchRecord:
    token: int
    mode: str = "global"
    room: str | None = None
    users: tuple[str, ...] = ()
    ignored_users: set[str] = field(default_factory=set)


@dataclass
class Page:
    token: int
    cap: int
    results: dict[str, str] = field(default_factory=dict)
    selected_users: set[str] = field(default_factory=set)
    selected_results: set[int] = field(default_factory=set)
    filters: dict[str, str] = field(default_factory=dict)
    grouping: str = "folder_grouping"
    sort: tuple[str, str] = ("id", "ascending")
    tab_index: int = 0
    focused: bool = True
    unread: bool = False

    def reset_epoch(self, new_token: int) -> None:
        self.token = new_token
        self.results.clear()
        self.selected_users.clear()
        self.selected_results.clear()
        self.unread = False


@dataclass(frozen=True)
class Request:
    token: int
    recipient: str


class SearchRepeatSystem:
    """Small state machine for the token, page, and result owners."""

    def __init__(self, *, token: int = 100, mode: str = "global", cap: int = 3) -> None:
        search = SearchRecord(token=token, mode=mode)
        page = Page(token=token, cap=cap)
        self.token = token
        self.searches = {token: search}
        self.pages = {token: page}
        self.allowed_tokens = {token}
        self.own_tokens: set[int] = set()
        self.requests: list[Request] = []
        self.history_writes = 1
        self.plugin_runs = 1
        self.recently_closed: list[int] = []

    @property
    def search(self) -> SearchRecord:
        return self.searches[self.token]

    @property
    def page(self) -> Page:
        return self.pages[self.token]

    def seed_results(self, *users: str) -> None:
        for user in users:
            if len(self.page.results) >= self.page.cap:
                raise ValueError("seed exceeds cap")
            self.page.results[user] = f"seed:{user}"

    def _send(self, recipients: tuple[str, ...]) -> None:
        self.allowed_tokens.add(self.token)
        self.requests.extend(Request(self.token, recipient) for recipient in recipients)

    def current_search_again(self, recipients: tuple[str, ...] = ("server",)) -> None:
        """Model current same-token Retry/Merge behavior."""
        self._send(recipients)

    def rekey_same_page(
        self,
        recipients: tuple[str, ...] = ("server",),
        *,
        online: bool = True,
    ) -> int | None:
        """Rotate ordinary search epochs; retain current wishlist retry policy."""
        if not online:
            return None

        search = self.search
        if search.mode == "wishlist":
            self._send(recipients)
            return self.token

        old_token = self.token
        old_page = self.page
        old_search = search
        old_page_order = tuple(self.pages)

        self.allowed_tokens.discard(old_token)
        self.own_tokens.discard(old_token)
        self.token += 1

        del self.searches[old_token]
        old_search.token = self.token
        self.searches[self.token] = old_search

        old_page.reset_epoch(self.token)
        remapped = [
            (self.token if token == old_token else token, page)
            for token, page in self.pages.items()
        ]
        self.pages.clear()
        self.pages.update(remapped)
        assert len(old_page_order) == len(self.pages)

        self._send(recipients)
        return self.token

    def accept_response(self, token: int, user: str) -> str:
        if token not in self.allowed_tokens:
            return "rejected-token"
        page = self.pages.get(token)
        if page is None:
            return "rejected-owner"
        if len(page.results) >= page.cap:
            self.allowed_tokens.discard(token)
            return "retired-at-cap"
        if user in page.results:
            return "duplicate-user"
        page.results[user] = f"fresh:{user}"
        return "accepted"
