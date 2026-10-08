from __future__ import annotations

import json

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_pick_window_json_includes_role_suggestions_and_preview(monkeypatch):
    import vhk.cli as cli_mod

    def fake_run_capture(cmd):
        if cmd == ["xdotool", "selectwindow"]:
            return "123\n"
        if cmd[:3] == ["xprop", "-id", "0x7b"]:
            return """WM_CLASS(STRING) = \"Navigator\", \"Firefox\"
WM_WINDOW_ROLE(STRING) = \"browser\"
_NET_WM_NAME(UTF8_STRING) = \"Docs (staging) [Project]\"
_NET_WM_PID(CARDINAL) = 4242
"""
        if cmd[:3] == ["xwininfo", "-id", "0x7b"]:
            return """xwininfo: Window id: 0x7b \"Docs (staging) [Project]\"

  Absolute upper-left X:  11
  Absolute upper-left Y:  22
  Width:  1280
  Height:  720
"""
        raise AssertionError(cmd)

    class FakeConn:
        def __init__(self, socket_path=None, timeout=2.0):
            self.socket_path = socket_path
            self.timeout = timeout

        def get_tree(self):
            return {
                "type": "root",
                "nodes": [
                    {
                        "type": "workspace",
                        "name": "1",
                        "nodes": [
                            {
                                "type": "con",
                                "id": 123,
                                "name": "Docs (staging) [Project]",
                                "focused": True,
                                "window_properties": {
                                    "class": "Firefox",
                                    "instance": "Navigator",
                                    "window_role": "browser",
                                    "title": "Docs (staging) [Project]",
                                },
                                "nodes": [],
                                "floating_nodes": [],
                            },
                            {
                                "type": "con",
                                "id": 124,
                                "name": "Mail",
                                "focused": False,
                                "window_properties": {
                                    "class": "Firefox",
                                    "instance": "Navigator",
                                    "window_role": "browser",
                                    "title": "Inbox",
                                },
                                "nodes": [],
                                "floating_nodes": [],
                            },
                        ],
                        "floating_nodes": [],
                    }
                ],
                "floating_nodes": [],
            }

    monkeypatch.setattr(cli_mod, "detect_backend", lambda: "x11")
    monkeypatch.setattr(cli_mod, "_run_capture", fake_run_capture)
    monkeypatch.setattr(cli_mod.shutil, "which", lambda name: f"/tmp/{name}" if name == "xdotool" else None)
    monkeypatch.setattr(cli_mod, "discover_socket_path", lambda: "/tmp/i3.sock")
    monkeypatch.setattr(cli_mod, "I3Connection", FakeConn)

    result = runner.invoke(app, ["pick-window", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)

    assert payload["window_role"] == "browser"
    assert payload["geometry"] == {"x": 11, "y": 22, "w": 1280, "h": 720}
    assert payload["selector_suggestions"]["stable"]["fields"] == ["class", "instance", "window_role"]
    assert payload["selector_suggestions"]["stable"]["i3_criteria"] == (
        '[class="^Firefox$" instance="^Navigator$" window_role="^browser$"]'
    )
    assert payload["i3_exact_criteria"] == (
        '[class="^Firefox$" instance="^Navigator$" window_role="^browser$" '
        'title="^Docs \\\\(staging\\\\) \\\\[Project\\\\]$"]'
    )
    assert payload["preview"]["status"] == "ok"
    assert payload["preview"]["stable"]["match_count"] == 2
    assert payload["preview"]["exact"]["match_count"] == 1
    assert payload["preview"]["warnings"]
    assert payload["selector_suggestions"]["title_warning"]



def test_pick_window_no_json_prints_stable_selector(monkeypatch):
    import vhk.cli as cli_mod

    def fake_run_capture(cmd):
        if cmd == ["xdotool", "selectwindow"]:
            return "321\n"
        if cmd[:3] == ["xprop", "-id", "0x141"]:
            return 'WM_CLASS(STRING) = "app", "MyApp"\n_NET_WM_NAME(UTF8_STRING) = "Dashboard"\n'
        if cmd[:3] == ["xwininfo", "-id", "0x141"]:
            return "Absolute upper-left X:  1\nAbsolute upper-left Y:  2\nWidth:  3\nHeight:  4\n"
        raise AssertionError(cmd)

    monkeypatch.setattr(cli_mod, "detect_backend", lambda: "x11")
    monkeypatch.setattr(cli_mod, "_run_capture", fake_run_capture)
    monkeypatch.setattr(cli_mod.shutil, "which", lambda name: f"/tmp/{name}" if name == "xdotool" else None)
    monkeypatch.setattr(
        cli_mod,
        "_preview_selector_against_i3",
        lambda stable, exact: {"status": "unavailable", "error": "no ipc in test"},
    )

    result = runner.invoke(app, ["pick-window", "--no-json"])
    assert result.exit_code == 0, result.stdout
    assert result.stdout.strip() == '[class="^MyApp$" instance="^app$"]'
