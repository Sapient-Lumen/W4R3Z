"""Research model for acknowledgement-gated search refresh epochs.

This is not an upstream implementation.  It separates queue acceptance,
network ownership, main-thread acknowledgement, socket serialization, and
remote response.  The distinction matters because no local acknowledgement can
prove delivery to a remote Soulseek peer.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterable, Literal


class RefreshRejected(RuntimeError):
    """Raised when a refresh cannot enter the network queue."""


class RefreshPending(RuntimeError):
    """Raised when a second refresh is rejected while one is pending."""


class SearchClosed(RuntimeError):
    """Raised when a logical search no longer exists."""


@dataclass(frozen=True)
class SearchRequestMessage:
    token: int
    destination: str
    term: str


@dataclass(frozen=True)
class EpochBatch:
    transaction_id: int
    logical_id: str
    generation: int
    old_token: int
    new_token: int
    requests: tuple[SearchRequestMessage, ...]


@dataclass(frozen=True)
class EpochCancel:
    transaction_id: int
    generation: int
    tokens: tuple[int, ...]


@dataclass(frozen=True)
class EpochApplied:
    transaction_id: int
    logical_id: str
    generation: int
    old_token: int
    new_token: int


@dataclass(frozen=True)
class EpochRejected:
    transaction_id: int
    logical_id: str
    generation: int
    reason: str


@dataclass(frozen=True)
class ServerDisconnected:
    generation: int


@dataclass(frozen=True)
class ResultEvent:
    generation: int
    token: int
    user: str
    payload: str


MainEvent = EpochApplied | EpochRejected | ServerDisconnected | ResultEvent
NetworkCommand = EpochBatch | EpochCancel


@dataclass
class NetworkPlane:
    """Network-thread state with explicit ownership and acknowledgement stages.

    A successful ``process_next_command`` owns every request before queuing the
    acknowledgement.  Ownership means that the networking subsystem has placed
    the request in a network-owned outgoing structure.  It does *not* mean the
    request was written to a socket or delivered remotely.
    """

    generation: int = 1
    queue_enabled: bool = True
    authenticated: bool = True
    allowed_tokens: set[int] = field(default_factory=set)
    commands: deque[NetworkCommand] = field(default_factory=deque)
    owned_requests: deque[SearchRequestMessage] = field(default_factory=deque)
    serialized_requests: list[SearchRequestMessage] = field(default_factory=list)
    pack_failures: set[str] = field(default_factory=set)
    operation_log: list[tuple[str, int]] = field(default_factory=list)

    def try_enqueue(self, command: NetworkCommand) -> bool:
        if not self.queue_enabled:
            return False
        self.commands.append(command)
        return True

    def _batch_rejection(self, batch: EpochBatch) -> str | None:
        if batch.generation != self.generation:
            return "stale-generation"
        if not self.queue_enabled:
            return "queue-disabled"
        if not self.authenticated:
            return "not-authenticated"
        if not batch.requests:
            return "empty-request-set"
        if any(request.token != batch.new_token for request in batch.requests):
            return "request-token-mismatch"
        destinations = [request.destination for request in batch.requests]
        if any(not destination for destination in destinations):
            return "empty-destination"
        if len(destinations) != len(set(destinations)):
            return "duplicate-destination"
        if any(destination in self.pack_failures for destination in destinations):
            return "request-pack-failed"
        return None

    def process_next_command(self, main_events: deque[MainEvent]) -> str:
        """Apply one command, acknowledging only after request ownership."""
        if not self.commands:
            return "empty"

        command = self.commands.popleft()
        if isinstance(command, EpochCancel):
            if command.generation == self.generation:
                retired = set(command.tokens)
                self.allowed_tokens.difference_update(retired)
                self.owned_requests = deque(
                    request for request in self.owned_requests
                    if request.token not in retired
                )
                for token in command.tokens:
                    self.operation_log.append(("cancel", token))
            return "cancelled"

        rejection = self._batch_rejection(command)
        if rejection is not None:
            main_events.append(EpochRejected(
                command.transaction_id,
                command.logical_id,
                command.generation,
                rejection,
            ))
            self.operation_log.append(("reject", command.new_token))
            return "rejected"

        self.allowed_tokens.discard(command.old_token)
        self.operation_log.append(("remove", command.old_token))
        self.allowed_tokens.add(command.new_token)
        self.operation_log.append(("add", command.new_token))

        # This is the failure-atomic local handoff point used by the model.
        # Validation above represents pre-packing every request. The abstract
        # owned queue represents bytes appended to network-owned output state.
        # Every fan-out member is staged before the acknowledgement is visible
        # to main.
        self.owned_requests.extend(command.requests)
        for request in command.requests:
            self.operation_log.append(("own", request.token))

        main_events.append(EpochApplied(
            command.transaction_id,
            command.logical_id,
            command.generation,
            command.old_token,
            command.new_token,
        ))
        self.operation_log.append(("ack", command.new_token))
        return "applied"

    def process_next_command_ack_first(
        self,
        main_events: deque[MainEvent],
        *,
        disconnect_before_ownership: bool = False,
    ) -> str:
        """Countermodel of the rev0078 acknowledgement-before-request sketch."""
        if not self.commands:
            return "empty"
        command = self.commands.popleft()
        if not isinstance(command, EpochBatch):
            raise TypeError("ack-first countermodel accepts only EpochBatch")

        rejection = self._batch_rejection(command)
        if rejection is not None:
            main_events.append(EpochRejected(
                command.transaction_id,
                command.logical_id,
                command.generation,
                rejection,
            ))
            return "rejected"

        self.allowed_tokens.discard(command.old_token)
        self.allowed_tokens.add(command.new_token)
        main_events.append(EpochApplied(
            command.transaction_id,
            command.logical_id,
            command.generation,
            command.old_token,
            command.new_token,
        ))
        self.operation_log.append(("ack", command.new_token))

        if disconnect_before_ownership:
            self.disconnect(main_events)
            return "acknowledged-then-lost"

        self.owned_requests.extend(command.requests)
        for request in command.requests:
            self.operation_log.append(("own", request.token))
        return "applied"

    def process_next_command_partial_ownership(
        self,
        main_events: deque[MainEvent],
        *,
        owned_count: int,
    ) -> str:
        """Countermodel that acknowledges after owning only part of a fan-out."""
        if not self.commands:
            return "empty"
        command = self.commands.popleft()
        if not isinstance(command, EpochBatch):
            raise TypeError("partial-ownership countermodel accepts only EpochBatch")

        rejection = self._batch_rejection(command)
        if rejection is not None:
            main_events.append(EpochRejected(
                command.transaction_id,
                command.logical_id,
                command.generation,
                rejection,
            ))
            return "rejected"
        if owned_count < 0 or owned_count > len(command.requests):
            raise ValueError("owned_count outside request set")

        self.allowed_tokens.discard(command.old_token)
        self.allowed_tokens.add(command.new_token)
        self.owned_requests.extend(command.requests[:owned_count])
        for request in command.requests[:owned_count]:
            self.operation_log.append(("own", request.token))
        main_events.append(EpochApplied(
            command.transaction_id,
            command.logical_id,
            command.generation,
            command.old_token,
            command.new_token,
        ))
        self.operation_log.append(("ack", command.new_token))
        return "partially-applied"

    def serialize_next_request(self) -> SearchRequestMessage | None:
        """Move one output-buffer-owned request to the modeled socket write."""
        if not self.owned_requests or not self.queue_enabled:
            return None
        request = self.owned_requests.popleft()
        self.serialized_requests.append(request)
        self.operation_log.append(("serialize", request.token))
        return request

    def receive_result(
        self,
        main_events: deque[MainEvent],
        *,
        token: int,
        user: str,
        payload: str,
    ) -> str:
        if token not in self.allowed_tokens:
            return "rejected-network"
        main_events.append(ResultEvent(self.generation, token, user, payload))
        self.operation_log.append(("result", token))
        return "queued-main"

    def disconnect(self, main_events: deque[MainEvent]) -> None:
        """Clear queue, admissions, and unsent network-owned work."""
        disconnected_generation = self.generation
        self.queue_enabled = False
        self.authenticated = False
        self.commands.clear()
        self.allowed_tokens.clear()
        self.owned_requests.clear()
        main_events.append(ServerDisconnected(disconnected_generation))
        self.operation_log.append(("disconnect", disconnected_generation))

    def reconnect(self) -> int:
        self.generation += 1
        self.queue_enabled = True
        self.authenticated = True
        return self.generation


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


@dataclass
class PendingEpoch:
    batch: EpochBatch
    old_results: dict[str, str]


@dataclass(frozen=True)
class RefreshOutcome:
    transaction_id: int
    logical_id: str
    old_token: int
    new_token: int
    generation: int
    recipients: tuple[str, ...]


@dataclass
class SearchEpochSystem:
    """Main-thread state with pending epochs and generation-tagged acks."""

    next_token: int = 100
    next_transaction_id: int = 0
    network: NetworkPlane = field(default_factory=NetworkPlane)
    searches: dict[str, LogicalSearch] = field(default_factory=dict)
    pages: dict[str, SearchPage] = field(default_factory=dict)
    token_routes: dict[int, str] = field(default_factory=dict)
    pending: dict[str, PendingEpoch] = field(default_factory=dict)
    main_events: deque[MainEvent] = field(default_factory=deque)
    completed_transactions: set[int] = field(default_factory=set)
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
            logical_id,
            term,
            mode,
            token,
            recipient_tuple,
        )
        self.pages[logical_id] = SearchPage(logical_id, token)
        self.token_routes[token] = logical_id
        self.network.allowed_tokens.add(token)

    def _allocate_token(self) -> int:
        self.next_token += 1
        return self.next_token

    def _allocate_transaction(self) -> int:
        self.next_transaction_id += 1
        return self.next_transaction_id

    @staticmethod
    def _recipients(
        search: LogicalSearch,
        *,
        live_buddies: Iterable[str],
        buddy_policy: Literal["live-at-epoch", "original-request"],
    ) -> tuple[str, ...]:
        if search.mode != "buddies":
            return search.original_recipients
        if buddy_policy == "live-at-epoch":
            return tuple(live_buddies)
        if buddy_policy == "original-request":
            return search.original_recipients
        raise ValueError(f"unknown buddy policy: {buddy_policy}")

    def begin_refresh(
        self,
        logical_id: str,
        *,
        live_buddies: Iterable[str] = (),
        buddy_policy: Literal["live-at-epoch", "original-request"] = "live-at-epoch",
    ) -> RefreshOutcome:
        search = self.searches.get(logical_id)
        page = self.pages.get(logical_id)
        if search is None or page is None:
            raise SearchClosed(logical_id)
        if logical_id in self.pending:
            raise RefreshPending(logical_id)

        old_token = search.current_token
        new_token = self._allocate_token()
        transaction_id = self._allocate_transaction()
        recipients = self._recipients(
            search,
            live_buddies=live_buddies,
            buddy_policy=buddy_policy,
        )
        if search.mode in {"global", "wishlist"}:
            destinations = ("server:global",)
        elif search.mode == "rooms":
            destinations = recipients or ("server:room",)
        else:
            destinations = recipients

        requests = tuple(
            SearchRequestMessage(new_token, destination, search.term)
            for destination in destinations
        )
        batch = EpochBatch(
            transaction_id,
            logical_id,
            self.network.generation,
            old_token,
            new_token,
            requests,
        )
        pending = PendingEpoch(batch, dict(page.results))

        # Both routes exist while pending.  The old route keeps the visible page
        # live; the new route is armed for the ack-before-result FIFO contract.
        self.token_routes[new_token] = logical_id
        self.pending[logical_id] = pending
        if not self.network.try_enqueue(batch):
            self.pending.pop(logical_id, None)
            self.token_routes.pop(new_token, None)
            raise RefreshRejected("network-enqueue-rejected")

        self.lifecycle_log.append(f"pending:{transaction_id}")
        return RefreshOutcome(
            transaction_id,
            logical_id,
            old_token,
            new_token,
            batch.generation,
            recipients,
        )

    def close_search(self, logical_id: str) -> None:
        pending = self.pending.pop(logical_id, None)
        search = self.searches.pop(logical_id, None)
        self.pages.pop(logical_id, None)
        routed_tokens = tuple(
            token for token, routed_id in self.token_routes.items()
            if routed_id == logical_id
        )
        for token in routed_tokens:
            self.token_routes.pop(token, None)

        if routed_tokens:
            generation = (
                pending.batch.generation if pending is not None
                else self.network.generation
            )
            transaction_id = (
                pending.batch.transaction_id if pending is not None else 0
            )
            self.network.try_enqueue(EpochCancel(
                transaction_id,
                generation,
                tuple(sorted(set(routed_tokens))),
            ))
        self.lifecycle_log.append(f"closed:{logical_id}")

    def _abort_pending(self, logical_id: str, reason: str) -> str:
        pending = self.pending.pop(logical_id, None)
        if pending is None:
            return "ignored-no-pending"
        self.token_routes.pop(pending.batch.new_token, None)
        self.lifecycle_log.append(
            f"aborted:{pending.batch.transaction_id}:{reason}"
        )
        return "aborted-pending"

    def _handle_applied(self, event: EpochApplied) -> str:
        if event.transaction_id in self.completed_transactions:
            return "ignored-duplicate-ack"
        pending = self.pending.get(event.logical_id)
        if pending is None:
            return "ignored-stale-ack"
        batch = pending.batch
        if (
            event.transaction_id != batch.transaction_id
            or event.generation != batch.generation
            or event.old_token != batch.old_token
            or event.new_token != batch.new_token
        ):
            return "ignored-mismatched-ack"

        search = self.searches.get(event.logical_id)
        page = self.pages.get(event.logical_id)
        if search is None or page is None:
            self.pending.pop(event.logical_id, None)
            self.token_routes.pop(event.new_token, None)
            return "ignored-closed-ack"

        search.current_token = event.new_token
        page.current_token = event.new_token
        page.results.clear()
        self.token_routes.pop(event.old_token, None)
        self.pending.pop(event.logical_id, None)
        self.completed_transactions.add(event.transaction_id)
        self.lifecycle_log.append(f"committed:{event.transaction_id}")
        return "committed"

    def _handle_rejected(self, event: EpochRejected) -> str:
        pending = self.pending.get(event.logical_id)
        if pending is None or pending.batch.transaction_id != event.transaction_id:
            return "ignored-stale-rejection"
        return self._abort_pending(event.logical_id, event.reason)

    def _handle_disconnect(self, event: ServerDisconnected) -> str:
        aborted = 0
        for logical_id, pending in tuple(self.pending.items()):
            if pending.batch.generation == event.generation:
                self._abort_pending(logical_id, "server-disconnect")
                aborted += 1
        self.lifecycle_log.append(f"disconnected:{event.generation}")
        return f"disconnect-aborted:{aborted}"

    def _handle_result(self, event: ResultEvent) -> str:
        logical_id = self.token_routes.get(event.token)
        if logical_id is None:
            return "rejected-core-route"
        search = self.searches.get(logical_id)
        page = self.pages.get(logical_id)
        if search is None or page is None:
            return "rejected-closed"

        pending = self.pending.get(logical_id)
        if pending is not None and event.token == pending.batch.new_token:
            # A correctly ordered network thread queues EpochApplied before any
            # result caused by the new request.  Seeing this state is a contract
            # violation, so fail closed rather than mutating old visible rows.
            return "rejected-result-before-ack"
        if event.token != search.current_token or event.token != page.current_token:
            return "rejected-stale-epoch"
        if event.user in page.results:
            return "ignored-existing-user"
        page.results[event.user] = event.payload
        return "accepted"

    def deliver_next_main_event(self) -> str:
        if not self.main_events:
            return "empty"
        event = self.main_events.popleft()
        if isinstance(event, EpochApplied):
            return self._handle_applied(event)
        if isinstance(event, EpochRejected):
            return self._handle_rejected(event)
        if isinstance(event, ServerDisconnected):
            return self._handle_disconnect(event)
        return self._handle_result(event)


def click_storm_fanout(
    clicks: int,
    recipients: int,
    *,
    policy: Literal["allow", "reject-while-pending", "coalesce-one-trailing"],
) -> tuple[int, int]:
    """Return (epochs, peer requests) for a bounded rapid-repeat policy model."""
    if clicks <= 0:
        return (0, 0)
    if policy == "allow":
        epochs = clicks
    elif policy == "reject-while-pending":
        epochs = 1
    elif policy == "coalesce-one-trailing":
        epochs = min(clicks, 2)
    else:  # pragma: no cover - defensive contract
        raise ValueError(policy)
    return (epochs, epochs * recipients)
