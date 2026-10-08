"""Executable model for stable Search Again page and notification identity.

This model deliberately excludes GTK widgets and network delivery.  It isolates
ownership rules that must hold before native UI validation is meaningful:
wire tokens may rotate, logical page IDs may not, persistent wishlist requests
retain Retry semantics, notifications are replaceable, and closed-page actions
cannot resolve to a later page.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Callable


class SearchKind(str, Enum):
    ORDINARY = "ordinary"
    MANUAL_WISHLIST = "manual-wishlist"
    PERSISTENT_WISHLIST = "persistent-wishlist"


@dataclass
class Page:
    token: int
    page_id: str
    kind: SearchKind
    rows: list[str] = field(default_factory=list)
    seen_users: set[str] = field(default_factory=set)
    closed: bool = False


class NotificationStore:
    """Gio-like replace/withdraw semantics keyed by application notification ID."""

    def __init__(self) -> None:
        self.visible: dict[str, str] = {}
        self.withdrawn: list[str] = []

    @staticmethod
    def notification_id(page_id: str) -> str:
        return f"search-{page_id}"

    def show(self, page_id: str) -> str:
        notification_id = self.notification_id(page_id)
        self.visible[notification_id] = page_id
        return notification_id

    def withdraw(self, page_id: str) -> None:
        notification_id = self.notification_id(page_id)
        self.visible.pop(notification_id, None)
        self.withdrawn.append(notification_id)


class WindowsBalloonStore:
    """Single-current-balloon model matching the existing Win32 tray implementation."""

    def __init__(self) -> None:
        self.current_action: tuple[str, str] | None = None
        self.withdrawals = 0

    def show(self, action: str, page_id: str) -> None:
        self.current_action = (action.removeprefix("app."), page_id)

    def withdraw(self, action: str, page_id: str) -> bool:
        expected = (action.removeprefix("app."), page_id)
        if self.current_action != expected:
            return False
        self.current_action = None
        self.withdrawals += 1
        return True


class SearchSession:
    def __init__(
        self,
        *,
        token_start: int = 100,
        page_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._next_token = token_start
        self._page_sequence = count(1)
        self._page_id_factory = page_id_factory or (
            lambda: f"session-page-{next(self._page_sequence)}"
        )
        self.by_token: dict[int, Page] = {}
        self.by_page_id: dict[str, Page] = {}
        self.notifications = NotificationStore()
        self.sent_tokens: list[int] = []

    def _new_token(self) -> int:
        self._next_token += 1
        return self._next_token

    def open_page(self, kind: SearchKind, rows: list[str] | None = None) -> Page:
        page = Page(
            token=self._new_token(),
            page_id=self._page_id_factory(),
            kind=kind,
            rows=list(rows or []),
        )
        if page.page_id in self.by_page_id:
            raise ValueError("page IDs must not be reused")
        self.by_token[page.token] = page
        self.by_page_id[page.page_id] = page
        return page

    def notify(self, page: Page) -> str:
        if page.closed:
            raise ValueError("closed pages cannot emit notifications")
        return self.notifications.show(page.page_id)

    def activate(self, page_id: str) -> Page | None:
        page = self.by_page_id.get(page_id)
        if page is None or page.closed:
            return None
        return page

    def repeat(self, page: Page, *, online: bool = True) -> int | None:
        if page.closed or not online:
            return None
        if page.kind is SearchKind.PERSISTENT_WISHLIST:
            self.sent_tokens.append(page.token)
            return page.token

        old_token = page.token
        new_token = self._new_token()
        del self.by_token[old_token]
        page.token = new_token
        page.rows.clear()
        page.seen_users.clear()
        self.by_token[new_token] = page
        self.sent_tokens.append(new_token)
        return new_token

    def close(self, page: Page) -> None:
        if page.closed:
            return
        page.closed = True
        self.by_token.pop(page.token, None)
        self.by_page_id.pop(page.page_id, None)
        self.notifications.withdraw(page.page_id)

    def shutdown(self) -> None:
        for page in tuple(self.by_page_id.values()):
            self.notifications.withdraw(page.page_id)
        self.by_page_id.clear()
        self.by_token.clear()
