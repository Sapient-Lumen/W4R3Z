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


def test_gen_keyd_config_emits_ids_and_layers(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-keyd-config", str(proj)])
    assert result.exit_code == 0, result.output

    text = result.output
    assert "[ids]" in text
    assert "*" in text.splitlines()[text.splitlines().index("[ids]") + 1]

    # Composite modifier layer for Mod4+Shift.
    assert "[meta+shift]" in text
    assert "p = command(" in text

    # Composite modifier layer for Ctrl+Alt.
    assert "[control+alt]" in text
    # Scoped binding should include require-window + vars.
    assert "--require-window" in text
    assert "Firefox" in text
    assert "--vars" in text
    assert "\"x\": 1" in text


def test_gen_keyd_config_command_prefix(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-keyd-config", str(proj), "--command-prefix", "sudo -u alice"])
    assert result.exit_code == 0, result.output
    assert "command(sudo -u alice" in result.output
