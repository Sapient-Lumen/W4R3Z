# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for OGG-CONTINUATION-ACCUM-01 / U-124.

Run against one Nicotine+ source lane with:

    NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_ogg_continuation_accumulation_reproducer.py

The assertions intentionally describe current behavior. A hardened metadata
scanner should impose a local parser budget for continued Ogg packet assembly
before materializing an arbitrarily long packet into one bytes/bytearray object.
"""
from __future__ import annotations

import io
import os
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import BinaryIO


_SOURCE = os.environ.get("NICOTINE_SOURCE")
if _SOURCE:
    sys.path.insert(0, str(Path(_SOURCE).resolve()))
else:
    sys.path.insert(0, str(Path.cwd().resolve()))

import pynicotine.external.tinytag as tinytag  # noqa: E402
from pynicotine.external.tinytag import TinyTag  # noqa: E402


MAX_SEGMENTS_PER_PAGE = 255
SEGMENT_SIZE = 255
MAX_CONTINUED_PAGE_BODY = MAX_SEGMENTS_PER_PAGE * SEGMENT_SIZE
SERIAL = 0x51474731


class TrackingBytesIO:
    """BytesIO-like object that records read sizes used by TinyTag.get()."""

    def __init__(self, data: bytes):
        self._bio = io.BytesIO(data)
        self.reads: list[tuple[int, int, int]] = []
        self.seeks: list[tuple[int, int, int, int]] = []

    def read(self, n: int = -1) -> bytes:
        before = self._bio.tell()
        data = self._bio.read(n)
        self.reads.append((before, n, len(data)))
        return data

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        before = self._bio.tell()
        after = self._bio.seek(offset, whence)
        self.seeks.append((before, offset, whence, after))
        return after

    def tell(self) -> int:
        return self._bio.tell()

    def close(self) -> None:
        return None

    def peek(self, n: int = -1) -> bytes:
        before = self._bio.tell()
        raw = self._bio.getvalue()
        return raw[before:] if n < 0 else raw[before:before + n]


def ogg_page(*, segment_sizes: list[int], payload: bytes, sequence: int, flags: int) -> bytes:
    """Build a minimal Ogg page.

    The CRC field is zero because the vendored TinyTag parser does not validate
    it in the archived lanes. This keeps the witness focused on continuation
    packet assembly rather than checksum handling.
    """
    assert len(segment_sizes) <= MAX_SEGMENTS_PER_PAGE
    assert all(0 <= size <= SEGMENT_SIZE for size in segment_sizes)
    assert len(payload) == sum(segment_sizes)

    header = struct.pack(
        "<4sBBqIIiB",
        b"OggS",
        0,          # stream structure version
        flags,
        0,          # granule position is irrelevant to the packet assembly witness
        SERIAL,
        sequence,
        0,          # checksum not enforced by TinyTag
        len(segment_sizes),
    )
    return header + bytes(segment_sizes) + payload


def make_continued_packet_stream(*, continuation_pages: int, terminator_size: int = 1,
                                 vorbis_identification: bool = False) -> bytes:
    """Construct one packet spanning N full-lacing pages and a final terminator.

    Every continuation page has 255 lacing entries of 255 bytes, so no packet is
    yielded until a later lacing value below 255 appears. The final one-byte
    terminator lets the parser yield exactly one accumulated packet.
    """
    assert continuation_pages >= 1
    assert 0 <= terminator_size < SEGMENT_SIZE

    pages: list[bytes] = []
    sequence = 0

    first_payload = b"C" * MAX_CONTINUED_PAGE_BODY
    if vorbis_identification:
        # Keep parsed numeric fields zero so the legacy duration pass returns
        # immediately after the metadata packet is assembled.
        first_payload = b"\x01vorbis" + b"\0" * (MAX_CONTINUED_PAGE_BODY - 7)

    pages.append(ogg_page(
        segment_sizes=[SEGMENT_SIZE] * MAX_SEGMENTS_PER_PAGE,
        payload=first_payload,
        sequence=sequence,
        flags=0x02,  # beginning-of-stream
    ))
    sequence += 1

    for _ in range(1, continuation_pages):
        pages.append(ogg_page(
            segment_sizes=[SEGMENT_SIZE] * MAX_SEGMENTS_PER_PAGE,
            payload=b"C" * MAX_CONTINUED_PAGE_BODY,
            sequence=sequence,
            flags=0x01,  # continued packet
        ))
        sequence += 1

    pages.append(ogg_page(
        segment_sizes=[terminator_size],
        payload=b"T" * terminator_size,
        sequence=sequence,
        flags=0x01 | 0x04,  # continued packet + end-of-stream
    ))

    return b"".join(pages)


def make_ogg_parser(file_obj: BinaryIO, filesize: int):
    """Instantiate the vendored Ogg parser across old and current TinyTag APIs."""
    parser_class = getattr(tinytag, "_Ogg", None) or getattr(tinytag, "Ogg")
    try:
        return parser_class(file_obj, filesize)
    except TypeError:
        parser = parser_class()
        parser._filehandler = file_obj  # pylint: disable=protected-access
        parser.filesize = filesize
        return parser


def first_packet_from_parse_pages(data: bytes):
    file_obj = io.BytesIO(data)
    parser = make_ogg_parser(file_obj, len(data))
    packet_iter = parser._parse_pages(file_obj)  # pylint: disable=protected-access
    packet = next(packet_iter)
    return bytes(packet)


def test_continued_ogg_packet_is_accumulated_across_full_lacing_pages_before_first_yield():
    continuation_pages = 4
    data = make_continued_packet_stream(continuation_pages=continuation_pages)

    packet = first_packet_from_parse_pages(data)

    expected_length = continuation_pages * MAX_CONTINUED_PAGE_BODY + 1
    assert len(packet) == expected_length
    assert packet.startswith(b"C" * 16)
    assert packet.endswith(b"T")


def test_accumulated_packet_size_scales_linearly_with_unterminated_continuation_pages():
    one_page_packet = first_packet_from_parse_pages(
        make_continued_packet_stream(continuation_pages=1)
    )
    four_page_packet = first_packet_from_parse_pages(
        make_continued_packet_stream(continuation_pages=4)
    )

    assert len(one_page_packet) == MAX_CONTINUED_PAGE_BODY + 1
    assert len(four_page_packet) == 4 * MAX_CONTINUED_PAGE_BODY + 1
    assert len(four_page_packet) - len(one_page_packet) == 3 * MAX_CONTINUED_PAGE_BODY


def test_tinytag_get_entry_path_materializes_each_full_continuation_page_before_returning():
    """Exercise the public TinyTag/Nicotine+ metadata-scanner entry shape.

    The first packet starts with a Vorbis identification signature so the normal
    Ogg metadata parser accepts it. The observed read pattern shows every 65,025
    byte full-lacing page body is read before the packet is complete.
    """
    continuation_pages = 4
    data = make_continued_packet_stream(
        continuation_pages=continuation_pages,
        vorbis_identification=True,
    )
    tracked = TrackingBytesIO(data)

    TinyTag.get(filename="witness.ogg", file_obj=tracked, tags=False, duration=True)

    read_size_counts = Counter(requested for _offset, requested, _actual in tracked.reads)
    assert read_size_counts[MAX_CONTINUED_PAGE_BODY] == continuation_pages
    assert sum(actual for _offset, _requested, actual in tracked.reads) == len(data)
    assert tracked.seeks[0][1:3] == (0, os.SEEK_END)
