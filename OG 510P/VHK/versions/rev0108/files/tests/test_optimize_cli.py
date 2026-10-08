from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_optimize_compacts_recording(tmp_path: Path):
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 10},
                    {"type": "Delay", "ms": 20},
                    # Redundant mouse moves.
                    {"type": "MouseMove", "x": 1, "y": 2},
                    {"type": "MouseMove", "x": 3, "y": 4},
                    {"type": "MouseMove", "x": 3, "y": 4},
                    {"type": "Log", "message": "sep"},
                    # Click sequence.
                    {"type": "MouseMove", "x": 10, "y": 10},
                    {"type": "MouseClick", "button": 1, "down": True},
                    {"type": "Delay", "ms": 50},
                    {"type": "MouseMove", "x": 11, "y": 10},
                    {"type": "MouseClick", "button": 1, "up": True},
                    # Chord sequence.
                    {"type": "KeyDown", "key": "ctrl"},
                    {"type": "KeyDown", "key": "l"},
                    {"type": "KeyUp", "key": "l"},
                    {"type": "KeyUp", "key": "ctrl"},
                    # Simple keypress.
                    {"type": "KeyDown", "key": "a"},
                    {"type": "Delay", "ms": 10},
                    {"type": "KeyUp", "key": "a"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    assert isinstance(out, dict)
    steps = out["steps"]

    # Delay merged.
    assert steps[0] == {"type": "Delay", "ms": 30}

    # MouseMove run squashed to the last move.
    assert steps[1] == {"type": "MouseMove", "x": 3, "y": 4}

    # Click compacted.
    assert {"type": "MouseClickAt", "x": 10, "y": 10, "button": 1} in steps

    # Chord + keypress compacted.
    assert {"type": "Key", "keys": "ctrl+l"} in steps
    assert {"type": "Key", "keys": "a"} in steps


def test_optimize_can_collapse_text_into_typetext(tmp_path: Path):
    macro = tmp_path / "t.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "t",
                "steps": [
                    {"type": "Key", "keys": "h"},
                    {"type": "Delay", "ms": 10},
                    {"type": "Key", "keys": "i"},
                    {"type": "Delay", "ms": 15},
                    {"type": "Key", "keys": "!"},
                    {"type": "Log", "message": "after"},
                ],
            }
        )
    )

    result = runner.invoke(app, ["optimize", str(macro), "--compress-text", "--quiet"])
    assert result.exit_code == 0, result.output
    out = yaml.safe_load(result.output)
    steps = out["steps"]
    assert steps[0]["type"] == "TypeText"
    assert steps[0]["text"] == "hi!"
    assert steps[0]["backend"] == "native"
    assert steps[1] == {"type": "Log", "message": "after"}
