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
        yaml.safe_dump(
            {
                "name": "a",
                "steps": [
                    {"type": "Delay", "ms": 2000},
                    {"type": "MouseClickAt", "x": 1, "y": 2},
                ],
            },
            sort_keys=False,
        )
    )
    (project_dir / "macros" / "b.yaml").write_text(
        yaml.safe_dump({"name": "b", "steps": [{"type": "Log", "message": "ok"}]}, sort_keys=False)
    )
    return project_dir


def test_scaffold_project_out_dir(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)
    out_dir = tmp_path / "out"
    res = runner.invoke(app, ["scaffold-project", str(project_dir), "--out-dir", str(out_dir), "--quiet"])
    assert res.exit_code == 0, res.output

    a_out = yaml.safe_load((out_dir / "a.yaml").read_text())
    assert any(s.get("type") == "WaitForImage" and s.get("enabled") is False for s in a_out["steps"])
    assert any(s.get("type") == "ClickNeedle" and s.get("enabled") is False for s in a_out["steps"])

    # Original should remain unchanged.
    a_in = yaml.safe_load((project_dir / "macros" / "a.yaml").read_text())
    assert all(s.get("enabled", True) is True for s in a_in["steps"])


def test_scaffold_project_check(tmp_path: Path) -> None:
    project_dir = _write_project(tmp_path)
    res = runner.invoke(app, ["scaffold-project", str(project_dir), "--check", "--quiet"])
    assert res.exit_code == 1
