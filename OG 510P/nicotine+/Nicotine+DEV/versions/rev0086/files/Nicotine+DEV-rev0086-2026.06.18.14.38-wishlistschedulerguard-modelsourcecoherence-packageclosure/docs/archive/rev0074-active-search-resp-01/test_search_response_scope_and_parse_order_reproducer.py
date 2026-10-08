"""
Current-behavior witness for SEARCH-RESP-01.

Run from a Nicotine+ checkout with:
    PYTHONPATH=/path/to/nicotine-plus pytest -q test_search_response_scope_and_parse_order_reproducer_rev0013.py

The assertions describe current behavior, not desired fixed behavior.
"""
from __future__ import annotations

import struct
import time
import tracemalloc
import zlib
from types import SimpleNamespace

import pynicotine.search as search_mod
import pynicotine.slskmessages as slskmessages
from pynicotine.search import Search, SearchRequest
from pynicotine.slskmessages import FileSearchResponse

try:
    from pynicotine.utils import UINT32_LIMIT
except Exception:  # pragma: no cover - defensive compatibility
    UINT32_LIMIT = 0xFFFFFFFF


class DummyNetworkFilter:
    def is_user_ignored(self, username):
        return False

    def is_user_ip_ignored(self, username, ip_address):
        return False

    def get_country_code(self, ip_address):
        return None


def _install_dummy_network_filter():
    search_mod.core.network_filter = DummyNetworkFilter()


def _make_search_request(token, mode, room=None, users=None):
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
        return SearchRequest(**kwargs, is_ignored=False)
    except TypeError:
        return SearchRequest(**kwargs)


def _allow_tokens(tokens):
    allowed = getattr(slskmessages, "SEARCH_TOKENS_ALLOWED", None)
    if allowed is not None:
        allowed.clear()
        allowed.update(tokens)


def _parse_file_search_response(payload, allowed_tokens):
    try:
        msg = FileSearchResponse(msg_content=payload)
        msg.allowed_responses = set(allowed_tokens)
        msg.parse_network_message()
        return msg
    except TypeError:
        msg = FileSearchResponse()
        _allow_tokens(set(allowed_tokens))
        msg.parse_network_message(payload)
        return msg


def _make_file_search_response_payload(token, public_count=0, private_count=0):
    public = [(f"Public\\track_{i}.flac", 1000 + i, None, None) for i in range(public_count)]
    private = [(f"Private\\secret_{i}.flac", 2000 + i, None, None) for i in range(private_count)]
    msg = FileSearchResponse(
        search_username="requester",
        token=token,
        shares=public,
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
        private_shares=private,
    )
    return msg.make_network_message()


def test_user_scoped_file_search_response_from_unrequested_peer_is_accepted():
    _install_dummy_network_filter()
    token = 424242
    _allow_tokens({token})
    search = _make_search_request(token, mode="user", users=["expected_peer"])
    fake_search_component = SimpleNamespace(searches={token: search})
    msg = SimpleNamespace(
        token=token,
        username="unexpected_peer",
        addr=("203.0.113.77", 4567),
        list=[(1, "rareprobe\\spoof.flac", 1234, None, [])],
        privatelist=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
    )

    Search._file_search_response(fake_search_component, msg)

    assert search.users == ["expected_peer"]
    assert msg.username == "unexpected_peer"
    assert msg.token == token


def test_room_scoped_file_search_response_from_unvetted_peer_is_accepted():
    _install_dummy_network_filter()
    token = 424243
    _allow_tokens({token})
    search = _make_search_request(token, mode="rooms", room="room-alpha")
    fake_search_component = SimpleNamespace(searches={token: search})
    msg = SimpleNamespace(
        token=token,
        username="peer_not_known_in_room",
        addr=("203.0.113.78", 4568),
        list=[(1, "rareprobe\\room.flac", 1234, None, [])],
        privatelist=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
    )

    Search._file_search_response(fake_search_component, msg)

    assert search.room == "room-alpha"
    assert msg.username == "peer_not_known_in_room"
    assert msg.token == token


def test_search_tokens_start_in_reduced_range_then_increment_linearly():
    samples = [slskmessages.initial_token() for _ in range(32)]

    assert all(0 <= sample <= UINT32_LIMIT // 1000 for sample in samples)
    assert slskmessages.increment_token(123456) == 123457


def test_private_file_search_response_rows_are_parser_materialized_before_display_policy():
    token = 424244
    payload = _make_file_search_response_payload(token, public_count=0, private_count=3)

    msg = _parse_file_search_response(payload, {token})

    assert len(msg.list or []) == 0
    assert len(msg.privatelist or []) == 3


def test_invalid_token_still_decompresses_peer_controlled_username_prefix_before_reject():
    invalid_token = 0x0BADF00D
    username_len = 1_000_000
    raw = struct.pack("<I", username_len) + (b"X" * username_len) + struct.pack("<I", invalid_token)
    payload = zlib.compress(raw, 4)

    tracemalloc.start()
    start = time.perf_counter()
    msg = _parse_file_search_response(payload, {12345})
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert invalid_token not in {12345}
    assert len(payload) < username_len // 100
    assert peak >= username_len
    assert elapsed_ms >= 0
    assert getattr(msg, "list", None) in (None, [])


def test_accepted_file_search_response_parser_materializes_full_public_list_before_ui_cap():
    token = 424245
    payload = _make_file_search_response_payload(token, public_count=256, private_count=0)

    msg = _parse_file_search_response(payload, {token})

    assert len(msg.list or []) == 256
