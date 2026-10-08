from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_gen_udev_uinput_default_stdout():
    result = runner.invoke(app, ["gen-udev-uinput"])
    assert result.exit_code == 0, result.output
    text = result.output
    assert 'KERNEL=="uinput"' in text
    assert 'GROUP="uinput"' in text
    assert 'MODE="0660"' in text
    assert 'static_node=uinput' in text


def test_gen_udev_uinput_uaccess_flag():
    result = runner.invoke(app, ["gen-udev-uinput", "--uaccess"])
    assert result.exit_code == 0, result.output
    text = result.output
    assert 'TAG+="uaccess"' in text
    assert 'SUBSYSTEM=="misc"' in text


def test_gen_udev_uinput_out_dir_writes_multiple_files(tmp_path: Path):
    out_dir = tmp_path / "rules"
    result = runner.invoke(app, ["gen-udev-uinput", "--out-dir", str(out_dir), "--evdev-name", "AT Translated Set 2 keyboard"])
    assert result.exit_code == 0, result.output

    uinput_rule = out_dir / "80-uinput-vhk.rules"
    modprobe = out_dir / "uinput.conf"
    evdev_rule = out_dir / "90-input-vhk.rules"

    assert uinput_rule.exists()
    assert modprobe.exists()
    assert evdev_rule.exists()

    assert 'KERNEL=="uinput"' in uinput_rule.read_text()
    assert 'uinput' in modprobe.read_text()
    assert 'ATTRS{name}=="AT Translated Set 2 keyboard"' in evdev_rule.read_text()
    assert 'TAG+="uaccess"' in evdev_rule.read_text()
