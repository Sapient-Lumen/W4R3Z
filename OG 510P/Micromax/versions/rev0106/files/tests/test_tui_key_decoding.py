import curses

from micromax_editor.tui import decode_key_event


def test_decode_ctrl_space_maps_to_ctrl_space() -> None:
    assert decode_key_event("\x00") == "Ctrl-Space"


def test_decode_alt_letter_and_shift_letter() -> None:
    assert decode_key_event("\x1b", "g") == "Alt-g"
    assert decode_key_event("\x1b", "P") == "Alt-Shift-p"


def test_decode_alt_special_keys() -> None:
    assert decode_key_event("\x1b", curses.KEY_UP) == "Alt-UpArrow"
    assert decode_key_event("\x1b", curses.KEY_LEFT) == "Alt-LeftArrow"
