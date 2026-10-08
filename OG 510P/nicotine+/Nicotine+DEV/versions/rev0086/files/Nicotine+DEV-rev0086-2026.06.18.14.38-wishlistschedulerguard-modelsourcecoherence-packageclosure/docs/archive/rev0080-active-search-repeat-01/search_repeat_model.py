"""Executable research model for Nicotine+ Search Again policies.

The model intentionally separates four meanings that had been conflated in the
cube: retry/merge, clear-and-retry, fresh-token page replacement, and in-place
fresh-token migration.  It is not upstream implementation code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Request:
    token: int
    recipient: str
    click: int


@dataclass(frozen=True)
class Response:
    token: int
    username: str
    payload: str
    originating_click: int | None = None


@dataclass
class Page:
    token: int
    cap: int
    results: dict[str, str] = field(default_factory=dict)
    view_state: dict[str, str] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return len(self.results)


@dataclass
class SearchRepeatSystem:
    """Small state machine matching the relevant current GUI/core behavior."""

    token: int = 100
    cap: int = 3
    page: Page = field(init=False)
    allowed_tokens: set[int] = field(default_factory=set)
    requests: list[Request] = field(default_factory=list)
    click: int = 0
    next_token: int = 100
    lifecycle: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.page = Page(token=self.token, cap=self.cap)
        self.allowed_tokens.add(self.token)
        self.next_token = max(self.next_token, self.token)

    def seed_results(self, usernames: Iterable[str]) -> None:
        for username in usernames:
            if self.page.count >= self.page.cap:
                raise ValueError("seed exceeds page cap")
            self.page.results[username] = f"seed:{username}"

    def _emit(self, token: int, recipients: Iterable[str]) -> int:
        self.click += 1
        recipient_tuple = tuple(recipients)
        self.requests.extend(Request(token, recipient, self.click) for recipient in recipient_tuple)
        return len(recipient_tuple)

    def search_again_current(self, recipients: Iterable[str]) -> int:
        """Current same-token Retry/Merge behavior."""
        self.allowed_tokens.add(self.page.token)
        self.lifecycle.append(f"retry:{self.page.token}")
        return self._emit(self.page.token, recipients)

    def receive(self, response: Response) -> str:
        """Apply the relevant dispatcher cap gate and page username gate."""
        if response.token not in self.allowed_tokens:
            return "rejected-token"

        # Searches.file_search_response() retires admission before handing the
        # message to the page once the stored-result count is already at cap.
        if self.page.count >= self.page.cap:
            self.allowed_tokens.discard(response.token)
            self.lifecycle.append(f"cap-retired:{response.token}")
            return "cap-retired"

        # Search.file_search_response() accepts at most one response per user.
        if response.username in self.page.results:
            return "ignored-existing-user"

        self.page.results[response.username] = response.payload
        return "accepted"

    def clear_same_token(self, recipients: Iterable[str]) -> int:
        """Historical manual-clear shape followed by same-token resend."""
        self.page.results.clear()
        self.allowed_tokens.add(self.page.token)
        self.lifecycle.append(f"clear-same-token:{self.page.token}")
        return self._emit(self.page.token, recipients)

    def replace_page_fresh_token(
        self,
        recipients: Iterable[str],
        *,
        preserve_view_state: bool = False,
    ) -> tuple[int, int]:
        """Best-effort page recreation with a fresh wire token.

        This policy does not promise queue/network acknowledgement.  It defines
        Search Again as closing one request/page lifetime and starting another,
        just as a new search does today.  That narrower product contract avoids
        pretending a stable in-place page transaction is mandatory.
        """
        old_token = self.page.token
        old_view = dict(self.page.view_state)
        self.next_token += 1
        new_token = self.next_token

        self.allowed_tokens.discard(old_token)
        self.allowed_tokens.add(new_token)
        self.page = Page(token=new_token, cap=self.cap)
        if preserve_view_state:
            self.page.view_state = old_view
        self.lifecycle.append(f"replace:{old_token}->{new_token}")
        self._emit(new_token, recipients)
        return old_token, new_token


def policy_matrix() -> list[dict[str, str]]:
    """Human- and machine-readable policy comparison."""
    return [
        {
            "policy": "current same-token Retry/Merge",
            "cap_recovery": "no",
            "late_old_response_isolation": "no",
            "page_local_state": "preserved",
            "network_ack_required": "no",
            "principal_cost": "dead at cap; repeated-user responses suppressed",
        },
        {
            "policy": "clear then same-token retry",
            "cap_recovery": "yes",
            "late_old_response_isolation": "no",
            "page_local_state": "partly preserved",
            "network_ack_required": "no",
            "principal_cost": "old and new same-token responses are indistinguishable",
        },
        {
            "policy": "fresh-token page replacement",
            "cap_recovery": "yes",
            "late_old_response_isolation": "yes",
            "page_local_state": "must be chosen/copied",
            "network_ack_required": "no for best-effort new-search semantics",
            "principal_cost": "tab/view/plugin/wishlist carry-over must be specified",
        },
        {
            "policy": "fresh-token in-place transactional refresh",
            "cap_recovery": "yes",
            "late_old_response_isolation": "yes",
            "page_local_state": "preserved",
            "network_ack_required": "yes if failure-atomic visible commit is promised",
            "principal_cost": "cross-thread generation, fan-out, reconnect, and zero-result policy",
        },
    ]
