"""Small executable model for Search Again token-consumer ordering.

Research-only. This model intentionally represents only identities and ordering
that can be established from the current source; it is not a GTK substitute.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Page:
    token: int
    mode: str = "global"
    rows: int = 4


@dataclass
class Request:
    token: int
    mode: str = "global"


class SearchConsumerModel:
    def __init__(self, tokens=(10, 20, 30)):
        self.pages = OrderedDict((token, Page(token)) for token in tokens)
        self.requests = {token: Request(token) for token in tokens}
        self.allowed_tokens = set(tokens)
        self.own_tokens = {tokens[min(1, len(tokens) - 1)]} if tokens else set()
        self.sent_tokens: list[int] = []
        self.trace: list[str] = []

    def _gui_rekey(self, old_token: int, new_token: int) -> None:
        page = self.pages[old_token]
        self.pages = OrderedDict(
            (new_token if token == old_token else token, value)
            for token, value in self.pages.items()
        )
        page.token = new_token
        page.rows = 0
        self.trace.append("gui-rekey")

    def repeat(self, old_token: int, new_token: int) -> int | None:
        request = self.requests.get(old_token)
        if request is None or request.mode == "wishlist":
            return None

        self.allowed_tokens.discard(old_token)
        self.own_tokens.discard(old_token)
        del self.requests[old_token]
        request.token = new_token
        self.requests[new_token] = request
        self.trace.append("core-rekey")

        # The source event emitter is synchronous. GUI identity changes before
        # a request carrying the new token can be emitted.
        self._gui_rekey(old_token, new_token)
        self.allowed_tokens.add(new_token)
        self.sent_tokens.append(new_token)
        self.trace.append("send")
        return new_token

    def accept_response(self, token: int) -> bool:
        return token in self.allowed_tokens and token in self.requests and token in self.pages

    def close(self, token: int) -> None:
        self.allowed_tokens.discard(token)
        self.requests.pop(token, None)
        self.pages.pop(token, None)

    def restore_args(self, token: int) -> tuple[str, str, str | None, tuple[str, ...]]:
        page = self.pages[token]
        return ("term", page.mode, None, ())
