# SPDX-License-Identifier: GPL-3.0-or-later
"""Boundary witness for U-138 / ID3v2 advertised-frame materialization.

Run against one Nicotine+ source lane with:

    NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_id3v2_frame_materialization_boundary_reproducer.py

The assertions intentionally describe current behavior and split the old U-138
claim into two different paths:

* the Nicotine+ share-scanner MP3 route requests tags=False, duration=True and
  does not read a parsable ID3v2 frame body as one advertised allocation;
* the generic tags-enabled TinyTag ID3v2 parser still reads mapped text-frame
  bodies according to the frame's advertised size.

This witness is used to demote/archive the broad "share-scanner general ID3v2"
claim, not to promote a new strict/front packet.
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

PROBE_TEXT_BYTES = 1024 * 1024 + 333
LARGER_TEXT_BYTES = 2 * 1024 * 1024 + 777
SMALL_TEXT_BYTES = 513
MP3_FRAME_BYTES = 417
ID3V1_TRAILER_BYTES = 128


def synchsafe_u28(value: int) -> bytes:
    assert 0 <= value < (1 << 28)
    return bytes([
        (value >> 21) & 0x7F,
        (value >> 14) & 0x7F,
        (value >> 7) & 0x7F,
        value & 0x7F,
    ])


def id3v23_frame(frame_id: bytes, payload: bytes) -> bytes:
    assert len(frame_id) == 4
    return frame_id + len(payload).to_bytes(4, "big") + b"\x00\x00" + payload


def id3v23_text_frame(text_bytes: int) -> bytes:
    assert text_bytes >= 1
    return id3v23_frame(b"TIT2", b"\x03" + b"A" * (text_bytes - 1))


def id3v23_private_frame(payload_bytes: int) -> bytes:
    return id3v23_frame(b"PRIV", b"P" * payload_bytes)


def id3v23_tag(frame: bytes) -> bytes:
    return b"ID3" + bytes([3, 0, 0]) + synchsafe_u28(len(frame)) + frame


def mpeg1_layer3_frame() -> bytes:
    return b"\xff\xfb\x90\x64" + b"\x00" * (MP3_FRAME_BYTES - 4)


def mp3_stream_with_id3v2(frame: bytes) -> bytes:
    return id3v23_tag(frame) + (mpeg1_layer3_frame() * 6) + (b"\x00" * ID3V1_TRAILER_BYTES)


class TrackingFile:
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


def parse_id3_mp3(frame: bytes, *, tags: bool, duration: bool) -> TrackingFile:
    tracked = TrackingFile(mp3_stream_with_id3v2(frame))
    try:
        tracked.tag = TinyTag.get(
            filename="u138-boundary.mp3",
            file_obj=tracked,
            tags=tags,
            duration=duration,
            image=False,
        )
    except Exception as exc:  # pragma: no cover - captured for assertion output
        tracked.exception = exc
    return tracked


def read_requests(tracked: TrackingFile) -> list[tuple[int, int, int]]:
    return [
        (offset, requested, actual)
        for kind, offset, requested, actual, *_rest in tracked.events
        if kind == "read"
    ]


def seek_requests(tracked: TrackingFile) -> list[tuple[int, int, int, int]]:
    requests: list[tuple[int, int, int, int]] = []
    for event in tracked.events:
        if event[0] == "seek":
            _kind, before, offset, whence, after = event
            requests.append((before, offset, whence, after))
    return requests


def body_reads_of(tracked: TrackingFile, payload_bytes: int) -> list[tuple[int, int, int]]:
    return [
        request for request in read_requests(tracked)
        if request[1] == payload_bytes or request[2] == payload_bytes
    ]


def test_share_scanner_style_mp3_duration_only_does_not_materialize_parsable_text_frame_body():
    tracked = parse_id3_mp3(id3v23_text_frame(PROBE_TEXT_BYTES), tags=False, duration=True)

    assert tracked.exception is None
    assert tracked.tag is not None
    assert tracked.tag.duration is not None
    assert tracked.tag.title is None
    assert body_reads_of(tracked, PROBE_TEXT_BYTES) == []

    id3_payload_len = len(id3v23_text_frame(PROBE_TEXT_BYTES))
    assert any(abs(after - id3_payload_len) <= 10 for _before, _offset, _whence, after in seek_requests(tracked))


def test_tags_enabled_generic_id3v2_parse_materializes_mapped_text_frame_body():
    tracked = parse_id3_mp3(id3v23_text_frame(PROBE_TEXT_BYTES), tags=True, duration=False)

    assert tracked.exception is None
    assert tracked.tag is not None
    assert tracked.tag.duration is None
    assert tracked.tag.title == "A" * (PROBE_TEXT_BYTES - 1)
    assert body_reads_of(tracked, PROBE_TEXT_BYTES) == [(20, PROBE_TEXT_BYTES, PROBE_TEXT_BYTES)]


def test_tags_enabled_materialized_text_read_scales_with_advertised_frame_size():
    small = parse_id3_mp3(id3v23_text_frame(PROBE_TEXT_BYTES), tags=True, duration=False)
    large = parse_id3_mp3(id3v23_text_frame(LARGER_TEXT_BYTES), tags=True, duration=False)

    assert small.exception is None
    assert large.exception is None
    small_body = body_reads_of(small, PROBE_TEXT_BYTES)
    large_body = body_reads_of(large, LARGER_TEXT_BYTES)

    assert small_body == [(20, PROBE_TEXT_BYTES, PROBE_TEXT_BYTES)]
    assert large_body == [(20, LARGER_TEXT_BYTES, LARGER_TEXT_BYTES)]
    assert large_body[0][2] - small_body[0][2] == LARGER_TEXT_BYTES - PROBE_TEXT_BYTES


def test_ignored_private_frame_is_skipped_without_materializing_payload():
    tracked = parse_id3_mp3(id3v23_private_frame(PROBE_TEXT_BYTES), tags=True, duration=False)

    assert tracked.exception is None
    assert tracked.tag is not None
    assert body_reads_of(tracked, PROBE_TEXT_BYTES) == []
    assert any(
        offset == PROBE_TEXT_BYTES and whence == os.SEEK_CUR
        for _before, offset, whence, _after in seek_requests(tracked)
    )


def test_small_tags_and_duration_combination_still_parses_duration_and_title():
    tracked = parse_id3_mp3(id3v23_text_frame(SMALL_TEXT_BYTES), tags=True, duration=True)

    assert tracked.exception is None
    assert tracked.tag is not None
    assert tracked.tag.title == "A" * (SMALL_TEXT_BYTES - 1)
    assert tracked.tag.duration is not None
