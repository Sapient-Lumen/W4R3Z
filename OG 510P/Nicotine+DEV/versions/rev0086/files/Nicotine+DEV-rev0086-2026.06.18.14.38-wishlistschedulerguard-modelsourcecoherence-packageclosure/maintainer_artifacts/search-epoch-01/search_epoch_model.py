"""Research model for stable search identity and replaceable wire epochs.

This is not an upstream implementation. It makes the cross-thread contract
explicit so counterexamples can be tested without pretending that three
ordinary queue calls are atomic.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Iterable


class RefreshError(RuntimeError):
    """Raised for an injected or enqueue failure."""


class SearchClosed(RuntimeError):
    """Raised when a refresh loses its logical page before the enqueue attempt."""


@dataclass(frozen=True)
class ResultEvent:
    token: int
    user: str
    payload: str


@dataclass(frozen=True)
class SearchRequestMessage:
    token: int
    recipients: tuple[str, ...]
    term: str


@dataclass(frozen=True)
class EpochBatch:
    old_token: int
    new_token: int
    requests: tuple[SearchRequestMessage, ...]


@dataclass
class NetworkPlane:
    """Network-thread admission and enqueue model.

    ``try_enqueue_epoch`` is deliberately stronger than Nicotine+'s current
    fire-and-forget queue event: it reports whether one composite epoch batch
    was accepted. Acceptance is not an applied acknowledgement; disconnect can
    still clear accepted work before processing.
    """

    queue_enabled: bool = True
    allowed_tokens: set[int] = field(default_factory=set)
    batches: deque[EpochBatch] = field(default_factory=deque)
    sent_requests: list[SearchRequestMessage] = field(default_factory=list)
    operation_log: list[tuple[str, int]] = field(default_factory=list)

    def try_enqueue_epoch(self, batch: EpochBatch) -> bool:
        if not self.queue_enabled:
            return False
        self.batches.append(batch)
        return True

    def disconnect_and_clear(self) -> None:
        """Model the server-disconnect queue and admission reset."""
        self.queue_enabled = False
        self.batches.clear()
        self.allowed_tokens.clear()

    def process_next_batch(self) -> EpochBatch | None:
        if not self.batches:
            return None
        batch = self.batches.popleft()
        self.allowed_tokens.discard(batch.old_token)
        self.operation_log.append(("remove", batch.old_token))
        self.allowed_tokens.add(batch.new_token)
        self.operation_log.append(("add", batch.new_token))
        for request in batch.requests:
            self.sent_requests.append(request)
            self.operation_log.append(("send", request.token))
        return batch

    def parse_result(self, event: ResultEvent, main_queue: deque[ResultEvent]) -> str:
        if event.token not in self.allowed_tokens:
            return "rejected-network"
        main_queue.append(event)
        return "queued-main"


@dataclass
class LogicalSearch:
    logical_id: str
    term: str
    mode: str
    current_token: int
    original_recipients: tuple[str, ...] = ()


@dataclass
class SearchPage:
    logical_id: str
    current_token: int
    results: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RefreshOutcome:
    logical_id: str
    old_token: int
    new_token: int
    recipients: tuple[str, ...]
    queue_accepted: bool


@dataclass
class SearchEpochSystem:
    """Main-thread model with stable logical IDs and token routes."""

    next_token: int = 100
    network: NetworkPlane = field(default_factory=NetworkPlane)
    searches: dict[str, LogicalSearch] = field(default_factory=dict)
    pages: dict[str, SearchPage] = field(default_factory=dict)
    token_routes: dict[int, str] = field(default_factory=dict)
    main_events: deque[ResultEvent] = field(default_factory=deque)
    notifications: list[tuple[str, str]] = field(default_factory=list)
    lifecycle_log: list[str] = field(default_factory=list)

    def open_search(
        self,
        logical_id: str,
        *,
        token: int,
        term: str = "query",
        mode: str = "global",
        recipients: Iterable[str] = (),
    ) -> None:
        recipient_tuple = tuple(recipients)
        self.next_token = max(self.next_token, token)
        self.searches[logical_id] = LogicalSearch(
            logical_id=logical_id,
            term=term,
            mode=mode,
            current_token=token,
            original_recipients=recipient_tuple,
        )
        self.pages[logical_id] = SearchPage(logical_id=logical_id, current_token=token)
        self.token_routes[token] = logical_id
        self.network.allowed_tokens.add(token)

    def close_search(self, logical_id: str) -> None:
        search = self.searches.pop(logical_id, None)
        self.pages.pop(logical_id, None)
        if search is None:
            return
        for token, routed_id in tuple(self.token_routes.items()):
            if routed_id == logical_id:
                del self.token_routes[token]
        self.network.allowed_tokens.discard(search.current_token)
        self.lifecycle_log.append(f"closed:{logical_id}")

    def notify(self, logical_id: str, text: str) -> str:
        if logical_id not in self.searches:
            return "ignored-closed"
        self.notifications.append((logical_id, text))
        return logical_id

    def activate_notification(self, logical_id: str) -> SearchPage | None:
        return self.pages.get(logical_id)

    def receive_at_network(self, *, token: int, user: str, payload: str) -> str:
        return self.network.parse_result(ResultEvent(token, user, payload), self.main_events)

    def deliver_next_main_event(self) -> str:
        if not self.main_events:
            return "empty"
        event = self.main_events.popleft()
        logical_id = self.token_routes.get(event.token)
        if logical_id is None:
            return "rejected-core-route"
        search = self.searches.get(logical_id)
        page = self.pages.get(logical_id)
        if search is None or page is None:
            return "rejected-closed"
        if search.current_token != event.token or page.current_token != event.token:
            return "rejected-stale-epoch"
        if event.user in page.results:
            return "ignored-existing-user"
        page.results[event.user] = event.payload
        return "accepted"

    def _allocate_token(self) -> int:
        self.next_token += 1
        return self.next_token

    def _recipients(
        self,
        search: LogicalSearch,
        *,
        live_buddies: Iterable[str],
        buddy_policy: str,
    ) -> tuple[str, ...]:
        if search.mode != "buddies":
            return search.original_recipients
        if buddy_policy == "live-at-epoch":
            return tuple(live_buddies)
        if buddy_policy == "original-request":
            return search.original_recipients
        raise ValueError(f"unknown buddy policy: {buddy_policy}")

    def refresh(
        self,
        logical_id: str,
        *,
        live_buddies: Iterable[str] = (),
        buddy_policy: str = "live-at-epoch",
        fail_at: str | None = None,
        close_at: str | None = None,
    ) -> RefreshOutcome:
        """Rotate one logical search to a fresh wire epoch.

        All reversible main-thread mutation occurs before the enqueue attempt. One
        composite network batch is then accepted or rejected synchronously. This
        models the minimum immediate rollback contract, not durable application:
        a later disconnect can still clear an accepted batch.
        """
        search = self.searches.get(logical_id)
        page = self.pages.get(logical_id)
        if search is None or page is None:
            raise SearchClosed(logical_id)

        old_token = search.current_token
        old_results = dict(page.results)
        old_page_token = page.current_token
        old_route = self.token_routes.get(old_token)
        new_token = self._allocate_token()
        recipients = self._recipients(
            search,
            live_buddies=live_buddies,
            buddy_policy=buddy_policy,
        )
        checkpoints = (
            "allocated",
            "new-route-installed",
            "current-token-switched",
            "old-route-retired",
            "results-cleared",
            "before-enqueue",
        )

        def checkpoint(name: str) -> None:
            self.lifecycle_log.append(name)
            if close_at == name:
                self.close_search(logical_id)
                raise SearchClosed(name)
            if fail_at == name:
                raise RefreshError(name)

        def rollback() -> None:
            if logical_id not in self.searches or logical_id not in self.pages:
                self.token_routes.pop(new_token, None)
                return
            restored_search = self.searches[logical_id]
            restored_page = self.pages[logical_id]
            restored_search.current_token = old_token
            restored_page.current_token = old_page_token
            restored_page.results = old_results
            self.token_routes.pop(new_token, None)
            if old_route is not None:
                self.token_routes[old_token] = old_route
            self.lifecycle_log.append("rolled-back")

        try:
            checkpoint(checkpoints[0])
            self.token_routes[new_token] = logical_id
            checkpoint(checkpoints[1])
            search.current_token = new_token
            page.current_token = new_token
            checkpoint(checkpoints[2])
            self.token_routes.pop(old_token, None)
            checkpoint(checkpoints[3])
            page.results.clear()
            checkpoint(checkpoints[4])
            checkpoint(checkpoints[5])

            request = SearchRequestMessage(new_token, recipients, search.term)
            batch = EpochBatch(old_token, new_token, (request,))
            if not self.network.try_enqueue_epoch(batch):
                raise RefreshError("network-enqueue-rejected")

        except SearchClosed:
            self.token_routes.pop(new_token, None)
            # The local transaction knows both epochs even after the old route
            # has been retired. Closure before the enqueue attempt must revoke both.
            self.network.allowed_tokens.discard(old_token)
            self.network.allowed_tokens.discard(new_token)
            raise
        except Exception:
            rollback()
            raise

        self.lifecycle_log.append("queue-accepted")
        return RefreshOutcome(logical_id, old_token, new_token, recipients, True)


@dataclass
class FireAndForgetQueue:
    """Countermodel of the current queue callback's silent-drop behavior."""

    enabled: bool
    items: list[object] = field(default_factory=list)

    def enqueue(self, item: object) -> None:
        if self.enabled:
            self.items.append(item)


def enqueue_three_ordinary_messages(
    queue: FireAndForgetQueue,
    *,
    old_token: int,
    new_token: int,
) -> None:
    queue.enqueue(("remove", old_token))
    queue.enqueue(("add", new_token))
    queue.enqueue(("send", new_token))
