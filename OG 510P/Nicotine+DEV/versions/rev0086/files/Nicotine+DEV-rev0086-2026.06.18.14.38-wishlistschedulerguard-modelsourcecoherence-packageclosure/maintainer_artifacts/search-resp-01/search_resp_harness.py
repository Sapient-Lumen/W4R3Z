"""Shared exact-current harness for SEARCH-RESP-01A research tests.

The helpers keep three facts separate: the search request's intended user set,
the username attached to a peer connection, and the token carried by a result.
"""
from __future__ import annotations

from types import SimpleNamespace

import pynicotine.search as search_mod
import pynicotine.slskmessages as slskmessages
from pynicotine.search import Search, SearchRequest
from pynicotine.slskmessages import FileSearchResponse, PeerInit
from pynicotine.slskproto import NetworkThread


class DummyNetworkFilter:
    def is_user_ignored(self, _username):
        return False

    def is_user_ip_ignored(self, _username, _ip_address):
        return False

    def get_country_code(self, _ip_address):
        return None


def allow_token(token: int) -> None:
    slskmessages.SEARCH_TOKENS_ALLOWED.clear()
    slskmessages.SEARCH_TOKENS_ALLOWED.add(token)


def make_search(token: int, *, mode: str = "user", users=None) -> SearchRequest:
    return SearchRequest(
        token=token,
        term="rareprobe",
        term_sanitized="rareprobe",
        term_transmitted="rareprobe",
        included_words=["rareprobe"],
        excluded_words=[],
        mode=mode,
        users=users,
        is_ignored=False,
    )


def make_message(token: int, username: str):
    return SimpleNamespace(
        token=token,
        username=username,
        addr=("203.0.113.90", 4999),
        list=[(1, "rareprobe\\result.flac", 1234, None, [])],
        privatelist=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
    )


def dispatch(search: SearchRequest, msg):
    search_mod.core.network_filter = DummyNetworkFilter()
    allow_token(search.token)
    component = SimpleNamespace(searches={search.token: search})
    Search._file_search_response(component, msg)
    return msg


def response_from_peerinit_claim(
    token: int,
    *,
    claimed_username: str,
    search_username: str = "requester",
):
    """Build a parsed response whose connection username came from wire PeerInit.

    No assertion is made here about who controls the socket. The point is that
    the value checked by the rev0039 guard is supplied by the unauthenticated
    PeerInit name, not by a server-bound response authorization.
    """
    init_wire = PeerInit(init_user=claimed_username, conn_type="P").make_network_message()
    init = NetworkThread._unpack_network_message(
        PeerInit,
        memoryview(init_wire),
        len(init_wire),
        conn_type="peer-init",
    )
    assert init is not None

    allow_token(token)
    payload = FileSearchResponse(
        search_username=search_username,
        token=token,
        shares=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
        private_shares=[],
    ).make_network_message()
    msg = NetworkThread._unpack_network_message(
        FileSearchResponse,
        memoryview(payload),
        len(payload),
        conn_type="peer",
        addr=("203.0.113.91", 5000),
        username=init.target_user,
    )
    assert msg is not None
    return init, msg
