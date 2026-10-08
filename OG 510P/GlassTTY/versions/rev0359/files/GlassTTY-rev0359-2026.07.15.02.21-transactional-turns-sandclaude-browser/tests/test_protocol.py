from __future__ import annotations

import io

from glassttyd.protocol import read_native_message, write_native_message


class FakeStdIO:
    def __init__(self) -> None:
        self.buffer = io.BytesIO()


def test_native_message_round_trip() -> None:
    writer = FakeStdIO()
    payload = {'hello': 'world', 'n': 3}
    write_native_message(writer, payload)
    writer.buffer.seek(0)
    assert read_native_message(writer) == payload


def test_native_message_size_guard_rejects_oversize_payload() -> None:
    writer = FakeStdIO()
    payload = {'blob': 'x' * (1024 * 1024)}
    try:
        write_native_message(writer, payload)
    except RuntimeError as exc:
        assert 'too large' in str(exc)
    else:
        raise AssertionError('expected oversize payload to be rejected')
