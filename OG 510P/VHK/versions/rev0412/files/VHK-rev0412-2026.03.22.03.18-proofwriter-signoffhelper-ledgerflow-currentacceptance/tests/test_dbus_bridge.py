from __future__ import annotations

from vhk.system.dbus_bridge import build_match_rule, parse_dbus_monitor_block, parse_gdbus_monitor_line, signal_text


def test_parse_dbus_monitor_block_extracts_metadata_and_args():
    block = '''signal time=1.0 sender=:1.53 -> destination=(null destination) serial=143 path=/org/vhk/Trigger; interface=org.vhk.Trigger; member=Fire
       string "hello"
       int32 42
       boolean true
       double 0.5
'''
    sig = parse_dbus_monitor_block(block)
    assert sig is not None
    assert sig.interface == "org.vhk.Trigger"
    assert sig.member == "Fire"
    assert sig.path == "/org/vhk/Trigger"
    assert sig.args == ["hello", 42, True, 0.5]


def test_parse_dbus_monitor_block_auto_json_decodes_first_arg():
    block = '''signal time=1.0 sender=:1.53 -> destination=(null destination) serial=143 path=/org/vhk/Trigger; interface=org.vhk.Trigger; member=Fire
       string "{\\"macro\\":\\"sig\\",\\"vars\\":{\\"x\\":1}}"
'''
    sig = parse_dbus_monitor_block(block)
    assert sig is not None
    assert isinstance(sig.args[0], dict)
    assert sig.args[0]["macro"] == "sig"
    assert sig.args[0]["vars"]["x"] == 1


def test_parse_gdbus_monitor_line_extracts_metadata_and_args():
    line = "/org/mpris/MediaPlayer2: org.freedesktop.DBus.Properties.PropertiesChanged ('org.mpris.MediaPlayer2.Player', {'PlaybackStatus': <'Playing'>}, @as [])"
    sig = parse_gdbus_monitor_line(line)
    assert sig is not None
    assert sig.path == "/org/mpris/MediaPlayer2"
    assert sig.interface == "org.freedesktop.DBus.Properties"
    assert sig.member == "PropertiesChanged"
    assert sig.args[0] == "org.mpris.MediaPlayer2.Player"
    assert sig.args[1]["PlaybackStatus"] == "Playing"


def test_build_match_rule_and_signal_text_are_stable():
    rule = build_match_rule(sender="org.mpris.MediaPlayer2.vlc", interface="org.freedesktop.DBus.Properties", member="PropertiesChanged")
    assert "type='signal'" in rule
    assert "sender='org.mpris.MediaPlayer2.vlc'" in rule
    sig = parse_dbus_monitor_block('''signal time=1.0 sender=:1.53 -> destination=(null destination) serial=143 path=/org/vhk/Trigger; interface=org.vhk.Trigger; member=Fire
       string "hello"
''')
    assert sig is not None
    txt = signal_text(sig)
    assert '"interface": "org.vhk.Trigger"' in txt
    assert '"args": ["hello"]' in txt
