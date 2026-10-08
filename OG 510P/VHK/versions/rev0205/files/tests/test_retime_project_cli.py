from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _write_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "project.yaml").write_text("name: proj\n")

    (project_dir / "macros" / "a.yaml").write_text(
        yaml.safe_dump({"name": "a", "steps": [{"type": "Delay", "ms": 100}]})
    )
    (project_dir / "macros" / "b.yaml").write_text(
        yaml.safe_dump({"name": "b", "steps": [{"type": "Log", "message": "hi", "delay_ms": 50}]})
    )
    return project_dir


def test_retime_project_writes_out_dir(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)
    out_dir = tmp_path / "out"

    res = runner.invoke(app, ["retime-project", str(project_dir), "--out-dir", str(out_dir), "--speed", "2", "--quiet"])
    assert res.exit_code == 0, res.output

    a_out = yaml.safe_load((out_dir / "a.yaml").read_text())
    assert a_out["steps"][0]["ms"] == 50

    b_out = yaml.safe_load((out_dir / "b.yaml").read_text())
    assert b_out["steps"][0]["delay_ms"] == 25

    # Original should remain unchanged.
    a_in = yaml.safe_load((project_dir / "macros" / "a.yaml").read_text())
    assert a_in["steps"][0]["ms"] == 100


def test_retime_project_in_place(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)

    res = runner.invoke(app, ["retime-project", str(project_dir), "--in-place", "--factor", "2", "--quiet"])
    assert res.exit_code == 0, res.output

    a_in = yaml.safe_load((project_dir / "macros" / "a.yaml").read_text())
    assert a_in["steps"][0]["ms"] == 200
