from __future__ import annotations

import json

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_window_spy_json_includes_suggestions(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_active_window_info",
        lambda: (
            {
                "class": "Firefox",
                "instance": "Navigator",
                "title": "Mozilla Firefox",
                "workspace": "1",
                "focused": True,
            },
            "i3",
        ),
    )

    monkeypatch.setattr(
        aw,
        "get_active_window_geometry",
        lambda: ({"x": 10, "y": 20, "w": 300, "h": 200}, {"x": 12, "y": 25, "w": 296, "h": 190}, "i3"),
    )

    result = runner.invoke(app, ["window-spy"])
    assert result.exit_code == 0, result.output

    payload = json.loads(result.output)
    assert payload["wm"] == "i3"
    assert payload["active"]["class"] == "Firefox"

    stable = payload["suggested"]["stable"]
    exact = payload["suggested"]["exact"]

    assert stable.get("class") == "Firefox"
    assert "title" not in stable

    assert exact.get("class") == "Firefox"
    assert exact.get("title") == "Mozilla Firefox"

    assert payload["geometry"]["rect"]["x"] == 10
    assert payload["geometry"]["client"]["y"] == 25


def test_window_spy_no_json_prints_stable_selector(monkeypatch):
    import vhk.system.active_window as aw

    monkeypatch.setattr(
        aw,
        "get_active_window_info",
        lambda: (
            {
                "class": "Firefox",
                "title": "Mozilla Firefox",
                "workspace": "1",
                "focused": True,
            },
            "i3",
        ),
    )

    result = runner.invoke(app, ["window-spy", "--no-json"])
    assert result.exit_code == 0, result.output
    stable = json.loads(result.output)
    assert stable["class"] == "Firefox"
    assert "title" not in stable
