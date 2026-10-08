from __future__ import annotations

from pathlib import Path

import yaml
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
                "steps": [{"type": "Return", "value_expr": '"OK"', "out_var": "return_value"}],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"sig": "macros/sig.yaml"},
                "bindings": [
                    {"keys": "Mod4+P", "macro": "sig", "description": "Primary P"},
                    {"keys": "Control+P", "macro": "sig", "description": "Alt P"},
                    {"keys": "Mod4+K", "macro": "sig", "description": "K"},
                ],
            }
        )
    )

    return proj


def test_gen_kmonad_config_basic_and_collision_layers(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-kmonad-config", str(proj)])
    assert result.exit_code == 0, result.output

    text = result.output

    # Core blocks.
    assert "(defcfg" in text
    assert "fallthrough true" in text
    assert "allow-cmd true" in text

    # Leader defaults.
    assert "(defalias" in text
    assert "vhk (tap-hold" in text

    # Two bindings share P -> one alt layer should exist with a selector key.
    assert "(deflayer vhk_alt1" in text
    assert "alt1 (layer-next vhk_alt1)" in text

    # Command buttons exist.
    assert "(cmd-button" in text
    assert "vhk run" in text


def test_gen_kmonad_config_on_release(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-kmonad-config", str(proj), "--on-release"])
    assert result.exit_code == 0, result.output
    # On-release uses a no-op ':' press command plus a release command.
    assert '(cmd-button ":"' in result.output
