from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_lint_macro_json_and_check(tmp_path: Path) -> None:
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 2500},
                    {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
                ],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint", str(macro), "--json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    codes = {i["code"] for i in data["issues"]}
    assert "DELAY_LONG" in codes
    assert "COORD_CLICK" in codes

    # Check mode should fail on warnings by default.
    res2 = runner.invoke(app, ["lint", str(macro), "--check", "--fail-on", "warning", "--json"])
    assert res2.exit_code == 1


def test_lint_fail_on_error_only(tmp_path: Path) -> None:
    macro = tmp_path / "m.yaml"
    # Only info-level issues (NO_REGION) should not fail when fail-on=warning/error.
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "WaitForImage", "needle_path": "assets/foo.png"},
                ],
            },
            sort_keys=False,
        )
    )

    res = runner.invoke(app, ["lint", str(macro), "--check", "--fail-on", "warning", "--json"])
    assert res.exit_code == 0
