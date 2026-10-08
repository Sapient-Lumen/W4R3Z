from __future__ import annotations

import yaml
from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_scaffold_inserts_disabled_stubs_and_comments(tmp_path: Path):
    mp = tmp_path / "m.yaml"
    mp.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 2000},
                    {"type": "MouseClickAt", "x": 10, "y": 20, "button": 1},
                    {"type": "WaitForImage", "needle_path": "assets/ok.png", "timeout_ms": 1000},
                ],
            },
            sort_keys=False,
        )
    )

    result = runner.invoke(app, ["scaffold", str(mp)])
    assert result.exit_code == 0, result.output
    payload = yaml.safe_load(result.output)
    assert isinstance(payload, dict)
    steps = payload.get("steps")
    assert isinstance(steps, list)

    # Disabled stubs are inserted before the original brittle steps.
    assert any(s.get("type") == "WaitForImage" and s.get("enabled") is False for s in steps)
    assert any(s.get("type") == "ClickNeedle" and s.get("enabled") is False for s in steps)

    # Comments should be present on the original Delay and MouseClickAt steps.
    delay = next(s for s in steps if s.get("type") == "Delay")
    assert "Delay" in str(delay.get("comment"))

    click = next(s for s in steps if s.get("type") == "MouseClickAt")
    assert "Absolute click" in str(click.get("comment"))


def test_scaffold_check_exit_code(tmp_path: Path):
    mp = tmp_path / "m.yaml"
    mp.write_text(
        yaml.safe_dump({"name": "m", "steps": [{"type": "Delay", "ms": 2000}]}, sort_keys=False)
    )
    result = runner.invoke(app, ["scaffold", str(mp), "--check"])
    assert result.exit_code == 1


def test_scaffold_diff_mode(tmp_path: Path):
    mp = tmp_path / "m.yaml"
    mp.write_text(
        yaml.safe_dump({"name": "m", "steps": [{"type": "Delay", "ms": 2000}]}, sort_keys=False)
    )
    result = runner.invoke(app, ["scaffold", str(mp), "--diff", "--quiet"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("--- ")
