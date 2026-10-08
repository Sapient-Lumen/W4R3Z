# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for MP4-M4A-ATOM-BUDGET-01 / U-125.

Run against one Nicotine+ source lane with:

    NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_mp4_m4a_atom_budget_reproducer.py

The assertions intentionally describe current behavior. A hardened metadata
scanner should avoid materializing an arbitrary MP4 atom leaf into one bytes
object when only a small fixed prefix is needed for duration/header parsing.
"""
from __future__ import annotations

import io
import os
import struct
import sys
from collections import Counter
from pathlib import Path


_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

from pynicotine.external.tinytag import TinyTag  # noqa: E402


MVHD_PREFIX = (
    b"\x00"                # version 0
    + b"\x00\x00\x00"    # flags
    + struct.pack(">II", 0, 0)       # creation and modification times
    + struct.pack(">II", 1000, 5000) # timescale and duration
)
PROBE_PAYLOAD_BYTES = 1024 * 1024 + 123
LARGE_PAYLOAD_BYTES = 2 * 1024 * 1024 + 17


def atom(atom_type: bytes, payload: bytes) -> bytes:
    """Build a compact 32-bit-size MP4 atom."""
    assert len(atom_type) == 4
    return struct.pack(">I4s", 8 + len(payload), atom_type) + payload


def make_mp4_with_large_mvhd_payload(payload_len: int) -> bytes:
    """Build an MP4-like stream whose duration atom has controllable padding.

    The `mvhd` parser needs only the fixed header fields at the start of the
    atom payload for this witness. The trailing padding demonstrates that the
    current traversal layer materializes the entire leaf payload before calling
    the parser.
    """
    assert payload_len >= len(MVHD_PREFIX)
    mvhd_payload = MVHD_PREFIX + b"P" * (payload_len - len(MVHD_PREFIX))
    ftyp = atom(b"ftyp", b"M4A " + b"\0" * 8)
    moov = atom(b"moov", atom(b"mvhd", mvhd_payload))
    return ftyp + moov


class TrackingFile:
    """Small binary file object that records TinyTag read/seek behavior."""

    def __init__(self, data: bytes):
        self._bio = io.BytesIO(data)
        self.events: list[tuple] = []

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
        # Older TinyTag only needs peek() when no filename is supplied. Keep the
        # method here so the tracker remains a file-like object for all lanes.
        before = self._bio.tell()
        raw = self._bio.getvalue()
        data = raw[before:] if n < 0 else raw[before:before + n]
        self.events.append(("peek", before, n, len(data)))
        return data


def parse_with_tracking(payload_len: int) -> TrackingFile:
    tracked = TrackingFile(make_mp4_with_large_mvhd_payload(payload_len))
    TinyTag.get(filename="witness.m4a", file_obj=tracked, tags=False, duration=True, image=False)
    return tracked


def read_requests(tracked: TrackingFile) -> list[tuple[int, int, int]]:
    return [
        (offset, requested, actual)
        for kind, offset, requested, actual, *_rest in tracked.events
        if kind == "read"
    ]


def test_mp4_duration_path_materializes_entire_mvhd_atom_payload_before_parsing_header_fields():
    tracked = parse_with_tracking(PROBE_PAYLOAD_BYTES)
    requests = read_requests(tracked)

    # After ftyp, moov, and mvhd headers, the traversal layer reads exactly the
    # advertised mvhd payload length into one bytes object and passes it to the
    # mvhd parser.
    assert (36, PROBE_PAYLOAD_BYTES, PROBE_PAYLOAD_BYTES) in requests

    requested_counts = Counter(requested for _offset, requested, _actual in requests)
    assert requested_counts[PROBE_PAYLOAD_BYTES] == 1
    assert any(
        kind == "seek" and offset == 0 and whence == os.SEEK_END
        for kind, _before, offset, whence, *_rest in tracked.events
    )


def test_materialized_mvhd_read_size_scales_with_advertised_atom_payload_size():
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


def test_valid_minimal_mvhd_duration_only_needs_small_prefix_but_current_path_reads_padding_too():
    minimal_len = len(MVHD_PREFIX)
    padded_len = minimal_len + 4096

    minimal = parse_with_tracking(minimal_len)
    padded = parse_with_tracking(padded_len)

    minimal_requests = read_requests(minimal)
    padded_requests = read_requests(padded)

    assert (36, minimal_len, minimal_len) in minimal_requests
    assert (36, padded_len, padded_len) in padded_requests
    assert padded_len > minimal_len
