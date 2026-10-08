from __future__ import annotations

import yaml
from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_delay_ms_accepts_expression_string(tmp_path: Path, monkeypatch):
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "m.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "m",
                "steps": [
                    {"type": "Delay", "ms": "1 + 1"},
                    {"type": "Return", "value_expr": "'OK'", "out_var": "return_value"},
                ],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "macros": {"m": "macros/m.yaml"},
            }
        )
    )

    import vhk.core.runner as r

    slept = []

    def fake_sleep(seconds: float):
        slept.append(seconds)

    monkeypatch.setattr(r.time, "sleep", fake_sleep)

    result = runner.invoke(app, ["run", str(proj), "m", "--quiet", "--print-return"])
    assert result.exit_code == 0, result.output
    assert result.output == "OK"
    assert slept, "Delay should call sleep"
    assert abs(slept[0] - 0.002) < 1e-9
