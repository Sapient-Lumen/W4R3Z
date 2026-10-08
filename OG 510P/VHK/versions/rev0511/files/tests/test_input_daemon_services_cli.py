from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def test_gen_ydotoold_service_writes_unit(tmp_path: Path):
    out_dir = tmp_path / "units"
    result = runner.invoke(app, ["gen-ydotoold-service", "--out-dir", str(out_dir), "--name", "ydotoold-test"])
    assert result.exit_code == 0, result.output

    unit = out_dir / "ydotoold-test.service"
    assert unit.exists()
    text = unit.read_text()
    assert "ExecStart=" in text
    assert "ydotoold" in text
    assert "--socket-path" in text
    assert "--socket-perm" in text


def test_gen_dotoold_service_writes_unit(tmp_path: Path):
    out_dir = tmp_path / "units"
    result = runner.invoke(app, ["gen-dotoold-service", "--out-dir", str(out_dir), "--name", "dotoold-test"])
    assert result.exit_code == 0, result.output

    unit = out_dir / "dotoold-test.service"
    assert unit.exists()
    text = unit.read_text()
    assert "ExecStart=" in text
    assert "dotoold" in text
