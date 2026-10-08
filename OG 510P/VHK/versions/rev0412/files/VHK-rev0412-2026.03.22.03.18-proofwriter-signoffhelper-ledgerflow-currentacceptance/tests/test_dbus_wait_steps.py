from __future__ import annotations

import time
from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project
from vhk.system.dbus_bridge import DBusSignal


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_wait_for_dbus_signal_matches_filters_and_sets_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "WaitForDbusSignal",
                        "bus": "session",
                        "interface": "org.mpris.MediaPlayer2.Player",
                        "member": "Seeked",
                        "pattern": r'"args": \[13\]',
                        "condition": "dbus_args[0] == 13 and dbus_interface == 'org.mpris.MediaPlayer2.Player'",
                        "timeout_ms": 500,
                    }
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    seen = {}

    def fake_iter(*, match_rule: str, bus: str = "session", timeout_s=None):
        seen["match_rule"] = match_rule
        seen["bus"] = bus
        yield DBusSignal(
            sender=":1.77",
            path="/org/mpris/MediaPlayer2",
            interface="org.mpris.MediaPlayer2.Player",
            member="PropertiesChanged",
            args=[{"PlaybackStatus": "Paused"}],
            raw="signal one\n",
        )
        yield DBusSignal(
            sender=":1.77",
            path="/org/mpris/MediaPlayer2",
            interface="org.mpris.MediaPlayer2.Player",
            member="Seeked",
            args=[13],
            raw="signal two\n",
        )

    monkeypatch.setattr(runner_mod.dbus_bridge_mod, "iter_dbus_signals", fake_iter)

    res = Runner(load_project(proj)).run("m")
    assert res.ok, res.error
    assert seen["bus"] == "session"
    assert "type='signal'" in seen["match_rule"]
    assert "interface='org.mpris.MediaPlayer2.Player'" in seen["match_rule"]
    assert "member='Seeked'" in seen["match_rule"]
    assert res.vars["dbus_bus"] == "session"
    assert res.vars["dbus_interface"] == "org.mpris.MediaPlayer2.Player"
    assert res.vars["dbus_member"] == "Seeked"
    assert res.vars["dbus_args"] == [13]
    assert res.vars["dbus_signal"]["args"] == [13]
    assert '"member": "Seeked"' in res.vars["dbus_text"]
    assert res.vars["dbus_raw"] == "signal two\n"


def test_wait_for_dbus_signal_times_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {"m": {"name": "m", "steps": [{"type": "WaitForDbusSignal", "interface": "org.test.Demo", "member": "Fire", "timeout_ms": 50}]}}
    )

    import vhk.core.runner as runner_mod

    def fake_iter(*, match_rule: str, bus: str = "session", timeout_s=None):
        if False:
            yield None
        return
        yield

    monkeypatch.setattr(runner_mod.dbus_bridge_mod, "iter_dbus_signals", fake_iter)

    res = Runner(load_project(proj)).run("m")
    assert not res.ok
    assert "WaitForDbusSignal" in (res.error or "")
