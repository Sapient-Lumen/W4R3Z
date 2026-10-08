from __future__ import annotations

import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_cursor_step_default_click_yaml(monkeypatch):
    from vhk.system.cursor_pos import CursorPos
    import vhk.system.cursor_pos as cp

    monkeypatch.setattr(cp, "get_cursor_pos", lambda: CursorPos(x=10, y=20, backend="hyprctl"))

    result = runner.invoke(app, ["cursor-step"])
    assert result.exit_code == 0, result.output
    data = yaml.safe_load(result.output)
    assert isinstance(data, list) and len(data) == 1
    step = data[0]
    assert step["type"] == "MouseClickAt"
    assert step["x"] == 10 and step["y"] == 20
    assert step["button"] == "left"


def test_cursor_step_move_json(monkeypatch):
    from vhk.system.cursor_pos import CursorPos
    import vhk.system.cursor_pos as cp

    monkeypatch.setattr(cp, "get_cursor_pos", lambda: CursorPos(x=5, y=7, backend="hyprctl"))

    result = runner.invoke(app, ["cursor-step", "move", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["type"] == "MouseMove"
    assert payload["x"] == 5 and payload["y"] == 7
