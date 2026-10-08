from __future__ import annotations

from vhk.system.global_shortcuts_portal import (
    parse_shortcut_signal_block,
    vhk_hotkey_to_shortcuts_spec,
)


def test_hotkey_to_shortcuts_spec_basic():
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+Alt+t") == "CTRL+ALT+t"
    assert vhk_hotkey_to_shortcuts_spec("Mod4+Shift+p") == "LOGO+SHIFT+p"


def test_hotkey_to_shortcuts_spec_special_keys():
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+Alt+Return") == "CTRL+ALT+Return"
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+Alt+enter") == "CTRL+ALT+Return"
    assert vhk_hotkey_to_shortcuts_spec("Shift+F5") == "SHIFT+F5"


def test_parse_shortcut_signal_block_activated_matches_session():
    block = '''signal time=1.0 sender=:1.2 -> destination=(null destination) serial=10 path=/org/freedesktop/portal/desktop; interface=org.freedesktop.portal.GlobalShortcuts; member=Activated
       object path "/org/freedesktop/portal/desktop/session/1_2/vhk"
       string "shot"
       uint64 12345
       array [
       ]
'''
    out = parse_shortcut_signal_block(block, session_handle="/org/freedesktop/portal/desktop/session/1_2/vhk")
    assert out is not None
    assert out.kind == "Activated"
    assert out.shortcut_id == "shot"
    assert out.timestamp == 12345


def test_parse_shortcut_signal_block_filters_other_sessions():
    block = '''signal time=1.0 sender=:1.2 -> destination=(null destination) serial=10 path=/org/freedesktop/portal/desktop; interface=org.freedesktop.portal.GlobalShortcuts; member=Activated
       object path "/org/freedesktop/portal/desktop/session/1_2/other"
       string "shot"
       uint64 12345
'''
    out = parse_shortcut_signal_block(block, session_handle="/org/freedesktop/portal/desktop/session/1_2/vhk")
    assert out is None
