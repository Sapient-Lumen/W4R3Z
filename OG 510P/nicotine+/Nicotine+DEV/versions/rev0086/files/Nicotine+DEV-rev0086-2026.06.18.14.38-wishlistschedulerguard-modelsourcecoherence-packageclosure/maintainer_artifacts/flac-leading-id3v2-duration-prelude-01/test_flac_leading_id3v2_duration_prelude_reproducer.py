# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-behavior witness for FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 / U-139.

Run against one Nicotine+ source lane with:

    NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_flac_leading_id3v2_duration_prelude_reproducer.py

The assertions intentionally describe current behavior. Legacy 3.3.x-era lanes
parse and apply leading ID3v2 text-frame content even though the share scanner
asks TinyTag for duration only. The master lane changed tag-field handling for
this path, but still traverses the leading ID3v2 envelope before reaching the
native FLAC STREAMINFO duration block.
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

from pynicotine.external import tinytag  # noqa: E402
from pynicotine.external.tinytag import TinyTag  # noqa: E402

STREAMINFO_LEN = 34
PROBE_ID3_TEXT_BYTES = 1024 * 1024 + 73
SMALL_ID3_TEXT_BYTES = 64


def is_master_style() -> bool:
    return hasattr(tinytag, "_Flac")


def synchsafe_u28(value: int) -> bytes:
    assert 0 <= value < (1 << 28)
    return bytes([
        (value >> 21) & 0x7F,
        (value >> 14) & 0x7F,
        (value >> 7) & 0x7F,
        value & 0x7F,
    ])


def streaminfo_record(
    sample_rate: int = 44100,
    channels: int = 2,
    bitdepth: int = 16,
    total_samples: int = 44100 * 7,
) -> bytes:
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


def flac_streaminfo_block() -> bytes:
    # Native FLAC marker followed by a last STREAMINFO block of exact length 34.
    return b"fLaC" + bytes([0x80]) + STREAMINFO_LEN.to_bytes(3, "big") + streaminfo_record()


def id3v2_text_frame(text_bytes: int) -> bytes:
    # TIT2 is a normal mapped ID3v2 text frame. One leading \x03 selects UTF-8.
    content = b"\x03" + b"A" * (text_bytes - 1)
    return b"TIT2" + len(content).to_bytes(4, "big") + b"\x00\x00" + content


def id3v2_tag(text_bytes: int) -> bytes:
    frame = id3v2_text_frame(text_bytes)
    return b"ID3" + bytes([3, 0, 0]) + synchsafe_u28(len(frame)) + frame


def make_leading_id3_flac(text_bytes: int = SMALL_ID3_TEXT_BYTES) -> bytes:
    return id3v2_tag(text_bytes) + flac_streaminfo_block()


class TrackingFile:
    """Small binary file object recording read/seek/peek calls."""

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
        before = self._bio.tell()
        raw = self._bio.getvalue()
        data = raw[before:] if n < 0 else raw[before:before + n]
        self.events.append(("peek", before, n, len(data)))
        return data


def parse_with_tracking(text_bytes: int = SMALL_ID3_TEXT_BYTES) -> TrackingFile:
    tracked = TrackingFile(make_leading_id3_flac(text_bytes))
    try:
        tracked.tag = TinyTag.get(
            filename="leading-id3.flac",
            file_obj=tracked,
            tags=False,
            duration=True,
            image=False,
        )
    except Exception as exc:
        tracked.exception = exc
    return tracked


def read_requests(tracked: TrackingFile) -> list[tuple[int, int, int]]:
    return [
        (offset, requested, actual)
        for kind, offset, requested, actual, *_rest in tracked.events
        if kind == "read"
    ]


def test_duration_only_flac_with_leading_id3v2_still_reaches_streaminfo_duration():
    tracked = parse_with_tracking()

    assert tracked.exception is None
    assert tracked.tag is not None
    assert tracked.tag.duration == 7

    streaminfo_offset = len(id3v2_tag(SMALL_ID3_TEXT_BYTES)) + 8
    assert (streaminfo_offset, STREAMINFO_LEN, STREAMINFO_LEN) in read_requests(tracked)


def test_leading_id3v2_header_is_processed_before_native_flac_marker():
    tracked = parse_with_tracking()
    reads = read_requests(tracked)

    assert any(offset == 0 and requested in {4, 10} for offset, requested, _actual in reads)
    assert any(kind == "seek" and offset == 0 and whence == os.SEEK_END for kind, _before, offset, whence, *_ in tracked.events)

    id3_end = len(id3v2_tag(SMALL_ID3_TEXT_BYTES))
    # All lanes position/probe at the native fLaC marker after the ID3v2 envelope.
    assert any(
        kind in {"read", "peek"} and offset == id3_end and actual >= 4
        for kind, offset, _requested, actual, *_rest in tracked.events
    )


def test_legacy_lanes_apply_id3v2_text_frame_even_though_tags_false_master_does_not():
    tracked = parse_with_tracking()

    assert tracked.exception is None
    if is_master_style():
        assert tracked.tag.title is None
        assert (20, SMALL_ID3_TEXT_BYTES, SMALL_ID3_TEXT_BYTES) not in read_requests(tracked)
    else:
        assert tracked.tag.title == "A" * (SMALL_ID3_TEXT_BYTES - 1)
        assert (20, SMALL_ID3_TEXT_BYTES, SMALL_ID3_TEXT_BYTES) in read_requests(tracked)


def test_large_legacy_id3v2_text_frame_is_materialized_in_duration_only_path_master_bounds_it():
    tracked = parse_with_tracking(PROBE_ID3_TEXT_BYTES)
    reads = read_requests(tracked)

    assert tracked.exception is None
    assert tracked.tag is not None
    assert tracked.tag.duration == 7

    if is_master_style():
        assert tracked.tag.title is None
        assert (20, PROBE_ID3_TEXT_BYTES, PROBE_ID3_TEXT_BYTES) not in reads
        # Master still enters the ID3 parser and probes from inside the frame body
        # before seeking to the end of the ID3 envelope.
        assert any(offset == 20 and requested == 10 for offset, requested, _actual in reads)
    else:
        assert tracked.tag.title is not None
        assert len(tracked.tag.title) == PROBE_ID3_TEXT_BYTES - 1
        assert (20, PROBE_ID3_TEXT_BYTES, PROBE_ID3_TEXT_BYTES) in reads
