"""Small executable model of persistent wishlist result-page ownership.

This is research scaffolding, not Nicotine+ contribution material.  It models
only the state transitions needed to distinguish a persistent wishlist inbox
from a page-owned manual search.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Delivery:
    outcome: str
    added: int = 0


@dataclass
class ManualPage:
    """Independent page created by the wishlist dialog's Search for Item."""

    token: int
    mode: str = "wishlist"
    request_class: str = "SearchRequest"
    rows: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class PersistentWishInbox:
    """Model the scheduled WishSearchRequest and its transient result batch."""

    token: int = 100
    max_results: int = 3
    auto_search: bool = True
    is_ignored: bool = True
    allowed: bool = False
    page_open: bool = False
    ignored_users: set[str] = field(default_factory=set)
    rows: list[tuple[str, str]] = field(default_factory=list)
    page_users: set[str] = field(default_factory=set)
    scheduled_requests: int = 0
    manual_same_token_requests: int = 0
    parser_drops: int = 0
    core_drops: int = 0
    duplicate_user_drops: int = 0
    cap_drops: int = 0

    @property
    def num_results(self) -> int:
        return len(self.rows)

    @property
    def at_capacity(self) -> bool:
        return self.num_results >= self.max_results

    def dispatch_selected_request(self) -> bool:
        """Model delivery after the outer scheduler has selected this request.

        Eligibility and collection rotation belong to WISHLIST-SCHED-01.  This
        downstream model deliberately accepts a disabled request so current
        source's failed-eligibility fallback remains observable instead of
        being silently corrected inside the model.
        """
        self.is_ignored = False
        self.allowed = True
        self.scheduled_requests += 1
        return True

    def current_search_again(self) -> bool:
        """Model the inherited tab action: same-token ordinary FileSearch."""
        self.allowed = True
        self.manual_same_token_requests += 1
        return True

    @staticmethod
    def candidate_search_again_available() -> bool:
        """The rev0085 candidate removes this action from persistent pages."""
        return False

    def search_for_item(self, token: int) -> ManualPage:
        """Create an independent manual SearchRequest page."""
        return ManualPage(token=token)

    def receive(self, username: str, files: list[str]) -> Delivery:
        """Pass one response through parser, core and GUI ownership checks."""
        if not self.allowed:
            self.parser_drops += 1
            return Delivery("parser-denied")
        if self.is_ignored or username in self.ignored_users:
            self.core_drops += 1
            return Delivery("core-ignored")

        if not self.page_open:
            self.page_open = True

        # Current GUI checks capacity before handing the whole peer response to
        # the page.  The first otherwise-admissible response at capacity also
        # revokes parser admission for the remaining responses in that epoch.
        if self.at_capacity:
            self.allowed = False
            self.cap_drops += 1
            return Delivery("capacity-drop")

        if username in self.page_users:
            self.duplicate_user_drops += 1
            return Delivery("page-user-dedup")

        self.page_users.add(username)
        self.rows.extend((username, file_path) for file_path in files)
        return Delivery("added", len(files))

    def mark_read(self) -> None:
        """Persist sender-level seen state for all currently visible senders."""
        self.ignored_users.update(self.page_users)

    def close_page(self) -> None:
        """Close one delivered batch without deleting the persistent wish."""
        self.page_open = False
        self.rows.clear()
        self.page_users.clear()
        self.is_ignored = True
        self.allowed = False

    def reset_seen_results(self) -> None:
        self.ignored_users.clear()
