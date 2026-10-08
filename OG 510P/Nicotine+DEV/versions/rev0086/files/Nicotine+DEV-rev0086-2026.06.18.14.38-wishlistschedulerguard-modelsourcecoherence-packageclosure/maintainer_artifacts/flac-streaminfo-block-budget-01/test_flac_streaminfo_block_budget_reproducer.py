# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127.

Run against one Nicotine+ source lane with:

    NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_flac_streaminfo_block_budget_reproducer.py

The assertions intentionally describe current behavior. A hardened metadata
scanner should validate or bound the FLAC STREAMINFO metadata block before
materializing an arbitrary advertised payload when duration extraction only
needs the fixed 34-byte STREAMINFO record.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

from pynicotine.external.tinytag import TinyTag  # noqa: E402

STREAMINFO_LEN = 34
PROBE_PAYLOAD_BYTES = 1024 * 1024 + 101
LARGE_PAYLOAD_BYTES = 2 * 1024 * 1024 + 257


def streaminfo_prefix(
    sample_rate: int = 44100,
    channels: int = 2,
    bitdepth: int = 16,
    total_samples: int = 44100 * 5,
) -> bytes:
    """Build a valid 34-byte FLAC STREAMINFO duration record."""
    payload = bytearray(STREAMINFO_LEN)
    payload[0:2] = (4096).to_bytes(2, "big")
    payload[2:4] = (4096).to_bytes(2, "big")
    packed = (
        (sample_rate & ((1 << 20) - 1)) << (3 + 5 + 36)
        | ((channels - 1) & 0x7) << (5 + 36)
        | ((bitdepth - 1) & 0x1F) << 36
        | (total_samples & ((1 << 36) - 1))
    )
    payload[10:18] = packed.to_bytes(8, "big")
    return bytes(payload)


def metadata_block_header(block_type: int, payload_len: int, is_last: bool = True) -> bytes:
    """Build the FLAC 4-byte metadata-block header."""
    assert 0 <= payload_len <= 0xFFFFFF
    first = block_type | (0x80 if is_last else 0)
    return bytes([first]) + payload_len.to_bytes(3, "big")


def make_flac_with_streaminfo_block(payload_len: int) -> bytes:
    """Build a compact FLAC-like stream with controllable STREAMINFO length."""
    assert payload_len >= STREAMINFO_LEN
    payload = streaminfo_prefix() + b"P" * (payload_len - STREAMINFO_LEN)
    return b"fLaC" + metadata_block_header(0, payload_len) + payload


class TrackingFile:
    """Small binary file object that records TinyTag read/seek behavior."""

    def __init__(self, data: bytes):
        self._bio = io.BytesIO(data)
        self.events: list[tuple] = []
        self.tag = None
        self.exception = None

    def read(self, n: int = -1) -> bytes:
        before = self._bio.tell()
        data = self._bio.read(n)
        self.events.append(("read", before, n, len(data)))
        return data

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        before = self._bio.tell()
        after = self._bio.seek(offset, whence)
        self.events.append(("seek", before, offset, whence, after))
        return after

    def tell(self) -> int:
        return self._bio.tell()

    def close(self) -> None:
        return None

    def peek(self, n: int = -1) -> bytes:
        # Older TinyTag lanes peek at the magic bytes before selecting the parser.
        before = self._bio.tell()
        raw = self._bio.getvalue()
        data = raw[before:] if n < 0 else raw[before:before + n]
        self.events.append(("peek", before, n, len(data)))
        return data


def parse_with_tracking(streaminfo_payload_len: int) -> TrackingFile:
    tracked = TrackingFile(make_flac_with_streaminfo_block(streaminfo_payload_len))
    try:
        tracked.tag = TinyTag.get(filename="witness.flac", file_obj=tracked, tags=False, duration=True, image=False)
    except Exception as exc:  # Older lanes raise after materializing oversized STREAMINFO payloads.
        tracked.exception = exc
    return tracked


def read_requests(tracked: TrackingFile) -> list[tuple[int, int, int]]:
    return [
        (offset, requested, actual)
        for kind, offset, requested, actual, *_rest in tracked.events
        if kind == "read"
    ]


def test_valid_exact_streaminfo_block_uses_the_fixed_34_byte_record():
    tracked = parse_with_tracking(STREAMINFO_LEN)

    assert tracked.exception is None
    assert tracked.tag is not None
    assert tracked.tag.duration == 5
    assert (8, STREAMINFO_LEN, STREAMINFO_LEN) in read_requests(tracked)


def test_streaminfo_duration_path_reads_the_advertised_block_before_fixed_length_validation():
    tracked = parse_with_tracking(PROBE_PAYLOAD_BYTES)

    assert (8, PROBE_PAYLOAD_BYTES, PROBE_PAYLOAD_BYTES) in read_requests(tracked)
    assert any(
        kind == "seek" and offset == 0 and whence == os.SEEK_END
        for kind, _before, offset, whence, *_rest in tracked.events
    )


def test_materialized_streaminfo_read_size_scales_with_advertised_block_length():
    small = parse_with_tracking(PROBE_PAYLOAD_BYTES)
    large = parse_with_tracking(LARGE_PAYLOAD_BYTES)

    small_reads = [
        actual for _offset, requested, actual in read_requests(small)
        if requested == PROBE_PAYLOAD_BYTES
    ]
    large_reads = [
        actual for _offset, requested, actual in read_requests(large)
        if requested == LARGE_PAYLOAD_BYTES
    ]

    assert small_reads == [PROBE_PAYLOAD_BYTES]
    assert large_reads == [LARGE_PAYLOAD_BYTES]
    assert large_reads[0] - small_reads[0] == LARGE_PAYLOAD_BYTES - PROBE_PAYLOAD_BYTES


def test_padded_streaminfo_block_reads_padding_even_though_duration_fields_are_fixed_prefix():
    padded_len = STREAMINFO_LEN + 4096
    tracked = parse_with_tracking(padded_len)

    assert (8, padded_len, padded_len) in read_requests(tracked)
    assert padded_len > STREAMINFO_LEN
