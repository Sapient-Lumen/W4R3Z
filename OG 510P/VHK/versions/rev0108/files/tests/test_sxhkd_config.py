from __future__ import annotations

import yaml
from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "sig.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sig",
                "steps": [
                    {"type": "Return", "value_expr": '"OK"', "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"sig": "macros/sig.yaml"},
                "bindings": [
                    {
                        "keys": "Mod4+Shift+P",
                        "macro": "sig",
                        "description": "Run signature",
                    },
                    {
                        "keys": "Control+Alt+K",
                        "macro": "sig",
                        "description": "Scoped",
                        "when": {"class": "Firefox"},
                        "vars": {"x": 1},
                    },
                ],
            }
        )
    )

    return proj


def test_gen_sxhkd_config_basic(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-sxhkd-config", str(proj)])
    assert result.exit_code == 0, result.output

    text = result.output
    # Basic mapping + ordering.
    assert "super + shift + p" in text
    assert "ctrl + alt + k" in text

    # Scoped bind should include require-window and vars JSON.
    assert "--require-window" in text
    assert '"class"' in text and "Firefox" in text
    assert "--vars" in text
    assert '"x"' in text and "1" in text


def test_gen_sxhkd_config_leader_chords(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-sxhkd-config", str(proj), "--leader", "Mod4+Space"])
    assert result.exit_code == 0, result.output

    text = result.output
    # Chord chain uses ';' by default.
    assert "super + space ; super + shift + p" in text
    assert "super + space ; ctrl + alt + k" in text


def test_gen_sxhkd_config_via_bus_embeds_require_window(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)

    runtime = tmp_path / "run"
    runtime.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))

    result = runner.invoke(app, ["gen-sxhkd-config", str(proj), "--via-bus"])
    assert result.exit_code == 0, result.output

    text = result.output
    assert "vhk-emit" in text
    assert "--socket" in text
    # The scoped binding should embed require_window in the payload.
    assert "require_window" in text
    assert "Firefox" in text
