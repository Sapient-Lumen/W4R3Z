from __future__ import annotations

from vhk.system.global_shortcuts_portal import (
    _extract_bound_shortcuts,
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




def test_hotkey_to_shortcuts_spec_punctuation_keys():
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+[") == "CTRL+bracketleft"
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+]") == "CTRL+bracketright"
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+;") == "CTRL+semicolon"
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+slash") == "CTRL+slash"
    assert vhk_hotkey_to_shortcuts_spec("Ctrl+backslash") == "CTRL+backslash"

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


def test_extract_bound_shortcuts_from_dbus_monitor_response():
    block = '''signal time=1.0 sender=:1.2 -> destination=(null destination) serial=10 path=/org/freedesktop/portal/desktop/request/1_2/vhk_bind_x; interface=org.freedesktop.portal.Request; member=Response
       uint32 0
       array [
          dict entry(
             string "shortcuts"
             variant             array [
                   struct {
                      string "launch_hotkey"
                      array [
                         dict entry(
                            string "description"
                            variant                               string "Launch macro"
                         )
                         dict entry(
                            string "trigger_description"
                            variant                               string "Super+Shift+P"
                         )
                      ]
                   }
             ]
          )
       ]
'''
    out = _extract_bound_shortcuts(block)
    assert len(out) == 1
    assert out[0].shortcut_id == "launch_hotkey"
    assert out[0].description == "Launch macro"
    assert out[0].trigger_description == "Super+Shift+P"


def test_extract_bound_shortcuts_from_gdbus_inline_response():
    block = "Response (0, {'shortcuts': <[('launch_hotkey', {'description': <'Launch macro'>, 'trigger_description': <'Super+Shift+P'>})]>})"
    out = _extract_bound_shortcuts(block)
    assert len(out) == 1
    assert out[0].shortcut_id == "launch_hotkey"
    assert out[0].description == "Launch macro"
    assert out[0].trigger_description == "Super+Shift+P"
