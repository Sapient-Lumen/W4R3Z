from __future__ import annotations

import json
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


def test_gen_kanata_config_emits_cfg_virtualkeys_and_switch(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-kanata-config", str(proj)])
    assert result.exit_code == 0, result.output

    text = result.output
    assert "(defcfg" in text
    assert "process-unmapped-keys yes" in text
    assert "danger-enable-cmd yes" in text

    # One vkey per binding, and uses cmd-log.
    assert "(defvirtualkeys" in text
    assert "(cmd-log none error" in text

    # Should map trigger keys in deflayermap.
    assert "(deflayermap (base)" in text
    assert "p @vhk_key_p" in text
    assert "k @vhk_key_k" in text

    # Key 'p' should have a switch checking lmet+lsft.
    assert "vhk_key_p (switch" in text
    assert "(and (input real lmet) (input real lsft))" in text

    # Scoped bind should include require-window and vars JSON.
    assert "--require-window" in text
    # JSON arg will be escaped inside a quoted string token.
    assert "\\\"class\\\":\\\"Firefox\\\"" in text
    assert "--vars" in text
    assert "\\\"x\\\": 1" in text


def test_gen_kanata_config_on_press_flag(tmp_path: Path):
    proj = _make_project(tmp_path)
    result = runner.invoke(app, ["gen-kanata-config", str(proj), "--on-press"])
    assert result.exit_code == 0, result.output
    assert "(on-press tap-vkey" in result.output
