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
                        "keys": "Mod4+K",
                        "macro": "sig",
                        "description": "Scoped",
                        "when": {"class": "Firefox"},
                    },
                ],
            }
        )
    )
    return proj


def test_gen_wm_config_i3_mode_one_shot(tmp_path: Path):
    proj = _make_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "gen-wm-config",
            str(proj),
            "--wm",
            "i3",
            "--mode-enter",
            "Mod4+R",
            "--mode-name",
            "vhk",
            "--mode-strip-mods",
            "Mod4",
        ],
    )
    assert result.exit_code == 0, result.output
    text = result.output

    assert 'bindsym Mod4+R mode "vhk"' in text
    assert 'mode "vhk" {' in text
    assert 'bindsym Escape mode "default"' in text

    # Mod4+Shift+P becomes "P" inside the mode.
    assert "bindsym --release P" in text
    # One-shot: macro runs then exits the mode.
    assert '; mode "default"' in text


def test_gen_wm_config_hyprland_submap_includes_reset_and_require_window(tmp_path: Path):
    proj = _make_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "gen-wm-config",
            str(proj),
            "--wm",
            "hyprland",
            "--mode-enter",
            "Mod4+R",
            "--mode-name",
            "vhk",
            "--mode-strip-mods",
            "Mod4",
        ],
    )
    assert result.exit_code == 0, result.output
    text = result.output

    assert "bind = SUPER, R, submap, vhk" in text
    assert "submap = vhk, reset" in text
    assert "submap = reset" in text

    # Mod4+Shift+P becomes SHIFT+P inside submap.
    assert "bindrd = SHIFT, P, Run signature, exec," in text

    # Scoped binding should include --require-window JSON selector.
    assert "bindrd = , K, Scoped, exec," in text or "bindrd = , K, Scoped, exec," in text
    assert "--require-window" in text
    assert '"class":"Firefox"' in text
