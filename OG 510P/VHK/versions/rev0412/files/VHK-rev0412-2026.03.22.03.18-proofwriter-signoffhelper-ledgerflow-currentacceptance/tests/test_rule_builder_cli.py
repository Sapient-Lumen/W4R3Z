from __future__ import annotations

import json

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_build_rule_prefers_assign_for_workspace_only(monkeypatch):
    import vhk.cli as cli_mod

    monkeypatch.setattr(
        cli_mod,
        "_preview_selector_against_i3",
        lambda stable, exact: {"status": "unavailable", "error": "no ipc in test"},
    )

    result = runner.invoke(
        app,
        [
            "build-rule",
            "--json",
            "--class",
            "Firefox",
            "--instance",
            "Navigator",
            "--workspace",
            "2: web",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["selector"]["stable"] == '[class="^Firefox$" instance="^Navigator$"]'
    assert payload["recommendation"]["preferred_rule_type"] == "assign"
    assert payload["rules"]["i3_assign"] == 'assign [class="^Firefox$" instance="^Navigator$"] "2: web"'
    assert payload["rules"]["i3_for_window"] == (
        'for_window [class="^Firefox$" instance="^Navigator$"] move container to workspace "2: web"'
    )
    assert payload["rules"]["devilspie2_lua"] is not None
    assert "set_window_workspace(\"2: web\")" in payload["rules"]["devilspie2_lua"]



def test_build_rule_pick_apply_once_runs_i3_and_wmctrl(monkeypatch):
    import vhk.cli as cli_mod

    executed = []

    class FakeConn:
        def __init__(self, socket_path=None, timeout=2.0):
            self.socket_path = socket_path
            self.timeout = timeout

        def command(self, cmd):
            executed.append(("i3", cmd))
            return [{"success": True}]

    def fake_subprocess_run(cmd, check=False, capture_output=False, text=False, timeout=None):
        executed.append(("subprocess", cmd))

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(cli_mod, "_pick_x11_window_id", lambda: "0x7b")
    monkeypatch.setattr(
        cli_mod,
        "_inspect_x11_window",
        lambda wid: {
            "window_id": wid,
            "pid": 4242,
            "class": "Firefox",
            "instance": "Navigator",
            "window_role": "browser",
            "title": "Docs",
            "geometry": {"x": 1, "y": 2, "w": 3, "h": 4},
        },
    )
    monkeypatch.setattr(
        cli_mod,
        "_preview_selector_against_i3",
        lambda stable, exact: {"status": "ok", "stable": {"match_count": 1}, "exact": {"match_count": 1}, "warnings": []},
    )
    monkeypatch.setattr(cli_mod, "discover_socket_path", lambda: "/tmp/i3.sock")
    monkeypatch.setattr(cli_mod, "I3Connection", FakeConn)
    monkeypatch.setattr(cli_mod.subprocess, "run", fake_subprocess_run)

    result = runner.invoke(
        app,
        [
            "build-rule",
            "--pick",
            "--json",
            "--include-title",
            "--float",
            "--sticky",
            "--above",
            "--x",
            "10",
            "--y",
            "20",
            "--width",
            "800",
            "--height",
            "600",
            "--apply-once",
        ],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["rules"]["i3_for_window"] == (
        'for_window [class="^Firefox$" instance="^Navigator$" window_role="^browser$" title="^Docs$"] '
        'floating enable, sticky enable, move position 10 px 20 px, resize set 800 px 600 px'
    )
    assert payload["rules"]["wmctrl_apply_once"] == [
        "wmctrl -i -r 0x7b -b add,above",
        "wmctrl -i -r 0x7b -b add,sticky",
        "wmctrl -i -r 0x7b -e 0,10,20,800,600",
    ]
    assert payload["rules"]["devilspie2_lua"] is not None
    assert "make_always_on_top()" in payload["rules"]["devilspie2_lua"]
    assert "pin_window()" in payload["rules"]["devilspie2_lua"]
    assert payload["apply_once"]["ok"] is True
    assert any(kind == "i3" for kind, _ in executed)
    assert any(kind == "subprocess" for kind, _ in executed)
