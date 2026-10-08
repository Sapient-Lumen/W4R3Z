from __future__ import annotations

from vhk.system.dbus_bridge import parse_dbus_monitor_block


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
