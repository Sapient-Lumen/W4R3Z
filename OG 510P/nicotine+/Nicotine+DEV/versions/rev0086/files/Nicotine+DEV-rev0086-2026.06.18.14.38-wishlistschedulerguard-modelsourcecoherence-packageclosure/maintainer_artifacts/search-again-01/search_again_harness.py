"""Shared research harness for Search Again token and epoch experiments.

This is cube-only research material, not upstream contribution content.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from pynicotine.search import Search, SearchRequest

LOCAL_USER = "local_user"
SEARCH_TOKEN = 700001
LATEST_TOKEN = 700099


def make_component(*, latest_token=LATEST_TOKEN, search_token=SEARCH_TOKEN, users=None):
    """Create the smallest real Search object needed by the request methods."""
    if users is None:
        users = [LOCAL_USER]

    component = object.__new__(Search)
    component.searches = {
        search_token: SearchRequest(
            token=search_token,
            term="rareprobe",
            term_sanitized="rareprobe",
            term_transmitted="rareprobe",
            included_words=["rareprobe"],
            excluded_words=[],
            mode="user",
            users=list(users),
        )
    }
    component.token = latest_token
    component._own_tokens = set()
    return component


def make_outgoing_core(server_messages, network_messages):
    return SimpleNamespace(
        users=SimpleNamespace(login_username=LOCAL_USER),
        send_message_to_server=server_messages.append,
        send_message_to_network_thread=network_messages.append,
    )


def make_incoming_core():
    return SimpleNamespace(
        users=SimpleNamespace(login_username=LOCAL_USER),
        uploads=SimpleNamespace(pending_shutdown=False),
    )


@dataclass
class EpochModel:
    """Small model separating wire-token admission from tab result policy."""

    current_token: int
    allowed_tokens: set[int] = field(default_factory=set)
    visible_users: dict[str, str] = field(default_factory=dict)

    def allow(self, token: int) -> None:
        self.allowed_tokens.add(token)

    def retire(self, token: int) -> None:
        self.allowed_tokens.discard(token)

    def clear_results(self) -> None:
        self.visible_users.clear()

    def receive(self, *, token: int, user: str, payload: str) -> str:
        if token not in self.allowed_tokens:
            return "rejected-token"
        if user in self.visible_users:
            return "ignored-existing-user"
        self.visible_users[user] = payload
        return "accepted"
