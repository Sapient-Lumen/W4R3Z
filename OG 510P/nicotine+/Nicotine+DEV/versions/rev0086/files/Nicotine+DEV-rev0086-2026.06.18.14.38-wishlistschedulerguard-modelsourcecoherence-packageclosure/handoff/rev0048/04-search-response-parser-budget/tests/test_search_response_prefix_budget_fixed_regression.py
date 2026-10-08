"""
Fixed-behavior regression for SEARCH-RESP-PARSE-BUDGET-A / rev0041.

The assertions describe desired parser-budget behavior for FileSearchResponse:
read the compressed uint32 username length first, reject overlong username
prefixes before decompressing the peer-advertised prefix body, and preserve
normal accepted responses.
"""
from __future__ import annotations

import struct
import zlib

import pytest

import pynicotine.slskmessages as slskmessages
from pynicotine.slskmessages import FileSearchResponse

MAX_REASONABLE_PREFIX_OUTPUT = 64 * 1024


class CountingDecompressor:
    def __init__(self, inner, counter):
        self._inner = inner
        self._counter = counter

    def decompress(self, data, max_length=0):
        out = self._inner.decompress(data, max_length)
        self._counter['calls'].append(len(out))
        self._counter['total'] += len(out)
        return out

    @property
    def unconsumed_tail(self):
        return self._inner.unconsumed_tail


def _allow_tokens(tokens):
    allowed = getattr(slskmessages, 'SEARCH_TOKENS_ALLOWED', None)
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


def _make_minimal_prefix_payload(username_len, token):
    raw = bytearray()
    raw += struct.pack('<I', username_len)
    raw += b'X' * username_len
    raw += struct.pack('<I', token)
    raw += struct.pack('<I', 0)
    raw += struct.pack('?', True)
    raw += struct.pack('<I', 0)
    raw += struct.pack('<I', 0)
    raw += struct.pack('<I', 0)
    return zlib.compress(bytes(raw), 4)


def _make_normal_payload(token, search_username='requester'):
    msg = FileSearchResponse(
        search_username=search_username,
        token=token,
        shares=[],
        freeulslots=True,
        ulspeed=0,
        inqueue=0,
        private_shares=[],
    )
    return msg.make_network_message()


@pytest.fixture
def decompress_counter(monkeypatch):
    counter = {'calls': [], 'total': 0}
    real_decompressobj = zlib.decompressobj

    def factory():
        return CountingDecompressor(real_decompressobj(), counter)

    monkeypatch.setattr(slskmessages.zlib, 'decompressobj', factory)
    return counter


def test_invalid_token_overlong_username_prefix_is_rejected_before_materializing_prefix(decompress_counter):
    token = 0x0BADF00D
    payload = _make_minimal_prefix_payload(username_len=1_000_000, token=token)
    msg = _parse_file_search_response(payload, allowed_tokens={12345})

    assert token not in {12345}
    assert decompress_counter['total'] < MAX_REASONABLE_PREFIX_OUTPUT
    assert max(decompress_counter['calls'] or [0]) < MAX_REASONABLE_PREFIX_OUTPUT
    assert getattr(msg, 'list', None) in (None, [])


def test_valid_token_overlong_username_prefix_is_rejected_before_materializing_prefix(decompress_counter):
    token = 0x12345678
    payload = _make_minimal_prefix_payload(username_len=1_000_000, token=token)
    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert decompress_counter['total'] < MAX_REASONABLE_PREFIX_OUTPUT
    assert max(decompress_counter['calls'] or [0]) < MAX_REASONABLE_PREFIX_OUTPUT
    assert getattr(msg, 'list', None) in (None, [])


def test_normal_valid_search_response_still_parses():
    token = 0x12345679
    payload = _make_normal_payload(token)
    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert msg.token == token
    assert msg.list == []
    assert msg.freeulslots is True


def test_max_length_login_username_prefix_still_parses():
    token = 0x1234567A
    payload = _make_normal_payload(token, search_username='a' * 30)
    msg = _parse_file_search_response(payload, allowed_tokens={token})

    assert msg.token == token
    assert msg.list == []
    assert msg.freeulslots is True
