from __future__ import annotations


from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.textpos import cursor_to_index, index_to_cursor


def test_textpos_round_trip_across_lines() -> None:
    buf = Buffer("aa\nbbb\ncccc")

    cur = Cursor(1, 2)  # inside "bbb"
    idx = cursor_to_index(buf, cur)
    assert idx == len("aa\n") + 2
    assert index_to_cursor(buf, idx) == cur

    # End of buffer clamps.
    assert index_to_cursor(buf, 10_000) == Cursor(2, 4)
