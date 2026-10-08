# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for WMA-ASF-TINYSTEP-01 / U-273.

Run against one Nicotine+ source lane with:

    NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_wma_asf_tinystep_reproducer.py

The assertions intentionally describe current behavior. A hardened parser should
reject or stop on ASF object sizes smaller than the 24-byte object header before
performing a backwards/overlapping seek.
"""
from __future__ import annotations

import io
import os
import struct
import sys
from pathlib import Path


_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

from pynicotine.external.tinytag import TinyTag  # noqa: E402


ASF_HEADER_GUID = b"0&\xb2u\x8ef\xcf\x11\xa6\xd9\x00\xaa\x00b\xcel"
ASF_HEADER_LEN = 30
ASF_OBJECT_HEADER_LEN = 24
MALFORMED_OBJECT_SIZE = 8
VALID_MIN_OBJECT_SIZE = ASF_OBJECT_HEADER_LEN
PAYLOAD_LEN = 1024


class TrackingFile:
    """Small binary file object that records parser read/seek progress."""

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
        # method here so the tracker remains a file-like object for both lanes.
        before = self._bio.tell()
        raw = self._bio.getvalue()
        data = raw[before:] if n < 0 else raw[before:before + n]
        self.events.append(("peek", before, n, len(data)))
        return data


def make_asf_with_repeating_unknown_objects(*, object_size: int, payload_len: int = PAYLOAD_LEN) -> bytes:
    """Build a compact ASF-like stream with repeated unknown object headers.

    For object_size=8, each loop consumes a 24-byte header and then seeks back
    16 bytes, so the next object starts only 8 bytes later. The chosen size is
    below the 24-byte ASF object header but still large enough to place the next
    little-endian size field without overlapping contradictions.
    """
    header = bytearray()
    header += ASF_HEADER_GUID
    header += struct.pack("<Q", ASF_HEADER_LEN + payload_len)
    header += struct.pack("<I", 1)  # object count is not enforced by the parser
    header += b"\x01\x02"

    payload = bytearray(b"A" * payload_len)
    step = object_size
    for start in range(0, payload_len - ASF_OBJECT_HEADER_LEN + 1, step):
        size_offset = start + 16
        if size_offset + 8 <= payload_len:
            payload[size_offset:size_offset + 8] = struct.pack("<Q", object_size)

    return bytes(header + payload)


def parse_with_tracking(data: bytes) -> TrackingFile:
    tracked = TrackingFile(data)
    TinyTag.get(filename="witness.wma", file_obj=tracked, tags=False, duration=True)
    return tracked


def object_header_read_starts(tracked: TrackingFile) -> list[int]:
    """Return ASF object-loop start offsets for both old and new TinyTag shapes."""
    starts = []
    for event in tracked.events:
        if event[0] != "read":
            continue
        _kind, offset, requested, _actual = event
        # Older lanes read object_id (16) then object_size (8). Master reads the
        # whole 24-byte object header at once. In both cases, offsets >= 30 are
        # object-loop starts for this witness.
        if offset >= ASF_HEADER_LEN and requested in (16, ASF_OBJECT_HEADER_LEN):
            starts.append(offset)
    return starts


def backwards_object_seeks(tracked: TrackingFile) -> list[tuple]:
    return [
        event for event in tracked.events
        if event[0] == "seek" and event[2] < 0 and event[3] == os.SEEK_CUR
    ]


def test_wma_asf_object_size_below_header_causes_overlapping_tiny_step_walk():
    malformed = make_asf_with_repeating_unknown_objects(object_size=MALFORMED_OBJECT_SIZE)

    tracked = parse_with_tracking(malformed)
    starts = object_header_read_starts(tracked)
    backwards_seeks = backwards_object_seeks(tracked)

    assert len(starts) >= 120
    assert starts[:6] == [30, 38, 46, 54, 62, 70]
    assert all((right - left) == MALFORMED_OBJECT_SIZE for left, right in zip(starts, starts[1:20]))
    assert len(backwards_seeks) >= 120
    assert all(event[2] == MALFORMED_OBJECT_SIZE - ASF_OBJECT_HEADER_LEN for event in backwards_seeks[:20])


def test_valid_minimum_sized_unknown_objects_do_not_overlap_baseline():
    valid_minimum = make_asf_with_repeating_unknown_objects(object_size=VALID_MIN_OBJECT_SIZE)

    tracked = parse_with_tracking(valid_minimum)
    starts = object_header_read_starts(tracked)

    assert len(starts) <= 45
    assert starts[:6] == [30, 54, 78, 102, 126, 150]
    assert all((right - left) == VALID_MIN_OBJECT_SIZE for left, right in zip(starts, starts[1:20]))
    assert backwards_object_seeks(tracked) == []


def test_under_header_object_size_performs_about_three_times_more_object_iterations_than_minimum_valid_size():
    malformed = parse_with_tracking(make_asf_with_repeating_unknown_objects(object_size=MALFORMED_OBJECT_SIZE))
    valid_minimum = parse_with_tracking(make_asf_with_repeating_unknown_objects(object_size=VALID_MIN_OBJECT_SIZE))

    malformed_loops = len(object_header_read_starts(malformed))
    valid_loops = len(object_header_read_starts(valid_minimum))

    assert malformed_loops == 127
    assert valid_loops == 43
    assert malformed_loops / valid_loops > 2.9
