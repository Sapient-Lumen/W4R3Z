"""Bounded model for Search Again ownership at the wishlist-mode boundary.

Research scaffolding only.  It distinguishes request provenance from GUI mode
because a manually launched wishlist query is a ``SearchRequest`` while its page
still owns wishlist-mode filters and token-addressed notifications.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SearchRecord:
    token: int
    mode: str
    request_kind: str
    ignored_users: set[str] = field(default_factory=set)


@dataclass
class SearchPage:
    token: int
    mode: str
    rows: list[str] = field(default_factory=list)
    notification_tokens: list[int] = field(default_factory=list)


class SearchAgainOwnershipModel:
    """Model the current retry and proposed non-wishlist rekey boundaries."""

    def __init__(self, *, mode: str, request_kind: str, token: int = 40) -> None:
        self.token = token
        self.searches = {token: SearchRecord(token, mode, request_kind)}
        self.pages = {token: SearchPage(token, mode)}
        self.allowed_tokens = {token}
        self.sent_tokens: list[int] = []
        self.trace: list[str] = []

    @property
    def search(self) -> SearchRecord:
        return self.searches[self.token]

    @property
    def page(self) -> SearchPage:
        return self.pages[self.token]

    def notify(self) -> int | None:
        if self.page.mode != "wishlist":
            return None
        self.page.notification_tokens.append(self.token)
        return self.token

    def activate_notification(self, token: int) -> str:
        return "opened" if token in self.pages else "stale-target"

    def _send(self, token: int) -> None:
        self.allowed_tokens.add(token)
        self.sent_tokens.append(token)
        self.trace.append("send")

    def repeat_mode_owned(self) -> int:
        """Central candidate: only non-wishlist page modes rotate tokens."""
        search = self.search
        if search.mode == "wishlist":
            self.trace.append("wishlist-retry")
            self._send(self.token)
            return self.token

        old_token = self.token
        self.allowed_tokens.discard(old_token)
        self.token += 1
        search.token = self.token
        page = self.pages.pop(old_token)
        page.token = self.token
        page.rows.clear()
        self.searches = {self.token: search}
        self.pages[self.token] = page
        self.trace.extend(("core-rekey", "gui-rekey"))
        self._send(self.token)
        return self.token

    def repeat_type_only(self) -> int:
        """Counterexample policy from the superseded core guard."""
        if self.search.request_kind == "WishSearchRequest":
            self._send(self.token)
            return self.token

        old_token = self.token
        self.allowed_tokens.discard(old_token)
        self.token += 1
        search = self.searches.pop(old_token)
        page = self.pages.pop(old_token)
        search.token = page.token = self.token
        page.rows.clear()
        self.searches[self.token] = search
        self.pages[self.token] = page
        self._send(self.token)
        return self.token
