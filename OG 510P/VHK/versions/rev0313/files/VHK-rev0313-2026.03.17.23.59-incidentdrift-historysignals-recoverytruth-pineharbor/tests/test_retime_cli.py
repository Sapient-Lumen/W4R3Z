from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_retime_scales_delays_and_typing(tmp_path: Path) -> None:
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": 100},
                    {"type": "RandomWait", "min_ms": 100, "max_ms": 200},
                    {"type": "Log", "message": "sep", "delay_ms": 20},
                    {"type": "Log", "message": "retry", "retry_delay_ms": 40},
                    {"type": "TypeText", "text": "hi", "delay_ms_per_char": 10},
                ],
            }
        )
    )

    # 2x faster => divide delays by 2.
    res = runner.invoke(app, ["retime", str(macro), "--speed", "2", "--quiet"])
    assert res.exit_code == 0, res.output
    out = yaml.safe_load(res.output)
    steps = out["steps"]
    assert steps[0]["ms"] == 50
    assert steps[1]["min_ms"] == 50
    assert steps[1]["max_ms"] == 100
    assert steps[2]["delay_ms"] == 10
    assert steps[3]["retry_delay_ms"] == 20
    assert steps[4]["delay_ms_per_char"] == 5


def test_retime_leaves_timeouts_unchanged_by_default(tmp_path: Path) -> None:
    macro = tmp_path / "m.yaml"
    macro.write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "WaitForImageFile", "haystack_path": "a.png", "needle_path": "b.png", "timeout_ms": 1000, "poll_ms": 200},
                    {"type": "Delay", "ms": 100},
                ],
            }
        )
    )

    res = runner.invoke(app, ["retime", str(macro), "--speed", "2", "--quiet"])
    assert res.exit_code == 0, res.output
    out = yaml.safe_load(res.output)
    steps = out["steps"]
    assert steps[0]["timeout_ms"] == 1000
    assert steps[0]["poll_ms"] == 200
    assert steps[1]["ms"] == 50

    res2 = runner.invoke(app, ["retime", str(macro), "--speed", "2", "--include-timeouts", "--include-polling", "--quiet"])
    assert res2.exit_code == 0, res2.output
    out2 = yaml.safe_load(res2.output)
    steps2 = out2["steps"]
    assert steps2[0]["timeout_ms"] == 500
    assert steps2[0]["poll_ms"] == 100
