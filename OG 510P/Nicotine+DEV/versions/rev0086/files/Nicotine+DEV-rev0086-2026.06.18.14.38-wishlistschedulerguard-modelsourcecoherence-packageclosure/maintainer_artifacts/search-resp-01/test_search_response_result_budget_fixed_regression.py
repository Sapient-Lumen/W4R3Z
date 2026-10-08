"""
Fixed-behavior regression for SEARCH-RESP-PARSE-BUDGET-B / rev0042.

FileSearchResponse accepted public and private result lists should share one
parser count budget. Over-budget public counts should be rejected before the
full accepted body is inflated, over-budget private lists should not be
materialized, and small public/private responses should continue to parse.
"""
from __future__ import annotations

import zlib

import pytest

import pynicotine.slskmessages as slskmessages
from pynicotine.slskmessages import FileSearchResponse

TEST_RESULT_COUNT_CAP = 64
MAX_REASONABLE_ACCEPTED_OUTPUT = 64 * 1024


class CountingDecompressor:
    def __init__(self, inner, counter):
        self._inner = inner
        self._counter = counter

    def decompress(self, data, max_length=0):
        out = self._inner.decompress(data, max_length)
        self._counter["calls"].append(len(out))
        self._counter["total"] += len(out)
        return out

    @property
    def unconsumed_tail(self):
        return self._inner.unconsumed_tail


def _set_test_result_count_cap(monkeypatch):
    if hasattr(slskmessages, "MAX_SEARCH_RESPONSE_RESULT_COUNT"):
        monkeypatch.setattr(slskmessages, "MAX_SEARCH_RESPONSE_RESULT_COUNT", TEST_RESULT_COUNT_CAP)
    return TEST_RESULT_COUNT_CAP


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


def _make_rows(prefix, count, name_len=16):
    stem = "x" * name_len
    return [(f"{prefix}\\{stem}_{index:05d}.flac", 1000 + index, None, None) for index in range(count)]


def _make_payload(token, public_count=0, private_count=0, name_len=16):
    msg = FileSearchResponse(
        search_username="requester",
        token=token,
        shares=_make_rows("Public", public_count, name_len=name_len),
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
        private_shares=_make_rows("Private", private_count, name_len=name_len),
    )
    return msg.make_network_message()


@pytest.fixture
def decompress_counter(monkeypatch):
    counter = {"calls": [], "total": 0}
    real_decompressobj = zlib.decompressobj

    def factory():
        return CountingDecompressor(real_decompressobj(), counter)

    monkeypatch.setattr(slskmessages.zlib, "decompressobj", factory)
    return counter


def _is_rejected(msg):
    return getattr(msg, "token", None) is None or getattr(msg, "list", None) in (None, [])


def test_public_result_count_over_cap_is_rejected_before_full_body_inflate(decompress_counter, monkeypatch):
    cap = _set_test_result_count_cap(monkeypatch)
    token = 0x420001
    payload = _make_payload(token, public_count=cap + 1, private_count=0, name_len=2048)

    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert _is_rejected(msg)
    assert len(getattr(msg, "list", None) or []) != cap + 1
    assert decompress_counter["total"] < MAX_REASONABLE_ACCEPTED_OUTPUT
    assert max(decompress_counter["calls"] or [0]) < MAX_REASONABLE_ACCEPTED_OUTPUT


def test_private_result_count_over_remaining_budget_is_not_materialized(monkeypatch):
    cap = _set_test_result_count_cap(monkeypatch)
    token = 0x420002
    payload = _make_payload(token, public_count=0, private_count=cap + 1, name_len=128)

    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert _is_rejected(msg)
    assert len(getattr(msg, "privatelist", None) or []) != cap + 1


def test_public_and_private_lists_share_one_total_result_budget(monkeypatch):
    cap = _set_test_result_count_cap(monkeypatch)
    token = 0x420003
    payload = _make_payload(token, public_count=cap, private_count=1, name_len=8)

    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert _is_rejected(msg)
    assert not getattr(msg, "privatelist", None)


def test_normal_public_and_private_search_response_still_parses():
    token = 0x420004
    payload = _make_payload(token, public_count=3, private_count=2, name_len=12)

    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert msg.token == token
    assert len(msg.list or []) == 3
    assert len(msg.privatelist or []) == 2
    assert msg.freeulslots is True
