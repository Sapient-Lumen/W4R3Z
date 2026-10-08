from __future__ import annotations

from micromax_editor.tui import (
    is_paste_char,
    normalize_paste_text,
    parse_bracketed_paste_stream,
)


def test_is_paste_char_accepts_printable_and_newlines() -> None:
    assert is_paste_char('a')
    assert is_paste_char(' ')
    assert is_paste_char('\n')
    assert is_paste_char('\r')
    assert is_paste_char('\t')
    assert not is_paste_char('\x1b')
    assert not is_paste_char(123)  # type: ignore[arg-type]


def test_normalize_paste_text_crlf_to_lf() -> None:
    assert normalize_paste_text('a\r\nb\r\nc') == 'a\nb\nc'


def test_parse_bracketed_paste_stream_parses_payload_and_rest() -> None:
    events = [
        '\x1b', '[', '2', '0', '0', '~',
        'h', 'i', '\r', '\n',
        '\x1b', '[', '2', '0', '1', '~',
        'X',
    ]
    payload, rest = parse_bracketed_paste_stream(events)
    assert payload == 'hi\n'
    assert rest == ['X']


def test_parse_bracketed_paste_stream_returns_none_when_missing_end() -> None:
    events = ['\x1b', '[', '2', '0', '0', '~', 'h', 'i']
    payload, rest = parse_bracketed_paste_stream(events)
    assert payload is None
    assert rest == events
