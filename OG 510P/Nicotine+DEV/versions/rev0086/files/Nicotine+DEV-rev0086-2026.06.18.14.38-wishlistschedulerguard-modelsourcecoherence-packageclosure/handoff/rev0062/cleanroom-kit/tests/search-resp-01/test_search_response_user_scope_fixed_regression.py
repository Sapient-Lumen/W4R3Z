"""
Fixed-behavior regression for SEARCH-RESP-01A user-scoped search response admission.

Run from a Nicotine+ checkout with:
    PYTHONPATH=/path/to/nicotine-plus pytest -q test_search_response_user_scope_fixed_regression_rev0039.py

The assertions describe desired fixed behavior for the narrow, production-ready
sub-invariant: user-scoped searches should only accept FileSearchResponse rows
from the requested user(s). Broad modes remain broad-source compatible.
"""
from __future__ import annotations

from types import SimpleNamespace

import pynicotine.search as search_mod
import pynicotine.slskmessages as slskmessages
from pynicotine.search import Search, SearchRequest


class DummyNetworkFilter:
    def is_user_ignored(self, username):
        return False

    def is_user_ip_ignored(self, username, ip_address):
        return False

    def get_country_code(self, ip_address):
        return None


def _install_dummy_network_filter():
    search_mod.core.network_filter = DummyNetworkFilter()


def _allow_token_for_legacy_handler(token):
    allowed = getattr(slskmessages, "SEARCH_TOKENS_ALLOWED", None)
    if allowed is not None:
        allowed.clear()
        allowed.add(token)


def _make_search_request(token, mode, room=None, users=None, is_ignored=False):
    kwargs = dict(
        token=token,
        term="rareprobe",
        term_sanitized="rareprobe",
        term_transmitted="rareprobe",
        included_words=["rareprobe"],
        excluded_words=[],
        mode=mode,
        room=room,
        users=users,
    )
    try:
        return SearchRequest(**kwargs, is_ignored=is_ignored)
    except TypeError:
        return SearchRequest(**kwargs)


def _msg(token, username):
    return SimpleNamespace(
        token=token,
        username=username,
        addr=("203.0.113.90", 4999),
        list=[(1, "rareprobe\\spoof.flac", 1234, None, [])],
        privatelist=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
    )


def _dispatch(search, msg):
    _install_dummy_network_filter()
    _allow_token_for_legacy_handler(search.token)
    fake_search_component = SimpleNamespace(searches={search.token: search})
    Search._file_search_response(fake_search_component, msg)
    return msg


def test_user_scoped_response_from_unrequested_peer_is_rejected():
    token = 510001
    search = _make_search_request(token, mode="user", users=["expected_peer"])
    msg = _msg(token, username="unexpected_peer")
    _dispatch(search, msg)
    assert msg.token is None


def test_user_scoped_response_from_requested_peer_is_preserved():
    token = 510002
    search = _make_search_request(token, mode="user", users=["expected_peer"])
    msg = _msg(token, username="expected_peer")
    _dispatch(search, msg)
    assert msg.token == token


def test_user_scoped_response_from_any_requested_peer_is_preserved():
    token = 510003
    search = _make_search_request(token, mode="user", users=["peer_a", "peer_b"])
    msg = _msg(token, username="peer_b")
    _dispatch(search, msg)
    assert msg.token == token


def test_user_scoped_response_without_expected_users_is_rejected_closed():
    token = 510004
    search = _make_search_request(token, mode="user", users=[])
    msg = _msg(token, username="unexpected_peer")
    _dispatch(search, msg)
    assert msg.token is None


def test_global_search_response_remains_broad_source_compatible():
    token = 510005
    search = _make_search_request(token, mode="global")
    msg = _msg(token, username="any_peer")
    _dispatch(search, msg)
    assert msg.token == token


def test_room_search_response_remains_broad_source_compatible():
    token = 510006
    search = _make_search_request(token, mode="rooms", room="room-alpha")
    msg = _msg(token, username="room_peer")
    _dispatch(search, msg)
    assert msg.token == token


def test_buddy_search_response_remains_broad_source_compatible():
    token = 510007
    search = _make_search_request(token, mode="buddies")
    msg = _msg(token, username="buddy_peer")
    _dispatch(search, msg)
    assert msg.token == token
